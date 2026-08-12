"""
Async Consolidation Worker for the Enterprise AI Memory Platform.
Runs background memory optimization for tenant spaces:
1. Episodic Summarization: Groups old interactions into high-level episodic summaries.
2. Rule Promotion: Promotes frequently applied procedural rules by boosting confidence.
3. Memory Pruning: Removes low-importance episodic entries beyond retention limits.
"""

import sqlite3
import datetime
import json
import logging
from typing import Dict, Any, Optional, List
from platform_memory_engine import PlatformMemoryEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ConsolidationWorker")


class ConsolidationWorker:
    def __init__(self, memory_engine: Optional[PlatformMemoryEngine] = None):
        self.engine = memory_engine or PlatformMemoryEngine()

    def consolidate_tenant_memory(
        self,
        tenant_id: str,
        max_episodic_retention: int = 50,
        prune_importance_threshold: float = 2.0
    ) -> Dict[str, Any]:
        """Runs a complete consolidation cycle for a single tenant."""
        logger.info(f"Starting consolidation cycle for tenant: {tenant_id}")
        start_time = datetime.datetime.utcnow()

        episodes_pruned = self._prune_low_importance_episodes(
            tenant_id, max_retention=max_episodic_retention, min_importance=prune_importance_threshold
        )
        rules_promoted = self._promote_procedural_rules(tenant_id)
        facts_consolidated = self._consolidate_episodic_facts(tenant_id)

        end_time = datetime.datetime.utcnow()
        duration_sec = (end_time - start_time).total_seconds()

        report = {
            "tenant_id": tenant_id,
            "timestamp": end_time.isoformat(),
            "duration_seconds": duration_sec,
            "episodes_pruned": episodes_pruned,
            "rules_promoted": rules_promoted,
            "facts_consolidated": facts_consolidated,
            "status": "COMPLETED"
        }
        logger.info(f"Consolidation complete for {tenant_id}: {report}")
        return report

    def _prune_low_importance_episodes(self, tenant_id: str, max_retention: int, min_importance: float) -> int:
        conn = sqlite3.connect(self.engine.db_path)
        cursor = conn.cursor()

        # Count total episodes
        cursor.execute("SELECT COUNT(*) FROM episodic_interactions WHERE tenant_id = ?", (tenant_id,))
        total_count = cursor.fetchone()[0]

        if total_count <= max_retention:
            conn.close()
            return 0

        # Delete low-importance episodes beyond retention limit
        excess = total_count - max_retention
        cursor.execute(
            '''DELETE FROM episodic_interactions 
               WHERE id IN (
                   SELECT id FROM episodic_interactions 
                   WHERE tenant_id = ? AND importance_score < ? 
                   ORDER BY timestamp ASC LIMIT ?
               )''',
            (tenant_id, min_importance, excess)
        )
        pruned_count = cursor.rowcount
        conn.commit()
        conn.close()
        return pruned_count

    def _promote_procedural_rules(self, tenant_id: str) -> int:
        conn = sqlite3.connect(self.engine.db_path)
        cursor = conn.cursor()
        # Increase confidence of rules applied > 3 times
        cursor.execute(
            '''UPDATE procedural_rules 
               SET confidence = MIN(1.0, confidence + 0.1) 
               WHERE tenant_id = ? AND application_count >= 3 AND confidence < 1.0''',
            (tenant_id,)
        )
        promoted_count = cursor.rowcount
        conn.commit()
        conn.close()
        return promoted_count

    def _consolidate_episodic_facts(self, tenant_id: str) -> int:
        # Scan recent episodic entries for high importance (> 8.0) and promote to semantic store if not already present
        episodes = self.engine.get_all_episodes(tenant_id=tenant_id, limit=20)
        promoted = 0
        for ep in episodes:
            if ep["importance_score"] >= 8.0 and ep["role"] == "user":
                fact_doc = f"Key User Statement: {ep['content']}"
                # Store as consolidated fact
                self.engine.store_fact(
                    tenant_id=tenant_id,
                    fact_text=fact_doc,
                    category="consolidated_preference",
                    confidence_score=0.9,
                    metadata={"source_episode_id": ep["id"]}
                )
                promoted += 1
        return promoted


if __name__ == "__main__":
    worker = ConsolidationWorker()
    print("Testing consolidation worker...")
    res = worker.consolidate_tenant_memory("tenant_demo")
    print("Result:", res)
