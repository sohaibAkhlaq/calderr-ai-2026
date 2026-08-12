"""
Lab 7.3: Production MCP Gateway with Tool Namespace Routing & Schema Caching
Provides:
1. Tool Discovery across 3 Downstream MCP Servers (Filesystem, Database, Utilities)
2. Namespace Routing (fs:*, db:*, util:*)
3. 60-Second Tool Schema Caching
4. Aggregated Health Status Monitoring (/health endpoint)
5. Transparent Routing Proxy for LangGraph Agents
"""

import time
import json
import asyncio
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

# Import Downstream Tool Implementations
from lab7_1_first_mcp_server import calculate, string_processor, date_helper
from lab7_2_database_mcp import (
    describe_schema, query_table, insert_record,
    write_file, read_file, list_directory
)

# Initialize MCP Gateway Server
gateway_mcp = FastMCP(
    name="EnterpriseMCPGateway",
    instructions="Unified Gateway Proxy hosting and routing requests across Filesystem (fs:), Database (db:), and Utility (util:) MCP servers."
)

# Downstream Server Definitions & Registry
DOWNSTREAM_SERVERS = {
    "fs": {
        "name": "FilesystemServer",
        "prefix": "fs",
        "tools": {
            "read_file": read_file,
            "write_file": write_file,
            "list_directory": list_directory
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
    "util": {
        "name": "UtilityServer",
        "prefix": "util",
        "tools": {
            "calculate": calculate,
            "string_processor": string_processor,
            "date_helper": date_helper
        },
        "status": "ONLINE"
    }
}

# Schema Cache State
SCHEMA_CACHE: Dict[str, Any] = {"timestamp": 0.0, "schemas": {}}
CACHE_TTL_SECONDS = 60.0


class MCPGateway:
    def __init__(self):
        self.servers = DOWNSTREAM_SERVERS

    def discover_tools(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Discovers tools across all downstream servers with 60-second caching."""
        now = time.time()
        if not force_refresh and (now - SCHEMA_CACHE["timestamp"] < CACHE_TTL_SECONDS) and SCHEMA_CACHE["schemas"]:
            return {"cached": True, "schemas": SCHEMA_CACHE["schemas"]}

        registry = {}
        for prefix, s_info in self.servers.items():
            if s_info["status"] != "ONLINE":
                continue
            for t_name, t_func in s_info["tools"].items():
                namespaced_name = f"{prefix}:{t_name}"
                registry[namespaced_name] = {
                    "server_prefix": prefix,
                    "original_tool": t_name,
                    "description": getattr(t_func, "__doc__", f"Tool {t_name} on server {prefix}"),
                    "function_ref": t_func
                }

        SCHEMA_CACHE["timestamp"] = now
        SCHEMA_CACHE["schemas"] = registry
        return {"cached": False, "schemas": registry}

    def route_tool_call(self, namespaced_tool: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Routes an incoming namespaced tool call to the correct downstream server."""
        start_t = time.time()
        discovery = self.discover_tools()
        registry = discovery["schemas"]

        if namespaced_tool not in registry:
            return {
                "success": False,
                "error": f"Gateway Error: Unknown namespaced tool '{namespaced_tool}'. Discovered tools: {list(registry.keys())}",
                "error_type": "ToolNotFoundError"
            }

        tool_info = registry[namespaced_tool]
        prefix = tool_info["server_prefix"]
        
        # Verify server health status
        if self.servers[prefix]["status"] != "ONLINE":
            return {
                "success": False,
                "error": f"Gateway Error: Downstream server '{prefix}' is OFFLINE.",
                "error_type": "ServerOfflineError"
            }

        target_func = tool_info["function_ref"]
        try:
            # Execute downstream tool function
            result = target_func(**kwargs)
            latency = (time.time() - start_t) * 1000
            return {
                "gateway_routed": True,
                "namespaced_tool": namespaced_tool,
                "server_prefix": prefix,
                "latency_ms": round(latency, 2),
                "result": result
            }
        except Exception as e:
            latency = (time.time() - start_t) * 1000
            return {
                "gateway_routed": True,
                "namespaced_tool": namespaced_tool,
                "server_prefix": prefix,
                "latency_ms": round(latency, 2),
                "success": False,
                "error": f"Downstream Execution Error: {str(e)}"
            }

    def get_health_status(self) -> Dict[str, Any]:
        """Aggregates health status from all downstream servers (/health)."""
        summary = {}
        total_servers = len(self.servers)
        online_count = 0
        
        for prefix, info in self.servers.items():
            status = info["status"]
            if status == "ONLINE":
                online_count += 1
            summary[prefix] = {
                "name": info["name"],
                "status": status,
                "tool_count": len(info["tools"])
            }

        overall_status = "HEALTHY" if online_count == total_servers else ("DEGRADED" if online_count > 0 else "UNHEALTHY")
        return {
            "gateway_status": overall_status,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "online_servers": f"{online_count}/{total_servers}",
            "downstream_servers": summary
        }


# Instantiate Global Gateway
gateway = MCPGateway()


# =============================================================================
# FASTMCP PROXY TOOLS (Exposed to LangGraph Agents via Gateway)
# =============================================================================
@gateway_mcp.tool(name="gateway_list_tools", description="Lists all namespaced tools across all downstream MCP servers.")
def gateway_list_tools() -> Dict[str, Any]:
    discovery = gateway.discover_tools()
    tools_list = []
    for namespaced_name, info in discovery["schemas"].items():
        tools_list.append({
            "name": namespaced_name,
            "server": info["server_prefix"],
            "description": info["description"]
        })
    return {"success": True, "tools_count": len(tools_list), "tools": tools_list}


@gateway_mcp.tool(name="gateway_call_tool", description="Executes any namespaced tool (e.g. 'fs:read_file', 'db:query_table', 'util:calculate').")
def gateway_call_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    return gateway.route_tool_call(tool_name, arguments)


if __name__ == "__main__":
    print("🚀 Starting FastMCP Gateway Server...")
    gateway_mcp.run()
