# CalderR AI Internship

**Project Location:** `Desktop/calderr-ai-2026`  
**Author:** Sohaib Akhlaq  
**Status:** Week 6 Fully Complete (Weeks 1 through 6 Completed)
 
---

## Executive Overview

This repository documents the complete setup, learning progress, and hands-on implementations completed during the CalderR AI internship (2026). It covers environment configuration, foundational AI concepts, agentic systems, LangChain workflows, prompt engineering experiments, structured outputs, tool calling, external API integration, RAG architectures, LangGraph agent workflows, multi-agent teams, persistent memory architectures, knowledge graphs, and fully deployed production AI platforms.

---

## Project Goals

- Work with large language models via APIs (Groq, HuggingFace, sentence-transformers)
- Master agentic AI design patterns (ReAct, Chain-of-Thought, Supervisor, Peer-to-Peer, Hierarchical Teams)
- Implement advanced retrieval architectures (Vector RAG, BM25 Hybrid Search, Re-ranking, GraphRAG)
- Construct persistent multi-layer agent memory (Working, Episodic, Semantic, Procedural)
- Build knowledge graphs with NetworkX and query them using natural language traversals
- Create reusable, production-ready documentation and deploy full-stack applications (Streamlit, FastAPI, Docker Compose)

---

## Quick Start — Running Week 6 Projects

```powershell
# Activate the environment
cd C:\Users\USER\Desktop\calderr-ai-2026
.\calderr-env\Scripts\Activate.ps1
```

### 1️⃣ Week 6 Intermediate Project (Project 6-I-A: Long-Term Personal Research Assistant)
```powershell
streamlit run "WEEK 6\intermediate_project\app.py"
```
- Open `http://localhost:8501` in your browser.
- Go to the **🧪 Automated Test Suite** tab and press **🚀 Run All Tests** (16/16 Passed, 100% Pass Rate).

### 2️⃣ Week 6 Production Project (Project 6-P-A: Enterprise AI Memory Platform)
```powershell
# Terminal 1: FastAPI REST API Memory Service (Port 8000)
python "WEEK 6\production_project\main.py"

# Terminal 2: Streamlit Observability Admin Dashboard (Port 8501)
streamlit run "WEEK 6\production_project\admin_app.py"

# Terminal 3: External AI Agent Client REST Demo
python "WEEK 6\production_project\client_agent_demo.py"

# Terminal 4: RAGAS Retrieval Quality Benchmark
python "WEEK 6\production_project\eval_retrieval_quality.py"
```

---

## Environment Summary

- **Python:** 3.11.9
- **Virtual environment:** `calderr-env`
- **Git:** Configured & Connected to GitHub (`sohaibAkhlaq/calderr-ai-2026`)

### Installed Libraries

| Category | Packages |
|---|---|
| LLM | LangChain, LangChain-Groq, LangChain-Community, LangGraph, Groq |
| Memory & Graphs | SQLite, Pure-Python Vector Engine, NetworkX, sentence-transformers |
| Multi-Agent | Pydantic v2, TypedDict, asyncio, custom message bus |
| Data | Pandas, NumPy, Plotly, Pyvis |
| Web & API | Streamlit, FastAPI, Uvicorn, HTTPX |
| Terminal | Rich, Typer |
| Testing & DevOps | PyTest, Docker Compose |

---

## Repository Structure

```
calderr-ai-2026/
├── .env                          # API keys (not committed)
├── .env.template                 # Template for API keys
├── requirements.txt              # Full dependencies
├── README.md                     # Master Repository README
│
├── week1/                        # Week 1: AI Fundamentals & Prompt Engineering
│   ├── professional_chatbot.py
│   ├── multi_model_benchmark.py
│   ├── prompt_evaluator.py
│   ├── react_agent.py
│   ├── document_qa_chain.py
│   ├── weekly_assessment.md
│   └── week1day1.txt ... week1day4.txt
│
├── week2/                        # Week 2: Advanced AI Patterns & Tool Integration
│   ├── lab2.1_cot_pipeline.py
│   ├── lab2.1_structured_extractor.py
│   ├── lab2.2_multi_tool_agent.py
│   ├── lab2.3_external_api_tools.py
│   ├── project2_i_c_api_aggregator.py      <- Intermediate Project (CLI)
│   ├── project2_p_c_financial_analysis.py  <- Production Project (Streamlit)
│   └── week2_assessment.md
│
├── WEEK 3/                       # Week 3: Embeddings, RAG & Vector Databases
│   ├── lab3_1.py                 # Semantic Search CLI & PCA
│   ├── lab3_2.py                 # Vector DBs & Chunking
│   ├── lab3_3_naive_rag.py       # Naive RAG Architecture
│   ├── lab3_4_advanced_retrieval.py # Hybrid Search & Re-ranking
│   ├── lab3_5_rag_evaluation.py  # RAG Evaluation Suite
│   ├── intermediate_project/     # Hybrid Search Engine (BM25 + Vector)
│   └── production_project/       # RAG Evaluation Benchmark Dashboard
│
├── Week 4/                       # Week 4: LangGraph & Stateful Agent Workflows
│   ├── lab4.1_document_processing.py
│   ├── lab4.2_self_correcting_loop.py
│   ├── lab4.3_approval_workflow.py
│   ├── lab4.4_production_graph.py
│   └── production_project/       # AI-Powered Hiring Pipeline Platform
│
├── WEEK 5/                       # Week 5: Multi-Agent Systems & Team Architectures
│   ├── lab5.1_typed_message_bus.py        # Pydantic Typed Message Bus Lab
│   ├── lab5.2_supervisor_failure_recovery.py # Supervisor Pattern Lab
│   ├── lab5.3_consensus_engine.py         # Debate & Consensus Engine Lab
│   ├── lab5.3_hierarchical_teams.py       # Hierarchical Teams & Context Isolation
│   ├── WEEK5_ASSESSMENT.md
│   ├── intermediate_project/              # Autonomous Competitive Intelligence Agent
│   └── production_project/                # Autonomous AI Research Lab
│
└── WEEK 6/                       # Week 6: Memory Systems & Knowledge Graphs
    ├── README.md                          # Full Week 6 Detailed Documentation
    ├── WEEK6DAY1.txt ... WEEK6DAY5.txt    # Mon-Fri Daily Learning Concept Journals
    ├── WEEK6_ASSESSMENT.md                # Written Assessment Solutions (All 6 Questions)
    ├── lab6_1_memory_augmented_chatbot.py # Lab 6.1: Cross-Session Recall Chatbot
    ├── lab6_2_knowledge_graph_query_agent.py # Lab 6.2: NetworkX Multi-Hop Query Agent
    ├── lab6_3_graphrag_hybrid_retrieval.py # Lab 6.3: ChromaDB + NetworkX GraphRAG Merger
    ├── intermediate_project/              # Project 6-I-A: Personal Research Assistant (Streamlit)
    └── production_project/                # Project 6-P-A: Enterprise AI Memory Platform (FastAPI + Streamlit)
```

---

## Week 6 — Memory Systems & Knowledge Graphs Highlights

| Project / Deliverable | Type | Features & Status | Key Files |
|---|---|---|---|
| **Lab 6.1** | Lab | Cross-Session Recall Chatbot with SQLite Episodic + Vector Memory | `lab6_1_memory_augmented_chatbot.py` |
| **Lab 6.2** | Lab | NetworkX Knowledge Graph Query Agent with 2-Hop Path Traversals | `lab6_2_knowledge_graph_query_agent.py` |
| **Lab 6.3** | Lab | GraphRAG Hybrid Retrieval combining Vector Search and Knowledge Graphs | `lab6_3_graphrag_hybrid_retrieval.py` |
| **Project 6-I-A** | Intermediate | Long-Term Personal Research Assistant (4-Tab Streamlit UI, 16/16 Tests) | `WEEK 6/intermediate_project/` |
| **Project 6-P-A** | Production | Enterprise AI Memory Platform (FastAPI REST API, 4 Memory Types, Multi-Tenant Isolation, Consolidation Worker, 5-Tab Admin UI, Docker Compose) | `WEEK 6/production_project/` |

---

## Complete Labs Matrix (Weeks 1–6)

| Lab | Week | Description | Status |
|---|---|---|---|
| Lab 1.1 | 1 | Groq CLI chatbot with history, `/clear`, `/exit` | Complete |
| Lab 1.2 | 1 | Manual ReAct agent with search, calculate, time tools | Complete |
| Lab 1.3 | 1 | Prompt A/B testing with five system prompts | Complete |
| Lab 2.1 | 2 | Structured output extractor (Pydantic job posting parser) | Complete |
| Lab 2.2 | 2 | Multi-tool research agent with 5 tools + routing | Complete |
| Lab 2.3 | 2 | Error recovery agent with real APIs + retry + fallbacks | Complete |
| Lab 3.1 | 3 | Semantic search CLI, embedding models, PCA visualization | Complete |
| Lab 4.1 | 4 | LangGraph workflow: load $\rightarrow$ validate $\rightarrow$ chunk $\rightarrow$ embed | Complete |
| Lab 4.2 | 4 | Self-correcting agent loop with classification router | Complete |
| Lab 4.3 | 4 | Stateful approval workflow with human review | Complete |
| Lab 5.1 | 5 | Typed message bus using Pydantic contracts | Complete |
| Lab 5.2 | 5 | Supervisor failure recovery with retries and fallbacks | Complete |
| Lab 5.3 | 5 | Debate & consensus engine with weighted confidence voting | Complete |
| Lab 6.1 | 6 | Memory-augmented chatbot demonstrating cross-session recall | Complete |
| Lab 6.2 | 6 | Knowledge graph query agent with multi-hop NetworkX traversal | Complete |
| Lab 6.3 | 6 | GraphRAG hybrid retrieval combining vector search and graph traversal | Complete |

---

## GitHub Repository

[https://github.com/sohaibAkhlaq/calderr-ai-2026](https://github.com/sohaibAkhlaq/calderr-ai-2026)
