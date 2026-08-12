"""
Production Project 7-P-A: Code Intelligence MCP Server
Namespace: code:*
Tools:
- code:analyze_file
- code:find_dependencies
- code:detect_code_smells
"""

import ast
from typing import Dict, Any
from fastmcp import FastMCP

mcp = FastMCP(
    name="CodeIntelligenceEnterpriseServer",
    instructions="Production Code Intelligence MCP Server providing AST analysis and complexity metrics."
)


def _complexity(node: ast.AST) -> int:
    score = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With, ast.BoolOp)):
            score += 1
    return score


@mcp.tool(name="analyze_file", description="Analyzes Python source code for AST structure and complexity.")
def analyze_file(code_content: str) -> Dict[str, Any]:
    try:
        parsed = ast.parse(code_content)
        funcs = [n.name for n in ast.walk(parsed) if isinstance(n, ast.FunctionDef)]
        score = _complexity(parsed)
        return {
            "success": True,
            "line_count": len(code_content.splitlines()),
            "functions": funcs,
            "cyclomatic_complexity": score,
            "rating": "LOW" if score <= 5 else ("MEDIUM" if score <= 12 else "HIGH")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool(name="find_dependencies", description="Parses Python code to extract module imports.")
def find_dependencies(code_content: str) -> Dict[str, Any]:
    try:
        parsed = ast.parse(code_content)
        imports = []
        for node in ast.walk(parsed):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return {"success": True, "dependencies": sorted(list(set(imports)))}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool(name="detect_code_smells", description="Scans Python code for deep nesting and architectural code smells.")
def detect_code_smells(code_content: str) -> Dict[str, Any]:
    smells = []
    lines = code_content.splitlines()
    for idx, line in enumerate(lines, 1):
        indent = len(line) - len(line.lstrip())
        if indent >= 16:
            smells.append({"line": idx, "smell": "DEEP_NESTING", "snippet": line.strip()[:30]})
    return {"success": True, "smell_count": len(smells), "quality_score": max(20, 100 - len(smells) * 15), "smells": smells}


if __name__ == "__main__":
    mcp.run()
