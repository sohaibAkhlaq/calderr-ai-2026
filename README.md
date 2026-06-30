# CalderR AI Internship

**Project Location:** `Desktop/calderr-ai-2026`
**Author:** Sohaib Akhlaq
**Status:** Week 1 Day 5 Complete ✅

---

## Overview

This repository documents the complete setup, learning progress, and hands‑on implementation completed during the CalderR AI internship. It covers environment configuration, foundational AI concepts, agentic systems, LangChain workflows, prompt‑engineering experiments, and a fully integrated professional chatbot.

---

## Project Goals

- Work with large language models via APIs
- Understand agentic AI design patterns
- Build simple LLM‑based applications in Python
- Explore prompt engineering and persona‑driven prompting
- Create reusable, readable project documentation
- Integrate all concepts into a production‑ready demo

---

## Environment Summary

- **Python:** 3.11.9
- **Virtual environment:** `calderr-env`
- **pip:** latest
- **Git:** SSH configured

### Installed Tools & Libraries

- LangChain, LangChain‑Groq, LangChain‑Community, LangGraph
- Groq, OpenAI, Pydantic, python‑dotenv
- FastAPI, Uvicorn, ChromaDB
- HTTPX, Rich, Typer, PyTest, Jupyter, Streamlit
- PyTorch 2.12.1 (CPU‑only, Windows compatible)
- rank‑bm25 for keyword‑based retrieval

### Development Environment

- Docker Desktop installed & configured
- VS Code with Python, Pylance, and Jupyter extensions

---

## Week 0 – Environment Setup

```powershell
# Activate virtual environment
.\calderr-env\Scripts\Activate.ps1
```

- Created virtual environment `calderr-env`
- Upgraded pip and installed the above dependencies
- Configured Git with SSH keys

---

## Week 1 – AI Fundamentals

### Day 1 – LLM Foundations (✅)
- Topics: Transformers, tokenisation, temperature, inference vs training
- Implemented: `test_groq_monday.py`, `temperature_experiment.py`, `cli_chatbot.py`

### Day 2 – Agentic AI Concepts (✅)
- Topics: ReAct pattern, agent loop, tool use, planning
- Implemented: `react_agent.py`

### Day 3 – LangChain Core (✅)
- Topics: LCEL pipeline, Runnable, RunnablePassthrough, RunnableParallel, BM25 retrieval
- Implemented: `document_qa_chain.py`, `chain_patterns.py`

### Day 4 – Prompt Engineering (✅)
- Topics: System prompts, few‑shot, chain‑of‑thought, persona prompting
- Implemented: `prompt_engineering_lab.py`, `persona_agent.py`, `weekly_assessment.md`

### Day 5 – Integration & Demo (✅)
- Built a **Professional Chatbot** with:
  - Five personas (general, technical, creative, academic, mentor)
  - Conversation memory & statistics (tokens, turns, duration)
  - Rich terminal UI (panels, tables, markdown)
  - Commands: `/exit`, `/clear`, `/history`, `/stats`, `/help`
- Updated `architecture_diagram.md` with Mermaid diagrams
- Completed `weekly_assessment.md`

---

## Architecture Diagram

The repository now includes `architecture_diagram.md` which visualises the chatbot architecture, agent loop, and data flow using Mermaid.

---

## Quick Start

```powershell
# Activate environment
.\calderr-env\Scripts\Activate.ps1

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run the professional chatbot
python professional_chatbot.py
```

### Jupyter Lab

```powershell
jupyter lab
```

### Docker

```powershell
docker build -t calderr-ai-2026 .
# Run container
docker run --rm calderr-ai-2026
```

---

## Repository Structure

```
calderr-ai-2026/
├─ .git/                     # Git metadata
├─ .gitignore                # Ignored files (env, __pycache__, etc.)
├─ .env.template             # Template for environment variables
├─ requirements.txt          # Full dependency list
├─ requirements-minimal.txt  # Minimal setup for local experiments
├─ requirements-windows.txt  # Windows‑specific dependencies
├─ main.py                   # Entry point (Week 0)
├─ test_*.py                 # Verification and experiment scripts
├─ professional_chatbot.py   # Week 5 professional chatbot
├─ architecture_diagram.md   # Mermaid diagrams of architecture & agent loop
├─ weekly_assessment.md      # Completed assessment
├─ README.md                 # **(this file)**
├─ ... (other source files as listed above)
```

---

## Security Notes

- **Never** commit `.env` files – they contain API keys.
- Keep your Groq API key secret; use the `.env` template to provide it locally.
- Review Git history before pushing to ensure no credentials are leaked.

---

## GitHub Repository

[https://github.com/sohaibAkhlaq/calderr-ai-2026](https://github.com/sohaibAkhlaq/calderr-ai-2026)

---

## Week 1 Progress Summary

| Week/Day | Topic | Status |
|----------|-------|--------|
| Week 0   | Environment Setup | ✅ Complete |
| Day 1    | LLM Foundations | ✅ Complete |
| Day 2    | Agentic AI Concepts | ✅ Complete |
| Day 3    | LangChain Core | ✅ Complete |
| Day 4    | Prompt Engineering | ✅ Complete |
| Day 5    | Integration & Demo | ✅ Complete |

---

## Labs Completed (Week 1)

| Lab | Description | Status |
|-----|-------------|--------|
| Lab 1.1 | Groq CLI chatbot with history, `/clear`, `/exit` | ✅ Complete |
| Lab 1.2 | Manual ReAct agent with search, calculate, time tools | ✅ Complete |
| Lab 1.3 | Prompt A/B testing with five system prompts | ✅ Complete |

---

## Week 1 Projects Completed (✅)

### Intermediate Project (1-I-B): Prompt Engineering Evaluator
- Generates 3 prompts per task
- Tests and scores on accuracy, brevity, helpfulness
- Rich CLI with tables and panels
- JSON report export

### Production Project (1-P-B): Multi-Model Comparison Engine
- Tests 2+ models on 5+ tasks
- Async parallel execution
- Statistical analysis with rich visualizations
- HTML + JSON reports

---

## Week 2 Progress Summary (In Progress)

| Week/Day | Topic | Status |
|----------|-------|--------|
| Day 1    | Advanced Prompting | Complete |
| Day 2    | Structured Outputs | Complete |
| Day 3    | Multi-Tool Research Agent | Pending |
| Day 4    | Error Recovery Agent | Pending |
| Day 5    | Intermediate & Production Projects | Pending |

---

## Labs Completed (Week 2)

| Lab | Description | Status |
|-----|-------------|--------|
| Lab 2.1 | Advanced Prompting Techniques & CoT Pipeline | Complete |
| Lab 2.2 | Structured Output Extractor with Pydantic | Complete |

---

**Week 2 — In Progress!**
