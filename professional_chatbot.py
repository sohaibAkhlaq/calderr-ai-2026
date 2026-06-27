"""
Week 1 - Day 5: Professional CLI Chatbot
Lab 1.1 Enhanced - Multi-turn chatbot with memory, persona, Rich UI
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich import box

load_dotenv()
console = Console()

class ProfessionalChatbot:
    """Professional CLI chatbot with memory, persona, and Rich UI"""
    
    def __init__(self, model="llama-3.3-70b-versatile", temperature=0.7, persona="general"):
        self.model = model
        self.temperature = temperature
        self.persona = persona
        
        # Define personas
        self.personas = {
            "general": "You are a helpful AI assistant. You are knowledgeable, concise, and friendly.",
            "technical": "You are a senior software engineer. Provide technical explanations with code examples. Be precise and thorough.",
            "creative": "You are a creative writer. Use vivid language, metaphors, and storytelling in your responses.",
            "academic": "You are a university professor. Provide well-structured, scholarly responses with references to key concepts.",
            "mentor": "You are a patient mentor. Guide users to find answers themselves. Ask questions and provide hints."
        }
        
        # Initialize LLM
        self.llm = ChatGroq(
            model=self.model,
            temperature=self.temperature,
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        # Initialize memory
        self.messages = []
        self.total_tokens = 0
        self.turn_count = 0
        self.start_time = datetime.now()
        
        # Create prompt template with memory
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.personas.get(persona, self.personas["general"])),
            MessagesPlaceholder(variable_name="history"),
            ("user", "{input}")
        ])
        
        # Create chain
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def chat(self, user_input):
        """Process user input and return response"""
        self.turn_count += 1
        
        # Add user message to history
        self.messages.append(HumanMessage(content=user_input))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Thinking...", total=None)
            
            # Get response
            response = self.chain.invoke({
                "history": self.messages[:-1],
                "input": user_input
            })
        
        # Add assistant response to history
        self.messages.append(AIMessage(content=response))
        
        # Estimate tokens (rough estimate: ~4 chars per token)
        total_chars = len(user_input) + len(response)
        self.total_tokens += total_chars // 4
        
        return response
    
    def clear(self):
        """Clear conversation history"""
        self.messages = []
        self.turn_count = 0
        console.print("[green]✓[/green] Conversation cleared.")
    
    def show_history(self):
        """Display conversation history"""
        if not self.messages:
            console.print("[yellow]No conversation history.[/yellow]")
            return
        
        table = Table(title="Conversation History", box=box.ROUNDED)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Role", style="blue", width=12)
        table.add_column("Message", style="white")
        
        for i, msg in enumerate(self.messages, 1):
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            content = msg.content[:80] + "..." if len(msg.content) > 80 else msg.content
            table.add_row(str(i), role, content)
        
        console.print(table)
    
    def show_stats(self):
        """Display conversation statistics"""
        elapsed = datetime.now() - self.start_time
        
        table = Table(title="Session Statistics", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Model", self.model)
        table.add_row("Persona", self.persona)
        table.add_row("Temperature", str(self.temperature))
        table.add_row("Turns", str(self.turn_count))
        table.add_row("Total Messages", str(len(self.messages)))
        table.add_row("Estimated Tokens", str(self.total_tokens))
        table.add_row("Session Duration", str(elapsed).split('.')[0])
        
        console.print(table)

def main():
    """Main entry point"""
    console.print(Panel.fit(
        "[bold cyan]🤖 CalderR AI Internship - Professional Chatbot[/bold cyan]\n"
        "[white]Week 1 Day 5 - Integration & Demo[/white]",
        border_style="cyan"
    ))
    
    # Persona selection
    console.print("\n[bold]Select Persona:[/bold]")
    console.print("  1. General Assistant (default)")
    console.print("  2. Technical Engineer")
    console.print("  3. Creative Writer")
    console.print("  4. Academic Professor")
    console.print("  5. Mentor")
    
    persona_choice = Prompt.ask("Enter choice", choices=["1", "2", "3", "4", "5"], default="1")
    persona_map = {"1": "general", "2": "technical", "3": "creative", "4": "academic", "5": "mentor"}
    persona = persona_map[persona_choice]
    
    # Model selection
    console.print("\n[bold]Select Model:[/bold]")
    console.print("  1. llama-3.3-70b-versatile (best quality)")
    console.print("  2. llama-3.1-8b-instant (fastest)")
    
    model_choice = Prompt.ask("Enter choice", choices=["1", "2"], default="1")
    model = "llama-3.3-70b-versatile" if model_choice == "1" else "llama-3.1-8b-instant"
    
    # Temperature selection
    console.print("\n[bold]Select Temperature:[/bold]")
    console.print("  1. 0.0 (Deterministic)")
    console.print("  2. 0.3 (Slightly Creative)")
    console.print("  3. 0.7 (Balanced) [recommended]")
    console.print("  4. 1.0 (Creative)")
    
    temp_choice = Prompt.ask("Enter choice", choices=["1", "2", "3", "4"], default="3")
    temp_map = {"1": 0.0, "2": 0.3, "3": 0.7, "4": 1.0}
    temperature = temp_map[temp_choice]
    
    # Initialize chatbot
    chatbot = ProfessionalChatbot(
        model=model,
        temperature=temperature,
        persona=persona
    )
    
    # Display welcome
    console.print(Panel.fit(
        f"[bold green]✓[/bold green] Chatbot initialized!\n"
        f"Persona: [cyan]{persona}[/cyan] | Model: [cyan]{model}[/cyan] | Temperature: [cyan]{temperature}[/cyan]\n"
        f"[dim]Type /help for commands[/dim]",
        border_style="green"
    ))
    
    # Main loop
    while True:
        try:
            # Get user input with rich prompt
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith('/'):
                cmd = user_input.lower()
                
                if cmd == '/exit' or cmd == '/quit':
                    console.print("\n[bold green]✓[/bold green] Goodbye!")
                    break
                
                elif cmd == '/clear':
                    chatbot.clear()
                    continue
                
                elif cmd == '/history':
                    chatbot.show_history()
                    continue
                
                elif cmd == '/stats':
                    chatbot.show_stats()
                    continue
                
                elif cmd == '/help':
                    console.print(Panel(
                        "[bold]Available Commands:[/bold]\n"
                        "  /exit     - Exit the chatbot\n"
                        "  /clear    - Clear conversation history\n"
                        "  /history  - Show conversation history\n"
                        "  /stats    - Show session statistics\n"
                        "  /help     - Show this help message",
                        title="Help",
                        border_style="cyan"
                    ))
                    continue
                
                else:
                    console.print("[yellow]Unknown command. Type /help for available commands.[/yellow]")
                    continue
            
            # Get response
            response = chatbot.chat(user_input)
            
            # Display response with Markdown support
            console.print(Panel(
                Markdown(response),
                title=f"[bold green]Assistant[/bold green]",
                border_style="green"
            ))
            
        except KeyboardInterrupt:
            console.print("\n\n[bold green]✓[/bold green] Goodbye!")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    main()