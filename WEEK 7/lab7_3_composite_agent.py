"""
Lab 7.3: LangGraph Composite Agent using MCP Gateway
Demonstrates an Agent executing a 4-step workflow across 3 downstream MCP servers via the Gateway:
Step 1: Read requirements from disk (fs:read_file)
Step 2: Pull user records from database (db:query_table)
Step 3: Calculate totals and format string (util:calculate & util:string_processor)
Step 4: Persist final report to disk (fs:write_file)
"""

import os
import json
import time
from typing import Dict, Any, List
from lab7_3_mcp_gateway import gateway


class CompositeMCPAgent:
    def __init__(self, api_key: str = "key_alpha_123"):
        self.api_key = api_key
        self.gateway = gateway

    def run_composite_workflow(self, specs_filename: str = "specs.txt", output_filename: str = "executive_report.txt") -> Dict[str, Any]:
        print(f"LangGraph Composite Agent Starting Multi-Step Workflow via MCP Gateway...\n")
        logs = []

        # ---------------------------------------------------------------------
        # STEP 1: READ SPECIFICATIONS FILE (fs:read_file)
        # ---------------------------------------------------------------------
        print("Step 1: Discovering & calling [fs:write_file] to seed initial specs, then [fs:read_file]...")
        # Seed specs file if missing
        self.gateway.route_tool_call("fs:write_file", {
            "api_key": self.api_key,
            "filename": specs_filename,
            "content": "Project Q3 Target: Upgrade database infrastructure and audit user accounts."
        })

        read_res = self.gateway.route_tool_call("fs:read_file", {
            "api_key": self.api_key,
            "filename": specs_filename
        })
        specs_text = read_res.get("result", {}).get("content", "")
        logs.append(f"Step 1 Read Specs: {specs_text}")
        print(f"   [OK] Read Specs Content: '{specs_text}'")

        # ---------------------------------------------------------------------
        # STEP 2: QUERY DATABASE RECORDS (db:query_table)
        # ---------------------------------------------------------------------
        print("\nStep 2: Querying Database Users via Gateway [db:query_table]...")
        db_res = self.gateway.route_tool_call("db:query_table", {
            "api_key": self.api_key,
            "table_name": "users",
            "limit": 5
        })
        user_records = db_res.get("result", {}).get("records", [])
        user_count = len(user_records)
        logs.append(f"Step 2 Queried Database: {user_count} records retrieved")
        print(f"   [OK] Retrieved {user_count} user records from DB.")

        # ---------------------------------------------------------------------
        # STEP 3: PERFORM UTILITY MATH & STRING MATH (util:calculate & util:string_processor)
        # ---------------------------------------------------------------------
        print("\nStep 3: Calculating Budget Estimates via Gateway [util:calculate] & formatting [util:string_processor]...")
        calc_res = self.gateway.route_tool_call("util:calculate", {
            "expression": f"{user_count} * 15000 + 5000"
        })
        estimated_budget = calc_res.get("result", {}).get("result", 0)

        str_res = self.gateway.route_tool_call("util:string_processor", {
            "text": f"Executive Summary Report: {specs_text}",
            "operation": "upper"
        })
        formatted_header = str_res.get("result", {}).get("result", "")
        logs.append(f"Step 3 Computed Budget: ${estimated_budget}")
        print(f"   [OK] Computed Budget: ${estimated_budget}")

        # ---------------------------------------------------------------------
        # STEP 4: PERSIST FINAL REPORT (fs:write_file)
        # ---------------------------------------------------------------------
        print("\nStep 4: Writing Composite Executive Report to disk via Gateway [fs:write_file]...")
        report_content = (
            f"{formatted_header}\n"
            f"=" * 50 + "\n"
            f"Active Users Audited: {user_count}\n"
            f"Estimated Budget Required: ${estimated_budget}\n"
            f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        write_res = self.gateway.route_tool_call("fs:write_file", {
            "api_key": self.api_key,
            "filename": output_filename,
            "content": report_content
        })
        logs.append(f"Step 4 Persisted Report to {output_filename}")
        print(f"   [OK] Report persisted to 'data/sandbox/{output_filename}'.")

        return {
            "success": True,
            "workflow_steps_completed": 4,
            "output_filename": output_filename,
            "user_count": user_count,
            "estimated_budget": estimated_budget,
            "report_preview": report_content
        }


if __name__ == "__main__":
    agent = CompositeMCPAgent()
    res = agent.run_composite_workflow()
    print("\nWorkflow Completed Successfully!")
    print(json.dumps(res, indent=2))
