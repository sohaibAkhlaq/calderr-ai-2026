"""
Unified Multi-Tenant Memory Engine for the Enterprise AI Memory Platform.
Handles 4 distinct memory layers with tenant-isolated namespaces:
1. Episodic Memory Store (SQLite - interaction logs per tenant)
2. Semantic Memory Store (SQLite Vector Store with Pure-Python Cosine Similarity per tenant)
3. Procedural Memory Store (SQLite - domain rules & error corrections per tenant)
4. Knowledge Graph Store (NetworkX - per-tenant entity/relationship sub-graphs serialized to JSON)
"""

import sqlite3
import json
import uuid
import datetime
import os
import hashlib
import numpy as np
import networkx as nx
from typing import List, Dict, Any, Optional

# Ensure data directories exist
DATA_DIR = "data"
GRAPHS_DIR = os.path.join(DATA_DIR, "graphs")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(GRAPHS_DIR, exist_ok=True)


def compute_embedding(text: str) -> List[float]:
    """Pure-Python deterministic random-indexing vector embedding generator.
    Produces a 384-dimensional normalized vector without C++ DLL dependencies."""
    words = str(text).lower().replace('.', '').replace(',', '').replace('!', '').replace('?', '').split()
    if not words:
        return [0.0] * 384
    vec = np.zeros(384)
    for w in words:
        h = int(hashlib.md5(w.encode('utf-8')).hexdigest(), 16)
        np.random.seed(h % (2**32))
        vec += np.random.randn(384)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two 384-dimensional vectors."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


class PlatformMemoryEngine:
    def __init__(self, db_path: str = "data/enterprise_memory.db"):
        self.db_path = db_path
        self._init_sqlite()

    def _init_sqlite(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 1. Episodic Store Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodic_interactions (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                importance_score REAL DEFAULT 5.0,
                metadata TEXT
            )
        ''')

        # 2. Semantic Facts Table (Vector Index)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS semantic_facts (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                document TEXT NOT NULL,
                category TEXT NOT NULL,
                confidence_score REAL DEFAULT 1.0,
                recency_timestamp TEXT NOT NULL,
                embedding TEXT NOT NULL,
                metadata TEXT
            )
        ''')

        # 3. Procedural Rules Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS procedural_rules (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                domain TEXT NOT NULL,
                original_mistake TEXT NOT NULL,
                correction_rule TEXT NOT NULL,
                confidence REAL DEFAULT 0.8,
                application_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        ''')

        # Create indexes for fast multi-tenant querying
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_episodic_tenant ON episodic_interactions(tenant_id, session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_semantic_tenant ON semantic_facts(tenant_id, category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_procedural_tenant ON procedural_rules(tenant_id, domain)')

        conn.commit()
        conn.close()

    # =========================================================================
    # 1. EPISODIC MEMORY METHODS
    # =========================================================================
    def log_episode(
        self,
        tenant_id: str,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
        importance_score: float = 5.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        entry_id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow().isoformat()
        meta_json = json.dumps(metadata or {})

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO episodic_interactions 
               (id, tenant_id, session_id, user_id, timestamp, role, content, importance_score, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (entry_id, tenant_id, session_id, user_id, timestamp, role, content, importance_score, meta_json)
        )
        conn.commit()
        conn.close()
        return entry_id

    def get_episodic_history(self, tenant_id: str, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT id, timestamp, role, content, importance_score, metadata 
               FROM episodic_interactions 
               WHERE tenant_id = ? AND session_id = ? 
               ORDER BY timestamp ASC LIMIT ?''',
            (tenant_id, session_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()

        history = []
        for r in rows:
            history.append({
                "id": r[0],
                "timestamp": r[1],
                "role": r[2],
                "content": r[3],
                "importance_score": r[4],
                "metadata": json.loads(r[5]) if r[5] else {}
            })
        return history

    def get_all_episodes(self, tenant_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if tenant_id:
            cursor.execute(
                '''SELECT id, tenant_id, session_id, user_id, timestamp, role, content, importance_score 
                   FROM episodic_interactions WHERE tenant_id = ? ORDER BY timestamp DESC LIMIT ?''',
                (tenant_id, limit)
            )
        else:
            cursor.execute(
                '''SELECT id, tenant_id, session_id, user_id, timestamp, role, content, importance_score 
                   FROM episodic_interactions ORDER BY timestamp DESC LIMIT ?''',
                (limit,)
            )
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": r[0], "tenant_id": r[1], "session_id": r[2], "user_id": r[3],
                "timestamp": r[4], "role": r[5], "content": r[6], "importance_score": r[7]
            }
            for r in rows
        ]

    # =========================================================================
    # 2. SEMANTIC MEMORY METHODS
    # =========================================================================
    def store_fact(
        self,
        tenant_id: str,
        fact_text: str,
        category: str = "general",
        confidence_score: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        fact_id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow().isoformat()
        embedding = compute_embedding(fact_text)
        meta_json = json.dumps(metadata or {})

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO semantic_facts 
               (id, tenant_id, document, category, confidence_score, recency_timestamp, embedding, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (fact_id, tenant_id, fact_text, category, confidence_score, timestamp, json.dumps(embedding), meta_json)
        )
        conn.commit()
        conn.close()
        return fact_id

    def search_semantic_facts(
        self,
        tenant_id: str,
        query: str,
        n_results: int = 5,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if category_filter:
            cursor.execute(
                "SELECT id, document, category, confidence_score, recency_timestamp, embedding, metadata FROM semantic_facts WHERE tenant_id = ? AND category = ?",
                (tenant_id, category_filter)
            )
        else:
            cursor.execute(
                "SELECT id, document, category, confidence_score, recency_timestamp, embedding, metadata FROM semantic_facts WHERE tenant_id = ?",
                (tenant_id,)
            )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return []

        query_embedding = compute_embedding(query)
        scored = []
        for r in rows:
            fact_emb = json.loads(r[5])
            sim = cosine_similarity(query_embedding, fact_emb)
            scored.append({
                "id": r[0],
                "fact": r[1],
                "category": r[2],
                "confidence_score": r[3],
                "timestamp": r[4],
                "similarity": round(sim, 4),
                "metadata": json.loads(r[6]) if r[6] else {}
            })

        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:n_results]

    def get_all_facts(self, tenant_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if tenant_id:
            cursor.execute(
                "SELECT id, tenant_id, document, category, confidence_score, recency_timestamp FROM semantic_facts WHERE tenant_id = ? ORDER BY recency_timestamp DESC LIMIT ?",
                (tenant_id, limit)
            )
        else:
            cursor.execute(
                "SELECT id, tenant_id, document, category, confidence_score, recency_timestamp FROM semantic_facts ORDER BY recency_timestamp DESC LIMIT ?",
                (limit,)
            )
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": r[0], "tenant_id": r[1], "fact": r[2], "category": r[3],
                "confidence_score": r[4], "timestamp": r[5]
            }
            for r in rows
        ]

    # =========================================================================
    # 3. PROCEDURAL MEMORY METHODS
    # =========================================================================
    def register_procedural_rule(
        self,
        tenant_id: str,
        domain: str,
        original_mistake: str,
        correction_rule: str,
        confidence: float = 0.8
    ) -> str:
        rule_id = str(uuid.uuid4())
        created_at = datetime.datetime.utcnow().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO procedural_rules 
               (id, tenant_id, domain, original_mistake, correction_rule, confidence, application_count, created_at)
               VALUES (?, ?, ?, ?, ?, ?, 0, ?)''',
            (rule_id, tenant_id, domain, original_mistake, correction_rule, confidence, created_at)
        )
        conn.commit()
        conn.close()
        return rule_id

    def query_procedural_rules(self, tenant_id: str, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if domain:
            cursor.execute(
                '''SELECT id, domain, original_mistake, correction_rule, confidence, application_count, created_at 
                   FROM procedural_rules WHERE tenant_id = ? AND domain = ? ORDER BY confidence DESC''',
                (tenant_id, domain)
            )
        else:
            cursor.execute(
                '''SELECT id, domain, original_mistake, correction_rule, confidence, application_count, created_at 
                   FROM procedural_rules WHERE tenant_id = ? ORDER BY confidence DESC''',
                (tenant_id,)
            )
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": r[0], "domain": r[1], "original_mistake": r[2], "correction_rule": r[3],
                "confidence": r[4], "application_count": r[5], "created_at": r[6]
            }
            for r in rows
        ]

    def increment_rule_application(self, rule_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE procedural_rules SET application_count = application_count + 1, confidence = MIN(1.0, confidence + 0.05) WHERE id = ?",
            (rule_id,)
        )
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

    # =========================================================================
    # 4. KNOWLEDGE GRAPH METHODS (NetworkX per Tenant)
    # =========================================================================
    def _get_graph_path(self, tenant_id: str) -> str:
        return os.path.join(GRAPHS_DIR, f"{tenant_id}_graph.json")

    def _load_tenant_graph(self, tenant_id: str) -> nx.DiGraph:
        path = self._get_graph_path(tenant_id)
        G = nx.DiGraph()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                G = nx.node_link_graph(data)
            except Exception:
                G = nx.DiGraph()
        return G

    def _save_tenant_graph(self, tenant_id: str, G: nx.DiGraph):
        path = self._get_graph_path(tenant_id)
        data = nx.node_link_data(G)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def add_graph_triples(self, tenant_id: str, triples: List[Dict[str, str]]) -> int:
        """triples is a list of dicts: [{"subject": "A", "predicate": "USES", "object": "B"}]"""
        G = self._load_tenant_graph(tenant_id)
        added = 0
        for t in triples:
            sub = t.get("subject", "").strip()
            pred = t.get("predicate", "").strip()
            obj = t.get("object", "").strip()
            if sub and pred and obj:
                G.add_node(sub, label=sub)
                G.add_node(obj, label=obj)
                G.add_edge(sub, obj, relation=pred)
                added += 1
        self._save_tenant_graph(tenant_id, G)
        return added

    def query_tenant_graph(self, tenant_id: str, entity: str, max_depth: int = 2) -> Dict[str, Any]:
        G = self._load_tenant_graph(tenant_id)
        if entity not in G:
            return {"entity": entity, "found": False, "nodes": [], "edges": [], "paths": []}

        subgraph_nodes = set([entity])
        current_layer = {entity}
        for _ in range(max_depth):
            next_layer = set()
            for node in current_layer:
                neighbors = set(G.successors(node)).union(set(G.predecessors(node)))
                next_layer.update(neighbors)
            subgraph_nodes.update(next_layer)
            current_layer = next_layer

        subgraph = G.subgraph(subgraph_nodes)
        nodes = [{"id": n, "label": n} for n in subgraph.nodes()]
        edges = [
            {"source": u, "target": v, "relation": d.get("relation", "RELATED_TO")}
            for u, v, d in subgraph.edges(data=True)
        ]

        return {
            "entity": entity,
            "found": True,
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges)
        }

    def get_full_tenant_graph(self, tenant_id: str) -> Dict[str, Any]:
        G = self._load_tenant_graph(tenant_id)
        nodes = [{"id": n, "label": n} for n in G.nodes()]
        edges = [
            {"source": u, "target": v, "relation": d.get("relation", "RELATED_TO")}
            for u, v, d in G.edges(data=True)
        ]
        return {
            "tenant_id": tenant_id,
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges)
        }

    # =========================================================================
    # 5. MULTI-TENANT AUDIT & STATS
    # =========================================================================
    def get_all_tenants(self) -> List[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT tenant_id FROM episodic_interactions UNION SELECT DISTINCT tenant_id FROM semantic_facts UNION SELECT DISTINCT tenant_id FROM procedural_rules")
        rows = cursor.fetchall()
        conn.close()

        tenants = set([r[0] for r in rows if r[0]])
        # Also check graph JSON files
        if os.path.exists(GRAPHS_DIR):
            for fname in os.listdir(GRAPHS_DIR):
                if fname.endswith("_graph.json"):
                    tenants.add(fname.replace("_graph.json", ""))
        return sorted(list(tenants))

    def get_tenant_stats(self, tenant_id: str) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM episodic_interactions WHERE tenant_id = ?", (tenant_id,))
        episodes_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM semantic_facts WHERE tenant_id = ?", (tenant_id,))
        facts_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM procedural_rules WHERE tenant_id = ?", (tenant_id,))
        rules_count = cursor.fetchone()[0]
        conn.close()

        graph_info = self.get_full_tenant_graph(tenant_id)

        return {
            "tenant_id": tenant_id,
            "episodic_count": episodes_count,
            "semantic_count": facts_count,
            "procedural_count": rules_count,
            "graph_nodes": graph_info["node_count"],
            "graph_edges": graph_info["edge_count"]
        }
