"""
Week 2 - Day 3: Lab 2.2 - Multi-Tool Research Agent
Building a 5-tool agent with tool calling
Tools: search_db, calculate, format_date, convert_currency, summarize_text
"""

import os
import json
import re
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

load_dotenv()
console = Console()

# ─── Tool 1: Search Database ───

@tool
def search_database(query: str) -> str:
    """
    Search a mock database of facts and information.
    Use this when the user asks about facts, historical events, or general knowledge.
    
    Args:
        query: The search query or question
    
    Returns:
        str: Search results from the database
    """
    
    # Mock database
    DATABASE = {
        "capital of france": "Paris",
        "capital of germany": "Berlin",
        "capital of italy": "Rome",
        "capital of spain": "Madrid",
        "capital of uk": "London",
        "capital of japan": "Tokyo",
        "largest ocean": "Pacific Ocean",
        "tallest mountain": "Mount Everest (8,848 meters)",
        "longest river": "Nile River (6,650 km)",
        "population of china": "1.4 billion",
        "population of india": "1.3 billion",
        "population of usa": "331 million",
        "inventor of python": "Guido van Rossum",
        "inventor of c": "Dennis Ritchie",
        "inventor of java": "James Gosling",
        "year of independence pakistan": "1947",
        "founder of pakistan": "Quaid-e-Azam Muhammad Ali Jinnah",
        "national language pakistan": "Urdu",
        "capital of pakistan": "Islamabad"
    }
    
    query_lower = query.lower()
    results = []
    
    for key, value in DATABASE.items():
        if key in query_lower or query_lower in key:
            results.append(f"{key.title()}: {value}")
    
    if results:
        return "Found:\n" + "\n".join(results)
    else:
        return f"No results found for '{query}'. Try rephrasing your question."

# ─── Tool 2: Calculate ───

@tool
def calculate(expression: str) -> str:
    """
    Calculate mathematical expressions. Use this when the user asks for math calculations.
    
    Args:
        expression: The mathematical expression to calculate (e.g., '25 * 4 + 10')
    
    Returns:
        str: The calculation result
    """
    
    # Clean expression
    clean_expr = re.sub(r'[^0-9+\-*/().^% ]', '', expression)
    
    try:
        if not clean_expr:
            return "Error: No valid expression provided."
        
        # Safely evaluate
        result = eval(clean_expr, {"__builtins__": {}}, {})
        return f"{expression} = {result}"
    except ZeroDivisionError:
        return "Error: Division by zero is not allowed."
    except Exception as e:
        return f"Error: Invalid expression - {str(e)}"

# ─── Tool 3: Format Date ───

@tool
def format_date(date_input: str, format_type: str = "standard") -> str:
    """
    Format or calculate dates. Use this when the user asks about dates, days, or time.
    
    Args:
        date_input: A date string (e.g., '2026-06-30') or relative phrase (e.g., 'today', 'tomorrow')
        format_type: Output format - 'standard', 'long', or 'iso'
    
    Returns:
        str: Formatted date information
    """
    
    try:
        # Handle relative dates
        if date_input.lower() == "today":
            date_obj = datetime.now()
        elif date_input.lower() == "tomorrow":
            date_obj = datetime.now() + timedelta(days=1)
        elif date_input.lower() == "yesterday":
            date_obj = datetime.now() - timedelta(days=1)
        elif date_input.lower().startswith("+"):
            days = int(re.search(r'\d+', date_input).group())
            date_obj = datetime.now() + timedelta(days=days)
        elif date_input.lower().startswith("-"):
            days = int(re.search(r'\d+', date_input).group())
            date_obj = datetime.now() - timedelta(days=days)
        else:
            date_obj = datetime.strptime(date_input, "%Y-%m-%d")
        
        # Format output
        if format_type == "long":
            result = date_obj.strftime("%A, %B %d, %Y at %I:%M %p")
        elif format_type == "iso":
            result = date_obj.strftime("%Y-%m-%d")
        else:
            result = date_obj.strftime("%A, %B %d, %Y")
        
        return f"Date: {result}"
        
    except ValueError:
        return f"Error: Could not parse date '{date_input}'. Use format YYYY-MM-DD."
    except Exception as e:
        return f"Error: {str(e)}"

# ─── Tool 4: Convert Currency ───

@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Convert between currencies using mock exchange rates.
    
    Args:
        amount: The amount to convert
        from_currency: Source currency code (USD, EUR, GBP, PKR, JPY, CAD)
        to_currency: Target currency code (USD, EUR, GBP, PKR, JPY, CAD)
    
    Returns:
        str: Conversion result
    """
    
    # Mock exchange rates (as of 2026)
    EXCHANGE_RATES = {
        "USD": 1.0,
        "EUR": 0.85,
        "GBP": 0.72,
        "PKR": 279.0,
        "JPY": 157.0,
        "CAD": 1.36
    }
    
    from_curr = from_currency.upper()
    to_curr = to_currency.upper()
    
    if from_curr not in EXCHANGE_RATES:
        return f"Error: Unknown currency '{from_currency}'. Supported: USD, EUR, GBP, PKR, JPY, CAD"
    if to_curr not in EXCHANGE_RATES:
        return f"Error: Unknown currency '{to_currency}'. Supported: USD, EUR, GBP, PKR, JPY, CAD"
    
    # Convert to USD first
    usd_amount = amount / EXCHANGE_RATES[from_curr]
    # Convert to target currency
    converted = usd_amount * EXCHANGE_RATES[to_curr]
    
    return f"{amount:,.2f} {from_curr} = {converted:,.2f} {to_curr}"

# ─── Tool 5: Summarize Text ───

@tool
def summarize_text(text: str, max_length: int = 50) -> str:
    """
    Summarize a piece of text. Use this when the user wants a summary of a long text.
    
    Args:
        text: The text to summarize
        max_length: Maximum number of words in the summary
    
    Returns:
        str: The summarized text
    """
    
    words = text.split()
    
    if len(words) <= max_length:
        return f"Summary: {text}"
    
    # Simple summarization using first and last sentences
    sentences = re.split(r'[.!?]+', text)
    
    if len(sentences) <= 3:
        # If only 3 sentences, return all
        summary = " ".join(sentences[:3])
    else:
        # Take first 2 sentences and last sentence
        summary = sentences[0] + ". " + sentences[1] + ". ... " + sentences[-1] + "."
    
    return f"Summary ({len(words)} words -> summarized): {summary}"

# ─── Tool Registry ───

class ToolRegistry:
    """Registry for all tools with routing logic"""
    
    def __init__(self):
        self.tools = {
            "search": {
                "func": search_database,
                "keywords": ["what is", "who is", "capital", "population", "inventor", "when did", "how many", "what are", "tell me about", "founder", "language", "country", "city", "river", "mountain", "ocean", "history", "independence", "national"],
                "description": "Search database for facts and general knowledge"
            },
            "calculate": {
                "func": calculate,
                "keywords": ["calculate", "math", "add", "multiply", "divide", "subtract", "+", "-", "*", "/", "sum", "difference", "product", "quotient", "power", "square", "sqrt", "percentage"],
                "description": "Calculate mathematical expressions"
            },
            "date": {
                "func": format_date,
                "keywords": ["date", "today", "tomorrow", "yesterday", "day", "week", "month", "year", "time", "when"],
                "description": "Format or calculate dates"
            },
            "currency": {
                "func": convert_currency,
                "keywords": ["convert", "currency", "exchange", "usd", "eur", "gbp", "pkr", "jpy", "cad", "dollar", "euro", "pound", "rupee"],
                "description": "Convert between currencies"
            },
            "summarize": {
                "func": summarize_text,
                "keywords": ["summarize", "summary", "brief", "shorten", "condense"],
                "description": "Summarize text"
            }
        }
    
    def select_tool(self, query: str) -> str:
        """Select the most appropriate tool based on keywords"""
        
        query_lower = query.lower()
        
        best_tool = "search"
        best_score = 0
        
        for tool_name, tool_info in self.tools.items():
            score = 0
            for keyword in tool_info["keywords"]:
                if keyword in query_lower:
                    score += 1
            if score > best_score:
                best_score = score
                best_tool = tool_name
        
        return best_tool
    
    def get_tool(self, tool_name: str):
        """Get a tool by name"""
        return self.tools.get(tool_name, {}).get("func")

# ─── Multi-Tool Agent ───

class MultiToolAgent:
    """Agent with 5 tools that routes queries to the right tool"""
    
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.registry = ToolRegistry()
        self.history = []
        self.tool_calls = []
    
    def process_query(self, query: str) -> str:
        """Process a user query by selecting and calling the right tool"""
        
        console.print(f"\n[dim]Processing: {query}[/dim]")
        
        # Step 1: Select tool
        selected_tool_name = self.registry.select_tool(query)
        tool_func = self.registry.get_tool(selected_tool_name)
        
        console.print(f"[dim]Selected tool: {selected_tool_name}[/dim]")
        
        # Step 2: Call tool
        try:
            tool_description = self.registry.tools[selected_tool_name]["description"]
            result = tool_func(query)
            
            # Log tool call
            self.tool_calls.append({
                "query": query,
                "tool": selected_tool_name,
                "result": result
            })
            
            # Add to history
            self.history.append({
                "user": query,
                "tool": selected_tool_name,
                "response": result
            })
            
            return result
            
        except Exception as e:
            error_msg = f"Error calling {selected_tool_name}: {str(e)}"
            self.history.append({
                "user": query,
                "tool": selected_tool_name,
                "response": error_msg
            })
            return error_msg
    
    def show_history(self):
        """Display conversation history"""
        
        console.print("\n" + "="*70)
        console.print("[bold cyan]AGENT HISTORY[/bold cyan]")
        console.print("="*70)
        
        table = Table(title="Conversation History", box=box.ROUNDED)
        table.add_column("#", style="dim", width=3)
        table.add_column("User Query", style="cyan")
        table.add_column("Tool Used", style="yellow")
        table.add_column("Response", style="green")
        
        for i, entry in enumerate(self.history, 1):
            table.add_row(
                str(i),
                entry["user"][:30] + "..." if len(entry["user"]) > 30 else entry["user"],
                entry["tool"],
                entry["response"][:40] + "..." if len(entry["response"]) > 40 else entry["response"]
            )
        
        console.print(table)
    
    def show_stats(self):
        """Show tool usage statistics"""
        
        console.print("\n" + "="*70)
        console.print("[bold cyan]TOOL USAGE STATISTICS[/bold cyan]")
        console.print("="*70)
        
        if not self.tool_calls:
            console.print("No tool calls recorded yet.")
            return
        
        # Count tool usage
        tool_counts = {}
        for call in self.tool_calls:
            tool_name = call["tool"]
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
        
        table = Table(title="Tool Usage", box=box.ROUNDED)
        table.add_column("Tool", style="cyan")
        table.add_column("Calls", style="yellow", justify="center")
        table.add_column("Percentage", style="green", justify="center")
        
        total = sum(tool_counts.values())
        for tool_name, count in sorted(tool_counts.items(), key=lambda x: -x[1]):
            percentage = (count / total) * 100
            table.add_row(tool_name, str(count), f"{percentage:.1f}%")
        
        console.print(table)
        console.print(f"Total Tool Calls: {total}")

# ─── Test Cases ───

def run_tests(agent: MultiToolAgent):
    """Run test cases for all tools"""
    
    console.print("\n[bold cyan]Running Test Cases...[/bold cyan]\n")
    
    test_queries = [
        # Search tests
        "What is the capital of France?",
        "Who is the founder of Pakistan?",
        "What is the largest ocean?",
        "When did Pakistan get independence?",
        "What is the population of India?",
        
        # Calculate tests
        "Calculate 25 * 4 + 10",
        "What is 100 / 4?",
        "Calculate 2 + 3 * 4",
        "What is 15% of 200?",
        "Calculate 7 * 8",
        
        # Date tests
        "What is today's date?",
        "What day is tomorrow?",
        "What is the date 5 days from now?",
        "Format date 2026-07-04 in long format",
        
        # Currency tests
        "Convert 100 USD to PKR",
        "Convert 50 EUR to GBP",
        "Convert 1000 PKR to USD",
        
        # Summarize tests
        "Summarize this: AI is transforming every industry. It helps doctors diagnose diseases faster. It helps banks detect fraud. It helps teachers personalize education."
    ]
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        console.print(f"[{i}/{len(test_queries)}] Testing: {query}")
        result = agent.process_query(query)
        console.print(f"  -> {result}\n")
        results.append({"query": query, "result": result})
    
    console.print("[bold green]All tests completed![/bold green]")
    return results

# ─── Interactive Chat ───

def interactive_chat(agent: MultiToolAgent):
    """Interactive chat mode"""
    
    console.print("\n" + "="*70)
    console.print("[bold cyan]INTERACTIVE MODE[/bold cyan]")
    console.print("Available Tools:")
    console.print("  [search_db]        - Search facts and general knowledge")
    console.print("  [calculate]        - Mathematical calculations")
    console.print("  [format_date]      - Date formatting and calculations")
    console.print("  [convert_currency] - Currency conversion")
    console.print("  [summarize_text]   - Text summarization")
    console.print("")
    console.print("Commands: /history, /stats, /help, /exit")
    console.print("="*70)
    
    while True:
        try:
            query = input("\nYou: ").strip()
            
            if not query:
                continue
            
            if query.lower() == '/exit':
                console.print("\nGoodbye!")
                break
            
            if query.lower() == '/history':
                agent.show_history()
                continue
            
            if query.lower() == '/stats':
                agent.show_stats()
                continue
            
            if query.lower() == '/help':
                console.print("\n[bold]Commands:[/bold]")
                console.print("  /history  - Show conversation history")
                console.print("  /stats    - Show tool usage statistics")
                console.print("  /help     - Show this help message")
                console.print("  /exit     - Exit")
                console.print("\n[bold]Try asking:[/bold]")
                console.print("  What is the capital of France?")
                console.print("  Calculate 25 * 4 + 10")
                console.print("  What is today's date?")
                console.print("  Convert 100 USD to PKR")
                console.print("  Summarize this: [your text]")
                continue
            
            result = agent.process_query(query)
            console.print(f"\n[bold]Response:[/bold] {result}")
            
        except KeyboardInterrupt:
            console.print("\n\nGoodbye!")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

# ─── Main ───

def main():
    """Main entry point"""
    
    console.print(Panel.fit(
        "[bold white]Week 2 - Day 3: Multi-Tool Research Agent[/bold white]\n"
        "[cyan]Lab 2.2 - 5-Tool Agent with Routing[/cyan]",
        border_style="cyan"
    ))
    
    agent = MultiToolAgent()
    
    console.print("\n[bold cyan]Tools Available:[/bold cyan]")
    console.print("  1. [search_db]        - Search facts and general knowledge")
    console.print("  2. [calculate]        - Mathematical calculations")
    console.print("  3. [format_date]      - Date formatting and calculations")
    console.print("  4. [convert_currency] - Currency conversion")
    console.print("  5. [summarize_text]   - Text summarization")
    
    # Run tests
    run_tests(agent)
    
    # Interactive mode
    interactive_chat(agent)

if __name__ == "__main__":
    main()
