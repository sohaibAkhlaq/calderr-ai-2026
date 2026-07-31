"""
Autonomous AI Research Lab - Command Line Interface (CLI)

Interactive CLI tool to execute 5-phase autonomous deep research,
display real-time progress logs across all phases, and export reports.

Usage:
    python cli.py --question "Evaluate multi-agent orchestration frameworks for enterprise production" --output "research_report.md"
"""

import sys
import os
import time
import argparse
from datetime import datetime

from graph import build_research_graph
from schemas import ResearchReport
from agents import ReportPublisher


def main():
    parser = argparse.ArgumentParser(description="Autonomous AI Research Lab CLI")
    parser.add_argument("--question", type=str, default="Evaluate multi-agent orchestration frameworks for enterprise production", help="Target research question")
    parser.add_argument("--output", type=str, default=None, help="Output file path (e.g. report.md or report.json)")
    parser.add_argument("--format", type=str, choices=["markdown", "json"], default="markdown", help="Export format")

    args = parser.parse_args()
    q = args.question.strip()

    print("=" * 70)
    print("AUTONOMOUS AI RESEARCH LAB - 5-PHASE EXECUTION ENGINE")
    print(f"Research Question: {q}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)

    # Compile 5-phase graph and execute
    graph = build_research_graph()

    report_id = f"rep_{int(time.time()*1000)}"
    initial_state = {
        "question": q,
        "report_id": report_id,
        "domain": {},
        "hypothesis": {},
        "evidence_gathered": [],
        "critic_challenges": [],
        "synthesis_body": "",
        "citations": [],
        "peer_review": {},
        "final_report": {},
        "total_tokens": 0,
        "start_time": 0.0,
        "messages": []
    }

    print("\n[RESEARCH PIPELINE START] Launching 5-phase autonomous deep research workflow...")
    result_state = graph.invoke(initial_state)

    report_dict = result_state.get("final_report", {})
    report = ResearchReport(**report_dict)

    if args.format == "json":
        output_text = ReportPublisher.to_json(report)
    else:
        output_text = ReportPublisher.to_markdown(report)

    print("\n" + "=" * 70)
    print("AUTONOMOUS RESEARCH REPORT SUMMARY")
    print("=" * 70)
    print(f"Report ID: {report.report_id}")
    print(f"Title: {report.title}")
    print(f"Domain: {report.domain}")
    print(f"Peer Review Status: {report.peer_review.approval_status} (Rigor: {report.peer_review.methodological_rigor*100:.0f}%)")
    print(f"Total Tokens: {report.total_tokens}")
    print(f"Execution Latency: {report.execution_time_sec}s")
    print(f"Estimated Cost: ${report.cost_usd}")
    print("-" * 70)
    print(f"Executive Summary:\n{report.executive_summary}\n")
    print(f"Evidence Items Gathered: {len(report.evidence_gathered)}")
    print(f"Critic Challenges Resolved: {len(report.critic_challenges)}")
    print(f"Peer Review Notes:\n  {report.peer_review.reviewer_notes}")
    print("=" * 70)

    # Save output file
    output_filename = args.output
    if not output_filename:
        ext = "json" if args.format == "json" else "md"
        output_filename = f"autonomous_research_{report_id}.{ext}"

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(output_text)

    print(f"\n[REPORT PUBLISHED] Successfully saved to: {os.path.abspath(output_filename)}")


if __name__ == "__main__":
    main()
