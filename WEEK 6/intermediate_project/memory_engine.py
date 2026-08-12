"""
Unified Memory Engine for the Long-Term Personal Research Assistant.
Handles:
- SQLite Episodic Store (interaction logs)
- SQLite User Profile Store (JSON aggregation)
- SQLite Semantic Store (fact retrieval with pure-Python cosine similarity)

This implementation uses ONLY SQLite + numpy for all storage,
completely bypassing ChromaDB and its onnxruntime C++ DLL dependency
which crashes on Windows environments with broken DLLs.
"""

import sqlite3
import json
import uuid
import datetime
import os
import hashlib
import numpy as np

# Ensure data directory exists
os.makedirs("data", exist_ok=True)


def compute_embedding(text):
    """Pure-Python embedding using deterministic random indexing.
    Produces a 384-dim vector from word hashes — no ML models needed."""
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


def cosine_similarity(vec_a, vec_b):
    """Compute cosine similarity between two vectors."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


class MemoryEngine:
    def __init__(self, db_path="data/episodic_memory.db"):
        self.db_path = db_path
        self._init_sqlite()

    def _init_sqlite(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Episodic Interactions Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodic_interactions (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                timestamp TEXT,
                role TEXT,
                content TEXT,
                importance_score REAL
            )
        ''')
        
        # User Profile Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profile (
                user_id TEXT PRIMARY KEY,
                profile_data TEXT
            )
        ''')
        
        # Semantic Facts Table (replaces ChromaDB)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS semantic_facts (
                id TEXT PRIMARY KEY,
                document TEXT,
                category TEXT,
                confidence_score REAL,
                recency_timestamp TEXT,
                embedding TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize default user profile if empty
        self._init_default_profile()

    def _init_default_profile(self, user_id="usr_9981"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profile WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            default_profile = {
                "user_id": user_id,
                "known_topics": [],
                "preferred_depth": "balanced",
                "communication_style": "standard",
                "active_research_goals": [],
                "open_questions": []
            }
            cursor.execute(
                "INSERT INTO user_profile (user_id, profile_data) VALUES (?, ?)", 
                (user_id, json.dumps(default_profile))
            )
            conn.commit()
        conn.close()

    # --- Episodic Memory Methods ---
    def log_interaction(self, session_id, role, content, importance_score=1.0):
        interaction_id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO episodic_interactions (id, session_id, timestamp, role, content, importance_score) VALUES (?, ?, ?, ?, ?, ?)",
            (interaction_id, session_id, timestamp, role, content, importance_score)
        )
        conn.commit()
        conn.close()

    def get_recent_history(self, session_id, limit=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM episodic_interactions WHERE session_id = ? ORDER BY timestamp ASC LIMIT ?",
            (session_id, limit)
        )
        history = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
        conn.close()
        return history

    def get_all_episodic_logs(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, session_id, role, content, importance_score FROM episodic_interactions ORDER BY timestamp DESC")
        logs = cursor.fetchall()
        conn.close()
        return logs

    # --- Semantic Memory Methods (Pure SQLite — no ChromaDB) ---
    def add_fact(self, fact_text, category, confidence_score=1.0):
        fact_id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow().isoformat()
        embedding = compute_embedding(fact_text)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO semantic_facts (id, document, category, confidence_score, recency_timestamp, embedding) VALUES (?, ?, ?, ?, ?, ?)",
            (fact_id, fact_text, category, confidence_score, timestamp, json.dumps(embedding))
        )
        conn.commit()
        conn.close()
        return fact_id

    def retrieve_relevant_facts(self, query, n_results=5):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, document, category, recency_timestamp, embedding FROM semantic_facts")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return []
        
        query_embedding = compute_embedding(query)
        
        scored = []
        for row in rows:
            fact_embedding = json.loads(row[4])
            score = cosine_similarity(query_embedding, fact_embedding)
            scored.append({
                "fact": row[1],
                "metadata": {
                    "category": row[2],
                    "recency_timestamp": row[3],
                    "confidence_score": score
                }
            })
        
        scored.sort(key=lambda x: x["metadata"]["confidence_score"], reverse=True)
        return scored[:n_results]
        
    def get_all_facts(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, document, category, recency_timestamp FROM semantic_facts ORDER BY recency_timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        
        facts = []
        for row in rows:
            facts.append({
                "id": row[0],
                "fact": row[1], 
                "category": row[2],
                "timestamp": row[3]
            })
        return facts

    # --- User Profile Methods ---
    def get_user_profile(self, user_id="usr_9981"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT profile_data FROM user_profile WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
        return {}

    def update_user_profile(self, updated_profile, user_id="usr_9981"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE user_profile SET profile_data = ? WHERE user_id = ?",
            (json.dumps(updated_profile), user_id)
        )
        conn.commit()
        conn.close()
