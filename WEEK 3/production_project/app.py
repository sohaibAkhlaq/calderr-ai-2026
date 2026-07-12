"""
app.py — Real-Time Research Engine (Streamlit Frontend)
=======================================================
Week 3 Production Project (Day 7) — Option B

Professional, human-made UI with Light Theme.
No AI-generated styling gimmicks — clean, enterprise-grade layout.
"""

import os
import sys
import time

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import streamlit as st

# ─── Page must be configured FIRST before any other st calls ─────────────────
st.set_page_config(
    page_title="Research Engine — Week 3 Production",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Import engine (after page config) ───────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from engine import ResearchEngine, ResearchEngineError, PipelineStage, EngineStatus

# ─── Custom CSS (Light Theme, professional typography) ────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ─── Header bar ─── */
    .app-header {
        background: #1B4FE4;
        padding: 1.2rem 2rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .app-header h1 {
        color: #FFFFFF;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0;
    }
    .app-header p {
        color: #C8D8FF;
        font-size: 0.85rem;
        margin: 0;
    }

    /* ─── Query box ─── */
    .stTextInput > div > div > input {
        border: 2px solid #D0D8F0;
        border-radius: 6px;
        font-size: 1rem;
        padding: 0.6rem 1rem;
        background: #FFFFFF;
        color: #1A1A2E;
        transition: border-color 0.2s;
    }
    .stTextInput > div > div > input:focus {
        border-color: #1B4FE4;
        outline: none;
        box-shadow: 0 0 0 3px rgba(27, 79, 228, 0.12);
    }

    /* ─── Result card ─── */
    .result-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F4;
        border-left: 4px solid #1B4FE4;
        border-radius: 8px;
        padding: 1.1rem 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 4px rgba(27, 79, 228, 0.06);
    }
    .result-card.rank-1 { border-left-color: #1B4FE4; }
    .result-card.rank-2 { border-left-color: #3B7AE2; }
    .result-card.rank-3 { border-left-color: #6EA1F1; }
    .result-card.rank-4 { border-left-color: #A8C4F8; }

    .result-meta {
        display: flex;
        gap: 0.6rem;
        margin-bottom: 0.5rem;
        flex-wrap: wrap;
    }
    .badge {
        background: #EEF2FF;
        color: #1B4FE4;
        padding: 0.15rem 0.55rem;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .badge-score {
        background: #F0FAF4;
        color: #1A6B42;
    }
    .result-content {
        font-size: 0.92rem;
        color: #2D3748;
        line-height: 1.65;
    }

    /* ─── Status pill ─── */
    .status-ready {
        display: inline-block;
        background: #ECFDF5;
        color: #1A6B42;
        border: 1px solid #A7F3D0;
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .status-error {
        display: inline-block;
        background: #FEF2F2;
        color: #9B1C1C;
        border: 1px solid #FECACA;
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* ─── Sidebar ─── */
    section[data-testid="stSidebar"] {
        background: #F4F6FA;
        border-right: 1px solid #E2E8F4;
    }

    /* ─── Stat tiles ─── */
    .stat-tile {
        background: #FFFFFF;
        border: 1px solid #E2E8F4;
        border-radius: 8px;
        padding: 0.9rem 1.2rem;
        text-align: center;
    }
    .stat-tile .num {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1B4FE4;
    }
    .stat-tile .label {
        font-size: 0.78rem;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* ─── Hide Streamlit branding ─── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ─── Session State Initialization ────────────────────────────────────────────
if "engine" not in st.session_state:
    st.session_state.engine = None
if "engine_status" not in st.session_state:
    st.session_state.engine_status = None
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0


# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="app-header">
        <div>
            <h1>🔬 Real-Time Research Engine</h1>
            <p>Week 3 Production Project · Hybrid BM25 + Semantic Search · Cross-Encoder Re-ranking</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Engine Control")
    st.markdown("---")

    # Initialize button
    if st.button("🚀 Initialize Engine", use_container_width=True, type="primary"):
        with st.spinner("Initializing pipeline... (first run downloads models & PDFs)"):
            engine = ResearchEngine()
            status_placeholder = st.empty()

            def on_progress(msg: str):
                status_placeholder.info(msg)

            status = engine.initialize(progress_callback=on_progress)
            status_placeholder.empty()

        if status.ready:
            st.session_state.engine = engine
            st.session_state.engine_status = status
            st.success("Engine is ready!")
        else:
            st.session_state.engine_status = status
            st.error(f"Initialization failed at: **{status.stage_failed}**")

    st.markdown("---")

    # Engine status display
    st.markdown("### 📊 Engine Status")
    if st.session_state.engine_status is None:
        st.markdown('<span class="status-error">⬤ Not Initialized</span>', unsafe_allow_html=True)
    elif st.session_state.engine_status.ready:
        st.markdown('<span class="status-ready">⬤ Ready</span>', unsafe_allow_html=True)
        st.markdown("")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                f'<div class="stat-tile"><div class="num">{st.session_state.engine_status.chunks_loaded}</div>'
                f'<div class="label">Chunks</div></div>',
                unsafe_allow_html=True,
            )
        with col_b:
            st.markdown(
                f'<div class="stat-tile"><div class="num">{st.session_state.total_queries}</div>'
                f'<div class="label">Queries</div></div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<span class="status-error">⬤ Error</span>', unsafe_allow_html=True)
        with st.expander("View Error Details"):
            st.error(f"**Failed Stage:** {st.session_state.engine_status.stage_failed}")
            st.code(st.session_state.engine_status.error or "No details available.")

    st.markdown("---")

    # Error handling reference
    st.markdown("### 🛡️ Fault Tolerance")
    with st.expander("Pipeline Failure Flow"):
        st.markdown(
            """
            | Step | Failure | Action |
            |------|---------|--------|
            | 1. Download | No internet / bad URL | **ABORT** — show error |
            | 2. Load | Corrupted / image PDF | **ABORT** — show error |
            | 3. Split | 0 chunks produced | **ABORT** — show error |
            | 4. Embed | HuggingFace offline | **ABORT** — show error |
            | 5. Store | Disk permission denied | **ABORT** — show error |
            | 6. Retrieve | Retriever fails | **ABORT** — show error |
            | 7. Re-rank | Cross-Encoder fails | **FALLBACK** — use hybrid ranking |
            """
        )

    st.markdown("---")
    st.markdown("### 📚 Knowledge Sources")
    st.markdown("- **Attention Is All You Need** (Vaswani et al., 2017)")
    st.markdown("- **BERT Pre-training** (Devlin et al., 2018)")

    st.markdown("---")
    # Sample queries
    st.markdown("### 💡 Sample Queries")
    sample_queries = [
        "What is the Transformer architecture?",
        "How does multi-head attention work?",
        "What optimizer was used in training?",
        "How is BERT different from GPT?",
        "What are positional encodings?",
        "How many encoder layers does BERT have?",
    ]
    for sq in sample_queries:
        if st.button(sq, key=f"sample_{sq[:20]}", use_container_width=True):
            st.session_state["prefill_query"] = sq


# ─── Main Panel ──────────────────────────────────────────────────────────────
main_col, history_col = st.columns([3, 1])

with main_col:
    # ── Query Input ──────────────────────────────────────────────────────────
    prefill = st.session_state.pop("prefill_query", "")
    query = st.text_input(
        "Enter your research query",
        value=prefill,
        placeholder="e.g. How does scaled dot-product attention work?",
        key="query_input",
    )

    search_btn = st.button("🔍 Search", type="primary", use_container_width=False)

    st.markdown("---")

    # ── Engine not initialized warning ───────────────────────────────────────
    if st.session_state.engine is None:
        st.info(
            "**Engine not initialized.** Click **🚀 Initialize Engine** in the sidebar to download "
            "the research papers, build the vector store, and load all models. "
            "First run may take 2–3 minutes."
        )

    # ── Run Search ───────────────────────────────────────────────────────────
    elif search_btn or (query and query != st.session_state.get("last_query", "")):
        if query.strip():
            st.session_state["last_query"] = query

            with st.spinner("Searching across research papers..."):
                start_time = time.time()
                try:
                    results = st.session_state.engine.search(query)
                    elapsed = time.time() - start_time
                    st.session_state.total_queries += 1
                    st.session_state.query_history.insert(0, query)
                    if len(st.session_state.query_history) > 10:
                        st.session_state.query_history.pop()

                except ResearchEngineError as e:
                    st.error(
                        f"**Search failed at stage:** {e.stage.value}\n\n{e.message}"
                    )
                    results = []
                except Exception as e:
                    st.error(f"**Unexpected error during search:** {e}")
                    results = []

            if results:
                st.markdown(
                    f"**{len(results)} results** for *\"{query}\"* — retrieved in {elapsed:.2f}s"
                )
                st.markdown("")

                for res in results:
                    score_color = "badge-score" if res.score > 0 else ""
                    score_label = f"{res.score:.2f}" if res.score != 0 else "hybrid"
                    st.markdown(
                        f"""
                        <div class="result-card rank-{res.rank}">
                            <div class="result-meta">
                                <span class="badge">#{res.rank}</span>
                                <span class="badge">{res.topic}</span>
                                <span class="badge">📄 {res.source} · Page {res.page}</span>
                                <span class="badge {score_color}">Score: {score_label}</span>
                            </div>
                            <div class="result-content">{res.content}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            elif query.strip():
                st.warning("No results found. Try rephrasing your query or using different keywords.")

        else:
            st.warning("Please enter a query before searching.")

    elif st.session_state.engine is not None and not query:
        st.markdown("**Engine is ready.** Type a query above and click Search.")


# ─── Query History Panel ─────────────────────────────────────────────────────
with history_col:
    st.markdown("### 🕐 Recent Queries")
    if st.session_state.query_history:
        for i, q in enumerate(st.session_state.query_history[:8]):
            st.markdown(
                f'<div style="background:#F4F6FA;border-radius:6px;padding:0.5rem 0.7rem;'
                f'margin-bottom:0.4rem;font-size:0.82rem;color:#2D3748;">'
                f'<b>{i+1}.</b> {q}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div style="color:#9CA3AF;font-size:0.82rem;">No queries yet.</div>',
            unsafe_allow_html=True,
        )
