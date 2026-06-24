# CalderR AI Internship
**Project location:** Desktop/calderr-ai-2026
**Author:** Sohaib Akhlaq
**Status:** Week 1 Day 3 Complete

---

## Overview
This repository contains the complete setup and daily progress for the CalderR AI internship program. It captures the local development environment, installed dependencies, LLM integration, and week-by-week progress.

---

## Week 0: Environment Setup (Complete)

### Environment

- **Python:** 3.11.9
- **Virtual environment:** calderr-env (ignored by VCS)
- **pip:** Upgraded to latest version

### Installed Packages

- langchain, langchain-groq, langchain-community, langgraph
- groq, openai, pydantic, python-dotenv
- fastapi, uvicorn, chromadb
- httpx, rich, typer, pytest, jupyter, streamlit
- PyTorch 2.12.1 (CPU-only for Windows compatibility)
- rank-bm25 (for keyword-based retrieval)

### Version Control

- Git configured with SSH key
- Repository: calderr-ai-2026

### Containerization

- Docker Desktop installed
- Dockerfile included

### IDE

- VS Code with Python, Pylance, Jupyter extensions

---

## Week 1: AI Fundamentals

### Day 1 — LLM Foundations (Complete)
**Status:** ✅ Complete

**What was covered:**

- Transformer architecture and self-attention mechanism
- Tokenization, context windows, and temperature parameters
- Training vs inference concepts
- Groq API models: llama-3.3-70b-versatile, llama-3.1-8b-instant
- Model performance comparison and benchmarking

**Implementation:**

- `test_groq_monday.py` — Model testing across temperatures (0, 0.7, 1.5). Found llama-3.1-8b-instant fastest (~0.8s), llama-3.3-70b-versatile highest quality (~1.5s).
- `temperature_experiment.py` — Temperature range testing (0.0 to 2.0). Confirmed 0.0 = deterministic, 0.7 = balanced, 1.5+ = creative.
- `cli_chatbot.py` — CLI chatbot with conversation history and commands (/clear, /history, /exit).
- `week1day1.txt` — Detailed notes and key takeaways.

**Key Findings:**

- llama-3.1-8b-instant: Fastest (0.77-0.96s), best for prototyping
- llama-3.3-70b-versatile: Best quality (1.35-2.10s), slower
- mixtral-8x7b-32768: Decommissioned (not available)

---

### Day 2 — Agentic AI Concepts (Complete)
**Status:** ✅ Complete

**What was covered:**

- ReAct pattern: Reasoning + Acting in LLMs
- Agent Loop: Perceive → Reason → Plan → Act → Observe → Repeat
- Reactive vs Proactive agents
- Tools, memory, and planning concepts
- Agent decision-making and tool selection

**Implementation:**

- `react_agent.py` — Manual ReAct agent built without any framework. Implements 3 tools:
  - `search_database()` — Mock database for facts (capitals, populations, inventors)
  - `calculate()` — Math expression evaluation using eval()
  - `get_current_time()` — Current date and time retrieval
  - Tool selection based on keyword matching
  - Full agent loop with verbose logging
  - CLI with /history, /help, /exit commands
- `week1day2.txt` — Detailed notes on agentic AI concepts

**Key Learnings:**

- Language Model: Generates text based on patterns
- Agent: Uses tools, makes decisions, takes actions
- Agent adds: Planning, tool use, memory, decision-making
- ReAct combines reasoning and acting in a loop
- Tools extend agent capabilities beyond text generation

---

### Day 3 — LangChain Core (Complete)
**Status:** ✅ Complete

**What was covered:**

- LCEL (LangChain Expression Language) and the pipe operator (`|`)
- Runnable, RunnablePassthrough, RunnableParallel
- RAG (Retrieval-Augmented Generation) pattern
- Document loading, splitting, and retrieval
- BM25 keyword-based retrieval (no embeddings required)
- Three different chain patterns with LCEL

**Implementation:**

- `document_qa_chain.py` — Complete RAG pipeline with BM25 retriever:
  - Load document → Split into chunks → Create BM25 retriever → Build RAG chain → Answer questions
  - Interactive Q&A system with conversation
- `chain_patterns.py` — 3 different chain patterns:
  1. **Simple Chain:** `prompt | llm | parser`
  2. **RunnablePassthrough:** Passes data through unchanged
  3. **RunnableParallel:** Multiple chains in parallel
- `week1day3.txt` — Detailed notes on LangChain Core concepts

**Key Learnings:**

- **LCEL:** Makes chains readable, composable, and production-ready
- **Runnable:** Base interface for all chainable objects
- **RunnablePassthrough:** Passes data through to multiple places
- **RunnableParallel:** Runs multiple chains simultaneously
- **RAG:** Improves accuracy by retrieving relevant context
- **BM25:** Effective keyword-based retrieval without embeddings

---

## Environment Notes (Windows Fix)

### PyTorch DLL Issue (RESOLVED)
The original installation encountered `OSError: [WinError 1114]` when importing PyTorch due to mixed GPU/CPU builds. 

**Solution:**
- Reinstalled PyTorch CPU-only from official repository: `pip install torch --index-url https://download.pytorch.org/whl/cpu`
- Removed problematic `sentence-transformers` dependency
- Switched to BM25 retriever for keyword-based search (no embeddings needed)

### Requirements Files
- `requirements-minimal.txt` — Lightweight setup (LangChain + Groq + BM25, no heavy ML)
- `requirements-windows.txt` — Full stack (includes optional extras)

---

```
Desktop/calderr-ai-2026/
├── calderr-env/                 # Virtual environment (gitignored)
├── .git/                        # Git repository metadata
├── .gitignore                   # Git ignore rules
├── .env                         # Environment variables (gitignored)
├── .env.template                # Environment variable template
├── requirements.txt             # Python dependencies
├── requirements-minimal.txt     # Minimal Windows-compatible dependencies
├── requirements-windows.txt     # Full Windows setup
├── main.py                      # Main application entry point
├── test_setup.py                # Week 0 verification script
├── test_env.py                  # API key verification
├── test_groq.py                 # Day 2 first LLM call
├── test_groq_stream.py          # Day 2 streaming example
├── test_groq_monday.py          # Week 1 Day 1 model testing
├── temperature_experiment.py    # Week 1 Day 1 temperature testing
├── cli_chatbot.py               # Week 1 Day 1 CLI chatbot
├── react_agent.py               # Week 1 Day 2 Manual ReAct Agent
├── document_qa_chain.py         # Week 1 Day 3 Document Q&A Chain
├── chain_patterns.py            # Week 1 Day 3 Chain Patterns
├── week1day1.txt                # Week 1 Day 1 notes
├── week1day2.txt                # Week 1 Day 2 notes
├── week1day3.txt                # Week 1 Day 3 notes
├── notebooks/
│   ├── 01_first_llm_call.ipynb  # Day 2 Jupyter notebook
│   └── README.md                # Notebook documentation
├── Dockerfile                   # Docker configuration
├── day1-summary.txt             # Day 1 summary
├── day2-summary.txt             # Day 2 summary
└── README.md                    # This file
```

---

## Quick Start

### Activate Virtual Environment (PowerShell)

```powershell
.\calderr-env\Scripts\Activate.ps1
```

### Run Applications

```powershell
python main.py                    # Week 0: Main application
python test_env.py                # API key verification
python test_groq.py               # Day 2: First LLM call
python test_groq_stream.py        # Day 2: Streaming example
python test_groq_monday.py        # Week 1 Day 1: Model testing
python temperature_experiment.py  # Week 1 Day 1: Temperature testing
python cli_chatbot.py             # Week 1 Day 1: CLI chatbot
python react_agent.py             # Week 1 Day 2: Manual ReAct Agent
python document_qa_chain.py       # Week 1 Day 3: Document Q&A Chain
python chain_patterns.py          # Week 1 Day 3: Chain Patterns
```

### Launch Jupyter Lab
```powershell
jupyter lab
```

### Docker
```powershell
docker build -t calderr-ai-2026 .
docker run --rm calderr-ai-2026
```

---

## Security Notes

- Never commit `.env` to version control
- Refer to `.env.template` for required environment variables
- Groq API provides ~14,400 requests/day on free tier

---

## GitHub Repository
[https://github.com/sohaibAkhlaq/calderr-ai-2026](https://github.com/sohaibAkhlaq/calderr-ai-2026)

---

## Week Progress

| Day | Topic | Status |
|-----|-------|--------|
| Week 0 | Environment Setup | ✅ Complete |
| Day 1 | LLM Foundations | ✅ Complete |
| Day 2 | Agentic AI Concepts | ✅ Complete |
| Day 3 | LangChain Core | ✅ Complete |
| Day 4 | Prompt Engineering | ⏳ Upcoming |
| Day 5 | Integration & Demo | ⏳ Upcoming |
