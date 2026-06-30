"""
Week 2 - Day 1: Lab 2.1 - Chain-of-Thought Prompting Pipeline
Compare answers with and without CoT on math and logic problems
"""

import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

load_dotenv()
console = Console()

# ─── Test Problems ───

PROBLEMS = [
    {
        "category": "Math",
        "question": "A farmer has 15 chickens and 8 cows. If 3 chickens are sold and 2 cows are bought, how many animals does the farmer have now?",
        "answer": "18"
    },
    {
        "category": "Math",
        "question": "If a train travels at 60 km/h for 2.5 hours, how far does it travel?",
        "answer": "150 km"
    },
    {
        "category": "Math",
        "question": "A store sells apples at $2 per kg and oranges at $3 per kg. If someone buys 3 kg apples and 2 kg oranges, how much do they pay?",
        "answer": "$12"
    },
    {
        "category": "Logic",
        "question": "All cats are animals. Some animals are pets. Can we conclude that some cats are pets? Explain why or why not.",
        "answer": "No"
    },
    {
        "category": "Logic",
        "question": "If it rains, the ground gets wet. The ground is wet. Can we conclude it rained? Explain why or why not.",
        "answer": "No"
    },
    {
        "category": "Math",
        "question": "A rectangle has length 8 cm and width 5 cm. What is its perimeter and area?",
        "answer": "Perimeter: 26 cm, Area: 40 cm²"
    },
    {
        "category": "Logic",
        "question": "Sarah is older than John. John is older than Mike. Who is the youngest?",
        "answer": "Mike"
    },
    {
        "category": "Math",
        "question": "If 3x + 7 = 22, what is the value of x?",
        "answer": "5"
    },
    {
        "category": "Logic",
        "question": "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?",
        "answer": "$0.05"
    },
    {
        "category": "Math",
        "question": "A pizza is cut into 8 slices. If 3 people each eat 2 slices, how many slices are left?",
        "answer": "2"
    }
]

# ─── Prompts ───

# Without CoT - Direct Answer
DIRECT_PROMPT = ChatPromptTemplate.from_template("""
You are a helpful assistant. Answer the following question directly and concisely.

Question: {question}

Answer:
""")

# With CoT - Step-by-Step Reasoning
COT_PROMPT = ChatPromptTemplate.from_template("""
You are a helpful assistant. Answer the following question by thinking step by step.

Question: {question}

Let me think through this step by step:
1. 
2. 
3. 

Final Answer:
""")

# ─── Evaluator ───

class CoTEvaluator:
    """Compare answers with and without Chain-of-Thought"""
    
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        self.direct_chain = DIRECT_PROMPT | self.llm | StrOutputParser()
        self.cot_chain = COT_PROMPT | self.llm | StrOutputParser()
    
    def evaluate(self, problem: dict) -> dict:
        """Evaluate a single problem with both approaches"""
        
        question = problem["question"]
        expected = problem["answer"]
        category = problem["category"]
        
        # Direct answer (no CoT)
        start_time = time.time()
        direct_response = self.direct_chain.invoke({"question": question})
        direct_time = time.time() - start_time
        
        # CoT answer
        start_time = time.time()
        cot_response = self.cot_chain.invoke({"question": question})
        cot_time = time.time() - start_time
        
        return {
            "category": category,
            "question": question,
            "expected": expected,
            "direct_response": direct_response.strip(),
            "direct_time": direct_time,
            "cot_response": cot_response.strip(),
            "cot_time": cot_time
        }
    
    def run_all(self) -> list:
        """Run evaluation on all problems"""
        
        results = []
        total = len(PROBLEMS)
        
        console.print(f"\n[bold cyan]Running evaluation on {total} problems...[/bold cyan]\n")
        
        for i, problem in enumerate(PROBLEMS, 1):
            console.print(f"  [{i}/{total}] {problem['category']}: {problem['question'][:50]}...")
            result = self.evaluate(problem)
            results.append(result)
            
            # Show progress
            status = "Pass" if result["direct_response"].lower() == result["expected"].lower() else "Fail"
            console.print(f"    Direct: {status}  CoT: {'Pass' if result['cot_response'].lower() == result['expected'].lower() else 'Fail'}")
        
        return results

# ─── Report Generator ───

class ReportGenerator:
    """Generate comparison report"""
    
    @staticmethod
    def generate(results: list):
        """Generate and display the report"""
        
        console.print("\n" + "="*70)
        console.print("[bold cyan]CHAIN-OF-THOUGHT EVALUATION REPORT[/bold cyan]")
        console.print("="*70)
        
        # Summary statistics
        total = len(results)
        direct_correct = sum(1 for r in results if r["expected"].lower() in r["direct_response"].lower())
        cot_correct = sum(1 for r in results if r["expected"].lower() in r["cot_response"].lower())
        
        direct_avg_time = sum(r["direct_time"] for r in results) / total
        cot_avg_time = sum(r["cot_time"] for r in results) / total
        
        # Summary table
        summary_table = Table(title="Performance Summary", box=box.ROUNDED)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Direct (No CoT)", style="yellow")
        summary_table.add_column("Chain-of-Thought", style="green")
        
        summary_table.add_row("Accuracy", f"{direct_correct}/{total} ({direct_correct/total*100:.1f}%)", f"{cot_correct}/{total} ({cot_correct/total*100:.1f}%)")
        summary_table.add_row("Avg Time", f"{direct_avg_time:.2f}s", f"{cot_avg_time:.2f}s")
        
        console.print(summary_table)
        
        # Detailed results
        detail_table = Table(title="Detailed Results", box=box.ROUNDED)
        detail_table.add_column("#", style="dim", width=3)
        detail_table.add_column("Category", width=10)
        detail_table.add_column("Question", width=30)
        detail_table.add_column("Direct", width=10)
        detail_table.add_column("CoT", width=10)
        detail_table.add_column("Direct Time", width=10)
        detail_table.add_column("CoT Time", width=10)
        
        for i, r in enumerate(results, 1):
            direct_status = "Pass" if r["expected"].lower() in r["direct_response"].lower() else "Fail"
            cot_status = "Pass" if r["expected"].lower() in r["cot_response"].lower() else "Fail"
            
            detail_table.add_row(
                str(i),
                r["category"],
                r["question"][:27] + "...",
                direct_status,
                cot_status,
                f"{r['direct_time']:.2f}s",
                f"{r['cot_time']:.2f}s"
            )
        
        console.print(detail_table)
        
        # Key Insights
        console.print("\n[bold cyan]Key Insights:[/bold cyan]")
        
        if cot_correct > direct_correct:
            console.print("  [Pass] CoT improved accuracy by", f"{cot_correct - direct_correct}", "problems")
            console.print("  [Improvement]", f"{(cot_correct - direct_correct)/total*100:.1f}%", "improvement")
        else:
            console.print("  [Notice] CoT did not significantly improve accuracy")
        
        if cot_avg_time > direct_avg_time:
            console.print(f"  [Time] CoT took {cot_avg_time - direct_avg_time:.2f}s longer on average")
        else:
            console.print(f"  [Speed] CoT was {direct_avg_time - cot_avg_time:.2f}s faster on average")
        
        console.print("\n" + "="*70)
        
        # Show example comparison
        console.print("\n[bold]Example Comparison:[/bold]")
        
        example = results[0]
        console.print(Panel(
            f"[bold]Question:[/bold] {example['question']}\n\n"
            f"[bold]Expected:[/bold] {example['expected']}\n\n"
            f"[bold]Direct (No CoT):[/bold]\n{example['direct_response'][:200]}...\n\n"
            f"[bold]Chain-of-Thought:[/bold]\n{example['cot_response'][:300]}...\n\n"
            f"[bold]CoT was {'Correct' if example['expected'].lower() in example['cot_response'].lower() else 'Incorrect'}[/bold]",
            title="Example Comparison",
            border_style="cyan"
        ))

# ─── Interactive Demo ───

def interactive_demo():
    """Allow user to test their own questions"""
    
    console.print("\n" + "="*70)
    console.print("[bold cyan]INTERACTIVE COT DEMO[/bold cyan]")
    console.print("="*70)
    console.print("\nTest your own question with and without Chain-of-Thought")
    console.print("Type 'exit' to quit\n")
    
    evaluator = CoTEvaluator()
    
    while True:
        try:
            question = input("\n[bold]Enter your question: [/bold]").strip()
            
            if question.lower() == 'exit':
                console.print("\nGoodbye!")
                break
            
            if not question:
                continue
            
            # Create a problem dict
            problem = {
                "category": "Custom",
                "question": question,
                "answer": "N/A"
            }
            
            # Run evaluation
            console.print("\n[dim]Thinking...[/dim]")
            result = evaluator.evaluate(problem)
            
            # Display results
            console.print(Panel(
                f"[bold]Question:[/bold] {question}\n\n"
                f"[bold]Direct Answer (No CoT):[/bold]\n{result['direct_response'][:200]}...\n\n"
                f"[bold]Time:[/bold] {result['direct_time']:.2f}s\n\n"
                f"[bold]Chain-of-Thought Answer:[/bold]\n{result['cot_response'][:300]}...\n\n"
                f"[bold]Time:[/bold] {result['cot_time']:.2f}s",
                title="Comparison Results",
                border_style="green"
            ))
            
        except KeyboardInterrupt:
            console.print("\n\nGoodbye!")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

# ─── Main ───

def main():
    """Main entry point"""
    
    console.print(Panel.fit(
        "[bold white]Week 2 - Day 1: Chain-of-Thought Prompting Pipeline[/bold white]\n"
        "[cyan]Lab 2.1 - CoT Evaluation[/cyan]",
        border_style="cyan"
    ))
    
    # Run evaluation
    evaluator = CoTEvaluator()
    results = evaluator.run_all()
    
    # Generate report
    ReportGenerator.generate(results)
    
    # Interactive demo
    interactive_demo()

if __name__ == "__main__":
    main()
