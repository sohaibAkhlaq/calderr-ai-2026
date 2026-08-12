"""
Automated Verification Suite for Lab 7.4 (Hardened Public API MCP Server).
Tests:
1. Header Authentication Validation (Invalid API Key returns 401 error)
2. Per-Endpoint Rate Limiting (6th search_github_code request returns 429 error)
3. Public API Wrapper: get_repo_info (stars, forks, open issues)
4. Developer Profile API Wrapper: get_user_profile (repos, followers)
5. Repository Health Analytics: analyze_repo_health (0-100 rating)
6. SQLite Security Audit Persistence (data/mcp_security_audit.db)
"""

import sqlite3
import os
import time
import asyncio
from lab7_4_public_api_mcp import (
    get_repo_info, search_github_code, get_user_profile,
    analyze_repo_health, mcp, AUDIT_DB_PATH, ENDPOINT_RATE_LIMITS
)


def run_tests():
    print("=" * 70)
    print("[RUNNING AUTOMATED TESTS] LAB 7.4: HARDENED PUBLIC API MCP SERVER")
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
    # TEST GROUP 1: HEADER AUTHENTICATION
    # =========================================================================
    print("\n--- GROUP 1: HEADER AUTHENTICATION ---")
    res_auth1 = get_repo_info(api_key="bad_unauthorized_key", owner="fastapi", repo="fastapi")
    assert_test("Invalid Key Rejection (401)", res_auth1.get("success") is False and res_auth1.get("error_type") == "AuthenticationError", f"Error: {res_auth1.get('error')}")

    # =========================================================================
    # TEST GROUP 2: PUBLIC API WRAPPERS (VALID KEY)
    # =========================================================================
    print("\n--- GROUP 2: PUBLIC API WRAPPERS ---")
    valid_key = "gh_key_alpha"

    res_repo = get_repo_info(api_key=valid_key, owner="fastapi", repo="fastapi")
    assert_test("Public API get_repo_info", res_repo.get("success") is True and "stars" in res_repo.get("repo_info", {}), f"Stars: {res_repo.get('repo_info', {}).get('stars')}")

    res_prof = get_user_profile(api_key=valid_key, username="tiangolo")
    assert_test("Developer Profile get_user_profile", res_prof.get("success") is True and "public_repos" in res_prof.get("profile", {}), f"Public Repos: {res_prof.get('profile', {}).get('public_repos')}")

    res_health = analyze_repo_health(api_key=valid_key, owner="fastapi", repo="fastapi")
    assert_test("Repo Health Analytics analyze_repo_health", res_health.get("success") is True and "health_score" in res_health, f"Health Score: {res_health.get('health_score')}/100, Rating: {res_health.get('rating')}")

    # =========================================================================
    # TEST GROUP 3: PER-ENDPOINT RATE LIMITING
    # =========================================================================
    print("\n--- GROUP 3: PER-ENDPOINT RATE LIMITING ---")
    rate_key = "gh_key_beta"
    key_tuple = (rate_key, "search_github_code")
    ENDPOINT_RATE_LIMITS[key_tuple] = [] # Reset for clean test

    # Send 5 allowed search requests
    allowed_count = 0
    for i in range(5):
        r = search_github_code(api_key=rate_key, query="mcp", language="python")
        if r.get("success"):
            allowed_count += 1

    assert_test("5 Search Requests Allowed", allowed_count == 5, f"Allowed: {allowed_count}/5")

    # 6th request must be rate limited with 429
    res_6th = search_github_code(api_key=rate_key, query="mcp", language="python")
    assert_test("6th Request Endpoint Rate Limited (429)", res_6th.get("success") is False and res_6th.get("error_type") == "RateLimitExceeded", f"Error: {res_6th.get('error')}")

    # =========================================================================
    # TEST GROUP 4: SQLITE SECURITY AUDIT PERSISTENCE
    # =========================================================================
    print("\n--- GROUP 4: SQLITE SECURITY AUDIT PERSISTENCE ---")
    conn = sqlite3.connect(AUDIT_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, api_key_hash, tool_name, status, latency_ms FROM security_audit_logs ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()

    assert_test("Security Audit Log Has Entries", len(rows) > 0, f"Logged events: {len(rows)}")
    if rows:
        latest = rows[0]
        assert_test("Audit Entry Schema Valid", len(latest) == 6 and latest[4] in ["SUCCESS", "FAILURE"], f"Latest Event: tool='{latest[3]}', status='{latest[4]}'")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("=" * 70)
    print(f"SUMMARY: Passed {passed_count}/{total_tests} tests ({(passed_count/total_tests)*100:.1f}%)")
    print("=" * 70)
    if failed_count == 0:
        print("[SUCCESS] ALL LAB 7.4 TESTS PASSED SUCCESSFULLY!")
    else:
        print(f"[WARNING] {failed_count} TEST(S) FAILED.")


if __name__ == "__main__":
    run_tests()
