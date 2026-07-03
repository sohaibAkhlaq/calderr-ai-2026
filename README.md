# CalderR AI Internship

**Project Location:** `Desktop/calderr-ai-2026`  
**Author:** Sohaib Akhlaq  
**Status:** Week 2 Complete

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

# All Week 1 and Week 2 scripts are now available.
# No extra installs needed — streamlit, plotly, httpx, etc. all included.
```

After activation, run any project with a single command:

```powershell
# Week 1: Professional Chatbot
python week1/professional_chatbot.py

# Week 2: API Aggregator Agent (CLI)
python week2/project2_i_c_api_aggregator.py

# Week 2: Financial Data Analysis Agent (Streamlit)
python -m streamlit run week2/project2_p_c_financial_analysis.py
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

## Labs Completed

| Lab | Week | Description | Status |
|---|---|---|---|
| Lab 1.1 | 1 | Groq CLI chatbot with history, `/clear`, `/exit` | Complete |
| Lab 1.2 | 1 | Manual ReAct agent with search, calculate, time tools | Complete |
| Lab 1.3 | 1 | Prompt A/B testing with five system prompts | Complete |
| Lab 2.1 | 2 | Structured output extractor (Pydantic job posting parser) | Complete |
| Lab 2.2 | 2 | Multi-tool research agent with 5 tools + routing | Complete |
| Lab 2.3 | 2 | Error recovery agent with real APIs + retry + fallbacks | Complete |

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
