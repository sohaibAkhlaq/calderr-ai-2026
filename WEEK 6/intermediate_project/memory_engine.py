"""
Unified Memory Engine for the Long-Term Personal Research Assistant.
Handles:
- SQLite Episodic Store (interaction logs)
- SQLite User Profile Store (JSON aggregation)
- ChromaDB Semantic Store (atomic fact retrieval)
"""

import sqlite3
import json
import uuid
import datetime
import os
import chromadb

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

class MemoryEngine:
    def __init__(self, db_path="data/episodic_memory.db", chroma_path="data/chroma_db"):
        self.db_path = db_path
        self.chroma_path = chroma_path
        self._init_sqlite()
        self._init_chroma()

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

    def _init_chroma(self):
        self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
        self.semantic_collection = self.chroma_client.get_or_create_collection(
            name="user_research_facts",
            metadata={"hnsw:space": "cosine"}
        )

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

    # --- Semantic Memory Methods ---
    def add_fact(self, fact_text, category, confidence_score=1.0):
        fact_id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow().isoformat()
        
        self.semantic_collection.add(
            documents=[fact_text],
            metadatas=[{"category": category, "recency_timestamp": timestamp, "confidence_score": confidence_score}],
            ids=[fact_id]
        )
        return fact_id

    def retrieve_relevant_facts(self, query, n_results=5):
        if self.semantic_collection.count() == 0:
            return []
            
        results = self.semantic_collection.query(
            query_texts=[query],
            n_results=min(n_results, self.semantic_collection.count())
        )
        
        facts = []
        if results['documents']:
            for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                facts.append({"fact": doc, "metadata": meta})
        return facts
        
    def get_all_facts(self):
        if self.semantic_collection.count() == 0:
            return []
        
        results = self.semantic_collection.get()
        facts = []
        if results['documents']:
            for i, doc in enumerate(results['documents']):
                facts.append({
                    "id": results['ids'][i],
                    "fact": doc, 
                    "category": results['metadatas'][i].get("category", ""),
                    "timestamp": results['metadatas'][i].get("recency_timestamp", "")
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
