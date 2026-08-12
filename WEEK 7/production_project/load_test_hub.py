"""
Production Project 7-P-A: 50 Concurrent Tool Calls Load Test Benchmark
Simulates high-concurrency enterprise load against the Universal Enterprise Tool Hub.
Measures:
- Total Calls: 50 concurrent tool calls
- Success Rate (%)
- Average Latency (ms)
- 95th Percentile Latency (target < 2000ms / 2.0 seconds)
"""

import time
import json
import concurrent.futures
from hub_gateway import hub_gateway

TOTAL_CONCURRENT_CALLS = 50
API_KEY = "key_enterprise_admin"

TEST_CALLS = [
    ("fs:list_directory", {}),
    ("db:query_table", {"table_name": "accounts"}),
    ("comm:check_calendar", {}),
    ("analytics:compute_statistics", {"metric_name": "revenue_usd"}),
    ("code:analyze_file", {"code_content": "def test(): return True\n"})
]


def execute_single_call(idx: int):
    target_tool, kwargs = TEST_CALLS[idx % len(TEST_CALLS)]
    start_t = time.time()
    res = hub_gateway.route_tool_call(API_KEY, target_tool, kwargs)
    duration_ms = (time.time() - start_t) * 1000
    success = res.get("gateway_routed", False) or res.get("success", False)
    return {"idx": idx, "tool": target_tool, "success": success, "latency_ms": duration_ms}


def run_load_test() -> dict:
    print("=" * 70)
    print(f"[RUNNING BENCHMARK] 50 CONCURRENT TOOL CALLS LOAD TEST")
    print("=" * 70)

    start_total = time.time()
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(execute_single_call, i) for i in range(TOTAL_CONCURRENT_CALLS)]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    total_duration_sec = time.time() - start_total
    latencies = [r["latency_ms"] for r in results]
    success_count = sum(1 for r in results if r["success"])

    latencies.sort()
    p95_index = int(0.95 * len(latencies)) - 1
    p95_latency = latencies[max(0, p95_index)]
    avg_latency = sum(latencies) / len(latencies)

    print(f"Total Calls Executed: {len(results)}")
    print(f"Success Rate: {success_count}/{len(results)} ({(success_count/len(results))*100:.1f}%)")
    print(f"Total Load Test Duration: {total_duration_sec:.2f} seconds")
    print(f"Average Latency: {avg_latency:.2f} ms")
    print(f"95th Percentile Latency: {p95_latency:.2f} ms (Target < 2000 ms)")

    status = "PASS" if (p95_latency < 2000.0 and success_count == TOTAL_CONCURRENT_CALLS) else "FAIL"
    print(f"Benchmark Status: [{status}]")

    return {
        "total_calls": TOTAL_CONCURRENT_CALLS,
        "success_count": success_count,
        "success_rate": (success_count / len(results)) * 100,
        "total_duration_sec": round(total_duration_sec, 2),
        "avg_latency_ms": round(avg_latency, 2),
        "p95_latency_ms": round(p95_latency, 2),
        "status": status
    }


if __name__ == "__main__":
    run_load_test()
