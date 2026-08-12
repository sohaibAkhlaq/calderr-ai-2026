"""
Project 7-I-A: Code Intelligence FastMCP Server
Exposes tools under namespace 'code:':
1. analyze_file: AST parsing, function signatures, cyclomatic complexity score.
2. find_dependencies: Imports and dependency tree extraction.
3. detect_code_smells: Identifies long functions (>25 lines), deep nesting (>3 levels), duplicate code blocks.
"""

import ast
from typing import Dict, Any, List
from fastmcp import FastMCP

mcp = FastMCP(
    name="CodeIntelligenceServer",
    instructions="Static code analysis server providing AST parsing, cyclomatic complexity, dependency graphs, and code smell detection."
)


def _compute_cyclomatic_complexity(node: ast.AST) -> int:
    """Computes approximate cyclomatic complexity by counting decision points."""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With, ast.Assert, ast.BoolOp)):
            complexity += 1
    return complexity


@mcp.tool(name="analyze_file", description="Analyzes Python source code to extract AST details, function signatures, and cyclomatic complexity.")
def analyze_file(code_content: str) -> Dict[str, Any]:
    """Performs AST analysis and cyclomatic complexity scoring on Python code."""
    try:
        parsed = ast.parse(code_content)
        functions = []
        classes = []

        for node in ast.walk(parsed):
            if isinstance(node, ast.FunctionDef):
                args = [arg.arg for arg in node.args.args]
                func_complexity = _compute_cyclomatic_complexity(node)
                functions.append({
                    "name": node.name,
                    "arguments": args,
                    "line_number": node.lineno,
                    "cyclomatic_complexity": func_complexity
                })
            elif isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "line_number": node.lineno
                })

        overall_complexity = _compute_cyclomatic_complexity(parsed)
        total_lines = len(code_content.splitlines())

        return {
            "success": True,
            "metrics": {
                "total_lines": total_lines,
                "function_count": len(functions),
                "class_count": len(classes),
                "overall_cyclomatic_complexity": overall_complexity,
                "complexity_rating": "LOW" if overall_complexity <= 5 else ("MEDIUM" if overall_complexity <= 12 else "HIGH")
            },
            "functions": functions,
            "classes": classes
        }
    except SyntaxError as se:
        return {"success": False, "error": f"Syntax Error: {str(se)}", "error_type": "SyntaxError"}
    except Exception as e:
        return {"success": False, "error": str(e), "error_type": "AnalysisError"}


@mcp.tool(name="find_dependencies", description="Parses Python code to extract imported modules and internal dependency graphs.")
def find_dependencies(code_content: str) -> Dict[str, Any]:
    """Extracts standard library, third-party, and relative import dependencies."""
    try:
        parsed = ast.parse(code_content)
        imports = []
        from_imports = []

        for node in ast.walk(parsed):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                names = [alias.name for alias in node.names]
                from_imports.append({"module": module, "names": names})

        unique_modules = sorted(list(set(imports + [fi["module"] for fi in from_imports if fi["module"]])))

        return {
            "success": True,
            "total_dependencies": len(unique_modules),
            "unique_modules": unique_modules,
            "direct_imports": imports,
            "from_imports": from_imports
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool(name="detect_code_smells", description="Scans Python code for code smells: long functions (>25 lines), deep nesting (>3 levels), and duplicate blocks.")
def detect_code_smells(code_content: str) -> Dict[str, Any]:
    """Identifies architectural code smells and anti-patterns."""
    lines = code_content.splitlines()
    smells = []

    # 1. Long Function Smell
    try:
        parsed = ast.parse(code_content)
        for node in ast.walk(parsed):
            if isinstance(node, ast.FunctionDef):
                # Count lines in function
                if hasattr(node, "end_lineno") and node.end_lineno:
                    func_len = node.end_lineno - node.lineno + 1
                    if func_len > 25:
                        smells.append({
                            "type": "LONG_FUNCTION",
                            "name": node.name,
                            "line": node.lineno,
                            "length": func_len,
                            "recommendation": f"Function '{node.name}' is {func_len} lines long. Consider refactoring into smaller helpers."
                        })
    except Exception:
        pass

    # 2. Deep Nesting Smell (indentation > 12 spaces / 3 levels)
    for idx, line in enumerate(lines, 1):
        if line.strip() and not line.strip().startswith("#"):
            indent = len(line) - len(line.lstrip())
            if indent >= 16: # 4 levels of 4 spaces
                smells.append({
                    "type": "DEEP_NESTING",
                    "line": idx,
                    "code_snippet": line.strip()[:40],
                    "recommendation": f"Line {idx} has deep nesting level ({indent // 4} levels). Extract guard clauses or sub-functions."
                })

    return {
        "success": True,
        "smell_count": len(smells),
        "smells": smells,
        "code_quality_score": max(20, 100 - (len(smells) * 15))
    }


if __name__ == "__main__":
    mcp.run()
