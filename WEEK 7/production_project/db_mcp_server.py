"""
Production Project 7-P-A: Database MCP Server
Namespace: db:*
Tools:
- db:describe_schema
- db:query_table
- db:insert_record
"""

import os
import sqlite3
import datetime
from typing import Dict, Any
from fastmcp import FastMCP

mcp = FastMCP(
    name="DatabaseEnterpriseServer",
    instructions="Production Database MCP Server providing SQLite relational schema tools."
)

DB_PATH = os.path.join("data", "enterprise_db.db")
os.makedirs("data", exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            plan_tier TEXT DEFAULT 'Enterprise',
            monthly_spend REAL DEFAULT 15000.0,
            created_at TEXT NOT NULL
        )
    ''')
    cur.execute("SELECT COUNT(*) FROM accounts")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO accounts (company_name, plan_tier, monthly_spend, created_at) VALUES ('Acme Corp', 'Enterprise', 25000.0, '2026-08-01')")
        cur.execute("INSERT INTO accounts (company_name, plan_tier, monthly_spend, created_at) VALUES ('TechGlobal', 'Pro', 12000.0, '2026-08-05')")
    conn.commit()
    conn.close()

init_db()


@mcp.tool(name="describe_schema", description="Returns table schemas for the database.")
def describe_schema() -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [r[0] for r in cur.fetchall()]
    conn.close()
    return {"success": True, "tables": tables}


@mcp.tool(name="query_table", description="Queries records from a database table.")
def query_table(table_name: str = "accounts", limit: int = 10) -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM accounts LIMIT ?", (limit,))
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    conn.close()
    records = [dict(zip(cols, r)) for r in rows]
    return {"success": True, "table": "accounts", "count": len(records), "records": records}


@mcp.tool(name="insert_record", description="Inserts a new enterprise account record.")
def insert_record(company_name: str, plan_tier: str = "Enterprise", monthly_spend: float = 10000.0) -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    dt = datetime.date.today().isoformat()
    cur.execute("INSERT INTO accounts (company_name, plan_tier, monthly_spend, created_at) VALUES (?, ?, ?, ?)", (company_name, plan_tier, monthly_spend, dt))
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"success": True, "inserted_id": new_id, "company_name": company_name}


if __name__ == "__main__":
    mcp.run()
