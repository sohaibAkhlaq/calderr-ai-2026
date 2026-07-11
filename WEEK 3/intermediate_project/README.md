# Week 3 Intermediate Project — Hybrid Search Engine (Option C)

## 📌 Project Choice: Option C — Hybrid Search Engine

I chose **Option C: Hybrid Search Engine** because it is the only intermediate project that applies **ALL 5 days** of Week 3 learning. Options A and B only cover Days 1-3, but Option C requires BM25 keyword search, cross-encoder re-ranking, AND evaluation metrics — making it a complete consolidation of the entire week.

---

## 🧠 Concepts Applied & Where We Learned Them

### Day 1 (Monday) — Embeddings Deep Dive
- **Concept:** Sentence-Transformer Embeddings (`all-MiniLM-L6-v2`)
- **Definition:** Dense vector representations that capture the semantic meaning of text. Similar meanings map to nearby points in vector space.
- **How it's used in this project:** Every document chunk is converted into a 384-dimensional embedding vector using `sentence-transformers`. These vectors power the semantic half of our hybrid search.
- **Learned in:** `lab3_1.py` — Semantic Search CLI where we embedded 100 Wikipedia sentences and compared models.

### Day 2 (Tuesday) — Vector Databases & Document Processing
- **Concept:** ChromaDB Storage + Document Chunking with Metadata
- **Definition:** ChromaDB is an open-source vector database that stores embeddings alongside original text and metadata. Chunking splits large documents into smaller pieces so embedding models can process them.
- **How it's used in this project:** Documents are split into 512-character chunks with 50-character overlap using `RecursiveCharacterTextSplitter`, then stored in ChromaDB with topic metadata for filtered queries.
- **Learned in:** `lab3_2.py` — We built a document ingestion pipeline for 50 PDF pages with metadata filtering.

### Day 3 (Wednesday) — Naive RAG Architecture
- **Concept:** Full RAG Pipeline (Load → Split → Embed → Store → Retrieve → Generate)
- **Definition:** RAG (Retrieval-Augmented Generation) retrieves relevant documents from a knowledge base and uses them as context for generating accurate responses.
- **How it's used in this project:** The entire pipeline follows the RAG architecture: we load documents, split them, embed them, store in ChromaDB, retrieve on query, and present results.
- **Learned in:** `lab3_3_naive_rag.py` — We built a naive RAG pipeline and tuned chunk sizes (256 vs 1024).

### Day 4 (Thursday) — Advanced Retrieval
- **Concept:** BM25 Hybrid Search + Cross-Encoder Re-ranking
- **Definition:** BM25 is a keyword-based ranking algorithm. Hybrid search combines BM25 with semantic search. Cross-Encoders take both query and document simultaneously to produce a deep relevancy score.
- **How it's used in this project:** We use LangChain's `EnsembleRetriever` to combine BM25 (40% weight) with semantic search (60% weight). Results are then re-ranked using a Cross-Encoder (`ms-marco-MiniLM-L-6-v2`).
- **Learned in:** `lab3_4_advanced_retrieval.py` — We implemented hybrid search, re-ranking, and multi-query retrieval.

### Day 5 (Friday) — RAG Evaluation & Assessment
- **Concept:** Context Precision, Answer Relevancy, Faithfulness Metrics
- **Definition:** These RAGAS-style metrics measure how relevant the retrieved context is, how well the answer matches ground truth, and whether the answer can be traced back to retrieved documents.
- **How it's used in this project:** We evaluate the hybrid search engine on **30 queries** with expected answers. Each query is scored on all 3 metrics, and an aggregate report with pass/fail rates is generated.
- **Learned in:** `lab3_5_rag_evaluation.py` — We built a manual RAGAS-style evaluation system.

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
Make sure you have the `calderr-env` virtual environment activated with all Week 3 dependencies.

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
1. Downloads a sample PDF (or uses built-in knowledge base of 30 documents)
2. Splits documents into 512-character chunks with 50-char overlap
3. Embeds chunks using `all-MiniLM-L6-v2`
4. Stores embeddings in ChromaDB
5. Builds a hybrid retriever (BM25 + Semantic)
6. Loads a Cross-Encoder re-ranker
7. Runs evaluation on **30 queries** and prints a scored report
8. Opens an interactive CLI where you can type your own queries

### Adding Your Own PDFs
Drop any `.pdf` file into the `WEEK 3/intermediate_project/docs/` folder and re-run. The engine will automatically ingest all PDFs it finds.

---

## 📊 Evaluation

The engine evaluates itself on 30 queries spanning 6 topic categories:
- **Python** (5 queries)
- **Machine Learning** (5 queries)
- **NLP** (5 queries)
- **Databases** (5 queries)
- **DevOps** (5 queries)
- **Web Development** (5 queries)

Each query is scored on:
| Metric | Description |
|---|---|
| Context Precision | % of retrieved docs matching the expected topic |
| Answer Relevancy | % of expected answer words found in top result |
| Faithfulness | Whether the expected answer is fully present in context |

Results are saved to `evaluation_results.json` for review.
