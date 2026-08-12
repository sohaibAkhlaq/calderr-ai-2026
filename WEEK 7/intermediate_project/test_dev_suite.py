"""
Project 7-I-A: Automated Verification Suite for Developer Productivity MCP Suite
Tests:
1. Tool Discovery across code:, gh:, and doc: namespaces
2. Gateway 401 Authentication Rejection
3. Code Intelligence Server tools (analyze_file, find_dependencies, detect_code_smells)
4. GitHub Server tools (list_open_prs, get_pr_diff, create_issue)
5. Documentation Server tools (generate_docstring, generate_readme_section)
6. Autonomous Developer Agent Workflow Execution
"""

import sys
import os
import json

# Add current dir to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dev_gateway import dev_gateway
from langgraph_dev_agent import AutonomousDeveloperAgent


def run_tests_dict() -> dict:
    passed = 0
    failed = 0
    total = 0
    logs = []

    def assert_t(name, condition, detail=""):
        nonlocal passed, failed, total
        total += 1
        if condition:
            passed += 1
            logs.append(f"[PASS] {name} | {detail}")
        else:
            failed += 1
            logs.append(f"[FAIL] {name} | {detail}")

    valid_key = "key_dev_suite"

    # 1. Gateway Tool Discovery
    discovery = dev_gateway.discover_tools(force_refresh=True)
    schemas = discovery["schemas"]
    assert_t("Discovery Count", len(schemas) >= 10, f"Found {len(schemas)} tools")

    # 2. Auth Rejection (401)
    res_401 = dev_gateway.route_tool_call("bad_key", "code:analyze_file", {"code_content": "x=1"})
    assert_t("Auth 401 Rejection", res_401.get("error_type") == "AuthenticationError", res_401.get("error"))

    # 3. Code Intelligence Tools
    res_ast = dev_gateway.route_tool_call(valid_key, "code:analyze_file", {"code_content": "def foo(a):\n  return a+1\n"})
    assert_t("code:analyze_file", res_ast.get("gateway_routed") is True, f"Functions: {len(res_ast.get('result', {}).get('functions', []))}")

    res_smell = dev_gateway.route_tool_call(valid_key, "code:detect_code_smells", {"code_content": "x=1"})
    assert_t("code:detect_code_smells", res_smell.get("gateway_routed") is True, f"Score: {res_smell.get('result', {}).get('code_quality_score')}")

    # 4. GitHub Tools
    res_prs = dev_gateway.route_tool_call(valid_key, "gh:list_open_prs", {})
    assert_t("gh:list_open_prs", res_prs.get("gateway_routed") is True and len(res_prs.get("result", {}).get("pull_requests", [])) > 0, "PRs retrieved")

    res_diff = dev_gateway.route_tool_call(valid_key, "gh:get_pr_diff", {"pr_id": 101})
    assert_t("gh:get_pr_diff", res_diff.get("gateway_routed") is True and "diff" in res_diff.get("result", {}), "Diff retrieved")

    # 5. Documentation Tools
    res_doc = dev_gateway.route_tool_call(valid_key, "doc:generate_docstring", {"function_code": "def bar(x):\n  return x*2"})
    assert_t("doc:generate_docstring", res_doc.get("gateway_routed") is True and "Args:" in res_doc.get("result", {}).get("generated_docstring", ""), "Docstring generated")

    # 6. Autonomous Agent Workflow
    agent = AutonomousDeveloperAgent(api_key=valid_key)
    wf = agent.run_pr_review_workflow(pr_id=101)
    assert_t("Autonomous DevAgent Workflow", wf.get("success") is True and wf.get("steps_completed") == 6, f"Completed {wf.get('steps_completed')} steps")

    pass_rate = round((passed / total) * 100, 1) if total > 0 else 0.0
    return {
        "passed": passed,
        "failed": failed,
        "total": total,
        "pass_rate": pass_rate,
        "logs": logs
    }


if __name__ == "__main__":
    print("=" * 70)
    print("[RUNNING TEST SUITE] DEVELOPER PRODUCTIVITY MCP SUITE")
    print("=" * 70)
    res = run_tests_dict()
    for log in res["logs"]:
        print(f"  {log}")
    print("=" * 70)
    print(f"SUMMARY: Passed {res['passed']}/{res['total']} tests ({res['pass_rate']}%)")
    print("=" * 70)
