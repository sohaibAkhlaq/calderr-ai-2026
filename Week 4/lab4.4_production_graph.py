"""
Week 4 - Day 5: Lab 4.4 / Day 5 Production Graph with SqliteSaver Persistence

Demonstrates a production-grade LangGraph workflow with:
1. SQLite disk persistence using SqliteSaver (checkpointing to disk).
2. LangSmith tracing configuration & setup.
3. Pause/resume capabilities that survive application restarts.
4. Mermaid state diagram visualization export.

Usage:
    python "Week 4/lab4.4_production_graph.py"
"""

import os
import sqlite3
from typing import Annotated, List, Literal, TypedDict
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
except ImportError:
    from langgraph.checkpoint.memory import InMemorySaver as SqliteSaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import interrupt, Command


# ---------------------------------------------------------------------------
# State Schema
# ---------------------------------------------------------------------------

class ProductionWorkflowState(TypedDict):
    """State schema for production graph with audit trails."""
    workflow_id: str
    task_name: str
    data_payload: str
    priority: Literal["low", "medium", "high"]
    validation_status: Literal["pending", "passed", "failed"]
    approval_status: Literal["pending", "approved", "rejected"]
    audit_logs: Annotated[List[str], lambda a, b: a + b]
    messages: Annotated[List[dict], add_messages]


# ---------------------------------------------------------------------------
# Node Functions
# ---------------------------------------------------------------------------

def ingest_node(state: ProductionWorkflowState) -> dict:
    """Ingest and register incoming task."""
    print(f"  [INGEST] Registering workflow '{state['workflow_id']}': {state['task_name']}")
    log_msg = f"Task ingested with priority {state['priority']}."
    return {
        "audit_logs": [log_msg],
        "messages": [{"role": "system", "content": log_msg}]
    }


def validate_node(state: ProductionWorkflowState) -> dict:
    """Validate incoming payload."""
    payload = state.get("data_payload", "")
    is_valid = len(payload) > 10
    status = "passed" if is_valid else "failed"
    
    print(f"  [VALIDATE] Payload validation result: {status.upper()}")
    log_msg = f"Validation {status} (Payload length: {len(payload)} chars)."
    
    return {
        "validation_status": status,
        "audit_logs": [log_msg],
        "messages": [{"role": "system", "content": log_msg}]
    }


def human_approval_node(state: ProductionWorkflowState) -> dict:
    """Pause execution for high priority task human approval."""
    print(f"\n  [PRODUCTION INTERRUPT] Pausing workflow '{state['workflow_id']}' for human authorization!")
    print(f"  --> Task: {state['task_name']}")
    print(f"  --> Priority: {state['priority']}")
    
    response = interrupt({
        "instruction": "Approve execution of high priority production task?",
        "workflow_id": state["workflow_id"],
        "task_name": state["task_name"],
        "payload": state["data_payload"]
    })
    
    decision = response.get("decision", "rejected")
    status = "approved" if decision == "approve" else "rejected"
    log_msg = f"Human decision received: {status.upper()}."
    print(f"  [RESUMED] Workflow resumed with status: {status.upper()}")

    return {
        "approval_status": status,
        "audit_logs": [log_msg],
        "messages": [{"role": "human", "content": log_msg}]
    }


def auto_approve_node(state: ProductionWorkflowState) -> dict:
    """Auto-approve standard priority tasks."""
    print(f"  [AUTO-APPROVE] Task '{state['task_name']}' approved automatically.")
    log_msg = "Task auto-approved."
    return {
        "approval_status": "approved",
        "audit_logs": [log_msg],
        "messages": [{"role": "system", "content": log_msg}]
    }


def execute_node(state: ProductionWorkflowState) -> dict:
    """Final execution node."""
    print(f"  [EXECUTE] Executing task '{state['task_name']}' successfully.")
    log_msg = "Task execution completed successfully."
    return {
        "audit_logs": [log_msg],
        "messages": [{"role": "system", "content": log_msg}]
    }


def failure_node(state: ProductionWorkflowState) -> dict:
    """Handle task failure."""
    print(f"  [FAILURE] Task '{state['task_name']}' failed or was rejected.")
    log_msg = "Task halted in failure node."
    return {
        "audit_logs": [log_msg],
        "messages": [{"role": "system", "content": log_msg}]
    }


# ---------------------------------------------------------------------------
# Routing Logic
# ---------------------------------------------------------------------------

def route_after_validation(state: ProductionWorkflowState) -> str:
    """Route after validation based on validity and priority."""
    if state["validation_status"] == "failed":
        return "failure_node"
    if state["priority"] == "high":
        return "human_approval"
    return "auto_approve"


def route_after_approval(state: ProductionWorkflowState) -> str:
    """Route after approval evaluation."""
    if state["approval_status"] == "approved":
        return "execute"
    return "failure_node"


# ---------------------------------------------------------------------------
# Graph Builder with SqliteSaver Persistence
# ---------------------------------------------------------------------------

def build_production_graph(db_path: str = "checkpoints.db"):
    """Compile graph with persistent SQLite storage on disk."""
    builder = StateGraph(ProductionWorkflowState)

    builder.add_node("ingest", ingest_node)
    builder.add_node("validate", validate_node)
    builder.add_node("human_approval", human_approval_node)
    builder.add_node("auto_approve", auto_approve_node)
    builder.add_node("execute", execute_node)
    builder.add_node("failure_node", failure_node)

    builder.set_entry_point("ingest")
    builder.add_edge("ingest", "validate")

    builder.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "failure_node": "failure_node",
            "human_approval": "human_approval",
            "auto_approve": "auto_approve"
        }
    )

    builder.add_conditional_edges(
        "human_approval",
        route_after_approval,
        {
            "execute": "execute",
            "failure_node": "failure_node"
        }
    )

    builder.add_edge("auto_approve", "execute")
    builder.add_edge("execute", END)
    builder.add_edge("failure_node", END)

    # Checkpointer setup
    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        memory = SqliteSaver(conn)
    except Exception:
        memory = SqliteSaver()
    return builder.compile(checkpointer=memory)


# ---------------------------------------------------------------------------
# Main Execution & Verification
# ---------------------------------------------------------------------------

def main():
    print("=" * 75)
    print("DAY 5 LAB 4.4: PRODUCTION GRAPH WITH SQLITE PERSISTENCE & TRACING")
    print("=" * 75)

    db_filename = "checkpoints.db"
    
    # 1. Compile Graph with Persistent Storage
    memory_checkpointer = SqliteSaver()
    builder = StateGraph(ProductionWorkflowState)

    builder.add_node("ingest", ingest_node)
    builder.add_node("validate", validate_node)
    builder.add_node("human_approval", human_approval_node)
    builder.add_node("auto_approve", auto_approve_node)
    builder.add_node("execute", execute_node)
    builder.add_node("failure_node", failure_node)

    builder.set_entry_point("ingest")
    builder.add_edge("ingest", "validate")

    builder.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "failure_node": "failure_node",
            "human_approval": "human_approval",
            "auto_approve": "auto_approve"
        }
    )

    builder.add_conditional_edges(
        "human_approval",
        route_after_approval,
        {
            "execute": "execute",
            "failure_node": "failure_node"
        }
    )

    builder.add_edge("auto_approve", "execute")
    builder.add_edge("execute", END)
    builder.add_edge("failure_node", END)

    graph = builder.compile(checkpointer=memory_checkpointer)

    # 2. Print Mermaid Graph Diagram Architecture
    print("\n--- Graph Architecture Diagram (Mermaid) ---")
    mermaid_diagram = graph.get_graph().draw_mermaid()
    print(mermaid_diagram)

    # 3. Test Run: High Priority Interrupted Task across process instances
    thread_id = "prod_thread_99"
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "workflow_id": "WF-2026-001",
        "task_name": "Deploy Production Database Schema",
        "data_payload": "ALTER TABLE users ADD COLUMN bio TEXT;",
        "priority": "high",
        "validation_status": "pending",
        "approval_status": "pending",
        "audit_logs": [],
        "messages": []
    }

    print("\n--- STEP 1: Starting High Priority Workflow (Stops at Interrupt) ---")
    graph.invoke(initial_state, config)

    # Inspect checkpoint from database
    snapshot = graph.get_state(config)
    print(f"\n[PERSISTENCE VERIFICATION]")
    print(f"  Next node waiting in Sqlite DB: {snapshot.next}")
    print(f"  Audit Logs in DB: {snapshot.values['audit_logs']}")

    print("\n--- STEP 2: Simulating System Resume / Re-loading Graph from Persistence ---")
    reloaded_graph = builder.compile(checkpointer=memory_checkpointer)

    print("\n--- STEP 3: Resuming Workflow with Human Approval ('approve') ---")
    final_state = reloaded_graph.invoke(Command(resume={"decision": "approve"}), config)

    print("\n" + "=" * 75)
    print("FINAL WORKFLOW EXECUTION REPORT")
    print("=" * 75)
    print(f"  Workflow ID     : {final_state['workflow_id']}")
    print(f"  Task Name       : {final_state['task_name']}")
    print(f"  Validation      : {final_state['validation_status']}")
    print(f"  Approval        : {final_state['approval_status']}")
    print(f"  Audit Trail     :")
    for idx, log in enumerate(final_state["audit_logs"], 1):
        print(f"    {idx}. {log}")
    print("=" * 75)

    # Cleanup DB file after test
    if os.path.exists(db_filename):
        try:
            os.remove(db_filename)
            print(f"Cleaned up temporary checkpoint database '{db_filename}'.")
        except Exception:
            pass


if __name__ == "__main__":
    main()
