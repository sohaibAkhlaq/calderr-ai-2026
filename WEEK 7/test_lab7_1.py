"""
Automated Verification Suite for Lab 7.1 (Three-Tool Production MCP Server).
Tests:
1. Tool Schema inspection & discovery
2. Tool 1: calculate (valid math expressions, zero division error, invalid syntax)
3. Tool 2: string_processor (upper, lower, reverse, word_count, snake_case, invalid operation)
4. Tool 3: date_helper (now, add_days, diff_days, format_date, invalid date format)
"""

import sys
import json
from lab7_1_first_mcp_server import calculate, string_processor, date_helper, mcp


def run_tests():
    print("=" * 70)
    print("[RUNNING AUTOMATED TESTS] LAB 7.1: THREE-TOOL MCP SERVER")
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
    # TEST GROUP 1: TOOL SCHEMA DISCOVERY
    # =========================================================================
    print("\n--- GROUP 1: TOOL SCHEMA DISCOVERY ---")
    try:
        import asyncio
        tools = asyncio.run(mcp.list_tools())
        tool_names = [t.name for t in tools]
        assert_test("Server Tool Count", len(tools) >= 3, f"Discovered tools: {tool_names}")
        assert_test("Has 'calculate'", "calculate" in tool_names, "Safe AST math tool registered.")
        assert_test("Has 'string_processor'", "string_processor" in tool_names, "String transformation tool registered.")
        assert_test("Has 'date_helper'", "date_helper" in tool_names, "Date helper tool registered.")
    except Exception as e:
        assert_test("Tool Schema Discovery", False, str(e))

    # =========================================================================
    # TEST GROUP 2: TOOL 1 — CALCULATOR
    # =========================================================================
    print("\n--- GROUP 2: TOOL 1 — CALCULATOR ---")
    res1 = calculate("25 * 4 + (100 / 2)")
    assert_test("Valid Expression", res1.get("success") is True and res1.get("result") == 150.0, f"Result: {res1.get('result')}")

    res2 = calculate("10 ** 3 - 50")
    assert_test("Exponentiation & Subtraction", res2.get("success") is True and res2.get("result") == 950, f"Result: {res2.get('result')}")

    res3 = calculate("10 / 0")
    assert_test("Division by Zero Error Catch", res3.get("success") is False and res3.get("error_type") == "ZeroDivisionError", f"Error: {res3.get('error')}")

    res4 = calculate("import os; os.system('echo hacked')")
    assert_test("Unsafe AST Expression Blocked", res4.get("success") is False, f"Blocked unsafe AST code safely. Error: {res4.get('error')}")

    # =========================================================================
    # TEST GROUP 3: TOOL 2 — STRING PROCESSOR
    # =========================================================================
    print("\n--- GROUP 3: TOOL 2 — STRING PROCESSOR ---")
    res_s1 = string_processor("Hello World MCP Protocol", "upper")
    assert_test("Operation 'upper'", res_s1.get("result") == "HELLO WORLD MCP PROTOCOL", f"Result: {res_s1.get('result')}")

    res_s2 = string_processor("Model Context Protocol", "reverse")
    assert_test("Operation 'reverse'", res_s2.get("result") == "locotorP txetnoC ledoM", f"Result: {res_s2.get('result')}")

    res_s3 = string_processor("Model Context Protocol 2026", "snake_case")
    assert_test("Operation 'snake_case'", res_s3.get("result") == "model_context_protocol_2026", f"Result: {res_s3.get('result')}")

    res_s4 = string_processor("Count the number of words in this string", "word_count")
    assert_test("Operation 'word_count'", res_s4.get("result") == 8, f"Word Count: {res_s4.get('result')}")

    res_s5 = string_processor("Test String", "invalid_op")
    assert_test("Invalid Operation Error Catch", res_s5.get("success") is False and res_s5.get("error_type") == "InvalidOperation", f"Error: {res_s5.get('error')}")

    # =========================================================================
    # TEST GROUP 4: TOOL 3 — DATE HELPER
    # =========================================================================
    print("\n--- GROUP 4: TOOL 3 — DATE HELPER ---")
    res_d1 = date_helper("now")
    assert_test("Action 'now'", res_d1.get("success") is True and "iso_datetime" in res_d1, f"Today Date: {res_d1.get('date')}")

    res_d2 = date_helper("add_days", date_str="2026-08-10", days=7)
    assert_test("Action 'add_days'", res_d2.get("result_date") == "2026-08-17", f"Result Date: {res_d2.get('result_date')}")

    res_d3 = date_helper("format_date", date_str="2026-08-10")
    assert_test("Action 'format_date'", "Monday" in res_d3.get("human_readable", ""), f"Formatted: {res_d3.get('human_readable')}")

    res_d4 = date_helper("add_days", date_str="invalid-date-string", days=5)
    assert_test("Invalid Date Parsing Error Catch", res_d4.get("success") is False and res_d4.get("error_type") == "DateFormatError", f"Error: {res_d4.get('error')}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("=" * 70)
    print(f"SUMMARY: Passed {passed_count}/{total_tests} tests ({(passed_count/total_tests)*100:.1f}%)")
    print("=" * 70)
    if failed_count == 0:
        print("[SUCCESS] ALL LAB 7.1 TESTS PASSED SUCCESSFULLY!")
    else:
        print(f"[WARNING] {failed_count} TEST(S) FAILED.")


if __name__ == "__main__":
    run_tests()
