import os
import datetime
import numpy as np
import faiss
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# --- 1. MOCK DOCUMENT GENERATION (Simulating 50 PDF pages) ---
def generate_mock_documents():
    print("Generating 50 mock PDF pages...")
    docs = []
    base_date = datetime.date(2026, 7, 7)
    
    for i in range(1, 51):
        content = f"This is the content of page {i} of the AI engineering manual. "
        content += f"On this page, we discuss topic {i}. " * 10
        
        doc = Document(
            page_content=content,
            metadata={
                "source": "AI_Engineering_Manual.pdf",
                "page": i,
                "date": str(base_date + datetime.timedelta(days=i))
            }
        )
        docs.append(doc)
    return docs

def demo_chroma(docs, embeddings):
    print("\n--- ChromaDB Pipeline ---")
    print("Splitting documents...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    splits = text_splitter.split_documents(docs)
    print(f"Split {len(docs)} pages into {len(splits)} chunks.")

    print("Storing in persistent ChromaDB...")
    persist_directory = "./chroma_db"
    
    # Create or load the vector store
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=embeddings, 
        persist_directory=persist_directory,
        collection_name="manual_collection"
    )
    
    print("\nQuerying ChromaDB with Metadata Filters...")
    query = "What is discussed on page 42?"
    
    # Filter for a specific page using metadata
    search_docs = vectorstore.similarity_search(
        query, 
        k=2, 
        filter={"page": 42}
    )
    
    for i, doc in enumerate(search_docs):
        print(f"Result {i+1}: [Page {doc.metadata['page']}] {doc.page_content[:60]}...")

def demo_faiss():
    print("\n--- FAISS Tutorial ---")
    # Generate some random vectors (e.g., 384 dimensions for all-MiniLM-L6-v2)
    dimension = 384
    num_vectors = 10000
    print(f"Generating {num_vectors} random vectors of dimension {dimension}...")
    
    # FAISS expects numpy arrays of type float32
    vectors = np.random.random((num_vectors, dimension)).astype('float32')
    
    # 1. IndexFlatL2 (Exact Search - exhaustive, perfect accuracy but slower)
    print("\nBuilding IndexFlatL2 (Exact Search)...")
    index_flat = faiss.IndexFlatL2(dimension)
    index_flat.add(vectors)
    print(f"Total vectors in IndexFlatL2: {index_flat.ntotal}")
    
    # 2. IndexIVFFlat (Approximate Search - faster, uses Voronoi cells/clustering)
    print("Building IndexIVFFlat (Approximate Search)...")
    nlist = 100  # Number of clusters
    quantizer = faiss.IndexFlatL2(dimension)
    index_ivf = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_L2)
    
    # IVF needs to be trained on the data distribution before adding vectors
    index_ivf.train(vectors)
    index_ivf.add(vectors)
    print(f"Total vectors in IndexIVFFlat: {index_ivf.ntotal}")
    
    # Query both indexes
    query_vector = np.random.random((1, dimension)).astype('float32')
    
    print("\nSearching IndexFlatL2...")
    distances, indices = index_flat.search(query_vector, k=3)
    print(f"Top 3 indices: {indices[0]}, Distances: {distances[0]}")
    
    print("Searching IndexIVFFlat...")
    index_ivf.nprobe = 10 # Number of clusters to visit
    distances_ivf, indices_ivf = index_ivf.search(query_vector, k=3)
    print(f"Top 3 indices: {indices_ivf[0]}, Distances: {distances_ivf[0]}")

if __name__ == "__main__":
    print("Initializing embedding model (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    docs = generate_mock_documents()
    
    demo_chroma(docs, embeddings)
    demo_faiss()
    
    print("\nDay 2 Lab Completed Successfully!")
