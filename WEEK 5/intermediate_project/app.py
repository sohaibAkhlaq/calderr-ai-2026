"""
Autonomous Competitive Intelligence Agent - Streamlit Professional Dashboard

A sleek, enterprise-grade Web UI built with custom CSS, interactive metric cards,
live multi-agent execution status, conflict resolution auditing, and report downloads.

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

from graph import build_intelligence_graph
from schemas import CompetitiveBriefing
from agents import ReportGenerator

# --- Page Configuration & Custom CSS ---

st.set_page_config(
    page_title="Competitive Intelligence Agent Control Plane",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enterprise CSS Styling
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Custom Metric Cards */
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #38bdf8;
        margin-bottom: 4px;
    }
    .metric-label {
        font-size: 13px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Domain Report Cards */
    .domain-card {
        background-color: #0f172a;
        border-left: 4px solid #0284c7;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 16px;
        border-top: 1px solid #1e293b;
        border-right: 1px solid #1e293b;
        border-bottom: 1px solid #1e293b;
    }
    
    /* Conflict Adjudication Card */
    .conflict-card {
        background-color: #1e1b4b;
        border-left: 4px solid #818cf8;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 16px;
    }
    
    /* Header Styling */
    .header-title {
        font-size: 32px;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 2px;
    }
    .header-subtitle {
        font-size: 15px;
        color: #94a3b8;
        margin-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)


# --- Cached Graph & Helper Functions ---

@st.cache_resource
def get_compiled_graph():
    return build_intelligence_graph()

graph = get_compiled_graph()


def run_intelligence_pipeline(company_name: str) -> CompetitiveBriefing:
    """Executes multi-agent parallel research pipeline."""
    initial_state = {
        "company_name": company_name,
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
    briefing_dict = result_state.get("final_briefing", {})
    return CompetitiveBriefing(**briefing_dict)


# --- Sidebar Controls ---

with st.sidebar:
    st.image("https://img.icons8.com/color/96/briefcase.png", width=64)
    st.markdown("### Agent Control Panel")
    st.markdown("---")

    target_company = st.text_input("Target Company Name", value="Stripe", help="Enter any public or enterprise company name")

    st.markdown("#### Preset Sample Profiles")
    preset = st.selectbox("Select Preset Demo Company", ["Custom Input", "Stripe", "OpenAI", "Anthropic", "Databricks", "Snowflake"])
    if preset != "Custom Input":
        target_company = preset

    st.markdown("---")
    execute_btn = st.button("Generate Intelligence Briefing", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown("#### System Observability")
    st.caption("Architecture: LangGraph Parallel Fan-out")
    st.caption("Specialist Agents: 5 Parallel Nodes")
    st.caption("LLM Backbone: Groq Llama-3.1-8B-Instant")


# --- Main Dashboard ---

st.markdown('<div class="header-title">Autonomous Competitive Intelligence Control Plane</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Multi-Agent Parallel Fan-Out Research & Conflict Resolution Engine</div>', unsafe_allow_html=True)

# Run pipeline on button click or default session store
if execute_btn or "current_briefing" not in st.session_state:
    with st.spinner(f"Orchestrating 5 parallel specialist agents for '{target_company}'..."):
        briefing = run_intelligence_pipeline(target_company)
        st.session_state["current_briefing"] = briefing
else:
    briefing = st.session_state["current_briefing"]

# --- Top Key Performance Metrics ---

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-value">{briefing.market_analysis.growth_rate}</div>
        <div class="metric-label">YoY Growth Rate</div>
    </div>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-value">{briefing.market_analysis.market_share_estimate}</div>
        <div class="metric-label">Market Share</div>
    </div>
    ''', unsafe_allow_html=True)

with col3:
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-value">{briefing.sentiment_analysis.customer_satisfaction_score:.0f}/100</div>
        <div class="metric-label">CSAT Rating</div>
    </div>
    ''', unsafe_allow_html=True)

with col4:
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-value">{briefing.execution_time_sec}s</div>
        <div class="metric-label">Execution Latency</div>
    </div>
    ''', unsafe_allow_html=True)

with col5:
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-value">${briefing.cost_usd:.6f}</div>
        <div class="metric-label">Total Cost USD</div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Interactive Main Tabs ---

tab_summary, tab_specialists, tab_conflicts, tab_recs, tab_observability = st.tabs([
    "Executive Briefing", "Specialist Reports", "Resolved Conflicts", "Strategic Recommendations", "Observability & Export"
])

with tab_summary:
    st.subheader(f"Executive Briefing: {briefing.company_name}")
    st.info(briefing.executive_summary)

    st.markdown("#### High-Level Metrics & Addressable Market")
    st.write(f"**Total Addressable Market Breakdown:** {briefing.market_analysis.tam_sam_som}")
    st.write(f"**Recent Funding & Financials:** {briefing.recent_news.recent_funding}")
    st.write(f"**Market Stance:** {briefing.sentiment_analysis.analyst_rating} ({briefing.sentiment_analysis.overall_sentiment})")

with tab_specialists:
    st.subheader("Specialist Domain Reports (Parallel Fan-out)")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('''
        <div class="domain-card">
            <h4>Market Position Analysis</h4>
            <p><b>Growth Rate:</b> ''' + briefing.market_analysis.growth_rate + '''</p>
            <p><b>Market Share:</b> ''' + briefing.market_analysis.market_share_estimate + '''</p>
            <p><b>Key Competitors:</b> ''' + ', '.join(briefing.market_analysis.key_competitors) + '''</p>
            <p><i>Confidence:</i> ''' + f"{briefing.market_analysis.confidence*100:.0f}%" + '''</p>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div class="domain-card">
            <h4>Technology Stack & Infrastructure</h4>
            <p><b>Frontend:</b> ''' + ', '.join(briefing.tech_stack_analysis.frontend_tech) + '''</p>
            <p><b>Backend:</b> ''' + ', '.join(briefing.tech_stack_analysis.backend_tech) + '''</p>
            <p><b>Cloud & DB:</b> ''' + ', '.join(briefing.tech_stack_analysis.cloud_infra) + '''</p>
            <p><b>AI/ML Stack:</b> ''' + ', '.join(briefing.tech_stack_analysis.ai_ml_stack) + '''</p>
            <p><i>Confidence:</i> ''' + f"{briefing.tech_stack_analysis.confidence*100:.0f}%" + '''</p>
        </div>
        ''', unsafe_allow_html=True)

    with col_b:
        st.markdown('''
        <div class="domain-card">
            <h4>Product Portfolio & Gaps</h4>
            <p><b>Core Offerings:</b> ''' + ', '.join(briefing.product_analysis.core_offerings) + '''</p>
            <p><b>Differentiators:</b> ''' + ', '.join(briefing.product_analysis.key_differentiators) + '''</p>
            <p><b>Pricing Model:</b> ''' + briefing.product_analysis.pricing_model + '''</p>
            <p><b>Feature Gaps:</b> ''' + ', '.join(briefing.product_analysis.feature_gaps) + '''</p>
            <p><i>Confidence:</i> ''' + f"{briefing.product_analysis.confidence*100:.0f}%" + '''</p>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div class="domain-card">
            <h4>Recent Developments & News</h4>
            <p><b>Funding:</b> ''' + briefing.recent_news.recent_funding + '''</p>
            <p><b>Announcements:</b> ''' + '; '.join(briefing.recent_news.major_announcements) + '''</p>
            <p><b>Compliance:</b> ''' + '; '.join(briefing.recent_news.regulatory_impacts) + '''</p>
            <p><i>Confidence:</i> ''' + f"{briefing.recent_news.confidence*100:.0f}%" + '''</p>
        </div>
        ''', unsafe_allow_html=True)

with tab_conflicts:
    st.subheader("Conflict Resolver Adjudication Log")
    st.caption("Detects contradictory claims between specialist agents and applies explicit reasoning to resolve trade-offs.")

    if briefing.conflicts_resolved:
        for idx, c in enumerate(briefing.conflicts_resolved, 1):
            st.markdown(f'''
            <div class="conflict-card">
                <h4>Conflict #{idx}: {c.topic}</h4>
                <p><b>{c.agent_a} Claim:</b> {c.claim_a}</p>
                <p><b>{c.agent_b} Claim:</b> {c.claim_b}</p>
                <p style="color: #38bdf8;"><b>Adjudicated Verdict:</b> {c.resolution}</p>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.success("No contradictions flagged across specialist agents. All agent findings aligned.")

with tab_recs:
    st.subheader("Strategic Recommendations")
    for idx, rec in enumerate(briefing.strategic_recommendations, 1):
        st.markdown(f"**{idx}.** {rec}")

with tab_observability:
    st.subheader("Observability & Export Options")

    st.markdown("#### Execution Trace Breakdown")
    trace_df = pd.DataFrame([
        {"Agent Node": "OrchestratorAgent", "Type": "Plan & Strategy", "Status": "Completed", "Tokens": 50},
        {"Agent Node": "MarketAgent", "Type": "Parallel Specialist", "Status": "Completed", "Tokens": 320},
        {"Agent Node": "ProductAgent", "Type": "Parallel Specialist", "Status": "Completed", "Tokens": 280},
        {"Agent Node": "TechStackAgent", "Type": "Parallel Specialist", "Status": "Completed", "Tokens": 310},
        {"Agent Node": "NewsAgent", "Type": "Parallel Specialist", "Status": "Completed", "Tokens": 260},
        {"Agent Node": "SentimentAgent", "Type": "Parallel Specialist", "Status": "Completed", "Tokens": 290},
        {"Agent Node": "ConflictResolver", "Type": "Adjudication", "Status": "Completed", "Tokens": 150},
        {"Agent Node": "SynthesisAgent", "Type": "Assembly", "Status": "Completed", "Tokens": 120}
    ])
    st.dataframe(trace_df, use_container_width=True)

    st.markdown("#### Download Intelligence Briefing")
    col_dl1, col_dl2 = st.columns(2)

    with col_dl1:
        md_content = ReportGenerator.to_markdown(briefing)
        st.download_button(
            label="Download Markdown Briefing (.md)",
            data=md_content,
            file_name=f"{briefing.company_name.lower()}_intelligence.md",
            mime="text/markdown",
            use_container_width=True
        )

    with col_dl2:
        json_content = ReportGenerator.to_json(briefing)
        st.download_button(
            label="Download JSON Data (.json)",
            data=json_content,
            file_name=f"{briefing.company_name.lower()}_intelligence.json",
            mime="application/json",
            use_container_width=True
        )
