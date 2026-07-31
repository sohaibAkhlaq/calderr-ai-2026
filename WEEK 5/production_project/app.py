"""
Autonomous AI Research Lab - Streamlit Enterprise Control Plane

Production web interface for executing 5-phase autonomous deep research,
monitoring dynamic agent assembly, inspecting critic challenges & peer review scorecards,
and downloading published research papers.

Usage:
    streamlit run app.py
"""

import sys
import os
import json
import time
from datetime import datetime
import streamlit as st
import pandas as pd

from graph import build_research_graph
from schemas import ResearchReport
from agents import ReportPublisher

# --- Page Config & Enterprise CSS ---

st.set_page_config(
    page_title="Autonomous AI Research Lab Control Plane",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Global App Background & Typography */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Executive Metric Card */
    .metric-card {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-val {
        font-size: 24px;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-lbl {
        font-size: 12px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Phase Stepper Badge */
    .phase-badge {
        display: inline-block;
        background-color: #0284c7;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 8px;
    }
    
    /* Evidence & Critic Cards */
    .evidence-card {
        background-color: #1e293b;
        border-left: 4px solid #38bdf8;
        padding: 14px;
        border-radius: 6px;
        margin-bottom: 12px;
    }
    .critic-card {
        background-color: #311b92;
        border-left: 4px solid #b388ff;
        padding: 14px;
        border-radius: 6px;
        margin-bottom: 12px;
    }
    
    .header-main {
        font-size: 30px;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 2px;
    }
    .header-sub {
        font-size: 14px;
        color: #94a3b8;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


# --- Cached Graph & Helper ---

@st.cache_resource
def get_compiled_research_graph():
    return build_research_graph()

research_graph = get_compiled_research_graph()


def execute_research_pipeline(question: str) -> ResearchReport:
    report_id = f"rep_{int(time.time()*1000)}"
    initial_state = {
        "question": question,
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
    return ResearchReport(**report_dict)


# --- Sidebar ---

with st.sidebar:
    st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=64)
    st.markdown("### Research Lab Control")
    st.markdown("---")

    query_input = st.text_area(
        "Research Question Prompt",
        value="Evaluate multi-agent orchestration frameworks for enterprise production",
        height=100
    )

    st.markdown("#### Sample Demo Topics")
    topic_preset = st.selectbox(
        "Select Research Topic Preset",
        ["Custom Input", "LLM Multi-Agent Orchestration", "Healthcare AI Reliability", "Cybersecurity Vulnerability Mitigation"]
    )

    if topic_preset == "LLM Multi-Agent Orchestration":
        query_input = "Evaluate multi-agent orchestration frameworks for enterprise production"
    elif topic_preset == "Healthcare AI Reliability":
        query_input = "Investigate reliability and safety verification of AI diagnostic models in clinical healthcare"
    elif topic_preset == "Cybersecurity Vulnerability Mitigation":
        query_input = "Analyze automated threat modeling and vulnerability patch verification using autonomous AI agents"

    st.markdown("---")
    run_btn = st.button("Launch 5-Phase Autonomous Research", width="stretch", type="primary")

    st.markdown("---")
    st.caption("Architecture: 5-Phase Multi-Phase Graph")
    st.caption("Phase 1: Domain & Hypothesis")
    st.caption("Phase 2: Dynamic Evidence RAG")
    st.caption("Phase 3: Critic Challenge Audit")
    st.caption("Phase 4: Synthesis Body")
    st.caption("Phase 5: Peer Review & Publish")


# --- Main Dashboard ---

st.markdown('<div class="header-main">Autonomous AI Research Lab</div>', unsafe_allow_html=True)
st.markdown('<div class="header-sub">Fully Autonomous 5-Phase Deep Research Engine with Critic Challenge & Peer Review</div>', unsafe_allow_html=True)

if run_btn or "current_research_report" not in st.session_state:
    with st.spinner(f"Executing 5-phase autonomous deep research for: '{query_input[:50]}...'"):
        report = execute_research_pipeline(query_input)
        st.session_state["current_research_report"] = report
else:
    report = st.session_state["current_research_report"]


# --- Top Metrics Row ---

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-val">{report.peer_review.approval_status}</div>
        <div class="metric-lbl">Peer Review Status</div>
    </div>
    ''', unsafe_allow_html=True)

with c2:
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-val">{report.peer_review.methodological_rigor * 100:.0f}%</div>
        <div class="metric-lbl">Methodological Rigor</div>
    </div>
    ''', unsafe_allow_html=True)

with c3:
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-val">{len(report.evidence_gathered)}</div>
        <div class="metric-lbl">Evidence Items</div>
    </div>
    ''', unsafe_allow_html=True)

with c4:
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-val">{report.execution_time_sec}s</div>
        <div class="metric-lbl">Execution Time</div>
    </div>
    ''', unsafe_allow_html=True)

with c5:
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-val">${report.cost_usd:.6f}</div>
        <div class="metric-lbl">Estimated Cost USD</div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# --- Tabs ---

t_summary, t_hypothesis, t_evidence, t_critic, t_paper, t_export = st.tabs([
    "Executive Summary & Peer Review", "Tested Hypothesis", "Evidence & Citations", "Critic Challenges", "Full Paper Body", "Observability & Export"
])

with t_summary:
    st.subheader(f"Published Research Brief: {report.title}")
    st.info(report.executive_summary)

    st.markdown("#### Peer Review Scorecard (Phase 5 Audit)")
    sc_col1, sc_col2, sc_col3 = st.columns(3)
    sc_col1.metric("Methodological Rigor", f"{report.peer_review.methodological_rigor * 100:.0f}%")
    sc_col2.metric("Citation Completeness", f"{report.peer_review.citation_completeness * 100:.0f}%")
    sc_col3.metric("Logical Coherence", f"{report.peer_review.coherence_rating * 100:.0f}%")

    st.markdown(f"**Reviewer Notes:** {report.peer_review.reviewer_notes}")

with t_hypothesis:
    st.subheader("Phase 1: Formulated Hypothesis")
    st.markdown(f"**Hypothesis ID:** `{report.hypothesis.hypothesis_id}`")
    st.markdown(f"**Title:** {report.hypothesis.title}")
    st.markdown(f"**Core Hypothesis Statement:**\n> {report.hypothesis.statement}")

    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.markdown("**Expected Validation Indicators:**")
        for outcome in report.hypothesis.expected_outcomes:
            st.markdown(f"- {outcome}")

    with col_h2:
        st.markdown("**Identified Failure Modes & Risks:**")
        for risk in report.hypothesis.risk_factors:
            st.markdown(f"- {risk}")

with t_evidence:
    st.subheader(f"Phase 2: Gathered Evidence ({len(report.evidence_gathered)} Items)")
    for idx, ev in enumerate(report.evidence_gathered, 1):
        st.markdown(f'''
        <div class="evidence-card">
            <h4>Evidence #{idx}: {ev.sub_question}</h4>
            <p><b>Finding:</b> {ev.finding}</p>
            <p><b>Specialist Agent:</b> {ev.agent_name} | <b>Quality Score:</b> {ev.quality_score * 100:.0f}%</p>
            <p><b>Source Citation:</b> <code>{ev.source_citation}</code></p>
        </div>
        ''', unsafe_allow_html=True)

with t_critic:
    st.subheader(f"Phase 3: Critic Agent Evidence Audit ({len(report.critic_challenges)} Challenges)")
    if report.critic_challenges:
        for idx, ch in enumerate(report.critic_challenges, 1):
            st.markdown(f'''
            <div class="critic-card">
                <h4>Critic Challenge #{idx}: {ch.challenge_type} (Severity: {ch.severity})</h4>
                <p><b>Critique:</b> {ch.critique}</p>
                <p><b>Recommended Revision:</b> {ch.suggested_revision}</p>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.success("No critical flaws flagged by Critic Agent.")

with t_paper:
    st.subheader("Phase 4: Synthesized Autonomous Research Paper Body")
    st.markdown(report.synthesis_report)

with t_export:
    st.subheader("Observability & Export Center")

    st.markdown("#### Phase Execution Trace")
    phase_df = pd.DataFrame([
        {"Phase": "Phase 1", "Node": "DomainClassifier & HypothesisGenerator", "Tokens": 190, "Status": "Completed"},
        {"Phase": "Phase 2", "Node": "Dynamic Specialist Evidence Gatherers", "Tokens": 420, "Status": "Completed"},
        {"Phase": "Phase 3", "Node": "CriticAgent Evidence Challenge Audit", "Tokens": 160, "Status": "Completed"},
        {"Phase": "Phase 4", "Node": "SynthesisAgent Paper Body Assembly", "Tokens": 220, "Status": "Completed"},
        {"Phase": "Phase 5", "Node": "PeerReviewAgent & ReportPublisher", "Tokens": 130, "Status": "Published"}
    ])
    st.dataframe(phase_df, width="stretch")

    st.markdown("#### Download Published Report")
    dl_col1, dl_col2 = st.columns(2)

    with dl_col1:
        md_text = ReportPublisher.to_markdown(report)
        st.download_button(
            label="Download Markdown Paper (.md)",
            data=md_text,
            file_name=f"{report.report_id}.md",
            mime="text/markdown",
            width="stretch"
        )

    with dl_col2:
        json_text = ReportPublisher.to_json(report)
        st.download_button(
            label="Download JSON Data (.json)",
            data=json_text,
            file_name=f"{report.report_id}.json",
            mime="application/json",
            width="stretch"
        )
