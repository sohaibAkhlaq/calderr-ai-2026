"""
Week 2 - Day 2: Lab 2.1 - Structured Output Extractor
Extract structured data from unstructured job postings using Pydantic
"""

import os
import json
from typing import List, Optional, Literal
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, validator, model_validator
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

load_dotenv()
console = Console()

# ─── Pydantic Models ───

class JobPosting(BaseModel):
    """Model for extracting job posting information"""
    
    title: str = Field(description="Job title/position name")
    company: str = Field(description="Company name")
    salary_min: Optional[int] = Field(None, description="Minimum salary in USD")
    salary_max: Optional[int] = Field(None, description="Maximum salary in USD")
    salary_currency: Literal["USD", "EUR", "GBP", "PKR"] = Field("USD", description="Currency of salary")
    location: str = Field(description="Job location city, country")
    remote_status: Literal["Remote", "Hybrid", "On-site"] = Field(description="Remote work status")
    required_skills: List[str] = Field(description="List of required skills")
    experience_years: Optional[float] = Field(None, description="Required experience in years")
    posted_date: Optional[str] = Field(None, description="Date job was posted")
    job_type: Literal["Full-time", "Part-time", "Contract", "Internship"] = Field("Full-time", description="Employment type")
    
    # ─── Validators ───
    
    @validator('salary_min')
    def validate_salary_min(cls, v):
        if v is not None and v < 0:
            raise ValueError("Salary cannot be negative")
        return v
    
    @validator('salary_max')
    def validate_salary_max(cls, v, values):
        if v is not None:
            salary_min = values.get('salary_min')
            if salary_min is not None and v < salary_min:
                raise ValueError(f"Salary max ({v}) cannot be less than salary min ({salary_min})")
        return v
    
    @model_validator(mode='after')
    def validate_salary_range(self):
        if self.salary_min is not None and self.salary_max is not None:
            if self.salary_max < self.salary_min:
                raise ValueError(f"Salary max ({self.salary_max}) cannot be less than salary min ({self.salary_min})")
        return self
    
    # ─── Model Config ───
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Senior Python Developer",
                "company": "TechCorp Inc.",
                "salary_min": 120000,
                "salary_max": 160000,
                "salary_currency": "USD",
                "location": "Remote",
                "remote_status": "Remote",
                "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                "experience_years": 5.0,
                "posted_date": "2026-06-29",
                "job_type": "Full-time"
            }
        }

# ─── Job Posting Extractor ───

class JobPostingExtractor:
    """Extract structured job posting data using Pydantic"""
    
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        self.parser = PydanticOutputParser(pydantic_object=JobPosting)
    
    def extract(self, text: str) -> JobPosting:
        """Extract job posting from unstructured text"""
        
        prompt = ChatPromptTemplate.from_template("""
        You are a job posting parser. Extract structured information from the following job posting.
        
        IMPORTANT: Return ONLY valid JSON that matches the schema below.
        
        {format_instructions}
        
        Job Posting:
        {text}
        
        Extracted JSON:
        """)
        
        chain = prompt | self.llm | self.parser
        
        try:
            result = chain.invoke({
                "text": text,
                "format_instructions": self.parser.get_format_instructions()
            })
            return result
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            return None

# ─── Test Data ───

JOB_POSTINGS = [
    {
        "name": "Senior AI Engineer",
        "text": """
        We are hiring a Senior AI Engineer to join our growing team at AI Innovations Inc.
        
        Location: Remote (US-based)
        Salary: $140,000 - $180,000 per year
        Job Type: Full-time
        
        Requirements:
        - 5+ years of experience in AI/ML
        - Strong Python skills
        - Experience with LangChain and LLMs
        - Knowledge of Groq API
        - Experience with vector databases
        
        Posted: June 28, 2026
        """
    },
    {
        "name": "Data Scientist",
        "text": """
        Data Scientist Position at DataCorp
        Location: New York, NY (Hybrid)
        
        We are looking for a Data Scientist with 3+ years of experience.
        Salary range: $100,000 - $130,000 USD
        
        Required Skills:
        - Python
        - SQL
        - Machine Learning
        - Statistics
        - Data Visualization
        
        This is a full-time position with benefits.
        Posted 2 days ago.
        """
    },
    {
        "name": "Software Engineer",
        "text": """
        Software Engineer (Entry Level)
        TechSolutions Inc.
        Location: San Francisco, CA (On-site)
        
        We are looking for a junior software engineer to join our team.
        
        Skills required:
        - JavaScript
        - Python
        - HTML/CSS
        - Git
        
        Experience: 0-2 years
        Job Type: Full-time
        """
    },
    {
        "name": "ML Operations Engineer",
        "text": """
        MLOps Engineer wanted at CloudAI Systems
        Remote position, 100% work from home.
        
        Salary: $130,000 - $160,000
        Currency: USD
        
        We need someone with:
        4+ years in DevOps
        Experience with Kubeflow
        Knowledge of ML pipelines
        Python expertise
        AWS experience
        
        Contract position
        """
    }
]

# ─── Main Application ───

def main():
    """Main entry point"""
    
    console.print(Panel.fit(
        "[bold white]Week 2 - Day 2: Structured Output Extractor[/bold white]\n"
        "[cyan]Lab 2.1 - Job Posting Extraction with Pydantic[/cyan]",
        border_style="cyan"
    ))
    
    extractor = JobPostingExtractor()
    
    # Process all job postings
    results = []
    
    console.print("\n[bold cyan]Extracting structured data from job postings...[/bold cyan]\n")
    
    for i, job in enumerate(JOB_POSTINGS, 1):
        console.print(f"[{i}/{len(JOB_POSTINGS)}] Processing: {job['name']}")
        
        result = extractor.extract(job['text'])
        
        if result:
            results.append(result)
            console.print(f"  [Success] Extracted: {result.title} at {result.company}")
        else:
            console.print(f"  [Failed] Failed to extract")
    
    # Display summary table
    console.print("\n" + "="*70)
    console.print("[bold cyan]EXTRACTION SUMMARY[/bold cyan]")
    console.print("="*70)
    
    table = Table(title="Job Posting Extractions", box=box.ROUNDED)
    table.add_column("Title", style="cyan")
    table.add_column("Company", style="green")
    table.add_column("Location", style="yellow")
    table.add_column("Remote", style="magenta")
    table.add_column("Salary", style="white")
    table.add_column("Skills", style="blue")
    table.add_column("Experience", style="white")
    
    for r in results:
        salary_str = f"${r.salary_min:,} - ${r.salary_max:,}" if r.salary_min and r.salary_max else "Not specified"
        skills_str = ", ".join(r.required_skills[:3]) + ("..." if len(r.required_skills) > 3 else "")
        exp_str = f"{r.experience_years} yrs" if r.experience_years else "Not specified"
        
        table.add_row(
            r.title[:20],
            r.company[:15],
            r.location[:15],
            r.remote_status,
            salary_str,
            skills_str,
            exp_str
        )
    
    console.print(table)
    
    # Show JSON output for first result
    if results:
        console.print("\n[bold cyan]Sample JSON Output (First Result):[/bold cyan]")
        console.print(json.dumps(results[0].model_dump(), indent=2))
    
    # Interactive mode
    console.print("\n" + "="*70)
    console.print("[bold cyan]INTERACTIVE MODE[/bold cyan]")
    console.print("Enter your own job posting text to extract")
    console.print("Type 'exit' to quit\n")
    
    while True:
        try:
            text = input("\n[bold]Paste job posting: [/bold]").strip()
            
            if text.lower() == 'exit':
                console.print("\nGoodbye!")
                break
            
            if not text:
                continue
            
            console.print("\n[dim]Extracting...[/dim]")
            result = extractor.extract(text)
            
            if result:
                console.print(Panel(
                    f"[bold]Title:[/bold] {result.title}\n"
                    f"[bold]Company:[/bold] {result.company}\n"
                    f"[bold]Location:[/bold] {result.location}\n"
                    f"[bold]Remote:[/bold] {result.remote_status}\n"
                    f"[bold]Salary:[/bold] ${result.salary_min:,} - ${result.salary_max:,} {result.salary_currency}\n"
                    f"[bold]Skills:[/bold] {', '.join(result.required_skills)}\n"
                    f"[bold]Experience:[/bold] {result.experience_years} years\n"
                    f"[bold]Job Type:[/bold] {result.job_type}",
                    title="Extracted Data",
                    border_style="green"
                ))
            else:
                console.print("[bold red]Failed to extract. Please try again.[/bold red]")
            
        except KeyboardInterrupt:
            console.print("\n\nGoodbye!")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    main()
