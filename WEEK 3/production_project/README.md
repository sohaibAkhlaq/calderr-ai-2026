# 🔬 Real-Time Research Engine
## Week 3 Production Project — Day 7 (Option B)

---

## 📌 Why This Project?

I chose **Option B: Real-Time Research Engine** for the Day 7 Production Project because it is the only option that brings together **every concept learned across all 5 days of Week 3** and packages it into a real web application a real user can interact with:

| Week 3 Day | Concept Learned | Used in This Project |
|---|---|---|
| Day 1 (Monday) | Sentence-Transformer Embeddings | `HuggingFaceEmbeddings(all-MiniLM-L6-v2)` in `engine.py` |
| Day 2 (Tuesday) | FAISS, Vector Storage, Document Chunking | `RecursiveCharacterTextSplitter` + FAISS persistence in `engine.py` |
| Day 3 (Wednesday) | Naive RAG Pipeline (load→split→embed→store→retrieve) | The 7-step sequential pipeline is the backbone of `engine.py` |
| Day 4 (Thursday) | Hybrid BM25 + Semantic Search, Cross-Encoder Re-ranking | `EnsembleRetriever` (40% BM25, 60% Semantic) + `CrossEncoder` in `engine.py` |
| Day 5 (Friday) | RAG Evaluation Metrics | `test_suite.py` evaluates Relevancy and Precision on 10 real queries |

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                     │
│                        app.py                            │
│  ┌──────────────┐  ┌──────────────────────────────────┐  │
│  │   Sidebar    │  │         Main Panel               │  │
│  │ - Initialize │  │  - Query Input                   │  │
│  │ - Status     │  │  - Result Cards                  │  │
│  │ - Error Flow │  │  - Metadata Badges               │  │
│  │ - Samples    │  │  - Query History                 │  │
│  └──────┬───────┘  └──────────────┬───────────────────┘  │
└─────────┼────────────────────────┼──────────────────────┘
          │ engine.initialize()    │ engine.search(query)
          ▼                        ▼
┌──────────────────────────────────────────────────────────┐
│                 RESEARCH ENGINE BACKEND                  │
│                       engine.py                          │
│                                                          │
│  Step 1: _download_pdfs()    ─── SSL-safe urllib         │
│  Step 2: _load_documents()   ─── PyPDFLoader             │
│  Step 3: _split_documents()  ─── RecursiveTextSplitter   │
│  Step 4: _create_embeddings()─── all-MiniLM-L6-v2        │
│  Step 5: _create_vector_store()─ FAISS (persistent)      │
│  Step 6: _create_retriever() ─── BM25 + FAISS Ensemble   │
│  Step 7: _load_reranker()    ─── ms-marco CrossEncoder    │
│                                                          │
│   ┌───────────────────────────────────────────────────┐  │
│   │  search(query) → retrieve → rerank → SearchResult │  │
│   └───────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## 🛡️ Error Handling & Fault Tolerance

A production pipeline must never silently fail. Every step has an explicit validation, and if it fails, a `ResearchEngineError` is raised with the **stage name** and a **human-readable recovery message** — the Streamlit UI catches this and displays it to the user without crashing.

### Complete Failure Flow:

```
Step 1 — PDF Download
   ├── If: Network down / bad URL
   └── Then: ResearchEngineError(DOWNLOAD) raised → Pipeline ABORTS
             Streamlit shows: "Download failed, check your internet."

Step 2 — Document Loading  
   ├── If: PDF missing on disk / corrupted / image-only PDF
   └── Then: ResearchEngineError(LOAD) raised → Pipeline ABORTS
             Streamlit shows: "PDF could not be parsed."

Step 3 — Text Splitting
   ├── If: 0 chunks produced (e.g. blank pages)
   └── Then: ResearchEngineError(SPLIT) raised → Pipeline ABORTS
             Streamlit shows: "Splitting produced 0 chunks."

Step 4 — Embedding Model
   ├── If: HuggingFace Hub offline / model corrupted
   └── Then: ResearchEngineError(EMBED) raised → Pipeline ABORTS
             Streamlit shows: "Could not load embedding model."

Step 5 — FAISS Vector Store
   ├── If: Disk permission denied / out of disk space
   └── Then: ResearchEngineError(STORE) raised → Pipeline ABORTS
             Streamlit shows: "Vector store initialization failed."

Step 6 — Retriever Assembly
   ├── If: BM25 / FAISS retriever fails to assemble
   └── Then: ResearchEngineError(RETRIEVE) raised → Pipeline ABORTS
             Streamlit shows: "Retriever assembly failed."

Step 7 — Cross-Encoder Re-ranking
   ├── If: Re-ranker model unavailable
   └── Then: ⚠️ GRACEFUL FALLBACK — uses hybrid ranking order
             (Re-ranking is non-critical, so we degrade gracefully)
```

### Error Code Flow in `engine.py`:
```python
try:
    results = engine.search(query)
except ResearchEngineError as e:
    # Stage-specific, clean error — show to user
    st.error(f"Failed at: {e.stage.value}\n{e.message}")
except Exception as e:
    # Unexpected runtime error — show stack trace
    st.error(f"Unexpected error: {e}")
```

---

## 🚀 How to Run

### Prerequisites
Ensure your `calderr-env` virtual environment is active.

```powershell
cd C:\Users\USER\Desktop\calderr-ai-2026
.\calderr-env\Scripts\Activate.ps1
```

### Install Dependencies (first time only)
```powershell
pip install -r "WEEK 3\production_project\requirements.txt"
```

### Launch the Streamlit App
```powershell
cd "WEEK 3\production_project"
streamlit run app.py
```
The browser will automatically open at `http://localhost:8501`.

### First-Run Steps (inside the app):
1. Click **🚀 Initialize Engine** in the left sidebar.
2. Wait ~2–3 minutes (downloads PDFs + models on first run).
3. Once **Engine Status** shows ⬤ Ready, type a query and click **🔍 Search**.

---

## 🧪 How to Test

Run the automated test suite to validate the full backend pipeline without the UI:

```powershell
cd C:\Users\USER\Desktop\calderr-ai-2026
.\calderr-env\Scripts\python "WEEK 3\production_project\test_suite.py"
```

This runs:
- **Phase 1:** Engine initialization (all 7 pipeline steps)
- **Phase 2:** Vector store chunk count validation
- **Phase 3:** 10 evaluation queries with keyword-based relevancy scoring

Results are saved to `test_results.json`. Exit code `0` = all pass.

---

## 📁 Project Structure

```
WEEK 3/production_project/
├── app.py              # Streamlit UI (Light Theme, professional layout)
├── engine.py           # Core RAG pipeline with strict error boundaries
├── test_suite.py       # Automated health check and evaluation script
├── requirements.txt    # All Python dependencies
├── README.md           # This file
├── .streamlit/
│   └── config.toml     # Light theme + server config
├── docs/               # Auto-created: downloaded PDF files
│   ├── attention_is_all_you_need.pdf
│   └── bert_pretraining.pdf
├── faiss_db/           # Auto-created: persistent FAISS vector store
└── test_results.json   # Auto-created: test results after running test_suite.py
```

---

## 📦 Key Dependencies

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | ≥1.28 | Web UI framework |
| `langchain` | ≥0.2 | RAG orchestration |
| `sentence-transformers` | ≥2.7 | Embedding model |
| `faiss-cpu` | ≥1.7.4 | Persistent vector store & index |
| `rank_bm25` | ≥0.2.2 | BM25 keyword retrieval |
| `pypdf` | ≥3.0 | PDF text extraction |

---

## 🎓 Concepts Applied (Week 3 Deep Dive)

### Embeddings (Day 1)
**Definition:** Converting text into high-dimensional numerical vectors that capture semantic meaning. Similar sentences have vectors that are geometrically close to each other in the embedding space.
- **Used in:** `_create_embeddings()` in `engine.py` using `all-MiniLM-L6-v2`

### Vector Database (Day 2)
**Definition:** A specialized database optimized for storing and querying embedding vectors. Unlike traditional databases (SQL), vector DBs find the "nearest neighbor" vectors to a query vector.
- **Used in:** `_create_vector_store()` using FAISS with local persistence

### RAG Pipeline (Day 3)
**Definition:** Retrieval-Augmented Generation. Instead of asking an LLM to answer from memory, we first retrieve relevant documents from a knowledge base and feed them as context.
- **Used in:** The 7-step sequential pipeline in `ResearchEngine.initialize()`

### Hybrid Search (Day 4)
**Definition:** Combining keyword-based search (BM25) with semantic vector search. BM25 finds exact word matches; semantic search finds conceptually similar content. Together they are more robust than either alone.
- **Used in:** `_create_retriever()` with `EnsembleRetriever(weights=[0.4, 0.6])`

### Cross-Encoder Re-ranking (Day 4)
**Definition:** A model that jointly scores a (query, document) pair to produce a fine-grained relevancy score. Unlike bi-encoder retrieval (fast but less accurate), cross-encoders see both texts together and are far more accurate.
- **Used in:** `_load_reranker()` using `ms-marco-MiniLM-L-6-v2`

### Evaluation Metrics (Day 5)
**Definition:** Measuring RAG pipeline quality systematically using Context Precision (are retrieved chunks relevant?) and Answer Relevancy (does the top result answer the query?).
- **Used in:** `test_suite.py` keyword-based relevancy scoring across 10 queries
