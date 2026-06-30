"""
Week 2 - Day 2: Extraction Comparison
Compare different methods of extracting structured outputs
"""

import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

load_dotenv()
console = Console()

# ─── Define Model ───

class PersonInfo(BaseModel):
    """Model for person information extraction"""
    name: str = Field(description="Full name of the person")
    age: int = Field(description="Age of the person")
    city: str = Field(description="City where the person lives")
    profession: str = Field(description="Job or profession of the person")
    hobby: str = Field(description="Favorite hobby")

# ─── Test Data ───

TEST_DATA = [
    "John Smith is 32 years old, lives in London, works as a software engineer, and loves playing guitar.",
    "Maria Garcia is a 28-year-old architect from Barcelona. She enjoys painting in her free time.",
    "Ahmad from Dubai, aged 45, is a pilot. His favorite hobby is photography.",
    "Emma Wilson, 27, lives in Sydney. She works as a data scientist and enjoys hiking.",
    "Dr. Rajesh Kumar is 52, resides in Bangalore, practices medicine, and loves gardening."
]

# ─── Method 1: Direct String Output ───

def method_direct(llm, text):
    """Method 1: Direct string output without structure"""
    
    prompt = ChatPromptTemplate.from_template("""
    Extract the following information from the text:
    - Name
    - Age
    - City
    - Profession
    - Hobby
    
    Text: {text}
    
    Return as plain text, each on a new line:
    """)
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"text": text})

# ─── Method 2: JSON Output ───

def method_json(llm, text):
    """Method 2: JSON output"""
    
    prompt = ChatPromptTemplate.from_template("""
    Extract the following information from the text and return as valid JSON.
    
    Text: {text}
    
    Required fields: name, age, city, profession, hobby
    
    Return ONLY valid JSON:
    """)
    
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"text": text})
    
    try:
        # Try to parse JSON
        import re
        json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return response
    except:
        return response

# ─── Method 3: Pydantic Output ───

def method_pydantic(llm, text):
    """Method 3: Pydantic structured output"""
    
    parser = PydanticOutputParser(pydantic_object=PersonInfo)
    
    prompt = ChatPromptTemplate.from_template("""
    Extract information from the text and return as valid JSON.
    
    {format_instructions}
    
    Text: {text}
    
    JSON:
    """)
    
    chain = prompt | llm | parser
    
    try:
        return chain.invoke({
            "text": text,
            "format_instructions": parser.get_format_instructions()
        })
    except Exception as e:
        return f"Error: {e}"

# ─── Main Comparison ───

def main():
    """Compare different extraction methods"""
    
    console.print(Panel.fit(
        "[bold white]Week 2 - Day 2: Extraction Method Comparison[/bold white]",
        border_style="cyan"
    ))
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    console.print("\n[bold cyan]Comparing 3 extraction methods[/bold cyan]\n")
    
    table = Table(title="Method Comparison", box=box.ROUNDED)
    table.add_column("Method", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Structured", style="yellow")
    table.add_column("Validation", style="magenta")
    table.add_column("Reliability", style="white")
    
    table.add_row(
        "String Output",
        "Plain text, no structure",
        "[No]",
        "[No]",
        "[Medium]"
    )
    table.add_row(
        "JSON Output",
        "JSON string, manual parsing",
        "[Yes]",
        "[Manual]",
        "[Medium]"
    )
    table.add_row(
        "Pydantic Output",
        "Pydantic model with validation",
        "[Yes]",
        "[Yes]",
        "[High]"
    )
    
    console.print(table)
    
    # Test each method
    console.print("\n[bold cyan]Testing on sample data...[/bold cyan]\n")
    
    test_text = TEST_DATA[0]
    console.print(f"[dim]Input: {test_text}[/dim]\n")
    
    # Method 1
    console.print("[bold]Method 1: String Output[/bold]")
    result1 = method_direct(llm, test_text)
    console.print(result1)
    console.print("")
    
    # Method 2
    console.print("[bold]Method 2: JSON Output[/bold]")
    result2 = method_json(llm, test_text)
    console.print(json.dumps(result2, indent=2) if isinstance(result2, dict) else result2)
    console.print("")
    
    # Method 3
    console.print("[bold]Method 3: Pydantic Output[/bold]")
    result3 = method_pydantic(llm, test_text)
    if isinstance(result3, PersonInfo):
        console.print(f"Name: {result3.name}")
        console.print(f"Age: {result3.age}")
        console.print(f"City: {result3.city}")
        console.print(f"Profession: {result3.profession}")
        console.print(f"Hobby: {result3.hobby}")
    else:
        console.print(result3)
    
    console.print("\n" + "="*70)
    console.print("[bold green]Conclusion:[/bold green]")
    console.print("  Pydantic provides the most reliable structured output with built-in validation.")
    console.print("  JSON output requires manual parsing and validation.")
    console.print("  String output is the least reliable for structured data.")
    console.print("="*70)

if __name__ == "__main__":
    main()
