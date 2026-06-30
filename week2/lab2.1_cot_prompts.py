"""
Week 2 - Day 1: Lab 2.1 - Various Prompting Techniques
Demonstrates: CoT, ToT, Self-Consistency, Meta-Prompting, Prompt Chaining, Negative Prompting
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from rich.console import Console
from rich.panel import Panel

load_dotenv()
console = Console()

# ─── 1. Chain-of-Thought (CoT) ───

def demonstrate_cot():
    """Demonstrate Chain-of-Thought prompting"""
    
    console.print(Panel(
        "[bold]Chain-of-Thought (CoT) Prompting[/bold]\n"
        "Asking the model to reason step by step",
        border_style="cyan"
    ))
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    question = "A farmer has 17 sheep. All but 9 die. How many are left?"
    
    # Without CoT
    prompt_no_cot = ChatPromptTemplate.from_template(
        "Answer: {question}"
    )
    chain_no_cot = prompt_no_cot | llm | StrOutputParser()
    
    # With CoT
    prompt_cot = ChatPromptTemplate.from_template("""
    Question: {question}
    
    Let me think step by step:
    1. 
    2. 
    3. 
    
    Therefore, the answer is:
    """)
    chain_cot = prompt_cot | llm | StrOutputParser()
    
    console.print(f"\n[bold]Question:[/bold] {question}")
    
    console.print("\n[bold]Without CoT:[/bold]")
    response = chain_no_cot.invoke({"question": question})
    console.print(response)
    
    console.print("\n[bold]With CoT:[/bold]")
    response = chain_cot.invoke({"question": question})
    console.print(response)
    
    console.print("\n[dim]Note: CoT shows the reasoning process, making the answer more transparent and reliable.[/dim]")

# ─── 2. Tree-of-Thought (ToT) ───

def demonstrate_tot():
    """Demonstrate Tree-of-Thought prompting"""
    
    console.print(Panel(
        "[bold]Tree-of-Thought (ToT) Prompting[/bold]\n"
        "Exploring multiple reasoning paths before converging on an answer",
        border_style="cyan"
    ))
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    question = "What are 3 ways to reduce carbon emissions in a city?"
    
    prompt = ChatPromptTemplate.from_template("""
    Question: {question}
    
    Let me explore multiple approaches:
    
    Approach 1:
    Approach 2:
    Approach 3:
    
    After exploring all approaches, the best solution is a combination of:
    """)
    
    chain = prompt | llm | StrOutputParser()
    
    console.print(f"\n[bold]Question:[/bold] {question}")
    console.print("\n[bold]Tree-of-Thought Approach:[/bold]")
    response = chain.invoke({"question": question})
    console.print(response)
    
    console.print("\n[dim]Note: ToT explores multiple reasoning paths for more comprehensive answers.[/dim]")

# ─── 3. Self-Consistency ───

def demonstrate_self_consistency():
    """Demonstrate Self-Consistency prompting"""
    
    console.print(Panel(
        "[bold]Self-Consistency Prompting[/bold]\n"
        "Generate multiple answers and take the most consistent one",
        border_style="cyan"
    ))
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    question = "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?"
    
    prompt = ChatPromptTemplate.from_template("""
    Question: {question}
    
    Let me think carefully and solve this:
    """)
    
    chain = prompt | llm | StrOutputParser()
    
    console.print(f"\n[bold]Question:[/bold] {question}")
    
    # Generate 3 answers
    answers = []
    for i in range(3):
        console.print(f"\n[bold]Attempt {i+1}:[/bold]")
        response = chain.invoke({"question": question})
        console.print(response)
        answers.append(response)
    
    console.print("\n[bold]Self-Consistency Result:[/bold]")
    console.print("The most consistent answer appears to be $0.05")
    
    console.print("\n[dim]Note: Self-consistency uses multiple attempts to find the most reliable answer.[/dim]")

# ─── 4. Meta-Prompting ───

def demonstrate_meta_prompting():
    """Demonstrate Meta-Prompting"""
    
    console.print(Panel(
        "[bold]Meta-Prompting[/bold]\n"
        "Asking the model to evaluate its own response",
        border_style="cyan"
    ))
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    question = "Explain what a token is in LLMs."
    
    # Primary prompt
    prompt = ChatPromptTemplate.from_template("""
    Question: {question}
    
    Answer concisely in 3-4 sentences.
    """)
    chain = prompt | llm | StrOutputParser()
    
    # Meta prompt (evaluate own response)
    meta_prompt = ChatPromptTemplate.from_template("""
    You asked: {question}
    
    Your previous answer: {answer}
    
    Now evaluate your own answer:
    1. Is it accurate? 
    2. Is it complete? 
    3. What would you add or improve?
    
    Improved version:
    """)
    meta_chain = meta_prompt | llm | StrOutputParser()
    
    console.print(f"\n[bold]Question:[/bold] {question}")
    
    console.print("\n[bold]Initial Response:[/bold]")
    initial = chain.invoke({"question": question})
    console.print(initial)
    
    console.print("\n[bold]Self-Evaluation & Improvement:[/bold]")
    improved = meta_chain.invoke({"question": question, "answer": initial})
    console.print(improved)
    
    console.print("\n[dim]Note: Meta-prompting enables self-evaluation and improvement.[/dim]")

# ─── 5. Prompt Chaining ───

def demonstrate_prompt_chaining():
    """Demonstrate Prompt Chaining"""
    
    console.print(Panel(
        "[bold]Prompt Chaining[/bold]\n"
        "Breaking a complex task into multiple sequential prompts",
        border_style="cyan"
    ))
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    text = "Artificial Intelligence is transforming industries by automating tasks and providing insights from data."
    
    # Step 1: Extract key points
    prompt1 = ChatPromptTemplate.from_template("""
    Extract 3 key points from this text:
    Text: {text}
    
    Key Points:
    """)
    chain1 = prompt1 | llm | StrOutputParser()
    
    # Step 2: Expand each point
    prompt2 = ChatPromptTemplate.from_template("""
    For each of these key points, provide a 1-sentence explanation:
    
    Key Points:
    {points}
    
    Explanations:
    """)
    chain2 = prompt2 | llm | StrOutputParser()
    
    # Step 3: Synthesize summary
    prompt3 = ChatPromptTemplate.from_template("""
    Synthesize these explanations into a single concise paragraph:
    
    Explanations:
    {explanations}
    
    Summary:
    """)
    chain3 = prompt3 | llm | StrOutputParser()
    
    console.print(f"\n[bold]Original Text:[/bold] {text}")
    
    # Execute chain
    console.print("\n[bold]Step 1 - Extract Key Points:[/bold]")
    points = chain1.invoke({"text": text})
    console.print(points)
    
    console.print("\n[bold]Step 2 - Expand Each Point:[/bold]")
    explanations = chain2.invoke({"points": points})
    console.print(explanations)
    
    console.print("\n[bold]Step 3 - Synthesize Summary:[/bold]")
    summary = chain3.invoke({"explanations": explanations})
    console.print(summary)
    
    console.print("\n[dim]Note: Prompt chaining breaks complex tasks into manageable steps.[/dim]")

# ─── 6. Negative Prompting ───

def demonstrate_negative_prompting():
    """Demonstrate Negative Prompting"""
    
    console.print(Panel(
        "[bold]Negative Prompting[/bold]\n"
        "Specifying what NOT to do in the prompt",
        border_style="cyan"
    ))
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    question = "Explain artificial intelligence."
    
    # Positive prompt (what to do)
    prompt_positive = ChatPromptTemplate.from_template("""
    Explain artificial intelligence in 3-4 sentences.
    
    {question}
    """)
    
    # Negative prompt (what NOT to do)
    prompt_negative = ChatPromptTemplate.from_template("""
    Explain artificial intelligence in 3-4 sentences.
    
    DO NOT use: jargon, technical terms, acronyms
    DO NOT mention: specific technologies, companies, or products
    DO NOT: write more than 4 sentences
    
    {question}
    """)
    
    chain_positive = prompt_positive | llm | StrOutputParser()
    chain_negative = prompt_negative | llm | StrOutputParser()
    
    console.print(f"\n[bold]Question:[/bold] {question}")
    
    console.print("\n[bold]Without Negative Prompting:[/bold]")
    response = chain_positive.invoke({"question": question})
    console.print(response)
    
    console.print("\n[bold]With Negative Prompting:[/bold]")
    response = chain_negative.invoke({"question": question})
    console.print(response)
    
    console.print("\n[dim]Note: Negative prompting constrains the model to avoid unwanted content.[/dim]")

# ─── Main ───

def main():
    """Main entry point"""
    
    console.print(Panel.fit(
        "[bold white]Week 2 - Day 1: Advanced Prompting Techniques[/bold white]\n"
        "[cyan]Lab 2.1 - Demonstrating 6 Prompting Techniques[/cyan]",
        border_style="cyan"
    ))
    
    techniques = [
        ("Chain-of-Thought (CoT)", demonstrate_cot),
        ("Tree-of-Thought (ToT)", demonstrate_tot),
        ("Self-Consistency", demonstrate_self_consistency),
        ("Meta-Prompting", demonstrate_meta_prompting),
        ("Prompt Chaining", demonstrate_prompt_chaining),
        ("Negative Prompting", demonstrate_negative_prompting),
    ]
    
    for name, func in techniques:
        console.print(f"\n{'='*70}")
        console.print(f"[bold cyan]Technique {techniques.index((name, func)) + 1}/{len(techniques)}: {name}[/bold cyan]")
        console.print("="*70)
        func()
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
