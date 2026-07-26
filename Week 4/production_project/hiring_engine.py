"""
Project 4-P-A: AI-Powered Hiring Pipeline - Core LangGraph & Engine
Week 4 Production Project

Architecture:
  [Ingest Resume] -> [Score Candidate] -> [Bias Check Node] -> (Conditional Router)
                                                                 ├── Shortlisted ──> [Generate Interview Questions] -> [HITL Human Review Interrupt]
                                                                 │                                                           ├── Approved ──> [Final Hiring Decision] -> [Audit Log & DB Export]
                                                                 │                                                           └── Rejected ──> [Rejection Decision] -> [Audit Log & DB Export]
                                                                 └── Not Shortlisted ──> [Rejection Decision] -> [Audit Log & DB Export]
"""

import json
import sqlite3
import time
from typing import Annotated, List, Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Command, interrupt


# ---------------------------------------------------------------------------
# Database Initialization & Persistent Audit Schema
# ---------------------------------------------------------------------------

DB_PATH = "hiring_pipeline_audit.db"

def init_db(db_path: str = DB_PATH):
    """Initialize SQLite table for audit logging & hiring records."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hiring_audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id TEXT,
            candidate_name TEXT,
            target_role TEXT,
            match_score REAL,
            bias_detected INTEGER,
            bias_flags TEXT,
            shortlisted INTEGER,
            human_decision TEXT,
            reviewer_notes TEXT,
            final_status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()


# ---------------------------------------------------------------------------
# State Schema
# ---------------------------------------------------------------------------

class CandidateState(TypedDict):
    """State schema for AI-Powered Hiring Pipeline."""
    candidate_id: str
    candidate_name: str
    target_role: str
    experience_years: float
    skills: List[str]
    resume_text: str
    match_score: float
    scoring_reasoning: str
    bias_detected: bool
    bias_flags: List[str]
    bias_score: float
    shortlisted: bool
    interview_questions: List[str]
    human_decision: Literal["pending", "approved", "rejected"]
    reviewer_notes: str
    final_status: Literal["pending", "hired", "rejected"]
    audit_logs: Annotated[List[str], lambda a, b: a + b]
    messages: Annotated[List[dict], add_messages]


# ---------------------------------------------------------------------------
# Node Functions
# ---------------------------------------------------------------------------

def ingest_resume_node(state: CandidateState) -> dict:
    """Ingest resume text and register candidate details."""
    log_msg = f"Ingested resume for '{state['candidate_name']}' applying for '{state['target_role']}' ({state['experience_years']} years exp)."
    return {
        "audit_logs": [log_msg],
        "messages": [{"role": "system", "content": log_msg}]
    }


def score_candidate_node(state: CandidateState) -> dict:
    """Score candidate resume against job description using deterministic AI rules."""
    skills = [s.lower() for s in state.get("skills", [])]
    role = state.get("target_role", "").lower()
    exp = state.get("experience_years", 0)

    # Job Role Keyword Weighting
    role_weights = {
        "ai agentic engineer": ["python", "langgraph", "langchain", "llm", "fastapi", "docker", "rag"],
        "senior python developer": ["python", "fastapi", "docker", "postgresql", "asyncio", "pytest"],
        "data scientist": ["python", "machine learning", "pandas", "numpy", "scikit-learn", "sql"]
    }

    req_skills = role_weights.get(role, ["python", "machine learning", "fastapi", "llm"])
    matched = [s for s in req_skills if s in skills]
    
    skill_score = (len(matched) / max(1, len(req_skills))) * 70.0
    exp_score = min(30.0, exp * 6.0)
    total_score = round(skill_score + exp_score, 1)

    reasoning = f"Matched {len(matched)}/{len(req_skills)} required skills ({', '.join(matched) if matched else 'None'}). Experience bonus: {exp_score:.1f} pts."
    shortlisted = total_score >= 60.0

    log_msg = f"Scored Candidate: {total_score}/100. Shortlisted: {shortlisted}. Rationale: {reasoning}"

    return {
        "match_score": total_score,
        "scoring_reasoning": reasoning,
        "shortlisted": shortlisted,
        "audit_logs": [log_msg],
        "messages": [{"role": "system", "content": log_msg}]
    }


def bias_check_node(state: CandidateState) -> dict:
    """
    Bias Detection Node.
    Scans resume text for potentially biased demographic indicators (age, gender, origin, elitist university flags).
    """
    resume_lower = state.get("resume_text", "").lower()
    bias_flags = []

    bias_indicators = {
        "Age Bias": ["graduated in 1990", "graduated in 1985", "over 50 years old", "junior candidate born in 2005"],
        "Gender/Pronoun Bias": ["mother of two", "father of three", "sorority president", "fraternity president"],
        "Elitism Bias": ["ivy league graduate only", "harvard alumnus", "stanford elite scholar"],
        "Location/Nationality Gate": ["native english speakers only", "us citizens preferred"]
    }

    for category, phrases in bias_indicators.items():
        for phrase in phrases:
            if phrase in resume_lower:
                bias_flags.append(f"{category}: Detected term '{phrase}'")

    bias_detected = len(bias_flags) > 0
    bias_score = round(len(bias_flags) * 2.5, 1)

    log_msg = f"Bias Check Completed. Flagged: {bias_detected} ({len(bias_flags)} warnings)."
    if bias_detected:
        log_msg += f" Warnings: {'; '.join(bias_flags)}"

    return {
        "bias_detected": bias_detected,
        "bias_flags": bias_flags,
        "bias_score": bias_score,
        "audit_logs": [log_msg],
        "messages": [{"role": "system", "content": log_msg}]
    }


def generate_questions_node(state: CandidateState) -> dict:
    """Generate tailored technical and behavioral interview questions."""
    role = state.get("target_role", "AI Engineer")
    skills = state.get("skills", [])
    
    questions = [
        f"Can you explain a complex {skills[0] if skills else 'Python'} system you architected from scratch?",
        f"How do you handle cyclic state management and interrupts in {role} workflows?",
        f"Describe a situation where your candidate project required bias mitigation or persistent audit logging."
    ]

    log_msg = f"Generated {len(questions)} custom interview questions."
    return {
        "interview_questions": questions,
        "audit_logs": [log_msg],
        "messages": [{"role": "system", "content": log_msg}]
    }


def human_review_node(state: CandidateState) -> dict:
    """
    Human-in-the-Loop Review Node using explicit interrupt().
    Pauses graph execution for shortlisted candidates and awaits HR manager decision.
    """
    human_response = interrupt({
        "instruction": f"HR Approval Required for Candidate '{state['candidate_name']}' (Score: {state['match_score']}/100).",
        "candidate_id": state["candidate_id"],
        "candidate_name": state["candidate_name"],
        "target_role": state["target_role"],
        "match_score": state["match_score"],
        "bias_flags": state["bias_flags"]
    })

    decision = human_response.get("decision", "rejected")
    notes = human_response.get("notes", "No review notes provided.")

    log_msg = f"HR Manager Decision: {decision.upper()}. Notes: '{notes}'."

    return {
        "human_decision": decision,
        "reviewer_notes": notes,
        "audit_logs": [log_msg],
        "messages": [{"role": "human", "content": log_msg}]
    }


def final_hire_node(state: CandidateState) -> dict:
    """Process official candidate hiring decision & write to audit database."""
    log_msg = f"Candidate '{state['candidate_name']}' officially HIRED for '{state['target_role']}'."
    
    # Save audit snapshot to SQLite
    _save_to_sqlite(state, final_status="hired")

    return {
        "final_status": "hired",
        "audit_logs": [log_msg],
        "messages": [{"role": "system", "content": log_msg}]
    }


def final_reject_node(state: CandidateState) -> dict:
    """Process candidate rejection decision & write to audit database."""
    log_msg = f"Candidate '{state['candidate_name']}' REJECTED for '{state['target_role']}'."
    
    # Save audit snapshot to SQLite
    _save_to_sqlite(state, final_status="rejected")

    return {
        "final_status": "rejected",
        "audit_logs": [log_msg],
        "messages": [{"role": "system", "content": log_msg}]
    }


def _save_to_sqlite(state: CandidateState, final_status: str):
    """Write execution snapshot to SQLite persistent audit log."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO hiring_audit_logs 
            (candidate_id, candidate_name, target_role, match_score, bias_detected, bias_flags, shortlisted, human_decision, reviewer_notes, final_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            state["candidate_id"],
            state["candidate_name"],
            state["target_role"],
            state["match_score"],
            1 if state.get("bias_detected") else 0,
            json.dumps(state.get("bias_flags", [])),
            1 if state.get("shortlisted") else 0,
            state.get("human_decision", "pending"),
            state.get("reviewer_notes", ""),
            final_status
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error persisting to SQLite: {e}")


# ---------------------------------------------------------------------------
# Routing Functions
# ---------------------------------------------------------------------------

def route_after_bias_check(state: CandidateState) -> str:
    """Route based on candidate score / shortlisting status."""
    if state["shortlisted"]:
        return "generate_questions"
    return "final_reject_node"


def route_after_human_review(state: CandidateState) -> str:
    """Route based on HR manager decision."""
    if state["human_decision"] == "approved":
        return "final_hire_node"
    return "final_reject_node"


# ---------------------------------------------------------------------------
# Graph Builder
# ---------------------------------------------------------------------------

def build_hiring_graph():
    """Compile AI Hiring Pipeline StateGraph with MemorySaver checkpointer."""
    builder = StateGraph(CandidateState)

    builder.add_node("ingest_resume", ingest_resume_node)
    builder.add_node("score_candidate", score_candidate_node)
    builder.add_node("bias_check", bias_check_node)
    builder.add_node("generate_questions", generate_questions_node)
    builder.add_node("human_review", human_review_node)
    builder.add_node("final_hire_node", final_hire_node)
    builder.add_node("final_reject_node", final_reject_node)

    builder.set_entry_point("ingest_resume")
    builder.add_edge("ingest_resume", "score_candidate")
    builder.add_edge("score_candidate", "bias_check")

    builder.add_conditional_edges(
        "bias_check",
        route_after_bias_check,
        {
            "generate_questions": "generate_questions",
            "final_reject_node": "final_reject_node"
        }
    )

    builder.add_edge("generate_questions", "human_review")

    builder.add_conditional_edges(
        "human_review",
        route_after_human_review,
        {
            "final_hire_node": "final_hire_node",
            "final_reject_node": "final_reject_node"
        }
    )

    builder.add_edge("final_hire_node", END)
    builder.add_edge("final_reject_node", END)

    memory = InMemorySaver()
    return builder.compile(checkpointer=memory)
