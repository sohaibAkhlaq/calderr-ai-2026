"""
Project 4-P-A: AI-Powered Hiring Pipeline - Streamlit Production App
Enterprise Grade Web UI for HR Teams with LangGraph Orchestration.
"""

import streamlit as st
import pandas as pd
import sqlite3
import json
import plotly.express as px
from langgraph.types import Command
from hiring_engine import build_hiring_graph, CandidateState, DB_PATH

st.set_page_config(
    page_title="AI-Powered Hiring Pipeline | LangGraph",
    page_icon="💼",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; color: #1E3A8A; font-weight: 800; }
    .sub-header { font-size: 1.1rem; color: #4B5563; margin-bottom: 25px; }
    .stMetric { background-color: #F3F4F6; padding: 12px; border-radius: 8px; }
    .card-box { background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 10px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_graph():
    return build_hiring_graph()

graph = get_graph()

# Sample Resumes Database (10 Benchmark Resumes)
SAMPLE_RESUMES = [
    {
        "id": "CAND-001",
        "name": "Sohaib Akhlaq",
        "role": "AI Agentic Engineer",
        "exp": 4.5,
        "skills": ["Python", "LangGraph", "FastAPI", "Docker", "RAG", "LLM"],
        "resume": "Senior AI Engineer with 4.5 years experience building complex agentic systems with LangGraph, FastAPI, Docker, and hybrid vector RAG retrieval."
    },
    {
        "id": "CAND-002",
        "name": "Amina Khan",
        "role": "Senior Python Developer",
        "exp": 6.0,
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AsyncIO"],
        "resume": "Lead backend engineer proficient in Python microservices, PostgreSQL query optimization, FastAPI endpoints, and Docker containerization."
    },
    {
        "id": "CAND-003",
        "name": "David Miller",
        "role": "AI Agentic Engineer",
        "exp": 2.0,
        "skills": ["Python", "Machine Learning", "Pandas"],
        "resume": "Junior candidate born in 2005 with basic Python and Pandas knowledge. Graduated in 1990 with Ivy League graduate only preference."
    },
    {
        "id": "CAND-004",
        "name": "Elena Rostova",
        "role": "Data Scientist",
        "exp": 5.0,
        "skills": ["Python", "Machine Learning", "Pandas", "NumPy", "Scikit-Learn", "SQL"],
        "resume": "Experienced Data Scientist skilled in predictive analytics, Scikit-Learn pipelines, SQL aggregations, and mother of two handling data modeling."
    },
    {
        "id": "CAND-005",
        "name": "Marcus Vance",
        "role": "AI Agentic Engineer",
        "exp": 7.0,
        "skills": ["Python", "LangGraph", "LangChain", "LLM", "FastAPI", "Docker", "RAG"],
        "resume": "Staff AI Architect specializing in autonomous agent loops, prompt evaluation benchmarks, and scalable LangGraph deployments."
    },
    {
        "id": "CAND-006",
        "name": "Sophia Zhang",
        "role": "Senior Python Developer",
        "exp": 5.5,
        "skills": ["Python", "FastAPI", "Docker", "PostgreSQL", "PyTest"],
        "resume": "Backend developer with 5.5 years focusing on test-driven development, FastAPI server architectures, and Docker automated builds."
    },
    {
        "id": "CAND-007",
        "name": "James O'Connor",
        "role": "AI Agentic Engineer",
        "exp": 1.0,
        "skills": ["Python", "HTML"],
        "resume": "Junior web enthusiast looking to transition into AI engineering. Limited exposure to LLM frameworks."
    },
    {
        "id": "CAND-008",
        "name": "Fatima Al-Mansoor",
        "role": "Data Scientist",
        "exp": 4.0,
        "skills": ["Python", "Machine Learning", "Pandas", "NumPy", "SQL"],
        "resume": "Data Scientist with 4 years experience building churn prediction models, feature engineering pipelines, and SQL dashboards."
    },
    {
        "id": "CAND-009",
        "name": "Robert Chen",
        "role": "Senior Python Developer",
        "exp": 8.0,
        "skills": ["Python", "FastAPI", "Docker", "PostgreSQL", "AsyncIO", "PyTest"],
        "resume": "Principal software engineer with 8 years of Python experience, native English speakers only preference, and cloud deployments."
    },
    {
        "id": "CAND-010",
        "name": "Zoe Taylor",
        "role": "AI Agentic Engineer",
        "exp": 3.5,
        "skills": ["Python", "LangGraph", "LangChain", "LLM", "RAG"],
        "resume": "AI Engineer skilled in building stateful LangGraph agents, RAG retrival engines, and custom prompt evaluation toolings."
    }
]

# Header UI
st.markdown('<div class="main-header">💼 AI-Powered Hiring Pipeline Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Week 4 Production Project (4-P-A): LangGraph StateGraph, Bias Detection & HITL Governance</div>', unsafe_allow_html=True)

# Tabs Navigation
tab1, tab2, tab3, tab4 = st.tabs(["🚀 Ingest Candidate", "⚖️ HR Approval Portal", "📊 Pipeline Audit Analytics", "📐 Graph Architecture"])

with tab1:
    st.markdown("### 📄 Ingest & Process Resume")
    
    col_in1, col_in2 = st.columns([1, 1])
    
    with col_in1:
        st.markdown("#### Select Benchmark Resume or Custom Input")
        preset_option = st.selectbox("Select Candidate Preset", ["Custom Entry"] + [f"{c['name']} ({c['role']})" for c in SAMPLE_RESUMES])
        
        if preset_option != "Custom Entry":
            selected_cand = next(c for c in SAMPLE_RESUMES if f"{c['name']} ({c['role']})" == preset_option)
            default_id = selected_cand["id"]
            default_name = selected_cand["name"]
            default_role = selected_cand["role"]
            default_exp = selected_cand["exp"]
            default_skills = ", ".join(selected_cand["skills"])
            default_resume = selected_cand["resume"]
        else:
            default_id = "CAND-100"
            default_name = "Jane Doe"
            default_role = "AI Agentic Engineer"
            default_exp = 4.0
            default_skills = "Python, LangGraph, LLM, FastAPI"
            default_resume = "Experienced AI developer specializing in LangGraph agent workflows."

        with st.form("ingest_form"):
            c_id = st.text_input("Candidate ID", value=default_id)
            c_name = st.text_input("Candidate Name", value=default_name)
            c_role = st.selectbox("Target Job Role", ["AI Agentic Engineer", "Senior Python Developer", "Data Scientist"], index=0)
            c_exp = st.number_input("Years of Experience", value=default_exp, step=0.5)
            c_skills = st.text_input("Key Skills (comma separated)", value=default_skills)
            c_resume = st.text_area("Full Resume Text", value=default_resume, height=120)

            submit_cand = st.form_submit_button("Run Hiring Pipeline Graph")

    with col_in2:
        st.markdown("#### ⚡ Real-Time Graph Output")
        if submit_cand:
            skills_list = [s.strip() for s in c_skills.split(",") if s.strip()]
            thread_id = f"thread_{c_id}"
            config = {"configurable": {"thread_id": thread_id}}

            init_state: CandidateState = {
                "candidate_id": c_id,
                "candidate_name": c_name,
                "target_role": c_role,
                "experience_years": c_exp,
                "skills": skills_list,
                "resume_text": c_resume,
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
            st.session_state["active_thread"] = thread_id

            st.success(f"Pipeline executed for {c_name}!")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Match Score", f"{snapshot.values.get('match_score', 0):.1f}/100")
            m2.metric("Shortlisted", "YES" if snapshot.values.get('shortlisted') else "NO")
            m3.metric("Bias Warning", "FLAGGED" if snapshot.values.get('bias_detected') else "CLEAN")

            if snapshot.values.get("bias_flags"):
                st.warning("⚠️ **Bias Detection Flags:**")
                for flag in snapshot.values["bias_flags"]:
                    st.write(f"- {flag}")

            st.markdown("##### 📜 Node Audit Execution Logs")
            for log in snapshot.values.get("audit_logs", []):
                st.info(log)

            if snapshot.next and "human_review" in snapshot.next:
                st.error("🛑 **Workflow Interrupted at HR Review Node!** Switch to 'HR Approval Portal' tab to review and approve.")

with tab2:
    st.markdown("### ⚖️ HR Manager Review Portal (Human-in-the-Loop)")
    active_thread = st.session_state.get("active_thread", "thread_CAND-001")
    thread_input = st.text_input("Active Candidate Thread ID", value=active_thread)

    config = {"configurable": {"thread_id": thread_input}}
    snapshot = graph.get_state(config)

    if snapshot and snapshot.values:
        val = snapshot.values
        st.markdown(f"#### Reviewing Candidate: **{val.get('candidate_name')}** ({val.get('target_role')})")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Score", f"{val.get('match_score', 0):.1f}/100")
        c2.metric("Experience", f"{val.get('experience_years')} yrs")
        c3.metric("Bias Warnings", len(val.get("bias_flags", [])))

        st.markdown("##### ❓ AI-Generated Tailored Interview Questions")
        for q in val.get("interview_questions", []):
            st.write(f"- {q}")

        if snapshot.next and "human_review" in snapshot.next:
            st.markdown("---")
            st.warning("⚠️ **ACTION REQUIRED: Resume Pending Manager Approval**")
            hr_notes = st.text_area("HR Manager Notes / Rationale", value="Candidate passed technical bar and question review.")
            
            b_app, b_rej = st.columns(2)
            if b_app.button("✅ Approve & Hire Candidate"):
                res = graph.invoke(Command(resume={"decision": "approved", "notes": hr_notes}), config)
                st.success(f"Candidate {val.get('candidate_name')} HIRED! Recorded to SQLite database.")
                st.rerun()

            if b_rej.button("❌ Reject Candidate"):
                res = graph.invoke(Command(resume={"decision": "rejected", "notes": hr_notes}), config)
                st.error(f"Candidate {val.get('candidate_name')} REJECTED. Recorded to SQLite database.")
                st.rerun()
        else:
            st.info(f"Current Status: **{val.get('final_status', 'complete').upper()}**")
    else:
        st.info("No active interrupted candidate thread selected. Ingest a candidate first.")

with tab3:
    st.markdown("### 📊 Pipeline Audit Analytics & Reports")
    
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM hiring_audit_logs ORDER BY timestamp DESC", conn)
    conn.close()

    if not df.empty:
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Total Resumes Audited", len(df))
        col_m2.metric("Total Hired", len(df[df['final_status'] == 'hired']))
        col_m3.metric("Total Rejected", len(df[df['final_status'] == 'rejected']))
        col_m4.metric("Bias Flag Rate", f"{(df['bias_detected'].sum() / len(df)) * 100:.1f}%")

        st.markdown("#### 📈 Candidate Score Distribution")
        fig = px.histogram(df, x="match_score", color="final_status", nbins=10, title="Match Score Distribution by Hiring Outcome")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 📜 Persistent SQLite Audit Records")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No audit logs found in SQLite database. Run candidates to generate analytics.")

with tab4:
    st.markdown("### 📐 LangGraph Workflow Architecture")
    st.code("""
    [Ingest Resume] ──> [Score Candidate] ──> [Bias Check Node] ──(Conditional Router)
                                                                        ├── Shortlisted ──> [Generate Questions] ──> [HITL Human Review]
                                                                        │                                                      ├── Approved ──> [Final Hire] ──> [SQLite Export] ──> END
                                                                        │                                                      └── Rejected ──> [Final Reject] ─> [SQLite Export] ──> END
                                                                        └── Not Shortlisted ───────────────────────────────────────────────────> [Final Reject] ─> [SQLite Export] ──> END
    """, language="text")
