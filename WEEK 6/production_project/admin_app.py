import streamlit as st
import pandas as pd
import json
import time
import uuid
import os
from platform_memory_engine import PlatformMemoryEngine
from consolidation_worker import ConsolidationWorker
from eval_retrieval_quality import MemoryEvaluator

# Page Configuration
st.set_page_config(page_title="Enterprise AI Memory Platform Admin", page_icon="🌐", layout="wide")

# Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0b0f19; color: #c9d1d9; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; background-color: rgba(22, 27, 34, 0.8); border-radius: 12px; padding: 8px 16px; }
    .stTabs [data-baseweb="tab"] { color: #8b949e; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #58a6ff; background-color: rgba(88, 166, 255, 0.1); border-radius: 8px; }
    div[data-testid="metric-container"] { background: rgba(22, 27, 34, 0.8); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 16px; }
    .test-pass { background: linear-gradient(135deg, rgba(46, 160, 67, 0.2), rgba(46, 160, 67, 0.05)); border-left: 4px solid #2ea043; padding: 12px 16px; border-radius: 8px; margin: 8px 0; }
    .test-fail { background: linear-gradient(135deg, rgba(248, 81, 73, 0.2), rgba(248, 81, 73, 0.05)); border-left: 4px solid #f85149; padding: 12px 16px; border-radius: 8px; margin: 8px 0; }
    .header-box { background: linear-gradient(135deg, rgba(88, 166, 255, 0.12), rgba(136, 132, 216, 0.08)); border: 1px solid rgba(88, 166, 255, 0.25); padding: 16px 20px; border-radius: 12px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# State
if "engine" not in st.session_state:
    st.session_state.engine = PlatformMemoryEngine()
if "worker" not in st.session_state:
    st.session_state.worker = ConsolidationWorker(st.session_state.engine)

engine = st.session_state.engine
worker = st.session_state.worker

# Ensure demo tenants exist
demo_tenants = ["tenant_alpha", "tenant_beta", "tenant_gamma"]
for t in demo_tenants:
    if t not in engine.get_all_tenants():
        engine.store_fact(t, f"Default initialization fact for {t}", "system")
        engine.register_procedural_rule(t, "general", "Unchecked input", "Validate input schema", 0.85)

st.title("🌐 Enterprise AI Memory Platform")
st.markdown("*Multi-Tenant Memory-as-a-Service Infrastructure & Observability Admin Dashboard*")
st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏢 Multi-Tenant Inspector",
    "🕸️ Knowledge Graph",
    "⚙️ Procedural Rules",
    "🧹 Consolidation Controller",
    "🧪 Automated Test Suite"
])

# ==============================================================================
# TAB 1: MULTI-TENANT INSPECTOR
# ==============================================================================
with tab1:
    tenants = engine.get_all_tenants()
    col_t1, col_t2 = st.columns([1, 3])

    with col_t1:
        selected_tenant = st.selectbox("Select Tenant Namespace:", tenants if tenants else ["tenant_alpha"])
        stats = engine.get_tenant_stats(selected_tenant)
        st.markdown("### Tenant Stats")
        st.metric("Episodic Logs", stats["episodic_count"])
        st.metric("Semantic Facts", stats["semantic_count"])
        st.metric("Procedural Rules", stats["procedural_count"])
        st.metric("Graph Nodes", stats["graph_nodes"])

    with col_t2:
        st.markdown(f"### Live Memory State for `{selected_tenant}`")
        
        tab_sub1, tab_sub2 = st.tabs(["Semantic Memory (Vector Search)", "Episodic Interactions"])
        
        with tab_sub1:
            q = st.text_input("Semantic Search Query:", value="PostgreSQL or infrastructure preferences")
            if st.button("Search Facts", key="btn_search"):
                res = engine.search_semantic_facts(selected_tenant, q)
                if res:
                    st.dataframe(pd.DataFrame(res), width="stretch", hide_index=True)
                else:
                    st.info("No matching semantic facts found for this tenant.")
            else:
                facts = engine.get_all_facts(selected_tenant)
                if facts:
                    st.dataframe(pd.DataFrame(facts), width="stretch", hide_index=True)
                else:
                    st.info("No semantic facts stored for this tenant.")
                    
        with tab_sub2:
            episodes = engine.get_all_episodes(selected_tenant)
            if episodes:
                st.dataframe(pd.DataFrame(episodes), width="stretch", hide_index=True)
            else:
                st.info("No episodic logs stored for this tenant.")

# ==============================================================================
# TAB 2: KNOWLEDGE GRAPH
# ==============================================================================
with tab2:
    st.markdown("### 🕸️ Multi-Tenant Knowledge Graph Explorer")
    t_graph = st.selectbox("Select Tenant for Graph View:", engine.get_all_tenants(), key="sb_graph")
    
    col_g1, col_g2 = st.columns([1, 2])
    with col_g1:
        st.markdown("**Add New Relationship Triple:**")
        sub = st.text_input("Subject Entity:", value="FastAPI")
        pred = st.text_input("Predicate / Relation:", value="USES")
        obj = st.text_input("Object Entity:", value="Pydantic")
        if st.button("Add Triple", key="btn_triple"):
            engine.add_graph_triples(t_graph, [{"subject": sub, "predicate": pred, "object": obj}])
            st.success(f"Added triple: {sub} -> {pred} -> {obj}")
            st.rerun()
            
    with col_g2:
        graph_data = engine.get_full_tenant_graph(t_graph)
        st.markdown(f"**Knowledge Graph Structure (`{t_graph}`)**")
        st.metric("Total Graph Nodes", graph_data["node_count"])
        st.metric("Total Graph Edges", graph_data["edge_count"])
        
        if graph_data["nodes"]:
            col_n, col_e = st.columns(2)
            with col_n:
                st.markdown("**Nodes List:**")
                st.dataframe(pd.DataFrame(graph_data["nodes"]), width="stretch", hide_index=True)
            with col_e:
                st.markdown("**Edges List:**")
                st.dataframe(pd.DataFrame(graph_data["edges"]), width="stretch", hide_index=True)
        else:
            st.info("Knowledge Graph is empty for this tenant. Add triples to build graph.")

# ==============================================================================
# TAB 3: PROCEDURAL RULES
# ==============================================================================
with tab3:
    st.markdown("### ⚙️ Procedural Memory & Error Correction Rules")
    t_rules = st.selectbox("Select Tenant for Rules:", engine.get_all_tenants(), key="sb_rules")
    
    col_r1, col_r2 = st.columns([1, 2])
    with col_r1:
        st.markdown("**Register New Correction Rule:**")
        dom = st.text_input("Domain:", value="sql_queries")
        mistake = st.text_input("Original Mistake:", value="Using SELECT * in production queries")
        rule = st.text_input("Correction Rule:", value="Specify explicit column names in SELECT statements")
        conf = st.slider("Confidence Score:", 0.0, 1.0, 0.85)
        if st.button("Register Rule", key="btn_reg_rule"):
            engine.register_procedural_rule(t_rules, dom, mistake, rule, conf)
            st.success("Rule registered successfully!")
            st.rerun()
            
    with col_r2:
        rules = engine.query_procedural_rules(t_rules)
        st.markdown(f"**Active Rules for `{t_rules}`**")
        if rules:
            st.dataframe(pd.DataFrame(rules), width="stretch", hide_index=True)
        else:
            st.info("No procedural rules registered for this tenant.")

# ==============================================================================
# TAB 4: CONSOLIDATION CONTROLLER
# ==============================================================================
with tab4:
    st.markdown("### 🧹 Async Memory Consolidation Controller")
    st.markdown("*Summarize old episodes, promote active rules, and prune decayed memory.*")
    
    t_cons = st.selectbox("Select Tenant for Consolidation:", engine.get_all_tenants(), key="sb_cons")
    retention = st.slider("Max Episodic Retention Limit:", 10, 200, 30)
    thresh = st.slider("Importance Score Pruning Threshold:", 1.0, 5.0, 2.0)
    
    if st.button("🚀 Trigger Consolidation Cycle", type="primary", key="btn_trigger_cons"):
        with st.spinner("Consolidating tenant memory..."):
            report = worker.consolidate_tenant_memory(
                t_cons, max_episodic_retention=retention, prune_importance_threshold=thresh
            )
            st.success("Consolidation cycle completed!")
            st.json(report)

# ==============================================================================
# TAB 5: AUTOMATED TEST SUITE
# ==============================================================================
with tab5:
    st.markdown("### 🧪 Automated Platform Verification & Test Suite")
    st.markdown("*Execute comprehensive unit, multi-tenant boundary, and integration tests with one click.*")
    st.markdown("---")

    def render_test_result(name, passed, detail=""):
        icon = "✅" if passed else "❌"
        css_class = "test-pass" if passed else "test-fail"
        st.markdown(f'<div class="{css_class}"><strong>{icon} {name}</strong><br/>{detail}</div>', unsafe_allow_html=True)

    if st.button("🚀 Run All Platform Tests", type="primary", use_container_width=True, key="btn_run_tests"):
        test_db = "data/platform_test_runner.db"
        if os.path.exists(test_db):
            try: os.remove(test_db)
            except: pass
            
        t_engine = PlatformMemoryEngine(db_path=test_db)
        t_worker = ConsolidationWorker(t_engine)
        
        passed_count = 0
        failed_count = 0
        total_tests = 0

        # --- GROUP 1: MULTI-TENANT ISOLATION ---
        st.markdown('<div class="header-box"><strong>🔒 Test Group 1: Multi-Tenant Boundary Isolation</strong></div>', unsafe_allow_html=True)
        
        # Test 1.1: Semantic Isolation
        total_tests += 1
        try:
            t_engine.store_fact("tenant_sec_A", "Confidential Key Alpha 123", "secret")
            t_engine.store_fact("tenant_sec_B", "Confidential Key Beta 999", "secret")
            res_A = t_engine.search_semantic_facts("tenant_sec_A", "Confidential Key")
            has_beta_data = any("Beta 999" in r["fact"] for r in res_A)
            if not has_beta_data and len(res_A) > 0:
                render_test_result("1.1 Semantic Vector Isolation", True, "Tenant A vector search returned 0 facts from Tenant B. Strict isolation confirmed.")
                passed_count += 1
            else:
                render_test_result("1.1 Semantic Vector Isolation", False, f"Data leaked across tenant boundaries! Results: {res_A}")
                failed_count += 1
        except Exception as e:
            render_test_result("1.1 Semantic Vector Isolation", False, str(e))
            failed_count += 1

        # Test 1.2: Episodic Isolation
        total_tests += 1
        try:
            t_engine.log_episode("tenant_sec_A", "sess_A", "user_A", "user", "Alpha message")
            t_engine.log_episode("tenant_sec_B", "sess_B", "user_B", "user", "Beta message")
            ep_A = t_engine.get_all_episodes("tenant_sec_A")
            ep_B = t_engine.get_all_episodes("tenant_sec_B")
            has_leak = any(e["tenant_id"] != "tenant_sec_A" for e in ep_A)
            if not has_leak and len(ep_A) == 1 and len(ep_B) == 1:
                render_test_result("1.2 Episodic Store Isolation", True, "Episodic queries isolated strictly per tenant_id.")
                passed_count += 1
            else:
                render_test_result("1.2 Episodic Store Isolation", False, "Episodic store leaked entries!")
                failed_count += 1
        except Exception as e:
            render_test_result("1.2 Episodic Store Isolation", False, str(e))
            failed_count += 1

        # Test 1.3: Graph Isolation
        total_tests += 1
        try:
            t_engine.add_graph_triples("tenant_sec_A", [{"subject": "AlphaNode", "predicate": "OWNS", "object": "AlphaAsset"}])
            t_engine.add_graph_triples("tenant_sec_B", [{"subject": "BetaNode", "predicate": "OWNS", "object": "BetaAsset"}])
            g_A = t_engine.get_full_tenant_graph("tenant_sec_A")
            g_B = t_engine.get_full_tenant_graph("tenant_sec_B")
            nodes_A = [n["id"] for n in g_A["nodes"]]
            nodes_B = [n["id"] for n in g_B["nodes"]]
            if "BetaNode" not in nodes_A and "AlphaNode" not in nodes_B:
                render_test_result("1.3 Knowledge Graph Isolation", True, "Tenant NetworkX sub-graphs isolated per tenant namespace.")
                passed_count += 1
            else:
                render_test_result("1.3 Knowledge Graph Isolation", False, "Graph node collision detected!")
                failed_count += 1
        except Exception as e:
            render_test_result("1.3 Knowledge Graph Isolation", False, str(e))
            failed_count += 1

        # --- GROUP 2: VECTOR ENGINE & COSINE SIMILARITY ---
        st.markdown('<div class="header-box"><strong>🧬 Test Group 2: Semantic Vector Engine & Ranking</strong></div>', unsafe_allow_html=True)

        # Test 2.1: Similarity Accuracy
        total_tests += 1
        try:
            t_engine.store_fact("t_vec", "User specializes in PostgreSQL database tuning", "skill")
            t_engine.store_fact("t_vec", "User likes baking Italian sourdough bread", "hobby")
            hits = t_engine.search_semantic_facts("t_vec", "PostgreSQL database performance")
            if len(hits) >= 1 and "PostgreSQL" in hits[0]["fact"]:
                render_test_result("2.1 Cosine Similarity Precision", True, f"Top result: '{hits[0]['fact']}' (Sim: {hits[0]['similarity']})")
                passed_count += 1
            else:
                render_test_result("2.1 Cosine Similarity Precision", False, f"Incorrect top hit: {hits}")
                failed_count += 1
        except Exception as e:
            render_test_result("2.1 Cosine Similarity Precision", False, str(e))
            failed_count += 1

        # Test 2.2: Category Filtering
        total_tests += 1
        try:
            hits_hobby = t_engine.search_semantic_facts("t_vec", "baking", category_filter="hobby")
            if len(hits_hobby) == 1 and hits_hobby[0]["category"] == "hobby":
                render_test_result("2.2 Vector Metadata Category Filtering", True, "Successfully filtered vector search by category='hobby'.")
                passed_count += 1
            else:
                render_test_result("2.2 Vector Metadata Category Filtering", False, f"Filter failed: {hits_hobby}")
                failed_count += 1
        except Exception as e:
            render_test_result("2.2 Vector Metadata Category Filtering", False, str(e))
            failed_count += 1

        # --- GROUP 3: PROCEDURAL MEMORY & CONSOLIDATION ---
        st.markdown('<div class="header-box"><strong>⚙️ Test Group 3: Procedural Rules & Consolidation Worker</strong></div>', unsafe_allow_html=True)

        # Test 3.1: Rule Registration & Application Counter
        total_tests += 1
        try:
            r_id = t_engine.register_procedural_rule("t_proc", "sql", "Raw SQL query", "Use ORM queries", 0.8)
            t_engine.increment_rule_application(r_id)
            t_engine.increment_rule_application(r_id)
            rules = t_engine.query_procedural_rules("t_proc", "sql")
            if rules and rules[0]["application_count"] == 2:
                render_test_result("3.1 Procedural Rule Application Counter", True, f"Application count incremented to {rules[0]['application_count']}.")
                passed_count += 1
            else:
                render_test_result("3.1 Procedural Rule Application Counter", False, f"Rules: {rules}")
                failed_count += 1
        except Exception as e:
            render_test_result("3.1 Procedural Rule Application Counter", False, str(e))
            failed_count += 1

        # Test 3.2: Consolidation Worker Execution
        total_tests += 1
        try:
            for i in range(15):
                t_engine.log_episode("t_cons", "s1", "u1", "user", f"Message {i}", importance_score=1.0)
            report = t_worker.consolidate_tenant_memory("t_cons", max_episodic_retention=5, prune_importance_threshold=2.0)
            remaining = t_engine.get_all_episodes("t_cons")
            if report["episodes_pruned"] > 0 and len(remaining) <= 5:
                render_test_result("3.2 Async Consolidation Worker Pruning", True, f"Pruned {report['episodes_pruned']} low-importance episodes. Remaining: {len(remaining)}.")
                passed_count += 1
            else:
                render_test_result("3.2 Async Consolidation Worker Pruning", False, f"Report: {report}, Remaining: {len(remaining)}")
                failed_count += 1
        except Exception as e:
            render_test_result("3.2 Async Consolidation Worker Pruning", False, str(e))
            failed_count += 1

        # --- GROUP 4: KNOWLEDGE GRAPH MULTI-HOP ---
        st.markdown('<div class="header-box"><strong>🕸️ Test Group 4: Knowledge Graph Multi-Hop Traversal</strong></div>', unsafe_allow_html=True)

        # Test 4.1: Graph Path Traversal
        total_tests += 1
        try:
            t_engine.add_graph_triples("t_graph", [
                {"subject": "FastAPI", "predicate": "USES", "object": "Pydantic"},
                {"subject": "Pydantic", "predicate": "VALIDATES", "object": "JSON_Schema"}
            ])
            res = t_engine.query_tenant_graph("t_graph", "FastAPI", max_depth=2)
            nodes = [n["id"] for n in res["nodes"]]
            if "FastAPI" in nodes and "Pydantic" in nodes and "JSON_Schema" in nodes:
                render_test_result("4.1 Graph Multi-Hop Traversal", True, f"2-hop path found: FastAPI -> Pydantic -> JSON_Schema ({res['node_count']} nodes)")
                passed_count += 1
            else:
                render_test_result("4.1 Graph Multi-Hop Traversal", False, f"Nodes found: {nodes}")
                failed_count += 1
        except Exception as e:
            render_test_result("4.1 Graph Multi-Hop Traversal", False, str(e))
            failed_count += 1

        # --- FINAL METRICS ---
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("✅ Passed Tests", passed_count)
        with c2: st.metric("❌ Failed Tests", failed_count)
        with c3:
            pass_rate = round((passed_count / total_tests) * 100) if total_tests > 0 else 0
            st.metric("📊 Platform Pass Rate", f"{pass_rate}%")

        if failed_count == 0:
            st.success(f"🎉 ALL {total_tests} PLATFORM TESTS PASSED! Multi-tenant memory platform is fully operational.")
        else:
            st.warning(f"⚠️ {failed_count} test(s) failed.")

        try: os.remove(test_db)
        except: pass
