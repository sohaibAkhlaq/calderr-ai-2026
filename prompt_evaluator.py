"""
Week 1 - Project 1-I-B: Prompt Engineering Evaluator
Automated prompt generation, testing, and evaluation
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from pydantic import BaseModel, Field
import asyncio

load_dotenv()
console = Console()

# ─── Data Models ───

class PromptResult(BaseModel):
    """Result of a single prompt test"""
    prompt_name: str
    prompt_text: str
    response: str
    word_count: int
    char_count: int
    time_taken: float
    accuracy_score: float = Field(ge=0, le=10)
    brevity_score: float = Field(ge=0, le=10)
    helpfulness_score: float = Field(ge=0, le=10)
    overall_score: float = Field(ge=0, le=10)

class EvaluationReport(BaseModel):
    """Complete evaluation report"""
    task_description: str
    test_case: str
    prompts_evaluated: List[PromptResult]
    best_prompt: str
    best_score: float
    recommendations: List[str]
    generated_at: str

# ─── Prompt Generator ───

class PromptGenerator:
    """Generates different prompt variations for a task"""
    
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            api_key=os.getenv("GROQ_API_KEY")
        )
    
    def generate_prompts(self, task: str, num_prompts: int = 3) -> List[str]:
        """Generate multiple prompt variations for a task"""
        
        prompt_template = ChatPromptTemplate.from_template("""
        You are an expert prompt engineer. Generate {num_prompts} different system prompts 
        for the following task. Each prompt should have a different style and approach.
        
        Task: {task}
        
        Generate prompts with these styles:
        1. Concise and direct
        2. Detailed and structured with clear instructions
        3. Creative and engaging with examples
        
        Return ONLY the prompts, numbered 1-{num_prompts}. 
        Each prompt should start with the number and a period.
        """)
        
        chain = prompt_template | self.llm | StrOutputParser()
        
        response = chain.invoke({
            "task": task,
            "num_prompts": num_prompts
        })
        
        # Parse prompts from response
        prompts = []
        lines = response.strip().split('\n')
        for line in lines:
            if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith('-')):
                # Extract prompt text (remove number/bullet)
                text = line.strip()
                if text[0].isdigit() and '. ' in text:
                    text = text.split('. ', 1)[1] if '. ' in text else text
                elif text.startswith('- '):
                    text = text[2:]
                if text.strip():
                    prompts.append(text.strip())
        
        # Ensure we have exactly num_prompts
        while len(prompts) < num_prompts:
            prompts.append(f"You are a helpful assistant. {task}")
        
        return prompts[:num_prompts]

# ─── Prompt Evaluator ───

class PromptEvaluator:
    """Evaluates prompts against test cases"""
    
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY")
        )
    
    async def evaluate_prompt(self, prompt: str, task: str, test_case: str) -> PromptResult:
        """Evaluate a single prompt"""
        
        start_time = time.time()
        
        # Run the prompt
        full_prompt = ChatPromptTemplate.from_messages([
            ("system", prompt),
            ("user", test_case)
        ])
        
        chain = full_prompt | self.llm | StrOutputParser()
        
        try:
            response = chain.invoke({"input": test_case})
        except Exception as e:
            response = f"Error: {e}"
        
        end_time = time.time()
        
        # Calculate metrics
        word_count = len(response.split())
        char_count = len(response)
        time_taken = end_time - start_time
        
        # Score the response
        scores = await self.score_response(response, task)
        
        return PromptResult(
            prompt_name=f"Prompt {len(prompt[:20])}...",
            prompt_text=prompt,
            response=response,
            word_count=word_count,
            char_count=char_count,
            time_taken=time_taken,
            accuracy_score=scores["accuracy"],
            brevity_score=scores["brevity"],
            helpfulness_score=scores["helpfulness"],
            overall_score=(scores["accuracy"] + scores["brevity"] + scores["helpfulness"]) / 3
        )
    
    async def score_response(self, response: str, task: str) -> Dict[str, float]:
        """Score a response on accuracy, brevity, and helpfulness"""
        
        scorer_prompt = ChatPromptTemplate.from_template("""
        Score the following response for the task: {task}
        
        Response: {response}
        
        Score each criterion from 1-10 (1 = poor, 10 = excellent):
        1. Accuracy: Is the information correct and relevant?
        2. Brevity: Is the response concise and to the point?
        3. Helpfulness: Does the response actually help solve the problem?
        
        Return ONLY scores in this format:
        Accuracy: X
        Brevity: Y
        Helpfulness: Z
        """)
        
        chain = scorer_prompt | self.llm | StrOutputParser()
        
        try:
            result = chain.invoke({
                "task": task,
                "response": response
            })
            
            # Parse scores
            scores = {}
            for line in result.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = float(value.strip())
                    if key in ['accuracy', 'brevity', 'helpfulness']:
                        scores[key] = min(10, max(0, value))
            
            # Default fallback
            for key in ['accuracy', 'brevity', 'helpfulness']:
                if key not in scores:
                    scores[key] = 5.0
            
            return scores
            
        except Exception as e:
            return {"accuracy": 5.0, "brevity": 5.0, "helpfulness": 5.0}

# ─── Main Application ───

class PromptEngineeringEvaluator:
    """Main application for prompt engineering evaluation"""
    
    def __init__(self):
        self.generator = PromptGenerator()
        self.evaluator = PromptEvaluator()
    
    async def run_evaluation(self, task: str, test_case: str, num_prompts: int = 3) -> EvaluationReport:
        """Run complete evaluation"""
        
        console.print(Panel.fit(
            "[bold cyan]Prompt Engineering Evaluator[/bold cyan]",
            border_style="cyan"
        ))
        
        # Step 1: Generate prompts
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            progress.add_task(description="Generating prompts...", total=None)
            prompts = self.generator.generate_prompts(task, num_prompts)
        
        console.print(f"[green]✓[/green] Generated {len(prompts)} prompts\n")
        
        # Step 2: Evaluate each prompt
        console.print("[bold]Evaluating prompts...[/bold]\n")
        
        results = []
        for i, prompt in enumerate(prompts, 1):
            console.print(f"  Testing Prompt {i}...", end="")
            result = await self.evaluator.evaluate_prompt(prompt, task, test_case)
            results.append(result)
            console.print(f" [green]✓[/green] Score: {result.overall_score:.1f}/10")
        
        # Step 3: Generate report
        best_result = max(results, key=lambda x: x.overall_score)
        
        recommendations = []
        for r in results:
            if r.overall_score < 6:
                recommendations.append(f"Prompt '{r.prompt_name[:30]}...' scored low ({r.overall_score:.1f}). Consider improving clarity.")
            elif r.accuracy_score < 6:
                recommendations.append(f"Prompt '{r.prompt_name[:30]}...' lacks accuracy. Add more specific instructions.")
            elif r.brevity_score < 6:
                recommendations.append(f"Prompt '{r.prompt_name[:30]}...' needs better conciseness. Focus on key points.")
        
        if not recommendations:
            recommendations.append("All prompts performed well. Consider increasing test complexity.")
        
        return EvaluationReport(
            task_description=task,
            test_case=test_case,
            prompts_evaluated=results,
            best_prompt=best_result.prompt_name,
            best_score=best_result.overall_score,
            recommendations=recommendations,
            generated_at=datetime.now().isoformat()
        )
    
    def display_report(self, report: EvaluationReport):
        """Display the evaluation report"""
        
        console.print("\n" + "="*70)
        console.print("[bold cyan]EVALUATION REPORT[/bold cyan]")
        console.print("="*70)
        
        console.print(f"\n[bold]Task:[/bold] {report.task_description}")
        console.print(f"[bold]Test Case:[/bold] {report.test_case}")
        console.print(f"[bold]Generated:[/bold] {report.generated_at}")
        
        # Results table
        table = Table(title="Prompt Comparison", box=box.ROUNDED)
        table.add_column("Prompt", style="cyan", width=20)
        table.add_column("Accuracy", justify="center", width=10)
        table.add_column("Brevity", justify="center", width=10)
        table.add_column("Helpfulness", justify="center", width=10)
        table.add_column("Overall", justify="center", width=10)
        table.add_column("Time (s)", justify="center", width=10)
        
        for r in report.prompts_evaluated:
            table.add_row(
                r.prompt_name[:20],
                f"{r.accuracy_score:.1f}",
                f"{r.brevity_score:.1f}",
                f"{r.helpfulness_score:.1f}",
                f"{r.overall_score:.1f}",
                f"{r.time_taken:.2f}"
            )
        
        console.print(table)
        
        # Best prompt
        best = next(r for r in report.prompts_evaluated if r.prompt_name == report.best_prompt)
        console.print(Panel(
            f"[bold]Best Prompt:[/bold] {best.prompt_text[:200]}...\n"
            f"[bold]Score:[/bold] {best.overall_score:.1f}/10\n"
            f"[bold]Response:[/bold] {best.response[:300]}...",
            title="🏆 Best Performing Prompt",
            border_style="green"
        ))
        
        # Recommendations
        console.print("\n[bold]Recommendations:[/bold]")
        for rec in report.recommendations:
            console.print(f"  • {rec}")
        
        console.print("\n" + "="*70)

# ─── CLI Interface ───

async def main():
    """Main entry point"""
    
    console.print(Panel.fit(
        "[bold white]Prompt Engineering Evaluator[/bold white]\n"
        "[cyan]Week 1 - Project 1-I-B[/cyan]",
        border_style="cyan"
    ))
    
    # Get user input
    console.print("\n[bold]Enter task description:[/bold]")
    console.print("[dim](e.g., 'Summarize news articles in 2 sentences')[/dim]")
    task = input("> ").strip()
    
    if not task:
        task = "Summarize news articles in 2 sentences"
        console.print(f"[dim]Using default: {task}[/dim]")
    
    console.print("\n[bold]Enter test case:[/bold]")
    console.print("[dim](e.g., 'The company announced record profits...')[/dim]")
    test_case = input("> ").strip()
    
    if not test_case:
        test_case = "Artificial Intelligence has made significant progress in recent years, transforming industries and reshaping how we work. From healthcare to finance, AI-powered tools are helping professionals make faster, more accurate decisions."
        console.print(f"[dim]Using default test case[/dim]")
    
    console.print("\n[bold]Number of prompts to test:[/bold] [dim](default: 3)[/dim]")
    try:
        num_prompts = int(input("> ").strip())
    except:
        num_prompts = 3
    
    # Run evaluation
    evaluator = PromptEngineeringEvaluator()
    report = await evaluator.run_evaluation(task, test_case, num_prompts)
    
    # Display report
    evaluator.display_report(report)
    
    # Save report
    filename = f"prompt_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(report.model_dump(), f, indent=2, default=str)
    
    console.print(f"\n[green]✓[/green] Report saved to: {filename}")

if __name__ == "__main__":
    asyncio.run(main())
