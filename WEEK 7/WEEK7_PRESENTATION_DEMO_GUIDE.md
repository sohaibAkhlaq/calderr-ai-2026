# CALDER AGENTIC AI ENGINEERING WEEK 7: TEAM LEAD PRESENTATION & DEMO SCRIPT

---

## SECTION 1: WEEK 7 CORE CONCEPTS & INTERVIEW DEFENSE

Use this section to confidently answer any technical questions your Team Lead asks about Week 7 Model Context Protocol (MCP) concepts, protocol mechanics, security, and architecture.

---

### 1. Model Context Protocol (MCP) Overview
- **Definition:** MCP is an open-standard architecture published by Anthropic (2024) that standardizes how AI agents discover, authenticate, and execute external tools, read data resources, and invoke prompt templates.
- **Why It Matters:** Before MCP, every framework (LangChain, AutoGen, OpenAI) reinvented function calling. MCP decouples tool implementation from agent framework logic. A tool built once inside an MCP server works across Claude Desktop, LangChain agents, LangGraph workflows, and future AI clients without code modification.
- **Where Used in Projects:**
  - **Intermediate Project:** Exposed via 3 FastMCP servers (`code_intel_server.py`, `github_mcp_server.py`, `doc_mcp_server.py`).
  - **Production Project:** Exposed via 5 FastMCP servers (`fs_mcp_server.py`, `db_mcp_server.py`, `comm_mcp_server.py`, `analytics_mcp_server.py`, `code_intel_mcp_server.py`).

---

### 2. The Three MCP Primitives (Tools, Resources, Prompts)
- **i. Tools (Executable Actions):**
  - **Definition:** Callable functions that perform side-effecting actions or compute outputs.
  - **Example:** `db:query_table(table_name, limit)`, `fs:write_file(filename, content)`.
  - **Where Used:** Used across all servers in both Intermediate and Production projects.
- **ii. Resources (Read-Only Data URIs):**
  - **Definition:** Browsable data endpoints exposed as URI schemes (`resource://...` or `file://...`).
  - **Example:** `resource://sandbox/files`, `resource://db/schema`.
  - **Where Used:** Implemented in `WEEK 7/lab7_2_database_mcp.py` for read-only schema and file browsing.
- **iii. Prompts (Structured Workflow Templates):**
  - **Definition:** Pre-configured prompt templates returned by the server to guide agent workflows.
  - **Example:** `file_summarization(filename)`, `database_report(table_name)`.
  - **Where Used:** Implemented in `WEEK 7/lab7_2_database_mcp.py`.

---

### 3. Transport Layers: `stdio` vs `HTTP + SSE`
- **stdio (Standard Input / Output):**
  - Communication occurs over standard OS process streams (`stdin`/`stdout`).
  - **Use Case:** Local desktop integration (e.g. Claude Desktop app on developer machine).
  - **Tradeoffs:** Zero network latency, fast, process-isolated. Cannot be accessed remotely.
- **HTTP + Server-Sent Events (SSE):**
  - Communication over HTTP POST (`/messages`) with persistent SSE streaming (`GET /sse`).
  - **Use Case:** Production cloud microservices, Docker containers, multi-tenant enterprise tool hubs.
  - **Tradeoffs:** Network-accessible, containerizable, load-balancable. Requires API keys and rate limiting.
- **Where Used in Projects:** Configured in `Dockerfile.lab7_4` and `WEEK 7/production_project/Dockerfile.hub`.

---

### 4. Enterprise MCP Gateway Pattern & Namespace Routing
- **Definition:** An architectural pattern where a single proxy gateway presents a unified tool interface to external agents while routing calls to multiple downstream tool servers.
- **Namespace Routing:** Prevents tool name collisions across servers by prefixing tool names:
  - `code:*` $\rightarrow$ Code Intelligence Server
  - `gh:*` $\rightarrow$ GitHub Server
  - `doc:*` $\rightarrow$ Documentation Server
  - `fs:*` $\rightarrow$ Filesystem Server
  - `db:*` $\rightarrow$ Database Server
  - `comm:*` $\rightarrow$ Communication Server
  - `analytics:*` $\rightarrow$ Analytics Server
- **60-Second Schema Caching:** Gateway caches downstream tool schemas for 60 seconds (TTL) to avoid redundant network discovery overhead.
- **Where Used in Projects:**
  - `WEEK 7/intermediate_project/dev_gateway.py` (3 downstream servers).
  - `WEEK 7/production_project/hub_gateway.py` (5 downstream servers).

---

### 5. Security Engineering: Per-Tenant RBAC & Rate Limiting
- **i. Per-Tenant Role-Based Access Control (RBAC):**
  - Restricts namespace permissions per API key.
  - **Example:** `Tenant_Alpha` is granted `['fs', 'db', 'code', 'analytics']`. Attempting `comm:draft_email` returns **`403 Forbidden: Tenant_Alpha is not authorized to call namespace comm:*`**.
- **ii. Token-Bucket Rate Limiting:**
  - Limits call velocity per key (e.g. 60 or 100 calls/min). Excess requests return **`429 Rate Limit Exceeded`**.
- **iii. SQLite Security Audit Store:**
  - Immutably records every tool call (`timestamp`, `tenant_id`, `key_hash`, `tool_name`, `status`, `latency_ms`).
- **Where Used in Projects:**
  - Intermediate Project: `dev_gateway.py` (`data/dev_suite_audit.db`).
  - Production Project: `hub_gateway.py` (`data/enterprise_hub_audit.db`).

---

## SECTION 2: LIVE PRESENTATION & DEMO SCRIPT

When your Team Lead asks for a demo, follow this exact step-by-step presentation script.

---

### PART A: INTERMEDIATE PROJECT DEMO (Developer Productivity MCP Suite)

#### 📍 Step A1: Launch the Intermediate Project App
Open PowerShell and start the Streamlit web app:
```powershell
cd C:\Users\USER\Desktop\calderr-ai-2026
.\calderr-env\Scripts\Activate.ps1
streamlit run "WEEK 7\intermediate_project\app.py"
```
*App opens at `http://localhost:8501`.*

#### 🗣️ What to Say to Your Lead:
> *"Hi! I'd like to present the Week 7 Intermediate Project: Developer Productivity MCP Suite. Before MCP, developer tools were fragmented—developers had to switch between IDEs, GitHub diff pages, complexity analyzers, and docstring generators. We unified three independent FastMCP servers behind an MCP Gateway with namespace routing: Code Intelligence (`code:`), GitHub (`gh:`), and Documentation (`doc:`)."*

---

#### 📍 Step A2: Show Tab 1 — Autonomous PR Reviewer
1. Select **Pull Request #101** (*Refactor User Authentication & Password Hashing*).
2. Click **`🚀 Run Autonomous PR Review Workflow`**.

#### 🗣️ What to Say to Your Lead:
> *"Here in Tab 1, our LangGraph Autonomous Developer Agent connects to the Gateway and executes a 6-step PR code review workflow:*
> 1. *It fetches the PR code diff from `gh:get_pr_diff`.*
> 2. *It runs AST parsing and calculates Cyclomatic Complexity (`code:analyze_file`).*
> 3. *It maps import dependencies (`code:find_dependencies`).*
> 4. *It scans for architectural code smells (`code:detect_code_smells`).*
> 5. *It synthesizes a Google-style docstring (`doc:generate_docstring`).*
> 6. *It registers an automated code review ticket on GitHub (`gh:create_issue`).*
> *Notice how the agent achieved a 100/100 Quality Score and created Issue Ticket #501 automatically."*

---

#### 📍 Step A3: Show Tab 5 — 100% Automated Test Suite
1. Click **`🧪 Automated Test Suite`** (Tab 5).
2. Click **`🚀 Run Full Test Suite`**.

#### 🗣️ What to Say to Your Lead:
> *"In Tab 5, we have a 1-click verification test suite testing tool discovery, 401 auth rejection, AST complexity scoring, PR diff parsing, Google docstring generation, and agent workflow execution. As you can see, we achieved a 100.0% Pass Rate (8/8 Tests Passed)."*

---

### PART B: PRODUCTION PROJECT DEMO (Universal Enterprise Tool Hub)

#### 📍 Step B1: Launch the Production Project App
Open PowerShell and start the Streamlit Enterprise Dashboard:
```powershell
cd C:\Users\USER\Desktop\calderr-ai-2026
.\calderr-env\Scripts\Activate.ps1
streamlit run "WEEK 7\production_project\app.py"
```
*App opens at `http://localhost:8501`.*

#### 🗣️ What to Say to Your Lead:
> *"Now I'd like to present the Week 7 Production Project: Universal Enterprise Tool Hub. In production enterprise AI, connecting AI agents to 20 different tool integrations creates architectural chaos. Our Universal Tool Hub hosts 5 specialized MCP servers—Filesystem (`fs:`), Database (`db:`), Communication (`comm:`), Analytics (`analytics:`), and Code Intelligence (`code:`)—behind a single MCP Gateway with Per-Tenant RBAC Security."*

---

#### 📍 Step B2: Show Panel 1 — Multi-Server Enterprise Workflow
1. Stay on **`🏛️ Ecosystem Overview`** (Panel 1).
2. Click **`🚀 Run LangGraph Multi-Server Workflow (5 Servers)`**.

#### 🗣️ What to Say to Your Lead:
> *"In Panel 1, our LangGraph Enterprise Agent connects to the single Gateway endpoint and executes 5 distinct workflows across all 5 downstream servers:*
> - *Workflow 1: Seeding & reading project specs (`fs:write_file` & `fs:read_file`).*
> - *Workflow 2: Querying enterprise account balances (`db:query_table`).*
> - *Workflow 3: Computing revenue metrics summary (`analytics:compute_statistics`).*
> - *Workflow 4: Running AST code complexity analysis (`code:analyze_file`).*
> - *Workflow 5: Drafting executive strategy email (`comm:draft_email`)."*

---

#### 📍 Step B3: Show Panel 2 — Per-Tenant RBAC Security Inspector
1. Switch to **`🔒 Tenant RBAC Inspector`** (Panel 2).
2. In the sidebar, select **`Tenant_Alpha (key_tenant_alpha)`**.
3. Select tool **`comm:draft_email`** and click **`🔒 Test Access Permission`**.
4. Point out the red **`403 FORBIDDEN`** badge.
5. In the sidebar, switch to **`Enterprise_Admin (key_enterprise_admin)`** and re-test **`comm:draft_email`**. Point out **`200 OK ACCESS GRANTED`**.

#### 🗣️ What to Say to Your Lead:
> *"Security is critical in enterprise MCP deployments. In Panel 2, we demonstrate Per-Tenant RBAC enforcement. Tenant_Alpha is authorized for `fs`, `db`, `code`, and `analytics`, but NOT `comm`. When Tenant_Alpha attempts to call `comm:draft_email`, the Gateway blocks it with 403 Forbidden. Switching to Enterprise_Admin grants full access."*

---

#### 📍 Step B4: Show Panel 5 — 50 Concurrent Tool Calls Load Benchmark
1. Switch to **`⚡ Load Test Benchmark`** (Panel 5).
2. Click **`🚀 Run 50 Concurrent Calls Benchmark`**.

#### 🗣️ What to Say to Your Lead:
> *"To prove production engineering rigor, Panel 5 runs a high-concurrency load benchmark simulating 50 concurrent tool calls across all 5 servers. As you can see, we achieved a 100.0% Success Rate (50/50 Calls) with a 95th Percentile Latency of ~580ms, well under our 2.0-second SLA target."*

---

#### 📍 Step B5: Show Panel 6 — Automated Verification Test Suite
1. Switch to **`🧪 Automated Test Suite`** (Panel 6).
2. Click **`🚀 Run All Platform Tests`**.

#### 🗣️ What to Say to Your Lead:
> *"Finally, Panel 6 runs our automated platform verification suite covering 5-server tool discovery, RBAC isolation, 401 auth rejection, 429 rate limiting, SQLite security audit logging, and load testing. All 8/8 tests pass with 100% Pass Rate."*

---

## SUMMARY CHEAT SHEET FOR LEADS

| Topic | Quick Key Answer |
|---|---|
| **What is MCP?** | Open Anthropic protocol standardizing how AI agents call tools, read resources, and invoke prompts across frameworks. |
| **Why Gateway?** | Unifies multiple MCP servers behind 1 endpoint with namespace routing (`fs:`, `db:`, `comm:`) and schema caching. |
| **How is Auth handled?** | Bearer API Key validation mapped to Per-Tenant RBAC namespaces. Unauthorized calls return `403 Forbidden`. |
| **Rate Limiting?** | In-memory Token-Bucket algorithm (60 or 100 calls/min per key). Excess calls return `429 Rate Limit Exceeded`. |
| **Audit Logging?** | SQLite audit store (`enterprise_hub_audit.db`) logging timestamp, tenant_id, key hash, tool, status, and latency. |
| **Load Benchmark?** | 50 concurrent tool calls executed in ~0.8s, 95th percentile latency ~580ms (< 2.0s target). |
