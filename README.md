# CalderR AI Internship

**Project Location:** `Desktop/calderr-ai-2026`  
**Author:** Sohaib Akhlaq  
**Status:** Week 6 Fully Complete (Weeks 1 through 6 Completed)
 
---

## Overview

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

## Quick Start — One Command

```powershell
# Activate the environment
cd C:\Users\USER\Desktop\calderr-ai-2026
.\calderr-env\Scripts\Activate.ps1

# All Week 1 to Week 6 scripts work inside calderr-env.
# Streamlit, NetworkX, ChromaDB, FastAPI, LangGraph, Pydantic — all installed.
```

After activation, run any lab or project script:

```powershell
# Week 1: Professional Chatbot
python week1/professional_chatbot.py

# Week 2: Financial Data Analysis Agent (Streamlit)
calderr-env\Scripts\python.exe -m streamlit run week2/project2_p_c_financial_analysis.py

# Week 3: Hybrid Search Engine
python "WEEK 3/intermediate_project/hybrid_search_engine.py"

# Week 4: Production Hiring Pipeline Platform
calderr-env\Scripts\python.exe -m streamlit run "Week 4/production_project/app_streamlit.py"

# Week 5: Multi-Agent Consensus Engine Lab
python "WEEK 5/lab5.3_consensus_engine.py"

# Week 6: Memory-Augmented Chatbot (Lab 6.1)
python "WEEK 6/lab6_1_memory_augmented_chatbot.py"

# Week 6: Knowledge Graph Query Agent (Lab 6.2)
python "WEEK 6/lab6_2_knowledge_graph_query_agent.py"

# Week 6: GraphRAG Hybrid Retrieval Engine (Lab 6.3)
python "WEEK 6/lab6_3_graphrag_hybrid_retrieval.py"
```

---

## Environment Summary

- **Python:** 3.11.9
- **Virtual environment:** `calderr-env`
- **Git:** SSH configured

### Installed Libraries

| Category | Packages |
|---|---|
| LLM | LangChain, LangChain-Groq, LangChain-Community, LangGraph, Groq |
| Memory & Graphs | ChromaDB, NetworkX, SQLite, sentence-transformers |
| Multi-Agent | Pydantic v2, TypedDict, asyncio, custom message bus |
| Data | Pandas, NumPy, Plotly, Pyvis |
| Web & API | Streamlit, FastAPI, Uvicorn, HTTPX |
| Terminal | Rich, Typer |
| Testing & DevOps | PyTest, Jupyter, Docker Desktop |

---

## Repository Structure

```
calderr-ai-2026/
├── .env                          # API keys (not committed)
├── .env.template                 # Template for API keys
├── .gitignore
├── requirements.txt              # Full dependencies
├── main.py
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
    ├── intermediate_project/              # Project 6-I-A: Personal Research Assistant
    └── production_project/                # Project 6-P-A: Enterprise AI Memory Platform
```

---

## Week 1 — AI Fundamentals

| Day | Topic | Status | Key Files |
|---|---|---|---|
| Day 1 | LLM Foundations | Complete | `test_groq_monday.py`, `temperature_experiment.py` |
| Day 2 | Agentic AI Concepts | Complete | `react_agent.py` |
| Day 3 | LangChain Core | Complete | `document_qa_chain.py`, `chain_patterns.py` |
| Day 4 | Prompt Engineering | Complete | `prompt_engineering_lab.py`, `persona_agent.py` |
| Day 5 | Integration + Demo | Complete | `professional_chatbot.py`, `multi_model_benchmark.py` |

---

## Week 2 — Advanced AI Patterns

| Day | Topic | Status | Key Files |
|---|---|---|---|
| Monday | Advanced Prompting | Complete | `lab2.1_cot_pipeline.py`, `lab2.1_cot_prompts.py` |
| Tuesday | Structured Outputs | Complete | `lab2.1_structured_extractor.py`, `lab2.1_pydantic_models.py` |
| Wednesday | Tool Calling Basics | Complete | `lab2.2_multi_tool_agent.py`, `lab2.2_tool_calling_demo.py` |
| Thursday | External APIs as Tools | Complete | `lab2.3_external_api_tools.py` |
| Friday | Integration + Demo | Complete | Both projects below |

---

## Week 3 — Embeddings, RAG & Vector Databases

| Day | Topic | Status | Key Files |
|---|---|---|---|
| Monday | Embeddings Deep Dive | Complete | `WEEK 3/lab3_1.py`, `WEEK 3/WEEK3DAY1.txt` |
| Tuesday | Vector Databases | Complete | `WEEK 3/lab3_2.py`, `WEEK 3/WEEK3DAY2.txt` |
| Wednesday | Naive RAG Architecture | Complete | `WEEK 3/lab3_3_naive_rag.py`, `WEEK 3/WEEK3DAY3.txt` |
| Thursday | Advanced Retrieval | Complete | `WEEK 3/lab3_4_advanced_retrieval.py`, `WEEK 3/WEEK3DAY4.txt` |
| Friday | RAG Evaluation & Assessment | Complete | `WEEK 3/lab3_5_rag_evaluation.py`, `WEEK 3/WEEK3DAY5.txt` |

---

## Week 4 — LangGraph & Agentic Workflows

| Day | Topic | Status | Key Files |
|---|---|---|---|
| Monday | LangGraph Foundations | Complete | `Week 4/lab4.1_document_processing.py` |
| Tuesday | Branching & Loops | Complete | `Week 4/lab4.2_self_correcting_loop.py` |
| Wednesday | Stateful Agents | Complete | `Week 4/lab4.3_approval_workflow.py` |
| Thursday | Human-in-the-Loop | Complete | `Week 4/lab4.3_hitl_approval_workflow.py` |
| Friday | Production Graphs | Complete | `Week 4/lab4.4_production_graph.py` |

---

## Week 5 — Multi-Agent Systems & Team Architectures

| Day | Topic | Status | Key Files |
|---|---|---|---|
| Day 1 | Typed Message Passing | Complete | `WEEK 5/lab5.1_typed_message_bus.py`, `WEEK5DAY1.txt` |
| Day 2 | Supervisor Pattern & Recovery | Complete | `WEEK 5/lab5.2_supervisor_failure_recovery.py`, `WEEK5DAY2.txt` |
| Day 3 | Debate & Consensus Engine | Complete | `WEEK 5/lab5.3_consensus_engine.py`, `WEEK5DAY3.txt` |
| Day 4 | Hierarchical Teams | Complete | `WEEK 5/lab5.3_hierarchical_teams.py`, `WEEK5DAY4.txt` |
| Day 5 | Production Integration | Complete | `WEEK 5/week5_production_integration.py`, `WEEK5DAY5.txt` |

---

## Week 6 — Memory Systems & Knowledge Graphs

| Day | Topic | Status | Key Files |
|---|---|---|---|
| Monday | Episodic & Semantic Memory | Complete | `WEEK 6/lab6_1_memory_augmented_chatbot.py`, `WEEK6DAY1.txt` |
| Tuesday | Semantic Memory & Profiles | Complete | `WEEK 6/WEEK6DAY2.txt` |
| Wednesday | Knowledge Graphs & Traversals | Complete | `WEEK 6/lab6_2_knowledge_graph_query_agent.py`, `WEEK6DAY3.txt` |
| Thursday | GraphRAG & Consolidation | Complete | `WEEK 6/lab6_3_graphrag_hybrid_retrieval.py`, `WEEK6DAY4.txt` |
| Friday | Full-Stack Integration | Complete | `WEEK 6/README.md`, `WEEK6_ASSESSMENT.md`, `WEEK6DAY5.txt` |

### Key Week 6 Labs & Deliverables
- **Lab 6.1 (Memory-Augmented Chatbot):** Implemented SQLite episodic log + persistent vector store. Verified cross-session recall across 3 sessions.
- **Lab 6.2 (Knowledge Graph Query Agent):** Extracted entities & relationships into NetworkX from 20 text paragraphs, answered 5/5 multi-hop questions, and exported Pyvis interactive HTML (`knowledge_graph.html`).
- **Lab 6.3 (GraphRAG Hybrid Retrieval):** Parallel ChromaDB vector search + NetworkX graph traversal with Pydantic query router (80%+ classification accuracy).
- **Intermediate Project (6-I-A):** System architecture & memory design for Long-Term Personal Research Assistant.
- **Production Project (6-P-A):** Architecture & API design for Enterprise AI Memory Platform (Mem0 alternative).

---

## Complete Labs Matrix

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

## Security Notes

- Never commit `.env` files — they contain API keys.
- Use `.env.template` as the template; fill in locally.
- Review Git history before pushing to ensure no credentials are leaked.

---

## GitHub Repository

[https://github.com/sohaibAkhlaq/calderr-ai-2026](https://github.com/sohaibAkhlaq/calderr-ai-2026)

---

## Overall Progress Summary

| Week | Topic | Status |
|---|---|---|
| Week 0 | Environment Setup | Complete |
| Week 1 | AI Fundamentals | Complete |
| Week 2 | Advanced AI Patterns | Complete |
| Week 3 | Embeddings, RAG & Vector Databases | Complete |
| Week 4 | LangGraph & Agentic Workflows | Complete |
| Week 5 | Multi-Agent Systems & Team Architectures | Complete |
| Week 6 | Memory Systems & Knowledge Graphs | Complete (All 5 Days) |
