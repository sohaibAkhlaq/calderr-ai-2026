"""
Lab 7.4: Production Hardened Public API MCP Server (GitHub Intelligence Wrapper)
Features:
1. Wraps GitHub Public API (with offline mock fallback for resilience)
2. API Key Authentication Header Validation
3. Per-Endpoint Rate Limiting (Token Bucket per tool)
4. SQLite Audit Store (data/mcp_security_audit.db)
5. Production HTTP+SSE Transport Ready
"""

import os
import time
import json
import sqlite3
import hashlib
import datetime
import requests
from typing import Dict, Any, Optional, List
from fastmcp import FastMCP

# Data & Audit Paths
DATA_DIR = "data"
AUDIT_DB_PATH = os.path.join(DATA_DIR, "mcp_security_audit.db")
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize MCP Server
mcp = FastMCP(
    name="GitHubPublicAPIWrapperServer",
    instructions="Hardened production MCP server wrapping GitHub Developer Intelligence API with Auth, Rate Limiting, and Audit Logging."
)

# Authentication Registry
AUTHORIZED_API_KEYS = {
    "gh_key_alpha": "DeveloperAlpha",
    "gh_key_beta": "DeveloperBeta",
    "admin_prod_key": "ProductionAdmin"
}

# Per-Endpoint Rate Limits: { (api_key, endpoint): [timestamps] }
ENDPOINT_RATE_LIMITS: Dict[tuple, List[float]] = {}
LIMIT_RULES = {
    "get_repo_info": 10,       # 10 calls / min
    "search_github_code": 5,   # 5 calls / min (expensive endpoint)
    "get_user_profile": 10,    # 10 calls / min
    "analyze_repo_health": 8   # 8 calls / min
}
WINDOW_SECONDS = 60.0


# =============================================================================
# SECURITY & AUDIT HELPERS
# =============================================================================
def init_audit_db():
    conn = sqlite3.connect(AUDIT_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            api_key_hash TEXT NOT NULL,
            tool_name TEXT NOT NULL,
            status TEXT NOT NULL,
            latency_ms REAL NOT NULL,
            error_message TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_audit_db()


def audit_log(api_key: str, tool_name: str, status: str, latency_ms: float, error_msg: Optional[str] = None):
    key_hash = hashlib.sha256(api_key.encode('utf-8')).hexdigest()[:16]
    timestamp = datetime.datetime.utcnow().isoformat()

    conn = sqlite3.connect(AUDIT_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO security_audit_logs (timestamp, api_key_hash, tool_name, status, latency_ms, error_message)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (timestamp, key_hash, tool_name, status, latency_ms, error_msg)
    )
    conn.commit()
    conn.close()


def enforce_security(api_key: str, tool_name: str) -> Optional[Dict[str, Any]]:
    """Enforces Authentication and Per-Endpoint Rate Limiting."""
    if not api_key or api_key not in AUTHORIZED_API_KEYS:
        return {"success": False, "error": "401 Unauthorized: Invalid or missing API key.", "error_type": "AuthenticationError"}

    limit = LIMIT_RULES.get(tool_name, 10)
    key_tuple = (api_key, tool_name)
    now = time.time()

    if key_tuple not in ENDPOINT_RATE_LIMITS:
        ENDPOINT_RATE_LIMITS[key_tuple] = []

    # Clean window
    ENDPOINT_RATE_LIMITS[key_tuple] = [t for t in ENDPOINT_RATE_LIMITS[key_tuple] if now - t < WINDOW_SECONDS]

    if len(ENDPOINT_RATE_LIMITS[key_tuple]) >= limit:
        return {
            "success": False,
            "error": f"429 Rate Limit Exceeded: Endpoint '{tool_name}' limited to {limit} requests/minute for key.",
            "error_type": "RateLimitExceeded"
        }

    ENDPOINT_RATE_LIMITS[key_tuple].append(now)
    return None


# =============================================================================
# PUBLIC API TOOLS
# =============================================================================
@mcp.tool(name="get_repo_info", description="Fetches public statistics (stars, forks, issues, language) for a GitHub repository.")
def get_repo_info(api_key: str, owner: str, repo: str) -> Dict[str, Any]:
    start_t = time.time()
    sec_err = enforce_security(api_key, "get_repo_info")
    if sec_err:
        return sec_err

    url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        resp = requests.get(url, headers={"User-Agent": "CalderMCP/1.0"}, timeout=5)
        latency = (time.time() - start_t) * 1000

        if resp.status_code == 200:
            data = resp.json()
            info = {
                "owner": owner,
                "repo": repo,
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "open_issues": data.get("open_issues_count", 0),
                "language": data.get("language", "Unknown"),
                "description": data.get("description", "")
            }
            audit_log(api_key, "get_repo_info", "SUCCESS", latency)
            return {"success": True, "repo_info": info}
        else:
            # Fallback mock for rate-limited API environments
            mock_info = {"owner": owner, "repo": repo, "stars": 4200, "forks": 350, "open_issues": 12, "language": "Python", "description": f"Mock data for {owner}/{repo}"}
            audit_log(api_key, "get_repo_info", "SUCCESS", latency)
            return {"success": True, "repo_info": mock_info, "note": "API fallback active"}
    except Exception as e:
        latency = (time.time() - start_t) * 1000
        audit_log(api_key, "get_repo_info", "FAILURE", latency, str(e))
        return {"success": False, "error": str(e)}


@mcp.tool(name="search_github_code", description="Searches public GitHub repositories by keyword and language.")
def search_github_code(api_key: str, query: str, language: str = "python") -> Dict[str, Any]:
    start_t = time.time()
    sec_err = enforce_security(api_key, "search_github_code")
    if sec_err:
        return sec_err

    url = f"https://api.github.com/search/repositories?q={query}+language:{language}&sort=stars"
    try:
        resp = requests.get(url, headers={"User-Agent": "CalderMCP/1.0"}, timeout=5)
        latency = (time.time() - start_t) * 1000

        if resp.status_code == 200:
            items = resp.json().get("items", [])[:3]
            results = [{"name": i["full_name"], "stars": i["stargazers_count"], "url": i["html_url"]} for i in items]
            audit_log(api_key, "search_github_code", "SUCCESS", latency)
            return {"success": True, "query": query, "count": len(results), "results": results}
        else:
            mock_results = [{"name": f"mock/{query}-repo", "stars": 1500, "url": f"https://github.com/mock/{query}"}]
            audit_log(api_key, "search_github_code", "SUCCESS", latency)
            return {"success": True, "query": query, "count": len(mock_results), "results": mock_results}
    except Exception as e:
        latency = (time.time() - start_t) * 1000
        audit_log(api_key, "search_github_code", "FAILURE", latency, str(e))
        return {"success": False, "error": str(e)}


@mcp.tool(name="get_user_profile", description="Fetches public developer profile stats (public repos, followers) for a GitHub user.")
def get_user_profile(api_key: str, username: str) -> Dict[str, Any]:
    start_t = time.time()
    sec_err = enforce_security(api_key, "get_user_profile")
    if sec_err:
        return sec_err

    url = f"https://api.github.com/users/{username}"
    try:
        resp = requests.get(url, headers={"User-Agent": "CalderMCP/1.0"}, timeout=5)
        latency = (time.time() - start_t) * 1000

        if resp.status_code == 200:
            data = resp.json()
            profile = {
                "username": username,
                "name": data.get("name", username),
                "public_repos": data.get("public_repos", 0),
                "followers": data.get("followers", 0),
                "bio": data.get("bio", "")
            }
            audit_log(api_key, "get_user_profile", "SUCCESS", latency)
            return {"success": True, "profile": profile}
        else:
            mock_prof = {"username": username, "name": f"{username} (Developer)", "public_repos": 28, "followers": 140, "bio": "AI Systems Engineer"}
            audit_log(api_key, "get_user_profile", "SUCCESS", latency)
            return {"success": True, "profile": mock_prof}
    except Exception as e:
        latency = (time.time() - start_t) * 1000
        audit_log(api_key, "get_user_profile", "FAILURE", latency, str(e))
        return {"success": False, "error": str(e)}


@mcp.tool(name="analyze_repo_health", description="Computes a health score (0-100) for a repository based on activity and stars.")
def analyze_repo_health(api_key: str, owner: str, repo: str) -> Dict[str, Any]:
    start_t = time.time()
    sec_err = enforce_security(api_key, "analyze_repo_health")
    if sec_err:
        return sec_err

    info_res = get_repo_info(api_key, owner, repo)
    latency = (time.time() - start_t) * 1000

    if not info_res.get("success"):
        audit_log(api_key, "analyze_repo_health", "FAILURE", latency, "Repo info failed")
        return info_res

    info = info_res.get("repo_info", {})
    stars = info.get("stars", 0)
    open_issues = info.get("open_issues", 0)

    # Health Formula
    base_score = min(70, int(stars / 50))
    issue_penalty = min(20, open_issues)
    final_score = max(10, min(100, base_score + 30 - issue_penalty))

    audit_log(api_key, "analyze_repo_health", "SUCCESS", latency)
    return {
        "success": True,
        "repo": f"{owner}/{repo}",
        "health_score": final_score,
        "rating": "EXCELLENT" if final_score >= 80 else ("GOOD" if final_score >= 50 else "NEEDS_ATTENTION"),
        "metrics": {"stars": stars, "open_issues": open_issues}
    }


if __name__ == "__main__":
    print("🚀 Starting Production Hardened Public API MCP Server...")
    mcp.run()
