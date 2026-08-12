"""
Production Project 7-P-A: Universal Enterprise Tool Hub — Streamlit Dashboard
A 6-Panel Enterprise Admin Observability & Control Platform:
1. 🏛️ Enterprise Ecosystem Overview & Architecture
2. 🔒 Per-Tenant RBAC & Access Matrix Inspector
3. 💚 Real-Time Server Health & Metrics Monitor
4. 🛠️ Live Interactive Tool Explorer
5. ⚡ 50 Concurrent Calls Load Test Benchmark
6. 🧪 100% Automated Verification Test Suite
"""

import streamlit as st
import json
import time
import sqlite3
import pandas as pd
from hub_gateway import hub_gateway, TENANT_RBAC, AUDIT_DB_PATH
from langgraph_hub_agent import LangGraphEnterpriseHubAgent
from load_test_hub import run_load_test
from test_production_hub import run_tests_dict

# Streamlit Page Config
st.set_page_config(
    page_title="Universal Enterprise Tool Hub",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Dark Theme CSS
st.markdown("""
    <style>
        .main { background-color: #0d1117; color: #c9d1d9; }
        .stButton>button { background-color: #1f6feb; color: white; border-radius: 6px; font-weight: 600; }
        .stButton>button:hover { background-color: #388bfd; border-color: #58a6ff; }
        .status-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; margin-bottom: 12px; }
        .success-badge { background-color: #238636; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: bold; }
        .forbidden-badge { background-color: #da3633; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)


# Sidebar Tenant Switcher
st.sidebar.title("🏛️ Enterprise Control Plane")
st.sidebar.markdown("---")

tenant_selection = st.sidebar.selectbox(
    "Active Tenant Identity",
    options=["Tenant_Alpha (key_tenant_alpha)", "Tenant_Beta (key_tenant_beta)", "Enterprise_Admin (key_enterprise_admin)"],
    index=2
)

api_key_map = {
    "Tenant_Alpha (key_tenant_alpha)": "key_tenant_alpha",
    "Tenant_Beta (key_tenant_beta)": "key_tenant_beta",
    "Enterprise_Admin (key_enterprise_admin)": "key_enterprise_admin"
}

active_key = api_key_map[tenant_selection]
tenant_rbac_info = TENANT_RBAC[active_key]

st.sidebar.markdown(f"**Tenant ID**: `{tenant_rbac_info['tenant_id']}`")
st.sidebar.markdown(f"**Allowed Namespaces**: `{tenant_rbac_info['allowed_namespaces']}`")
st.sidebar.markdown("---")

# Health Status Summary
health = hub_gateway.get_health()
st.sidebar.markdown(f"**Gateway Status**: `{health['gateway_status']}` ({health['online_servers']})")


# Header
st.title("🏛️ Universal Enterprise Tool Hub")
st.markdown("##### Production-Grade MCP Gateway Hosting 5 Specialized Tool Servers with Per-Tenant RBAC & Observability")
st.markdown("---")


# Tabs Navigation
t1, t2, t3, t4, t5, t6 = st.tabs([
    "🏛️ Ecosystem Overview",
    "🔒 Tenant RBAC Inspector",
    "💚 Real-Time Health",
    "🛠️ Live Tool Explorer",
    "⚡ Load Test Benchmark",
    "🧪 Automated Test Suite"
])


# =============================================================================
# PANEL 1: ECOSYSTEM OVERVIEW & ARCHITECTURE
# =============================================================================
with t1:
    st.header("🏛️ Enterprise Tool Ecosystem Architecture")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Hosted Servers", "5 Servers")
    m2.metric("Total Exposed Tools", "16 Tools")
    m3.metric("Supported Tenants", "3 Profiles")
    m4.metric("Gateway Uptime", "100.0%")

    st.markdown("---")
    st.subheader("System Architecture Diagram")
    st.code("""
  +-------------------------------------------------------------------------------+
  |                 LangGraph Enterprise Agent / AI Applications                  |
  +-------------------------------------------------------------------------------+
                                          |
                                          v  (HTTP + SSE / Namespaced JSON-RPC)
  +-------------------------------------------------------------------------------+
  |                 Universal Enterprise Tool Hub Gateway (hub_gateway.py)        |
  |   - Per-Tenant RBAC Policy Engine   |  Token-Bucket Rate Limiter (100/min)    |
  |   - 60-Second Tool Schema Cache     |  SQLite Security Audit Log              |
  +-------------------------------------------------------------------------------+
        |              |                  |                  |               |
        v              v                  v                  v               v
  +-----------+  +-----------+      +-----------+      +-----------+   +-----------+
  | Filesystem|  | Database  |      |  Comm.    |      | Analytics |   |Code Intel |
  | Server    |  | Server    |      | Server    |      | Server    |   |Server     |
  | (fs:*)    |  | (db:*)    |      | (comm:*)  |      | (analytics)|  | (code:*)  |
  +-----------+  +-----------+      +-----------+      +-----------+   +-----------+
    """, language="text")

    st.subheader("Run Multi-Server Enterprise Workflow")
    if st.button("🚀 Run LangGraph Multi-Server Workflow (5 Servers)", type="primary"):
        agent = LangGraphEnterpriseHubAgent(api_key=active_key)
        with st.spinner("Executing workflow across all 5 servers..."):
            wf_res = agent.run_enterprise_workflow()
        
        if wf_res.get("success"):
            st.success("🎉 Enterprise Workflow Completed Successfully Across All 5 Servers!")
            st.json(wf_res.get("logs"))


# =============================================================================
# PANEL 2: PER-TENANT RBAC INSPECTOR
# =============================================================================
with t2:
    st.header("🔒 Per-Tenant Role-Based Access Control (RBAC) Inspector")
    st.markdown("Verify tenant isolation boundaries. Tool requests for disallowed namespaces return **403 Forbidden**.")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.subheader("Current Policy Configuration")
        st.json(TENANT_RBAC)

    with col_r2:
        st.subheader("Test Namespace Permission Enforcement")
        test_tool = st.selectbox("Select Tool to Test", options=["fs:read_file", "db:query_table", "comm:draft_email", "analytics:compute_statistics", "code:analyze_file"])
        
        if st.button("🔒 Test Access Permission"):
            res_rbac = hub_gateway.route_tool_call(active_key, test_tool, {"filename": "test.txt", "table_name": "accounts", "recipient": "test@co.com", "code_content": "x=1"})
            
            if res_rbac.get("gateway_routed"):
                st.markdown('<span class="success-badge">ACCESS GRANTED (200 OK)</span>', unsafe_allow_html=True)
                st.json(res_rbac)
            else:
                st.markdown('<span class="forbidden-badge">ACCESS DENIED (403 FORBIDDEN)</span>', unsafe_allow_html=True)
                st.error(res_rbac.get("error"))


# =============================================================================
# PANEL 3: REAL-TIME SERVER HEALTH & METRICS
# =============================================================================
with t3:
    st.header("💚 Real-Time Server Health & Metrics Monitor")
    
    st.json(health)

    st.subheader("Recent Audit Log Activity")
    if st.button("🔄 Refresh Audit Logs"):
        conn = sqlite3.connect(AUDIT_DB_PATH)
        df = pd.read_sql_query("SELECT id, timestamp, tenant_id, namespaced_tool, status, latency_ms FROM hub_audit_logs ORDER BY id DESC LIMIT 10", conn)
        conn.close()
        st.dataframe(df, use_container_width=True)


# =============================================================================
# PANEL 4: LIVE INTERACTIVE TOOL EXPLORER
# =============================================================================
with t4:
    st.header("🛠️ Live Interactive Tool Explorer")
    
    discovery = hub_gateway.discover_tools()
    tool_names = list(discovery["schemas"].keys())
    
    selected_tool = st.selectbox("Select Namespaced Tool", options=tool_names)
    st.info(f"Description: {discovery['schemas'][selected_tool]['description']}")

    if st.button("⚡ Execute Tool via Gateway"):
        res_exec = hub_gateway.route_tool_call(active_key, selected_tool, {"filename": "test.txt", "table_name": "accounts", "metric_name": "revenue_usd", "code_content": "def foo(): pass\n", "recipient": "user@test.com", "subject": "Test", "body_text": "Hello"})
        st.json(res_exec)


# =============================================================================
# PANEL 5: LOAD TEST BENCHMARK
# =============================================================================
with t5:
    st.header("⚡ 50 Concurrent Tool Calls Load Test Benchmark")
    st.markdown("Executes 50 concurrent tool calls across all 5 downstream servers to evaluate gateway performance and 95th percentile latency.")

    if st.button("🚀 Run 50 Concurrent Calls Benchmark", type="primary"):
        with st.spinner("Running high-concurrency load benchmark..."):
            bench = run_load_test()
        
        st.markdown("---")
        b1, b2, b3, b4 = st.columns(4)
        b1.metric("Total Calls", bench["total_calls"])
        b2.metric("Success Rate", f"{bench['success_rate']}%")
        b3.metric("Avg Latency", f"{bench['avg_latency_ms']} ms")
        b4.metric("95th Percentile Latency", f"{bench['p95_latency_ms']} ms")

        if bench["status"] == "PASS":
            st.success("🎉 BENCHMARK PASSED! 95th Percentile Latency is under 2.0 seconds.")
        else:
            st.error("Benchmark failed target threshold.")


# =============================================================================
# PANEL 6: AUTOMATED TEST SUITE
# =============================================================================
with t6:
    st.header("🧪 100% Automated Verification Test Suite")

    if st.button("🚀 Run All Platform Tests", type="primary"):
        with st.spinner("Running test suite..."):
            results = run_tests_dict()
        
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("Passed Tests", results["passed"])
        c2.metric("Failed Tests", results["failed"])
        c3.metric("Pass Rate", f"{results['pass_rate']}%")

        if results["failed"] == 0:
            st.balloons()
            st.success("🎉 ALL PLATFORM TESTS PASSED PERFECTLY!")
        else:
            st.error("Some tests failed.")

        st.json(results["logs"])
