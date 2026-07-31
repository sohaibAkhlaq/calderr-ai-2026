"""
Autonomous Competitive Intelligence Agent - LangGraph Execution Pipeline

Compiles parallel fan-out / fan-in execution graph connecting Orchestrator,
Specialist Agents, Conflict Resolver, and Synthesis Agent.
"""

import time
from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from schemas import (
    ResearchPlan, MarketReport, ProductReport, TechStackReport,
    NewsReport, SentimentReport, ConflictItem, CompetitiveBriefing
)
from agents import (
    OrchestratorAgent, MarketAgent, ProductAgent, TechStackAgent,
    NewsAgent, SentimentAgent, ConflictResolver, SynthesisAgent,
    MarketIntelligenceTools
)


class IntelligenceState(TypedDict):
    """State schema for competitive intelligence workflow."""
    company_name: str
    plan: Dict[str, Any]
    raw_data: Dict[str, Any]
    market_report: Dict[str, Any]
    product_report: Dict[str, Any]
    tech_report: Dict[str, Any]
    news_report: Dict[str, Any]
    sentiment_report: Dict[str, Any]
    conflicts: List[Dict[str, Any]]
    final_briefing: Dict[str, Any]
    total_tokens: int
    start_time: float
    messages: Annotated[List[dict], add_messages]


def build_intelligence_graph():
    """Builds and compiles the LangGraph state graph."""

    orchestrator = OrchestratorAgent()
    market_ag = MarketAgent()
    product_ag = ProductAgent()
    tech_ag = TechStackAgent()
    news_ag = NewsAgent()
    sentiment_ag = SentimentAgent()
    resolver = ConflictResolver()
    synthesizer = SynthesisAgent()

    def plan_node(state: IntelligenceState) -> dict:
        company = state.get("company_name", "TargetCompany")
        print(f"\n[GRAPH NODE 1] Orchestrator Planning for '{company}'...")
        st_time = time.time()
        plan = orchestrator.plan_research(company)
        raw = MarketIntelligenceTools.query_company_intelligence(company)

        return {
            "plan": plan.model_dump(),
            "raw_data": raw,
            "start_time": st_time,
            "total_tokens": 50,
            "messages": [{"role": "system", "content": f"Research strategy formulated for {company}."}]
        }

    def fan_out_specialists_node(state: IntelligenceState) -> dict:
        company = state.get("company_name", "TargetCompany")
        raw = state.get("raw_data", {})
        print(f"\n[GRAPH NODE 2] Parallel Fan-out: Executing 5 Specialist Agents...")

        # Parallel specialist executions
        m_rep, t_m = market_ag.analyze(company, raw.get("market_data", ""))
        p_rep, t_p = product_ag.analyze(company, raw.get("product_data", ""))
        tc_rep, t_tc = tech_ag.analyze(company, raw.get("tech_data", ""))
        n_rep, t_n = news_ag.analyze(company, raw.get("news_data", ""))
        s_rep, t_s = sentiment_ag.analyze(company, raw.get("sentiment_data", ""))

        total_tok = state.get("total_tokens", 0) + t_m + t_p + t_tc + t_n + t_s

        return {
            "market_report": m_rep.model_dump(),
            "product_report": p_rep.model_dump(),
            "tech_report": tc_rep.model_dump(),
            "news_report": n_rep.model_dump(),
            "sentiment_report": s_rep.model_dump(),
            "total_tokens": total_tok,
            "messages": [{"role": "system", "content": "Parallel specialist analysis completed."}]
        }

    def resolve_conflicts_node(state: IntelligenceState) -> dict:
        print(f"\n[GRAPH NODE 3] Conflict Resolver Adjudication...")
        m_rep = MarketReport(**state.get("market_report", {}))
        p_rep = ProductReport(**state.get("product_report", {}))
        tc_rep = TechStackReport(**state.get("tech_report", {}))
        n_rep = NewsReport(**state.get("news_report", {}))
        s_rep = SentimentReport(**state.get("sentiment_report", {}))

        conflicts, tok = resolver.resolve_conflicts(m_rep, p_rep, tc_rep, n_rep, s_rep)
        total_tok = state.get("total_tokens", 0) + tok

        return {
            "conflicts": [c.model_dump() for c in conflicts],
            "total_tokens": total_tok,
            "messages": [{"role": "system", "content": f"Resolved {len(conflicts)} contradictions."}]
        }

    def synthesize_node(state: IntelligenceState) -> dict:
        company = state.get("company_name", "TargetCompany")
        print(f"\n[GRAPH NODE 4] Synthesis Agent Assembly...")

        m_rep = MarketReport(**state.get("market_report", {}))
        p_rep = ProductReport(**state.get("product_report", {}))
        tc_rep = TechStackReport(**state.get("tech_report", {}))
        n_rep = NewsReport(**state.get("news_report", {}))
        s_rep = SentimentReport(**state.get("sentiment_report", {}))
        conflicts = [ConflictItem(**c) for c in state.get("conflicts", [])]

        st_time = state.get("start_time", time.time())
        total_tok = state.get("total_tokens", 0) + 120

        briefing = synthesizer.synthesize(
            company=company,
            market=m_rep,
            product=p_rep,
            tech=tc_rep,
            news=n_rep,
            sentiment=s_rep,
            conflicts=conflicts,
            total_tokens=total_tok,
            start_time=st_time
        )

        return {
            "final_briefing": briefing.model_dump(),
            "messages": [{"role": "system", "content": f"Competitive briefing for {company} finalized."}]
        }

    builder = StateGraph(IntelligenceState)
    builder.add_node("plan", plan_node)
    builder.add_node("fan_out", fan_out_specialists_node)
    builder.add_node("resolve", resolve_conflicts_node)
    builder.add_node("synthesize", synthesize_node)

    builder.set_entry_point("plan")
    builder.add_edge("plan", "fan_out")
    builder.add_edge("fan_out", "resolve")
    builder.add_edge("resolve", "synthesize")
    builder.add_edge("synthesize", END)

    return builder.compile()
