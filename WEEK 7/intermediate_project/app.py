"""
Project 7-I-A: Developer Productivity MCP Suite — Streamlit UI
A modern, dark-themed 5-panel web application:
1. 🤖 Autonomous PR Code Reviewer
2. 🔍 Code Intelligence & Static Analysis
3. 🐙 GitHub PR & Issue Manager
4. 📝 Documentation Generator
5. 🧪 Automated Test Suite
"""

import streamlit as st
import json
import time
import sqlite3
from dev_gateway import dev_gateway, AUDIT_DB_PATH
from langgraph_dev_agent import AutonomousDeveloperAgent
from test_dev_suite import run_tests_dict

# Streamlit Page Config
st.set_page_config(
    page_title="Developer Productivity MCP Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Dark Theme CSS
st.markdown("""
    <style>
        .main { background-color: #0e1117; color: #c9d1d9; }
        .stButton>button { background-color: #238636; color: white; border-radius: 6px; font-weight: 600; }
        .stButton>button:hover { background-color: #2ea043; border-color: #3fb950; }
        .metric-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; margin-bottom: 10px; }
        .code-box { background-color: #0d1117; border: 1px solid #30363d; padding: 10px; border-radius: 6px; font-family: monospace; }
    </style>
""", unsafe_allow_html=True)


# Sidebar Configuration
st.sidebar.title("⚡ Dev Suite Control")
st.sidebar.markdown("---")
api_key = st.sidebar.text_input("MCP API Key", value="key_dev_suite", type="password")
st.sidebar.markdown("---")

# Health Status
health = dev_gateway.get_health()
st.sidebar.markdown(f"**Gateway Status**: `{health.get('gateway_status')}`")
for prefix, s in health.get("servers", {}).items():
    st.sidebar.markdown(f"- **{prefix}:** `{s['name']}` ({s['tool_count']} tools)")


# Main Title Header
st.title("⚡ Developer Productivity MCP Suite")
st.markdown("##### Composable Tool Ecosystem for Autonomous Code Review, AST Intelligence & Documentation")
st.markdown("---")

# Tab Selection
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🤖 Autonomous PR Reviewer",
    "🔍 Code Intelligence & AST",
    "🐙 GitHub PR & Issues",
    "📝 Docstring & README Generator",
    "🧪 Automated Test Suite"
])


# =============================================================================
# TAB 1: AUTONOMOUS PR REVIEWER
# =============================================================================
with tab1:
    st.header("🤖 Autonomous PR Code Reviewer (LangGraph Agent)")
    st.markdown("Executes end-to-end PR review: reads diff $\\rightarrow$ analyzes AST & complexity $\\rightarrow$ checks smells $\\rightarrow$ generates docstrings $\\rightarrow$ creates GitHub review ticket.")

    col1, col2 = st.columns([1, 2])
    with col1:
        pr_id = st.selectbox("Select Pull Request", options=[101, 102], index=0)
        run_btn = st.button("🚀 Run Autonomous PR Review Workflow", use_container_width=True)

    with col2:
        if run_btn:
            agent = AutonomousDeveloperAgent(api_key=api_key)
            with st.spinner("Agent running multi-step MCP workflow..."):
                res = agent.run_pr_review_workflow(pr_id=pr_id)

            if res.get("success"):
                st.success(f"🎉 Workflow Completed! All {res.get('steps_completed')} Steps Executed Successfully.")
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Cyclomatic Complexity", res.get("complexity"))
                m2.metric("Code Quality Score", f"{res.get('quality_score')}/100")
                m3.metric("Created Issue Ticket", f"#{res.get('issue_id')}")

                st.subheader("Synthesized Google-Style Docstring")
                st.code(res.get("generated_docstring"), language="python")

                st.subheader("Generated Module README Markdown")
                st.markdown(res.get("readme_markdown"))
            else:
                st.error(f"Workflow Failed: {res.get('error')}")


# =============================================================================
# TAB 2: CODE INTELLIGENCE & AST ANALYSIS
# =============================================================================
with tab2:
    st.header("🔍 Code Intelligence & Static Analysis")
    st.markdown("Perform AST parsing, function signature extraction, cyclomatic complexity, and code smell detection.")

    sample_python_code = (
        "def process_user_data(user_list, filter_active=True):\n"
        "    results = []\n"
        "    for u in user_list:\n"
        "        if filter_active:\n"
        "            if u.get('is_active'):\n"
        "                if u.get('score', 0) > 50:\n"
        "                    results.append(u['name'])\n"
        "    return results\n"
    )

    input_code = st.text_area("Input Python Code Snippet", value=sample_python_code, height=200)

    if st.button("🔍 Analyze Code Structure"):
        res_ast = dev_gateway.route_tool_call(api_key, "code:analyze_file", {"code_content": input_code})
        res_smells = dev_gateway.route_tool_call(api_key, "code:detect_code_smells", {"code_content": input_code})
        res_deps = dev_gateway.route_tool_call(api_key, "code:find_dependencies", {"code_content": input_code})

        if res_ast.get("gateway_routed"):
            data = res_ast.get("result", {})
            metrics = data.get("metrics", {})

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Total Lines", metrics.get("total_lines"))
            col_b.metric("Cyclomatic Complexity", metrics.get("overall_cyclomatic_complexity"))
            col_c.metric("Quality Rating", metrics.get("complexity_rating"))

            st.subheader("Functions Discovered")
            st.json(data.get("functions"))

            st.subheader("Code Smell Detection")
            smell_data = res_smells.get("result", {})
            st.warning(f"Detected {smell_data.get('smell_count')} Code Smells (Quality Score: {smell_data.get('code_quality_score')}/100)")
            st.json(smell_data.get("smells"))


# =============================================================================
# TAB 3: GITHUB PR & ISSUE MANAGER
# =============================================================================
with tab3:
    st.header("🐙 GitHub PR & Issue Manager")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Open Pull Requests")
        if st.button("🔄 Refresh Open PRs"):
            res_prs = dev_gateway.route_tool_call(api_key, "gh:list_open_prs", {})
            st.json(res_prs.get("result", {}))

    with col_g2:
        st.subheader("Fetch PR Code Diff")
        pr_num = st.number_input("PR ID", value=101)
        if st.button("📄 View Diff"):
            res_diff = dev_gateway.route_tool_call(api_key, "gh:get_pr_diff", {"pr_id": pr_num})
            if res_diff.get("gateway_routed"):
                st.code(res_diff.get("result", {}).get("diff", ""), language="diff")


# =============================================================================
# TAB 4: DOCUMENTATION GENERATOR
# =============================================================================
with tab4:
    st.header("📝 Documentation Generator")

    doc_code = st.text_area("Function Code for Docstring", value="def calculate_risk(score: float, factor: int) -> float:\n    return score * factor / 100.0", height=120)
    
    if st.button("📝 Generate Google Docstring"):
        res_doc = dev_gateway.route_tool_call(api_key, "doc:generate_docstring", {"function_code": doc_code})
        if res_doc.get("gateway_routed"):
            st.code(res_doc.get("result", {}).get("generated_docstring"), language="python")


# =============================================================================
# TAB 5: AUTOMATED TEST SUITE
# =============================================================================
with tab5:
    st.header("🧪 Automated Verification Test Suite")
    st.markdown("Executes complete end-to-end verification across all 3 MCP servers, gateway auth, rate limiting, and agent workflows.")

    if st.button("🚀 Run Full Test Suite", type="primary"):
        with st.spinner("Running test suite..."):
            test_results = run_tests_dict()

        st.markdown("---")
        t_col1, t_col2, t_col3 = st.columns(3)
        t_col1.metric("Passed Tests", test_results["passed"])
        t_col2.metric("Failed Tests", test_results["failed"])
        t_col3.metric("Pass Rate", f"{test_results['pass_rate']}%")

        if test_results["failed"] == 0:
            st.balloons()
            st.success(f"🎉 ALL {test_results['total']} TESTS PASSED PERFECTLY!")
        else:
            st.error("Some tests failed. Check log below.")

        st.json(test_results["logs"])
