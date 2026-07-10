import faiss
import torch
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

import warnings
warnings.filterwarnings("ignore")

# --- 1. BUILD THE RAG SYSTEM ---
def build_rag_system():
    """Build a complete RAG pipeline for evaluation."""
    print("Building RAG system for evaluation...")
    
    # Knowledge Base (our ground truth documents)
    docs = [
        Document(page_content="Python was created by Guido van Rossum and first released in 1991. It emphasizes code readability.", metadata={"topic": "python"}),
        Document(page_content="JavaScript is a programming language used for web development. It was created by Brendan Eich in 1995.", metadata={"topic": "javascript"}),
        Document(page_content="Machine learning is a subset of artificial intelligence that learns from data without being explicitly programmed.", metadata={"topic": "ml"}),
        Document(page_content="Docker is a platform for containerizing applications. It uses OS-level virtualization to deliver software in packages called containers.", metadata={"topic": "docker"}),
        Document(page_content="PostgreSQL is an advanced open-source relational database. It supports both SQL and JSON querying.", metadata={"topic": "database"}),
        Document(page_content="REST APIs use HTTP methods like GET, POST, PUT, DELETE. They follow a stateless client-server architecture.", metadata={"topic": "api"}),
        Document(page_content="Git is a distributed version control system created by Linus Torvalds in 2005 for Linux kernel development.", metadata={"topic": "git"}),
        Document(page_content="Neural networks are computing systems inspired by biological neural networks. They consist of layers of interconnected nodes.", metadata={"topic": "ml"}),
        Document(page_content="Kubernetes orchestrates containerized applications across clusters of machines. It automates deployment, scaling, and management.", metadata={"topic": "devops"}),
        Document(page_content="FastAPI is a modern Python web framework for building APIs. It is based on standard Python type hints and is very fast.", metadata={"topic": "python"}),
    ]
    
    # Split
    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30)
    splits = splitter.split_documents(docs)
    
    # Embed & Store
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(splits, embeddings, collection_name="eval_col")
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    return retriever, vectorstore

# --- 2. EVALUATION DATASET ---
def create_eval_dataset():
    """Create a dataset of questions, ground truth answers, and expected contexts."""
    eval_data = [
        {
            "question": "Who created Python?",
            "ground_truth": "Python was created by Guido van Rossum.",
            "expected_topic": "python"
        },
        {
            "question": "What is machine learning?",
            "ground_truth": "Machine learning is a subset of artificial intelligence that learns from data without being explicitly programmed.",
            "expected_topic": "ml"
        },
        {
            "question": "What is Docker used for?",
            "ground_truth": "Docker is a platform for containerizing applications using OS-level virtualization.",
            "expected_topic": "docker"
        },
        {
            "question": "When was JavaScript created?",
            "ground_truth": "JavaScript was created in 1995 by Brendan Eich.",
            "expected_topic": "javascript"
        },
        {
            "question": "What HTTP methods do REST APIs use?",
            "ground_truth": "REST APIs use HTTP methods like GET, POST, PUT, DELETE.",
            "expected_topic": "api"
        },
        {
            "question": "Who created Git?",
            "ground_truth": "Git was created by Linus Torvalds in 2005.",
            "expected_topic": "git"
        },
        {
            "question": "What is FastAPI?",
            "ground_truth": "FastAPI is a modern Python web framework for building APIs based on type hints.",
            "expected_topic": "python"
        },
        {
            "question": "What does Kubernetes do?",
            "ground_truth": "Kubernetes orchestrates containerized applications across clusters, automating deployment, scaling, and management.",
            "expected_topic": "devops"
        },
    ]
    return eval_data

# --- 3. MANUAL RAGAS-STYLE METRICS ---
def compute_context_precision(retrieved_docs, expected_topic):
    """How many of the retrieved docs are actually relevant (match expected topic)?"""
    relevant = sum(1 for doc in retrieved_docs if doc.metadata.get("topic") == expected_topic)
    return relevant / len(retrieved_docs) if retrieved_docs else 0.0

def compute_answer_relevancy(answer, ground_truth):
    """Simple word-overlap metric between answer and ground truth."""
    answer_words = set(answer.lower().split())
    truth_words = set(ground_truth.lower().split())
    if not truth_words:
        return 0.0
    overlap = answer_words & truth_words
    return len(overlap) / len(truth_words)

def compute_faithfulness(answer, retrieved_docs):
    """How much of the answer can be traced back to retrieved context?"""
    context_text = " ".join([doc.page_content for doc in retrieved_docs]).lower()
    answer_words = answer.lower().split()
    if not answer_words:
        return 0.0
    supported = sum(1 for word in answer_words if word in context_text)
    return supported / len(answer_words)

# --- 4. RUN EVALUATION ---
def run_evaluation(retriever):
    eval_data = create_eval_dataset()
    
    # Setup LLM Chain
    try:
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
        system_prompt = (
            "You are a helpful assistant. Use the following context to answer the question concisely. "
            "Context: {context}"
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        qa_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, qa_chain)
        has_llm = True
    except Exception:
        has_llm = False
        print("No Groq API key found. Using retrieval-only evaluation.\n")
    
    print("\n" + "="*70)
    print("RAG EVALUATION REPORT")
    print("="*70)
    
    total_precision = 0
    total_relevancy = 0
    total_faithfulness = 0
    
    for i, item in enumerate(eval_data):
        q = item["question"]
        gt = item["ground_truth"]
        topic = item["expected_topic"]
        
        print(f"\n--- Q{i+1}: {q} ---")
        
        # Retrieve
        retrieved = retriever.invoke(q)
        
        # Generate answer
        if has_llm:
            try:
                response = rag_chain.invoke({"input": q})
                answer = response["answer"]
            except Exception as e:
                answer = f"[LLM Error: {e}]"
        else:
            answer = retrieved[0].page_content if retrieved else "No context found."
        
        print(f"Answer: {answer}")
        print(f"Ground Truth: {gt}")
        
        # Compute Metrics
        precision = compute_context_precision(retrieved, topic)
        relevancy = compute_answer_relevancy(answer, gt)
        faithfulness = compute_faithfulness(answer, retrieved)
        
        print(f"Context Precision: {precision:.2f}")
        print(f"Answer Relevancy:  {relevancy:.2f}")
        print(f"Faithfulness:      {faithfulness:.2f}")
        
        total_precision += precision
        total_relevancy += relevancy
        total_faithfulness += faithfulness
    
    n = len(eval_data)
    print("\n" + "="*70)
    print("AGGREGATE SCORES")
    print("="*70)
    print(f"Avg Context Precision: {total_precision/n:.2f}")
    print(f"Avg Answer Relevancy:  {total_relevancy/n:.2f}")
    print(f"Avg Faithfulness:      {total_faithfulness/n:.2f}")
    print(f"Overall RAG Score:     {(total_precision + total_relevancy + total_faithfulness) / (3*n):.2f}")
    print("="*70)

# --- 5. WEEKLY ASSESSMENT ---
def weekly_assessment():
    print("\n" + "="*70)
    print("WEEK 3 - WEEKLY ASSESSMENT ANSWERS")
    print("="*70)
    
    assessment = {
        "Q1: What are embeddings and why do they matter?":
            "Embeddings are dense vector representations of text that capture semantic meaning. "
            "They matter because they allow us to compute mathematical similarity between pieces of "
            "text, enabling semantic search, clustering, and retrieval-augmented generation.",
        
        "Q2: What is the tradeoff in chunk size selection?":
            "Small chunks (256) give precise, focused context but may miss broader information. "
            "Large chunks (1024) provide more context but can dilute the relevant information with noise "
            "and use up the LLM's context window faster. The optimal size depends on the use case.",
        
        "Q3: What is the purpose of a Cross-Encoder in RAG?":
            "A Cross-Encoder takes BOTH the query and a document as input simultaneously and outputs "
            "a relevancy score. It is used as a re-ranker after initial retrieval to re-sort the top-K "
            "results by true relevance, significantly improving answer quality.",
        
        "Q4: How would you design a multi-tenant RAG system?":
            "Each tenant gets their own ChromaDB collection (or namespace). Documents are tagged with "
            "tenant_id metadata. Queries are filtered by tenant_id before retrieval. Access control is "
            "enforced at the API layer. This ensures data isolation while sharing infrastructure.",
        
        "Q5: What is the difference between BM25 and semantic search?":
            "BM25 is a keyword-based algorithm that matches exact words using term frequency. Semantic "
            "search uses embeddings to match meaning. BM25 is great for exact terms (IDs, names) while "
            "semantic search handles synonyms and context. Hybrid search combines both for best results.",
    }
    
    for question, answer in assessment.items():
        print(f"\n{question}")
        print(f"  → {answer}")

if __name__ == "__main__":
    retriever, vectorstore = build_rag_system()
    run_evaluation(retriever)
    weekly_assessment()
    print("\nDay 5 Lab Completed Successfully!")
