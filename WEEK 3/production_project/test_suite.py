"""
test_suite.py — Automated Health Check for Real-Time Research Engine
=====================================================================
Week 3 Production Project (Day 7)

Your lead can run this script to verify the full backend pipeline
without launching the Streamlit UI.

Usage:
    python test_suite.py

Exit codes:
    0 — All tests passed
    1 — One or more tests failed
"""

# MUST be set before torch/sentence-transformers import on Windows
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import sys
import json
import time


# ─── Color codes for terminal output ─────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

PASS_LABEL = f"{GREEN}{BOLD}[PASS]{RESET}"
FAIL_LABEL = f"{RED}{BOLD}[FAIL]{RESET}"
INFO_LABEL = f"{BLUE}{BOLD}[INFO]{RESET}"
WARN_LABEL = f"{YELLOW}{BOLD}[WARN]{RESET}"

sys.path.insert(0, os.path.dirname(__file__))
from engine import ResearchEngine, ResearchEngineError


# ─── Test definitions ─────────────────────────────────────────────────────────

EVALUATION_QUERIES = [
    {
        "query": "What is the Transformer architecture?",
        "expected_keywords": ["transformer", "attention", "encoder", "decoder"],
        "topic": "Transformer Architecture",
    },
    {
        "query": "How does scaled dot-product attention work?",
        "expected_keywords": ["query", "key", "value", "softmax"],
        "topic": "Transformer Architecture",
    },
    {
        "query": "What optimizer was used for training the Transformer?",
        "expected_keywords": ["adam"],
        "topic": "Transformer Architecture",
    },
    {
        "query": "What are positional encodings and why are they needed?",
        "expected_keywords": ["positional", "encoding", "sequence"],
        "topic": "Transformer Architecture",
    },
    {
        "query": "How many encoder layers does the base Transformer model have?",
        "expected_keywords": ["6", "layers", "stack"],
        "topic": "Transformer Architecture",
    },
    {
        "query": "What is BERT and how is it different from a standard language model?",
        "expected_keywords": ["bert", "bidirectional"],
        "topic": "BERT & Language Models",
    },
    {
        "query": "How is BERT pre-trained?",
        "expected_keywords": ["masked", "language", "pre-training"],
        "topic": "BERT & Language Models",
    },
    {
        "query": "What tasks was BERT fine-tuned on?",
        "expected_keywords": ["fine-tun", "classification", "squad"],
        "topic": "BERT & Language Models",
    },
    {
        "query": "What is multi-head attention?",
        "expected_keywords": ["heads", "parallel", "attention"],
        "topic": "Transformer Architecture",
    },
    {
        "query": "What regularization was used to prevent overfitting?",
        "expected_keywords": ["dropout"],
        "topic": "Transformer Architecture",
    },
]


def banner(title: str):
    print(f"\n{BOLD}{'═' * 65}{RESET}")
    print(f"{BOLD}  {title}{RESET}")
    print(f"{BOLD}{'═' * 65}{RESET}")


def run_tests():
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "tests": [],
    }

    banner("REAL-TIME RESEARCH ENGINE — TEST SUITE")
    print(f"{INFO_LABEL}  Running automated health checks and evaluation queries.\n")

    # ── Test 1: Engine initialization ─────────────────────────────────────────
    print(f"{BOLD}[ Phase 1: Pipeline Initialization ]{RESET}")
    engine = ResearchEngine()

    log_lines = []
    def on_progress(msg):
        log_lines.append(msg)
        print(f"  {INFO_LABEL} {msg}")

    t0 = time.time()
    status = engine.initialize(progress_callback=on_progress)
    elapsed = time.time() - t0

    results["total"] += 1
    if status.ready:
        print(f"\n  {PASS_LABEL} Engine initialized in {elapsed:.1f}s | {status.chunks_loaded} chunks loaded")
        results["passed"] += 1
        results["tests"].append({"test": "Engine Initialization", "status": "PASS"})
    else:
        print(f"\n  {FAIL_LABEL} Engine failed at stage: {status.stage_failed}")
        print(f"  {RED}  Error: {status.error}{RESET}")
        results["failed"] += 1
        results["tests"].append({
            "test": "Engine Initialization",
            "status": "FAIL",
            "error": status.error,
        })
        # If the engine failed to initialize, skip all search tests
        _write_results(results)
        return 1

    # ── Test 2: Validate chunk count ──────────────────────────────────────────
    print(f"\n{BOLD}[ Phase 2: Vector Store Validation ]{RESET}")
    results["total"] += 1
    if status.chunks_loaded >= 50:
        print(f"  {PASS_LABEL} Chunk count: {status.chunks_loaded} (threshold: ≥50)")
        results["passed"] += 1
        results["tests"].append({"test": "Chunk Count Validation", "status": "PASS", "chunks": status.chunks_loaded})
    else:
        print(f"  {FAIL_LABEL} Too few chunks: {status.chunks_loaded} (expected ≥50)")
        results["failed"] += 1
        results["tests"].append({"test": "Chunk Count Validation", "status": "FAIL"})

    # ── Test 3: Empty query handling ──────────────────────────────────────────
    results["total"] += 1
    try:
        empty_results = engine.search("")
        if empty_results == []:
            print(f"  {PASS_LABEL} Empty query returns [] (correct)")
            results["passed"] += 1
            results["tests"].append({"test": "Empty Query Handling", "status": "PASS"})
        else:
            print(f"  {FAIL_LABEL} Empty query should return [] but returned {len(empty_results)} results")
            results["failed"] += 1
            results["tests"].append({"test": "Empty Query Handling", "status": "FAIL"})
    except Exception as e:
        print(f"  {FAIL_LABEL} Empty query raised unexpected exception: {e}")
        results["failed"] += 1
        results["tests"].append({"test": "Empty Query Handling", "status": "FAIL", "error": str(e)})

    # ── Test 4: Evaluation queries ────────────────────────────────────────────
    print(f"\n{BOLD}[ Phase 3: Evaluation Queries ({len(EVALUATION_QUERIES)} queries) ]{RESET}")

    total_relevancy = 0.0
    for i, item in enumerate(EVALUATION_QUERIES):
        query   = item["query"]
        keywords = item["expected_keywords"]
        results["total"] += 1

        try:
            search_results = engine.search(query)
            if not search_results:
                raise ValueError("No results returned")

            # Check if any expected keyword appears in top result content
            top_content = search_results[0].content.lower()
            found_keywords = [kw for kw in keywords if kw.lower() in top_content]
            relevancy = len(found_keywords) / len(keywords)
            total_relevancy += relevancy

            if relevancy >= 0.5:
                status_label = PASS_LABEL
                results["passed"] += 1
                test_status = "PASS"
            else:
                status_label = FAIL_LABEL
                results["failed"] += 1
                test_status = "FAIL"

            print(
                f"  Q{i+1:02d} {status_label} "
                f"R:{relevancy:.2f} | Score:{search_results[0].score:.2f} | "
                f"{query[:55]}{'...' if len(query) > 55 else ''}"
            )

            results["tests"].append({
                "test": f"Q{i+1:02d}: {query}",
                "status": test_status,
                "relevancy": round(relevancy, 2),
                "reranker_score": round(search_results[0].score, 2),
                "top_result_excerpt": search_results[0].content[:120],
            })

        except Exception as e:
            print(f"  Q{i+1:02d} {FAIL_LABEL} Error: {e}")
            results["failed"] += 1
            results["tests"].append({"test": f"Q{i+1:02d}: {query}", "status": "FAIL", "error": str(e)})

    avg_relevancy = total_relevancy / len(EVALUATION_QUERIES)

    # ── Summary ───────────────────────────────────────────────────────────────
    banner("TEST SUMMARY")
    print(f"  Total Tests  : {results['total']}")
    print(f"  {GREEN}Passed{RESET}       : {results['passed']}")
    print(f"  {RED}Failed{RESET}       : {results['failed']}")
    print(f"  Pass Rate    : {results['passed'] / results['total'] * 100:.1f}%")
    print(f"  Avg Relevancy: {avg_relevancy:.2f}")

    results["summary"] = {
        "total": results["total"],
        "passed": results["passed"],
        "failed": results["failed"],
        "pass_rate": round(results["passed"] / results["total"] * 100, 1),
        "avg_query_relevancy": round(avg_relevancy, 2),
    }

    _write_results(results)

    if results["failed"] == 0:
        print(f"\n  {GREEN}{BOLD}All tests passed! Engine is production-ready.{RESET}\n")
        return 0
    else:
        print(f"\n  {YELLOW}{BOLD}{results['failed']} test(s) failed. Review test_results.json for details.{RESET}\n")
        return 1


def _write_results(results: dict):
    out_path = os.path.join(os.path.dirname(__file__), "test_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  {INFO_LABEL} Results saved to: {out_path}")


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
