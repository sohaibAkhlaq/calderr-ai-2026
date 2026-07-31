"""
Autonomous AI Research Lab - Pydantic Schemas

Defines typed contracts for domain classification, dynamic team assembly,
hypothesis generation, multi-phase evidence gathering, critic challenge,
peer review auditing, and final published research reports.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class ResearchDomain(BaseModel):
    """Domain classification result produced by DomainClassifier."""
    primary_domain: str = Field(..., description="Target domain (e.g. Artificial Intelligence, Healthcare, Finance, Cybersecurity)")
    sub_domains: List[str] = Field(..., description="Secondary domain classifications")
    recommended_specialists: List[str] = Field(..., description="Recommended specialist evidence agents")
    confidence: float = Field(..., description="Classification confidence score (0.0 to 1.0)")


class Hypothesis(BaseModel):
    """Structured hypothesis proposed prior to evidence gathering."""
    hypothesis_id: str = Field(..., description="Unique hypothesis identifier")
    title: str = Field(..., description="Hypothesis title")
    statement: str = Field(..., description="Core hypothesis statement")
    expected_outcomes: List[str] = Field(..., description="Expected validation metrics or evidence indicators")
    risk_factors: List[str] = Field(..., description="Potential counter-arguments or failure modes")


class EvidenceItem(BaseModel):
    """Granular evidence item gathered by specialist evidence agents."""
    sub_question: str = Field(..., description="Target sub-question answered")
    agent_name: str = Field(..., description="Name of evidence agent")
    finding: str = Field(..., description="Core evidence finding")
    source_citation: str = Field(..., description="Source citation or documentation reference")
    quality_score: float = Field(..., description="Initial evidence quality score (0.0 to 1.0)")


class CriticChallenge(BaseModel):
    """Critical evaluation produced by Critic Agent in Phase 3."""
    target_evidence_id: str = Field(..., description="Target evidence item challenged")
    challenge_type: str = Field(..., description="Type of challenge (e.g. Unsupported Claim, Methodological Flaw, Bias)")
    critique: str = Field(..., description="Detailed critique reasoning")
    severity: str = Field(..., description="Severity level (Low, Medium, High, Critical)")
    suggested_revision: str = Field(..., description="Recommended revision or qualification")


class PeerReviewScorecard(BaseModel):
    """Second-pass peer review verification produced by Peer Review Agent."""
    methodological_rigor: float = Field(..., description="Score 0.0 - 1.0 for methodology")
    citation_completeness: float = Field(..., description="Score 0.0 - 1.0 for evidence citations")
    coherence_rating: float = Field(..., description="Score 0.0 - 1.0 for logical coherence")
    contradiction_count: int = Field(..., description="Count of unresolved internal contradictions")
    approval_status: str = Field(..., description="Status: Approved, Approved with Revisions, Rejected")
    reviewer_notes: str = Field(..., description="Qualitative peer review summary")


class ResearchReport(BaseModel):
    """Final autonomous published research report."""
    report_id: str = Field(..., description="Unique report identifier")
    title: str = Field(..., description="Report title")
    domain: str = Field(..., description="Research domain")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    executive_summary: str = Field(..., description="High-level executive summary")
    hypothesis: Hypothesis = Field(..., description="Initial hypothesis statement")
    evidence_gathered: List[EvidenceItem] = Field(..., description="Compiled evidence items")
    critic_challenges: List[CriticChallenge] = Field(..., description="Critic Agent challenge feedback")
    peer_review: PeerReviewScorecard = Field(..., description="Peer review scorecard")
    synthesis_report: str = Field(..., description="Full synthesized research paper body")
    citations: List[str] = Field(..., description="List of all references and sources")
    total_tokens: int = Field(default=0, description="Total tokens consumed across all phases")
    execution_time_sec: float = Field(default=0.0, description="Total execution time in seconds")
    cost_usd: float = Field(default=0.0, description="Estimated total API cost USD")
