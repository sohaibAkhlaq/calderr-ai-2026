"""
Automated Verification Suite for Lab 7.3 (MCP Gateway with Namespace Routing & Health Aggregation).
Tests:
1. Tool Discovery & Namespace Prefixing (fs:*, db:*, util:*)
2. Schema Caching (60-second TTL cache hit)
3. Transparent Namespace Routing to Downstream Servers
4. Gateway Aggregated Health Status (/health)
5. Graceful Downstream Failure Handling (Server Offline)
6. Composite Agent Multi-Step Workflow Execution
"""

import time
import json
from lab7_3_mcp_gateway import gateway, DOWNSTREAM_SERVERS
from lab7_3_composite_agent import CompositeMCPAgent


def run_tests():
    print("=" * 70)
    print("[RUNNING AUTOMATED TESTS] LAB 7.3: MCP GATEWAY WITH NAMESPACE ROUTING")
    print("=" * 70)

    passed_count = 0
    failed_count = 0
    total_tests = 0

    def assert_test(name, condition, detail=""):
        nonlocal passed_count, failed_count, total_tests
        total_tests += 1
        if condition:
            passed_count += 1
            print(f"  [PASS] {name} | {detail}")
        else:
            failed_count += 1
            print(f"  [FAIL] {name} | {detail}")

    # =========================================================================
    # TEST GROUP 1: TOOL DISCOVERY & NAMESPACE PREFIXING
    # =========================================================================
    print("\n--- GROUP 1: TOOL DISCOVERY & NAMESPACE PREFIXING ---")
    discovery = gateway.discover_tools(force_refresh=True)
    schemas = discovery["schemas"]
    tool_names = list(schemas.keys())

    assert_test("Gateway Tool Discovery Count", len(tool_names) >= 9, f"Discovered {len(tool_names)} namespaced tools.")
    assert_test("Has 'fs:read_file'", "fs:read_file" in tool_names, "Filesystem namespace registered.")
    assert_test("Has 'db:query_table'", "db:query_table" in tool_names, "Database namespace registered.")
    assert_test("Has 'util:calculate'", "util:calculate" in tool_names, "Utility namespace registered.")

    # =========================================================================
    # TEST GROUP 2: SCHEMA CACHING
    # =========================================================================
    print("\n--- GROUP 2: 60-SECOND SCHEMA CACHING ---")
    second_discovery = gateway.discover_tools(force_refresh=False)
    assert_test("Schema Cache Hit", second_discovery.get("cached") is True, "Returned cached schema registry within 60s TTL.")

    # =========================================================================
    # TEST GROUP 3: TRANSPARENT NAMESPACE ROUTING
    # =========================================================================
    print("\n--- GROUP 3: TRANSPARENT NAMESPACE ROUTING ---")
    valid_key = "key_alpha_123"

    res_fs = gateway.route_tool_call("fs:write_file", {"api_key": valid_key, "filename": "gw_test.txt", "content": "Gateway routed payload"})
    assert_test("Route 'fs:write_file'", res_fs.get("gateway_routed") is True and res_fs.get("server_prefix") == "fs", f"Latency: {res_fs.get('latency_ms')}ms")

    res_db = gateway.route_tool_call("db:query_table", {"api_key": valid_key, "table_name": "users", "limit": 2})
    assert_test("Route 'db:query_table'", res_db.get("gateway_routed") is True and res_db.get("server_prefix") == "db", f"Server: {res_db.get('server_prefix')}")

    res_util = gateway.route_tool_call("util:calculate", {"expression": "500 * 2"})
    assert_test("Route 'util:calculate'", res_util.get("gateway_routed") is True and res_util.get("result", {}).get("result") == 1000, f"Result: {res_util.get('result')}")

    # =========================================================================
    # TEST GROUP 4: AGGREGATED HEALTH MONITORING (/health)
    # =========================================================================
    print("\n--- GROUP 4: AGGREGATED HEALTH MONITORING (/health) ---")
    health = gateway.get_health_status()
    assert_test("Overall Gateway Status", health.get("gateway_status") == "HEALTHY", f"Status: {health.get('gateway_status')}")
    assert_test("Online Server Ratio", health.get("online_servers") == "3/3", f"Online ratio: {health.get('online_servers')}")

    # =========================================================================
    # TEST GROUP 5: DOWNSTREAM FAILURE HANDLING
    # =========================================================================
    print("\n--- GROUP 5: DOWNSTREAM FAILURE HANDLING ---")
    # Simulate DB server offline
    DOWNSTREAM_SERVERS["db"]["status"] = "OFFLINE"
    res_off = gateway.route_tool_call("db:query_table", {"api_key": valid_key, "table_name": "users"})
    assert_test("Offline Server Rejection", res_off.get("error_type") == "ServerOfflineError", f"Gracefully rejected offline server call. Error: {res_off.get('error')}")

    # Restore DB server
    DOWNSTREAM_SERVERS["db"]["status"] = "ONLINE"

    # =========================================================================
    # TEST GROUP 6: COMPOSITE AGENT MULTI-STEP WORKFLOW
    # =========================================================================
    print("\n--- GROUP 6: COMPOSITE AGENT WORKFLOW EXECUTION ---")
    agent = CompositeMCPAgent(api_key=valid_key)
    wf_res = agent.run_composite_workflow(specs_filename="specs.txt", output_filename="executive_report.txt")
    assert_test("Composite Agent Execution", wf_res.get("success") is True and wf_res.get("workflow_steps_completed") == 4, f"Steps Completed: {wf_res.get('workflow_steps_completed')}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("=" * 70)
    print(f"SUMMARY: Passed {passed_count}/{total_tests} tests ({(passed_count/total_tests)*100:.1f}%)")
    print("=" * 70)
    if failed_count == 0:
        print("[SUCCESS] ALL LAB 7.3 TESTS PASSED SUCCESSFULLY!")
    else:
        print(f"[WARNING] {failed_count} TEST(S) FAILED.")


if __name__ == "__main__":
    run_tests()
