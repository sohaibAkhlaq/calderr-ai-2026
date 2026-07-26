"""
Week 4 - Day 4: Lab 4.3 (Enhanced) / Day 4 HITL - Human-in-the-Loop Approval Workflow

Demonstrates native LangGraph interrupt patterns, human review breakpoints,
state persistence across interrupts using MemorySaver, state inspection,
and resumption with modified human decisions.

Usage:
    python "Week 4/lab4.3_hitl_approval_workflow.py"
"""

from typing import Annotated, List, Literal, TypedDict
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import interrupt, Command


# ---------------------------------------------------------------------------
# State Schema
# ---------------------------------------------------------------------------

class ModerationState(TypedDict):
    """State schema for content moderation with HITL interrupts."""
    post_id: str
    content: str
    author: str
    category: str
    risk_score: float
    status: Literal["pending", "auto_approved", "auto_rejected", "human_approved", "human_rejected", "revised"]
    human_feedback: str
    review_required: bool
    iteration: int
    messages: Annotated[List[dict], add_messages]


# ---------------------------------------------------------------------------
# Node Functions
# ---------------------------------------------------------------------------

def classify_content(state: ModerationState) -> dict:
    """Classify risk level of incoming post."""
    text = state["content"].lower()
    high_risk_terms = ["scam", "fraud", "exploit", "hack", "illegal"]
    medium_risk_terms = ["complaint", "refund", "issue", "poor", "bad", "disappointed"]

    risk_score = 1.0
    if any(word in text for word in high_risk_terms):
        risk_score = 9.0
    elif any(word in text for word in medium_risk_terms):
        risk_score = 5.0
    
    if risk_score >= 8.0:
        category = "high_risk"
        review_required = False
    elif risk_score >= 4.0:
        category = "medium_risk"
        review_required = True
    else:
        category = "low_risk"
        review_required = False

    print(f"  [CLASSIFY] Post '{state['post_id']}' classified as {category} (Risk Score: {risk_score:.1f})")

    return {
        "category": category,
        "risk_score": risk_score,
        "review_required": review_required,
        "messages": [{"role": "system", "content": f"Classification: {category} (Score: {risk_score})"}]
    }


def auto_approve(state: ModerationState) -> dict:
    """Auto-approve low risk content."""
    print(f"  [AUTO-APPROVE] Post '{state['post_id']}' automatically published.")
    return {
        "status": "auto_approved",
        "messages": [{"role": "system", "content": "Post auto-approved."}]
    }


def auto_reject(state: ModerationState) -> dict:
    """Auto-reject high risk content."""
    print(f"  [AUTO-REJECT] Post '{state['post_id']}' blocked due to policy violations.")
    return {
        "status": "auto_rejected",
        "messages": [{"role": "system", "content": "Post auto-rejected."}]
    }


def human_review_node(state: ModerationState) -> dict:
    """
    Human Review Node using explicit interrupt().
    Pauses workflow execution and awaits external input.
    """
    print(f"\n  [HITL INTERRUPT] Pausing execution for post '{state['post_id']}'!")
    print(f"  --> Pending Content: \"{state['content']}\"")
    print(f"  --> Author: {state['author']} | Risk: {state['risk_score']}")

    # Interrupt execution and send context to human reviewer
    human_response = interrupt({
        "instruction": "Please review this post and provide decision ('approve', 'reject', or 'revise').",
        "post_id": state["post_id"],
        "content": state["content"],
        "risk_score": state["risk_score"]
    })

    # When resumed via Command(resume=...), human_response receives the payload
    decision = human_response.get("decision", "reject")
    feedback = human_response.get("feedback", "")
    print(f"  [RESUMED] Human responded with Decision: '{decision}', Feedback: '{feedback}'")

    status_map = {
        "approve": "human_approved",
        "reject": "human_rejected",
        "revise": "revised"
    }

    return {
        "status": status_map.get(decision, "human_rejected"),
        "human_feedback": feedback,
        "messages": [{"role": "human", "content": f"Decision: {decision}. Feedback: {feedback}"}]
    }


def apply_revision(state: ModerationState) -> dict:
    """Revise post content based on human reviewer feedback."""
    feedback = state.get("human_feedback", "")
    content = state["content"]
    iteration = state.get("iteration", 0) + 1

    revised_content = f"{content} (Revised as requested: {feedback})"
    print(f"  [REVISE] Iteration {iteration}: Updated post content.")

    return {
        "content": revised_content,
        "iteration": iteration,
        "status": "pending",
        "messages": [{"role": "system", "content": f"Content revised in iteration {iteration}."}]
    }


# ---------------------------------------------------------------------------
# Routing Logic
# ---------------------------------------------------------------------------

def route_after_classification(state: ModerationState) -> str:
    """Route based on classification risk level."""
    if state["category"] == "high_risk":
        return "auto_reject"
    elif state["category"] == "medium_risk":
        return "human_review"
    return "auto_approve"


def route_after_human_review(state: ModerationState) -> str:
    """Route based on human decision output."""
    if state["status"] == "revised":
        return "apply_revision"
    return END


# ---------------------------------------------------------------------------
# Graph Construction
# ---------------------------------------------------------------------------

def build_hitl_graph():
    """Build and compile the HITL state graph with persistence."""
    builder = StateGraph(ModerationState)

    builder.add_node("classify", classify_content)
    builder.add_node("auto_approve", auto_approve)
    builder.add_node("auto_reject", auto_reject)
    builder.add_node("human_review", human_review_node)
    builder.add_node("apply_revision", apply_revision)

    builder.set_entry_point("classify")

    builder.add_conditional_edges(
        "classify",
        route_after_classification,
        {
            "auto_approve": "auto_approve",
            "auto_reject": "auto_reject",
            "human_review": "human_review"
        }
    )

    builder.add_conditional_edges(
        "human_review",
        route_after_human_review,
        {
            "apply_revision": "apply_revision",
            END: END
        }
    )

    builder.add_edge("apply_revision", "human_review")
    builder.add_edge("auto_approve", END)
    builder.add_edge("auto_reject", END)

    checkpointer = InMemorySaver()
    return builder.compile(checkpointer=checkpointer)


# ---------------------------------------------------------------------------
# Demonstration / Execution Pipeline
# ---------------------------------------------------------------------------

def main():
    print("=" * 75)
    print("DAY 4 LAB 4.3: HUMAN-IN-THE-LOOP (HITL) APPROVAL WORKFLOW DEMO")
    print("=" * 75)

    graph = build_hitl_graph()

    # Case 1: Low risk -> Auto Approve
    print("\n--- Test Case 1: Low Risk Post ---")
    config1 = {"configurable": {"thread_id": "thread_post_1"}}
    init_state1 = {
        "post_id": "P001",
        "content": "This product was very helpful and easy to set up!",
        "author": "Alice",
        "category": "",
        "risk_score": 0.0,
        "status": "pending",
        "human_feedback": "",
        "review_required": False,
        "iteration": 0,
        "messages": []
    }
    res1 = graph.invoke(init_state1, config1)
    print(f"Final Status: {res1['status']}\n")

    # Case 2: Borderline -> Interrupt -> Resume with Approval
    print("--- Test Case 2: Medium Risk Post (Interrupt & Resume with Approval) ---")
    config2 = {"configurable": {"thread_id": "thread_post_2"}}
    init_state2 = {
        "post_id": "P002",
        "content": "I had a poor experience with delivery, but customer support fixed it.",
        "author": "Bob",
        "category": "",
        "risk_score": 0.0,
        "status": "pending",
        "human_feedback": "",
        "review_required": False,
        "iteration": 0,
        "messages": []
    }
    
    # Initial invocation stops at interrupt()
    print("Step 1: Invoking graph until interrupt...")
    graph.invoke(init_state2, config2)

    # Inspect current state checkpoint
    snapshot = graph.get_state(config2)
    print(f"Checkpoint State inspect -> Next Node: {snapshot.next}")
    print(f"Interrupt Tasks Payload: {snapshot.tasks[0].interrupts[0].value}")

    # Resume graph execution with human input
    print("\nStep 2: Resuming graph with Human Decision ('approve')...")
    res2 = graph.invoke(Command(resume={"decision": "approve", "feedback": "Approved with warning."}), config2)
    print(f"Final Status: {res2['status']}\n")

    # Case 3: Borderline -> Interrupt -> Resume with Revision -> Re-review
    print("--- Test Case 3: Medium Risk Post (Interrupt & Revision Loop) ---")
    config3 = {"configurable": {"thread_id": "thread_post_3"}}
    init_state3 = {
        "post_id": "P003",
        "content": "Service had a minor issue with refund timing.",
        "author": "Charlie",
        "category": "",
        "risk_score": 0.0,
        "status": "pending",
        "human_feedback": "",
        "review_required": False,
        "iteration": 0,
        "messages": []
    }

    print("Step 1: Invoking graph...")
    graph.invoke(init_state3, config3)

    print("\nStep 2: Resuming with Human Request for Revision ('revise')...")
    res_rev = graph.invoke(Command(resume={"decision": "revise", "feedback": "Softened tone."}), config3)
    
    # State loops back to human_review node and interrupts again!
    snapshot3 = graph.get_state(config3)
    print(f"Post-Revision Checkpoint Next Node: {snapshot3.next}")
    print(f"Updated Content in State: \"{snapshot3.values['content']}\"")

    print("\nStep 3: Resuming second human review round with final approval ('approve')...")
    res3 = graph.invoke(Command(resume={"decision": "approve", "feedback": "Revised version approved."}), config3)
    print(f"Final Status: {res3['status']}\n")

    print("=" * 75)
    print("LAB 4.3 HITL DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 75)


if __name__ == "__main__":
    main()
