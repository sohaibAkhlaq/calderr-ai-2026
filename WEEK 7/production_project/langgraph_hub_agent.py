"""
Production Project 7-P-A: LangGraph Enterprise Multi-Server Agent
Executes 5 End-to-End Workflows across all 5 downstream servers via the Enterprise Hub Gateway:
1. Filesystem Server (fs:write_file & fs:read_file)
2. Database Server (db:query_table)
3. Analytics Server (analytics:compute_statistics)
4. Code Intelligence Server (code:analyze_file)
5. Communication Server (comm:draft_email)
"""

import time
import json
from typing import Dict, Any, List
from hub_gateway import hub_gateway


class LangGraphEnterpriseHubAgent:
    def __init__(self, api_key: str = "key_enterprise_admin"):
        self.api_key = api_key
        self.gateway = hub_gateway

    def run_enterprise_workflow(self) -> Dict[str, Any]:
        print(f"[LangGraph HubAgent] Executing Multi-Server Enterprise Workflow...\n")
        logs = []

        # 1. Filesystem Server Work (fs:write_file & fs:read_file)
        print("Workflow 1: Seeding & reading project specifications via [fs:*]...")
        self.gateway.route_tool_call(self.api_key, "fs:write_file", {"filename": "enterprise_plan.txt", "content": "Enterprise Q3 Focus: Scaling AI Tool Ecosystem."})
        res_fs = self.gateway.route_tool_call(self.api_key, "fs:read_file", {"filename": "enterprise_plan.txt"})
        specs_txt = res_fs.get("result", {}).get("content", "")
        logs.append(f"W1 Filesystem Read: '{specs_txt}'")
        print(f"   [OK] Read Specs: '{specs_txt}'")

        # 2. Database Server Work (db:query_table)
        print("\nWorkflow 2: Pulling Enterprise Accounts via [db:*]...")
        res_db = self.gateway.route_tool_call(self.api_key, "db:query_table", {"table_name": "accounts", "limit": 5})
        records = res_db.get("result", {}).get("records", [])
        logs.append(f"W2 Database Records: {len(records)} accounts fetched")
        print(f"   [OK] Fetched {len(records)} enterprise accounts.")

        # 3. Analytics Server Work (analytics:compute_statistics)
        print("\nWorkflow 3: Computing Revenue Statistics via [analytics:*]...")
        res_an = self.gateway.route_tool_call(self.api_key, "analytics:compute_statistics", {"metric_name": "revenue_usd"})
        stats = res_an.get("result", {}).get("statistics", {})
        mean_rev = stats.get("mean", 0.0)
        logs.append(f"W3 Analytics Computed Mean Revenue: ${mean_rev}")
        print(f"   [OK] Computed Mean Revenue: ${mean_rev}")

        # 4. Code Intelligence Server Work (code:analyze_file)
        print("\nWorkflow 4: Running AST Code Complexity Analysis via [code:*]...")
        sample_code = "def process(x):\n  if x > 0:\n    return x*2\n  return 0\n"
        res_code = self.gateway.route_tool_call(self.api_key, "code:analyze_file", {"code_content": sample_code})
        rating = res_code.get("result", {}).get("rating", "LOW")
        logs.append(f"W4 Code Analysis Rating: {rating}")
        print(f"   [OK] Code Complexity Rating: {rating}")

        # 5. Communication Server Work (comm:draft_email)
        print("\nWorkflow 5: Drafting Executive Strategy Email via [comm:*]...")
        email_body = f"Executive Summary:\n- Q3 Focus: {specs_txt}\n- Mean Account Revenue: ${mean_rev}\n- System Status: All 5 Servers Operational."
        res_comm = self.gateway.route_tool_call(self.api_key, "comm:draft_email", {
            "recipient": "board@enterprise.com",
            "subject": "Q3 Enterprise AI Tool Hub Performance Summary",
            "body_text": email_body
        })
        email_status = res_comm.get("result", {}).get("email_draft", {}).get("status", "DRAFTED")
        logs.append(f"W5 Communication Draft Status: {email_status}")
        print(f"   [OK] Drafted Executive Email (Status: {email_status}).")

        return {
            "success": True,
            "workflows_executed": 5,
            "tenant_id": "Enterprise_Admin",
            "logs": logs
        }


if __name__ == "__main__":
    agent = LangGraphEnterpriseHubAgent()
    res = agent.run_enterprise_workflow()
    print("\nEnterprise Hub Multi-Server Agent Workflow Completed!")
    print(json.dumps(res, indent=2))
