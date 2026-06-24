"""
Week 1 - Day 3: LangChain Core - Chain Patterns
Demonstrating 3 different chain patterns with LCEL
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

load_dotenv()

def chain_pattern_1_simple():
    """Pattern 1: Simple Chain - prompt | llm | parser"""
    print("\n" + "="*60)
    print("PATTERN 1: Simple Chain")
    print("prompt | llm | parser")
    print("="*60)
    
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.7,
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Keep responses concise."),
        ("user", "Explain {concept} in simple terms.")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    response = chain.invoke({"concept": "LangChain"})
    print(f"Response: {response}")

def chain_pattern_2_passthrough():
    """Pattern 2: With RunnablePassthrough"""
    print("\n" + "="*60)
    print("PATTERN 2: With RunnablePassthrough")
    print("RunnablePassthrough passes data through unchanged")
    print("="*60)
    
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.7,
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    prompt = ChatPromptTemplate.from_template("""
    Context: {context}
    Question: {question}
    Answer: 
    """)
    
    chain = {
        "context": RunnablePassthrough() | (lambda x: f"Topic: {x['topic']}"),
        "question": RunnablePassthrough() | (lambda x: x['question'])
    } | prompt | llm | StrOutputParser()
    
    response = chain.invoke({
        "topic": "AI Agents",
        "question": "What is an AI agent?"
    })
    print(f"Response: {response}")

def chain_pattern_3_parallel():
    """Pattern 3: RunnableParallel - Multiple chains in parallel"""
    print("\n" + "="*60)
    print("PATTERN 3: RunnableParallel")
    print("Run multiple chains in parallel")
    print("="*60)
    
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.7,
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    prompt_short = ChatPromptTemplate.from_messages([
        ("system", "You are a concise assistant. Answer in 1 sentence."),
        ("user", "Summarize {topic}")
    ])
    
    prompt_detailed = ChatPromptTemplate.from_messages([
        ("system", "You are a detailed assistant. Give comprehensive answer."),
        ("user", "Explain {topic} in detail")
    ])
    
    chain = RunnableParallel({
        "short_answer": prompt_short | llm | StrOutputParser(),
        "detailed_answer": prompt_detailed | llm | StrOutputParser()
    })
    
    result = chain.invoke({"topic": "LangChain LCEL"})
    
    print(f"Short Answer: {result['short_answer']}")
    print(f"\nDetailed Answer: {result['detailed_answer']}")

def main():
    print("="*60)
    print("WEEK 1 - DAY 3: LANGCHAIN CHAIN PATTERNS")
    print("3 Different Chain Patterns with LCEL")
    print("="*60)
    
    chain_pattern_1_simple()
    chain_pattern_2_passthrough()
    chain_pattern_3_parallel()

if __name__ == "__main__":
    main()