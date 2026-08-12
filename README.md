# CalderR AI Internship

**Project Location:** `Desktop/calderr-ai-2026`  
**Author:** Sohaib Akhlaq  
**Status:** Week 7 Fully Complete (Weeks 1 through 7 Completed)
 
---

## Executive Overview

This repository documents the complete setup, learning progress, and hands-on implementations completed during the CalderR AI internship (2026). It covers environment configuration, foundational AI concepts, agentic systems, LangChain workflows, prompt engineering experiments, structured outputs, tool calling, external API integration, RAG architectures, LangGraph agent workflows, multi-agent teams, persistent memory architectures, knowledge graphs, Model Context Protocol (MCP) ecosystems, and fully deployed production AI platforms.

---

## Project Goals

- Work with large language models via APIs (Groq, HuggingFace, sentence-transformers, FastMCP)
- Master agentic AI design patterns (ReAct, Chain-of-Thought, Supervisor, Peer-to-Peer, Hierarchical Teams)
- Implement advanced retrieval architectures (Vector RAG, BM25 Hybrid Search, Re-ranking, GraphRAG)
- Construct persistent multi-layer agent memory (Working, Episodic, Semantic, Procedural)
- Build knowledge graphs with NetworkX and query them using natural language traversals
- Develop standardized **Model Context Protocol (MCP)** tool servers, gateway proxies, and client agents
- Create reusable, production-ready documentation and deploy full-stack applications (Streamlit, FastAPI, Docker Compose)

---

## Quick Start — Running Week 7 Projects

```powershell
# Activate the environment
cd C:\Users\USER\Desktop\calderr-ai-2026
.\calderr-env\Scripts\Activate.ps1
```

### 1️⃣ Week 7 Intermediate Project (Project 7-I-A: Developer Productivity MCP Suite)
```powershell
# 1. Run Automated Test Suite
python "WEEK 7\intermediate_project\test_dev_suite.py"

# 2. Run Autonomous LangGraph Developer Agent
python "WEEK 7\intermediate_project\langgraph_dev_agent.py"

# 3. Launch Streamlit Web Application
streamlit run "WEEK 7\intermediate_project\app.py"
```
- Open `http://localhost:8501` in your browser.
- Run autonomous PR code reviews, AST cyclomatic complexity analysis, and Google docstring generation.

### 2️⃣ Week 7 Production Project (Project 7-P-A: Universal Enterprise Tool Hub)
```powershell
# 1. Run Automated Test Suite & 50 Concurrent Calls Load Test Benchmark
python "WEEK 7\production_project\test_production_hub.py"

# 2. Run LangGraph Multi-Server Enterprise Agent
python "WEEK 7\production_project\langgraph_hub_agent.py"

# 3. Launch Streamlit Observability Dashboard
streamlit run "WEEK 7\production_project\app.py"

# 4. Single-Command Multi-Container Docker Deployment
docker-compose -f "WEEK 7\production_project\docker-compose.yml" up --build
```
- Open Streamlit Enterprise Dashboard: `http://localhost:8501`.
- Open Gateway REST Proxy: `http://localhost:8000`.

---

## Environment Summary

- **Python:** 3.11.9
- **Virtual environment:** `calderr-env`
- **Git:** Configured & Connected to GitHub (`sohaibAkhlaq/calderr-ai-2026`)

### Installed Libraries

| Category | Packages |
|---|---|
| LLM & Protocols | FastMCP, MCP Python SDK, LangChain, LangChain-Groq, LangChain-Community, LangGraph, Groq |
| Memory & Graphs | SQLite, Pure-Python Vector Engine, NetworkX, sentence-transformers |
| Multi-Agent | Pydantic v2, TypedDict, asyncio, custom message bus |
| Data | Pandas, NumPy, Plotly, Pyvis |
| Web & API | Streamlit, FastAPI, Uvicorn, HTTPX |
| Terminal | Rich, Typer |
| Testing & DevOps | PyTest, Docker, Docker Compose |

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
├── week2/                        # Week 2: Advanced AI Patterns & Tool Integration
├── WEEK 3/                       # Week 3: Embeddings, RAG & Vector Databases
├── Week 4/                       # Week 4: LangGraph & Stateful Agent Workflows
├── WEEK 5/                       # Week 5: Multi-Agent Systems & Team Architectures
├── WEEK 6/                       # Week 6: Memory Systems & Knowledge Graphs
│
└── WEEK 7/                       # Week 7: MCP, Agent Protocols & Tool Ecosystems
    ├── README.md                          # Full Week 7 Master Documentation
    ├── WEEK7DAY1.txt ... WEEK7DAY5.txt    # Mon-Fri Daily Learning Concept Journals
    ├── lab7_1_first_mcp_server.py         # Lab 7.1: Three-Tool FastMCP Server (17/17 Passed)
    ├── lab7_2_database_mcp.py             # Lab 7.2: Authenticated MCP Server + Audit Log (14/14 Passed)
    ├── lab7_3_mcp_gateway.py              # Lab 7.3: MCP Gateway with Namespace Routing (12/12 Passed)
    ├── lab7_3_composite_agent.py          # Lab 7.3: LangGraph Composite Agent
    ├── lab7_4_public_api_mcp.py           # Lab 7.4: Hardened Public GitHub API MCP Server (8/8 Passed)
    ├── Dockerfile.lab7_4                  # Lab 7.4 Dockerfile
    ├── lab7_5_standup_demo.py             # Lab 7.5: Automated Friday Standup Live Demo
    │
    ├── intermediate_project/              # Project 7-I-A: Developer Productivity MCP Suite (Streamlit + LangGraph)
    └── production_project/                # Project 7-P-A: Universal Enterprise Tool Hub (5 Servers + Gateway + Docker)
```

---

## Week 7 — MCP, Agent Protocols & Tool Ecosystems Highlights

| Project / Deliverable | Type | Features & Status | Key Files |
|---|---|---|---|
| **Lab 7.1** | Lab | Three-Tool FastMCP Production Server (Safe AST Math, String, Date) | `WEEK 7/lab7_1_first_mcp_server.py` |
| **Lab 7.2** | Lab | Authenticated MCP Server with Token-Bucket Rate Limiting (429) & SQLite Audit | `WEEK 7/lab7_2_database_mcp.py` |
| **Lab 7.3** | Lab | MCP Gateway with Tool Namespace Routing (`fs:`, `db:`, `util:`), 60s Cache & LangGraph Agent | `WEEK 7/lab7_3_mcp_gateway.py` |
| **Lab 7.4** | Lab | Production Hardened Public GitHub API MCP Server + Dockerfile | `WEEK 7/lab7_4_public_api_mcp.py` |
| **Lab 7.5** | Lab | Friday Standup Demonstration & Downstream Server Failure Resilience Suite | `WEEK 7/lab7_5_standup_demo.py` |
| **Project 7-I-A** | Intermediate | **Developer Productivity MCP Suite** (3 MCP Servers, Gateway, LangGraph DevAgent, 5-Panel Streamlit UI, Claude Desktop Config) | `WEEK 7/intermediate_project/` |
| **Project 7-P-A** | Production | **Universal Enterprise Tool Hub** (5 MCP Servers, Gateway, Per-Tenant RBAC, 6-Panel Streamlit Dashboard, 50 Concurrent Calls Benchmark, Docker Compose) | `WEEK 7/production_project/` |

---

## Complete Labs Matrix (Weeks 1–7)

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
| Lab 7.1 | 7 | Three-tool production MCP server with FastMCP | Complete |
| Lab 7.2 | 7 | Authenticated MCP server with token-bucket rate limiting & audit logging | Complete |
| Lab 7.3 | 7 | MCP gateway with tool namespace routing & 60s schema caching | Complete |
| Lab 7.4 | 7 | Hardened public GitHub API wrapper MCP server & Docker container | Complete |
| Lab 7.5 | 7 | Friday standup live ecosystem demonstration & failure resilience suite | Complete |

---

## GitHub Repository

[https://github.com/sohaibAkhlaq/calderr-ai-2026](https://github.com/sohaibAkhlaq/calderr-ai-2026)
