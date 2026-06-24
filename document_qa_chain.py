"""
Week 1 - Day 3: LangChain Core - Document Q&A Chain
Using BM25 retriever (keyword-based, no embeddings needed)
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever

load_dotenv()

# ─── Comprehensive Sample Document ───
SAMPLE_DOCUMENT = """
CalderR AI Internship Program - Week 1 Overview

Week 1 establishes the conceptual and practical foundation for the entire internship.
Interns move from understanding how large language models work to building their
first working agentic system using LangChain and Groq.

DETAILED INFORMATION:
Week Dates: Monday 22 June – Friday 26 June 2026
Theme: AI Fundamentals & Agentic AI Foundations
Primary Stack: Python · LangChain · Groq API · ChromaDB (in-memory)
Total Commitment: 20 hours (4 hours/day · 5 days)

Deliverable Due: Friday - 1 Intermediate Project + 1 Production Project

Learning Objectives:
- Understand how large language models work at a conceptual and practical level
- Distinguish between AI, ML, deep learning, and LLMs
- Explain what makes an AI 'agentic' versus reactive
- Build a simple conversational agent using LangChain and Groq
- Understand tokens, context windows, temperature, and sampling parameters
- Write effective system prompts for agent personas

DAY 1: LLM Foundations
Core Learning: Watch Karpathy 'Intro to LLMs'. Read Attention Is All You Need summary.
Study transformer architecture diagrams.
Applied Practice: Build first Groq API call in Python. Explore different models.
Experiment with temperature (0 vs 1 vs 2).

DAY 2: Agentic AI Concepts
Core Learning: Read 'ReAct: Synergizing Reasoning and Acting' paper summary.
Study the Agent Loop: Perceive → Plan → Act → Observe.
Applied Practice: Build a simple ReAct-style loop manually in Python (no framework).
Agent decides which of 3 tools to call based on user input.

DAY 3: LangChain Core
Core Learning: LangChain LCEL tutorial. Study Runnable, RunnablePassthrough, RunnableParallel.
Build 3 different chain patterns.
Applied Practice: Build a document Q&A chain (load text file → split → embed → retrieve → answer).
Use ChromaDB in-memory.

DAY 4: Prompt Engineering
Core Learning: Study system prompts, zero-shot vs few-shot, chain-of-thought.
Read Anthropic Prompt Engineering guide.
Applied Practice: Build a persona-based agent (customer support bot, code reviewer, data analyst).
Measure output quality differences.

DAY 5: Integration + Demo
Core Learning: Integrate all concepts: multi-turn chatbot with memory, custom persona,
Groq backend, rich terminal UI. Weekly standup prep.
Applied Practice: Demo your chatbot. Peer code review. Start intermediate project.

MODELS AVAILABLE ON GROQ:
1. llama-3.3-70b-versatile: Best quality, slower, higher accuracy
2. llama-3.1-8b-instant: Fastest, good for prototyping, lower latency
3. mixtral-8x7b-32768: Decommissioned (not available)

TEMPERATURE GUIDELINES:
- 0.0: Deterministic, consistent output, always same response
- 0.3: Slightly creative, still predictable
- 0.7: Balanced, good for most tasks, recommended default
- 1.0+: Creative, more random, varied responses
- 1.5+: Highly creative, may be incoherent
- 2.0: Highly random, may produce nonsensical output

KEY CONCEPTS:
- Token: Unit of text processed by LLMs (approx 4 chars = 1 token)
- Context window: Maximum tokens model can process at once
- Temperature: Controls randomness of output
- System prompt: Instruction that defines model's behavior
- Agent: Uses tools, makes decisions, takes actions
- ReAct: Reasoning + Acting pattern for agents
- Agent Loop: Perceive → Reason → Plan → Act → Observe → Repeat

RECOMMENDED RESOURCES:
1. Andrej Karpathy – Intro to Large Language Models (YouTube)
2. Andrej Karpathy – Let's Build GPT From Scratch (YouTube)
3. Attention Is All You Need (Vaswani et al., 2017)
4. ReAct: Synergizing Reasoning and Acting in LLMs
5. LangChain Python Docs – Get Started
6. Groq Cloud Documentation
7. Anthropic – What Is Constitutional AI?
8. LangChain Blog – LCEL Explained
9. LangChain Cookbook (GitHub)
10. DeepLearning.AI – LangChain for LLM Application Development

HANDS-ON LABS:
Lab 1.1: Your First Groq Agent - Python CLI chatbot with conversation history
Lab 1.2: Manual ReAct Loop - Implement ReAct agent without frameworks
Lab 1.3: Prompt Engineering A/B Test - Compare different system prompts

WEEKLY ASSESSMENT QUESTIONS:
1. Explain the difference between a language model and an agent.
2. What is the 'context window' and why does it matter?
3. Describe the ReAct pattern. When to use it vs simple chain?
4. What is LCEL in LangChain? Write a 5-line example using pipe operator.
5. Explain the role of temperature in LLM sampling. When to set it to 0?
6. Design a simple agent architecture for a customer support chatbot.

WEEKLY STANDUP REQUIREMENTS:
- Live demo of your chatbot (2 minutes)
- Explain one concept that surprised you
- Draw the agent loop your chatbot follows
- Share your most interesting code snippet
- Name one technical challenge and how you solved it

PROJECTS (Choose One Intermediate + One Production):
Intermediate Projects:
1. Intelligent CLI Assistant - Terminal-based AI assistant with conversation memory
2. Prompt Engineering Evaluator - Compare prompt effectiveness
3. Domain Expert Agent - Specialized agent with persona

Production Projects:
1. AI-Powered Customer Support Platform - FastAPI REST API with Streamlit UI
2. Multi-Model Comparison Engine - Benchmark different Groq models
3. Agentic Research Assistant - Research agent with planning and synthesis
"""

def create_document_qa_chain():
    """Build a document Q&A chain using BM25 retriever"""
    
    print("="*60)
    print("WEEK 1 - DAY 3: DOCUMENT Q&A CHAIN")
    print("LangChain Core - LCEL, Runnables")
    print("="*60)
    
    # ─── Step 1: Load Document ───
    print("\n[1] Loading document...")
    
    with open("sample_document.txt", "w", encoding="utf-8") as f:
        f.write(SAMPLE_DOCUMENT)
    
    loader = TextLoader("sample_document.txt")
    documents = loader.load()
    print(f"    Loaded {len(documents)} document(s)")
    
    # ─── Step 2: Split Document ───
    print("\n[2] Splitting document into chunks...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"    Created {len(chunks)} chunks")
    
    # ─── Step 3: Create BM25 Retriever ───
    print("\n[3] Creating BM25 retriever (keyword-based)...")
    
    retriever = BM25Retriever.from_documents(chunks)
    retriever.k = 3
    print(f"    BM25 retriever created with {len(chunks)} documents")
    
    # ─── Step 4: Initialize LLM ───
    print("\n[4] Initializing Groq LLM...")
    
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.3,
        api_key=os.getenv("GROQ_API_KEY")
    )
    print(f"    Model: llama-3.1-8b-instant")
    
    # ─── Step 5: Create Chains ───
    print("\n[5] Building chains with LCEL...")
    
    # Prompt for RAG
    rag_prompt = ChatPromptTemplate.from_template("""
    You are a helpful assistant answering questions about the CalderR AI Internship program.
    
    Context from the document:
    {context}
    
    Question: {question}
    
    Answer the question based ONLY on the context provided. If the answer is not in the context, say:
    "I don't have enough information to answer that question based on the provided document."
    
    Be specific and use information from the context.
    """)
    
    # ─── Chain 1: Simple RAG Chain ───
    print("\n    Chain 1: RAG Chain with RunnablePassthrough")
    
    rag_chain = (
        {
            "context": retriever | (lambda docs: "\n\n".join([d.page_content for d in docs])),
            "question": RunnablePassthrough()
        }
        | rag_prompt
        | llm
        | StrOutputParser()
    )
    
    # ─── Chain 2: Parallel Chain ───
    print("\n    Chain 2: RunnableParallel for multiple outputs")
    
    parallel_chain = RunnableParallel({
        "answer": rag_chain,
        "context_docs": retriever
    })
    
    # ─── Chain 3: Simple Chain without RAG ───
    print("\n    Chain 3: Simple Chain (without retrieval)")
    
    simple_prompt = ChatPromptTemplate.from_template("""
    Answer the following question about the CalderR AI Internship program.
    If you don't know, say "I don't have enough information."
    
    Question: {question}
    """)
    
    simple_chain = simple_prompt | llm | StrOutputParser()
    
    print("\n✅ All chains created successfully!")
    return rag_chain, parallel_chain, simple_chain

def test_chains(rag_chain, parallel_chain, simple_chain):
    """Test the chains with sample questions"""
    
    print("\n" + "="*60)
    print("TESTING RAG CHAIN")
    print("="*60)
    
    questions = [
        "What are the week dates for the internship?",
        "What models are available on Groq?",
        "What is the theme of Week 1?",
        "What is the primary stack used?",
        "What is Day 3 about?",
        "What is the temperature guideline for 0.7?",
        "Explain the ReAct pattern.",
        "What is the internship duration?",
        "What are the learning objectives?",
        "What projects can I choose?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n[{i}] Question: {question}")
        print("-" * 40)
        
        try:
            response = rag_chain.invoke(question)
            print(f"Answer: {response}")
        except Exception as e:
            print(f"Error: {e}")

def interactive_chat(rag_chain):
    """Interactive chat with the document Q&A system"""
    
    print("\n" + "="*60)
    print("INTERACTIVE DOCUMENT Q&A")
    print("Ask questions about the CalderR Internship Program")
    print("Commands: /exit")
    print("="*60)
    
    while True:
        try:
            question = input("\nYou: ").strip()
            
            if not question:
                continue
            
            if question.lower() == '/exit':
                print("\nGoodbye!")
                break
            
            print("\nAssistant: ", end="", flush=True)
            response = rag_chain.invoke(question)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")

def main():
    # Build chains
    rag_chain, parallel_chain, simple_chain = create_document_qa_chain()
    
    # Test chains
    test_chains(rag_chain, parallel_chain, simple_chain)
    
    # Interactive chat
    interactive_chat(rag_chain)

if __name__ == "__main__":
    main()