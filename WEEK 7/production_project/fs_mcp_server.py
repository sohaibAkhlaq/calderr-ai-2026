"""
Production Project 7-P-A: Filesystem MCP Server
Namespace: fs:*
Tools:
- fs:read_file
- fs:write_file
- fs:list_directory
- fs:search_files
"""

import os
from typing import Dict, Any
from fastmcp import FastMCP

mcp = FastMCP(
    name="FilesystemEnterpriseServer",
    instructions="Production Filesystem MCP Server providing sandboxed file operations."
)

SANDBOX_DIR = os.path.join("data", "enterprise_sandbox")
os.makedirs(SANDBOX_DIR, exist_ok=True)


def _safe_path(filename: str) -> str:
    clean = os.path.basename(filename)
    return os.path.join(SANDBOX_DIR, clean)


@mcp.tool(name="read_file", description="Reads sandboxed text file content.")
def read_file(filename: str) -> Dict[str, Any]:
    fp = _safe_path(filename)
    if not os.path.exists(fp):
        return {"success": False, "error": f"File '{filename}' not found."}
    with open(fp, "r", encoding="utf-8") as f:
        data = f.read()
    return {"success": True, "filename": filename, "content": data}


@mcp.tool(name="write_file", description="Writes text content to a sandboxed file.")
def write_file(filename: str, content: str) -> Dict[str, Any]:
    fp = _safe_path(filename)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)
    return {"success": True, "filename": filename, "bytes_written": len(content.encode('utf-8'))}


@mcp.tool(name="list_directory", description="Lists all files in the enterprise sandbox.")
def list_directory() -> Dict[str, Any]:
    files = os.listdir(SANDBOX_DIR)
    details = [{"filename": f, "size_bytes": os.path.getsize(os.path.join(SANDBOX_DIR, f))} for f in files]
    return {"success": True, "file_count": len(files), "files": details}


@mcp.tool(name="search_files", description="Searches sandboxed text files by keyword.")
def search_files(keyword: str) -> Dict[str, Any]:
    clean_k = keyword.strip().lower()
    matches = []
    for fn in os.listdir(SANDBOX_DIR):
        fp = os.path.join(SANDBOX_DIR, fn)
        try:
            with open(fp, "r", encoding="utf-8") as f:
                txt = f.read()
                if clean_k in txt.lower():
                    matches.append({"filename": fn, "matches": txt.lower().count(clean_k)})
        except Exception:
            pass
    return {"success": True, "keyword": keyword, "matches": matches}


if __name__ == "__main__":
    mcp.run()
