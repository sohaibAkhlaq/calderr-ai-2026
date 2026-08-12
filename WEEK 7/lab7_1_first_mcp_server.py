"""
Lab 7.1: Three-Tool Production MCP Server
Builds an MCP server exposing 3 callable tools:
1. calculate: Evaluates math expressions safely using Python AST (no eval()).
2. string_processor: Performs text transformations (upper, lower, reverse, word_count, snake_case).
3. date_helper: Handles date math (now, add_days, diff_days, format_date).

Includes complete JSON Schemas, input validation, and structured error responses.
"""

import ast
import operator
import datetime
import sys
import json
from typing import Dict, Any, Union
from fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP(
    name="ThreeToolHelperServer",
    instructions="Production MCP server exposing safe math calculation, string processing, and date utility tools."
)


# =============================================================================
# TOOL 1: SAFE MATH CALCULATOR (AST Parsing, No eval)
# =============================================================================
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def eval_ast_node(node):
    if isinstance(node, ast.Constant): # numbers in Python 3.8+
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value)}")
    elif isinstance(node, ast.BinOp):
        left = eval_ast_node(node.left)
        right = eval_ast_node(node.right)
        op_type = type(node.op)
        if op_type in ALLOWED_OPERATORS:
            if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
                raise ZeroDivisionError("Division or modulo by zero is not allowed.")
            return ALLOWED_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported operator: {op_type.__name__}")
    elif isinstance(node, ast.UnaryOp):
        operand = eval_ast_node(node.operand)
        op_type = type(node.op)
        if op_type in ALLOWED_OPERATORS:
            return ALLOWED_OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
    else:
        raise ValueError(f"Unsupported AST syntax: {type(node).__name__}")


@mcp.tool(
    name="calculate",
    description="Safely evaluates mathematical expressions (+, -, *, /, %, **) using AST parsing without unsafe eval()."
)
def calculate(expression: str) -> Dict[str, Any]:
    """Safely evaluates a mathematical expression string."""
    try:
        if not expression or not expression.strip():
            return {"success": False, "error": "Expression string cannot be empty."}
            
        parsed = ast.parse(expression.strip(), mode='eval')
        result = eval_ast_node(parsed.body)
        return {
            "success": True,
            "expression": expression,
            "result": result,
            "result_type": type(result).__name__
        }
    except ZeroDivisionError as e:
        return {"success": False, "error": str(e), "error_type": "ZeroDivisionError"}
    except Exception as e:
        return {"success": False, "error": f"Invalid mathematical expression: {str(e)}", "error_type": "InvalidExpression"}


# =============================================================================
# TOOL 2: STRING PROCESSOR
# =============================================================================
@mcp.tool(
    name="string_processor",
    description="Performs text manipulation: 'upper', 'lower', 'reverse', 'word_count', or 'snake_case'."
)
def string_processor(text: str, operation: str) -> Dict[str, Any]:
    """Performs specified string operation on input text."""
    if not isinstance(text, str):
        return {"success": False, "error": "Input 'text' must be a string."}

    op = str(operation).strip().lower()
    
    if op == "upper":
        res = text.upper()
    elif op == "lower":
        res = text.lower()
    elif op == "reverse":
        res = text[::-1]
    elif op == "word_count":
        words = text.strip().split()
        res = len(words)
    elif op == "snake_case":
        clean = "".join([c if c.isalnum() else " " for c in text])
        res = "_".join(clean.lower().split())
    else:
        return {
            "success": False,
            "error": f"Unsupported operation '{operation}'. Allowed: upper, lower, reverse, word_count, snake_case.",
            "error_type": "InvalidOperation"
        }

    return {
        "success": True,
        "input_text": text,
        "operation": op,
        "result": res
    }


# =============================================================================
# TOOL 3: DATE HELPER
# =============================================================================
@mcp.tool(
    name="date_helper",
    description="Performs date operations: 'now', 'add_days' (date_str + days), 'diff_days' (date1 vs date2), 'format_date'."
)
def date_helper(action: str, date_str: str = "", days: int = 0) -> Dict[str, Any]:
    """Handles date utilities and date math calculations."""
    act = str(action).strip().lower()
    now_dt = datetime.datetime.now()

    try:
        if act == "now":
            return {
                "success": True,
                "action": "now",
                "iso_datetime": now_dt.isoformat(),
                "formatted": now_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "date": now_dt.strftime("%Y-%m-%d")
            }

        elif act == "add_days":
            base_dt = datetime.datetime.strptime(date_str, "%Y-%m-%d") if date_str else now_dt
            new_dt = base_dt + datetime.timedelta(days=days)
            return {
                "success": True,
                "action": "add_days",
                "base_date": base_dt.strftime("%Y-%m-%d"),
                "days_added": days,
                "result_date": new_dt.strftime("%Y-%m-%d")
            }

        elif act == "diff_days":
            if not date_str:
                return {"success": False, "error": "date_str is required for diff_days (format: YYYY-MM-DD)."}
            target_dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            diff = (target_dt.date() - now_dt.date()).days
            return {
                "success": True,
                "action": "diff_days",
                "target_date": date_str,
                "today_date": now_dt.strftime("%Y-%m-%d"),
                "days_difference": diff
            }

        elif act == "format_date":
            base_dt = datetime.datetime.strptime(date_str, "%Y-%m-%d") if date_str else now_dt
            return {
                "success": True,
                "action": "format_date",
                "date": base_dt.strftime("%Y-%m-%d"),
                "human_readable": base_dt.strftime("%A, %B %d, %Y")
            }

        else:
            return {
                "success": False,
                "error": f"Unsupported action '{action}'. Allowed: now, add_days, diff_days, format_date.",
                "error_type": "InvalidAction"
            }

    except ValueError as ve:
        return {"success": False, "error": f"Date parsing error. Use format YYYY-MM-DD. Error: {str(ve)}", "error_type": "DateFormatError"}
    except Exception as e:
        return {"success": False, "error": str(e), "error_type": "DateHelperError"}


# CLI entry point to run stdio or SSE server
if __name__ == "__main__":
    print("🚀 Starting FastMCP Server: ThreeToolHelperServer...")
    mcp.run()
