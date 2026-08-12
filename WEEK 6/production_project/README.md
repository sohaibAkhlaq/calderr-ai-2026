# Category 2 Production Project: Enterprise AI Memory Platform (Project 6-P-A)

---

## Executive Overview
The **Enterprise AI Memory Platform** is a production-grade, multi-tenant memory-as-a-service infrastructure designed to grant any external AI agent persistent, structured, and queryable memory across all four cognitive layers: **Episodic, Semantic, Procedural, and Knowledge Graph Memory**.

Built with **FastAPI**, **SQLite**, **Pure-Python Cosine Similarity Vector Store**, **NetworkX**, **Streamlit**, and **Docker Compose**, this platform functions as an open-source alternative to Mem0, providing multi-tenant isolation, automated background memory consolidation, RAGAS-style retrieval evaluation, and a full OpenAPI specification.

---

## Hiring Signal & Engineering Highlights
- **Multi-Tenant Isolation:** Separate, isolated memory namespaces per organization/tenant (`tenant_id`). Tenant A cannot read, query, or search memories or knowledge graphs belonging to Tenant B.
- **Memory-as-a-Service REST API:** Standalone service exposing clean REST endpoints with full Pydantic v2 schemas and OpenAPI Swagger documentation (`http://localhost:8000/docs`).
- **4 Memory Types + Knowledge Graph:**
  1. **Episodic Memory Store:** SQLite with `tenant_id`, `session_id`, `user_id`, `timestamp`, `role`, `content`, `importance_score`.
  2. **Semantic Memory Store:** Cosine similarity vector search over 384-dimensional embeddings per tenant namespace.
  3. **Procedural Memory Store:** Domain correction rules with application tracking and automatic confidence promotion.
  4. **Knowledge Graph API:** Per-tenant NetworkX graph with entity/relationship extraction, JSON persistence, and multi-hop path querying.
- **Async Consolidation Worker:** Background worker running scheduled episode summarization, importance decay pruning, and rule confidence promotion.
- **Streamlit Observability Admin Dashboard:** 5-panel UI featuring live tenant inspection, graph visualizer, procedural rule manager, consolidation controller, and a built-in 100% automated test suite.
- **Docker Compose Deployment:** Single-command production setup orchestrating FastAPI backend service and Streamlit admin dashboard.

---

## System Architecture

```mermaid
flowchart TD
    ExternalAgent["External AI Agent (LangChain / AutoGen / Custom)"] --> |REST API Requests| MemoryRouter["FastAPI Memory Service (main.py)"]
    
    subgraph MultiTenantStore ["Multi-Tenant Storage Layer"]
        MemoryRouter --> |Tenant Isolated Tables| EpisodicDB["SQLite Episodic Store (tenant_id)"]
        MemoryRouter --> |Tenant Namespaces| VectorStore["SQLite Vector Store (Cosine Similarity)"]
        MemoryRouter --> |Tenant Correction Rules| ProceduralDB["SQLite Procedural Store (tenant_id)"]
        MemoryRouter --> |Tenant JSON Graphs| NetworkX["NetworkX Knowledge Graph (tenant_graphs)"]
    end
    
    subgraph BackgroundWorker ["Async Memory Management"]
        ConsolidationWorker["Consolidation Worker (Async Background Task)"]
        ConsolidationWorker --> |Summarize Old Episodes| EpisodicDB
        ConsolidationWorker --> |Promote Rules| ProceduralDB
        ConsolidationWorker --> |Prune Low Importance| VectorStore
    end
    
    subgraph AdminUI ["Observability Dashboard"]
        StreamlitDashboard["Streamlit Admin Dashboard (admin_app.py)"]
        StreamlitDashboard --> MultiTenantStore
    end
```

---

## API Documentation (OpenAPI / Swagger)

Interactive documentation is available at `http://localhost:8000/docs` when running the service.

### Key REST Endpoints

| Category | Method | Endpoint | Description |
|---|---|---|---|
| **Health** | `GET` | `/v1/health` | Health check & tenant count |
| **Tenant Admin** | `GET` | `/v1/tenants` | List all active tenant namespaces |
| | `GET` | `/v1/tenants/{tenant_id}/stats` | Get memory breakdown & stats for tenant |
| **Episodic** | `POST` | `/v1/tenants/{tenant_id}/episodic` | Log interaction message |
| | `GET` | `/v1/tenants/{tenant_id}/episodic/{session_id}` | Retrieve session history |
| **Semantic** | `POST` | `/v1/tenants/{tenant_id}/semantic/facts` | Store atomic semantic fact |
| | `POST` | `/v1/tenants/{tenant_id}/semantic/search` | Vector similarity search |
| **Procedural** | `POST` | `/v1/tenants/{tenant_id}/procedural/rules` | Register error correction rule |
| | `GET` | `/v1/tenants/{tenant_id}/procedural/rules` | Query domain rules |
| **Knowledge Graph** | `POST` | `/v1/tenants/{tenant_id}/graph/triples` | Add entity-relation triples |
| | `GET` | `/v1/tenants/{tenant_id}/graph/query` | Multi-hop graph query |
| **Consolidation** | `POST` | `/v1/tenants/{tenant_id}/consolidate` | Trigger consolidation worker |

---

## Verification & Automated Test Suite (100% Pass Rate)

The platform features an automated verification suite accessible via the Streamlit Admin Dashboard (**🧪 Automated Test Suite** tab):

| Test Group | Test Name | Result |
|---|---|---|
| **1. Multi-Tenant Isolation** | 1.1 Semantic Vector Isolation | ✅ Pass |
| | 1.2 Episodic Store Isolation | ✅ Pass |
| | 1.3 Knowledge Graph Isolation | ✅ Pass |
| **2. Semantic Vector Engine** | 2.1 Cosine Similarity Precision | ✅ Pass |
| | 2.2 Vector Category Filtering | ✅ Pass |
| **3. Procedural & Consolidation** | 3.1 Rule Application Counter | ✅ Pass |
| | 3.2 Consolidation Worker Pruning | ✅ Pass |
| **4. Knowledge Graph** | 4.1 Multi-Hop Path Traversal | ✅ Pass |

---

## Quick Start & Execution

### Option 1: Local Execution (FastAPI + Streamlit)
```bash
# 1. Install Dependencies
pip install -r requirements.txt

# 2. Start FastAPI REST Service (Port 8000)
python main.py

# 3. Start Streamlit Admin Dashboard (Port 8501)
streamlit run admin_app.py

# 4. Run Client Agent Integration Demo
python client_agent_demo.py

# 5. Run RAGAS Retrieval Quality Evaluation
python eval_retrieval_quality.py
```

### Option 2: Docker Compose Deployment
```bash
docker-compose up --build
```
- REST API Service: `http://localhost:8000` (Docs: `http://localhost:8000/docs`)
- Admin Observability Dashboard: `http://localhost:8501`
