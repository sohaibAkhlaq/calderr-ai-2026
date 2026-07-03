# Week 2 — README

**CalderR AI Internship | Week 2: Advanced Prompting, Structured Outputs, Tool Calling, and API Integration**

---

## Overview

Week 2 builds on the foundations of Week 1 by introducing production-grade agentic patterns: chain-of-thought reasoning, Pydantic-validated structured output, multi-tool LLM agents, and robust external API integration with retry logic.

---

## Repository Structure

```
week2/
├── lab2.1_cot_pipeline.py           Day 1 — Chain-of-Thought pipeline
├── lab2.1_cot_prompts.py            Day 1 — Prompting techniques
├── lab2.1_extraction_comparison.py  Day 1 — Structured vs. unstructured comparison
├── lab2.1_structured_extractor.py   Day 2 — Job posting extractor (Pydantic)
├── lab2.1_pydantic_models.py        Day 2 — Five Pydantic models
├── lab2.2_multi_tool_agent.py       Day 3 — 5-tool agent with routing
├── lab2.2_tool_calling_demo.py      Day 3 — Tool calling demonstrations
├── lab2.3_external_api_tools.py     Day 4 — External APIs + retry + fallbacks
├── project2_i_c_api_aggregator.py   Day 5 — Intermediate Project (CLI)
├── project2_p_c_financial_analysis.py  Day 5 — Production Project (Streamlit)
├── week2_assessment.md              Weekly assessment Q&A
└── README.md                        This file
```

---

## Projects

### Project 2-I-C: API Aggregator Agent (Intermediate)

A command-line agent that pulls data from three public APIs **in parallel** and synthesises a financial morning briefing report.

**Architecture:**
```
asyncio.gather
    -> Weather (Open-Meteo, free)
    -> Financial News (GNews, free fallback)
    -> Currency Rates (exchangerate-api, free)
DataAggregator -> BriefingReport (Pydantic)
    -> ReportSynthesizer (Groq LLM, CoT prompt)
    -> ReportFormatter (Markdown + HTML output)
```

**Run:**
```bash
python week2/project2_i_c_api_aggregator.py
```

**Output:**
- `report_<timestamp>.md`
- `report_<timestamp>.html`

---

### Project 2-P-C: Financial Data Analysis Agent (Production)

A Streamlit web application for natural-language analysis of financial CSV data.

**Architecture:**
```
CSV Upload
    -> Dataset Profiler (Pydantic ColumnSchema)
    -> Tool Selector (keyword routing, 5 tools)
    -> Code Generator (Groq LLM, CoT prompt)
    -> Code Executor (subprocess sandbox)
    -> Chart Builder (Plotly)
    -> Report Builder (Groq LLM, CoT prompt)
    -> AnalysisResult (Pydantic structured output)
    -> Download buttons (Markdown, Python, JSON)
```

**Run locally:**
```bash
streamlit run week2/project2_p_c_financial_analysis.py
```

**Deploy to Streamlit Cloud:**
1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Connect the GitHub repository.
4. Set **Main file path:** `week2/project2_p_c_financial_analysis.py`
5. Add `GROQ_API_KEY` under **Advanced Settings > Secrets**.
6. Deploy.

---

## Setup

### Prerequisites

- Python 3.11+
- Groq API key

### Installation

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# or
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

---

## Week 2 Learning Outcomes

| Day | Topic | Key Concepts |
|---|---|---|
| 1 | Advanced Prompting | Chain-of-Thought, Tree-of-Thought, Self-Consistency, Meta-Prompting |
| 2 | Structured Outputs | Pydantic v2, PydanticOutputParser, field validators, model validators |
| 3 | Tool Calling Basics | Tool registry, keyword routing, 5-tool agent, conversation history |
| 4 | External API Tools | Exponential backoff, retry logic, fallback chains, error recovery |
| 5 | Integration | Parallel async calls, Streamlit deployment, end-to-end agent pipelines |

---

## Technologies Used

| Library | Purpose |
|---|---|
| `langchain-groq` | LLM inference via Groq |
| `langchain-core` | Prompts, output parsers, tool decorators |
| `pydantic` | Structured data schemas and validation |
| `streamlit` | Production web interface |
| `plotly` | Interactive financial charts |
| `httpx` | Async HTTP client for API calls |
| `asyncio` | Parallel tool execution |
| `rich` | Terminal formatting |
| `pandas` | Data manipulation |

---

## API Sources (All Free, No Key Required by Default)

| API | Endpoint | Purpose |
|---|---|---|
| Open-Meteo | `api.open-meteo.com` | Current weather |
| exchangerate-api | `api.exchangerate-api.com` | USD exchange rates |
| GNews | `gnews.io/api/v4` | Financial news (falls back to mock data) |
