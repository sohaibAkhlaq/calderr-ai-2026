# CalderR AI Internship

**Project Location:** `Desktop/calderr-ai-2026`  
**Author:** Sohaib Akhlaq  
**Status:** Week 4 Day 3 Complete

---

## Overview

This repository documents the complete setup, learning progress, and hands-on implementation completed during the CalderR AI internship. It covers environment configuration, foundational AI concepts, agentic systems, LangChain workflows, prompt-engineering experiments, structured outputs, tool calling, external API integration, and fully deployed production AI applications.

---

## Project Goals

- Work with large language models via APIs
- Understand agentic AI design patterns
- Build simple LLM-based applications in Python
- Explore prompt engineering and persona-driven prompting
- Create reusable, readable project documentation
- Integrate all concepts into production-ready deployments

---

## Quick Start — One Command

```powershell
# Activate the environment
cd C:\Users\USER\Desktop\calderr-ai-2026
.\calderr-env\Scripts\Activate.ps1

# All Week 1 and Week 2 scripts now work inside calderr-env.
# streamlit, plotly, httpx, langchain, pydantic — all installed.
```

After activation, run any project with a single command:

```powershell
# Week 1: Professional Chatbot
python week1/professional_chatbot.py

# Week 2: API Aggregator Agent (CLI)
python week2/project2_i_c_api_aggregator.py

# Week 2: Financial Data Analysis Agent (Streamlit)
# Use calderr-env python explicitly — streamlit is installed there
calderr-env\Scripts\python.exe -m streamlit run week2/project2_p_c_financial_analysis.py
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
| Data | Pandas, NumPy, Plotly |
| Web | Streamlit, FastAPI, Uvicorn |
| HTTP | HTTPX (async HTTP client) |
| Validation | Pydantic v2 |
| Vector DB | ChromaDB, sentence-transformers |
| Terminal | Rich, Typer |
| Testing | PyTest, Jupyter |
| DevOps | Docker Desktop, VS Code |

---

## Repository Structure

```
calderr-ai-2026/
├── .env                          # API keys (not committed)
├── .env.template                 # Template for API keys
├── .gitignore
├── requirements.txt              # Full dependencies
├── requirements-streamlit.txt    # Lean deps for Streamlit Cloud
├── main.py
├── README.md                     # This file
│
├── week1/                        # Week 1: AI Fundamentals
│   ├── professional_chatbot.py
│   ├── multi_model_benchmark.py
│   ├── prompt_evaluator.py
│   ├── react_agent.py
│   ├── document_qa_chain.py
│   ├── architecture_diagram.md
│   ├── weekly_assessment.md
│   ├── week1day1.txt ... week1day4.txt
│   └── ...
│
└── week2/                        # Week 2: Advanced AI Patterns
    ├── lab2.1_cot_pipeline.py
    ├── lab2.1_cot_prompts.py
    ├── lab2.1_structured_extractor.py
    ├── lab2.1_pydantic_models.py
    ├── lab2.2_multi_tool_agent.py
    ├── lab2.2_tool_calling_demo.py
    ├── lab2.3_external_api_tools.py
    ├── project2_i_c_api_aggregator.py      <- Intermediate Project (CLI)
    ├── project2_p_c_financial_analysis.py  <- Production Project (Streamlit)
    ├── project2_i_c_run_guide.md           <- Run guide + test cases (Project 1)
    ├── project2_p_c_run_guide.md           <- Run guide + sample CSVs (Project 2)
    ├── week2_assessment.md
    ├── week2day1.txt ... week2day5.txt
    └── README.md
│
└── WEEK 3/                       # Week 3: Embeddings, RAG & Vector DBs
    ├── lab3_1.py                 # Semantic Search CLI & PCA
    ├── lab3_2.py                 # Vector DBs & Chunking
    ├── lab3_3_naive_rag.py       # Naive RAG & Chunk Tuning
    ├── intermediate_project/     # Day 6: Hybrid Search Engine
    │   ├── hybrid_search_engine.py
    │   └── README.md
    ├── lab3_4_advanced_retrieval.py # Hybrid Search & Re-ranking
    ├── lab3_5_rag_evaluation.py  # RAG Evaluation & Weekly Assessment
    ├── WEEK3DAY1.txt             # Day 1 Journal
    ├── WEEK3DAY2.txt             # Day 2 Journal
    ├── WEEK3DAY3.txt             # Day 3 Journal
    ├── WEEK3DAY4.txt             # Day 4 Journal
    ├── WEEK3DAY5.txt             # Day 5 Journal
    └── WEEK 3 WORK.md            # 7-Day Schedule
│
└── Week 4/                       # Week 4: LangGraph & Agentic Workflows
    ├── lab4.1_document_processing.py # LangGraph Document Processing Lab
    ├── lab4.2_self_correcting_loop.py # Self-correcting loop lab
    ├── lab4.3_approval_workflow.py # Stateful approval workflow lab
    ├── day1_concepts.txt         # Day 1 Concepts
    ├── day2_concepts.txt         # Day 2 Concepts
    └── day3_concepts.txt         # Day 3 Concepts
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

### Week 1 Projects

| Project | Description |
|---|---|
| **1-I-B: Prompt Evaluator** | Generates and scores 3 prompts per task; JSON report export |
| **1-P-B: Multi-Model Benchmark** | Tests 2+ models on 5+ tasks; async execution; HTML + JSON reports |

---

## Week 2 — Advanced AI Patterns

| Day | Topic | Status | Key Files |
|---|---|---|---|
| Monday | Advanced Prompting | Complete | `lab2.1_cot_pipeline.py`, `lab2.1_cot_prompts.py` |
| Tuesday | Structured Outputs | Complete | `lab2.1_structured_extractor.py`, `lab2.1_pydantic_models.py` |
| Wednesday | Tool Calling Basics | Complete | `lab2.2_multi_tool_agent.py`, `lab2.2_tool_calling_demo.py` |
| Thursday | External APIs as Tools | Complete | `lab2.3_external_api_tools.py` |
| Friday | Integration + Demo | Complete | Both projects below |

### Week 2 Projects

#### Project 2-I-C: API Aggregator Agent (Intermediate)

Fetches weather, currency rates, and financial news **in parallel** using `asyncio.gather` and synthesises a professional morning briefing report via a chain-of-thought LLM prompt.

```powershell
python week2/project2_i_c_api_aggregator.py
```

Full run guide with test cases: `week2/project2_i_c_run_guide.md`

**Week 2 patterns used:**
- Day 1: Chain-of-thought LLM synthesis prompt
- Day 2: Pydantic `BriefingReport`, `WeatherData`, `CurrencyData` schemas
- Day 3: Tool registry with three async tool functions
- Day 4: Exponential backoff + jitter on every API call, mock fallbacks

---

#### Project 2-P-C: Financial Data Analysis Agent (Production)

A Streamlit web app. Upload any financial CSV, ask a natural-language question, get generated code, interactive Plotly charts, and a professional narrative report.

```powershell
python -m streamlit run week2/project2_p_c_financial_analysis.py
```

Full run guide with sample CSVs + 18 test questions: `week2/project2_p_c_run_guide.md`

**Week 2 patterns used:**
- Day 1: CoT prompts for both code generation and report generation
- Day 2: `AnalysisResult` and `DatasetProfile` Pydantic schemas
- Day 3: Five analysis tools (describe, plot, correlate, filter, stats) with keyword routing
- Day 4: Live currency rates via external API with retry + fallback
- Day 5: Subprocess sandbox, session history, dark professional Streamlit UI

**Streamlit Cloud deployment:**
1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository, set main file: `week2/project2_p_c_financial_analysis.py`
4. Add `GROQ_API_KEY` under Advanced Settings > Secrets
5. Deploy — uses `requirements-streamlit.txt`

---

## Week 3 — Embeddings, RAG & Vector Databases

| Day | Topic | Status | Key Files |
|---|---|---|---|
| Monday | Embeddings Deep Dive | Complete | `WEEK 3/lab3_1.py`, `WEEK 3/WEEK3DAY1.txt` |
| Tuesday | Vector Databases | Complete | `WEEK 3/lab3_2.py`, `WEEK 3/WEEK3DAY2.txt` |
| Wednesday | Naive RAG Architecture | Complete | `WEEK 3/lab3_3_naive_rag.py`, `WEEK 3/WEEK3DAY3.txt` |
| Thursday | Advanced Retrieval | Complete | `WEEK 3/lab3_4_advanced_retrieval.py`, `WEEK 3/WEEK3DAY4.txt` |
| Friday | RAG Evaluation & Assessment | Complete | `WEEK 3/lab3_5_rag_evaluation.py`, `WEEK 3/WEEK3DAY5.txt` |
| Saturday | Intermediate Project | Complete | `WEEK 3/intermediate_project/` |

### Week 3 Projects

#### Project 3-I-C: Hybrid Search Engine (Intermediate)

A CLI search tool that ingests PDF documents and provides intelligent hybrid search combining BM25 keyword search + semantic vector search + cross-encoder re-ranking. Includes built-in evaluation on 30 queries.

```powershell
python "WEEK 3/intermediate_project/hybrid_search_engine.py"
```

Full architecture, usage, and evaluation details: `WEEK 3/intermediate_project/README.md`

**Week 3 patterns used:**
- Day 1: Sentence-Transformer Embeddings (`all-MiniLM-L6-v2`)
- Day 2: ChromaDB Vector Storage & Document Chunking with Metadata
- Day 3: Full RAG Pipeline (load → split → embed → store → retrieve → generate)
- Day 4: BM25 Hybrid Search, EnsembleRetriever, Cross-Encoder Re-ranking
- Day 5: Evaluation Metrics (Context Precision, Answer Relevancy, Faithfulness)

#### Project 3-P-C: RAG Evaluation Benchmark (Production)

An advanced RAG Evaluation Benchmark dashboard deployed on Streamlit, comparing multiple chunk sizes, embedding models, and retrieval strategies (Semantic, BM25 Hybrid, Cross-Encoder Reranking) across 10 evaluation queries.

**Features:**
- **Dynamic Leaderboard:** Automatically ranks the best RAG configuration.
- **Plotly Visualizations:** Interactive charts for response times and metrics.
- **Robust Error Handling:** Recovers from library initialization and network errors gracefully.
- **Export Reports:** Downloads statistical comparison reports as JSON.

##### CLI Mode:
```powershell
python "WEEK 3/production_project/project3_p_c_rag_benchmark.py"
```

##### Streamlit UI Mode:
```powershell
streamlit run "WEEK 3/production_project/project3_p_c_rag_benchmark.py" -- --streamlit
```

---

## Week 4 — LangGraph & Agentic Workflows

| Day | Topic | Status | Key Files |
|---|---|---|---|
| Monday | LangGraph Foundations | Complete | `Week 4/lab4.1_document_processing.py`, `Week 4/day1_concepts.txt` |
| Tuesday | Branching & Loops | Complete | `Week 4/lab4.2_self_correcting_loop.py`, `Week 4/day2_concepts.txt` |
| Wednesday | Stateful Agents & Human-in-the-Loop | Complete | `Week 4/lab4.3_approval_workflow.py`, `Week 4/day3_concepts.txt` |

### Week 4 Projects

#### Lab 4.3: Stateful Approval Workflow

A LangGraph workflow for content moderation that routes content through auto-approve, auto-reject, and human-review steps. The workflow uses a TypedDict state schema, reducer-based message accumulation, and revision loops for bounded human-in-the-loop review.

```powershell
python "Week 4/lab4.3_approval_workflow.py"
```

---

## Labs Completed

| Lab | Week | Description | Status |
|---|---|---|---|
| Lab 1.1 | 1 | Groq CLI chatbot with history, `/clear`, `/exit` | Complete |
| Lab 1.2 | 1 | Manual ReAct agent with search, calculate, time tools | Complete |
| Lab 1.3 | 1 | Prompt A/B testing with five system prompts | Complete |
| Lab 2.1 | 2 | Structured output extractor (Pydantic job posting parser) | Complete |
| Lab 2.2 | 2 | Multi-tool research agent with 5 tools + routing | Complete |
| Lab 2.3 | 2 | Error recovery agent with real APIs + retry + fallbacks | Complete |
| Lab 3.1 | 3 | Semantic search CLI, embedding models, PCA visualization | Complete |
| Lab 4.1 | 4 | LangGraph workflow: load → validate → chunk → embed → confirm | Complete |
| Lab 4.2 | 4 | Self-correcting agent loop with classification router and bounded retries | Complete |
| Lab 4.3 | 4 | Stateful approval workflow with TypedDict state, reducers, and human review | Complete |

---

## APIs Used (All Free)

| API | Endpoint | Used In | Key Required |
|---|---|---|---|
| Open-Meteo | `api.open-meteo.com` | Weather fetch | No |
| exchangerate-api | `api.exchangerate-api.com` | Currency rates | No |
| GNews | `gnews.io/api/v4` | Financial news (mock fallback) | No |
| Groq | `api.groq.com` | LLM inference | Yes — set in `.env` |

---

## Security Notes

- Never commit `.env` files — they contain API keys.
- Use `.env.template` as the template; fill in locally.
- Review Git history before pushing to ensure no credentials are leaked.

---

## GitHub Repository

[https://github.com/sohaibAkhlaq/calderr-ai-2026](https://github.com/sohaibAkhlaq/calderr-ai-2026)

---

## Progress Summary

| Week | Topic | Status |
|---|---|---|
| Week 0 | Environment Setup | Complete |
| Week 1 | AI Fundamentals | Complete |
| Week 2 | Advanced AI Patterns | Complete |
| Week 3 | Embeddings, RAG & Vector Databases | Complete |
| Week 4 | LangGraph & Agentic Workflows | Complete for Day 3 |
