# CalderR AI Internship

Project Location: Desktop/calderr-ai-2026  
Author: Sohaib Akhlaq  
Status: Week 1 Day 4 Complete

---

## Overview

This repository documents the complete setup, learning progress, and hands-on implementation completed during the CalderR AI internship. It includes environment configuration, foundational AI concepts, agentic systems, LangChain workflows, and prompt engineering experiments.

---

## Project Goals

The objective of this project is to build practical experience in:

- Working with large language models through APIs
- Understanding agentic AI design patterns
- Building simple LLM-based applications with Python
- Exploring prompt engineering and persona-driven prompting
- Creating reusable, readable project documentation

---

## Week 0: Environment Setup

### Environment Summary

- Python 3.11.9
- Virtual environment: calderr-env
- pip upgraded to the latest version
- Git configured with SSH authentication

### Installed Tools and Libraries

- LangChain, LangChain Groq, LangChain Community, LangGraph
- Groq, OpenAI, Pydantic, python-dotenv
- FastAPI, Uvicorn, ChromaDB
- HTTPX, Rich, Typer, PyTest, Jupyter, Streamlit
- PyTorch 2.12.1 (CPU-only for Windows compatibility)
- rank-bm25 for keyword-based retrieval

### Development Environment

- Docker Desktop installed and configured
- VS Code configured with Python, Pylance, and Jupyter support

---

## Week 1: AI Fundamentals

### Day 1 — LLM Foundations

Status: ✅ Completed

Topics covered:
- Transformer architecture and self-attention
- Tokenization and context windows
- Temperature and sampling behavior
- Training vs inference
- Model comparison using Groq APIs

Implemented files:
- test_groq_monday.py
- temperature_experiment.py
- cli_chatbot.py
- week1day1.txt

Key findings:
- llama-3.1-8b-instant offered the fastest responses for prototyping
- llama-3.3-70b-versatile delivered stronger output quality
- Temperature 0.0 produced deterministic output, while higher values increased creativity

### Day 2 — Agentic AI Concepts

Status: ✅ Completed

Topics covered:
- ReAct pattern: Reasoning + Acting
- Agent loop design
- Reactive vs proactive agents
- Tool use, planning, and memory

Implemented files:
- react_agent.py
- week1day2.txt

Key learning:
- An agent extends a language model by adding decision-making, plans, tools, and actions.

### Day 3 — LangChain Core

Status: ✅ Completed

Topics covered:
- LCEL and the pipe operator
- Runnable, RunnablePassthrough, and RunnableParallel
- RAG workflow fundamentals
- Document loading, chunking, and retrieval
- BM25-based retrieval

Implemented files:
- document_qa_chain.py
- chain_patterns.py
- week1day3.txt

Key learning:
- LangChain enables composable, readable, and production-ready LLM workflows.

### Day 4 — Prompt Engineering

Status: ✅ Completed

Topics covered:
- System prompts and instruction design
- Zero-shot vs few-shot prompting
- Chain-of-thought reasoning principles
- Persona-based prompt design

Implemented files:
- prompt_engineering_lab.py
- persona_agent.py
- weekly_assessment.md

Key learning:
- Prompt design heavily influences clarity, structure, tone, and task performance.

---

## Environment Notes

### PyTorch Windows Compatibility

A Windows-specific PyTorch issue was resolved by reinstalling the CPU-only package from the official PyTorch repository. This also avoided dependency conflicts and allowed the project to remain lightweight and compatible.

### Requirements Files

- requirements-minimal.txt: Lightweight setup for local experimentation
- requirements-windows.txt: Broader Windows-compatible dependency set

---

## Repository Structure

```text
Desktop/calderr-ai-2026/
├── calderr-env/                 # Virtual environment (ignored by Git)
├── .git/                        # Git metadata
├── .gitignore                   # Ignore rules
├── .env                         # Local environment variables
├── .env.template                # Environment variable template
├── requirements.txt             # Main dependency list
├── requirements-minimal.txt     # Minimal dependency setup
├── requirements-windows.txt     # Windows-specific dependency setup
├── main.py                      # Main application entry point
├── test_setup.py                # Week 0 verification script
├── test_env.py                  # API key verification
├── test_groq.py                 # First Groq API test
├── test_groq_stream.py          # Streaming example
├── test_groq_monday.py          # Day 1 model testing
├── temperature_experiment.py    # Temperature experiments
├── cli_chatbot.py               # Day 1 CLI chatbot
├── react_agent.py               # Day 2 manual ReAct agent
├── document_qa_chain.py         # Day 3 document Q&A chain
├── chain_patterns.py            # Day 3 LangChain chain examples
├── prompt_engineering_lab.py    # Day 4 prompt engineering lab
├── persona_agent.py             # Day 4 persona-based agent
├── weekly_assessment.md         # Week 1 assessment
├── week1day1.txt                # Day 1 notes
├── week1day2.txt                # Day 2 notes
├── week1day3.txt                # Day 3 notes
├── notebooks/                   # Jupyter notebooks
├── Dockerfile                   # Docker configuration
├── day1-summary.txt             # Day 1 summary
├── day2-summary.txt             # Day 2 summary
└── README.md                    # Project documentation
```

---

## Quick Start

### Activate the virtual environment

```powershell
.\calderr-env\Scripts\Activate.ps1
```

### Run the examples

```powershell
python main.py
python test_env.py
python test_groq.py
python test_groq_stream.py
python test_groq_monday.py
python temperature_experiment.py
python cli_chatbot.py
python react_agent.py
python document_qa_chain.py
python chain_patterns.py
python prompt_engineering_lab.py
python persona_agent.py
```

### Launch Jupyter Lab

```powershell
jupyter lab
```

### Build and run with Docker

```powershell
docker build -t calderr-ai-2026 .
docker run --rm calderr-ai-2026
```

---

## Security Notes

- Do not commit .env files to version control
- Refer to .env.template for required environment variables
- The Groq free tier allows a limited number of API requests per day

---

## GitHub Repository

https://github.com/sohaibAkhlaq/calderr-ai-2026

---

## Week Progress

| Week/Day | Topic | Status |
|---|---|---|
| Week 0 | Environment Setup | ✅ Complete |
| Day 1 | LLM Foundations | ✅ Complete |
| Day 2 | Agentic AI Concepts | ✅ Complete |
| Day 3 | LangChain Core | ✅ Complete |
| Day 4 | Prompt Engineering | ✅ Complete |
| Day 5 | Integration & Demo | ⏳ Upcoming |
