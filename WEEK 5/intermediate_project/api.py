"""
Autonomous Competitive Intelligence Agent - FastAPI Control Plane

Exposes REST endpoints for triggering competitive research,
retrieving intelligence briefings, and monitoring agent observability metrics.

Usage:
    uvicorn api:app --reload
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from graph import build_intelligence_graph
from schemas import CompetitiveBriefing

VERSION = "1.0.0"

app = FastAPI(
    title="Autonomous Competitive Intelligence Agent API",
    description="Multi-agent parallel fan-out research engine exposing REST endpoints",
    version=VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory briefing store
BRIEFING_CACHE: Dict[str, Dict[str, Any]] = {}
graph = build_intelligence_graph()


class AnalyzeRequest(BaseModel):
    company_name: str = Field(..., description="Target company name for competitive analysis")


class AnalyzeResponse(BaseModel):
    company_name: str
    status: str
    timestamp: str
    briefing: Dict[str, Any]


@app.get("/")
async def root():
    return {
        "service": "Autonomous Competitive Intelligence Agent API",
        "version": VERSION,
        "status": "online",
        "endpoints": [
            "/api/v1/intelligence/analyze",
            "/api/v1/intelligence/reports",
            "/api/v1/intelligence/health"
        ]
    }


@app.post("/api/v1/intelligence/analyze", response_model=AnalyzeResponse)
async def analyze_company(request: AnalyzeRequest):
    company = request.company_name.strip()
    if not company:
        raise HTTPException(status_code=400, detail="company_name must not be empty")

    try:
        initial_state = {
            "company_name": company,
            "plan": {},
            "raw_data": {},
            "market_report": {},
            "product_report": {},
            "tech_report": {},
            "news_report": {},
            "sentiment_report": {},
            "conflicts": [],
            "final_briefing": {},
            "total_tokens": 0,
            "start_time": 0.0,
            "messages": []
        }

        result_state = graph.invoke(initial_state)
        briefing_data = result_state.get("final_briefing", {})
        BRIEFING_CACHE[company.lower()] = briefing_data

        return AnalyzeResponse(
            company_name=company,
            status="completed",
            timestamp=datetime.now().isoformat(),
            briefing=briefing_data
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/intelligence/reports")
async def get_reports():
    return {
        "reports_count": len(BRIEFING_CACHE),
        "companies": list(BRIEFING_CACHE.keys()),
        "reports": BRIEFING_CACHE
    }


@app.get("/api/v1/intelligence/health")
async def health_check():
    return {
        "status": "healthy",
        "version": VERSION,
        "timestamp": datetime.now().isoformat()
    }
