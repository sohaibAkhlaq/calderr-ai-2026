import streamlit as st
import time
import uuid
import pandas as pd
from memory_engine import MemoryEngine
from fact_extractor import FactExtractor
from research_agent import ResearchAgent

# Configure Page
st.set_page_config(page_title="Long-Term Research Assistant", page_icon="🧠", layout="wide")

# Custom CSS for Premium UI
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Dark Theme & Glassmorphism */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: rgba(22, 27, 34, 0.7);
        border-radius: 12px;
        padding: 10px 20px;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px;
        color: #8b949e;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        color: #58a6ff;
        background-color: rgba(88, 166, 255, 0.1);
    }
    
    /* Chat Messages */
    .stChatMessage {
        background-color: rgba(22, 27, 34, 0.8) !important;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(5px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Metric Cards */
    div[data-testid="metric-container"] {
        background-color: rgba(33, 38, 45, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #f0f6fc !important;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stMarkdown, .stDataFrame {
        animation: fadeIn 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# Application State Initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    
@st.cache_resource
def init_system():
    engine = MemoryEngine()
    extractor = FactExtractor()
    agent = ResearchAgent(engine, extractor)
    return engine, agent

engine, agent = init_system()

# UI Layout
st.title("🧠 Long-Term Personal Research Assistant")
st.markdown("*A highly contextual agent that builds a persistent memory and adapts to your needs.*")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["💬 Live Interaction", "🔍 Memory Inspector", "👤 User Profile Viewer"])

# --- TAB 1: LIVE INTERACTION ---
with tab1:
    st.markdown("### Engage with your Assistant")
    
    # Display chat history for current session from memory engine
    recent_logs = engine.get_recent_history(st.session_state.session_id, limit=20)
    for log in recent_logs:
        with st.chat_message(log["role"]):
            st.markdown(log["content"])

    # Chat Input
    if prompt := st.chat_input("Ask a question, state a preference, or define a goal..."):
        # User Message
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Assistant Response with loading animation
        with st.chat_message("assistant"):
            with st.spinner("Analyzing memory and synthesizing response..."):
                start_time = time.time()
                response = agent.get_response(prompt, st.session_state.session_id)
                latency = time.time() - start_time
                st.markdown(response)
                st.caption(f"⏱️ Response generated in {latency:.2f}s | Context integrated from episodic & semantic memory.")
                
        st.rerun()

# --- TAB 2: MEMORY INSPECTOR ---
with tab2:
    st.markdown("### Internal Memory States")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Semantic Facts (ChromaDB)")
        facts = engine.get_all_facts()
        if facts:
            df_facts = pd.DataFrame(facts)
            st.dataframe(df_facts, use_container_width=True, hide_index=True)
            st.metric("Total Extracted Facts", len(facts))
        else:
            st.info("No semantic facts extracted yet. Start chatting to build knowledge.")
            
    with col2:
        st.subheader("Episodic Logs (SQLite)")
        logs = engine.get_all_episodic_logs()
        if logs:
            df_logs = pd.DataFrame(logs, columns=["Timestamp", "Session ID", "Role", "Content", "Importance"])
            st.dataframe(df_logs, use_container_width=True, hide_index=True)
            st.metric("Total Interactions Logged", len(logs))
        else:
            st.info("No episodic logs available.")

# --- TAB 3: USER PROFILE VIEWER ---
with tab3:
    st.markdown("### Dynamic User Persona")
    st.markdown("*Continuously synthesized from interaction facts.*")
    
    profile = engine.get_user_profile()
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**🧠 Known Topics & Expertise:**")
        if profile.get("known_topics"):
            for t in profile["known_topics"]:
                st.markdown(f"- `{t}`")
        else:
            st.markdown("*None established yet.*")
            
        st.markdown("**🎯 Active Research Goals:**")
        if profile.get("active_research_goals"):
            for g in profile["active_research_goals"]:
                st.markdown(f"- {g}")
        else:
            st.markdown("*None active.*")
            
    with col_b:
        st.markdown("**📝 Communication Style Preference:**")
        st.info(profile.get("communication_style", "Not specified - using standard format."))
        
        st.markdown("**📏 Preferred Depth of Explanation:**")
        st.info(profile.get("preferred_depth", "Not specified - balancing depth."))
        
    st.divider()
    st.markdown("**Raw JSON Profile Data:**")
    st.json(profile)
