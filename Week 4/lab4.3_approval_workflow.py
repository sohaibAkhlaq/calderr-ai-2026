"""
Week 4 - Day 3: Lab 4.3 - Stateful Approval Workflow

Builds a stateful LangGraph workflow for human-in-the-loop content review.
The graph uses a TypedDict state schema, reducer-based message accumulation,
and checkpointing so the workflow can preserve progress across review rounds.

Usage:
    python "Week 4/lab4.3_approval_workflow.py"
"""

from typing import Annotated, List, Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver as MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_REVISIONS = 3


# ---------------------------------------------------------------------------
# State Schema
# ---------------------------------------------------------------------------

class ApprovalState(TypedDict):
    """State schema for the approval workflow."""

    post_id: str
    post_content: str
    author: str

    category: str
    risk_score: float

    decision: Literal["approved", "rejected", "pending"]
    decision_reason: str

    human_reviewed: bool
    human_decision: Literal["approved", "rejected", "needs_revision", "pending"]
    human_feedback: str

    iteration: int
    is_complete: bool

    messages: Annotated[List[dict], add_messages]


# ---------------------------------------------------------------------------
# Sample Content
# ---------------------------------------------------------------------------

SAMPLE_POSTS = [
    {
        "id": "post_001",
        "content": "This product is amazing and I highly recommend it to everyone.",
        "author": "user123",
    },
    {
        "id": "post_002",
        "content": "I think the service is okay, but it has several issues.",
        "author": "user456",
    },
    {
        "id": "post_003",
        "content": "This is a scam and they stole my money. Do not buy this product.",
        "author": "user789",
    },
    {
        "id": "post_004",
        "content": "The shipping was quick and the packaging was good.",
        "author": "user321",
    },
]


# ---------------------------------------------------------------------------
# Node Functions
# ---------------------------------------------------------------------------

def classify_post(state: ApprovalState) -> dict:
    """Classify the content by risk level and assign a category."""
    content = state.get("post_content", "")
    content_lower = content.lower()

    positive_words = ["amazing", "great", "excellent", "love", "recommend", "happy", "good"]
    negative_words = ["scam", "terrible", "worst", "hate", "fraud", "steal", "bad"]

    positive_score = sum(1 for word in positive_words if word in content_lower)
    negative_score = sum(1 for word in negative_words if word in content_lower)

    if negative_score > 0:
        risk_score = min(10.0, 2.0 + negative_score * 2.0)
    elif positive_score >= 3:
        risk_score = 1.0
    else:
        risk_score = 3.0

    if risk_score >= 7.0:
        category = "high_risk"
    elif risk_score >= 4.0:
        category = "medium_risk"
    else:
        category = "low_risk"

    print(f"[CLASSIFY] Post {state.get('post_id', 'unknown')} -> {category} ({risk_score:.1f}/10)")

    return {
        "category": category,
        "risk_score": risk_score,
        "messages": [
            {"role": "system", "content": f"Classified as {category} with risk {risk_score:.1f}"}
        ],
    }


def auto_approve(state: ApprovalState) -> dict:
    """Approve low-risk content automatically."""
    post_id = state.get("post_id", "unknown")
    print(f"[APPROVE] Post {post_id} approved automatically")

    return {
        "decision": "approved",
        "decision_reason": "Auto-approved because the content is low risk.",
        "is_complete": True,
        "messages": [{"role": "system", "content": f"Post {post_id} approved automatically"}],
    }


def auto_reject(state: ApprovalState) -> dict:
    """Reject high-risk content automatically."""
    post_id = state.get("post_id", "unknown")
    print(f"[REJECT] Post {post_id} rejected automatically")

    return {
        "decision": "rejected",
        "decision_reason": "Auto-rejected because the content is high risk.",
        "is_complete": True,
        "messages": [{"role": "system", "content": f"Post {post_id} rejected automatically"}],
    }


def human_review(state: ApprovalState) -> dict:
    """Simulate a human review step for borderline content."""
    content = state.get("post_content", "")
    content_lower = content.lower()

    negative_words = ["scam", "terrible", "worst", "hate", "fraud", "steal", "bad"]
    positive_words = ["great", "excellent", "good", "amazing", "recommend", "happy"]

    negative_score = sum(1 for word in negative_words if word in content_lower)
    positive_score = sum(1 for word in positive_words if word in content_lower)

    if negative_score > positive_score:
        human_decision = "rejected"
        feedback = "The content contains harmful or negative language."
    elif positive_score > negative_score:
        human_decision = "approved"
        feedback = "The content is constructive and acceptable."
    else:
        human_decision = "needs_revision"
        feedback = "The content is mixed. Please revise it to sound more balanced."

    print(f"[REVIEW] Human decision: {human_decision}")

    return {
        "human_reviewed": True,
        "human_decision": human_decision,
        "human_feedback": feedback,
        "messages": [{"role": "human", "content": feedback}],
    }


def process_human_decision(state: ApprovalState) -> dict:
    """Convert human review output into a final decision."""
    decision = state.get("human_decision", "pending")
    feedback = state.get("human_feedback", "")

    if decision == "approved":
        print("[PROCESS] Human approved the content")
        return {
            "decision": "approved",
            "decision_reason": f"Human approved: {feedback}",
            "is_complete": True,
            "messages": [{"role": "system", "content": "Post approved by human review"}],
        }

    if decision == "rejected":
        print("[PROCESS] Human rejected the content")
        return {
            "decision": "rejected",
            "decision_reason": f"Human rejected: {feedback}",
            "is_complete": True,
            "messages": [{"role": "system", "content": "Post rejected by human review"}],
        }

    next_iteration = state.get("iteration", 0) + 1
    print(f"[PROCESS] Revision requested by human reviewer (round {next_iteration})")
    return {
        "decision": "pending",
        "decision_reason": f"Needs revision: {feedback}",
        "is_complete": False,
        "iteration": next_iteration,
        "messages": [{"role": "system", "content": "Revision requested by human review"}],
    }


def revise_post(state: ApprovalState) -> dict:
    """Revise content based on human feedback."""
    content = state.get("post_content", "")
    feedback = state.get("human_feedback", "")
    current_iteration = state.get("iteration", 0)

    print(f"[REVISE] Revision round {current_iteration}")

    revised_content = content
    if "harmful" in feedback.lower() or "negative" in feedback.lower() or "balanced" in feedback.lower():
        replacements = {
            "scam": "problematic",
            "terrible": "difficult",
            "worst": "poor",
            "hate": "concern",
            "fraud": "misconduct",
            "steal": "take",
        }
        for old, new in replacements.items():
            revised_content = revised_content.replace(old, new)

    return {
        "post_content": revised_content,
        "iteration": current_iteration + 1,
        "messages": [{"role": "system", "content": f"Revised content for iteration {current_iteration + 1}"}],
    }


# ---------------------------------------------------------------------------
# Routing Functions
# ---------------------------------------------------------------------------

def route_after_classify(state: ApprovalState) -> str:
    """Route after classification."""
    risk_score = state.get("risk_score", 0.0)
    if risk_score >= 7.0:
        return "reject"
    if risk_score >= 3.0:
        return "review"
    return "approve"


def route_after_human_review(state: ApprovalState) -> str:
    """Route after human review."""
    if state.get("human_decision") in {"approved", "rejected"}:
        return "process"
    return "revise"


def route_after_revision(state: ApprovalState) -> str:
    """Route after revision."""
    if state.get("iteration", 0) >= MAX_REVISIONS:
        print("[ROUTE] Maximum revisions reached. Continuing to final processing.")
        return "process"
    print("[ROUTE] Sending content back for another review round.")
    return "review"


# ---------------------------------------------------------------------------
# Graph Builder
# ---------------------------------------------------------------------------

def build_approval_graph():
    """Build and compile the approval workflow graph."""
    builder = StateGraph(ApprovalState)

    builder.add_node("classify", classify_post)
    builder.add_node("approve", auto_approve)
    builder.add_node("reject", auto_reject)
    builder.add_node("review", human_review)
    builder.add_node("process", process_human_decision)
    builder.add_node("revise", revise_post)

    builder.set_entry_point("classify")

    builder.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "approve": "approve",
            "review": "review",
            "reject": "reject",
        },
    )

    builder.add_conditional_edges(
        "review",
        route_after_human_review,
        {
            "process": "process",
            "revise": "revise",
        },
    )

    builder.add_conditional_edges(
        "revise",
        route_after_revision,
        {
            "review": "review",
            "process": "process",
        },
    )

    builder.add_edge("approve", END)
    builder.add_edge("reject", END)
    builder.add_edge("process", END)

    memory = MemorySaver()
    return builder.compile(checkpointer=memory)


# ---------------------------------------------------------------------------
# Execution Helpers
# ---------------------------------------------------------------------------

def create_initial_state(post_data: dict) -> ApprovalState:
    """Create the initial state for a post."""
    return {
        "post_id": post_data["id"],
        "post_content": post_data["content"],
        "author": post_data["author"],
        "category": "",
        "risk_score": 0.0,
        "decision": "pending",
        "decision_reason": "",
        "human_reviewed": False,
        "human_decision": "pending",
        "human_feedback": "",
        "iteration": 0,
        "is_complete": False,
        "messages": [],
    }


def run_post(graph, post_data: dict, thread_id: str) -> dict:
    """Run one post through the workflow and print the final result."""
    initial_state = create_initial_state(post_data)
    config = {"configurable": {"thread_id": thread_id}}

    print("\n" + "=" * 70)
    print(f"RUNNING POST: {post_data['id']}")
    print("=" * 70)

    final_state = graph.invoke(initial_state, config)

    snapshot = graph.get_state(config)
    checkpoint_state = snapshot.values if snapshot else {}

    print("\nRESULT")
    print(f"  Decision: {final_state.get('decision', 'pending')}")
    print(f"  Category: {final_state.get('category', 'unclassified')}")
    print(f"  Risk Score: {final_state.get('risk_score', 0.0):.1f}")
    print(f"  Iterations: {final_state.get('iteration', 0)}")
    print(f"  Complete: {final_state.get('is_complete', False)}")
    print(f"  Checkpointed: {bool(checkpoint_state)}")

    return final_state


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the sample suite for the approval workflow."""
    print("=" * 70)
    print("LAB 4.3: STATEFUL APPROVAL WORKFLOW")
    print("=" * 70)

    graph = build_approval_graph()

    results = []
    for post in SAMPLE_POSTS:
        result = run_post(graph, post, f"thread_{post['id']}")
        results.append(result)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    approved = sum(1 for item in results if item.get("decision") == "approved")
    rejected = sum(1 for item in results if item.get("decision") == "rejected")
    pending = sum(1 for item in results if item.get("decision") == "pending")

    print(f"  Total posts: {len(results)}")
    print(f"  Approved: {approved}")
    print(f"  Rejected: {rejected}")
    print(f"  Pending: {pending}")

    for item in results:
        print(
            f"  - {item.get('post_id')}: {item.get('decision')} "
            f"(risk {item.get('risk_score', 0.0):.1f})"
        )


if __name__ == "__main__":
    main()
