import faiss
import torch
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from sentence_transformers import CrossEncoder

import warnings
warnings.filterwarnings("ignore")

# 1. Generate Mock Docs
def generate_docs():
    docs = [
        Document(page_content="The Eiffel Tower is located in Paris, France.", metadata={"id": 1}),
        Document(page_content="The capital of France is Paris. It's famous for croissants.", metadata={"id": 2}),
        Document(page_content="Apples are highly nutritious fruits that contain a lot of fiber.", metadata={"id": 3}),
        Document(page_content="Paris is a city full of historical landmarks like the Louvre.", metadata={"id": 4}),
        Document(page_content="Many people travel to France to see the Eiffel Tower.", metadata={"id": 5})
    ]
    return docs

def demo_hybrid_retrieval(docs, query):
    print("\n--- 1. Hybrid Search (EnsembleRetriever) ---")
    
    # Keyword-based Retriever
    bm25_retriever = BM25Retriever.from_documents(docs)
    bm25_retriever.k = 2
    
    # Semantic Retriever
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(docs, embeddings, collection_name="hybrid_col")
    semantic_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    
    # Ensemble (weights: 50% keyword, 50% semantic)
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, semantic_retriever], 
        weights=[0.5, 0.5]
    )
    
    results = ensemble_retriever.invoke(query)
    for i, doc in enumerate(results):
        print(f"Result {i+1}: {doc.page_content}")
    return results

def demo_reranker(query, retrieved_docs):
    print("\n--- 2. Cross-Encoder Re-ranking ---")
    print("Initializing CrossEncoder (cross-encoder/ms-marco-MiniLM-L-6-v2)...")
    try:
        model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", max_length=512)
        
        # Prepare pairs: (Query, Document)
        pairs = [[query, doc.page_content] for doc in retrieved_docs]
        
        # Predict scores
        scores = model.predict(pairs)
        
        # Combine docs with scores and sort
        scored_docs = list(zip(retrieved_docs, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        print("Re-ranked Results:")
        for i, (doc, score) in enumerate(scored_docs):
            print(f"Rank {i+1} (Score: {score:.2f}): {doc.page_content}")
    except Exception as e:
        print(f"Error loading CrossEncoder: {e}")

def demo_multi_query(vectorstore, query):
    print("\n--- 3. Multi-Query Retrieval ---")
    try:
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
        
        retriever_from_llm = MultiQueryRetriever.from_llm(
            retriever=vectorstore.as_retriever(), llm=llm
        )
        
        # This will silently generate multiple variations of the query under the hood
        results = retriever_from_llm.invoke(query)
        print(f"Retrieved {len(results)} unique documents after generating multi-queries.")
        for i, doc in enumerate(results[:2]): # Show top 2
            print(f"Result {i+1}: {doc.page_content}")
    except Exception as e:
        print(f"Error with Multi-Query (missing API key?): {e}")

if __name__ == "__main__":
    docs = generate_docs()
    query = "Where is the Eiffel Tower?"
    
    print(f"Original Query: '{query}'")
    
    # 1. Hybrid Search
    hybrid_results = demo_hybrid_retrieval(docs, query)
    
    # 2. Re-ranking
    demo_reranker(query, hybrid_results)
    
    # 3. Multi Query
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(docs, embeddings, collection_name="multi_query_col")
    demo_multi_query(vectorstore, query)
    
    print("\nDay 4 Lab Completed Successfully!")
