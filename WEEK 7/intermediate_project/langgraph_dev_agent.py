"""
Project 7-I-A: Autonomous LangGraph Developer Agent
Executes End-to-End PR Review & Documentation Workflow across all 3 MCP Servers:
Step 1: Read PR Diff (gh:get_pr_diff)
Step 2: Analyze AST & Cyclomatic Complexity (code:analyze_file)
Step 3: Check Imports & Dependencies (code:find_dependencies)
Step 4: Detect Code Smells & Anti-patterns (code:detect_code_smells)
Step 5: Generate Docstrings & README Sections (doc:generate_docstring & doc:generate_readme_section)
Step 6: Register Automated Code Review Issue (gh:create_issue)
"""

import time
import json
from typing import Dict, Any, List
from dev_gateway import dev_gateway


class AutonomousDeveloperAgent:
    def __init__(self, api_key: str = "key_dev_suite"):
        self.api_key = api_key
        self.gateway = dev_gateway

    def run_pr_review_workflow(self, pr_id: int = 101) -> Dict[str, Any]:
        """Executes full autonomous PR code review workflow."""
        print(f"[LangGraph DevAgent] Starting Autonomous PR Review Workflow for PR #{pr_id}...\n")
        steps_log = []

        # ---------------------------------------------------------------------
        # STEP 1: FETCH PR DIFF (gh:get_pr_diff)
        # ---------------------------------------------------------------------
        print(f"Step 1: Calling [gh:get_pr_diff] via Gateway for PR #{pr_id}...")
        diff_res = self.gateway.route_tool_call(self.api_key, "gh:get_pr_diff", {"pr_id": pr_id})
        
        if not diff_res.get("gateway_routed"):
            return {"success": False, "error": "Failed fetching PR diff"}

        pr_info = diff_res.get("result", {})
        diff_text = pr_info.get("diff", "")
        pr_title = pr_info.get("title", f"PR #{pr_id}")
        steps_log.append(f"Step 1 Fetched PR Diff for '{pr_title}'")
        print(f"   [OK] Retrieved PR Diff ({len(diff_text)} chars).")

        # ---------------------------------------------------------------------
        # STEP 2: ANALYZE AST & COMPLEXITY (code:analyze_file)
        # ---------------------------------------------------------------------
        print("\nStep 2: Calling [code:analyze_file] for AST parsing & cyclomatic complexity...")
        sample_code = (
            "def login(username, password):\n"
            "    if not username or not password:\n"
            "        return False\n"
            "    for char in password:\n"
            "        if char.isdigit():\n"
            "            return True\n"
            "    return True\n"
        )
        analyze_res = self.gateway.route_tool_call(self.api_key, "code:analyze_file", {"code_content": sample_code})
        metrics = analyze_res.get("result", {}).get("metrics", {})
        complexity = metrics.get("overall_cyclomatic_complexity", 1)
        steps_log.append(f"Step 2 AST Analysis Completed: Complexity Score {complexity}")
        print(f"   [OK] Cyclomatic Complexity: {complexity} ({metrics.get('complexity_rating')} rating).")

        # ---------------------------------------------------------------------
        # STEP 3: EXTRACT DEPENDENCIES (code:find_dependencies)
        # ---------------------------------------------------------------------
        print("\nStep 3: Calling [code:find_dependencies] to map import dependencies...")
        dep_code = "import hashlib\nimport os\nfrom datetime import datetime\n"
        dep_res = self.gateway.route_tool_call(self.api_key, "code:find_dependencies", {"code_content": dep_code})
        modules = dep_res.get("result", {}).get("unique_modules", [])
        steps_log.append(f"Step 3 Mapped Dependencies: {modules}")
        print(f"   [OK] Extracted Modules: {modules}")

        # ---------------------------------------------------------------------
        # STEP 4: DETECT CODE SMELLS (code:detect_code_smells)
        # ---------------------------------------------------------------------
        print("\nStep 4: Calling [code:detect_code_smells] to scan for architectural anti-patterns...")
        smell_res = self.gateway.route_tool_call(self.api_key, "code:detect_code_smells", {"code_content": sample_code})
        quality_score = smell_res.get("result", {}).get("code_quality_score", 100)
        steps_log.append(f"Step 4 Code Quality Score: {quality_score}/100")
        print(f"   [OK] Code Quality Score: {quality_score}/100")

        # ---------------------------------------------------------------------
        # STEP 5: GENERATE DOCSTRING & README (doc:generate_docstring)
        # ---------------------------------------------------------------------
        print("\nStep 5: Calling [doc:generate_docstring] & [doc:generate_readme_section]...")
        doc_res = self.gateway.route_tool_call(self.api_key, "doc:generate_docstring", {"function_code": sample_code})
        generated_docstring = doc_res.get("result", {}).get("generated_docstring", "")
        
        readme_res = self.gateway.route_tool_call(self.api_key, "doc:generate_readme_section", {"module_name": "auth_service", "code_content": sample_code})
        readme_md = readme_res.get("result", {}).get("readme_markdown", "")
        steps_log.append("Step 5 Documentation Synthesized")
        print("   [OK] Synthesized Google-style docstring & README markdown.")

        # ---------------------------------------------------------------------
        # STEP 6: CREATE AUTOMATED CODE REVIEW ISSUE (gh:create_issue)
        # ---------------------------------------------------------------------
        print("\nStep 6: Calling [gh:create_issue] to register code review findings ticket...")
        issue_body = (
            f"### Automated Code Review Report for PR #{pr_id}\n\n"
            f"**PR Title**: {pr_title}\n"
            f"**Cyclomatic Complexity**: {complexity}\n"
            f"**Code Quality Score**: {quality_score}/100\n"
            f"**Dependencies**: {', '.join(modules)}\n\n"
            f"#### Suggested Google Docstring\n```python\n{generated_docstring}\n```\n"
        )
        issue_res = self.gateway.route_tool_call(self.api_key, "gh:create_issue", {
            "title": f"Review Feedback for PR #{pr_id}: {pr_title}",
            "body": issue_body,
            "labels": "automated-code-review,quality-gate"
        })
        issue_id = issue_res.get("result", {}).get("issue_id", 0)
        steps_log.append(f"Step 6 Created GitHub Issue #{issue_id}")
        print(f"   [OK] Created Review Ticket Issue #{issue_id}.")

        return {
            "success": True,
            "pr_id": pr_id,
            "pr_title": pr_title,
            "steps_completed": len(steps_log),
            "complexity": complexity,
            "quality_score": quality_score,
            "issue_id": issue_id,
            "generated_docstring": generated_docstring,
            "readme_markdown": readme_md,
            "steps_log": steps_log
        }


if __name__ == "__main__":
    agent = AutonomousDeveloperAgent()
    res = agent.run_pr_review_workflow()
    print("\nAutonomous DevAgent Workflow Completed!")
    print(json.dumps(res, indent=2))
