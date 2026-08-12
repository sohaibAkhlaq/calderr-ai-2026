"""
Integration Example: External AI Agent Client for Project 6-P-A.
Demonstrates how any third-party AI agent (LangChain / AutoGen / Groq / custom)
connects to the Enterprise AI Memory Platform via REST API to read and write memories.
"""

import requests
import json
import time

# Configurable Memory API Base URL
BASE_URL = "http://localhost:8000"
TENANT_ID = "tenant_enterprise_demo"
SESSION_ID = "agent_session_99"


def main():
    print(f"External AI Agent Client Connecting to {BASE_URL} for Tenant [{TENANT_ID}]...\n")

    # 1. Health Check
    try:
        r = requests.get(f"{BASE_URL}/v1/health", timeout=5)
        print(f"[OK] Platform Health Check: {r.json()['status']} (Service: {r.json()['service']})")
    except Exception as e:
        print(f"[WARNING] Could not connect to API at {BASE_URL}. Ensure main.py is running. Local test fallback active.\nError: {e}")
        return

    # 2. Log User Episode (Episodic Store)
    print("\n1. Logging Interaction to Episodic Store...")
    ep_payload = {
        "session_id": SESSION_ID,
        "user_id": "usr_exec_101",
        "role": "user",
        "content": "We are migrating our database infrastructure from PostgreSQL to a multi-region Spanner cluster.",
        "importance_score": 9.0,
        "metadata": {"source": "slack_channel"}
    }
    r = requests.post(f"{BASE_URL}/v1/tenants/{TENANT_ID}/episodic", json=ep_payload)
    print(f"Response: {r.status_code} -> {r.json()}")

    # 3. Store Atomic Fact (Semantic Store)
    print("\n2. Storing Atomic Knowledge Fact in Semantic Vector Index...")
    fact_payload = {
        "fact_text": "Tenant enterprise infrastructure migrating to multi-region Spanner cluster in Q3 2026",
        "category": "infrastructure_goal",
        "confidence_score": 0.95
    }
    r = requests.post(f"{BASE_URL}/v1/tenants/{TENANT_ID}/semantic/facts", json=fact_payload)
    print(f"Response: {r.status_code} -> {r.json()}")

    # 4. Register Procedural Rule (Procedural Store)
    print("\n3. Registering Procedural Correction Rule...")
    rule_payload = {
        "domain": "database_queries",
        "original_mistake": "Writing raw SQL queries for Spanner without param binding",
        "correction_rule": "Always use parameterized Spanner queries to enable query plan caching",
        "confidence": 0.9
    }
    r = requests.post(f"{BASE_URL}/v1/tenants/{TENANT_ID}/procedural/rules", json=rule_payload)
    print(f"Response: {r.status_code} -> {r.json()}")

    # 5. Add Knowledge Graph Triples (Knowledge Graph Store)
    print("\n4. Building Knowledge Graph Triples...")
    graph_payload = {
        "triples": [
            {"subject": "Spanner", "predicate": "REPLACES", "object": "PostgreSQL"},
            {"subject": "Spanner", "predicate": "MANAGED_BY", "object": "Cloud_Ops_Team"},
            {"subject": "Cloud_Ops_Team", "predicate": "LEAD_BY", "object": "usr_exec_101"}
        ]
    }
    r = requests.post(f"{BASE_URL}/v1/tenants/{TENANT_ID}/graph/triples", json=graph_payload)
    print(f"Response: {r.status_code} -> {r.json()}")

    # 6. Retrieve Relevant Context via Vector Search
    print("\n5. Performing Vector Similarity Search across Semantic Memory...")
    search_payload = {
        "query": "database migration plans and Spanner architecture",
        "n_results": 3
    }
    r = requests.post(f"{BASE_URL}/v1/tenants/{TENANT_ID}/semantic/search", json=search_payload)
    results = r.json().get("results", [])
    for idx, hit in enumerate(results, 1):
        print(f"   Hit {idx}: [Sim: {hit['similarity']}] {hit['fact']}")

    # 7. Query Knowledge Graph
    print("\n6. Querying Knowledge Graph Multi-Hop Entity Relations...")
    r = requests.get(f"{BASE_URL}/v1/tenants/{TENANT_ID}/graph/query?entity=Spanner&max_depth=2")
    graph_res = r.json().get("result", {})
    print(f"   Found Nodes: {[n['id'] for n in graph_res.get('nodes', [])]}")
    print(f"   Found Edges: {[e['source'] + ' -> ' + e['relation'] + ' -> ' + e['target'] for e in graph_res.get('edges', [])]}")

    # 8. Trigger Async Memory Consolidation
    print("\n7. Triggering Memory Consolidation Worker...")
    r = requests.post(f"{BASE_URL}/v1/tenants/{TENANT_ID}/consolidate", json={"max_episodic_retention": 20})
    print(f"Consolidation Report: {r.json()}")

    print("\nClient Agent Demonstration Complete! Enterprise Memory successfully integrated.")


if __name__ == "__main__":
    main()
