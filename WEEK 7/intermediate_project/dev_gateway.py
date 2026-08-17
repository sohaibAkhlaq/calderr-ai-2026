"""
Project 7-I-A: Developer Productivity MCP Gateway
Manages Namespace Routing for 3 Servers:
- code:* -> Code Intelligence Server
- gh:*   -> GitHub Server
- doc:*  -> Documentation Server

Features:
- 60-second Tool Schema Caching
- Bearer API Key Authentication
- Token Bucket Rate Limiting (60 requests/minute)
- SQLite Audit Store (data/dev_suite_audit.db)
"""

import time
import os
import json
import sqlite3
import hashlib
import datetime
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

# Import Downstream Servers Tool Functions
from code_intel_server import analyze_file, find_dependencies, detect_code_smells
from github_mcp_server import list_open_prs, get_pr_diff, create_issue, search_repo_code, get_recent_commits
from doc_mcp_server import generate_docstring, generate_readme_section, generate_api_docs

DATA_DIR = "data"
AUDIT_DB_PATH = os.path.join(DATA_DIR, "dev_suite_audit.db")
os.makedirs(DATA_DIR, exist_ok=True)

# Gateway Server Instance
gateway_mcp = FastMCP(
    name="DeveloperProductivityMCPGateway",
    instructions="Developer Productivity Tool Suite Gateway proxying requests across code:, gh:, and doc: MCP namespaces."
)

AUTHORIZED_KEYS = {
    "key_dev_suite": "DeveloperSuiteUser",
    "key_admin_suite": "AdminSuiteUser"
}

# Rate Limits: { (key, tool): [timestamps] }
RATE_LIMIT_STORE: Dict[str, List[float]] = {}
MAX_CALLS_PER_MIN = 60
WINDOW_SEC = 60.0

DOWNSTREAM_REGISTRY = {
    "code": {
        "name": "CodeIntelligenceServer",
        "prefix": "code",
        "tools": {
            "analyze_file": analyze_file,
            "find_dependencies": find_dependencies,
            "detect_code_smells": detect_code_smells
        },
        "status": "ONLINE"
    },
    "gh": {
        "name": "GitHubServer",
        "prefix": "gh",
        "tools": {
            "list_open_prs": list_open_prs,
            "get_pr_diff": get_pr_diff,
            "create_issue": create_issue,
            "search_repo_code": search_repo_code,
            "get_recent_commits": get_recent_commits
        },
        "status": "ONLINE"
    },
    "doc": {
        "name": "DocumentationServer",
        "prefix": "doc",
        "tools": {
            "generate_docstring": generate_docstring,
            "generate_readme_section": generate_readme_section,
            "generate_api_docs": generate_api_docs
        },
        "status": "ONLINE"
    }
}

SCHEMA_CACHE: Dict[str, Any] = {"timestamp": 0.0, "schemas": {}}


def init_audit_db():
    conn = sqlite3.connect(AUDIT_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dev_audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            api_key_hash TEXT NOT NULL,
            namespaced_tool TEXT NOT NULL,
            status TEXT NOT NULL,
            latency_ms REAL NOT NULL,
            error_msg TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_audit_db()


def audit_log(api_key: str, tool_name: str, status: str, latency_ms: float, error_msg: Optional[str] = None):
    key_hash = hashlib.sha256(api_key.encode('utf-8')).hexdigest()[:16]
    timestamp = datetime.datetime.utcnow().isoformat()

    conn = sqlite3.connect(AUDIT_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO dev_audit_logs (timestamp, api_key_hash, namespaced_tool, status, latency_ms, error_msg)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (timestamp, key_hash, tool_name, status, latency_ms, error_msg)
    )
    conn.commit()
    conn.close()


class DevSuiteGateway:
    def __init__(self):
        self.registry = DOWNSTREAM_REGISTRY

    def discover_tools(self, force_refresh: bool = False) -> Dict[str, Any]:
        now = time.time()
        if not force_refresh and (now - SCHEMA_CACHE["timestamp"] < 60.0) and SCHEMA_CACHE["schemas"]:
            return {"cached": True, "schemas": SCHEMA_CACHE["schemas"]}

        tools_map = {}
        for prefix, server in self.registry.items():
            if server["status"] != "ONLINE":
                continue
            for t_name, t_func in server["tools"].items():
                namespaced_name = f"{prefix}:{t_name}"
                tools_map[namespaced_name] = {
                    "prefix": prefix,
                    "original_tool": t_name,
                    "description": getattr(t_func, "__doc__", f"{t_name} on {prefix}"),
                    "func": t_func
                }

        SCHEMA_CACHE["timestamp"] = now
        SCHEMA_CACHE["schemas"] = tools_map
        return {"cached": False, "schemas": tools_map}

    def route_tool_call(self, api_key: str, namespaced_tool: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        start_t = time.time()

        # Auth Check
        if not api_key or api_key not in AUTHORIZED_KEYS:
            latency = (time.time() - start_t) * 1000
            audit_log(api_key or "anonymous", namespaced_tool, "FAILURE", latency, "401 Unauthorized")
            return {"success": False, "error": "401 Unauthorized: Invalid API key.", "error_type": "AuthenticationError"}

        # Rate Limit Check
        now = time.time()
        if api_key not in RATE_LIMIT_STORE:
            RATE_LIMIT_STORE[api_key] = []
        RATE_LIMIT_STORE[api_key] = [t for t in RATE_LIMIT_STORE[api_key] if now - t < WINDOW_SEC]

        if len(RATE_LIMIT_STORE[api_key]) >= MAX_CALLS_PER_MIN:
            latency = (time.time() - start_t) * 1000
            audit_log(api_key, namespaced_tool, "FAILURE", latency, "429 RateLimitExceeded")
            return {"success": False, "error": f"429 Rate Limit Exceeded ({MAX_CALLS_PER_MIN}/min).", "error_type": "RateLimitExceeded"}

        RATE_LIMIT_STORE[api_key].append(now)

        discovery = self.discover_tools()
        schemas = discovery["schemas"]

        if namespaced_tool not in schemas:
            latency = (time.time() - start_t) * 1000
            audit_log(api_key, namespaced_tool, "FAILURE", latency, "Tool Not Found")
            return {"success": False, "error": f"Tool '{namespaced_tool}' not found in gateway registry.", "error_type": "ToolNotFoundError"}

        tool_item = schemas[namespaced_tool]
        target_func = tool_item["func"]

        try:
            import inspect
            sig = inspect.signature(target_func)
            valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
            res = target_func(**valid_kwargs)
            latency = (time.time() - start_t) * 1000
            audit_log(api_key, namespaced_tool, "SUCCESS", latency)
            return {
                "gateway_routed": True,
                "namespaced_tool": namespaced_tool,
                "server_prefix": tool_item["prefix"],
                "latency_ms": round(latency, 2),
                "result": res
            }
        except Exception as e:
            latency = (time.time() - start_t) * 1000
            audit_log(api_key, namespaced_tool, "FAILURE", latency, str(e))
            return {"success": False, "error": f"Downstream Execution Error: {str(e)}"}

    def get_health(self) -> Dict[str, Any]:
        status_map = {}
        for p, s in self.registry.items():
            status_map[p] = {"name": s["name"], "status": s["status"], "tool_count": len(s["tools"])}
        return {"gateway_status": "HEALTHY", "servers": status_map}


dev_gateway = DevSuiteGateway()


@gateway_mcp.tool(name="list_suite_tools", description="Lists all available tools across Developer Productivity MCP Suite.")
def list_suite_tools() -> Dict[str, Any]:
    discovery = dev_gateway.discover_tools()
    tools_list = [{"name": name, "server": info["prefix"], "description": info["description"]} for name, info in discovery["schemas"].items()]
    return {"success": True, "tool_count": len(tools_list), "tools": tools_list}


if __name__ == "__main__":
    gateway_mcp.run()
