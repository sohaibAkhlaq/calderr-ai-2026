"""
Automated Verification Suite for Lab 7.2 (Authenticated MCP Server with Audit Log & Rate Limiting).
Tests:
1. Authentication Enforcement (Invalid key returns 401 error)
2. Token Bucket Rate Limiting (11th request returns 429 error)
3. Database Tools (describe_schema, query_table, insert_record)
4. Filesystem Tools (write_file, read_file, list_directory)
5. SQLite Audit Log Persistence (Verifies records in data/mcp_audit.db)
6. Resource & Prompt Discovery
"""

import sqlite3
import os
import time
import json
import asyncio
from lab7_2_database_mcp import (
    describe_schema, query_table, insert_record,
    write_file, read_file, list_directory,
    mcp, AUDIT_DB_PATH, RATE_LIMIT_STORE
)


def run_tests():
    print("=" * 70)
    print("[RUNNING AUTOMATED TESTS] LAB 7.2: AUTHENTICATED MCP SERVER WITH AUDIT LOG")
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
    # TEST GROUP 1: AUTHENTICATION ENFORCEMENT
    # =========================================================================
    print("\n--- GROUP 1: AUTHENTICATION ENFORCEMENT ---")
    res_auth1 = describe_schema(api_key="invalid_bad_key")
    assert_test("Invalid Key Rejection (401)", res_auth1.get("success") is False and res_auth1.get("error_type") == "AuthenticationError", f"Error: {res_auth1.get('error')}")

    res_auth2 = describe_schema(api_key="")
    assert_test("Missing Key Rejection (401)", res_auth2.get("success") is False and res_auth2.get("error_type") == "AuthenticationError", f"Error: {res_auth2.get('error')}")

    # =========================================================================
    # TEST GROUP 2: DATABASE & FILESYSTEM TOOLS (VALID KEY)
    # =========================================================================
    print("\n--- GROUP 2: DATABASE & FILESYSTEM TOOLS ---")
    valid_key = "key_alpha_123"

    res_db1 = describe_schema(api_key=valid_key)
    assert_test("Database describe_schema", res_db1.get("success") is True and "users" in res_db1.get("tables", []), f"Tables: {res_db1.get('tables')}")

    res_db2 = query_table(api_key=valid_key, table_name="users", limit=5)
    assert_test("Database query_table", res_db2.get("success") is True and len(res_db2.get("records", [])) > 0, f"Record Count: {res_db2.get('count')}")

    res_db3 = insert_record(api_key=valid_key, name="Charlie Brown", email=f"charlie_{int(time.time())}@company.com", role="engineer")
    assert_test("Database insert_record", res_db3.get("success") is True and "inserted_id" in res_db3, f"Inserted ID: {res_db3.get('inserted_id')}")

    res_fs1 = write_file(api_key=valid_key, filename="test_notes.txt", content="MCP Day 2 Lab execution content.")
    assert_test("Filesystem write_file", res_fs1.get("success") is True and res_fs1.get("filename") == "test_notes.txt", f"Written bytes: {res_fs1.get('bytes_written')}")

    res_fs2 = read_file(api_key=valid_key, filename="test_notes.txt")
    assert_test("Filesystem read_file", res_fs2.get("success") is True and "MCP Day 2" in res_fs2.get("content", ""), f"Content: '{res_fs2.get('content')}'")

    res_fs3 = list_directory(api_key=valid_key)
    assert_test("Filesystem list_directory", res_fs3.get("success") is True and res_fs3.get("file_count") > 0, f"File count: {res_fs3.get('file_count')}")

    # =========================================================================
    # TEST GROUP 3: TOKEN BUCKET RATE LIMITING
    # =========================================================================
    print("\n--- GROUP 3: TOKEN BUCKET RATE LIMITING ---")
    rate_key = "key_beta_999"
    RATE_LIMIT_STORE[rate_key] = [] # Reset key bucket for clean test

    # Send 10 valid requests
    success_count = 0
    for i in range(10):
        r = describe_schema(api_key=rate_key)
        if r.get("success"):
            success_count += 1

    assert_test("First 10 Requests Allowed", success_count == 10, f"Allowed {success_count}/10 requests.")

    # 11th Request must fail with 429
    r_11 = describe_schema(api_key=rate_key)
    assert_test("11th Request Rate Limited (429)", r_11.get("success") is False and r_11.get("error_type") == "RateLimitExceeded", f"Error: {r_11.get('error')}")

    # =========================================================================
    # TEST GROUP 4: SQLITE AUDIT LOG PERSISTENCE
    # =========================================================================
    print("\n--- GROUP 4: SQLITE AUDIT LOG PERSISTENCE ---")
    conn = sqlite3.connect(AUDIT_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, api_key_hash, tool_name, status, latency_ms FROM audit_logs ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()

    assert_test("Audit Log Has Entries", len(rows) > 0, f"Logged entries count: {len(rows)}")
    if rows:
        latest = rows[0]
        assert_test("Audit Entry Schema Valid", len(latest) == 6 and latest[4] in ["SUCCESS", "FAILURE"], f"Latest audit log: tool='{latest[3]}', status='{latest[4]}', latency={latest[5]:.2f}ms")

    # =========================================================================
    # TEST GROUP 5: RESOURCES & PROMPT DISCOVERY
    # =========================================================================
    print("\n--- GROUP 5: RESOURCES & PROMPTS DISCOVERY ---")
    try:
        resources = asyncio.run(mcp.list_resources())
        prompts = asyncio.run(mcp.list_prompts())
        assert_test("Resource Provider Count", len(resources) >= 2, f"Resources registered: {[r.uri for r in resources]}")
        assert_test("Prompt Template Count", len(prompts) >= 2, f"Prompts registered: {[p.name for p in prompts]}")
    except Exception as e:
        assert_test("Resources & Prompts Discovery", False, str(e))

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("=" * 70)
    print(f"SUMMARY: Passed {passed_count}/{total_tests} tests ({(passed_count/total_tests)*100:.1f}%)")
    print("=" * 70)
    if failed_count == 0:
        print("[SUCCESS] ALL LAB 7.2 TESTS PASSED SUCCESSFULLY!")
    else:
        print(f"[WARNING] {failed_count} TEST(S) FAILED.")


if __name__ == "__main__":
    run_tests()
