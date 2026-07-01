"""
Week 2 - Day 3: Tool Calling Demo
Demonstrating tool calling with LangChain and Groq
"""

import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

load_dotenv()
console = Console()

# ─── Define Tools ───

@tool
def weather_lookup(city: str) -> str:
    """
    Get current weather for a city (mock data).
    
    Args:
        city: The city name
    
    Returns:
        str: Weather information
    """
    weather_data = {
        "london": "12°C, Rainy",
        "paris": "22°C, Sunny",
        "new york": "18°C, Partly Cloudy",
        "tokyo": "16°C, Light Rain",
        "dubai": "38°C, Very Hot",
        "karachi": "32°C, Humid",
        "islamabad": "28°C, Clear",
        "lahore": "34°C, Hot"
    }
    
    city_lower = city.lower()
    for key, value in weather_data.items():
        if key in city_lower or city_lower in key:
            return f"Weather in {city}: {value}"
    
    return f"Weather data not available for {city}"

@tool
def calculator(expression: str) -> str:
    """
    Calculate mathematical expressions.
    
    Args:
        expression: Math expression to calculate
    
    Returns:
        str: Result
    """
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {expression} = {result}"
    except Exception as e:
        return f"Error: {str(e)}"

# ─── Tool Binding ───

def demo_tool_binding():
    """Demonstrate tool binding with LangChain"""
    
    console.print(Panel(
        "[bold]Tool Binding with LangChain[/bold]\n"
        "Binding tools to ChatModels for function calling",
        border_style="cyan"
    ))
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    # Bind tools
    tools = [weather_lookup, calculator]
    llm_with_tools = llm.bind_tools(tools)
    
    console.print("\n[bold cyan]Tools Bound:[/bold cyan]")
    for tool in tools:
        console.print(f"  * {tool.name}: {tool.description[:50]}...")
    
    # Test weather lookup
    console.print("\n[bold]Test 1: Weather Lookup[/bold]")
    messages = [HumanMessage(content="What's the weather in London?")]
    response = llm_with_tools.invoke(messages)
    
    if hasattr(response, 'tool_calls') and response.tool_calls:
        console.print(f"Tool called: {response.tool_calls[0]['name']}")
        console.print(f"Args: {response.tool_calls[0]['args']}")
        
        # Execute tool
        tool_name = response.tool_calls[0]['name']
        tool_args = response.tool_calls[0]['args']
        
        if tool_name == "weather_lookup":
            result = weather_lookup.invoke(tool_args)
            console.print(f"Result: {result}")
    else:
        console.print("No tool call made")
    
    # Test calculator
    console.print("\n[bold]Test 2: Calculator[/bold]")
    messages = [HumanMessage(content="Calculate 25 * 4 + 10")]
    response = llm_with_tools.invoke(messages)
    
    if hasattr(response, 'tool_calls') and response.tool_calls:
        console.print(f"Tool called: {response.tool_calls[0]['name']}")
        console.print(f"Args: {response.tool_calls[0]['args']}")
        
        tool_name = response.tool_calls[0]['name']
        tool_args = response.tool_calls[0]['args']
        
        if tool_name == "calculator":
            result = calculator.invoke(tool_args)
            console.print(f"Result: {result}")
    else:
        console.print("No tool call made")

# ─── Tool Schema Design ───

def demo_tool_schema():
    """Demonstrate tool schema design following OpenAI format"""
    
    console.print(Panel(
        "[bold]Tool Schema Design[/bold]\n"
        "Following OpenAI function calling specification",
        border_style="cyan"
    ))
    
    schema = {
        "name": "send_email",
        "description": "Send an email to a specified recipient",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "Email address of the recipient"
                },
                "subject": {
                    "type": "string",
                    "description": "Subject line of the email"
                },
                "body": {
                    "type": "string",
                    "description": "Body content of the email"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "normal", "high"],
                    "description": "Priority level of the email"
                }
            },
            "required": ["to", "subject", "body"]
        }
    }
    
    console.print(json.dumps(schema, indent=2))
    
    console.print("\n[bold green]Schema Components:[/bold green]")
    console.print("  * name: Function name")
    console.print("  * description: What the function does")
    console.print("  * parameters: JSON schema for arguments")
    console.print("  * required: Required parameters")

# ─── Tool Lifecycle ───

def demo_tool_lifecycle():
    """Demonstrate the tool-calling lifecycle"""
    
    console.print(Panel(
        "[bold]Tool-Calling Lifecycle[/bold]\n"
        "Step by step of how tool calling works",
        border_style="cyan"
    ))
    
    steps = [
        ("1. User Input", "User asks a question that requires a tool"),
        ("2. Model Reasoning", "Model understands the request and decides a tool is needed"),
        ("3. Tool Selection", "Model selects the appropriate tool from available tools"),
        ("4. Tool Execution", "Tool is executed with the provided arguments"),
        ("5. Result Processing", "Model processes the tool result"),
        ("6. Response Generation", "Model generates final response to user")
    ]
    
    table = Table(title="Tool Calling Lifecycle", box=Table.box.ROUNDED)
    table.add_column("Step", style="cyan", width=20)
    table.add_column("Description", style="white")
    
    for step, desc in steps:
        table.add_row(step, desc)
    
    console.print(table)
    
    console.print("\n[bold yellow]Example:[/bold yellow]")
    console.print("User: 'What's the weather in London?'")
    console.print("-> Step 1: User input received")
    console.print("-> Step 2: Model recognizes weather query")
    console.print("-> Step 3: Model selects weather_lookup tool")
    console.print("-> Step 4: Tool executes with city='London'")
    console.print("-> Step 5: Model receives weather data")
    console.print("-> Step 6: Model responds with weather information")

# ─── Main ───

def main():
    """Main entry point"""
    
    console.print(Panel.fit(
        "[bold white]Week 2 - Day 3: Tool Calling Demo[/bold white]\n"
        "[cyan]Tool Binding, Schema Design, and Lifecycle[/cyan]",
        border_style="cyan"
    ))
    
    demos = [
        ("Tool Binding with LangChain", demo_tool_binding),
        ("Tool Schema Design", demo_tool_schema),
        ("Tool Calling Lifecycle", demo_tool_lifecycle)
    ]
    
    for name, func in demos:
        console.print(f"\n{'='*70}")
        console.print(f"[bold cyan]{name}[/bold cyan]")
        console.print("="*70)
        func()
        
        if name != demos[-1][0]:
            input("\nPress Enter to continue...")
    
    console.print("\n[bold green]All demonstrations complete![/bold green]")

if __name__ == "__main__":
    main()
