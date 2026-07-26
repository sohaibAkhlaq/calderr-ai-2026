"""
FastAPI REST Server for Project 4-P-A: AI-Powered Hiring Pipeline
Integrates LangGraph execution engine with REST endpoints.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn

from langgraph.types import Command
from hiring_engine import build_hiring_graph, CandidateState, DB_PATH
import sqlite3

app = FastAPI(
    title="AI-Powered Hiring Pipeline API",
    description="Production REST API for LangGraph hiring workflows with HITL interrupts and SQLite audit logs.",
    version="1.0.0"
)

# Global graph instance
graph = build_hiring_graph()


class IngestCandidateRequest(BaseModel):
    candidate_id: str = Field(..., example="CAND-101")
    candidate_name: str = Field(..., example="Sohaib Akhlaq")
    target_role: str = Field(..., example="AI Agentic Engineer")
    experience_years: float = Field(..., example=4.5)
    skills: List[str] = Field(..., example=["Python", "LangGraph", "FastAPI", "Docker", "RAG"])
    resume_text: str = Field(..., example="Experienced AI engineer proficient in Python, LangGraph, FastAPI, Docker, and RAG.")


class HumanReviewRequest(BaseModel):
    thread_id: str = Field(..., example="thread_CAND-101")
    decision: str = Field(..., example="approved")  # approved or rejected
    notes: Optional[str] = Field(default="Approved by HR lead.")


@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "AI-Powered Hiring Pipeline Platform",
        "framework": "FastAPI + LangGraph",
        "docs_url": "/docs"
    }


@app.post("/api/candidates/ingest")
def ingest_candidate(req: IngestCandidateRequest):
    """Ingest resume and trigger LangGraph hiring workflow."""
    thread_id = f"thread_{req.candidate_id}"
    config = {"configurable": {"thread_id": thread_id}}

    init_state: CandidateState = {
        "candidate_id": req.candidate_id,
        "candidate_name": req.candidate_name,
        "target_role": req.target_role,
        "experience_years": req.experience_years,
        "skills": req.skills,
        "resume_text": req.resume_text,
        "match_score": 0.0,
        "scoring_reasoning": "",
        "bias_detected": False,
        "bias_flags": [],
        "bias_score": 0.0,
        "shortlisted": False,
        "interview_questions": [],
        "human_decision": "pending",
        "reviewer_notes": "",
        "final_status": "pending",
        "audit_logs": [],
        "messages": []
    }

    graph.invoke(init_state, config)
    snapshot = graph.get_state(config)

    interrupted = bool(snapshot.next and "human_review" in snapshot.next)
    
    return {
        "status": "success",
        "thread_id": thread_id,
        "candidate_id": req.candidate_id,
        "match_score": snapshot.values.get("match_score"),
        "shortlisted": snapshot.values.get("shortlisted"),
        "bias_detected": snapshot.values.get("bias_detected"),
        "bias_flags": snapshot.values.get("bias_flags"),
        "interrupted_awaiting_human_review": interrupted,
        "audit_logs": snapshot.values.get("audit_logs", [])
    }


@app.post("/api/candidates/review")
def review_candidate(req: HumanReviewRequest):
    """Submit HR decision to resume an interrupted workflow."""
    config = {"configurable": {"thread_id": req.thread_id}}
    snapshot = graph.get_state(config)

    if not snapshot.values:
        raise HTTPException(status_code=404, detail="Candidate workflow thread not found.")

    resumed_state = graph.invoke(Command(resume={"decision": req.decision, "notes": req.notes}), config)

    return {
        "status": "success",
        "thread_id": req.thread_id,
        "final_status": resumed_state.get("final_status"),
        "human_decision": resumed_state.get("human_decision"),
        "audit_logs": resumed_state.get("audit_logs", [])
    }


@app.get("/api/audit-logs")
def get_audit_logs():
    """Retrieve all historical hiring decisions from SQLite audit database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hiring_audit_logs ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()

    logs = [dict(row) for row in rows]
    return {
        "count": len(logs),
        "audit_records": logs
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
