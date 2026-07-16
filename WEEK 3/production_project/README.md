# Week 3 Production Project — RAG Evaluation Benchmark (Option C)

## 📌 Project Choice: Option C — RAG Evaluation Benchmark

I chose **Option C: RAG Evaluation Benchmark** because it is the only production project that applies **ALL 5 days** of Week 3 learning into a reusable evaluation framework. Options A and B only build single RAG pipelines, but Option C requires systematic testing across **6 configurations**, statistical comparison, and publishable report generation — making it a genuine benchmarking tool for future projects.

---

## 🛡️ Pipeline Error Handling & Fault Tolerance (Production Ready)

Per enterprise requirements, this pipeline has been heavily refactored to include strict error boundaries. If a critical step fails, the pipeline intentionally aborts with a clean `PipelineError` rather than silently passing empty context and causing LLM hallucinations down the line.

### Expected Failure Flows:
1. **Missing or Corrupted PDF (Step 1 & 2):**
   - *Scenario:* The `attention_is_all_you_need.pdf` file fails to download or is corrupted.
   - *Action:* The pipeline catches the HTTP/IO error and immediately aborts with a `PipelineError`.
2. **Chunking Failure (Step 3):**
   - *Scenario:* The PDF is loaded, but 0 chunks are produced (e.g. an image-only PDF with no text).
   - *Action:* The pipeline detects 0 chunks and raises a `PipelineError`, preventing empty Vector DB initialization.
3. **Embedding Model Failure (Step 4):**
   - *Scenario:* HuggingFace Hub is down or the model name is invalid.
   - *Action:* The exception is caught, and the pipeline halts safely.
4. **Vector Store Failure (Step 5):**
   - *Scenario:* Read/Write permission error on disk or ChromaDB failure.
   - *Action:* Caught and aborted safely.
5. **Unknown Retrieval Strategy:**
   - *Scenario:* A config has an unrecognized `retrieval_strategy` value.
   - *Action:* A `PipelineError` is raised with a descriptive message.
6. **Per-Query Failures (Graceful Degradation):**
   - *Scenario:* A single evaluation query fails (e.g. LLM timeout).
   - *Action:* The error is logged, the query is skipped, and evaluation continues. The final `success_rate` metric reflects the proportion of successful queries.

All unexpected runtime errors are routed through a global exception handler that gracefully shuts down the program and prints a formatted stack trace.

---

## 🧠 Concepts Applied & Where We Learned Them

### Day 1 (Monday) — Embeddings Deep Dive
- **Concept:** Sentence-Transformer Embeddings (`all-MiniLM-L6-v2`)
- **How it's used in this project:** Every document chunk is converted into a 384-dimensional embedding vector for semantic retrieval.
- **Learned in:** `lab3_1.py`

### Day 2 (Tuesday) — Vector Databases & Document Processing
- **Concept:** ChromaDB Storage + Document Chunking
- **How it's used in this project:** Tested with multiple chunk sizes (512/50, 1024/100) and stored in ChromaDB with collection-per-config isolation.
- **Learned in:** `lab3_2.py`

### Day 3 (Wednesday) — Naive RAG Architecture
- **Concept:** Full RAG Pipeline (Load → Split → Embed → Store → Retrieve → Generate)
- **How it's used in this project:** Each `RAGConfig` builds a complete pipeline from PDF download through retrieval and evaluation.
- **Learned in:** `lab3_3_naive_rag.py`

### Day 4 (Thursday) — Advanced Retrieval
- **Concept:** BM25 Hybrid Search + Cross-Encoder Re-ranking
- **How it's used in this project:** The `hybrid` and `hybrid_rerank` strategies combine BM25 keyword search (weight 0.4) with semantic retrieval (weight 0.6) via `EnsembleRetriever`, with optional cross-encoder re-ranking using `ms-marco-MiniLM-L-6-v2`.
- **Learned in:** `lab3_4_advanced_retrieval.py`

### Day 5 (Friday) — RAG Evaluation & Assessment
- **Concept:** Context Precision, Answer Relevancy, Faithfulness Metrics
- **How it's used in this project:** All 6 configurations are evaluated on **10 curated questions** about the Attention Is All You Need paper, scoring each metric per query and computing statistical aggregates.
- **Learned in:** `lab3_5_rag_evaluation.py`

---

## ⚙️ System Design Principles Used

The following design principles guided the architecture of this evaluation framework:

### 1. Modular Monolith — Separation of Concerns
Each pipeline stage is isolated in its own class (`RAGPipelineBuilder`, `RAGEvaluator`, `ReportGenerator`). This allows independent testing, swapping components, and extending without modifying existing code.

### 2. Configuration-Driven Design
All RAG parameters are captured in the `RAGConfig` dataclass. Adding a new configuration means instantiating one object — no boilerplate, no code duplication. The `CONFIGS` list is the single source of truth for all benchmarked setups.

### 3. Fail-Fast with PipelineError
If a critical dependency (PDF, embedding model, vector store) fails, the pipeline raises a `PipelineError` immediately — it never silently falls back to empty context, preventing downstream LLM hallucinations.

### 4. Graceful Degradation (Per-Query)
Individual query failures are caught, logged, and skipped without aborting the entire evaluation. The `success_rate` metric transparently reports how many queries actually succeeded.

### 5. Strategy Pattern for Retrieval
The three retrieval strategies (`semantic`, `hybrid`, `hybrid_rerank`) are selected via a string flag in the config. New strategies can be added by extending the `if/elif` block in `build_pipeline()` without touching the evaluator or report generator.

### 6. Dual-Mode Interface (CLI + UI)
The same evaluation engine runs in both headless CLI mode and Streamlit UI. The entry point (`--streamlit` flag) selects the interface, keeping business logic completely reusable.

---

## 🏗️ Architecture

```
Config YAML / UI Input
         │
         ▼
┌─────────────────────────┐
│   RAGPipelineBuilder    │── Builds pipeline per config
│   (PDF → Chunk → Embed) │
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│  Sequential Evaluation  │── 6 configs × 10 queries
│  Runner (RAGEvaluator)  │   Metrics per query
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│   Custom Metrics        │── Context Precision
│   (Local computation)   │   Answer Relevancy
│                         │   Faithfulness
│                         │   Response Time
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│  Statistical Analyzer   │── Sorts & ranks configs
│  + Report Generator     │   JSON report export
│                         │   PDF report export
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│  Streamlit Dashboard    │── Leaderboard table
│  or CLI Output          │   Plotly bar charts
│                         │   Metric cards
│                         │   JSON/PDF download
└─────────────────────────┘
```

### Retrieval Strategies Evaluated

| Strategy | Description | Components |
|----------|-------------|------------|
| `semantic` | Pure dense retrieval | ChromaDB + MiniLM embeddings |
| `hybrid` | Sparse + dense fusion | BM25 (0.4) + ChromaDB (0.6) via EnsembleRetriever |
| `hybrid_rerank` | Hybrid + cross-encoder re-ranking | BM25 + ChromaDB + CrossEncoder (`ms-marco-MiniLM-L-6-v2`) |

---

## 🚀 How to Run

### Prerequisites
Make sure you have the `calderr-env` virtual environment activated and a `.env` file with your `GROQ_API_KEY` (or pass it via the UI/CLI).

### Install Dependencies
```powershell
pip install -r "WEEK 3/production_project/requirements_production.txt"
```

### Run the Streamlit Dashboard (Interactive UI)
```powershell
cd C:\Users\USER\Desktop\calderr-ai-2026
.\calderr-env\Scripts\Activate.ps1
streamlit run "WEEK 3/production_project/project3_p_c_rag_benchmark.py" -- --streamlit
```

### Run the CLI Benchmark (No UI)
```powershell
python "WEEK 3/production_project/project3_p_c_rag_benchmark.py"
```

### What Happens When You Run It
1. Downloads **"Attention Is All You Need" (Arxiv PDF)**
2. Processes the paper through **6 RAG configurations** with varying chunk sizes, retrievers, and `k` values
3. Evaluates each config against **10 test queries** about the paper's architecture
4. Computes **Context Precision, Answer Relevancy, Faithfulness, and Response Time**
5. Displays a ranked **leaderboard** with interactive Plotly charts (Streamlit) or a CLI table
6. Exports reports in **JSON** and **PDF** formats for further analysis

### Configuration Matrix

| Config Name | Chunk Size | Overlap | Strategy | k |
|-------------|-----------|---------|----------|---|
| Semantic_512_3 | 512 | 50 | semantic | 3 |
| Semantic_512_5 | 512 | 50 | semantic | 5 |
| Hybrid_512_3 | 512 | 50 | hybrid | 3 |
| Hybrid_512_5 | 512 | 50 | hybrid | 5 |
| HybridRerank_512_3 | 512 | 50 | hybrid_rerank | 3 |
| HybridRerank_1024_3 | 1024 | 100 | hybrid_rerank | 3 |

---

## 📊 Output & Results

- **Streamlit Dashboard:** Dark-themed glassmorphic UI with metric cards, leaderboard table, and Plotly bar charts
- **CLI Mode:** Color-coded terminal output with per-config metrics
- **JSON Export:** Full timestamped report with all configuration details, downloadable via button (Streamlit) or saved to `benchmark_results.json` (CLI)
- **PDF Export:** Publishable-quality report with embedded charts, leaderboard table, and per-configuration detail section — ready for sharing

---

## 🔧 Customization

To add new configurations, edit the `CONFIGS` list in `project3_p_c_rag_benchmark.py`:

```python
RAGConfig(
    name="MyCustomConfig",
    chunk_size=768,
    chunk_overlap=80,
    embedding_model="all-MiniLM-L6-v2",
    retrieval_strategy="hybrid_rerank",
    k=4
)
```

To add new test queries, extend the `TEST_QUERIES` list:

```python
{"query": "Your question here?", "expected": "expected keyword"}
```
