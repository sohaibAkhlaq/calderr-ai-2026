"""
Project 7-I-A: GitHub FastMCP Server
Exposes tools under namespace 'gh:':
1. list_open_prs: Lists open pull requests.
2. get_pr_diff: Fetches code diff for a specified PR ID.
3. create_issue: Registers a GitHub issue or PR review ticket.
4. search_repo_code: Searches codebase by keyword.
5. get_recent_commits: Fetches recent git commit history.
"""

import datetime
from typing import Dict, Any, List
from fastmcp import FastMCP

mcp = FastMCP(
    name="GitHubMCPServer",
    instructions="GitHub interaction server providing PR management, code diff analysis, issue creation, and commit tracking."
)

# In-memory mock database of repository PRs and commits
MOCK_PRS = {
    101: {
        "pr_id": 101,
        "title": "Refactor User Authentication & Password Hashing",
        "author": "dev_alice",
        "status": "OPEN",
        "branch": "feature/auth-refactor",
        "created_at": "2026-08-10",
        "diff": """--- a/auth.py
+++ b/auth.py
@@ -1,5 +1,12 @@
-def login(username, password):
-    if username == "admin" and password == "secret":
-        return True
-    return False
+import hashlib
+
+def hash_password(plain: str) -> str:
+    return hashlib.sha256(plain.encode('utf-8')).hexdigest()
+
+def login(username: str, password_hash: str) -> dict:
+    if not username or not password_hash:
+        return {"success": False, "error": "Missing credentials"}
+    # Query DB securely
+    return {"success": True, "username": username}
"""
    },
    102: {
        "pr_id": 102,
        "title": "Add FastMCP Vector Memory Store Integration",
        "author": "dev_bob",
        "status": "OPEN",
        "branch": "feature/mcp-memory",
        "created_at": "2026-08-11",
        "diff": """--- a/memory.py
+++ b/memory.py
@@ -0,0 +1,15 @@
+class MemoryStore:
+    def __init__(self):
+        self.facts = []
+    def add_fact(self, fact: str):
+        self.facts.append(fact)
"""
    }
}

MOCK_ISSUES = []


@mcp.tool(name="list_open_prs", description="Lists all open pull requests in the repository.")
def list_open_prs() -> Dict[str, Any]:
    """Fetches open PRs list."""
    pr_summary = []
    for pr_id, pr in MOCK_PRS.items():
        if pr["status"] == "OPEN":
            pr_summary.append({
                "pr_id": pr["pr_id"],
                "title": pr["title"],
                "author": pr["author"],
                "branch": pr["branch"],
                "created_at": pr["created_at"]
            })
    return {"success": True, "open_pr_count": len(pr_summary), "pull_requests": pr_summary}


@mcp.tool(name="get_pr_diff", description="Fetches the unified git code diff for a given PR ID.")
def get_pr_diff(pr_id: int) -> Dict[str, Any]:
    """Fetches code diff by PR ID."""
    if pr_id not in MOCK_PRS:
        return {"success": False, "error": f"PR #{pr_id} not found.", "error_type": "PRNotFound"}

    pr = MOCK_PRS[pr_id]
    return {
        "success": True,
        "pr_id": pr_id,
        "title": pr["title"],
        "author": pr["author"],
        "diff": pr["diff"]
    }


@mcp.tool(name="create_issue", description="Creates a new GitHub issue or automated code review ticket.")
def create_issue(title: str, body: str, labels: str = "automated-review") -> Dict[str, Any]:
    """Creates a GitHub issue/ticket."""
    issue_id = len(MOCK_ISSUES) + 501
    new_issue = {
        "issue_id": issue_id,
        "title": title,
        "body": body,
        "labels": [l.strip() for l in labels.split(",")],
        "created_at": datetime.date.today().isoformat(),
        "status": "OPEN"
    }
    MOCK_ISSUES.append(new_issue)
    return {"success": True, "issue_id": issue_id, "title": title, "status": "OPEN"}


@mcp.tool(name="search_repo_code", description="Searches repository PR titles and code diffs for a keyword query.")
def search_repo_code(query: str) -> Dict[str, Any]:
    """Searches PR diffs and metadata."""
    clean_q = query.strip().lower()
    matches = []
    for pr_id, pr in MOCK_PRS.items():
        if clean_q in pr["title"].lower() or clean_q in pr["diff"].lower():
            matches.append({"pr_id": pr_id, "title": pr["title"], "author": pr["author"]})

    return {"success": True, "query": query, "match_count": len(matches), "matches": matches}


@mcp.tool(name="get_recent_commits", description="Fetches recent commit history for the repository.")
def get_recent_commits(limit: int = 5) -> Dict[str, Any]:
    """Returns recent commit list."""
    commits = [
        {"commit_hash": "a1b2c3d", "message": "feat: add FastMCP server integration", "author": "sohaib", "date": "2026-08-12"},
        {"commit_hash": "e5f6g7h", "message": "fix: update token bucket rate limiter window", "author": "sohaib", "date": "2026-08-11"},
        {"commit_hash": "i9j0k1l", "message": "docs: add Week 6 production report", "author": "sohaib", "date": "2026-08-10"}
    ]
    return {"success": True, "commit_count": len(commits[:limit]), "commits": commits[:limit]}


if __name__ == "__main__":
    mcp.run()
