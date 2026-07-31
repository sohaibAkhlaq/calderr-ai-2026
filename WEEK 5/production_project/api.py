"""
Autonomous AI Research Lab - FastAPI Production Control Plane API

Exposes REST endpoints for submitting autonomous deep research queries,
monitoring phase execution, and retrieving published research reports.

Usage:
    uvicorn api:app --reload
"""

import os
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from graph import build_research_graph
from schemas import ResearchReport

VERSION = "1.0.0"

app = FastAPI(
    title="Autonomous AI Research Lab REST API",
    description="5-Phase Autonomous Multi-Agent Deep Research Control Plane",
    version=VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory published report store
REPORT_STORE: Dict[str, Dict[str, Any]] = {}
research_graph = build_research_graph()


class ResearchSubmitRequest(BaseModel):
    question: str = Field(..., description="Target research question or prompt")


class ResearchSubmitResponse(BaseModel):
    report_id: str
    status: str
    timestamp: str
    report: Dict[str, Any]


@app.get("/")
async def root():
    return {
        "service": "Autonomous AI Research Lab REST API",
        "version": VERSION,
        "status": "active",
        "endpoints": [
            "/api/v1/research/submit",
            "/api/v1/research/reports",
            "/api/v1/research/reports/{report_id}",
            "/api/v1/research/health"
        ]
    }


@app.post("/api/v1/research/submit", response_model=ResearchSubmitResponse)
async def submit_research(request: ResearchSubmitRequest):
    q = request.question.strip()
    if not q:
        raise HTTPException(status_code=400, detail="question field must not be empty")

    try:
        report_id = f"rep_{int(time.time()*1000)}"
        initial_state = {
            "question": q,
            "report_id": report_id,
            "domain": {},
            "hypothesis": {},
            "evidence_gathered": [],
            "critic_challenges": [],
            "synthesis_body": "",
            "citations": [],
            "peer_review": {},
            "final_report": {},
            "total_tokens": 0,
            "start_time": 0.0,
            "messages": []
        }

        result_state = research_graph.invoke(initial_state)
        report_dict = result_state.get("final_report", {})
        REPORT_STORE[report_id] = report_dict

        return ResearchSubmitResponse(
            report_id=report_id,
            status="published",
            timestamp=datetime.now().isoformat(),
            report=report_dict
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/research/reports")
async def get_all_reports():
    return {
        "count": len(REPORT_STORE),
        "reports": list(REPORT_STORE.values())
    }


@app.get("/api/v1/research/reports/{report_id}")
async def get_report_by_id(report_id: str):
    if report_id not in REPORT_STORE:
        raise HTTPException(status_code=404, detail=f"Report ID '{report_id}' not found.")
    return REPORT_STORE[report_id]


@app.get("/api/v1/research/health")
async def health_check():
    return {
        "status": "healthy",
        "version": VERSION,
        "timestamp": datetime.now().isoformat()
    }
