"""
Production Project 7-P-A: Universal Enterprise Tool Hub Gateway
Features:
1. Proxies 5 Downstream Servers: fs:, db:, comm:, analytics:, code:
2. Per-Tenant Role-Based Access Control (RBAC)
3. Token-Bucket Rate Limiting (100 calls/min per tenant)
4. 60-Second Tool Schema Caching
5. Real-Time Health & Audit Logging (data/enterprise_hub_audit.db)
"""

import time
import os
import json
import sqlite3
import hashlib
import datetime
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

# Import 5 Downstream MCP Servers Tool Functions
from fs_mcp_server import read_file, write_file, list_directory, search_files
from db_mcp_server import describe_schema, query_table, insert_record
from comm_mcp_server import draft_email, check_calendar, send_notification
from analytics_mcp_server import load_dataset, compute_statistics, generate_summary
from code_intel_mcp_server import analyze_file, find_dependencies, detect_code_smells

DATA_DIR = "data"
AUDIT_DB_PATH = os.path.join(DATA_DIR, "enterprise_hub_audit.db")
os.makedirs(DATA_DIR, exist_ok=True)

# Gateway Server Instance
gateway_mcp = FastMCP(
    name="UniversalEnterpriseToolHubGateway",
    instructions="Universal Enterprise Tool Hub Gateway routing 5 specialized MCP tool categories with per-tenant RBAC."
)

# Per-Tenant RBAC Permissions Definition
TENANT_RBAC = {
    "key_tenant_alpha": {
        "tenant_id": "Tenant_Alpha",
        "allowed_namespaces": ["fs", "db", "code", "analytics"]
    },
    "key_tenant_beta": {
        "tenant_id": "Tenant_Beta",
        "allowed_namespaces": ["comm", "analytics", "fs"]
    },
    "key_enterprise_admin": {
        "tenant_id": "Enterprise_Admin",
        "allowed_namespaces": ["*"]
    }
}

# 5 Downstream Server Definitions
DOWNSTREAM_HUB = {
    "fs": {
        "name": "FilesystemServer",
        "prefix": "fs",
        "tools": {
            "read_file": read_file,
            "write_file": write_file,
            "list_directory": list_directory,
            "search_files": search_files
        },
        "status": "ONLINE"
    },
    "db": {
        "name": "DatabaseServer",
        "prefix": "db",
        "tools": {
            "describe_schema": describe_schema,
            "query_table": query_table,
            "insert_record": insert_record
        },
        "status": "ONLINE"
    },
    "comm": {
        "name": "CommunicationServer",
        "prefix": "comm",
        "tools": {
            "draft_email": draft_email,
            "check_calendar": check_calendar,
            "send_notification": send_notification
        },
        "status": "ONLINE"
    },
    "analytics": {
        "name": "AnalyticsServer",
        "prefix": "analytics",
        "tools": {
            "load_dataset": load_dataset,
            "compute_statistics": compute_statistics,
            "generate_summary": generate_summary
        },
        "status": "ONLINE"
    },
    "code": {
        "name": "CodeIntelligenceServer",
        "prefix": "code",
        "tools": {
            "analyze_file": analyze_file,
            "find_dependencies": find_dependencies,
            "detect_code_smells": detect_code_smells
        },
        "status": "ONLINE"
    }
}

# Rate Limiter & Schema Cache State
RATE_LIMIT_STORE: Dict[str, List[float]] = {}
MAX_CALLS_PER_MIN = 100
SCHEMA_CACHE: Dict[str, Any] = {"timestamp": 0.0, "schemas": {}}


def init_audit_db():
    conn = sqlite3.connect(AUDIT_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hub_audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
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


def log_hub_audit(api_key: str, tenant_id: str, tool_name: str, status: str, latency_ms: float, error_msg: Optional[str] = None):
    key_hash = hashlib.sha256(api_key.encode('utf-8')).hexdigest()[:16]
    timestamp = datetime.datetime.utcnow().isoformat()

    conn = sqlite3.connect(AUDIT_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO hub_audit_logs (timestamp, tenant_id, api_key_hash, namespaced_tool, status, latency_ms, error_msg)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (timestamp, tenant_id, key_hash, tool_name, status, latency_ms, error_msg)
    )
    conn.commit()
    conn.close()


class EnterpriseHubGateway:
    def __init__(self):
        self.servers = DOWNSTREAM_HUB

    def discover_tools(self, force_refresh: bool = False) -> Dict[str, Any]:
        now = time.time()
        if not force_refresh and (now - SCHEMA_CACHE["timestamp"] < 60.0) and SCHEMA_CACHE["schemas"]:
            return {"cached": True, "schemas": SCHEMA_CACHE["schemas"]}

        registry = {}
        for prefix, server in self.servers.items():
            if server["status"] != "ONLINE":
                continue
            for t_name, t_func in server["tools"].items():
                namespaced = f"{prefix}:{t_name}"
                registry[namespaced] = {
                    "prefix": prefix,
                    "original_tool": t_name,
                    "description": getattr(t_func, "__doc__", f"{t_name} on {prefix}"),
                    "func": t_func
                }

        SCHEMA_CACHE["timestamp"] = now
        SCHEMA_CACHE["schemas"] = registry
        return {"cached": False, "schemas": registry}

    def route_tool_call(self, api_key: str, namespaced_tool: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        start_t = time.time()

        # 1. Authentication & Tenant Identification
        if not api_key or api_key not in TENANT_RBAC:
            latency = (time.time() - start_t) * 1000
            log_hub_audit(api_key or "anonymous", "UNKNOWN", namespaced_tool, "FAILURE", latency, "401 Unauthorized")
            return {"success": False, "error": "401 Unauthorized: Invalid API key.", "error_type": "AuthenticationError"}

        tenant_info = TENANT_RBAC[api_key]
        tenant_id = tenant_info["tenant_id"]
        allowed_namespaces = tenant_info["allowed_namespaces"]

        # 2. Extract prefix and verify RBAC
        prefix = namespaced_tool.split(":")[0] if ":" in namespaced_tool else ""
        if "*" not in allowed_namespaces and prefix not in allowed_namespaces:
            latency = (time.time() - start_t) * 1000
            log_hub_audit(api_key, tenant_id, namespaced_tool, "FAILURE", latency, "403 Forbidden - RBAC Policy")
            return {
                "success": False,
                "error": f"403 Forbidden: Tenant '{tenant_id}' is not authorized to call namespace '{prefix}:*'. Allowed: {allowed_namespaces}",
                "error_type": "RBACPermissionError"
            }

        # 3. Token Bucket Rate Limiter
        now = time.time()
        if api_key not in RATE_LIMIT_STORE:
            RATE_LIMIT_STORE[api_key] = []
        RATE_LIMIT_STORE[api_key] = [t for t in RATE_LIMIT_STORE[api_key] if now - t < 60.0]

        if len(RATE_LIMIT_STORE[api_key]) >= MAX_CALLS_PER_MIN:
            latency = (time.time() - start_t) * 1000
            log_hub_audit(api_key, tenant_id, namespaced_tool, "FAILURE", latency, "429 RateLimitExceeded")
            return {"success": False, "error": f"429 Rate Limit Exceeded ({MAX_CALLS_PER_MIN}/min).", "error_type": "RateLimitExceeded"}

        RATE_LIMIT_STORE[api_key].append(now)

        # 4. Route Call to Downstream Server Function
        discovery = self.discover_tools()
        schemas = discovery["schemas"]

        if namespaced_tool not in schemas:
            latency = (time.time() - start_t) * 1000
            log_hub_audit(api_key, tenant_id, namespaced_tool, "FAILURE", latency, "Tool Not Found")
            return {"success": False, "error": f"Tool '{namespaced_tool}' not found in Enterprise Hub registry.", "error_type": "ToolNotFoundError"}

        tool_item = schemas[namespaced_tool]
        target_func = tool_item["func"]

        try:
            import inspect
            sig = inspect.signature(target_func)
            valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
            res = target_func(**valid_kwargs)
            latency = (time.time() - start_t) * 1000
            log_hub_audit(api_key, tenant_id, namespaced_tool, "SUCCESS", latency)
            return {
                "gateway_routed": True,
                "tenant_id": tenant_id,
                "namespaced_tool": namespaced_tool,
                "server_prefix": prefix,
                "latency_ms": round(latency, 2),
                "result": res
            }
        except Exception as e:
            latency = (time.time() - start_t) * 1000
            log_hub_audit(api_key, tenant_id, namespaced_tool, "FAILURE", latency, str(e))
            return {"success": False, "error": f"Downstream Execution Error: {str(e)}"}

    def get_health(self) -> Dict[str, Any]:
        server_status = {}
        total = len(self.servers)
        online = 0
        for p, s in self.servers.items():
            if s["status"] == "ONLINE":
                online += 1
            server_status[p] = {"name": s["name"], "status": s["status"], "tool_count": len(s["tools"])}

        overall = "HEALTHY" if online == total else ("DEGRADED" if online > 0 else "UNHEALTHY")
        return {
            "gateway_status": overall,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "online_servers": f"{online}/{total}",
            "downstream_servers": server_status
        }


hub_gateway = EnterpriseHubGateway()


@gateway_mcp.tool(name="list_hub_tools", description="Lists all available tools across Universal Enterprise Tool Hub.")
def list_hub_tools() -> Dict[str, Any]:
    discovery = hub_gateway.discover_tools()
    tools_list = [{"name": name, "server": info["prefix"], "description": info["description"]} for name, info in discovery["schemas"].items()]
    return {"success": True, "tool_count": len(tools_list), "tools": tools_list}


if __name__ == "__main__":
    gateway_mcp.run()
