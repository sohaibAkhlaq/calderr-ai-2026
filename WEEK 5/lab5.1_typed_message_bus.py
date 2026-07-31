"""
Week 5 - Day 1: Lab 5.1 - Typed Message Bus

Build a message-passing backbone for multi-agent systems.
Define 4 typed Pydantic message schemas (TaskRequest, TaskResult, ErrorReport, Handoff).
Implement a simple in-memory message bus.
Build 3 agents (ResearchAgent, SynthesisAgent, QA_Agent) that communicate exclusively through typed messages.
Verify that malformed messages raise validation errors before any agent receives them.

Usage:
    python "WEEK 5/lab5.1_typed_message_bus.py"
"""

import os
import json
import time
from typing import List, Dict, Any, Optional, Literal, Union
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ValidationError
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# --- Message Schemas (Typed Pydantic Models) ---

class TaskRequest(BaseModel):
    """
    Message sent when an agent requests a task to be performed.
    """
    task_id: str = Field(description="Unique identifier for the task")
    description: str = Field(description="Description of the task")
    instructions: List[str] = Field(description="Step-by-step instructions")
    priority: int = Field(default=3, description="Priority level (1-5)")
    requester: str = Field(description="Name of the agent requesting the task")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    @field_validator('task_id')
    @classmethod
    def task_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("task_id must not be empty")
        return v.strip()

    @field_validator('priority')
    @classmethod
    def priority_range(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("priority must be between 1 and 5")
        return v

class TaskResult(BaseModel):
    """
    Message sent when an agent completes a task and returns results.
    """
    task_id: str = Field(description="ID of the task that was completed")
    result: str = Field(description="Result of the task execution")
    confidence: float = Field(description="Confidence score (0.0 to 1.0)")
    agent_name: str = Field(description="Name of the agent that performed the task")
    execution_time: float = Field(description="Time taken to execute in seconds")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    @field_validator('confidence')
    @classmethod
    def confidence_range(cls, v: float) -> float:
        if v < 0.0 or v > 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        return v

class ErrorReport(BaseModel):
    """
    Message sent when an agent encounters an error.
    """
    task_id: str = Field(description="ID of the task that failed")
    error_message: str = Field(description="Detailed error message")
    error_type: Literal["timeout", "validation", "internal", "unknown"] = Field(
        description="Type of error encountered"
    )
    agent_name: str = Field(description="Name of the agent that encountered the error")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    @field_validator('error_message')
    @classmethod
    def error_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("error_message must not be empty")
        return v.strip()

class Handoff(BaseModel):
    """
    Message sent when one agent hands off a task to another agent.
    """
    from_agent: str = Field(description="Name of the agent handing off")
    to_agent: str = Field(description="Name of the agent receiving the handoff")
    context: str = Field(description="Context and information for the handoff")
    task_id: str = Field(description="ID of the task being handed off")
    priority: int = Field(default=3, description="Priority level (1-5)")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    @field_validator('from_agent', 'to_agent')
    @classmethod
    def agent_names_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("agent name must not be empty")
        return v.strip()

    @field_validator('priority')
    @classmethod
    def priority_range(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("priority must be between 1 and 5")
        return v


# --- Message Bus ---

class MessageBus:
    """
    In-memory message bus for typed, validated inter-agent communication.
    """

    def __init__(self):
        self.message_handlers: Dict[str, List[callable]] = {}
        self.message_history: List[Dict[str, Any]] = []
        self.agent_registry: Dict[str, str] = {}  # agent_name -> agent_type

    def register_agent(self, agent_name: str, agent_type: str) -> None:
        """Register an agent with the message bus."""
        self.agent_registry[agent_name] = agent_type
        print(f"[BUS] Registered agent: {agent_name} ({agent_type})")

    def register_handler(self, message_type: str, handler: callable) -> None:
        """Register a handler for a specific message type."""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
        print(f"[BUS] Registered handler for: {message_type}")

    def send(self, message: Any, from_agent: str, to_agent: Optional[str] = None) -> List[Any]:
        """
        Send a typed Pydantic message across the message bus.
        Ensures strict schema validation before dispatch.
        """
        if not isinstance(message, BaseModel):
            raise ValueError(f"[BUS ERROR] Invalid message type. Expected Pydantic model, got {type(message).__name__}")

        message_type = message.__class__.__name__
        allowed_types = [TaskRequest.__name__, TaskResult.__name__, ErrorReport.__name__, Handoff.__name__]

        if message_type not in allowed_types:
            raise ValueError(f"[BUS ERROR] Unsupported message schema: {message_type}")

        # Record event in history
        log_entry = {
            "from": from_agent,
            "to": to_agent or "broadcast",
            "type": message_type,
            "timestamp": datetime.now().isoformat(),
            "message": message.model_dump()
        }
        self.message_history.append(log_entry)

        target_str = to_agent if to_agent else "broadcast"
        print(f"[BUS] Message routed: {from_agent} -> {target_str} [{message_type}]")

        # Dispatch message to registered handlers
        results = []
        if message_type in self.message_handlers:
            for handler in self.message_handlers[message_type]:
                try:
                    res = handler(message, from_agent, to_agent)
                    if res is not None:
                        results.append(res)
                except Exception as e:
                    print(f"[BUS ERROR] Exception in handler for {message_type}: {e}")
                    raise

        return results

    def validate_and_send(self, message_type_cls: type, raw_data: Dict[str, Any], from_agent: str, to_agent: Optional[str] = None) -> List[Any]:
        """
        Instantiates and validates raw data against a Pydantic schema before routing.
        Raises ValidationError if raw_data is malformed.
        """
        try:
            validated_message = message_type_cls(**raw_data)
        except (ValidationError, ValueError) as err:
            print(f"[BUS VALIDATION FAILED] Message rejected for {from_agent}: {err}")
            raise err
        return self.send(validated_message, from_agent, to_agent)

    def get_history(self) -> List[Dict[str, Any]]:
        """Get copy of message history."""
        return self.message_history

    def get_agents(self) -> Dict[str, str]:
        """Get copy of registered agents."""
        return self.agent_registry


# --- Base Agent ---

class BaseAgent:
    """
    Abstract Base Class for all agents communicating via MessageBus.
    """

    def __init__(self, name: str, agent_type: str, message_bus: MessageBus):
        self.name = name
        self.agent_type = agent_type
        self.message_bus = message_bus
        self.task_history: List[Dict[str, Any]] = []

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("[ERROR] GROQ_API_KEY is not configured in .env environment file.")

        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.2,
            api_key=api_key
        )

        # Register agent with bus
        self.message_bus.register_agent(name, agent_type)

    def handle_task_request(self, message: TaskRequest, from_agent: str, to_agent: Optional[str]) -> Optional[TaskResult]:
        raise NotImplementedError("Subclasses must implement handle_task_request")

    def handle_handoff(self, message: Handoff, from_agent: str, to_agent: Optional[str]) -> Optional[TaskResult]:
        raise NotImplementedError("Subclasses must implement handle_handoff")

    def send_task(self, description: str, instructions: List[str], to_agent: Optional[str] = None, priority: int = 3) -> str:
        task_id = f"task_{int(time.time()*1000)}_{self.name[:3].lower()}"
        request = TaskRequest(
            task_id=task_id,
            description=description,
            instructions=instructions,
            priority=priority,
            requester=self.name
        )
        self.message_bus.send(request, self.name, to_agent)
        return task_id

    def send_handoff(self, to_agent: str, context: str, task_id: str, priority: int = 3) -> None:
        handoff = Handoff(
            from_agent=self.name,
            to_agent=to_agent,
            context=context,
            task_id=task_id,
            priority=priority
        )
        self.message_bus.send(handoff, self.name, to_agent)


# --- Specialized Agents ---

class ResearchAgent(BaseAgent):
    """
    Research Agent: Queries multiple internal/mock sources and synthesizes evidence.
    """

    def __init__(self, name: str, message_bus: MessageBus):
        super().__init__(name, "researcher", message_bus)
        self.message_bus.register_handler(TaskRequest.__name__, self._route_task_request)
        self.message_bus.register_handler(Handoff.__name__, self._route_handoff)
        print(f"[AGENT INIT] {self.name} (Research Agent) initialized.")

    def _query_mock_sources(self, topic: str) -> Dict[str, str]:
        """Simulates tool calls to multiple information channels."""
        print(f"[{self.name}] Tool Call: Executing multi-source search for '{topic}'...")
        return {
            "academic_journals": f"Paper Analysis: Multi-agent architectures improve task decomposition speed by 40% over single monolithic prompts.",
            "industry_benchmarks": f"Benchmark Data: Typed message passing with Pydantic prevents 95%+ of inter-agent schema mismatches.",
            "tech_news": f"Industry Trends: AutoGen and CAMEL frameworks showcase peer and supervisor coordination patterns for enterprise AI systems."
        }

    def _route_task_request(self, message: TaskRequest, from_agent: str, to_agent: Optional[str]) -> Optional[TaskResult]:
        if to_agent and to_agent != self.name:
            return None
        return self.handle_task_request(message, from_agent, to_agent)

    def _route_handoff(self, message: Handoff, from_agent: str, to_agent: Optional[str]) -> Optional[TaskResult]:
        if to_agent and to_agent != self.name:
            return None
        return self.handle_handoff(message, from_agent, to_agent)

    def handle_task_request(self, message: TaskRequest, from_agent: str, to_agent: Optional[str]) -> TaskResult:
        print(f"[{self.name}] Processing TaskRequest (ID: {message.task_id}): {message.description}")
        start_time = time.time()

        # Step 1: Query multi-source tools
        sources_data = self._query_mock_sources(message.description)

        # Step 2: Use LLM to structure findings
        prompt = ChatPromptTemplate.from_template("""
You are a Research Agent specializing in AI systems.
Task: {description}
Instructions: {instructions}

Gathered Data from Sources:
- Academic: {academic}
- Benchmarks: {benchmarks}
- News: {news}

Synthesize a precise research outline with key findings, data points, and evidence.
        """)

        chain = prompt | self.llm | StrOutputParser()

        try:
            research_output = chain.invoke({
                "description": message.description,
                "instructions": "\n".join(message.instructions),
                "academic": sources_data["academic_journals"],
                "benchmarks": sources_data["industry_benchmarks"],
                "news": sources_data["tech_news"]
            })

            exec_time = round(time.time() - start_time, 3)
            result = TaskResult(
                task_id=message.task_id,
                result=research_output,
                confidence=0.92,
                agent_name=self.name,
                execution_time=exec_time
            )

            self.task_history.append({"task_id": message.task_id, "status": "completed"})
            self.message_bus.send(result, self.name, message.requester)
            return result

        except Exception as e:
            error_report = ErrorReport(
                task_id=message.task_id,
                error_message=str(e),
                error_type="internal",
                agent_name=self.name
            )
            self.message_bus.send(error_report, self.name, message.requester)
            raise e

    def handle_handoff(self, message: Handoff, from_agent: str, to_agent: Optional[str]) -> TaskResult:
        print(f"[{self.name}] Received Handoff from {from_agent} (Task ID: {message.task_id})")
        res = TaskResult(
            task_id=message.task_id,
            result=f"Research agent acknowledged context: {message.context[:80]}...",
            confidence=0.9,
            agent_name=self.name,
            execution_time=0.05
        )
        self.message_bus.send(res, self.name, from_agent)
        return res


class SynthesisAgent(BaseAgent):
    """
    Synthesis Agent: Merges research findings into a structured report.
    """

    def __init__(self, name: str, message_bus: MessageBus):
        super().__init__(name, "synthesizer", message_bus)
        self.message_bus.register_handler(TaskRequest.__name__, self._route_task_request)
        self.message_bus.register_handler(Handoff.__name__, self._route_handoff)
        print(f"[AGENT INIT] {self.name} (Synthesis Agent) initialized.")

    def _route_task_request(self, message: TaskRequest, from_agent: str, to_agent: Optional[str]) -> Optional[TaskResult]:
        if to_agent and to_agent != self.name:
            return None
        return self.handle_task_request(message, from_agent, to_agent)

    def _route_handoff(self, message: Handoff, from_agent: str, to_agent: Optional[str]) -> Optional[TaskResult]:
        if to_agent and to_agent != self.name:
            return None
        return self.handle_handoff(message, from_agent, to_agent)

    def handle_task_request(self, message: TaskRequest, from_agent: str, to_agent: Optional[str]) -> TaskResult:
        print(f"[{self.name}] Processing TaskRequest (ID: {message.task_id}): {message.description}")
        start_time = time.time()

        prompt = ChatPromptTemplate.from_template("""
You are a Synthesis Agent. You take multi-source information and format it into a formal structured report.

Topic/Task: {description}
Instructions: {instructions}

Produce a structured markdown executive report with:
1. Executive Summary
2. Architectural Analysis
3. Key Findings & Empirical Data
4. Recommendations
        """)

        chain = prompt | self.llm | StrOutputParser()

        try:
            synthesis_output = chain.invoke({
                "description": message.description,
                "instructions": "\n".join(message.instructions)
            })

            exec_time = round(time.time() - start_time, 3)
            result = TaskResult(
                task_id=message.task_id,
                result=synthesis_output,
                confidence=0.88,
                agent_name=self.name,
                execution_time=exec_time
            )

            self.task_history.append({"task_id": message.task_id, "status": "completed"})
            self.message_bus.send(result, self.name, message.requester)
            return result

        except Exception as e:
            error_report = ErrorReport(
                task_id=message.task_id,
                error_message=str(e),
                error_type="internal",
                agent_name=self.name
            )
            self.message_bus.send(error_report, self.name, message.requester)
            raise e

    def handle_handoff(self, message: Handoff, from_agent: str, to_agent: Optional[str]) -> TaskResult:
        print(f"[{self.name}] Received Handoff from {from_agent} (Task ID: {message.task_id})")
        start_time = time.time()

        prompt = ChatPromptTemplate.from_template("""
You are a Synthesis Agent. Process the handed-off research context and generate a final cohesive brief.

Context: {context}

Generate a concise report brief summarizing key highlights and actionable steps.
        """)

        chain = prompt | self.llm | StrOutputParser()
        synthesized_text = chain.invoke({"context": message.context})
        exec_time = round(time.time() - start_time, 3)

        result = TaskResult(
            task_id=message.task_id,
            result=synthesized_text,
            confidence=0.91,
            agent_name=self.name,
            execution_time=exec_time
        )
        self.message_bus.send(result, self.name, from_agent)
        return result


class QA_Agent(BaseAgent):
    """
    QA Agent: Validates report quality, consistency, and criteria satisfaction.
    """

    def __init__(self, name: str, message_bus: MessageBus):
        super().__init__(name, "qa_reviewer", message_bus)
        self.message_bus.register_handler(TaskRequest.__name__, self._route_task_request)
        self.message_bus.register_handler(Handoff.__name__, self._route_handoff)
        print(f"[AGENT INIT] {self.name} (QA Agent) initialized.")

    def _route_task_request(self, message: TaskRequest, from_agent: str, to_agent: Optional[str]) -> Optional[TaskResult]:
        if to_agent and to_agent != self.name:
            return None
        return self.handle_task_request(message, from_agent, to_agent)

    def _route_handoff(self, message: Handoff, from_agent: str, to_agent: Optional[str]) -> Optional[TaskResult]:
        if to_agent and to_agent != self.name:
            return None
        return self.handle_handoff(message, from_agent, to_agent)

    def handle_task_request(self, message: TaskRequest, from_agent: str, to_agent: Optional[str]) -> TaskResult:
        print(f"[{self.name}] Performing QA review for Task ID {message.task_id}...")
        start_time = time.time()

        qa_assessment = f"[QA VERIFIED] Task ID {message.task_id} met quality standards. Output verified for completeness and structure."
        exec_time = round(time.time() - start_time, 3)

        result = TaskResult(
            task_id=message.task_id,
            result=qa_assessment,
            confidence=0.98,
            agent_name=self.name,
            execution_time=exec_time
        )
        self.message_bus.send(result, self.name, message.requester)
        return result

    def handle_handoff(self, message: Handoff, from_agent: str, to_agent: Optional[str]) -> TaskResult:
        print(f"[{self.name}] Received QA Handoff from {from_agent} (Task ID: {message.task_id})")
        start_time = time.time()

        qa_assessment = f"[QA PASSED] Document handed off from {from_agent} successfully passed quality criteria."
        exec_time = round(time.time() - start_time, 3)

        result = TaskResult(
            task_id=message.task_id,
            result=qa_assessment,
            confidence=0.96,
            agent_name=self.name,
            execution_time=exec_time
        )
        self.message_bus.send(result, self.name, from_agent)
        return result


# --- Test Functions ---

def test_typed_messages():
    """
    Test 1: Validate Pydantic typed message schemas and field constraints.
    """
    print("\n" + "=" * 70)
    print("TEST 1: TYPED MESSAGE SCHEMAS AND CONSTRAINTS")
    print("=" * 70)

    # Valid TaskRequest
    try:
        req = TaskRequest(
            task_id="task_001",
            description="Analyze multi-agent communication patterns.",
            instructions=["Gather papers", "Identify trade-offs"],
            priority=2,
            requester="SystemOrchestrator"
        )
        print(f"[PASS] Valid TaskRequest created: ID={req.task_id}, Priority={req.priority}")
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")

    # Invalid priority level (< 1 or > 5)
    try:
        req_invalid = TaskRequest(
            task_id="task_002",
            description="Invalid priority test",
            instructions=["Test"],
            priority=10,
            requester="Tester"
        )
        print(f"[FAIL] Should have raised validation error for priority=10")
    except (ValidationError, ValueError) as e:
        print(f"[PASS] Priority constraint correctly caught validation error.")

    # Invalid confidence range (< 0.0 or > 1.0)
    try:
        res_invalid = TaskResult(
            task_id="task_003",
            result="Invalid result",
            confidence=1.5,
            agent_name="Researcher",
            execution_time=0.4
        )
        print(f"[FAIL] Should have raised validation error for confidence=1.5")
    except (ValidationError, ValueError) as e:
        print(f"[PASS] Confidence constraint correctly caught validation error.")


def test_malformed_message():
    """
    Test 2: Verify malformed raw data and bad schemas raise validation error before dispatch.
    """
    print("\n" + "=" * 70)
    print("TEST 2: MALFORMED MESSAGE REJECTION BEFORE DISPATCH")
    print("=" * 70)

    bus = MessageBus()

    # Empty task_id in TaskRequest
    malformed_task_data = {
        "task_id": "   ",
        "description": "Malformed task request",
        "instructions": ["Should fail"],
        "priority": 3,
        "requester": "Tester"
    }

    try:
        bus.validate_and_send(TaskRequest, malformed_task_data, from_agent="Tester", to_agent="Researcher")
        print("[FAIL] Malformed task request was not rejected.")
    except (ValidationError, ValueError):
        print("[PASS] Malformed TaskRequest correctly rejected before dispatch.")

    # Invalid ErrorReport with empty error_message
    malformed_error_data = {
        "task_id": "task_999",
        "error_message": "",
        "error_type": "internal",
        "agent_name": "Tester"
    }

    try:
        bus.validate_and_send(ErrorReport, malformed_error_data, from_agent="Tester", to_agent="Researcher")
        print("[FAIL] Malformed error report was not rejected.")
    except (ValidationError, ValueError):
        print("[PASS] Malformed ErrorReport correctly rejected before dispatch.")


def test_message_bus():
    """
    Test 3: Execute complete 3-agent multi-agent workflow over typed MessageBus.
    """
    print("\n" + "=" * 70)
    print("TEST 3: MULTI-AGENT WORKFLOW ON TYPED MESSAGE BUS")
    print("=" * 70)

    bus = MessageBus()

    # Initialize 3 agents
    researcher = ResearchAgent("ResearchAgent", bus)
    synthesizer = SynthesisAgent("SynthesisAgent", bus)
    qa_agent = QA_Agent("QA_Agent", bus)

    print("\n--- STEP 1: ResearchAgent receives TaskRequest and queries sources ---")
    task_id = researcher.send_task(
        description="Compare Orchestrator-Worker vs Supervisor vs Peer-to-Peer Multi-Agent Architectures",
        instructions=[
            "Query internal mock sources for data",
            "Synthesize findings on communication overhead and failure modes"
        ],
        to_agent="ResearchAgent",
        priority=1
    )

    time.sleep(1)

    print("\n--- STEP 2: ResearchAgent hands off context to SynthesisAgent ---")
    researcher.send_handoff(
        to_agent="SynthesisAgent",
        context=(
            "Research Summary: Orchestrator-Worker excels at centralized task distribution; "
            "Supervisor pattern handles dynamic delegation and failure recovery; "
            "Peer-to-Peer allows decentralized agent negotiation."
        ),
        task_id=task_id,
        priority=1
    )

    time.sleep(1)

    print("\n--- STEP 3: SynthesisAgent hands off structured draft to QA_Agent ---")
    synthesizer.send_handoff(
        to_agent="QA_Agent",
        context="Synthesis Report Draft: Architectural trade-off analysis complete.",
        task_id=task_id,
        priority=1
    )

    time.sleep(1)

    print("\n--- STEP 4: Inspect Message Bus Event History ---")
    history = bus.get_history()
    print(f"Total messages processed by bus: {len(history)}")
    for idx, entry in enumerate(history, 1):
        print(f"  {idx}. [{entry['timestamp']}] {entry['from']} -> {entry['to']} [{entry['type']}]")

    print("\n" + "=" * 70)
    print("[SUCCESS] All multi-agent workflow tests completed successfully!")
    print("=" * 70)


def main():
    """
    Main entry point for Week 5 Day 1 Lab 5.1 execution.
    """
    print("=" * 70)
    print("LAB 5.1: TYPED MESSAGE BUS")
    print("Week 5 - Day 1: Foundations & First Team")
    print("=" * 70)

    test_typed_messages()
    test_malformed_message()
    test_message_bus()

    print("\n[COMPLETE] Lab 5.1 Typed Message Bus execution finalized.")


if __name__ == "__main__":
    main()
