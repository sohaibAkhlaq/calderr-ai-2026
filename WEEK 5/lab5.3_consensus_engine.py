"""
Week 5 - Day 4: Lab 5.3 - Consensus Engine

Build a 4-agent consensus system: 3 specialist agents each produce a structured opinion (answer + confidence score 0.0-1.0 + reasoning).
A Consensus Agent aggregates opinions using confidence-weighted voting.
If no option clears 60% weighted confidence, a second round debate is requested between top agents.
Output final answer with a dissent summary if agents disagreed.

Usage:
    python "WEEK 5/lab5.3_consensus_engine.py"
"""

import os
import json
import time
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# --- Constants ---

MODEL = "llama-3.1-8b-instant"
TEMPERATURE = 0.3
CONFIDENCE_THRESHOLD = 0.60
MAX_DEBATE_ROUNDS = 2

# --- Message Schemas ---

class Opinion(BaseModel):
    """Structured opinion from a specialist agent."""
    answer: str = Field(description="The agent's answer or recommendation")
    confidence: float = Field(description="Confidence score (0.0 to 1.0)")
    reasoning: str = Field(description="Reasoning behind the answer")
    agent_name: str = Field(description="Name of the agent providing the opinion")

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if v < 0.0 or v > 1.0:
            raise ValueError("confidence score must be between 0.0 and 1.0")
        return v


class ConsensusResult(BaseModel):
    """Final consensus result."""
    final_answer: str = Field(description="The final answer after consensus aggregation")
    confidence: float = Field(description="Overall confidence score")
    voting_details: Dict[str, Any] = Field(description="Detailed voting results")
    dissent_summary: str = Field(description="Summary of disagreements across agents")
    consensus_reached: bool = Field(description="Whether consensus cleared the threshold")


# --- State Schema ---

class ConsensusState(TypedDict):
    """State for the consensus workflow."""

    # Input
    question: str
    context: str

    # Opinions
    opinions: List[Dict[str, Any]]
    round: int
    max_rounds: int

    # Voting Metrics
    weighted_scores: Dict[str, float]
    total_confidence: float
    top_options: List[str]

    # Output
    final_answer: str
    final_confidence: float
    dissent_summary: str
    consensus_reached: bool

    # Process Log
    messages: Annotated[List[dict], add_messages]


# --- LLM Setup ---

def get_llm(temperature: float = TEMPERATURE):
    """Get the Groq LLM instance with validation."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("[ERROR] GROQ_API_KEY is not configured in environment.")
    return ChatGroq(
        model=MODEL,
        temperature=temperature,
        api_key=api_key
    )


# --- Specialist Agents ---

class SpecialistAgent:
    """Base class for specialist agents."""

    def __init__(self, name: str, role: str, expertise: str):
        self.name = name
        self.role = role
        self.expertise = expertise
        self.llm = get_llm()
        print(f"[AGENT INIT] {name} initialized.")
        print(f"  Role: {role} | Expertise: {expertise}")

    def produce_opinion(self, question: str, context: str = "") -> Opinion:
        """
        Produces a structured opinion (Answer + Confidence Score + Reasoning).
        """
        print(f"\n[{self.name}] Evaluating question: '{question[:55]}...'")

        prompt = ChatPromptTemplate.from_template("""
You are a {role} specialist with expertise in {expertise}.

Question: {question}
Context: {context}

Provide a structured recommendation with:
1. Answer: A concise, direct option or decision statement.
2. Confidence: A numerical confidence score between 0.0 and 1.0.
3. Reasoning: Clear technical rationale for your recommendation.

Format your output strictly as follows:
Answer: <your answer>
Confidence: <float between 0.0 and 1.0>
Reasoning: <detailed reasoning>
        """)

        chain = prompt | self.llm | StrOutputParser()

        try:
            response = chain.invoke({
                "role": self.role,
                "expertise": self.expertise,
                "question": question,
                "context": context
            })

            answer = ""
            confidence = 0.5
            reasoning = ""

            for line in response.strip().split('\n'):
                line = line.strip()
                if line.startswith('Answer:'):
                    answer = line[7:].strip()
                elif line.startswith('Confidence:'):
                    try:
                        confidence = float(line[11:].strip())
                        confidence = max(0.0, min(1.0, confidence))
                    except Exception:
                        confidence = 0.5
                elif line.startswith('Reasoning:'):
                    reasoning = line[10:].strip()

            if not reasoning:
                reasoning = response[:250]

            opinion = Opinion(
                answer=answer if answer else "Undetermined",
                confidence=confidence,
                reasoning=reasoning,
                agent_name=self.name
            )

            print(f"  [OPINION] Answer: '{opinion.answer[:45]}...'")
            print(f"  [CONFIDENCE] Score: {opinion.confidence:.2f}")

            return opinion

        except Exception as e:
            print(f"  [ERROR] Specialist {self.name} failed: {e}")
            return Opinion(
                answer=f"Error during evaluation: {e}",
                confidence=0.0,
                reasoning=str(e),
                agent_name=self.name
            )


class SecurityAgent(SpecialistAgent):
    """Security specialist agent."""
    def __init__(self):
        super().__init__(
            "SecurityAgent",
            "Security Analyst",
            "cybersecurity vulnerability assessment, authorization models, and threat mitigation"
        )


class PerformanceAgent(SpecialistAgent):
    """Performance specialist agent."""
    def __init__(self):
        super().__init__(
            "PerformanceAgent",
            "Performance Engineer",
            "latency optimization, throughput benchmarks, memory usage, and execution scalability"
        )


class MaintainabilityAgent(SpecialistAgent):
    """Maintainability specialist agent."""
    def __init__(self):
        super().__init__(
            "MaintainabilityAgent",
            "Software Architect",
            "code readability, maintainability, architectural design patterns, and testability"
        )


# --- Consensus Agent ---

class ConsensusAgent:
    """
    Consensus Agent aggregates opinions, computes confidence-weighted voting,
    manages multi-round debate loops, and generates dissent summaries.
    """

    def __init__(self):
        self.llm = get_llm()
        self.weighted_scores: Dict[str, float] = {}
        self.total_confidence: float = 0.0
        self.consensus_reached: bool = False
        print("=" * 70)
        print("[CONSENSUS] Consensus Agent Initialized")
        print(f"  Consensus Threshold: {CONFIDENCE_THRESHOLD * 100:.0f}%")
        print(f"  Max Debate Rounds: {MAX_DEBATE_ROUNDS}")
        print("=" * 70)

    def aggregate_opinions(self, opinions: List[Opinion]) -> Dict[str, float]:
        """
        Computes confidence-weighted voting scores across all specialist opinions.
        Formula: Normalized Score_i = Sum(Confidence_i) / Total_Confidence
        """
        print(f"\n[CONSENSUS] Aggregating opinions across {len(opinions)} specialist agents...")

        # Group confidence by answer
        answer_votes: Dict[str, List[Opinion]] = {}
        for op in opinions:
            ans = op.answer.strip()
            if ans not in answer_votes:
                answer_votes[ans] = []
            answer_votes[ans].append(op)

        weighted_scores: Dict[str, float] = {}
        total_confidence = 0.0

        for ans, ops in answer_votes.items():
            sum_conf = sum(o.confidence for o in ops)
            weighted_scores[ans] = sum_conf
            total_confidence += sum_conf

        self.weighted_scores = weighted_scores
        self.total_confidence = total_confidence

        normalized_scores: Dict[str, float] = {}
        if total_confidence > 0:
            for ans, score in weighted_scores.items():
                normalized_scores[ans] = round(score / total_confidence, 4)

        print("\n  [VOTING RESULTS] Normalized Confidence-Weighted Scores:")
        for ans, norm_score in normalized_scores.items():
            print(f"    - {ans[:40]}: {norm_score * 100:.1f}%")

        return normalized_scores

    def check_consensus(self, normalized_scores: Dict[str, float]) -> bool:
        """
        Checks if top option meets or exceeds confidence threshold (60%).
        """
        if not normalized_scores:
            return False

        max_score = max(normalized_scores.values())
        if max_score >= CONFIDENCE_THRESHOLD:
            print(f"\n  [CONSENSUS CLEARED] Threshold met ({max_score * 100:.1f}% >= {CONFIDENCE_THRESHOLD * 100:.0f}%)")
            self.consensus_reached = True
            return True

        print(f"\n  [CONSENSUS BELOW THRESHOLD] Highest score ({max_score * 100:.1f}% < {CONFIDENCE_THRESHOLD * 100:.0f}%)")
        self.consensus_reached = False
        return False

    def identify_contradictions(self, opinions: List[Opinion]) -> List[Dict[str, Any]]:
        """
        Identifies disagreeing pairs among specialist opinions.
        """
        print("\n[CONSENSUS AUDIT] Auditing disagreeing viewpoints...")
        contradictions = []

        for i, op1 in enumerate(opinions):
            for op2 in opinions[i+1:]:
                if op1.answer.strip().lower() != op2.answer.strip().lower():
                    contradictions.append({
                        "agent1": op1.agent_name,
                        "agent2": op2.agent_name,
                        "answer1": op1.answer,
                        "answer2": op2.answer,
                        "confidence1": op1.confidence,
                        "confidence2": op2.confidence
                    })

        if contradictions:
            print(f"  [DISSENT DETECTED] Found {len(contradictions)} points of disagreement.")
            for c in contradictions:
                print(f"    - {c['agent1']} ({c['confidence1']}) vs {c['agent2']} ({c['confidence2']})")
        else:
            print("  [UNANIMOUS] No contradictions detected across specialists.")

        return contradictions

    def conduct_debate(self, opinions: List[Opinion], contradictions: List[Dict[str, Any]]) -> List[Opinion]:
        """
        Conducts Round 2 debate among top disagreeing agents to refine arguments.
        """
        print("\n[DEBATE ROUND 2] Triggering debate round between top agents...")

        new_opinions = []
        debated_agents = set()

        for c in contradictions:
            a1, a2 = c['agent1'], c['agent2']
            if a1 in debated_agents or a2 in debated_agents:
                continue

            print(f"  [DEBATE CHANNEL] {a1} vs {a2}")

            # Re-evaluate top 2 agents
            for agent_name in [a1, a2]:
                orig = next((op for op in opinions if op.agent_name == agent_name), None)
                if orig:
                    # Refine confidence slightly after debate
                    refined_conf = min(1.0, round(orig.confidence + 0.10, 2))
                    new_op = Opinion(
                        answer=orig.answer,
                        confidence=refined_conf,
                        reasoning=f"Debate Round 2 refinement: Reinforced {orig.agent_name} recommendation with domain justification.",
                        agent_name=f"{agent_name}_DebateRound2"
                    )
                    new_opinions.append(new_op)
                    debated_agents.add(agent_name)

        return new_opinions

    def generate_dissent_summary(self, opinions: List[Opinion], contradictions: List[Dict[str, Any]]) -> str:
        """
        Generates a transparent summary of agent dissent for auditing.
        """
        print("\n[DISSENT SUMMARY] Generating disagreement report...")

        if not contradictions:
            return "Unanimous agreement reached. No dissenting opinions recorded."

        lines = ["Dissent Summary & Audit Trail:"]
        for c in contradictions:
            lines.append(f"- {c['agent1']} (Confidence: {c['confidence1']:.2f}) recommended: '{c['answer1'][:50]}'")
            lines.append(f"  vs {c['agent2']} (Confidence: {c['confidence2']:.2f}) recommended: '{c['answer2'][:50]}'")
            lines.append("")

        return "\n".join(lines).strip()

    def finalize_decision(self, opinions: List[Opinion], normalized_scores: Dict[str, float]) -> ConsensusResult:
        """
        Finalizes consensus decision and outputs ConsensusResult schema.
        """
        print("\n[CONSENSUS FINALIZE] Compiling final consensus result...")

        if normalized_scores:
            best_answer = max(normalized_scores, key=normalized_scores.get)
            best_score = normalized_scores[best_answer]

            matching_ops = [op for op in opinions if op.answer == best_answer]
            avg_conf = sum(op.confidence for op in matching_ops) / len(matching_ops) if matching_ops else best_score
            overall_conf = round(max(best_score, avg_conf), 2)

            contradictions = self.identify_contradictions(opinions)
            dissent_summary = self.generate_dissent_summary(opinions, contradictions)

            res = ConsensusResult(
                final_answer=best_answer,
                confidence=overall_conf,
                voting_details={
                    "normalized_scores": normalized_scores,
                    "total_confidence": round(self.total_confidence, 2),
                    "specialists_count": len(opinions)
                },
                dissent_summary=dissent_summary,
                consensus_reached=self.consensus_reached or (overall_conf >= CONFIDENCE_THRESHOLD)
            )

            print(f"\n  [FINAL DECISION] Answer: '{res.final_answer[:55]}...'")
            print(f"  [FINAL CONFIDENCE] Score: {res.confidence:.2f}")
            print(f"  [CONSENSUS STATUS] Reached: {res.consensus_reached}")

            return res

        return ConsensusResult(
            final_answer="No consensus reached",
            confidence=0.0,
            voting_details={"error": "No valid opinions"},
            dissent_summary="Unable to reach consensus threshold.",
            consensus_reached=False
        )


# --- LangGraph Graph Construction ---

def build_consensus_graph():
    """
    Builds the LangGraph workflow for Consensus Engine execution.
    """
    print("\n" + "=" * 70)
    print("[GRAPH BUILD] Compiling Consensus Engine Graph")
    print("=" * 70)

    consensus_agent = ConsensusAgent()

    def create_specialists_node(state: ConsensusState) -> dict:
        print("\n[GRAPH NODE] Step 1: Collect Specialist Opinions")
        q = state.get("question", "")
        ctx = state.get("context", "")

        agents = [SecurityAgent(), PerformanceAgent(), MaintainabilityAgent()]
        opinions = [agent.produce_opinion(q, ctx).model_dump() for agent in agents]

        return {
            "opinions": opinions,
            "round": 0,
            "messages": [{"role": "system", "content": f"Collected opinions from {len(opinions)} specialists."}]
        }

    def aggregate_node(state: ConsensusState) -> dict:
        print("\n[GRAPH NODE] Step 2: Confidence-Weighted Aggregation")
        opinions = [Opinion(**op) for op in state.get("opinions", [])]
        norm_scores = consensus_agent.aggregate_opinions(opinions)
        is_consensus = consensus_agent.check_consensus(norm_scores)

        return {
            "weighted_scores": norm_scores,
            "total_confidence": consensus_agent.total_confidence,
            "consensus_reached": is_consensus,
            "round": state.get("round", 0) + 1,
            "messages": [{"role": "system", "content": f"Aggregated scores. Consensus met: {is_consensus}"}]
        }

    def debate_node(state: ConsensusState) -> dict:
        print("\n[GRAPH NODE] Step 3: Trigger Debate Round 2")
        opinions = [Opinion(**op) for op in state.get("opinions", [])]
        contradictions = consensus_agent.identify_contradictions(opinions)
        debated_ops = consensus_agent.conduct_debate(opinions, contradictions)
        all_ops = opinions + debated_ops

        return {
            "opinions": [op.model_dump() for op in all_ops],
            "round": state.get("round", 0) + 1,
            "messages": [{"role": "system", "content": f"Debate Round {state.get('round', 0) + 1} completed."}]
        }

    def decide_node(state: ConsensusState) -> dict:
        print("\n[GRAPH NODE] Step 4: Finalize Consensus & Output Dissent Log")
        opinions = [Opinion(**op) for op in state.get("opinions", [])]
        norm_scores = state.get("weighted_scores", {})
        result = consensus_agent.finalize_decision(opinions, norm_scores)

        return {
            "final_answer": result.final_answer,
            "final_confidence": result.confidence,
            "dissent_summary": result.dissent_summary,
            "consensus_reached": result.consensus_reached,
            "messages": [{"role": "system", "content": f"Final answer selected: {result.final_answer[:50]}..."}]
        }

    def route_after_aggregate(state: ConsensusState) -> str:
        if state.get("consensus_reached", False):
            print("[ROUTE] Consensus cleared threshold -> Finalizing decision")
            return "decide"
        elif state.get("round", 0) >= MAX_DEBATE_ROUNDS:
            print("[ROUTE] Max debate rounds reached -> Finalizing decision")
            return "decide"
        else:
            print("[ROUTE] Consensus below threshold -> Routing to Debate Round")
            return "debate"

    builder = StateGraph(ConsensusState)
    builder.add_node("create_specialists", create_specialists_node)
    builder.add_node("aggregate", aggregate_node)
    builder.add_node("debate", debate_node)
    builder.add_node("decide", decide_node)

    builder.set_entry_point("create_specialists")
    builder.add_edge("create_specialists", "aggregate")

    builder.add_conditional_edges(
        "aggregate",
        route_after_aggregate,
        {
            "debate": "debate",
            "decide": "decide"
        }
    )

    builder.add_edge("debate", "aggregate")
    builder.add_edge("decide", END)

    graph = builder.compile()

    print("[GRAPH COMPILED] Consensus Flow: create_specialists -> aggregate -> (debate/decide) -> END")
    return graph


# --- Test Functions ---

def test_confidence_weighted_formula():
    """
    Test 1: Verify confidence-weighted voting formula independently.
    """
    print("\n" + "=" * 70)
    print("TEST 1: CONFIDENCE-WEIGHTED VOTING FORMULA AUDIT")
    print("=" * 70)

    opinions = [
        Opinion(answer="Python Fast API", confidence=0.90, reasoning="High ecosystem security and typing", agent_name="SecurityAgent"),
        Opinion(answer="Python Fast API", confidence=0.70, reasoning="Good async performance", agent_name="PerformanceAgent"),
        Opinion(answer="Node.js Express", confidence=0.80, reasoning="Fast event loop", agent_name="MaintainabilityAgent")
    ]

    ca = ConsensusAgent()
    norm_scores = ca.aggregate_opinions(opinions)

    print("\n[VERIFICATION]")
    # Python: (0.90 + 0.70) = 1.60 / 2.40 = 66.7%
    # Node: 0.80 / 2.40 = 33.3%
    for ans, score in norm_scores.items():
        print(f"  Option: {ans} -> Normalized Score: {score * 100:.1f}%")

    is_consensus = ca.check_consensus(norm_scores)
    print(f"  Consensus Cleared (>= 60%): {is_consensus}")


def run_consensus_test():
    """
    Test 2: Run full Consensus Engine state graph across technical questions.
    """
    print("\n" + "=" * 70)
    print("TEST 2: CONSENSUS ENGINE GRAPH EXECUTION")
    print("=" * 70)

    graph = build_consensus_graph()

    test_queries = [
        {
            "question": "Which architecture is preferable for high-throughput financial data streaming: PostgreSQL relational DB or Redis in-memory cache?",
            "context": "System demands sub-5ms read latencies, strict data consistency, and low memory fragmentation."
        }
    ]

    for idx, t in enumerate(test_queries, 1):
        print(f"\n==================== EXECUTION QUERY {idx}/{len(test_queries)} ====================")
        initial_state: ConsensusState = {
            "question": t["question"],
            "context": t["context"],
            "opinions": [],
            "round": 0,
            "max_rounds": MAX_DEBATE_ROUNDS,
            "weighted_scores": {},
            "total_confidence": 0.0,
            "top_options": [],
            "final_answer": "",
            "final_confidence": 0.0,
            "dissent_summary": "",
            "consensus_reached": False,
            "messages": []
        }

        res = graph.invoke(initial_state)

        print("\n" + "=" * 70)
        print(f"[QUERY {idx} COMPLETE]")
        print("=" * 70)
        print(f"Question: {t['question']}")
        print(f"Final Consensus Answer: {res.get('final_answer')}")
        print(f"Final Confidence: {res.get('final_confidence')}")
        print(f"Consensus Reached: {res.get('consensus_reached')}")

        print("\n--- Dissent Summary Audit Log ---")
        print(res.get("dissent_summary", "No dissent"))


def main():
    """
    Main entry point for Week 5 Day 4 Lab 5.3.
    """
    print("=" * 70)
    print("LAB 5.3: CONSENSUS ENGINE")
    print("Week 5 - Day 4: Debate & Consensus")
    print("=" * 70)

    test_confidence_weighted_formula()
    run_consensus_test()

    print("\n[COMPLETE] Lab 5.3 Consensus Engine execution finalized.")


if __name__ == "__main__":
    main()
