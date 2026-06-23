"""
Week 1 - Day 2: Manual ReAct Agent
Agentic AI Concepts - ReAct Pattern Implementation
No frameworks used - pure Python implementation
"""

import re
import datetime
from typing import Dict, List, Tuple, Optional

# ─── Mock Database ───
MOCK_DATABASE = {
    "capital of france": "Paris",
    "capital of germany": "Berlin",
    "capital of italy": "Rome",
    "largest ocean": "Pacific Ocean",
    "tallest mountain": "Mount Everest",
    "population of china": "1.4 billion",
    "population of india": "1.3 billion",
    "inventor of python": "Guido van Rossum",
    "inventor of c": "Dennis Ritchie",
    "inventor of java": "James Gosling",
}

# ─── Tools ───

def search_database(query: str) -> str:
    """
    Tool 1: Search mock database for facts.
    Returns matching fact or error message.
    """
    query_lower = query.lower()
    for key, value in MOCK_DATABASE.items():
        if key in query_lower or query_lower in key:
            return f"Found: {key} → {value}"
    return "No matching fact found in database."

def calculate(expression: str) -> str:
    """
    Tool 2: Calculate math expressions using eval().
    Returns result or error message.
    """
    # Remove any non-math characters for safety
    clean_expr = re.sub(r'[^0-9+\-*/(). ]', '', expression)
    try:
        if not clean_expr:
            return "Error: No valid expression provided."
        result = eval(clean_expr)
        return f"Result: {clean_expr} = {result}"
    except Exception as e:
        return f"Error: Invalid expression - {str(e)}"

def get_current_time() -> str:
    """
    Tool 3: Get current date and time.
    Returns formatted datetime string.
    """
    now = datetime.datetime.now()
    return f"Current time: {now.strftime('%A, %B %d, %Y at %I:%M %p')}"

# ─── Tool Registry ───

TOOLS = {
    "search": {
        "func": search_database,
        "description": "Search database for facts about capitals, populations, inventors, geography",
        "keywords": ["capital", "population", "inventor", "ocean", "mountain", "largest"]
    },
    "calculate": {
        "func": calculate,
        "description": "Calculate math expressions (e.g., 25 * 4 + 10)",
        "keywords": ["calculate", "math", "add", "multiply", "divide", "subtract", "+", "-", "*", "/"]
    },
    "time": {
        "func": get_current_time,
        "description": "Get current date and time",
        "keywords": ["time", "date", "today", "now", "current"]
    }
}

# ─── Agent ───

class ReActAgent:
    """
    Manual ReAct Agent - No frameworks used.
    Perceive → Reason → Plan → Act → Observe → Repeat
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.history: List[Dict[str, str]] = []
        self.max_iterations = 5
    
    def perceive(self, user_input: str) -> str:
        """Step 1: Perceive - Receive and understand input"""
        self.history.append({"role": "user", "content": user_input})
        if self.verbose:
            print(f"\n[PERCEIVE] User: {user_input}")
        return user_input
    
    def reason(self, user_input: str) -> str:
        """Step 2: Reason - Analyze the problem and decide what to do"""
        # Check which tool to use based on keywords
        selected_tool = None
        input_lower = user_input.lower()
        
        for tool_name, tool_info in TOOLS.items():
            for keyword in tool_info["keywords"]:
                if keyword in input_lower or keyword in user_input:
                    selected_tool = tool_name
                    break
            if selected_tool:
                break
        
        # Default to search if no tool matches
        if not selected_tool:
            selected_tool = "search"
        
        if self.verbose:
            print(f"[REASON] Analyzing input: {user_input}")
            print(f"[REASON] Selected tool: {selected_tool}")
        
        return selected_tool
    
    def plan(self, tool: str, user_input: str) -> Dict[str, str]:
        """Step 3: Plan - Decide the action to take"""
        plan = {
            "tool": tool,
            "action": f"Call {tool} tool",
            "input": user_input
        }
        if self.verbose:
            print(f"[PLAN] Action: {plan['action']}")
        return plan
    
    def act(self, plan: Dict[str, str]) -> str:
        """Step 4: Act - Execute the action using the selected tool"""
        tool_name = plan["tool"]
        tool_input = plan["input"]
        
        if self.verbose:
            print(f"[ACT] Executing {tool_name} with input: {tool_input}")
        
        tool_info = TOOLS.get(tool_name)
        if not tool_info:
            return f"Error: Tool '{tool_name}' not found."
        
        result = tool_info["func"](tool_input)
        return result
    
    def observe(self, result: str) -> str:
        """Step 5: Observe - See the result of the action"""
        if self.verbose:
            print(f"[OBSERVE] Result: {result[:100]}...")
        self.history.append({"role": "assistant", "content": result})
        return result
    
    def run(self, user_input: str) -> str:
        """
        Full agent loop: Perceive → Reason → Plan → Act → Observe
        """
        if self.verbose:
            print("\n" + "="*60)
            print("AGENT LOOP START")
            print("="*60)
        
        # 1. Perceive
        perceived = self.perceive(user_input)
        
        # 2. Reason
        selected_tool = self.reason(perceived)
        
        # 3. Plan
        plan = self.plan(selected_tool, perceived)
        
        # 4. Act
        result = self.act(plan)
        
        # 5. Observe
        observation = self.observe(result)
        
        if self.verbose:
            print("="*60)
            print("AGENT LOOP END")
            print("="*60)
        
        return observation
    
    def show_history(self):
        """Display conversation history"""
        print("\n" + "="*60)
        print("AGENT HISTORY")
        print("="*60)
        for entry in self.history:
            role = entry["role"].upper()
            content = entry["content"]
            print(f"{role}: {content}")
        print("="*60)

# ─── Main CLI ───

def main():
    print("="*60)
    print("WEEK 1 - DAY 2: MANUAL REACT AGENT")
    print("Agentic AI Concepts - No Frameworks")
    print("="*60)
    print("\nTools Available:")
    print("- search  : Search database for facts (capitals, populations, inventors)")
    print("- calculate: Calculate math expressions (e.g., 25 * 4 + 10)")
    print("- time    : Get current date and time")
    print("\nCommands: /history, /help, /exit\n")
    
    agent = ReActAgent(verbose=True)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == '/exit':
                print("\nGoodbye!")
                break
            elif user_input.lower() == '/history':
                agent.show_history()
                continue
            elif user_input.lower() == '/help':
                print("\nCommands:")
                print("  /history  - Show conversation history")
                print("  /help     - Show this help message")
                print("  /exit     - Exit the agent")
                print("\nExample queries:")
                print("  'What is the capital of France?'")
                print("  'Calculate 15 + 30 * 2'")
                print("  'What time is it?'")
                continue
            
            response = agent.run(user_input)
            print(f"\nAgent: {response}")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()