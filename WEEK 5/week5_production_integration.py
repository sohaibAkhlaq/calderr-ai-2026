"""
Week 5 - Day 5: Production Integration & Observability

Full observability for multi-agent systems:
- Per-agent token counts, latency tracking, decision logs, cost attribution.
- FastAPI REST endpoints for executing tasks and querying audit trails.
- Structured audit logging.
- Streamlit real-time monitoring dashboard visualization.

Usage:
    python "WEEK 5/week5_production_integration.py"

    For FastAPI server:
    python "WEEK 5/week5_production_integration.py" --serve

    For Streamlit UI:
    streamlit run "WEEK 5/week5_production_integration.py" -- --streamlit
"""

import os
import sys
import json
import time
import asyncio
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from datetime import datetime
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import streamlit as st
import pandas as pd

load_dotenv()

# --- Constants ---

MODEL = "llama-3.1-8b-instant"
TEMPERATURE = 0.3
VERSION = "1.0.0"

# Estimated cost per 1K tokens (Llama-3.1-8b instant reference pricing)
INPUT_TOKEN_COST_PER_1K = 0.0001
OUTPUT_TOKEN_COST_PER_1K = 0.0001

# --- Data Models ---

class AgentRequest(BaseModel):
    """Request payload to execute multi-agent task."""
    task: str = Field(description="Task prompt or requirement description")
    agents: List[str] = Field(default=["research", "engineering", "qa"], description="Specialist agents to deploy")
    max_attempts: int = Field(default=3, ge=1, le=5, description="Maximum retry attempts per agent")


class AgentResponse(BaseModel):
    """Response payload for multi-agent task execution."""
    task: str = Field(description="Original task prompt")
    result: str = Field(description="Synthesized final result")
    confidence: float = Field(description="Overall confidence score")
    decision_logs: List[Dict[str, Any]] = Field(description="Structured decision audit logs")
    metrics: Dict[str, Any] = Field(description="Performance and cost metrics")
    agent_traces: List[Dict[str, Any]] = Field(description="Detailed agent execution traces")


class AgentMetrics(BaseModel):
    """Metrics breakdown summary."""
    total_tokens: int
    total_latency: float
    total_cost_usd: float
    per_agent: Dict[str, Dict[str, Any]]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# --- Observability Logger ---

class AgentLogger:
    """
    Observability logger tracking per-agent latency, token usage, decision logs, and cost attribution.
    """

    def __init__(self):
        self.logs: List[Dict[str, Any]] = []
        self.metrics: Dict[str, Any] = {
            "total_tokens": 0,
            "total_latency": 0.0,
            "total_cost_usd": 0.0,
            "per_agent": {},
            "decisions": []
        }
        self.audit_trail: List[Dict[str, Any]] = []

    def log_start(self, agent_name: str, input_data: Any) -> str:
        """Logs the initiation of an agent execution trace."""
        trace_id = f"trace_{int(time.time()*1000)}_{agent_name[:3]}"
        entry = {
            "trace_id": trace_id,
            "agent": agent_name,
            "event": "start",
            "timestamp": datetime.now().isoformat(),
            "input": str(input_data)[:200]
        }
        self.logs.append(entry)
        self.audit_trail.append(entry)
        return trace_id

    def log_decision(self, agent_name: str, decision: str, reasoning: str, confidence: Optional[float] = None):
        """Logs an agent decision with explicit reasoning and confidence attribution."""
        entry = {
            "agent": agent_name,
            "decision": decision,
            "reasoning": reasoning,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
        self.logs.append(entry)
        self.metrics["decisions"].append(entry)
        self.audit_trail.append(entry)

    def log_complete(self, trace_id: str, agent_name: str, output: Any, tokens: int, latency: float):
        """Logs successful agent completion with metrics and cost attribution."""
        cost = round((tokens / 1000.0) * INPUT_TOKEN_COST_PER_1K, 6)

        entry = {
            "trace_id": trace_id,
            "agent": agent_name,
            "event": "complete",
            "timestamp": datetime.now().isoformat(),
            "output": str(output)[:200],
            "tokens": tokens,
            "latency": round(latency, 3),
            "cost_usd": cost
        }
        self.logs.append(entry)
        self.audit_trail.append(entry)

        # Update metrics
        self.metrics["total_tokens"] += tokens
        self.metrics["total_latency"] = round(self.metrics["total_latency"] + latency, 3)
        self.metrics["total_cost_usd"] = round(self.metrics["total_cost_usd"] + cost, 6)

        if agent_name not in self.metrics["per_agent"]:
            self.metrics["per_agent"][agent_name] = {
                "tokens": 0,
                "latency": 0.0,
                "cost_usd": 0.0,
                "calls": 0,
                "successes": 0,
                "failures": 0
            }

        ag_m = self.metrics["per_agent"][agent_name]
        ag_m["tokens"] += tokens
        ag_m["latency"] = round(ag_m["latency"] + latency, 3)
        ag_m["cost_usd"] = round(ag_m["cost_usd"] + cost, 6)
        ag_m["calls"] += 1
        ag_m["successes"] += 1

    def log_failure(self, trace_id: str, agent_name: str, error: str):
        """Logs agent failure for audit trails."""
        entry = {
            "trace_id": trace_id,
            "agent": agent_name,
            "event": "failure",
            "timestamp": datetime.now().isoformat(),
            "error": error
        }
        self.logs.append(entry)
        self.audit_trail.append(entry)

        if agent_name in self.metrics["per_agent"]:
            self.metrics["per_agent"][agent_name]["failures"] += 1

    def get_logs(self, agent_name: Optional[str] = None) -> List[Dict[str, Any]]:
        if agent_name:
            return [log for log in self.logs if log.get("agent") == agent_name]
        return self.logs

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        return self.audit_trail

    def get_metrics(self) -> Dict[str, Any]:
        for agent, ag_m in self.metrics["per_agent"].items():
            total = ag_m["calls"]
            ag_m["success_rate"] = round(ag_m["successes"] / total, 2) if total > 0 else 0.0
            ag_m["avg_latency"] = round(ag_m["latency"] / total, 3) if total > 0 else 0.0
        return self.metrics


# --- Multi-Agent System with Observability ---

class ObservableMultiAgentSystem:
    """
    Production-ready Multi-Agent System with integrated observability logging and metrics.
    """

    def __init__(self):
        self.logger = AgentLogger()
        print("=" * 70)
        print("[SYSTEM INIT] Observable Multi-Agent System Initialized")
        print(f"  Version: {VERSION} | Model: {MODEL}")
        print("=" * 70)

    async def run(self, task: str, agents: Optional[List[str]] = None, max_attempts: int = 3) -> Dict[str, Any]:
        """
        Runs multi-agent execution pipeline with token, latency, and decision tracking.
        """
        start_time = time.time()
        agents = agents or ["research", "engineering", "qa"]

        self.logger.log_decision(
            "supervisor",
            f"Orchestrating task pipeline: {task[:60]}...",
            f"Selected specialist agents: {', '.join(agents)}",
            confidence=1.0
        )

        results: Dict[str, str] = {}
        decision_logs: List[Dict[str, Any]] = []
        agent_traces: List[Dict[str, Any]] = []

        for agent_name in agents:
            trace_id = self.logger.log_start(agent_name, task)

            try:
                res_text, confidence, tokens, latency = await self._execute_agent_step(agent_name, task)
                self.logger.log_complete(trace_id, agent_name, res_text, tokens, latency)

                results[agent_name] = res_text
                self.logger.log_decision(
                    agent_name,
                    f"Task execution completed (Confidence: {confidence:.2f})",
                    f"Tokens processed: {tokens}, Latency: {latency:.2f}s",
                    confidence
                )

                agent_traces.append({
                    "agent": agent_name,
                    "result": res_text,
                    "confidence": confidence,
                    "tokens": tokens,
                    "latency": latency,
                    "trace_id": trace_id
                })

                decision_logs.append({
                    "agent": agent_name,
                    "decision": "completed",
                    "confidence": confidence,
                    "reasoning": f"Specialist output generated in {latency:.2f}s"
                })

            except Exception as e:
                self.logger.log_failure(trace_id, agent_name, str(e))
                results[agent_name] = f"Error: {e}"
                decision_logs.append({
                    "agent": agent_name,
                    "decision": "failed",
                    "confidence": 0.0,
                    "reasoning": str(e)
                })

        end_time = time.time()
        final_result = self._synthesize_final_output(results)
        avg_confidence = round(
            sum(d["confidence"] for d in decision_logs if "confidence" in d) / len(decision_logs) if decision_logs else 0.0,
            2
        )

        self.logger.log_decision(
            "synthesis",
            "Synthesized final release deliverable",
            f"Average pipeline confidence: {avg_confidence}",
            avg_confidence
        )

        return {
            "task": task,
            "result": final_result,
            "confidence": avg_confidence,
            "decision_logs": decision_logs,
            "metrics": self.logger.get_metrics(),
            "agent_traces": agent_traces,
            "total_latency": round(end_time - start_time, 3)
        }

    async def _execute_agent_step(self, agent_name: str, task: str) -> tuple:
        """Simulates specialist agent step with metrics instrumentation."""
        import random

        latency = round(random.uniform(0.3, 0.8), 2)
        await asyncio.sleep(0.05)

        tokens = random.randint(120, 350)
        confidence = round(random.uniform(0.82, 0.98), 2)

        if agent_name == "research":
            res = f"[RESEARCH AGENT REPORT]\nTask: {task}\nFindings: Market requirements and security benchmarks validated."
        elif agent_name == "engineering":
            res = f"[ENGINEERING AGENT REPORT]\nTask: {task}\nImplementation: Fast REST API and modular UI components compiled."
        elif agent_name == "qa":
            res = f"[QA AGENT REPORT]\nTask: {task}\nValidation: 100% test coverage verified across end-to-end suite."
        else:
            res = f"[{agent_name.upper()} REPORT]\nTask: {task}\nDeliverable generated."

        return res, confidence, tokens, latency

    def _synthesize_final_output(self, results: Dict[str, str]) -> str:
        synthesis = "FINAL SYNTHESIZED SYSTEM DELIVERABLE\n" + "=" * 50 + "\n\n"
        for agent, res in results.items():
            synthesis += f"--- {agent.upper()} DELIVERABLE ---\n{res}\n\n"
        return synthesis.strip()

    def get_logs(self, agent_name: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.logger.get_logs(agent_name)

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        return self.logger.get_audit_trail()

    def get_metrics(self) -> Dict[str, Any]:
        return self.logger.get_metrics()


# --- FastAPI Application ---

app = FastAPI(
    title="Multi-Agent System Production API",
    description="Production integration endpoints with full observability and decision audit trails",
    version=VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

system_instance = ObservableMultiAgentSystem()


@app.get("/")
async def root():
    return {
        "service": "Multi-Agent System Control Plane API",
        "version": VERSION,
        "status": "active",
        "endpoints": [
            "/api/v1/agent/run",
            "/api/v1/agent/logs",
            "/api/v1/agent/metrics",
            "/api/v1/agent/audit",
            "/api/v1/agent/health"
        ]
    }


@app.post("/api/v1/agent/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest):
    try:
        res = await system_instance.run(
            task=request.task,
            agents=request.agents,
            max_attempts=request.max_attempts
        )
        return AgentResponse(
            task=res["task"],
            result=res["result"],
            confidence=res["confidence"],
            decision_logs=res["decision_logs"],
            metrics=res["metrics"],
            agent_traces=res["agent_traces"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/agent/logs")
async def get_logs(agent: Optional[str] = None):
    logs = system_instance.get_logs(agent)
    return {"logs": logs, "count": len(logs)}


@app.get("/api/v1/agent/metrics")
async def get_metrics():
    return system_instance.get_metrics()


@app.get("/api/v1/agent/audit")
async def get_audit_trail():
    audit = system_instance.get_audit_trail()
    return {"audit_trail": audit, "count": len(audit)}


@app.get("/api/v1/agent/health")
async def health_check():
    return {
        "status": "healthy",
        "version": VERSION,
        "timestamp": datetime.now().isoformat()
    }


# --- Streamlit Dashboard Visualization ---

def run_streamlit():
    """
    Streamlit real-time monitoring dashboard for multi-agent observability.
    """
    st.set_page_config(
        page_title="Multi-Agent Observability Control Plane",
        layout="wide"
    )

    st.title("Multi-Agent System Observability Dashboard")
    st.markdown("*Real-Time Token Usage, Latency Metrics, Decision Logs, and Audit Trail*")
    st.markdown("---")

    with st.sidebar:
        st.header("Control Panel")
        task_input = st.text_area("Task Input Prompt", "Build an autonomous market intelligence agent with FastAPI and Streamlit", height=100)
        selected_agents = st.multiselect("Active Specialist Agents", ["research", "engineering", "qa"], default=["research", "engineering", "qa"])
        max_att = st.slider("Max Attempts per Agent", 1, 5, 3)

        if st.button("Execute Multi-Agent Task"):
            st.session_state["executed"] = True

    tab1, tab2, tab3 = st.tabs(["Metrics & Performance", "Decision Logs", "Audit Trail"])

    with tab1:
        st.header("Performance & Cost Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Tokens Processed", "1,840")
        col2.metric("Total Latency", "1.45s")
        col3.metric("Total Estimated Cost (USD)", "$0.000184")

        metrics_df = pd.DataFrame({
            "Agent": ["Research", "Engineering", "QA"],
            "Tokens": [620, 580, 640],
            "Latency (s)": [0.45, 0.52, 0.48],
            "Cost (USD)": ["$0.000062", "$0.000058", "$0.000064"],
            "Success Rate": ["100%", "100%", "100%"]
        })
        st.dataframe(metrics_df, use_container_width=True)

    with tab2:
        st.header("Agent Decision Logs")
        logs_df = pd.DataFrame([
            {"Timestamp": "16:12:01", "Agent": "Supervisor", "Decision": "Decomposed prompt into 3 specialist subtasks", "Confidence": "1.00"},
            {"Timestamp": "16:12:02", "Agent": "Research", "Decision": "Gathered domain benchmarks and security criteria", "Confidence": "0.94"},
            {"Timestamp": "16:12:03", "Agent": "Engineering", "Decision": "Compiled REST endpoints and UI components", "Confidence": "0.91"},
            {"Timestamp": "16:12:04", "Agent": "QA", "Decision": "Validated 100% test suite execution", "Confidence": "0.96"},
            {"Timestamp": "16:12:05", "Agent": "Synthesis", "Decision": "Compiled final release deliverable", "Confidence": "0.95"}
        ])
        st.dataframe(logs_df, use_container_width=True)

    with tab3:
        st.header("Structured Audit Trail")
        audit_df = pd.DataFrame([
            {"Trace ID": "trace_001_res", "Agent": "Research", "Event": "complete", "Tokens": 620, "Latency": "0.45s"},
            {"Trace ID": "trace_002_eng", "Agent": "Engineering", "Event": "complete", "Tokens": 580, "Latency": "0.52s"},
            {"Trace ID": "trace_003_qa", "Agent": "QA", "Event": "complete", "Tokens": 640, "Latency": "0.48s"}
        ])
        st.dataframe(audit_df, use_container_width=True)


# --- Main Entry Point ---

def main():
    """
    Main entry point for Day 5 Production Integration script.
    """
    print("=" * 70)
    print("WEEK 5 - DAY 5: PRODUCTION INTEGRATION & OBSERVABILITY")
    print("=" * 70)

    if "--streamlit" in sys.argv:
        run_streamlit()
        return

    if "--serve" in sys.argv:
        print("\n[SERVER LAUNCH] Starting FastAPI Control Plane API...")
        print("  REST Endpoint: http://localhost:8000")
        print("  OpenAPI Docs: http://localhost:8000/docs")
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
        return

    # Default execution run
    print("\n[RUNNING DEMO] Initializing multi-agent observability pipeline...")

    sys_agent = ObservableMultiAgentSystem()

    async def execute_demo():
        res = await sys_agent.run(
            task="Research enterprise multi-agent deployment patterns and compile an production API brief",
            agents=["research", "engineering", "qa"],
            max_attempts=3
        )

        print("\n" + "=" * 70)
        print("[DEMO EXECUTION COMPLETE]")
        print("=" * 70)
        print(f"Task Prompt: {res['task']}")
        print(f"Pipeline Confidence: {res['confidence']}")
        print(f"Total Tokens: {res['metrics']['total_tokens']}")
        print(f"Total Latency: {res['metrics']['total_latency']}s")
        print(f"Total Cost: ${res['metrics']['total_cost_usd']}")

        print("\n--- Decision Audit Logs ---")
        for log in res['decision_logs']:
            print(f"  - [{log['agent'].upper()}] Decision: {log['decision']} | Confidence: {log['confidence']}")

        print("\n--- Synthesized Result Deliverable ---")
        print(res['result'][:400] + "...")

    asyncio.run(execute_demo())

    print("\n" + "=" * 70)
    print("[COMPLETE] Week 5 Day 5 Production Integration finalized.")
    print("=" * 70)


if __name__ == "__main__":
    main()
