# CalderR AI Internship
**Project location:** Desktop/calderr-ai-2026
**Author:** Sohaib Akhlaq
**Status:** Week 1 Day 1 Complete

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
- fastapi, uvicorn, chromadb, sentence-transformers
- httpx, rich, typer, pytest, jupyter, streamlit
- PyTorch 2.5.1

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

## Project Structure

```
Desktop/calderr-ai-2026/
├── calderr-env/                 # Virtual environment (gitignored)
├── .git/                        # Git repository metadata
├── .gitignore                   # Git ignore rules
├── .env                         # Environment variables (gitignored)
├── .env.template                # Environment variable template
├── requirements.txt             # Python dependencies
├── main.py                      # Main application entry point
├── test_setup.py                # Week 0 verification script
├── test_env.py                  # API key verification
├── test_groq.py                 # Day 2 first LLM call
├── test_groq_stream.py          # Day 2 streaming example
├── test_groq_monday.py          # Week 1 Day 1 model testing
├── temperature_experiment.py    # Week 1 Day 1 temperature testing
├── cli_chatbot.py               # Week 1 Day 1 CLI chatbot
├── week1day1.txt                # Week 1 Day 1 notes
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
| Day 2 | Agentic AI Concepts | ⏳ Upcoming |
| Day 3 | LangChain Core | ⏳ Upcoming |
| Day 4 | Prompt Engineering | ⏳ Upcoming |
| Day 5 | Integration & Demo | ⏳ Upcoming |
