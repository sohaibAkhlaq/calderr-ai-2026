"""
FastAPI REST API Memory Service for Project 6-P-A: Enterprise AI Memory Platform.
Provides multi-tenant Memory-as-a-Service for external AI agents across 4 memory layers:
1. Episodic API (SQLite interaction logs)
2. Semantic API (Pure-Python Cosine Similarity vector search)
3. Procedural API (SQLite correction rules)
4. Knowledge Graph API (NetworkX entity-relationship query & paths)
5. Consolidation Worker API (Async background consolidation)
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import uvicorn

from platform_memory_engine import PlatformMemoryEngine
from consolidation_worker import ConsolidationWorker

app = FastAPI(
    title="Enterprise AI Memory Platform API",
    description="Multi-tenant Memory-as-a-Service infrastructure for external AI agents (Mem0 alternative).",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend & dashboard integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = PlatformMemoryEngine()
worker = ConsolidationWorker(memory_engine=engine)


# =============================================================================
# PYDANTIC SCHEMAS
# =============================================================================
class LogEpisodeRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(default="usr_default", description="User identifier within tenant")
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Interaction content text")
    importance_score: float = Field(default=5.0, ge=1.0, le=10.0, description="Importance score (1.0 to 10.0)")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Optional metadata key-value pairs")


class StoreFactRequest(BaseModel):
    fact_text: str = Field(..., description="Atomic semantic fact text")
    category: str = Field(default="general", description="Category: preference, goal, skill, etc.")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Optional metadata")


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query")
    n_results: int = Field(default=5, ge=1, le=50, description="Max facts to retrieve")
    category_filter: Optional[str] = Field(default=None, description="Optional category filter")


class RegisterRuleRequest(BaseModel):
    domain: str = Field(..., description="Domain area (e.g., python, sql, style)")
    original_mistake: str = Field(..., description="Mistake pattern observed")
    correction_rule: str = Field(..., description="Rule instruction to prevent mistake")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Rule confidence score")


class AddTriplesRequest(BaseModel):
    triples: List[Dict[str, str]] = Field(..., description="List of triples: [{'subject': 'A', 'predicate': 'USES', 'object': 'B'}]")


class ConsolidateRequest(BaseModel):
    max_episodic_retention: int = Field(default=50, ge=5, description="Max episodes to retain before pruning")
    prune_importance_threshold: float = Field(default=2.0, ge=1.0, le=10.0, description="Prune episodes below this score")


# =============================================================================
# HEALTH & AUDIT ENDPOINTS
# =============================================================================
@app.get("/v1/health", status_code=status.HTTP_200_OK, tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "Enterprise AI Memory Platform",
        "version": "1.0.0",
        "tenants_count": len(engine.get_all_tenants())
    }


@app.get("/v1/tenants", tags=["Tenant Management"])
def list_tenants():
    """Returns a list of all active tenant namespaces."""
    tenants = engine.get_all_tenants()
    return {"tenants": tenants, "total_tenants": len(tenants)}


@app.get("/v1/tenants/{tenant_id}/stats", tags=["Tenant Management"])
def get_tenant_stats(tenant_id: str):
    """Returns memory state breakdown and statistics for a tenant."""
    return engine.get_tenant_stats(tenant_id)


# =============================================================================
# 1. EPISODIC MEMORY ENDPOINTS
# =============================================================================
@app.post("/v1/tenants/{tenant_id}/episodic", status_code=status.HTTP_201_CREATED, tags=["Episodic Memory"])
def log_episodic_entry(tenant_id: str, req: LogEpisodeRequest):
    """Logs an interaction message into the tenant's episodic memory store."""
    entry_id = engine.log_episode(
        tenant_id=tenant_id,
        session_id=req.session_id,
        user_id=req.user_id,
        role=req.role,
        content=req.content,
        importance_score=req.importance_score,
        metadata=req.metadata
    )
    return {"status": "success", "id": entry_id, "tenant_id": tenant_id, "session_id": req.session_id}


@app.get("/v1/tenants/{tenant_id}/episodic/{session_id}", tags=["Episodic Memory"])
def get_session_history(tenant_id: str, session_id: str, limit: int = Query(20, ge=1, le=100)):
    """Retrieves session interaction history for a specific session within a tenant."""
    history = engine.get_episodic_history(tenant_id=tenant_id, session_id=session_id, limit=limit)
    return {"tenant_id": tenant_id, "session_id": session_id, "count": len(history), "history": history}


@app.get("/v1/tenants/{tenant_id}/episodic", tags=["Episodic Memory"])
def get_all_tenant_episodes(tenant_id: str, limit: int = Query(50, ge=1, le=500)):
    """Lists recent episodic logs across all sessions for a tenant."""
    episodes = engine.get_all_episodes(tenant_id=tenant_id, limit=limit)
    return {"tenant_id": tenant_id, "count": len(episodes), "episodes": episodes}


# =============================================================================
# 2. SEMANTIC MEMORY ENDPOINTS
# =============================================================================
@app.post("/v1/tenants/{tenant_id}/semantic/facts", status_code=status.HTTP_201_CREATED, tags=["Semantic Memory"])
def store_semantic_fact(tenant_id: str, req: StoreFactRequest):
    """Stores an atomic semantic fact with vector embedding into the tenant vector namespace."""
    fact_id = engine.store_fact(
        tenant_id=tenant_id,
        fact_text=req.fact_text,
        category=req.category,
        confidence_score=req.confidence_score,
        metadata=req.metadata
    )
    return {"status": "success", "id": fact_id, "tenant_id": tenant_id}


@app.post("/v1/tenants/{tenant_id}/semantic/search", tags=["Semantic Memory"])
def search_semantic_facts(tenant_id: str, req: SemanticSearchRequest):
    """Performs cosine-similarity vector search over tenant semantic facts."""
    results = engine.search_semantic_facts(
        tenant_id=tenant_id,
        query=req.query,
        n_results=req.n_results,
        category_filter=req.category_filter
    )
    return {"tenant_id": tenant_id, "query": req.query, "count": len(results), "results": results}


@app.get("/v1/tenants/{tenant_id}/semantic/facts", tags=["Semantic Memory"])
def list_semantic_facts(tenant_id: str, limit: int = Query(50, ge=1, le=500)):
    """Lists all stored semantic facts for a tenant."""
    facts = engine.get_all_facts(tenant_id=tenant_id, limit=limit)
    return {"tenant_id": tenant_id, "count": len(facts), "facts": facts}


# =============================================================================
# 3. PROCEDURAL MEMORY ENDPOINTS
# =============================================================================
@app.post("/v1/tenants/{tenant_id}/procedural/rules", status_code=status.HTTP_201_CREATED, tags=["Procedural Memory"])
def register_procedural_rule(tenant_id: str, req: RegisterRuleRequest):
    """Registers a procedural correction rule to avoid repeating domain mistakes."""
    rule_id = engine.register_procedural_rule(
        tenant_id=tenant_id,
        domain=req.domain,
        original_mistake=req.original_mistake,
        correction_rule=req.correction_rule,
        confidence=req.confidence
    )
    return {"status": "success", "id": rule_id, "tenant_id": tenant_id, "domain": req.domain}


@app.get("/v1/tenants/{tenant_id}/procedural/rules", tags=["Procedural Memory"])
def query_procedural_rules(tenant_id: str, domain: Optional[str] = Query(None)):
    """Queries procedural correction rules for a tenant, optionally filtered by domain."""
    rules = engine.query_procedural_rules(tenant_id=tenant_id, domain=domain)
    return {"tenant_id": tenant_id, "domain": domain, "count": len(rules), "rules": rules}


@app.post("/v1/rules/{rule_id}/apply", tags=["Procedural Memory"])
def apply_procedural_rule(rule_id: str):
    """Increments the application count and confidence score of a procedural rule."""
    success = engine.increment_rule_application(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rule ID not found")
    return {"status": "success", "rule_id": rule_id, "applied": True}


# =============================================================================
# 4. KNOWLEDGE GRAPH ENDPOINTS
# =============================================================================
@app.post("/v1/tenants/{tenant_id}/graph/triples", status_code=status.HTTP_201_CREATED, tags=["Knowledge Graph"])
def add_graph_triples(tenant_id: str, req: AddTriplesRequest):
    """Adds entity-relation-entity triples into the tenant NetworkX Knowledge Graph."""
    added = engine.add_graph_triples(tenant_id=tenant_id, triples=req.triples)
    return {"status": "success", "tenant_id": tenant_id, "added_count": added}


@app.get("/v1/tenants/{tenant_id}/graph/query", tags=["Knowledge Graph"])
def query_tenant_graph(tenant_id: str, entity: str = Query(...), max_depth: int = Query(2, ge=1, le=5)):
    """Queries sub-graph nodes and edges connected to an entity up to max_depth traversal."""
    res = engine.query_tenant_graph(tenant_id=tenant_id, entity=entity, max_depth=max_depth)
    return {"tenant_id": tenant_id, "result": res}


@app.get("/v1/tenants/{tenant_id}/graph", tags=["Knowledge Graph"])
def get_full_tenant_graph(tenant_id: str):
    """Returns the complete Knowledge Graph structure for a tenant."""
    return engine.get_full_tenant_graph(tenant_id=tenant_id)


# =============================================================================
# 5. CONSOLIDATION WORKER ENDPOINTS
# =============================================================================
@app.post("/v1/tenants/{tenant_id}/consolidate", tags=["Consolidation Worker"])
def trigger_consolidation(tenant_id: str, req: ConsolidateRequest, background_tasks: BackgroundTasks):
    """Triggers an async memory consolidation cycle for a tenant."""
    report = worker.consolidate_tenant_memory(
        tenant_id=tenant_id,
        max_episodic_retention=req.max_episodic_retention,
        prune_importance_threshold=req.prune_importance_threshold
    )
    return {"status": "success", "report": report}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
