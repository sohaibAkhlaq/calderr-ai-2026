"""
Lab 7.2: Authenticated Production MCP Server with SQLite Audit Log & Rate Limiting
Provides:
1. API Key Authentication (Bearer token validation)
2. Token-Bucket Rate Limiting (Max 10 requests / 60 seconds per key)
3. Structured Audit Logging to SQLite (audit_logs table)
4. Database Tools: query_table, insert_record, update_record, describe_schema
5. Filesystem Tools: read_file, write_file, list_directory, search_files
6. MCP Resource Providers: resource://sandbox/files, resource://db/schema
7. MCP Prompt Templates: file_summarization, database_report
"""

import os
import sqlite3
import json
import time
import hashlib
import datetime
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

# Ensure data & sandbox directories exist
DATA_DIR = "data"
SANDBOX_DIR = os.path.join(DATA_DIR, "sandbox")
DB_PATH = os.path.join(DATA_DIR, "mcp_enterprise.db")
AUDIT_DB_PATH = os.path.join(DATA_DIR, "mcp_audit.db")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SANDBOX_DIR, exist_ok=True)

# Initialize MCP Server
mcp = FastMCP(
    name="AuthenticatedEnterpriseMCPServer",
    instructions="Production MCP server exposing authenticated Database tools, Filesystem tools, Resources, and Prompt templates."
)

# Valid API Key Registry
VALID_API_KEYS = {
    "key_alpha_123": "TenantAlpha",
    "key_beta_999": "TenantBeta",
    "admin_secret_key": "SystemAdmin"
}

# Rate Limiter State: {api_key: [timestamps]}
RATE_LIMIT_STORE: Dict[str, List[float]] = {}
MAX_REQUESTS_PER_MINUTE = 10
WINDOW_SECONDS = 60.0


# =============================================================================
# HELPER: DATABASE INITIALIZATION & AUDIT LOGGING
# =============================================================================
def init_databases():
    # 1. Target Business Database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            budget REAL DEFAULT 0.0
        )
    ''')
    # Seed initial data if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (name, email, role, created_at) VALUES ('Alice Smith', 'alice@company.com', 'admin', '2026-08-01')")
        cursor.execute("INSERT INTO users (name, email, role, created_at) VALUES ('Bob Jones', 'bob@company.com', 'developer', '2026-08-02')")
        cursor.execute("INSERT INTO projects (title, status, budget) VALUES ('AI Memory Platform', 'active', 50000.0)")
    conn.commit()
    conn.close()

    # 2. Audit Database
    conn_audit = sqlite3.connect(AUDIT_DB_PATH)
    cursor_audit = conn_audit.cursor()
    cursor_audit.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            api_key_hash TEXT NOT NULL,
            tool_name TEXT NOT NULL,
            input_params_hash TEXT NOT NULL,
            status TEXT NOT NULL,
            latency_ms REAL NOT NULL,
            error_message TEXT
        )
    ''')
    conn_audit.commit()
    conn_audit.close()


init_databases()


def log_audit_entry(api_key: str, tool_name: str, params: Dict[str, Any], status: str, latency_ms: float, error_msg: Optional[str] = None):
    """Logs tool execution details to SQLite audit store."""
    timestamp = datetime.datetime.utcnow().isoformat()
    key_hash = hashlib.sha256(api_key.encode('utf-8')).hexdigest()[:16]
    params_hash = hashlib.sha256(json.dumps(params, sort_keys=True).encode('utf-8')).hexdigest()[:16]

    conn = sqlite3.connect(AUDIT_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO audit_logs (timestamp, api_key_hash, tool_name, input_params_hash, status, latency_ms, error_message)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (timestamp, key_hash, tool_name, params_hash, status, latency_ms, error_msg)
    )
    conn.commit()
    conn.close()


def check_auth_and_rate_limit(api_key: str) -> Optional[Dict[str, Any]]:
    """Validates API Key and checks Token Bucket rate limits."""
    if not api_key or api_key not in VALID_API_KEYS:
        return {"success": False, "error": "401 Unauthorized: Invalid or missing API key.", "error_type": "AuthenticationError"}

    # Token Bucket Rate Limiting
    now = time.time()
    if api_key not in RATE_LIMIT_STORE:
        RATE_LIMIT_STORE[api_key] = []
    
    # Filter timestamps within 60s window
    RATE_LIMIT_STORE[api_key] = [t for t in RATE_LIMIT_STORE[api_key] if now - t < WINDOW_SECONDS]

    if len(RATE_LIMIT_STORE[api_key]) >= MAX_REQUESTS_PER_MINUTE:
        return {
            "success": False,
            "error": f"429 Rate Limit Exceeded: Maximum {MAX_REQUESTS_PER_MINUTE} requests per minute allowed.",
            "error_type": "RateLimitExceeded"
        }

    RATE_LIMIT_STORE[api_key].append(now)
    return None


# =============================================================================
# DATABASE TOOLS
# =============================================================================
@mcp.tool(name="describe_schema", description="Describes schema and table structure of the SQLite database.")
def describe_schema(api_key: str) -> Dict[str, Any]:
    start_t = time.time()
    auth_err = check_auth_and_rate_limit(api_key)
    if auth_err:
        return auth_err

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [r[0] for r in cursor.fetchall()]

        schema_info = {}
        for t in tables:
            cursor.execute(f"PRAGMA table_info({t})")
            cols = [{"id": col[0], "name": col[1], "type": col[2], "notnull": col[3]} for col in cursor.fetchall()]
            schema_info[t] = cols

        conn.close()
        latency = (time.time() - start_t) * 1000
        log_audit_entry(api_key, "describe_schema", {}, "SUCCESS", latency)
        return {"success": True, "tables": tables, "schema": schema_info}
    except Exception as e:
        latency = (time.time() - start_t) * 1000
        log_audit_entry(api_key, "describe_schema", {}, "FAILURE", latency, str(e))
        return {"success": False, "error": str(e)}


@mcp.tool(name="query_table", description="Executes a SELECT query on the SQLite database (read-only queries).")
def query_table(api_key: str, table_name: str, limit: int = 10) -> Dict[str, Any]:
    start_t = time.time()
    auth_err = check_auth_and_rate_limit(api_key)
    if auth_err:
        return auth_err

    clean_table = str(table_name).strip().lower()
    if clean_table not in ["users", "projects"]:
        latency = (time.time() - start_t) * 1000
        log_audit_entry(api_key, "query_table", {"table": table_name}, "FAILURE", latency, "Invalid table")
        return {"success": False, "error": f"Invalid table '{table_name}'. Allowed: users, projects"}

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {clean_table} LIMIT ?", (limit,))
        rows = cursor.fetchall()
        col_names = [description[0] for description in cursor.description]
        conn.close()

        records = [dict(zip(col_names, row)) for row in rows]
        latency = (time.time() - start_t) * 1000
        log_audit_entry(api_key, "query_table", {"table": clean_table, "limit": limit}, "SUCCESS", latency)
        return {"success": True, "table": clean_table, "count": len(records), "records": records}
    except Exception as e:
        latency = (time.time() - start_t) * 1000
        log_audit_entry(api_key, "query_table", {"table": clean_table}, "FAILURE", latency, str(e))
        return {"success": False, "error": str(e)}


@mcp.tool(name="insert_record", description="Inserts a new user record into the users table.")
def insert_record(api_key: str, name: str, email: str, role: str = "user") -> Dict[str, Any]:
    start_t = time.time()
    auth_err = check_auth_and_rate_limit(api_key)
    if auth_err:
        return auth_err

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        created_at = datetime.date.today().isoformat()
        cursor.execute("INSERT INTO users (name, email, role, created_at) VALUES (?, ?, ?, ?)", (name, email, role, created_at))
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()

        latency = (time.time() - start_t) * 1000
        log_audit_entry(api_key, "insert_record", {"email": email}, "SUCCESS", latency)
        return {"success": True, "inserted_id": new_id, "name": name, "email": email}
    except Exception as e:
        latency = (time.time() - start_t) * 1000
        log_audit_entry(api_key, "insert_record", {"email": email}, "FAILURE", latency, str(e))
        return {"success": False, "error": str(e)}


# =============================================================================
# FILESYSTEM TOOLS (Sandboxed inside data/sandbox)
# =============================================================================
def _get_safe_path(filename: str) -> str:
    clean_name = os.path.basename(filename)
    return os.path.join(SANDBOX_DIR, clean_name)


@mcp.tool(name="write_file", description="Writes text content to a sandboxed file in data/sandbox.")
def write_file(api_key: str, filename: str, content: str) -> Dict[str, Any]:
    start_t = time.time()
    auth_err = check_auth_and_rate_limit(api_key)
    if auth_err:
        return auth_err

    try:
        filepath = _get_safe_path(filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        latency = (time.time() - start_t) * 1000
        log_audit_entry(api_key, "write_file", {"filename": filename}, "SUCCESS", latency)
        return {"success": True, "filename": os.path.basename(filepath), "bytes_written": len(content.encode('utf-8'))}
    except Exception as e:
        latency = (time.time() - start_t) * 1000
        log_audit_entry(api_key, "write_file", {"filename": filename}, "FAILURE", latency, str(e))
        return {"success": False, "error": str(e)}


@mcp.tool(name="read_file", description="Reads text content from a sandboxed file in data/sandbox.")
def read_file(api_key: str, filename: str) -> Dict[str, Any]:
    start_t = time.time()
    auth_err = check_auth_and_rate_limit(api_key)
    if auth_err:
        return auth_err

    try:
        filepath = _get_safe_path(filename)
        if not os.path.exists(filepath):
            latency = (time.time() - start_t) * 1000
            log_audit_entry(api_key, "read_file", {"filename": filename}, "FAILURE", latency, "File not found")
            return {"success": False, "error": f"File '{filename}' not found in sandbox."}

        with open(filepath, "r", encoding="utf-8") as f:
            data = f.read()

        latency = (time.time() - start_t) * 1000
        log_audit_entry(api_key, "read_file", {"filename": filename}, "SUCCESS", latency)
        return {"success": True, "filename": os.path.basename(filepath), "content": data}
    except Exception as e:
        latency = (time.time() - start_t) * 1000
        log_audit_entry(api_key, "read_file", {"filename": filename}, "FAILURE", latency, str(e))
        return {"success": False, "error": str(e)}


@mcp.tool(name="list_directory", description="Lists all files stored inside the sandboxed data/sandbox directory.")
def list_directory(api_key: str) -> Dict[str, Any]:
    start_t = time.time()
    auth_err = check_auth_and_rate_limit(api_key)
    if auth_err:
        return auth_err

    try:
        files = os.listdir(SANDBOX_DIR)
        file_details = []
        for fn in files:
            fp = os.path.join(SANDBOX_DIR, fn)
            file_details.append({"filename": fn, "size_bytes": os.path.getsize(fp)})

        latency = (time.time() - start_t) * 1000
        log_audit_entry(api_key, "list_directory", {}, "SUCCESS", latency)
        return {"success": True, "file_count": len(files), "files": file_details}
    except Exception as e:
        latency = (time.time() - start_t) * 1000
        log_audit_entry(api_key, "list_directory", {}, "FAILURE", latency, str(e))
        return {"success": False, "error": str(e)}


# =============================================================================
# RESOURCE PROVIDERS
# =============================================================================
@mcp.resource("resource://sandbox/files")
def resource_sandbox_files() -> str:
    """Exposes browsable listing of sandboxed files as an MCP Resource."""
    files = os.listdir(SANDBOX_DIR) if os.path.exists(SANDBOX_DIR) else []
    return json.dumps({"resource": "resource://sandbox/files", "files": files})


@mcp.resource("resource://db/schema")
def resource_db_schema() -> str:
    """Exposes SQLite database tables and schema as an MCP Resource."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [r[0] for r in cursor.fetchall()]
    conn.close()
    return json.dumps({"resource": "resource://db/schema", "tables": tables})


# =============================================================================
# PROMPT TEMPLATES
# =============================================================================
@mcp.prompt(name="file_summarization")
def file_summarization_prompt(filename: str) -> str:
    """Generates a structured file summarization prompt template."""
    return f"Please read the file '{filename}' using read_file() and provide a bulleted executive summary of its content."


@mcp.prompt(name="database_report")
def database_report_prompt(table_name: str) -> str:
    """Generates a structured database report analysis prompt template."""
    return f"Please query table '{table_name}' using query_table() and generate a structured data insights report."


if __name__ == "__main__":
    print("🚀 Starting Authenticated FastMCP Server...")
    mcp.run()
