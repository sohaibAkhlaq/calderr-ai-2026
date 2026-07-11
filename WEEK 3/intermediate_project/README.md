# Week 3 Intermediate Project — Hybrid Search Engine (Option C)

## 📌 Project Choice: Option C — Hybrid Search Engine

I chose **Option C: Hybrid Search Engine** because it is the only intermediate project that applies **ALL 5 days** of Week 3 learning. Options A and B only cover Days 1-3, but Option C requires BM25 keyword search, cross-encoder re-ranking, AND evaluation metrics — making it a complete consolidation of the entire week.

---

## 🛡️ Pipeline Error Handling & Fault Tolerance (Production Ready)

Per enterprise requirements, this pipeline has been heavily refactored to include strict error boundaries. If a critical step fails, the pipeline intentionally aborts with a clean `PipelineError` rather than silently passing empty context and causing LLM hallucinations down the line.

### Expected Failure Flows:
1. **Missing or Corrupted PDF (Step 1 & 2):** 
   - *Scenario:* The `attention_is_all_you_need.pdf` file fails to download or is corrupted.
   - *Action:* The pipeline catches the HTTP/IO error and immediately aborts. It does not fall back to mock data.
2. **Chunking Failure (Step 3):**
   - *Scenario:* The PDF is loaded, but 0 chunks are produced (e.g. an image-only PDF with no text).
   - *Action:* The pipeline detects 0 chunks and raises a `PipelineError`, preventing an empty Vector DB initialization.
3. **Embedding Model Failure (Step 4):**
   - *Scenario:* HuggingFace Hub is down or offline.
   - *Action:* The exception is caught, and the pipeline halts safely.
4. **Vector Store Failure (Step 5):**
   - *Scenario:* Read/Write permission error on the disk.
   - *Action:* Caught and aborted safely.

All unexpected runtime errors are routed through a global exception handler that gracefully shuts down the program and prints a formatted stack trace.

---

## 🧠 Concepts Applied & Where We Learned Them

### Day 1 (Monday) — Embeddings Deep Dive
- **Concept:** Sentence-Transformer Embeddings (`all-MiniLM-L6-v2`)
- **How it's used in this project:** Every document chunk is converted into a 384-dimensional embedding vector.
- **Learned in:** `lab3_1.py`

### Day 2 (Tuesday) — Vector Databases & Document Processing
- **Concept:** ChromaDB Storage + Document Chunking
- **How it's used in this project:** Documents are split into 512-character chunks with 50-character overlap, then stored in ChromaDB.
- **Learned in:** `lab3_2.py`

### Day 3 (Wednesday) — Naive RAG Architecture
- **Concept:** Full RAG Pipeline (Load → Split → Embed → Store → Retrieve → Generate)
- **Learned in:** `lab3_3_naive_rag.py`

### Day 4 (Thursday) — Advanced Retrieval
- **Concept:** BM25 Hybrid Search + Cross-Encoder Re-ranking
- **How it's used in this project:** We use LangChain's `EnsembleRetriever` to combine BM25 with semantic search. Results are then re-ranked using a Cross-Encoder (`ms-marco-MiniLM-L-6-v2`).
- **Learned in:** `lab3_4_advanced_retrieval.py`

### Day 5 (Friday) — RAG Evaluation & Assessment
- **Concept:** Context Precision, Answer Relevancy, Faithfulness Metrics
- **How it's used in this project:** We evaluate the hybrid search engine on **10 real questions about the Attention Is All You Need paper**.
- **Learned in:** `lab3_5_rag_evaluation.py`

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────────────────┐
│  BM25 Keyword Retriever │──── weight: 0.4
│  (exact word matching)  │
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│   EnsembleRetriever     │──── Merges & deduplicates
│   (Hybrid Fusion)       │
└─────────┬───────────────┘
          │
          ▲
┌─────────┴───────────────┐
│  Semantic Retriever     │──── weight: 0.6
│  (ChromaDB + MiniLM)    │
└─────────────────────────┘
          │
          ▼
┌─────────────────────────┐
│  Cross-Encoder Reranker │──── ms-marco-MiniLM-L-6-v2
│  (deep relevancy score) │
└─────────┬───────────────┘
          │
          ▼
    Top 3 Results
```

---

## 🚀 How to Run

### Prerequisites
Make sure you have the `calderr-env` virtual environment activated.

### Run the Full Pipeline (Evaluation + Interactive Mode)
```powershell
cd C:\Users\USER\Desktop\calderr-ai-2026
.\calderr-env\Scripts\Activate.ps1
python "WEEK 3\intermediate_project\hybrid_search_engine.py"
```

### Run Evaluation Only (No Interactive Mode)
```powershell
python "WEEK 3\intermediate_project\hybrid_search_engine.py" --no-interactive
```

### What Happens When You Run It
1. Downloads **"Attention Is All You Need" (Arxiv PDF)**
2. Splits the research paper into chunks
3. Embeds chunks and stores in ChromaDB
4. Builds a hybrid retriever (BM25 + Semantic)
5. Evaluates 10 hard questions about the paper's architecture
6. Opens an interactive CLI where you can type your own queries
