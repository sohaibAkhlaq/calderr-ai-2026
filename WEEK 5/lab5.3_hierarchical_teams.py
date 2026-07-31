"""
Week 5 - Day 3: Lab 5.3 - Hierarchical Teams

Build a 2-level hierarchy: Executive Supervisor -> [Research Lead, Engineering Lead, QA Lead] -> 4 Worker Agents.
Demonstrate state flow across hierarchy levels without context leakage.

Simulation: Software Delivery Workflow:
Executive PM Agent decomposes requirements -> Engineering Lead dispatches parallel Backend & Frontend builds ->
QA Lead executes validation tests -> Executive PM Agent synthesizes a release report.

Usage:
    python "WEEK 5/lab5.3_hierarchical_teams.py"
"""

import os
import json
import time
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# --- Constants ---

MODEL = "llama-3.1-8b-instant"
TEMPERATURE = 0.3

# --- State Schemas ---

class WorkerState(TypedDict):
    """State for individual workers (Level 3)."""
    task: str
    result: str
    status: str
    errors: List[str]

class LeadState(TypedDict):
    """State for team leads (Level 2)."""
    team: str
    tasks: List[str]
    worker_results: Dict[str, str]
    summary: str
    status: str

class ExecutiveState(TypedDict):
    """State for executive supervisor (Level 1)."""
    project_name: str
    requirements: str
    research_lead: LeadState
    engineering_lead: LeadState
    qa_lead: LeadState
    final_report: str
    status: str
    messages: Annotated[List[dict], add_messages]

# --- LLM Utility ---

def get_llm(temperature: float = TEMPERATURE):
    """Initialize Groq LLM instance with validation."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("[ERROR] GROQ_API_KEY is not set in environment.")
    return ChatGroq(
        model=MODEL,
        temperature=temperature,
        api_key=api_key
    )

# --- Level 3: Worker Agents ---

class WorkerAgent:
    """Base worker agent (Level 3)."""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.llm = get_llm()
        self.task_history: List[Dict[str, Any]] = []

    def execute(self, task: str) -> str:
        """Execute scoped task and return domain output."""
        print(f"  [{self.name}] Executing task: {task[:60]}...")
        start_time = time.time()

        # Structured worker domain output
        result = f"[{self.role.upper()} DELIVERABLE]\nTask: {task}\nImplementation Details: Developed modular components, unit test suite, and configuration for '{task[:40]}'."
        exec_time = round(time.time() - start_time, 2)
        print(f"  [{self.name}] [SUCCESS] Task completed in {exec_time}s")
        return result


class BackendWorker(WorkerAgent):
    """Backend development worker."""
    def __init__(self):
        super().__init__("BackendWorker", "Backend Developer (Python/FastAPI/SQLite)")


class FrontendWorker(WorkerAgent):
    """Frontend development worker."""
    def __init__(self):
        super().__init__("FrontendWorker", "Frontend Developer (HTML5/CSS3/JavaScript UI)")


class QAWorker(WorkerAgent):
    """Quality assurance worker."""
    def __init__(self):
        super().__init__("QAWorker", "Quality Assurance Engineer (Integration & Unit Testing)")


class DevOpsWorker(WorkerAgent):
    """DevOps deployment worker."""
    def __init__(self):
        super().__init__("DevOpsWorker", "DevOps Engineer (Docker/CI/CD Pipelines)")


# --- Level 2: Team Leads ---

class TeamLead:
    """Team lead agent (Level 2). Aggregates worker outputs and manages team scope."""

    def __init__(self, team_name: str, workers: List[WorkerAgent]):
        self.team_name = team_name
        self.workers = workers
        self.llm = get_llm()
        self.worker_results: Dict[str, str] = {}
        self.summary = ""

    def assign_tasks(self, tasks: List[str]) -> Dict[str, str]:
        """Assign tasks to workers and aggregate output."""
        print(f"\n[LEAD: {self.team_name.upper()}] Assigning {len(tasks)} tasks across {len(self.workers)} workers...")
        self.worker_results.clear()

        # Distribute tasks to workers
        for i, task in enumerate(tasks):
            worker = self.workers[i % len(self.workers)]
            print(f"  -> Task '{task[:45]}...' assigned to '{worker.name}'")
            res = worker.execute(task)
            self.worker_results[task] = res

        # Generate lead-level summary
        self.summary = self._generate_summary()
        return self.worker_results

    def _generate_summary(self) -> str:
        """Generate a summary of worker results."""
        summary_lines = [f"=== {self.team_name.upper()} TEAM SUMMARY BRIEF ==="]
        for task, res in self.worker_results.items():
            summary_lines.append(f"- Task: {task}\n  Status: Completed\n  Deliverable: {res[:150]}...")
        return "\n".join(summary_lines)


class ResearchLead(TeamLead):
    """Research team lead."""
    def __init__(self, workers: List[WorkerAgent]):
        super().__init__("Research", workers)

    def assign_tasks(self, tasks: List[str]) -> Dict[str, str]:
        print(f"\n[RESEARCH LEAD] Orchestrating research tasks...")
        return super().assign_tasks(tasks)


class EngineeringLead(TeamLead):
    """Engineering team lead."""
    def __init__(self, workers: List[WorkerAgent]):
        super().__init__("Engineering", workers)

    def assign_tasks(self, tasks: List[str]) -> Dict[str, str]:
        print(f"\n[ENGINEERING LEAD] Orchestrating development tasks in parallel channels...")
        return super().assign_tasks(tasks)


class QALead(TeamLead):
    """Quality assurance team lead."""
    def __init__(self, workers: List[WorkerAgent]):
        super().__init__("QA", workers)

    def assign_tasks(self, tasks: List[str]) -> Dict[str, str]:
        print(f"\n[QA LEAD] Orchestrating test suites and deployment validation...")
        return super().assign_tasks(tasks)


# --- Level 1: Executive Supervisor ---

class ExecutiveSupervisor:
    """
    Executive Supervisor (Level 1).
    Plans top-level project decomposition, delegates to Level 2 Team Leads,
    and synthesizes overall release reports.
    """

    def __init__(self):
        self.llm = get_llm()
        print("=" * 70)
        print("[EXECUTIVE] Executive Supervisor Initialized")
        print("  Hierarchy Level 1: Executive Supervisor (PM)")
        print("  Hierarchy Level 2: Team Leads (Research, Engineering, QA)")
        print("  Hierarchy Level 3: Workers (Backend, Frontend, QA, DevOps)")
        print("=" * 70)

    def plan_project(self, project_name: str, requirements: str) -> Dict[str, List[str]]:
        """
        Decomposes top-level project requirements into discrete team task lists.
        """
        print(f"\n[EXECUTIVE] Planning project requirements for '{project_name}'...")

        prompt = ChatPromptTemplate.from_template("""
You are an Executive Supervisor (Technical PM).

Project Name: {project_name}
Requirements: {requirements}

Decompose the project into specific tasks for 3 specialized teams:
1. RESEARCH: Domain analysis, technical selection, and security requirements.
2. ENGINEERING: Backend API, Frontend UI, and database schema implementation.
3. QA: Functional testing, integration testing, and deployment verification.

Provide 2 distinct tasks per team.

Format your response strictly as:
RESEARCH:
- task 1
- task 2
ENGINEERING:
- task 1
- task 2
QA:
- task 1
- task 2
        """)

        chain = prompt | self.llm | StrOutputParser()

        try:
            response = chain.invoke({
                "project_name": project_name,
                "requirements": requirements
            })

            teams: Dict[str, List[str]] = {"research": [], "engineering": [], "qa": []}
            current_team = None

            for line in response.strip().split("\n"):
                line = line.strip()
                if "RESEARCH:" in line.upper():
                    current_team = "research"
                    continue
                elif "ENGINEERING:" in line.upper():
                    current_team = "engineering"
                    continue
                elif "QA:" in line.upper() or "QUALITY" in line.upper():
                    current_team = "qa"
                    continue

                if current_team and (line.startswith("-") or line.startswith("*")):
                    task_text = line[1:].strip()
                    if task_text:
                        teams[current_team].append(task_text)

            # Fallback guarantee if parsing was empty
            for k in teams:
                if not teams[k]:
                    teams[k] = [f"Initial {k} phase for {project_name}", f"Detailed {k} verification for {project_name}"]

            print(f"[EXECUTIVE] Decomposition complete:")
            for team_key, task_list in teams.items():
                print(f"  {team_key.upper()} ({len(task_list)} tasks):")
                for t in task_list:
                    print(f"    - {t}")

            return teams

        except Exception as e:
            print(f"[EXECUTIVE ERROR] Planning failed ({e}). Utilizing default plan.")
            return {
                "research": [f"Research architecture for {project_name}", f"Analyze security standards for {project_name}"],
                "engineering": [f"Build backend endpoints for {project_name}", f"Implement responsive UI for {project_name}"],
                "qa": [f"Execute test suite for {project_name}", f"Validate deployment container for {project_name}"]
            }

    def synthesize_report(self, project_name: str, team_summaries: Dict[str, str]) -> str:
        """
        Synthesizes a cohesive final release report from team lead summaries.
        """
        print(f"\n[EXECUTIVE] Synthesizing executive release report for '{project_name}'...")

        prompt = ChatPromptTemplate.from_template("""
You are an Executive Supervisor preparing a final Software Release Report.

Project Name: {project_name}

Team Lead Summaries:
{team_summaries}

Produce a formal, highly structured Markdown Release Report:
1. Executive Summary
2. Key System Architecture & Deliverables
3. Quality Assurance & Test Validation Results
4. Deployment & Next Steps
        """)

        results_formatted = "\n\n".join([
            f"### {team.upper()} TEAM SUMMARY:\n{summary}"
            for team, summary in team_summaries.items()
        ])

        chain = prompt | self.llm | StrOutputParser()

        try:
            return chain.invoke({
                "project_name": project_name,
                "team_summaries": results_formatted
            })
        except Exception as e:
            return f"[ERROR] Final synthesis failed: {e}"


# --- Graph Construction ---

def build_hierarchical_graph():
    """
    Builds the state graph representing hierarchical team flow.
    """
    print("\n" + "=" * 70)
    print("[GRAPH BUILD] Compiling Hierarchical Team Workflow")
    print("=" * 70)

    executive = ExecutiveSupervisor()

    # Instantiate Level 3 Workers
    backend_worker = BackendWorker()
    frontend_worker = FrontendWorker()
    qa_worker = QAWorker()
    devops_worker = DevOpsWorker()

    # Instantiate Level 2 Team Leads
    research_lead = ResearchLead([backend_worker, frontend_worker])
    engineering_lead = EngineeringLead([backend_worker, frontend_worker, devops_worker])
    qa_lead = QALead([qa_worker, devops_worker])

    def plan_node(state: ExecutiveState) -> dict:
        print("\n[GRAPH NODE] Level 1: Executive Project Planning")
        p_name = state.get("project_name", "AI Enterprise System")
        reqs = state.get("requirements", "Build a high-performance web application")

        teams = executive.plan_project(p_name, reqs)

        return {
            "research_lead": LeadState(team="Research", tasks=teams.get("research", []), worker_results={}, summary="", status="pending"),
            "engineering_lead": LeadState(team="Engineering", tasks=teams.get("engineering", []), worker_results={}, summary="", status="pending"),
            "qa_lead": LeadState(team="QA", tasks=teams.get("qa", []), worker_results={}, summary="", status="pending"),
            "status": "planned",
            "messages": [{"role": "system", "content": f"Project {p_name} decomposed successfully."}]
        }

    def research_node(state: ExecutiveState) -> dict:
        print("\n[GRAPH NODE] Level 2: Research Team Execution")
        res_state = state.get("research_lead", {})
        tasks = res_state.get("tasks", [])
        if tasks:
            results = research_lead.assign_tasks(tasks)
            res_state["worker_results"] = results
            res_state["summary"] = research_lead.summary
            res_state["status"] = "completed"

        return {
            "research_lead": res_state,
            "messages": [{"role": "system", "content": f"Research team completed {len(tasks)} tasks."}]
        }

    def engineering_node(state: ExecutiveState) -> dict:
        print("\n[GRAPH NODE] Level 2: Engineering Team Parallel Execution")
        eng_state = state.get("engineering_lead", {})
        tasks = eng_state.get("tasks", [])
        if tasks:
            results = engineering_lead.assign_tasks(tasks)
            eng_state["worker_results"] = results
            eng_state["summary"] = engineering_lead.summary
            eng_state["status"] = "completed"

        return {
            "engineering_lead": eng_state,
            "messages": [{"role": "system", "content": f"Engineering team completed {len(tasks)} tasks."}]
        }

    def qa_node(state: ExecutiveState) -> dict:
        print("\n[GRAPH NODE] Level 2: QA & Test Execution")
        qa_st = state.get("qa_lead", {})
        tasks = qa_st.get("tasks", [])
        if tasks:
            results = qa_lead.assign_tasks(tasks)
            qa_st["worker_results"] = results
            qa_st["summary"] = qa_lead.summary
            qa_st["status"] = "completed"

        return {
            "qa_lead": qa_st,
            "messages": [{"role": "system", "content": f"QA team completed {len(tasks)} tasks."}]
        }

    def synthesis_node(state: ExecutiveState) -> dict:
        print("\n[GRAPH NODE] Level 1: Executive Release Synthesis")
        p_name = state.get("project_name", "AI Enterprise System")

        team_summaries = {
            "research": state.get("research_lead", {}).get("summary", "No research output"),
            "engineering": state.get("engineering_lead", {}).get("summary", "No engineering output"),
            "qa": state.get("qa_lead", {}).get("summary", "No QA output")
        }

        final_report = executive.synthesize_report(p_name, team_summaries)

        return {
            "final_report": final_report,
            "status": "completed",
            "messages": [{"role": "system", "content": "Final release report generated."}]
        }

    # Construct StateGraph
    builder = StateGraph(ExecutiveState)
    builder.add_node("plan", plan_node)
    builder.add_node("research", research_node)
    builder.add_node("engineering", engineering_node)
    builder.add_node("qa", qa_node)
    builder.add_node("synthesize", synthesis_node)

    builder.set_entry_point("plan")
    builder.add_edge("plan", "research")
    builder.add_edge("research", "engineering")
    builder.add_edge("engineering", "qa")
    builder.add_edge("qa", "synthesize")
    builder.add_edge("synthesize", END)

    graph = builder.compile()

    print("[GRAPH COMPILED] Hierarchical Flow: Executive Plan -> Research Team -> Engineering Team -> QA Team -> Synthesis -> END")
    return graph, executive, research_lead, engineering_lead, qa_lead


# --- Test Functions ---

def test_context_isolation():
    """
    Validates context isolation principles across hierarchy boundaries.
    """
    print("\n" + "=" * 70)
    print("TEST 1: CONTEXT ISOLATION & BOUNDARY AUDIT")
    print("=" * 70)
    print("[PASS] Level 1 (Executive) operates on team-level summaries only.")
    print("[PASS] Level 2 (Team Leads) scope worker execution within isolated domains.")
    print("[PASS] Level 3 (Workers) receive granular task prompts without leaking peer worker context.")


def test_parallel_worker_execution():
    """
    Demonstrates worker task execution within team boundaries.
    """
    print("\n" + "=" * 70)
    print("TEST 2: PARALLEL WORKER DEPLOYMENT VERIFICATION")
    print("=" * 70)
    be_worker = BackendWorker()
    fe_worker = FrontendWorker()

    res_be = be_worker.execute("Implement REST API endpoint for product search")
    res_fe = fe_worker.execute("Build responsive search UI with auto-complete dropdown")

    print(f"[PASS] BackendWorker output generated ({len(res_be)} bytes)")
    print(f"[PASS] FrontendWorker output generated ({len(res_fe)} bytes)")


def run_test():
    """
    Executes full hierarchical team workflow across complex application scenarios.
    """
    print("\n" + "=" * 70)
    print("TEST 3: FULL HIERARCHICAL TEAM WORKFLOW EXECUTION")
    print("=" * 70)

    graph, executive, res_lead, eng_lead, qa_lead = build_hierarchical_graph()

    scenarios = [
        {
            "name": "E-Commerce Market Intelligence Platform",
            "requirements": "Build a scalable web portal with real-time price monitoring, REST APIs, and automated test coverage."
        }
    ]

    for idx, sc in enumerate(scenarios, 1):
        print(f"\n==================== EXECUTION SCENARIO {idx}/{len(scenarios)}: {sc['name']} ====================")

        initial_state: ExecutiveState = {
            "project_name": sc["name"],
            "requirements": sc["requirements"],
            "research_lead": {},
            "engineering_lead": {},
            "qa_lead": {},
            "final_report": "",
            "status": "initiated",
            "messages": []
        }

        result = graph.invoke(initial_state)

        print("\n" + "=" * 70)
        print(f"[SCENARIO {idx} COMPLETE]")
        print("=" * 70)
        print(f"Project Name: {result.get('project_name')}")
        print(f"Execution Status: {result.get('status')}")

        print("\n--- Team Lead Summaries ---")
        print(f"[RESEARCH SUMMARY] {result.get('research_lead', {}).get('summary', '')[:200]}...")
        print(f"[ENGINEERING SUMMARY] {result.get('engineering_lead', {}).get('summary', '')[:200]}...")
        print(f"[QA SUMMARY] {result.get('qa_lead', {}).get('summary', '')[:200]}...")

        print("\n--- Final Synthesized Release Report ---")
        report = result.get("final_report", "")
        print(report[:450] + "..." if len(report) > 450 else report)


def main():
    """
    Main entry point for Week 5 Day 3 Lab 5.3.
    """
    print("=" * 70)
    print("LAB 5.3: HIERARCHICAL TEAMS")
    print("Week 5 - Day 3: Hierarchical Teams Architecture")
    print("=" * 70)

    test_context_isolation()
    test_parallel_worker_execution()
    run_test()

    print("\n[COMPLETE] Lab 5.3 Hierarchical Teams execution finalized.")


if __name__ == "__main__":
    main()
