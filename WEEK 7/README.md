# Week 7: Model Context Protocol (MCP), Agent Protocols & Tool Ecosystems

---

## Executive Overview
Weeks 1–6 built AI agents that reason, retrieve, remember, and coordinate. **Week 7** connects agents to the outside world at scale through standard open protocols. The **Model Context Protocol (MCP)**, published by Anthropic in 2024, is the open industry standard for how AI agents discover, authenticate, and execute external tools, read resources, and invoke structured prompt templates.

By decoupling tool implementation from agent framework logic, MCP enables tools built once to be consumed seamlessly by Claude Desktop, LangChain, LangGraph, AutoGen, and any custom AI system.

---

## Key Learning Objectives & Themes
1. **MCP Primitives**: Master Tools, Resources, and Prompts.
2. **Transport Layer Engineering**: Understand stdio (local high-performance desktop transport) vs HTTP+SSE (remote, containerized production microservice transport).
3. **FastMCP Server Development**: Build production FastMCP servers with JSON Schema validation and structured error handling.
4. **Agent Integration & Gateways**: Connect MCP tool providers to LangChain / LangGraph agents and build composable tool gateways with namespace routing.
5. **Security & Production Hardening**: Implement API key authentication, token-bucket rate limiting, sandboxed AST math evaluation, per-endpoint quotas, and SQLite audit logging.

---

## Directory Structure & Daily Progress

```
WEEK 7/
├── WEEK7DAY1.txt                 # Monday Concept Journal: Protocol Overview, Transports & JSON-RPC
├── lab7_1_first_mcp_server.py    # Lab 7.1: Three-Tool FastMCP Production Server (Calculator, String, Date)
├── test_lab7_1.py                # Automated Verification Suite for Lab 7.1 (17/17 Passed)
│
├── WEEK7DAY2.txt                 # Tuesday Concept Journal: Tools, Resources, Prompts, Auth & Audit Logs
├── lab7_2_database_mcp.py        # Lab 7.2: Authenticated MCP Server with Rate Limiting & SQLite Audit Log
├── test_lab7_2.py                # Automated Verification Suite for Lab 7.2 (14/14 Passed)
│
├── WEEK7DAY3.txt                 # Wednesday Concept Journal: MCP + LangGraph Integration & Gateway Architecture
├── lab7_3_mcp_gateway.py         # Lab 7.3: MCP Gateway with Tool Namespace Routing (fs:, db:, util:) & Schema Cache
├── lab7_3_composite_agent.py     # Lab 7.3: LangGraph Composite Agent executing multi-step workflow via Gateway
├── test_lab7_3.py                # Automated Verification Suite for Lab 7.3 (12/12 Passed)
│
├── WEEK7DAY4.txt                 # Thursday Concept Journal: Security, OWASP Guidelines & Public API MCP Wrappers
├── lab7_4_public_api_mcp.py      # Lab 7.4: Hardened Public API MCP Server (GitHub Intelligence Wrapper)
├── Dockerfile.lab7_4             # Docker Containerization for Lab 7.4 HTTP+SSE MCP Server
├── test_lab7_4.py                # Automated Verification Suite for Lab 7.4 (8/8 Passed)
│
├── WEEK7DAY5.txt                 # Friday Concept Journal: Standup Requirements & Weekly Assessment Q&A (All 6 Answered)
├── lab7_5_standup_demo.py        # Lab 7.5: Automated Friday Standup Live Demo & Failure Resilience Suite
└── README.md                     # Master Week 7 Documentation
```

---

## Completed Lab Deliverables

### 1. Lab 7.1: Three-Tool Production MCP Server (`lab7_1_first_mcp_server.py`)
- **Overview**: Production MCP Server built with `FastMCP` exposing 3 safe utility tools:
  1. `calculate(expression)`: Evaluates math expressions safely using Python AST parsing (blocks dangerous code without using unsafe `eval()`).
  2. `string_processor(text, operation)`: Performs text operations (`upper`, `lower`, `reverse`, `word_count`, `snake_case`).
  3. `date_helper(action, date_str, days)`: Handles date utilities (`now`, `add_days`, `diff_days`, `format_date`).
- **Validation**: `python "WEEK 7\test_lab7_1.py"` $\rightarrow$ **`17 / 17 Tests Passed (100.0%)`**

### 2. Lab 7.2: Authenticated Production MCP Server with Audit Log (`lab7_2_database_mcp.py`)
- **Overview**: Production-hardened MCP Server supporting authentication, token-bucket rate limiting, and structured SQLite audit logging:
  1. **Authentication**: Bearer API Key validation (`key_alpha_123`, `key_beta_999`). Rejects unauthorized requests with 401.
  2. **Token Bucket Rate Limiting**: Maximum 10 requests / 60 seconds per API key. Returns 429 when exceeded.
  3. **SQLite Audit Store**: Records `timestamp`, `api_key_hash`, `tool_name`, `status`, and `latency_ms` to `data/mcp_audit.db`.
  4. **Database Tools**: `describe_schema`, `query_table`, `insert_record`.
  5. **Filesystem Tools**: `write_file`, `read_file`, `list_directory` (sandboxed inside `data/sandbox`).
  6. **Resource URIs**: `resource://sandbox/files`, `resource://db/schema`.
  7. **Prompt Templates**: `file_summarization`, `database_report`.
- **Validation**: `python "WEEK 7\test_lab7_2.py"` $\rightarrow$ **`14 / 14 Tests Passed (100.0%)`**

### 3. Lab 7.3: MCP Gateway with Tool Namespace Routing (`lab7_3_mcp_gateway.py` & `lab7_3_composite_agent.py`)
- **Overview**: Enterprise MCP Gateway proxying requests across 3 downstream tool servers:
  1. **Tool Namespace Routing**: Namespaces tools by server prefix (`fs:*`, `db:*`, `util:*`). Strips prefix and routes to downstream servers.
  2. **60-Second Schema Caching**: Caches tool discovery schemas to eliminate redundant discovery round-trips.
  3. **Aggregated Health Monitoring (`/health`)**: Polls and aggregates server status (`HEALTHY`, `DEGRADED`, `UNHEALTHY`).
  4. **Graceful Failure Handling**: Safely rejects calls targeting offline downstream servers (`ServerOfflineError`).
  5. **Composite LangGraph Agent (`lab7_3_composite_agent.py`)**: Executes 4-step workflow through Gateway (Read specs $\rightarrow$ Query DB $\rightarrow$ Calculate budget & string formatting $\rightarrow$ Write executive report to disk).
- **Validation**: `python "WEEK 7\test_lab7_3.py"` $\rightarrow$ **`12 / 12 Tests Passed (100.0%)`**

### 4. Lab 7.4: Production Hardened Public API MCP Server (`lab7_4_public_api_mcp.py` & `Dockerfile.lab7_4`)
- **Overview**: Security-hardened MCP server wrapping the GitHub Developer Intelligence Public API:
  1. **Header Authentication**: Validates authorized developer keys (`gh_key_alpha`, `gh_key_beta`).
  2. **Per-Endpoint Quotas**: Enforces specific rate limits per tool (e.g. 5 calls/min for expensive code searches, 10 calls/min for repository info).
  3. **Tools Exposed**: `get_repo_info`, `search_github_code`, `get_user_profile`, `analyze_repo_health`.
  4. **Security Audit Log**: Persists all access logs to `data/mcp_security_audit.db`.
  5. **Docker Containerization**: Includes `Dockerfile.lab7_4` for containerized HTTP+SSE deployment.
- **Validation**: `python "WEEK 7\test_lab7_4.py"` $\rightarrow$ **`8 / 8 Tests Passed (100.0%)`**

### 5. Lab 7.5: Automated Friday Standup Live Demonstration & Ecosystem Failure Resilience Suite (`lab7_5_standup_demo.py`)
- **Overview**: Live automated demonstration suite fulfilling all 5 Friday Standup Requirements:
  1. **Ecosystem Architecture Review**: Full diagram printout.
  2. **Live Tool Discovery**: Discovers 9 tools across `fs:`, `db:`, and `util:` namespaces.
  3. **Schema Walkthrough**: Validates JSON Schema definitions.
  4. **Security Walkthrough**: Live demo of 401 Auth Rejection, 429 Rate Limit Firing, and SQLite Audit Store verification.
  5. **Downstream Failure Demonstration**: Simulates Database Server failure (`OFFLINE`); Gateway catches condition gracefully (`DEGRADED` status) without agent crash, then recovers (`HEALTHY`).
  6. **Multi-Step Composite Agent Execution**: Completes 4-step workflow.
- **Validation**: `python "WEEK 7\lab7_5_standup_demo.py"` $\rightarrow$ **`Completed Successfully`**

---

## Quick Start & Running Commands

```powershell
# Activate Environment
cd C:\Users\USER\Desktop\calderr-ai-2026
.\calderr-env\Scripts\Activate.ps1

# Run All Lab Verification Test Suites (Labs 7.1, 7.2, 7.3, 7.4)
python "WEEK 7\test_lab7_1.py"
python "WEEK 7\test_lab7_2.py"
python "WEEK 7\test_lab7_3.py"
python "WEEK 7\test_lab7_4.py"

# Run Friday Standup Live Ecosystem Demonstration & Failure Resilience Suite
python "WEEK 7\lab7_5_standup_demo.py"
```
