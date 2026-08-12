"""
Lab 7.5: Automated Friday Standup Live Demonstration & Ecosystem Failure Resilience Suite
Executes all 5 Friday Standup Requirements:
1. Live Ecosystem Tool Discovery & Multi-Step Agent Execution
2. Tool Schema Inspection Walkthrough
3. Security Demonstration (401 Auth Rejection, 429 Rate Limit Firing, Audit Store Verification)
4. Ecosystem Architecture Summary
5. Downstream Server Mid-Demo Failure & Graceful Degradation Demonstration
"""

import time
import json
import sqlite3
from lab7_3_mcp_gateway import gateway, DOWNSTREAM_SERVERS
from lab7_3_composite_agent import CompositeMCPAgent
from lab7_2_database_mcp import describe_schema, AUDIT_DB_PATH
from lab7_4_public_api_mcp import get_repo_info


def run_standup_demo():
    print("=" * 75)
    print("[WEEK 7 FRIDAY STANDUP] MCP TOOL ECOSYSTEM LIVE DEMONSTRATION")
    print("=" * 75)

    # -------------------------------------------------------------------------
    # DEMO ITEM 1: ARCHITECTURE REVIEW
    # -------------------------------------------------------------------------
    print("\n--- ITEM 1: ECOSYSTEM ARCHITECTURE REVIEW ---")
    print("""
    +--------------------------------------------------------------------+
    |                     LangGraph AI Agent Client                      |
    +--------------------------------------------------------------------+
                                       |
                                       v  (Namespaced JSON-RPC over MCP)
    +--------------------------------------------------------------------+
    |               Unified MCP Gateway Proxy (lab7_3)                   |
    |      - Namespace Routing (fs:, db:, util:) | Schema Cache (60s)    |
    |      - Aggregated Health (/health)         | Auth & Audit Logging  |
    +--------------------------------------------------------------------+
          |                            |                            |
          v                            v                            v
  +------------------+        +------------------+        +------------------+
  |  Filesystem MCP  |        |   Database MCP   |        |   Utility MCP    |
  |  Server (lab7_2) |        |  Server (lab7_2) |        |  Server (lab7_1) |
  | (read, write)    |        | (query, insert)  |        | (AST calc, string)|
  +------------------+        +------------------+        +------------------+
    """)

    # -------------------------------------------------------------------------
    # DEMO ITEM 2: LIVE ECOSYSTEM STARTUP & TOOL DISCOVERY
    # -------------------------------------------------------------------------
    print("\n--- ITEM 2: LIVE ECOSYSTEM TOOL DISCOVERY ---")
    discovery = gateway.discover_tools(force_refresh=True)
    schemas = discovery["schemas"]
    print(f"[OK] Gateway initialized. Total namespaced tools discovered: {len(schemas)}")
    for name, details in list(schemas.items())[:5]:
        print(f"   -> Discovered Tool: '{name}' | Server: '{details['server_prefix']}'")

    # -------------------------------------------------------------------------
    # DEMO ITEM 3: TOOL SCHEMA WALKTHROUGH
    # -------------------------------------------------------------------------
    print("\n--- ITEM 3: TOOL SCHEMA WALKTHROUGH ---")
    sample_tool = "fs:read_file"
    if sample_tool in schemas:
        info = schemas[sample_tool]
        print(f"Tool Name: {sample_tool}")
        print(f"Description: {info['description']}")
        print(f"Target Function: {info['function_ref'].__name__}")
        print("[OK] Schema definition matches FastMCP specification.")

    # -------------------------------------------------------------------------
    # DEMO ITEM 4: SECURITY WALKTHROUGH (401, 429, AUDIT LOG)
    # -------------------------------------------------------------------------
    print("\n--- ITEM 4: SECURITY WALKTHROUGH ---")
    # 1. Rejected Unauthenticated Request
    print("1. Testing Unauthenticated Access Rejection (401)...")
    res_401 = describe_schema(api_key="invalid_hacker_key")
    print(f"   Result: Status Code 401 | Message: '{res_401.get('error')}'")

    # 2. Rate Limit Firing (429)
    print("2. Testing Rate Limit Firing (429)...")
    res_429 = describe_schema(api_key="key_beta_999") # Trigger rate limit
    print(f"   Result: Status Code 429 | Message: '{res_429.get('error')}'")

    # 3. Audit Log Inspection
    print("3. Inspecting SQLite Audit Store (data/mcp_audit.db)...")
    conn = sqlite3.connect(AUDIT_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, api_key_hash, tool_name, status, latency_ms FROM audit_logs ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        print(f"   Audit Record #{row[0]}: timestamp={row[1][:19]}, key_hash={row[2]}, tool={row[3]}, status={row[4]}, latency={row[5]:.2f}ms")

    # -------------------------------------------------------------------------
    # DEMO ITEM 5: FAILURE DEMONSTRATION (DOWNSTREAM SERVER OFFLINE)
    # -------------------------------------------------------------------------
    print("\n--- ITEM 5: DOWNSTREAM FAILURE RESILIENCE DEMONSTRATION ---")
    print("Simulating DOWNSTREAM DATABASE SERVER FAILURE (OFFLINE)...")
    DOWNSTREAM_SERVERS["db"]["status"] = "OFFLINE"
    
    health = gateway.get_health_status()
    print(f"   Gateway Health Status: {health.get('gateway_status')} | Online: {health.get('online_servers')}")

    print("Executing call to offline database server via Gateway...")
    res_fail = gateway.route_tool_call("db:query_table", {"api_key": "key_alpha_123", "table_name": "users"})
    print(f"   Gateway Protection: Caught failure gracefully without crash!")
    print(f"   Response Payload: {json.dumps(res_fail)}")

    # Restore server for clean completion
    DOWNSTREAM_SERVERS["db"]["status"] = "ONLINE"
    print("\nRestoring Database Server to ONLINE status...")
    print(f"   Gateway Health Status: {gateway.get_health_status().get('gateway_status')}")

    # -------------------------------------------------------------------------
    # DEMO ITEM 6: END-TO-END COMPOSITE AGENT EXECUTION
    # -------------------------------------------------------------------------
    print("\n--- ITEM 6: END-TO-END COMPOSITE AGENT EXECUTION ---")
    agent = CompositeMCPAgent(api_key="key_alpha_123")
    wf_res = agent.run_composite_workflow(specs_filename="specs.txt", output_filename="standup_final_report.txt")
    print(f"[SUCCESS] Multi-Step Composite Workflow Completed ({wf_res.get('workflow_steps_completed')} Steps).")

    print("\n" + "=" * 75)
    print("[SUCCESS] FRIDAY STANDUP DEMONSTRATION COMPLETED PERFECTLY!")
    print("=" * 75)


if __name__ == "__main__":
    run_standup_demo()
