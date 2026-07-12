"""
Week 3 Intermediate Project — Option C: Hybrid Search Engine
=============================================================
A CLI search tool with STRICT error handling and fault tolerance.
Downloads a real PDF ("Attention Is All You Need" from Arxiv),
processes it, and provides hybrid search (BM25 + Semantic) with
cross-encoder re-ranking.
"""

# pyrefly: ignore [missing-import]
import faiss
import torch
import os
import sys
import json
import urllib.request
import traceback
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
# pyrefly: ignore [missing-import]
from langchain.retrievers import EnsembleRetriever
from langchain_community.document_loaders import PyPDFLoader
from sentence_transformers import CrossEncoder

import warnings
warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION & EXCEPTIONS
# ============================================================
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(PROJECT_DIR, "docs")
CHROMA_DIR = os.path.join(PROJECT_DIR, "chroma_hybrid_db")
EVAL_RESULTS_FILE = os.path.join(PROJECT_DIR, "evaluation_results.json")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
BM25_WEIGHT = 0.4
SEMANTIC_WEIGHT = 0.6
TOP_K = 10
RERANK_TOP_N = 3

class PipelineError(Exception):
    """Custom exception raised when a critical pipeline step fails."""
    pass


# ============================================================
# 1. DOCUMENT INGESTION (Strict Error Handling)
# ============================================================
def download_sample_pdf():
    """Download a 'attention is all you need' PDF for testing."""
    print("\n[STEP 1] Downloading 'attention is all you need' PDF...")
    os.makedirs(PDF_DIR, exist_ok=True)
    pdf_path = os.path.join(PDF_DIR, "attention_is_all_you_need.pdf")

    if os.path.exists(pdf_path):
        print(f"  PDF already exists: {pdf_path}")
        return pdf_path

    url = "https://arxiv.org/pdf/1706.03762.pdf"
    try:
        urllib.request.urlretrieve(url, pdf_path)
        print(f"  Downloaded to: {pdf_path}")
        return pdf_path
    except Exception as e:
        raise PipelineError(f"Failed to download PDF from {url}. Error: {e}")


def load_documents(pdf_path):
    """Load the specific PDF file. Hard abort if it fails."""
    print(f"\n[STEP 2] Loading Document from {pdf_path}...")
    
    if not os.path.exists(pdf_path):
        raise PipelineError(f"PDF file not found at {pdf_path}")
    
    try:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
    except ImportError:
        raise PipelineError("Missing 'pypdf' package. Please run: pip install pypdf")
    except Exception as e:
        raise PipelineError(f"PyPDFLoader failed to read {pdf_path}. Error: {e}")

    if not docs:
        raise PipelineError("PDF was loaded, but 0 pages of text were extracted! Cannot proceed.")

    # Tag all docs with topic 'python' for evaluation
    for doc in docs:
        doc.metadata["topic"] = "python"
        
    print(f"  Successfully loaded {len(docs)} pages.")
    return docs


# ============================================================
# 2. TEXT SPLITTING
# ============================================================
def split_documents(docs):
    """Split documents into chunks. Hard abort if 0 chunks."""
    print(f"\n[STEP 3] Splitting Documents (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    
    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        splits = splitter.split_documents(docs)
    except Exception as e:
        raise PipelineError(f"Text splitting failed. Error: {e}")
        
    if not splits:
        raise PipelineError("Text splitting resulted in 0 chunks! Cannot build vector store.")

    print(f"  Created {len(splits)} chunks.")
    return splits


# ============================================================
# 3. EMBEDDING & VECTOR STORE
# ============================================================
def create_embeddings():
    """Initialize the embedding model. Catch download errors."""
    print(f"\n[STEP 4] Loading Embedding Model ({EMBEDDING_MODEL})...")
    try:
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        print("  Embedding model loaded successfully!")
        return embeddings
    except Exception as e:
        raise PipelineError(f"Failed to load embedding model {EMBEDDING_MODEL}. Is HuggingFace down? Error: {e}")


def create_vector_store(splits, embeddings):
    """Store embedded chunks in ChromaDB."""
    print(f"\n[STEP 5] Storing in ChromaDB ({CHROMA_DIR})...")
    try:
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            collection_name="attention_paper_col",
            persist_directory=CHROMA_DIR
        )
        print(f"  Stored {len(splits)} chunks in ChromaDB")
        return vectorstore
    except Exception as e:
        raise PipelineError(f"Failed to create ChromaDB collection. Check disk permissions. Error: {e}")


# ============================================================
# 4. HYBRID RETRIEVER
# ============================================================
def create_hybrid_retriever(splits, vectorstore):
    """Create a hybrid retriever combining BM25 + Semantic search."""
    print(f"\n[STEP 6] Building Hybrid Retriever (BM25={BM25_WEIGHT}, Semantic={SEMANTIC_WEIGHT})...")
    try:
        bm25_retriever = BM25Retriever.from_documents(splits)
        bm25_retriever.k = TOP_K
        
        semantic_retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
        
        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, semantic_retriever],
            weights=[BM25_WEIGHT, SEMANTIC_WEIGHT]
        )
        print("  Hybrid retriever ready!")
        return ensemble_retriever
    except Exception as e:
        raise PipelineError(f"Failed to initialize EnsembleRetriever. Error: {e}")


# ============================================================
# 5. CROSS-ENCODER RE-RANKER
# ============================================================
def load_reranker():
    """Load the cross-encoder re-ranking model."""
    print(f"\n[STEP 7] Loading Cross-Encoder Re-ranker ({RERANKER_MODEL})...")
    try:
        reranker = CrossEncoder(RERANKER_MODEL, max_length=512)
        print("  Re-ranker loaded successfully!")
        return reranker
    except Exception as e:
        raise PipelineError(f"Failed to load cross-encoder. Error: {e}")


def rerank_results(query, docs, reranker, top_n=RERANK_TOP_N):
    if not reranker or not docs:
        return docs[:top_n]
    
    try:
        pairs = [[query, doc.page_content] for doc in docs]
        scores = reranker.predict(pairs)
        scored_docs = list(zip(docs, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [(doc, float(score)) for doc, score in scored_docs[:top_n]]
    except Exception as e:
        print(f"  Warning: Re-ranking failed ({e}), falling back to standard hybrid ranking.")
        return docs[:top_n]


# ============================================================
# 6. EVALUATION SYSTEM (Targeted at Attention Paper)
# ============================================================
def create_evaluation_dataset():
    """Create evaluation queries tailored to the 'Attention Is All You Need' paper."""
    return [
        {"query": "What is the primary mechanism replacing recurrence in this architecture?", "expected": "attention mechanism", "topic": "transformers"},
        {"query": "What is the name of the new network architecture introduced?", "expected": "Transformer", "topic": "transformers"},
        {"query": "What is the formula for scaled dot-product attention?", "expected": "softmax", "topic": "transformers"},
        {"query": "How many identical layers does the encoder stack have?", "expected": "N = 6", "topic": "transformers"},
        {"query": "What optimization algorithm was used during training?", "expected": "Adam optimizer", "topic": "transformers"},
        {"query": "What prevents leftward information flow in the decoder?", "expected": "masking", "topic": "transformers"},
        {"query": "What is used to inject sequence order information since there are no recurrences?", "expected": "positional encodings", "topic": "transformers"},
        {"query": "How many attention heads (h) were used in the base model?", "expected": "h = 8", "topic": "transformers"},
        {"query": "What dataset was used for English-to-German translation?", "expected": "WMT 2014 English-to-German", "topic": "transformers"},
        {"query": "What regularization technique is applied to the output of each sub-layer?", "expected": "dropout", "topic": "transformers"}
    ]

def compute_context_precision(retrieved_docs, expected_topic):
    if not retrieved_docs:
        return 0.0
    docs_only = [d[0] if isinstance(d, tuple) else d for d in retrieved_docs]
    relevant = sum(1 for doc in docs_only if doc.metadata.get("topic") == expected_topic)
    return relevant / len(docs_only)

def compute_answer_relevancy(top_doc_content, expected_answer):
    if not top_doc_content:
        return 0.0
    expected_words = expected_answer.lower().split()
    content_lower = top_doc_content.lower()
    found = sum(1 for word in expected_words if word in content_lower)
    return found / len(expected_words) if expected_words else 0.0

def run_evaluation(retriever, reranker):
    print("\n" + "=" * 70)
    print("RUNNING EVALUATION ON 'ATTENTION IS ALL YOU NEED' PAPER")
    print("=" * 70)

    eval_data = create_evaluation_dataset()
    results = []
    total_precision = total_relevancy = 0

    for i, item in enumerate(eval_data):
        query = item["query"]
        expected = item["expected"]
        topic = item["topic"]
        
        try:
            retrieved = retriever.invoke(query)
            reranked = rerank_results(query, retrieved, reranker)
            top_content = reranked[0][0].page_content if reranked else ""
            
            precision = compute_context_precision(reranked, topic)
            relevancy = compute_answer_relevancy(top_content, expected)
            
            total_precision += precision
            total_relevancy += relevancy
            status = "PASS" if relevancy >= 0.5 else "FAIL"
            
            results.append({"query": query, "status": status})
            print(f"  Q{i+1:02d} [{status}] P:{precision:.2f} R:{relevancy:.2f} | {query}")
        except Exception as e:
            print(f"  Q{i+1:02d} [ERROR] Query failed: {e}")

    n = len(eval_data)
    avg_p = total_precision / n
    avg_r = total_relevancy / n
    print("\n" + "-" * 70)
    print(f"  Avg Context Precision: {avg_p:.2f}")
    print(f"  Avg Answer Relevancy:  {avg_r:.2f}")
    print("=" * 70)


# ============================================================
# MAIN ORCHESTRATOR WITH GLOBAL EXCEPTION HANDLING
# ============================================================
def main():
    print("=" * 70)
    print("PRODUCTION-GRADE HYBRID SEARCH ENGINE")
    print("=" * 70)

    try:
        # Pipeline Steps (Will abort immediately if any step fails)
        pdf_path = download_sample_pdf()
        docs = load_documents(pdf_path)
        splits = split_documents(docs)
        embeddings = create_embeddings()
        vectorstore = create_vector_store(splits, embeddings)
        retriever = create_hybrid_retriever(splits, vectorstore)
        reranker = load_reranker()
        
        # Eval
        run_evaluation(retriever, reranker)
        
        # Interactive Search
        if "--no-interactive" not in sys.argv:
            print("\nType your query and press Enter. Type 'quit' to exit.")
            while True:
                try:
                    query = input("\n Query: ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if not query or query.lower() in ('quit', 'exit', 'q'):
                    break
                retrieved = retriever.invoke(query)
                reranked = rerank_results(query, retrieved, reranker, top_n=3)
                print(f"\n  Found {len(retrieved)} results. Top {len(reranked)} after re-ranking:\n")
                for rank, (doc, score) in enumerate(reranked, 1):
                    print(f"  [{rank}] (Score: {score:.2f})")
                    print(f"      {doc.page_content[:200]}...\n")
                    
    except PipelineError as e:
        # This catches our explicit aborts
        print("\n" + "!" * 70)
        print("CRITICAL PIPELINE FAILURE (Handled Gracefully)")
        print(f"Error: {e}")
        print("Pipeline aborted to prevent cascading failures.")
        print("!" * 70)
        sys.exit(1)
    except Exception as e:
        # This catches unexpected runtime errors
        print("\n" + "!" * 70)
        print("UNEXPECTED RUNTIME ERROR")
        traceback.print_exc()
        print("!" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
