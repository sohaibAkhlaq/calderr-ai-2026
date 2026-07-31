"""
Autonomous Competitive Intelligence Agent - Command Line Interface (CLI)

Interactive CLI tool to execute multi-agent competitive research,
display progress, and export intelligence briefings.

Usage:
    python cli.py --company "Stripe" --output "stripe_briefing.md"
"""

import sys
import os
import argparse
from datetime import datetime

from graph import build_intelligence_graph
from schemas import CompetitiveBriefing
from agents import ReportGenerator


def main():
    parser = argparse.ArgumentParser(description="Autonomous Competitive Intelligence Agent CLI")
    parser.add_argument("--company", type=str, default="Stripe", help="Target company name for intelligence analysis")
    parser.add_argument("--output", type=str, default=None, help="Output file path (e.g. briefing.md or briefing.json)")
    parser.add_argument("--format", type=str, choices=["markdown", "json"], default="markdown", help="Export format")

    args = parser.parse_args()

    company = args.company.strip()
    print("=" * 70)
    print("AUTONOMOUS COMPETITIVE INTELLIGENCE AGENT")
    print(f"Target Company: {company}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)

    # Compile graph and run
    graph = build_intelligence_graph()

    initial_state = {
        "company_name": company,
        "plan": {},
        "raw_data": {},
        "market_report": {},
        "product_report": {},
        "tech_report": {},
        "news_report": {},
        "sentiment_report": {},
        "conflicts": [],
        "final_briefing": {},
        "total_tokens": 0,
        "start_time": 0.0,
        "messages": []
    }

    print("\n[PIPELINE START] Executing multi-agent parallel fan-out...")
    result_state = graph.invoke(initial_state)

    briefing_dict = result_state.get("final_briefing", {})
    briefing = CompetitiveBriefing(**briefing_dict)

    # Format report
    if args.format == "json":
        report_content = ReportGenerator.to_json(briefing)
    else:
        report_content = ReportGenerator.to_markdown(briefing)

    print("\n" + "=" * 70)
    print("COMPETITIVE BRIEFING SUMMARY")
    print("=" * 70)
    print(f"Company Analyzed: {briefing.company_name}")
    print(f"Total Tokens: {briefing.total_tokens}")
    print(f"Execution Latency: {briefing.execution_time_sec}s")
    print(f"Estimated API Cost: ${briefing.cost_usd}")
    print("-" * 70)
    print(f"Executive Summary:\n{briefing.executive_summary}\n")
    print(f"Conflicts Resolved: {len(briefing.conflicts_resolved)}")
    print("Strategic Recommendations:")
    for rec in briefing.strategic_recommendations:
        print(f"  - {rec}")
    print("=" * 70)

    # Save output file
    output_filename = args.output
    if not output_filename:
        ext = "json" if args.format == "json" else "md"
        output_filename = f"{company.lower().replace(' ', '_')}_intelligence_briefing.{ext}"

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"\n[REPORT SAVED] Successfully exported to: {os.path.abspath(output_filename)}")


if __name__ == "__main__":
    main()
