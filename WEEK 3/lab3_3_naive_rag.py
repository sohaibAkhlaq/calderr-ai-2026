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
from dotenv import load_dotenv

load_dotenv()

# --- 1. MOCK DOCUMENT GENERATION ---
def generate_mock_documents():
    docs = []
    # Create some specific facts so we can query them
    facts = [
        (1, "The capital of the AI nation is Neural City."),
        (10, "The learning rate used for the primary model was 0.0034."),
        (25, "In 2026, CalderR achieved a 99% accuracy on the benchmark."),
        (40, "The system architecture relies on a microservices pattern with ChromaDB."),
        (50, "The final deployment requires 32GB of RAM and 4 GPUs.")
    ]
    
    fact_dict = dict(facts)
    
    for i in range(1, 51):
        content = f"Page {i} of the AI engineering manual. "
        if i in fact_dict:
            content += f"CRITICAL INFO: {fact_dict[i]} "
        content += "General filler text about AI models and embeddings. " * 30
        
        doc = Document(page_content=content, metadata={"page": i})
        docs.append(doc)
    return docs

def evaluate_rag(docs, embeddings, chunk_size, k_val):
    print(f"\n--- Testing RAG with Chunk Size: {chunk_size}, K: {k_val} ---")
    
    # Split
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=50)
    splits = splitter.split_documents(docs)
    
    # Store
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, collection_name=f"rag_col_{chunk_size}_{k_val}")
    retriever = vectorstore.as_retriever(search_kwargs={"k": k_val})
    
    # Setup LLM & Chain
    try:
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    except Exception as e:
        print("Error initializing Groq LLM (missing API key?). Using mock responses.")
        llm = None
        
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer, say that you don't know. "
        "Context: {context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    if llm:
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    questions = [
        "What is the capital of the AI nation?",
        "What learning rate was used for the primary model?",
        "What accuracy did CalderR achieve in 2026?",
        "What architecture does the system rely on?",
        "What are the final deployment requirements?"
    ]
    
    for q in questions:
        print(f"\nQ: {q}")
        if llm:
            try:
                response = rag_chain.invoke({"input": q})
                print(f"A: {response['answer']}")
            except Exception as e:
                print(f"A: [Error invoking LLM: {e}]")
        else:
            # Just test retrieval if no API key
            retrieved = retriever.invoke(q)
            print(f"A: [Mock LLM] Found context in {len(retrieved)} chunks. Top chunk: {retrieved[0].page_content[:50]}...")

if __name__ == "__main__":
    docs = generate_mock_documents()
    print("Initializing embedding model (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Experiment 1: Small Chunks, low K
    evaluate_rag(docs, embeddings, chunk_size=256, k_val=3)
    
    # Experiment 2: Large Chunks, high K
    evaluate_rag(docs, embeddings, chunk_size=1024, k_val=10)
    
    print("\nDay 3 Lab Completed Successfully!")
