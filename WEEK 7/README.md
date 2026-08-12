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
5. **Security & Production Hardening**: Implement API key authentication, token-bucket rate limiting, sandboxed AST math evaluation, and SQLite audit logging.

---

## Directory Structure & Daily Progress

```
WEEK 7/
├── WEEK7DAY1.txt                 # Monday Concept Journal: Protocol Overview, Transports & JSON-RPC
├── lab7_1_first_mcp_server.py    # Lab 7.1: Three-Tool FastMCP Production Server (Calculator, String, Date)
├── test_lab7_1.py                # Automated Verification Suite for Lab 7.1 (17/17 Passed)
└── README.md                     # Master Week 7 Documentation
```

---

## Completed Lab Deliverables

### Lab 7.1: Three-Tool Production MCP Server (`lab7_1_first_mcp_server.py`)
- **Overview**: Production MCP Server built with `FastMCP` exposing 3 safe utility tools:
  1. `calculate(expression)`: Evaluates math expressions safely using Python AST parsing (blocks dangerous code like `os.system` without using unsafe `eval()`).
  2. `string_processor(text, operation)`: Performs text operations (`upper`, `lower`, `reverse`, `word_count`, `snake_case`).
  3. `date_helper(action, date_str, days)`: Handles date utilities (`now`, `add_days`, `diff_days`, `format_date`).
- **Validation**:
  - Run verification suite: `python "WEEK 7\test_lab7_1.py"`
  - **Results**: `17 / 17 Tests Passed (100.0% Pass Rate)`

---

## Quick Start & Running Commands

```powershell
# Activate Environment
cd C:\Users\USER\Desktop\calderr-ai-2026
.\calderr-env\Scripts\Activate.ps1

# Run Lab 7.1 Automated Verification Test Suite
python "WEEK 7\test_lab7_1.py"

# Run Lab 7.1 FastMCP Server
python "WEEK 7\lab7_1_first_mcp_server.py"
```
