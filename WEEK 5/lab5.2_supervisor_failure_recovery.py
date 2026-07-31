"""
Week 5 - Day 2: Lab 5.2 - Supervisor with Failure Recovery

Build a Supervisor Agent that delegates to 3 specialist agents.
Inject failures into specialists (random timeout, low-confidence response).
The supervisor detects failure types, logs reasoning for re-routing,
tries alternative agents, and produces a gracefully degraded response if all alternatives fail.

Usage:
    python "WEEK 5/lab5.2_supervisor_failure_recovery.py"
"""

import os
import json
import time
import random
from typing import TypedDict, List, Dict, Any, Optional, Annotated, Literal
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

MAX_RETRIES = 3
TIMEOUT_SECONDS = 2
MODEL = "llama-3.1-8b-instant"
TEMPERATURE = 0.3

# --- State Schema ---

class SupervisorState(TypedDict):
    """State for the supervisor workflow."""

    # Input
    user_task: str
    task_decomposition: List[str]

    # Delegation
    current_subtask: str
    current_agent: str
    agent_assignments: Dict[str, str]  # subtask -> agent

    # Results
    subtask_results: Dict[str, str]    # subtask -> result
    agent_results: Dict[str, Any]      # agent -> result

    # Failure Tracking
    failed_agents: List[str]
    attempts: int
    max_attempts: int

    # Control
    is_complete: bool
    final_response: str
    decision_log: List[Dict[str, Any]]

    # Messages
    messages: Annotated[List[dict], add_messages]

# --- Message Schemas ---

class TaskRequest(BaseModel):
    """Request sent to a specialist agent."""
    task_id: str = Field(description="Unique task identifier")
    description: str = Field(description="Task description")
    instructions: List[str] = Field(description="Step-by-step instructions")
    priority: int = Field(default=3, description="Priority level (1-5)")

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("priority must be between 1 and 5")
        return v

class TaskResult(BaseModel):
    """Result from a specialist agent."""
    task_id: str = Field(description="Task identifier")
    result: str = Field(description="Task result")
    confidence: float = Field(description="Confidence score (0.0 to 1.0)")
    agent_name: str = Field(description="Agent that produced the result")
    execution_time: float = Field(description="Execution time in seconds")
    success: bool = Field(default=True)
    error: Optional[str] = Field(default=None)

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if v < 0.0 or v > 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        return v

class ErrorReport(BaseModel):
    """Error report from an agent."""
    task_id: str = Field(description="Task identifier")
    error_message: str = Field(description="Error description")
    error_type: Literal["timeout", "validation", "low_confidence", "internal"] = Field(
        description="Error type"
    )
    agent_name: str = Field(description="Agent that reported the error")

# --- Specialist Agents ---

class SpecialistAgent:
    """
    Base class for specialist agents with failure injection support.
    """

    def __init__(self, name: str, specialization: str, failure_modes: Optional[List[str]] = None):
        self.name = name
        self.specialization = specialization
        self.failure_modes = failure_modes or []
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("[ERROR] GROQ_API_KEY is missing from environment.")

        self.llm = ChatGroq(
            model=MODEL,
            temperature=TEMPERATURE,
            api_key=api_key
        )
        self.task_history: List[Dict[str, Any]] = []
        print(f"[AGENT INIT] {name} initialized.")
        print(f"  Specialization: {specialization}")
        print(f"  Failure Modes Configured: {failure_modes}")

    def process_task(self, task: TaskRequest) -> TaskResult:
        """
        Process a task request with potential failure injection.
        """
        print(f"\n[{self.name}] Processing task: {task.description}")
        print(f"  Task ID: {task.task_id} | Priority: {task.priority}")

        start_time = time.time()

        # Failure injection check
        failure_type = None
        if self.failure_modes:
            if random.random() < 0.5:
                failure_type = random.choice(self.failure_modes)

        # 1. Simulate timeout failure
        if failure_type == "timeout":
            print(f"  [TIMEOUT] {self.name} encountered execution timeout...")
            time.sleep(TIMEOUT_SECONDS + 0.5)
            return TaskResult(
                task_id=task.task_id,
                result="",
                confidence=0.0,
                agent_name=self.name,
                execution_time=round(TIMEOUT_SECONDS + 0.5, 2),
                success=False,
                error="Execution timeout exceeded"
            )

        # 2. Simulate low confidence response
        if failure_type == "low_confidence":
            print(f"  [LOW CONFIDENCE] {self.name} generating low-confidence output...")
            confidence = round(random.uniform(0.15, 0.35), 2)
        else:
            confidence = round(random.uniform(0.78, 0.95), 2)

        # Process standard request via LLM
        try:
            prompt = ChatPromptTemplate.from_template("""
You are a {specialization} specialist agent.

Task: {task}
Instructions: {instructions}

Provide a comprehensive, professional response detailing key findings and domain analysis.
            """)

            chain = prompt | self.llm | StrOutputParser()

            result_text = chain.invoke({
                "specialization": self.specialization,
                "task": task.description,
                "instructions": "\n".join(task.instructions)
            })

            execution_time = round(time.time() - start_time, 2)

            task_result = TaskResult(
                task_id=task.task_id,
                result=result_text,
                confidence=confidence,
                agent_name=self.name,
                execution_time=execution_time,
                success=True
            )

            self.task_history.append({
                "task_id": task.task_id,
                "success": True,
                "confidence": confidence,
                "time": execution_time
            })

            print(f"  [SUCCESS] {self.name} completed task in {execution_time}s")
            print(f"  [CONFIDENCE] Score: {confidence}")

            return task_result

        except Exception as e:
            execution_time = round(time.time() - start_time, 2)
            print(f"  [ERROR] {self.name} failed with exception: {e}")

            return TaskResult(
                task_id=task.task_id,
                result="",
                confidence=0.0,
                agent_name=self.name,
                execution_time=execution_time,
                success=False,
                error=str(e)
            )


class MarketResearchAgent(SpecialistAgent):
    """Market research specialist."""
    def __init__(self, failure_modes: Optional[List[str]] = None):
        super().__init__("MarketResearchAgent", "market research and market sizing analysis", failure_modes)


class CompetitiveIntelligenceAgent(SpecialistAgent):
    """Competitive intelligence specialist."""
    def __init__(self, failure_modes: Optional[List[str]] = None):
        super().__init__("CompetitiveIntelligenceAgent", "competitive landscape and benchmark intelligence", failure_modes)


class TechnologyResearchAgent(SpecialistAgent):
    """Technology research specialist."""
    def __init__(self, failure_modes: Optional[List[str]] = None):
        super().__init__("TechnologyResearchAgent", "emerging technology trends and architectural analysis", failure_modes)


class FallbackAgent(SpecialistAgent):
    """Fallback agent for graceful degradation when primary specialists fail."""

    def __init__(self):
        super().__init__("FallbackAgent", "graceful degradation and contingency reporting", [])

    def process_task(self, task: TaskRequest) -> TaskResult:
        """
        Process task with guaranteed partial output (graceful degradation).
        """
        print(f"\n[FALLBACK] Activating Fallback Agent for Task ID: {task.task_id}")
        start_time = time.time()

        degraded_summary = f"""
[GRACEFUL DEGRADATION REPORT]
Task: {task.description}

Primary specialist execution was degraded due to timeouts or low confidence thresholds.
Partial Contingency Brief:
1. High-level Context: The task requires dedicated domain breakdown.
2. System Diagnostics: Primary specialists experienced non-fatal execution faults or low confidence scores.
3. Recommended Action: Re-issue sub-query with narrowed focus or increased timeout thresholds.
        """.strip()

        execution_time = round(time.time() - start_time, 2)

        return TaskResult(
            task_id=task.task_id,
            result=degraded_summary,
            confidence=0.40,
            agent_name=self.name,
            execution_time=execution_time,
            success=True
        )


# --- Supervisor Agent ---

class SupervisorAgent:
    """
    Supervisor Agent orchestrates task decomposition, specialist delegation,
    failure detection, dynamic rerouting, and decision logging.
    """

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("[ERROR] GROQ_API_KEY is missing from environment.")

        self.llm = ChatGroq(
            model=MODEL,
            temperature=TEMPERATURE,
            api_key=api_key
        )
        self.decision_log: List[Dict[str, Any]] = []
        self.max_attempts = MAX_RETRIES

        # Instantiate specialist agents with injected failure modes
        self.agents: Dict[str, SpecialistAgent] = {
            "market": MarketResearchAgent(failure_modes=["low_confidence", "timeout"]),
            "competitive": CompetitiveIntelligenceAgent(failure_modes=["timeout"]),
            "technology": TechnologyResearchAgent(failure_modes=["low_confidence"]),
            "fallback": FallbackAgent()
        }

        print("=" * 70)
        print("[SUPERVISOR] Supervisor Agent Initialized")
        print(f"  Registered Agents: {list(self.agents.keys())}")
        print(f"  Max Retries per Subtask: {self.max_attempts}")
        print("=" * 70)

    def decompose_task(self, task: str) -> List[str]:
        """
        Decomposes a complex user prompt into specific subtasks.
        """
        print(f"\n[SUPERVISOR] Decomposing complex task: {task}")

        prompt = ChatPromptTemplate.from_template("""
You are an expert Task Decomposition Supervisor.

Break down the following complex task into 3 distinct, concrete subtasks.
Each subtask must be self-contained for execution by specialized agents.

Task: {task}

Output ONLY a numbered list of subtasks (1. ..., 2. ..., 3. ...).
        """)

        chain = prompt | self.llm | StrOutputParser()

        try:
            response = chain.invoke({"task": task})
            subtasks = []
            for line in response.strip().split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-")):
                    if line[0].isdigit() and ". " in line:
                        line = line.split(". ", 1)[1]
                    elif line.startswith("- "):
                        line = line[2:]
                    subtasks.append(line.strip())

            if not subtasks:
                subtasks = [f"Market analysis for: {task}", f"Competitive analysis for: {task}", f"Tech overview for: {task}"]

            print(f"[SUPERVISOR] Task decomposed into {len(subtasks)} subtasks:")
            for i, st in enumerate(subtasks, 1):
                print(f"  {i}. {st}")

            return subtasks

        except Exception as e:
            print(f"[SUPERVISOR ERROR] Task decomposition failed ({e}). Using default decomposition.")
            return [
                f"Analyze market aspect of: {task}",
                f"Evaluate competitive landscape of: {task}",
                f"Assess technology impact of: {task}"
            ]

    def select_agent(self, subtask: str, previous_attempts: Optional[List[str]] = None) -> str:
        """
        Selects the best specialist agent for a subtask, avoiding failed previous attempts.
        """
        previous_attempts = previous_attempts or []
        subtask_lower = subtask.lower()

        # Match primary specialization keywords
        if "market" in subtask_lower or "size" in subtask_lower or "growth" in subtask_lower:
            primary_agent = "market"
        elif "competitor" in subtask_lower or "competitive" in subtask_lower or "landscape" in subtask_lower:
            primary_agent = "competitive"
        elif "technology" in subtask_lower or "tech" in subtask_lower or "emerging" in subtask_lower:
            primary_agent = "technology"
        else:
            primary_agent = "market"

        selected_agent = primary_agent

        # Reroute if primary agent already failed
        if primary_agent in previous_attempts:
            available_specialists = [a for a in ["market", "competitive", "technology"] if a not in previous_attempts]
            if available_specialists:
                selected_agent = available_specialists[0]
            else:
                selected_agent = "fallback"

        decision_entry = {
            "timestamp": datetime.now().isoformat(),
            "subtask": subtask,
            "selected_agent": selected_agent,
            "primary_preference": primary_agent,
            "previous_attempts": list(previous_attempts),
            "reasoning": f"Primary preference '{primary_agent}' selected." if selected_agent == primary_agent else f"Rerouted to '{selected_agent}' after failures."
        }
        self.decision_log.append(decision_entry)

        print(f"[SUPERVISOR ROUTER] Selected '{selected_agent}' for subtask: '{subtask[:50]}...'")
        if previous_attempts:
            print(f"  Previous Failed Attempts: {previous_attempts}")

        return selected_agent

    def execute_subtask(self, subtask: str, agent_name: str, task_id: str) -> TaskResult:
        """
        Dispatches subtask to target agent.
        """
        agent = self.agents.get(agent_name)
        if not agent:
            return TaskResult(
                task_id=task_id,
                result="",
                confidence=0.0,
                agent_name=agent_name,
                execution_time=0.0,
                success=False,
                error=f"Agent '{agent_name}' not found."
            )

        task_request = TaskRequest(
            task_id=task_id,
            description=subtask,
            instructions=["Provide thorough research analysis", "Include explicit reasoning"],
            priority=3
        )

        return agent.process_task(task_request)

    def handle_subtask_with_recovery(self, subtask: str, task_id: str) -> TaskResult:
        """
        Handles subtask execution with retry logic, failure detection, and fallback rerouting.
        """
        previous_attempts: List[str] = []
        agent_name = self.select_agent(subtask)

        while True:
            result = self.execute_subtask(subtask, agent_name, task_id)

            # Check if output is successful and meets confidence threshold (>= 0.50)
            if result.success and result.confidence >= 0.50:
                print(f"[SUPERVISOR SUCCESS] Subtask completed by '{agent_name}' (Confidence: {result.confidence})")
                return result

            # Detect failure mode
            if not result.success:
                failure_type = "timeout_or_error"
                print(f"[SUPERVISOR FAILURE DETECTED] Agent '{agent_name}' failed with error: {result.error}")
            elif result.confidence < 0.50:
                failure_type = "low_confidence"
                print(f"[SUPERVISOR LOW CONFIDENCE] Agent '{agent_name}' returned score {result.confidence} (< 0.50)")
            else:
                failure_type = "unknown"

            previous_attempts.append(agent_name)

            self.decision_log.append({
                "timestamp": datetime.now().isoformat(),
                "subtask": subtask,
                "failed_agent": agent_name,
                "failure_type": failure_type,
                "action": "reroute_or_fallback"
            })

            # Check if max retries exceeded
            if len(previous_attempts) >= self.max_attempts:
                print(f"[SUPERVISOR FALLBACK] All retry attempts {previous_attempts} exhausted. Routing to FallbackAgent...")
                return self.execute_subtask(subtask, "fallback", f"{task_id}_fallback")

            # Reroute to alternative agent
            agent_name = self.select_agent(subtask, previous_attempts)
            print(f"[SUPERVISOR REROUTE] Retrying subtask with alternative agent '{agent_name}'...")


# --- LangGraph Graph Construction ---

def build_supervisor_graph():
    """
    Builds and compiles the LangGraph StateGraph workflow for Supervisor execution.
    """
    print("\n" + "=" * 70)
    print("[GRAPH BUILD] Compiling LangGraph Supervisor Workflow")
    print("=" * 70)

    supervisor = SupervisorAgent()

    def decompose_node(state: SupervisorState) -> dict:
        print("\n[GRAPH NODE] Task Decomposition Node")
        user_task = state.get("user_task", "")
        subtasks = supervisor.decompose_task(user_task)
        return {
            "task_decomposition": subtasks,
            "messages": [{"role": "system", "content": f"Decomposed into {len(subtasks)} subtasks."}]
        }

    def execute_node(state: SupervisorState) -> dict:
        print("\n[GRAPH NODE] Subtask Execution & Recovery Node")
        subtasks = state.get("task_decomposition", [])
        subtask_results = {}
        failed_agents = []

        for idx, subtask in enumerate(subtasks, 1):
            task_id = f"st_{idx}_{int(time.time()*1000)}"
            print(f"\n[GRAPH EXEC] Processing Subtask {idx}/{len(subtasks)}...")

            res = supervisor.handle_subtask_with_recovery(subtask, task_id)
            subtask_results[subtask] = res.result

            if not res.success or res.confidence < 0.50:
                failed_agents.append(res.agent_name)

        final_response_parts = []
        for st, res_text in subtask_results.items():
            final_response_parts.append(f"Subtask: {st}\nResult: {res_text[:300]}...\n")
        final_response = "\n".join(final_response_parts)

        return {
            "subtask_results": subtask_results,
            "failed_agents": failed_agents,
            "decision_log": supervisor.decision_log,
            "is_complete": True,
            "final_response": final_response,
            "messages": [{"role": "system", "content": f"Executed {len(subtasks)} subtasks."}]
        }

    builder = StateGraph(SupervisorState)
    builder.add_node("decompose", decompose_node)
    builder.add_node("execute", execute_node)

    builder.set_entry_point("decompose")
    builder.add_edge("decompose", "execute")
    builder.add_edge("execute", END)

    graph = builder.compile()

    print("[GRAPH COMPILED] Flow: decompose -> execute -> END")
    return graph, supervisor


# --- Test Functions ---

def test_failure_modes():
    """
    Directly tests failure mode injections across specialist agents.
    """
    print("\n" + "=" * 70)
    print("TEST 1: DIRECT FAILURE MODE INJECTION CHECKS")
    print("=" * 70)

    agents = [
        MarketResearchAgent(failure_modes=["low_confidence", "timeout"]),
        CompetitiveIntelligenceAgent(failure_modes=["timeout"]),
        TechnologyResearchAgent(failure_modes=["low_confidence"])
    ]

    for agent in agents:
        print(f"\n--- Testing Agent: {agent.name} ---")
        req = TaskRequest(
            task_id=f"test_id_{agent.name}",
            description="Evaluate competitive benchmarking patterns",
            instructions=["Analyze performance metrics"],
            priority=3
        )
        res = agent.process_task(req)
        print(f"  Result Success: {res.success}")
        print(f"  Confidence Score: {res.confidence}")
        print(f"  Execution Error: {res.error}")


def run_test():
    """
    Runs full supervisor state graph workflow across complex research tasks.
    """
    print("\n" + "=" * 70)
    print("TEST 2: SUPERVISOR GRAPH WORKFLOW EXECUTION")
    print("=" * 70)

    graph, supervisor = build_supervisor_graph()

    test_tasks = [
        "Analyze enterprise AI adoption trends and key competitive players in healthcare for 2026",
        "Investigate modern LLM orchestration frameworks and market size expansion"
    ]

    for idx, task in enumerate(test_tasks, 1):
        print(f"\n==================== RUNNING TEST WORKFLOW {idx}/{len(test_tasks)} ====================")
        initial_state: SupervisorState = {
            "user_task": task,
            "task_decomposition": [],
            "current_subtask": "",
            "current_agent": "",
            "agent_assignments": {},
            "subtask_results": {},
            "agent_results": {},
            "failed_agents": [],
            "attempts": 0,
            "max_attempts": MAX_RETRIES,
            "is_complete": False,
            "final_response": "",
            "decision_log": [],
            "messages": []
        }

        result = graph.invoke(initial_state)

        print("\n" + "=" * 70)
        print(f"[TEST WORKFLOW {idx} COMPLETE]")
        print("=" * 70)
        print(f"User Task: {task}")
        print(f"Subtasks Generated: {len(result.get('task_decomposition', []))}")
        print(f"Completed Results: {len(result.get('subtask_results', {}))}")
        print(f"Decision Log Entries recorded: {len(result.get('decision_log', []))}")

        print("\n--- Decision Log Audit Snippets ---")
        for entry in result.get("decision_log", [])[-4:]:
            print(f"  - {entry}")

        print("\n--- Final Aggregated Response Summary ---")
        resp = result.get("final_response", "")
        print(resp[:400] + "..." if len(resp) > 400 else resp)


def main():
    """
    Main entry point for Week 5 Day 2 Lab 5.2.
    """
    print("=" * 70)
    print("LAB 5.2: SUPERVISOR WITH FAILURE RECOVERY")
    print("Week 5 - Day 2: Supervisor Pattern")
    print("=" * 70)

    test_failure_modes()
    run_test()

    print("\n[COMPLETE] Lab 5.2 Supervisor with Failure Recovery execution finalized.")


if __name__ == "__main__":
    main()
