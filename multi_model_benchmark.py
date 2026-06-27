"""
Week 1 - Project 1-P-B: Multi-Model Comparison Engine
Benchmark multiple Groq models with statistical analysis
"""

import os
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box
from rich.markdown import Markdown
import statistics
import yaml

load_dotenv()
console = Console()

# ─── Data Models ───

@dataclass
class ModelResult:
    """Result from a single model test"""
    model_name: str
    task: str
    response: str
    response_time: float
    word_count: int
    token_estimate: int
    success: bool
    error_message: Optional[str] = None

@dataclass
class ModelStatistics:
    """Statistical summary for a model"""
    model_name: str
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    median_response_time: float
    std_dev_response_time: float
    avg_word_count: float
    total_tokens: int
    success_rate: float
    task_count: int

@dataclass
class BenchmarkReport:
    """Complete benchmark report"""
    models_tested: List[str]
    tasks: List[str]
    results: List[ModelResult]
    statistics: Dict[str, ModelStatistics]
    generated_at: str
    total_time: float

# ─── Task Loader ───

class TaskLoader:
    """Load and manage test tasks"""
    
    DEFAULT_TASKS = [
        {
            "name": "summarization",
            "description": "Summarize the following text in 2-3 sentences",
            "input": "Artificial Intelligence has made significant progress in recent years, transforming industries and reshaping how we work. From healthcare to finance, AI-powered tools are helping professionals make faster, more accurate decisions. Machine learning models can now process vast amounts of data in seconds, identifying patterns that would take humans weeks to find."
        },
        {
            "name": "coding",
            "description": "Write a Python function to calculate the factorial of a number",
            "input": "Write a Python function called factorial that takes an integer n and returns n! (n factorial). Include a docstring and error handling for negative numbers."
        },
        {
            "name": "creative_writing",
            "description": "Write a short poem or creative paragraph",
            "input": "Write a short poem about a robot learning to paint."
        },
        {
            "name": "explanation",
            "description": "Explain a complex concept simply",
            "input": "Explain how transformers work in AI in simple terms that a non-technical person can understand."
        },
        {
            "name": "analysis",
            "description": "Analyze and provide insights",
            "input": "Analyze the pros and cons of remote work for software developers."
        }
    ]
    
    @staticmethod
    def load_tasks(file_path: Optional[str] = None) -> List[Dict]:
        """Load tasks from YAML file or return defaults"""
        
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
                return data.get('tasks', TaskLoader.DEFAULT_TASKS)
        
        return TaskLoader.DEFAULT_TASKS

# ─── Model Runner ───

class ModelRunner:
    """Run models in parallel with proper async handling"""
    
    def __init__(self):
        self.models = {
            "llama-3.3-70b-versatile": {
                "display_name": "LLaMA 3.3 70B",
                "description": "Best quality, slower",
                "color": "green"
            },
            "llama-3.1-8b-instant": {
                "display_name": "LLaMA 3.1 8B",
                "description": "Fastest, good for prototyping",
                "color": "blue"
            }
        }
    
    async def test_model(self, model_name: str, task: Dict) -> ModelResult:
        """Test a single model on a single task"""
        
        start_time = time.time()
        success = False
        error_message = None
        response = ""
        
        try:
            llm = ChatGroq(
                model=model_name,
                temperature=0.7,
                api_key=os.getenv("GROQ_API_KEY")
            )
            
            prompt = ChatPromptTemplate.from_template("""
            {description}
            
            Input: {input}
            
            Response:
            """)
            
            chain = prompt | llm | StrOutputParser()
            
            response = chain.invoke({
                "description": task["description"],
                "input": task["input"]
            })
            
            success = True
            
        except Exception as e:
            error_message = str(e)
            response = f"Error: {e}"
        
        end_time = time.time()
        
        return ModelResult(
            model_name=model_name,
            task=task["name"],
            response=response,
            response_time=end_time - start_time,
            word_count=len(response.split()),
            token_estimate=len(response) // 4,
            success=success,
            error_message=error_message
        )
    
    async def run_benchmark(self, models: List[str], tasks: List[Dict]) -> List[ModelResult]:
        """Run all models on all tasks in parallel"""
        
        results = []
        total_tests = len(models) * len(tasks)
        completed = 0
        
        with Progress(
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            
            task_progress = progress.add_task("Running benchmarks...", total=total_tests)
            
            # Run tests sequentially for better tracking
            for model in models:
                for task in tasks:
                    console.print(f"  Testing {model} on {task['name']}...", end="")
                    result = await self.test_model(model, task)
                    results.append(result)
                    completed += 1
                    progress.update(task_progress, advance=1)
                    
                    status = "✅" if result.success else "❌"
                    console.print(f" {status} {result.response_time:.2f}s")
        
        return results

# ─── Statistics Analyzer ───

class StatisticsAnalyzer:
    """Analyze benchmark results and generate statistics"""
    
    @staticmethod
    def analyze(results: List[ModelResult]) -> Dict[str, ModelStatistics]:
        """Calculate statistics for each model"""
        
        model_results = {}
        
        for r in results:
            if r.model_name not in model_results:
                model_results[r.model_name] = []
            model_results[r.model_name].append(r)
        
        stats = {}
        for model_name, results_list in model_results.items():
            response_times = [r.response_time for r in results_list]
            word_counts = [r.word_count for r in results_list]
            success_count = sum(1 for r in results_list if r.success)
            
            stats[model_name] = ModelStatistics(
                model_name=model_name,
                avg_response_time=statistics.mean(response_times) if response_times else 0,
                min_response_time=min(response_times) if response_times else 0,
                max_response_time=max(response_times) if response_times else 0,
                median_response_time=statistics.median(response_times) if response_times else 0,
                std_dev_response_time=statistics.stdev(response_times) if len(response_times) > 1 else 0,
                avg_word_count=statistics.mean(word_counts) if word_counts else 0,
                total_tokens=sum(r.token_estimate for r in results_list),
                success_rate=success_count / len(results_list) if results_list else 0,
                task_count=len(results_list)
            )
        
        return stats

# ─── Report Generator ───

class ReportGenerator:
    """Generate HTML and JSON reports"""
    
    @staticmethod
    def generate_json_report(report: BenchmarkReport, filename: str):
        """Generate JSON report"""
        
        data = {
            "models_tested": report.models_tested,
            "tasks": report.tasks,
            "total_time": report.total_time,
            "generated_at": report.generated_at,
            "results": [],
            "statistics": {}
        }
        
        for r in report.results:
            data["results"].append({
                "model": r.model_name,
                "task": r.task,
                "success": r.success,
                "response_time": r.response_time,
                "word_count": r.word_count,
                "token_estimate": r.token_estimate,
                "error": r.error_message,
                "response": r.response[:500]  # Truncate for size
            })
        
        for model_name, stats in report.statistics.items():
            data["statistics"][model_name] = {
                "avg_response_time": stats.avg_response_time,
                "min_response_time": stats.min_response_time,
                "max_response_time": stats.max_response_time,
                "median_response_time": stats.median_response_time,
                "std_dev_response_time": stats.std_dev_response_time,
                "avg_word_count": stats.avg_word_count,
                "total_tokens": stats.total_tokens,
                "success_rate": stats.success_rate,
                "task_count": stats.task_count
            }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def generate_html_report(report: BenchmarkReport, filename: str):
        """Generate HTML report with visualizations"""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Multi-Model Benchmark Report</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
                .header h1 {{ margin: 0; }}
                .header p {{ opacity: 0.9; margin: 5px 0 0; }}
                .card {{ background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .card h2 {{ margin-top: 0; color: #333; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
                th {{ background: #f8f9fa; font-weight: 600; }}
                .success {{ color: #28a745; }}
                .failure {{ color: #dc3545; }}
                .stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px; }}
                .stat-item {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }}
                .stat-value {{ font-size: 24px; font-weight: bold; color: #333; }}
                .stat-label {{ color: #666; font-size: 14px; }}
                .best {{ background: #d4edda; border-left: 4px solid #28a745; }}
                .worst {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
                .bar-container {{ background: #e9ecef; border-radius: 5px; height: 20px; margin: 10px 0; }}
                .bar {{ height: 100%; border-radius: 5px; transition: width 0.3s; }}
                .footer {{ text-align: center; color: #666; margin-top: 30px; padding: 20px; border-top: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 Multi-Model Benchmark Report</h1>
                <p>Generated: {report.generated_at}</p>
                <p>Models Tested: {len(report.models_tested)} • Tasks: {len(report.tasks)} • Total Time: {report.total_time:.2f}s</p>
            </div>
        """
        
        # Statistics Section
        html += f"""
            <div class="card">
                <h2>📊 Model Statistics</h2>
                <table>
                    <tr>
                        <th>Model</th>
                        <th>Avg Response (s)</th>
                        <th>Min (s)</th>
                        <th>Max (s)</th>
                        <th>Avg Words</th>
                        <th>Success Rate</th>
                        <th>Status</th>
                    </tr>
        """
        
        for model_name, stats in report.statistics.items():
            best_time = min(s.avg_response_time for s in report.statistics.values())
            is_best = stats.avg_response_time == best_time
            
            html += f"""
                <tr class="{'best' if is_best else ''}">
                    <td><strong>{model_name}</strong></td>
                    <td>{stats.avg_response_time:.2f}</td>
                    <td>{stats.min_response_time:.2f}</td>
                    <td>{stats.max_response_time:.2f}</td>
                    <td>{stats.avg_word_count:.1f}</td>
                    <td>{stats.success_rate * 100:.1f}%</td>
                    <td>{'✅' if stats.success_rate == 1.0 else '⚠️'}</td>
                </tr>
            """
        
        html += """
                </table>
            </div>
        """
        
        # Comparison Section
        html += """
            <div class="card">
                <h2>📈 Performance Comparison</h2>
        """
        
        max_time = max(s.avg_response_time for s in report.statistics.values())
        
        for model_name, stats in report.statistics.items():
            percentage = (stats.avg_response_time / max_time) * 100
            color = "#28a745" if percentage < 30 else ("#ffc107" if percentage < 60 else "#dc3545")
            
            html += f"""
                <div>
                    <span style="font-weight: 500;">{model_name}</span>
                    <span style="float: right; color: #666;">{stats.avg_response_time:.2f}s</span>
                </div>
                <div class="bar-container">
                    <div class="bar" style="width: {percentage}%; background: {color};"></div>
                </div>
            """
        
        html += """
            </div>
        """
        
        # Results Section
        html += """
            <div class="card">
                <h2>📝 Detailed Results</h2>
                <table>
                    <tr>
                        <th>Model</th>
                        <th>Task</th>
                        <th>Time (s)</th>
                        <th>Words</th>
                        <th>Status</th>
                    </tr>
        """
        
        for r in report.results:
            html += f"""
                <tr>
                    <td>{r.model_name}</td>
                    <td>{r.task}</td>
                    <td>{r.response_time:.2f}</td>
                    <td>{r.word_count}</td>
                    <td class="{'success' if r.success else 'failure'}">{'✅ Success' if r.success else '❌ Failed'}</td>
                </tr>
            """
        
        html += """
                </table>
            </div>
        """
        
        html += """
            <div class="footer">
                Generated by CalderR AI Internship - Week 1 Project 1-P-B
            </div>
        </body>
        </html>
        """
        
        with open(filename, 'w') as f:
            f.write(html)

# ─── Main Application ───

class MultiModelComparisonEngine:
    """Main application for multi-model benchmarking"""
    
    def __init__(self):
        self.models = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant"
        ]
    
    async def run_benchmark(self, tasks: List[Dict]) -> BenchmarkReport:
        """Run complete benchmark"""
        
        console.print(Panel.fit(
            "[bold cyan]Multi-Model Comparison Engine[/bold cyan]",
            border_style="cyan"
        ))
        
        start_time = time.time()
        
        # Step 1: Display models being tested
        console.print("\n[bold]Models Being Tested:[/bold]")
        for model in self.models:
            console.print(f"  • {model}")
        
        # Step 2: Run benchmark
        console.print(f"\n[bold]Running {len(self.models)} models on {len(tasks)} tasks...[/bold]")
        console.print("="*60)
        
        runner = ModelRunner()
        results = await runner.run_benchmark(self.models, tasks)
        
        # Step 3: Analyze results
        console.print("\n[bold]Analyzing results...[/bold]")
        stats = StatisticsAnalyzer.analyze(results)
        
        # Step 4: Generate report
        end_time = time.time()
        
        report = BenchmarkReport(
            models_tested=self.models,
            tasks=[t["name"] for t in tasks],
            results=results,
            statistics=stats,
            generated_at=datetime.now().isoformat(),
            total_time=end_time - start_time
        )
        
        return report
    
    def display_report(self, report: BenchmarkReport):
        """Display the benchmark report"""
        
        console.print("\n" + "="*70)
        console.print("[bold cyan]BENCHMARK REPORT[/bold cyan]")
        console.print("="*70)
        
        console.print(f"\n[bold]Generated:[/bold] {report.generated_at}")
        console.print(f"[bold]Total Time:[/bold] {report.total_time:.2f}s")
        
        # Statistics table
        table = Table(title="Model Statistics", box=box.ROUNDED)
        table.add_column("Model", style="cyan")
        table.add_column("Avg Time (s)", justify="center")
        table.add_column("Min (s)", justify="center")
        table.add_column("Max (s)", justify="center")
        table.add_column("Avg Words", justify="center")
        table.add_column("Success Rate", justify="center")
        
        for model_name, stats in report.statistics.items():
            table.add_row(
                model_name,
                f"{stats.avg_response_time:.2f}",
                f"{stats.min_response_time:.2f}",
                f"{stats.max_response_time:.2f}",
                f"{stats.avg_word_count:.1f}",
                f"{stats.success_rate * 100:.1f}%"
            )
        
        console.print(table)
        
        # Best performer
        best_model = min(report.statistics.items(), key=lambda x: x[1].avg_response_time)
        console.print(Panel(
            f"[bold]Fastest Model:[/bold] {best_model[0]}\n"
            f"[bold]Average Time:[/bold] {best_model[1].avg_response_time:.2f}s\n"
            f"[bold]Success Rate:[/bold] {best_model[1].success_rate * 100:.1f}%\n"
            f"[bold]Tokens Used:[/bold] {best_model[1].total_tokens}",
            title="🏆 Fastest Model",
            border_style="green"
        ))
        
        console.print("="*70)

# ─── CLI Interface ───

async def main():
    """Main entry point"""
    
    console.print(Panel.fit(
        "[bold white]Multi-Model Comparison Engine[/bold white]\n"
        "[cyan]Week 1 - Project 1-P-B[/cyan]",
        border_style="cyan"
    ))
    
    # Load tasks
    console.print("\n[bold]Loading tasks...[/bold]")
    tasks = TaskLoader.load_tasks()
    console.print(f"Loaded {len(tasks)} tasks")
    
    # Run benchmark
    engine = MultiModelComparisonEngine()
    report = await engine.run_benchmark(tasks)
    
    # Display report
    engine.display_report(report)
    
    # Save reports
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_file = f"benchmark_report_{timestamp}.json"
    html_file = f"benchmark_report_{timestamp}.html"
    
    ReportGenerator.generate_json_report(report, json_file)
    ReportGenerator.generate_html_report(report, html_file)
    
    console.print(f"\n[green]✓[/green] Reports saved:")
    console.print(f"  • JSON: {json_file}")
    console.print(f"  • HTML: {html_file}")

if __name__ == "__main__":
    asyncio.run(main())
