# Week 3: Embeddings, RAG & Vector Databases

**Goal:** Build systems that know things — retrieval-augmented generation at scale.
**Total Commitment:** ~20 hours (Distributed over 7 days for a balanced schedule)
**Primary Stack:** Python, LangChain, ChromaDB, FAISS, sentence-transformers, RAGAS

---

## 📅 Day 1: Monday - Embeddings Deep Dive
**Focus:** Understanding vector spaces, cosine similarity, and semantic meaning.

*   **Core Learning:**
    *   Study embedding theory: semantic similarity, cosine distance.
    *   Read: *Retrieval-Augmented Generation for Knowledge-Intensive NLP (Lewis et al., 2020)*.
*   **Applied Practice & Lab:**
    *   **Lab 3.1 — Semantic Search CLI:**
        *   Install `sentence-transformers`.
        *   Embed 100 Wikipedia sentences.
        *   Build a CLI tool that takes a query, embeds it, and returns the most semantically similar sentences.
        *   Compare results of different models (`all-MiniLM-L6-v2` vs `bge-small-en`).
        *   Visualize embeddings with 2D PCA.

---

## 📅 Day 2: Tuesday - Vector Databases & Document Processing
**Focus:** Storing and retrieving vectors efficiently, and preparing documents.

*   **Core Learning:**
    *   Vector Databases: ChromaDB (local), FAISS (in-process).
    *   Study tradeoffs: in-memory vs persistent vs server.
    *   Document Processing: Text splitting strategies, metadata extraction, document loaders.
*   **Applied Practice:**
    *   Complete ChromaDB tutorial: create collection, add docs, query.
    *   FAISS intro: `IndexFlatL2` vs `IndexIVFFlat`.
    *   Build a Document Ingestion Pipeline for 50 PDF pages. Store in ChromaDB with metadata (source, page, date). Query with filters.

---

## 📅 Day 3: Wednesday - Naive RAG Architecture
**Focus:** Building a complete basic RAG pipeline.

*   **Core Learning:**
    *   Study RAG Architecture: Ingestion pipeline vs query pipeline.
    *   Read: *LangChain RAG Tutorial (v0.3)*.
*   **Applied Practice & Lab:**
    *   **Lab 3.2 — Naive RAG Pipeline:**
        *   Build naive RAG with LangChain: `load → split → embed → store → retrieve → generate` over 50 pages of PDF content.
        *   Tune chunk size across 256, 512, and 1024 tokens.
        *   Evaluate retrieval accuracy: create 20 Q&A pairs from documents. Experiment with `k=3` vs `k=10` retrieved chunks and document the impact on answer quality.

---

## 📅 Day 4: Thursday - Advanced Retrieval
**Focus:** Improving retrieval quality with hybrid search and reranking.

*   **Core Learning:**
    *   Study hybrid search: BM25 (keyword) + semantic.
    *   Read: *Advanced RAG: Survey of Techniques (2024)*.
*   **Applied Practice & Lab:**
    *   **Lab 3.3 — Hybrid Retrieval:**
        *   Implement hybrid search combining BM25 keyword search with semantic retrieval using LangChain's `EnsembleRetriever`.
        *   Add cross-encoder re-ranking (e.g., `BAAI/bge-reranker-base`).
        *   Build Multi-query retrieval: Generate 3 query variations per user question, deduplicate, and re-rank. Measure improvement over naive RAG.

---

## 📅 Day 5: Friday - RAG Evaluation & Weekly Assessment
**Focus:** Measuring RAG performance systematically.

*   **Core Learning:**
    *   Study RAGAS metrics: faithfulness, answer relevancy, context precision, context recall.
*   **Applied Practice & Assessment:**
    *   Install RAGAS and build an evaluation dataset.
    *   Run faithfulness, answer relevancy, and context precision metrics on your RAG system from Thursday.
    *   **Complete Weekly Assessment:** Answer conceptual, technical, and design questions (e.g., embedding concepts, chunk size tradeoffs, cross-encoder purpose, multi-tenant design).

---

## 📅 Day 6: Saturday - Intermediate Project
**Focus:** Consolidate learnings by building an intermediate application.

*   **Task:** Choose exactly ONE Intermediate project and complete it. Push to GitHub.
    *   **Option A: Personal Knowledge Base** (CLI tool ingesting 20+ docs, ChromaDB, 15 Q&A examples)
    *   **Option B: Product Manual Assistant** (Streamlit app over open-source manual, FAISS, 20 test questions, citations)
    *   **Option C: Hybrid Search Engine** (CLI search tool over news corpus, BM25 + Vector Index + Re-ranker, evaluation on 30 queries)
*   **Deliverables:** Code, README with architecture, and specific project requirements.

---

## 📅 Day 7: Sunday - Production Project & Standup Prep
**Focus:** Build a robust, scalable system and prepare for presentation.

*   **Task 1: Production Project** (Choose ONE and complete it. Push to GitHub)
    *   **Option A: Enterprise Document Intelligence Platform** (FastAPI, Background Worker, Multi-tenant ChromaDB, Streamlit Admin, Docker Compose)
    *   **Option B: Real-Time Research Engine** (Knowledge Router, Web Search + Local Knowledge, Citation Generation, FastAPI + Streamlit)
    *   **Option C: RAG Evaluation Benchmark** (Evaluation framework, Statistical Analyzer, HTML Reports, GitHub Actions CI)
*   **Task 2: Standup Preparation**
    *   Prepare 2-minute live demo of your RAG system with at least 3 real queries.
    *   Prepare technical question answer (one concept that changed how you think about RAG).
    *   Draw full RAG pipeline architecture (ingestion and query paths).
    *   Review RAGAS evaluation results (what scored well/poorly).
    *   Document blockers (one challenge faced and the solution).
*   **Final Verification:** Review the "Week 3 Completion Checklist" to ensure all requirements are met.
