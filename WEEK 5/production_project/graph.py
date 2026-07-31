"""
Autonomous AI Research Lab - LangGraph 5-Phase Research Pipeline Graph

Compiles multi-phase state graph connecting Domain Classifier, Hypothesis Generator,
Dynamic Specialist Evidence Gathering, Critic Agent, Synthesis Agent, and Peer Review Agent.
"""

import time
from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from schemas import (
    ResearchDomain, Hypothesis, EvidenceItem, CriticChallenge,
    PeerReviewScorecard, ResearchReport
)
from agents import (
    DomainClassifier, HypothesisGenerator, EvidenceGathererAgent,
    CriticAgent, SynthesisAgent, PeerReviewAgent, ReportPublisher
)


class ResearchState(TypedDict):
    """State schema for 5-phase research workflow."""
    question: str
    report_id: str
    domain: Dict[str, Any]
    hypothesis: Dict[str, Any]
    evidence_gathered: List[Dict[str, Any]]
    critic_challenges: List[Dict[str, Any]]
    synthesis_body: str
    citations: List[str]
    peer_review: Dict[str, Any]
    final_report: Dict[str, Any]
    total_tokens: int
    start_time: float
    messages: Annotated[List[dict], add_messages]


def build_research_graph():
    """Builds and compiles the 5-Phase LangGraph Research Pipeline."""

    classifier = DomainClassifier()
    hypothesizer = HypothesisGenerator()
    critic = CriticAgent()
    synthesizer = SynthesisAgent()
    peer_reviewer = PeerReviewAgent()

    def classify_and_hypothesize_node(state: ResearchState) -> dict:
        q = state.get("question", "Research Topic")
        st_time = time.time()
        print(f"\n[PHASE 1] Domain Classification & Hypothesis Generation for '{q}'...")

        domain, t1 = classifier.classify(q)
        hypothesis, t2 = hypothesizer.generate(q, domain)

        return {
            "domain": domain.model_dump(),
            "hypothesis": hypothesis.model_dump(),
            "start_time": st_time,
            "total_tokens": t1 + t2,
            "messages": [{"role": "system", "content": f"Phase 1 complete: Domain classified as {domain.primary_domain}."}]
        }

    def gather_evidence_node(state: ResearchState) -> dict:
        q = state.get("question", "Research Topic")
        domain_dict = state.get("domain", {})
        domain = ResearchDomain(**domain_dict)

        print(f"\n[PHASE 2] Dynamic Specialist Assembly & Parallel Evidence Gathering ({len(domain.recommended_specialists)} agents)...")

        sub_questions = [
            f"What are the primary technological capabilities for {q}?",
            f"What are the safety, reliability, and security considerations for {q}?",
            f"What are the performance metrics and efficiency benchmarks for {q}?"
        ]

        evidence_list = []
        tot_tok = state.get("total_tokens", 0)

        for idx, spec_name in enumerate(domain.recommended_specialists):
            sub_q = sub_questions[idx % len(sub_questions)]
            agent = EvidenceGathererAgent(spec_name, domain.primary_domain)
            item, tok = agent.gather_evidence(sub_q)
            evidence_list.append(item.model_dump())
            tot_tok += tok

        return {
            "evidence_gathered": evidence_list,
            "total_tokens": tot_tok,
            "messages": [{"role": "system", "content": f"Phase 2 complete: Gathered {len(evidence_list)} evidence items."}]
        }

    def critic_challenge_node(state: ResearchState) -> dict:
        print(f"\n[PHASE 3] Critic Agent Evidence Audit & Challenge...")

        hyp = Hypothesis(**state.get("hypothesis", {}))
        ev_items = [EvidenceItem(**e) for e in state.get("evidence_gathered", [])]

        challenges, tok = critic.challenge_evidence(hyp, ev_items)
        tot_tok = state.get("total_tokens", 0) + tok

        return {
            "critic_challenges": [c.model_dump() for c in challenges],
            "total_tokens": tot_tok,
            "messages": [{"role": "system", "content": f"Phase 3 complete: Identified {len(challenges)} critic challenges."}]
        }

    def synthesis_node(state: ResearchState) -> dict:
        q = state.get("question", "Research Topic")
        print(f"\n[PHASE 4] Synthesis Agent Paper Body Compilation...")

        domain = ResearchDomain(**state.get("domain", {}))
        hyp = Hypothesis(**state.get("hypothesis", {}))
        ev_items = [EvidenceItem(**e) for e in state.get("evidence_gathered", [])]
        challenges = [CriticChallenge(**c) for c in state.get("critic_challenges", [])]

        paper_body, citations, tok = synthesizer.synthesize(q, domain, hyp, ev_items, challenges)
        tot_tok = state.get("total_tokens", 0) + tok

        return {
            "synthesis_body": paper_body,
            "citations": citations,
            "total_tokens": tot_tok,
            "messages": [{"role": "system", "content": "Phase 4 complete: Synthesized research paper body."}]
        }

    def peer_review_and_publish_node(state: ResearchState) -> dict:
        q = state.get("question", "Research Topic")
        rep_id = state.get("report_id", f"rep_{int(time.time()*1000)}")
        print(f"\n[PHASE 5] Peer Review Agent Quality Audit & Final Publication...")

        body = state.get("synthesis_body", "")
        ev_count = len(state.get("evidence_gathered", []))
        domain = ResearchDomain(**state.get("domain", {}))
        hyp = Hypothesis(**state.get("hypothesis", {}))
        ev_items = [EvidenceItem(**e) for e in state.get("evidence_gathered", [])]
        challenges = [CriticChallenge(**c) for c in state.get("critic_challenges", [])]
        citations = state.get("citations", [])

        scorecard, tok = peer_reviewer.review_report(body, ev_count)
        tot_tok = state.get("total_tokens", 0) + tok
        st_time = state.get("start_time", time.time())

        final_report = ReportPublisher.publish(
            report_id=rep_id,
            question=q,
            domain=domain,
            hypothesis=hyp,
            evidence_list=ev_items,
            challenges=challenges,
            scorecard=scorecard,
            paper_body=body,
            citations=citations,
            total_tokens=tot_tok,
            start_time=st_time
        )

        return {
            "peer_review": scorecard.model_dump(),
            "final_report": final_report.model_dump(),
            "messages": [{"role": "system", "content": f"Phase 5 complete: Published report '{final_report.title}'."}]
        }

    builder = StateGraph(ResearchState)
    builder.add_node("phase1", classify_and_hypothesize_node)
    builder.add_node("phase2", gather_evidence_node)
    builder.add_node("phase3", critic_challenge_node)
    builder.add_node("phase4", synthesis_node)
    builder.add_node("phase5", peer_review_and_publish_node)

    builder.set_entry_point("phase1")
    builder.add_edge("phase1", "phase2")
    builder.add_edge("phase2", "phase3")
    builder.add_edge("phase3", "phase4")
    builder.add_edge("phase4", "phase5")
    builder.add_edge("phase5", END)

    return builder.compile()
