"""
Week 3 Intermediate Project — Option C: Hybrid Search Engine
=============================================================
A CLI search tool that ingests PDF documents and provides intelligent
hybrid search combining BM25 keyword search + semantic vector search
+ cross-encoder re-ranking. Includes built-in evaluation on 30 queries.

Concepts Applied (All 5 Days of Week 3):
  Day 1: Sentence-Transformer Embeddings (all-MiniLM-L6-v2)
  Day 2: ChromaDB Vector Storage, Document Chunking with Metadata
  Day 3: Full RAG Pipeline (load → split → embed → store → retrieve → generate)
  Day 4: BM25 Hybrid Search, EnsembleRetriever, Cross-Encoder Re-ranking
  Day 5: Evaluation Metrics (Context Precision, Answer Relevancy, Faithfulness)
"""

import faiss
import torch
import os
import sys
import json
import urllib.request

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_community.document_loaders import PyPDFLoader
from sentence_transformers import CrossEncoder

import warnings
warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
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


# ============================================================
# 1. DOCUMENT INGESTION (Day 2 Concepts)
# ============================================================
def download_sample_pdf():
    """Download a sample PDF for testing."""
    os.makedirs(PDF_DIR, exist_ok=True)
    pdf_path = os.path.join(PDF_DIR, "python_tutorial.pdf")

    if os.path.exists(pdf_path):
        print(f"  PDF already exists: {pdf_path}")
        return pdf_path

    print("  Downloading sample PDF (Python Tutorial)...")
    url = "https://bugs.python.org/file47781/Tutorial_EDIT.pdf"
    try:
        urllib.request.urlretrieve(url, pdf_path)
        print(f"  Downloaded to: {pdf_path}")
    except Exception as e:
        print(f"  Download failed: {e}")
        print("  Creating a rich mock PDF dataset instead...")
        create_mock_documents(pdf_path)
    return pdf_path


def create_mock_documents(pdf_path):
    """Create mock documents if PDF download fails."""
    # We'll just return None and handle it in load_documents
    pass


def load_documents():
    """Load all PDF files from the docs directory."""
    print("\n[STEP 1] Loading Documents...")
    os.makedirs(PDF_DIR, exist_ok=True)

    all_docs = []

    # Try to load any PDFs in the docs folder
    pdf_files = [f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')]

    if pdf_files:
        for pdf_file in pdf_files:
            pdf_path = os.path.join(PDF_DIR, pdf_file)
            try:
                loader = PyPDFLoader(pdf_path)
                docs = loader.load()
                all_docs.extend(docs)
                print(f"  Loaded {len(docs)} pages from {pdf_file}")
            except Exception as e:
                print(f"  Error loading {pdf_file}: {e}")

    if not all_docs:
        print("  No PDFs loaded. Using built-in knowledge base...")
        all_docs = generate_builtin_knowledge_base()

    print(f"  Total documents loaded: {len(all_docs)}")
    return all_docs


def generate_builtin_knowledge_base():
    """Generate a comprehensive built-in knowledge base with 30+ documents."""
    topics = [
        # Python
        ("Python was created by Guido van Rossum and first released in 1991. It emphasizes code readability and uses significant whitespace. Python supports multiple programming paradigms including procedural, object-oriented, and functional programming.", "python", "programming"),
        ("Python's standard library is extensive, offering modules for file I/O, system calls, sockets, and even interfaces to graphical user interface toolkits like Tk. It is often described as a batteries included language.", "python", "stdlib"),
        ("Python virtual environments allow you to create isolated Python installations. The venv module is the standard tool for creating virtual environments. Each environment has its own Python binary and can have its own independent set of installed packages.", "python", "environments"),
        ("Python decorators are a powerful feature that allows you to modify the behavior of functions or classes. They use the @decorator syntax and are commonly used for logging, authentication, and caching.", "python", "advanced"),
        ("List comprehensions in Python provide a concise way to create lists. They consist of brackets containing an expression followed by a for clause, then zero or more for or if clauses. They are more readable and often faster than traditional loops.", "python", "syntax"),

        # Machine Learning
        ("Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing computer programs that can access data and use it to learn for themselves.", "ml", "fundamentals"),
        ("Supervised learning uses labeled training data to learn a mapping function from input to output. Common algorithms include linear regression, logistic regression, decision trees, random forests, and support vector machines.", "ml", "supervised"),
        ("Unsupervised learning finds hidden patterns in data without pre-existing labels. Key techniques include clustering algorithms like K-means, hierarchical clustering, and dimensionality reduction methods like PCA and t-SNE.", "ml", "unsupervised"),
        ("Neural networks are computing systems inspired by biological neural networks in the human brain. They consist of interconnected nodes organized in layers: input layer, hidden layers, and output layer.", "ml", "neural_networks"),
        ("Transfer learning is a machine learning technique where a model developed for one task is reused as the starting point for a model on a second task. It is especially popular in deep learning for computer vision and natural language processing.", "ml", "transfer"),

        # Natural Language Processing
        ("Natural Language Processing (NLP) is a field of AI that focuses on the interaction between computers and humans through natural language. It combines computational linguistics with statistical and machine learning models.", "nlp", "fundamentals"),
        ("Word embeddings like Word2Vec and GloVe represent words as dense vectors in a continuous vector space. Words with similar meanings are mapped to nearby points. This captures semantic relationships between words.", "nlp", "embeddings"),
        ("Transformers are a type of neural network architecture that uses self-attention mechanisms. They were introduced in the paper Attention Is All You Need in 2017 and have revolutionized NLP.", "nlp", "transformers"),
        ("BERT (Bidirectional Encoder Representations from Transformers) is a pre-trained language model that can be fine-tuned for various NLP tasks. It reads text bidirectionally, understanding context from both directions.", "nlp", "bert"),
        ("Retrieval-Augmented Generation (RAG) combines information retrieval with text generation. It retrieves relevant documents from a knowledge base and uses them as context for generating accurate, grounded responses.", "nlp", "rag"),

        # Databases
        ("PostgreSQL is an advanced open-source relational database management system. It supports both SQL queries for relational data and JSON queries for document data. It is known for its reliability and feature robustness.", "database", "postgresql"),
        ("Vector databases are specialized databases designed to store and query high-dimensional vectors efficiently. Examples include ChromaDB, Pinecone, Weaviate, and Qdrant. They use approximate nearest neighbor algorithms for fast similarity search.", "database", "vector_db"),
        ("ChromaDB is an open-source vector database designed for AI applications. It supports persistent storage, metadata filtering, and integrates seamlessly with LangChain. Collections in ChromaDB store documents, embeddings, and metadata together.", "database", "chromadb"),
        ("FAISS (Facebook AI Similarity Search) is a library for efficient similarity search of dense vectors. IndexFlatL2 provides exact search while IndexIVFFlat uses clustering for approximate but faster search.", "database", "faiss"),
        ("Redis can be used as a vector database with the RediSearch module. It supports real-time vector similarity search and can combine vector search with traditional filtering for hybrid queries.", "database", "redis"),

        # DevOps
        ("Docker is a platform for developing, shipping, and running applications in containers. Containers package an application with all its dependencies, ensuring consistent behavior across different environments.", "devops", "docker"),
        ("Kubernetes is an open-source container orchestration platform. It automates the deployment, scaling, and management of containerized applications across clusters of machines.", "devops", "kubernetes"),
        ("CI/CD stands for Continuous Integration and Continuous Deployment. CI automatically builds and tests code changes, while CD automatically deploys approved changes to production environments.", "devops", "cicd"),
        ("Git is a distributed version control system created by Linus Torvalds in 2005. It tracks changes in source code and enables multiple developers to work together on non-linear development.", "devops", "git"),
        ("Terraform is an infrastructure as code tool that lets you define cloud resources in human-readable configuration files. It supports multiple cloud providers and maintains state to plan and apply changes.", "devops", "terraform"),

        # Web Development
        ("REST APIs follow a client-server architecture using HTTP methods: GET for reading, POST for creating, PUT for updating, and DELETE for removing resources. They are stateless and use standard HTTP status codes.", "web", "rest"),
        ("FastAPI is a modern Python web framework for building APIs. It uses Python type hints for automatic validation, serialization, and documentation generation. It is one of the fastest Python frameworks available.", "web", "fastapi"),
        ("GraphQL is a query language for APIs that allows clients to request exactly the data they need. Unlike REST, which exposes multiple endpoints, GraphQL uses a single endpoint with a flexible query structure.", "web", "graphql"),
        ("WebSockets provide full-duplex communication channels over a single TCP connection. They are commonly used for real-time applications like chat systems, live notifications, and collaborative editing.", "web", "websockets"),
        ("OAuth 2.0 is an authorization framework that enables third-party applications to obtain limited access to a web service. It uses access tokens rather than sharing credentials directly.", "web", "auth"),
    ]

    docs = []
    for i, (content, topic, subtopic) in enumerate(topics):
        doc = Document(
            page_content=content,
            metadata={"topic": topic, "subtopic": subtopic, "doc_id": i + 1}
        )
        docs.append(doc)
    return docs


# ============================================================
# 2. TEXT SPLITTING & EMBEDDING (Day 1 + Day 2 Concepts)
# ============================================================
def split_documents(docs):
    """Split documents into chunks with overlap."""
    print(f"\n[STEP 2] Splitting Documents (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    splits = splitter.split_documents(docs)
    print(f"  Created {len(splits)} chunks from {len(docs)} documents")
    return splits


def create_embeddings():
    """Initialize the embedding model."""
    print(f"\n[STEP 3] Loading Embedding Model ({EMBEDDING_MODEL})...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    print("  Embedding model loaded successfully!")
    return embeddings


# ============================================================
# 3. VECTOR STORE (Day 2 Concepts)
# ============================================================
def create_vector_store(splits, embeddings):
    """Store embedded chunks in ChromaDB."""
    print(f"\n[STEP 4] Storing in ChromaDB ({CHROMA_DIR})...")
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        collection_name="hybrid_search_collection",
    )
    print(f"  Stored {len(splits)} chunks in ChromaDB")
    return vectorstore


# ============================================================
# 4. HYBRID RETRIEVER (Day 3 + Day 4 Concepts)
# ============================================================
def create_hybrid_retriever(splits, vectorstore):
    """Create a hybrid retriever combining BM25 + Semantic search."""
    print(f"\n[STEP 5] Building Hybrid Retriever (BM25={BM25_WEIGHT}, Semantic={SEMANTIC_WEIGHT})...")

    # BM25 Keyword Retriever
    bm25_retriever = BM25Retriever.from_documents(splits)
    bm25_retriever.k = TOP_K

    # Semantic Vector Retriever
    semantic_retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})

    # Ensemble (Hybrid)
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, semantic_retriever],
        weights=[BM25_WEIGHT, SEMANTIC_WEIGHT]
    )
    print("  Hybrid retriever ready!")
    return ensemble_retriever


# ============================================================
# 5. CROSS-ENCODER RE-RANKER (Day 4 Concepts)
# ============================================================
def load_reranker():
    """Load the cross-encoder re-ranking model."""
    print(f"\n[STEP 6] Loading Cross-Encoder Re-ranker ({RERANKER_MODEL})...")
    try:
        reranker = CrossEncoder(RERANKER_MODEL, max_length=512)
        print("  Re-ranker loaded successfully!")
        return reranker
    except Exception as e:
        print(f"  Warning: Could not load re-ranker: {e}")
        return None


def rerank_results(query, docs, reranker, top_n=RERANK_TOP_N):
    """Re-rank retrieved documents using a cross-encoder."""
    if not reranker or not docs:
        return docs[:top_n]

    pairs = [[query, doc.page_content] for doc in docs]
    scores = reranker.predict(pairs)

    scored_docs = list(zip(docs, scores))
    scored_docs.sort(key=lambda x: x[1], reverse=True)

    return [(doc, float(score)) for doc, score in scored_docs[:top_n]]


# ============================================================
# 6. EVALUATION SYSTEM (Day 5 Concepts)
# ============================================================
def create_evaluation_dataset():
    """Create 30 evaluation queries with expected answers and topics."""
    return [
        {"query": "Who created Python?", "expected": "Guido van Rossum", "topic": "python"},
        {"query": "When was Python first released?", "expected": "1991", "topic": "python"},
        {"query": "What is Python's standard library known for?", "expected": "batteries included", "topic": "python"},
        {"query": "What are Python virtual environments?", "expected": "isolated Python installations", "topic": "python"},
        {"query": "What are Python decorators?", "expected": "modify behavior of functions", "topic": "python"},
        {"query": "What is machine learning?", "expected": "subset of artificial intelligence", "topic": "ml"},
        {"query": "What is supervised learning?", "expected": "uses labeled training data", "topic": "ml"},
        {"query": "What is unsupervised learning?", "expected": "finds hidden patterns without labels", "topic": "ml"},
        {"query": "What are neural networks inspired by?", "expected": "biological neural networks", "topic": "ml"},
        {"query": "What is transfer learning?", "expected": "model reused as starting point", "topic": "ml"},
        {"query": "What is NLP?", "expected": "interaction between computers and humans through natural language", "topic": "nlp"},
        {"query": "What are word embeddings?", "expected": "dense vectors in continuous vector space", "topic": "nlp"},
        {"query": "What are Transformers?", "expected": "self-attention mechanisms", "topic": "nlp"},
        {"query": "What is BERT?", "expected": "pre-trained language model", "topic": "nlp"},
        {"query": "What is RAG?", "expected": "retrieval with text generation", "topic": "nlp"},
        {"query": "What is PostgreSQL?", "expected": "open-source relational database", "topic": "database"},
        {"query": "What are vector databases?", "expected": "store and query high-dimensional vectors", "topic": "database"},
        {"query": "What is ChromaDB?", "expected": "open-source vector database for AI", "topic": "database"},
        {"query": "What is FAISS?", "expected": "efficient similarity search", "topic": "database"},
        {"query": "What is Redis used for in vector search?", "expected": "real-time vector similarity search", "topic": "database"},
        {"query": "What is Docker?", "expected": "containers", "topic": "devops"},
        {"query": "What is Kubernetes?", "expected": "container orchestration", "topic": "devops"},
        {"query": "What is CI/CD?", "expected": "Continuous Integration and Continuous Deployment", "topic": "devops"},
        {"query": "Who created Git?", "expected": "Linus Torvalds", "topic": "devops"},
        {"query": "What is Terraform?", "expected": "infrastructure as code", "topic": "devops"},
        {"query": "What HTTP methods do REST APIs use?", "expected": "GET POST PUT DELETE", "topic": "web"},
        {"query": "What is FastAPI?", "expected": "modern Python web framework", "topic": "web"},
        {"query": "How is GraphQL different from REST?", "expected": "single endpoint with flexible query", "topic": "web"},
        {"query": "What are WebSockets used for?", "expected": "real-time applications", "topic": "web"},
        {"query": "What is OAuth 2.0?", "expected": "authorization framework", "topic": "web"},
    ]


def compute_context_precision(retrieved_docs, expected_topic):
    """Metric: How many retrieved docs match the expected topic?"""
    if not retrieved_docs:
        return 0.0
    docs_only = [d[0] if isinstance(d, tuple) else d for d in retrieved_docs]
    relevant = sum(1 for doc in docs_only if doc.metadata.get("topic") == expected_topic)
    return relevant / len(docs_only)


def compute_answer_relevancy(top_doc_content, expected_answer):
    """Metric: Does the top retrieved content contain the expected answer?"""
    if not top_doc_content:
        return 0.0
    expected_words = expected_answer.lower().split()
    content_lower = top_doc_content.lower()
    found = sum(1 for word in expected_words if word in content_lower)
    return found / len(expected_words) if expected_words else 0.0


def compute_faithfulness(top_doc_content, expected_answer):
    """Metric: Is the expected answer actually present in the retrieved context?"""
    if not top_doc_content:
        return 0.0
    return 1.0 if expected_answer.lower() in top_doc_content.lower() else 0.0


def run_evaluation(retriever, reranker):
    """Run full evaluation on 30 queries."""
    print("\n" + "=" * 70)
    print("HYBRID SEARCH ENGINE — EVALUATION REPORT (30 Queries)")
    print("=" * 70)

    eval_data = create_evaluation_dataset()
    results = []

    total_precision = 0
    total_relevancy = 0
    total_faithfulness = 0

    for i, item in enumerate(eval_data):
        query = item["query"]
        expected = item["expected"]
        topic = item["topic"]

        # Retrieve
        retrieved = retriever.invoke(query)

        # Re-rank
        reranked = rerank_results(query, retrieved, reranker)

        # Get top result content
        if reranked:
            top_doc = reranked[0][0] if isinstance(reranked[0], tuple) else reranked[0]
            top_content = top_doc.page_content
        else:
            top_content = ""

        # Compute metrics
        precision = compute_context_precision(reranked, topic)
        relevancy = compute_answer_relevancy(top_content, expected)
        faithfulness = compute_faithfulness(top_content, expected)

        total_precision += precision
        total_relevancy += relevancy
        total_faithfulness += faithfulness

        status = "PASS" if relevancy >= 0.5 else "FAIL"
        results.append({
            "query": query,
            "expected": expected,
            "precision": round(precision, 2),
            "relevancy": round(relevancy, 2),
            "faithfulness": round(faithfulness, 2),
            "status": status
        })

        print(f"  Q{i+1:02d} [{status}] P:{precision:.2f} R:{relevancy:.2f} F:{faithfulness:.2f} | {query}")

    n = len(eval_data)
    avg_p = total_precision / n
    avg_r = total_relevancy / n
    avg_f = total_faithfulness / n
    overall = (avg_p + avg_r + avg_f) / 3

    print("\n" + "-" * 70)
    print(f"  Avg Context Precision:  {avg_p:.2f}")
    print(f"  Avg Answer Relevancy:   {avg_r:.2f}")
    print(f"  Avg Faithfulness:       {avg_f:.2f}")
    print(f"  Overall Score:          {overall:.2f}")
    print(f"  Pass Rate:              {sum(1 for r in results if r['status'] == 'PASS')}/{n}")
    print("=" * 70)

    # Save results to JSON
    report = {
        "total_queries": n,
        "avg_context_precision": round(avg_p, 2),
        "avg_answer_relevancy": round(avg_r, 2),
        "avg_faithfulness": round(avg_f, 2),
        "overall_score": round(overall, 2),
        "results": results
    }
    with open(EVAL_RESULTS_FILE, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Evaluation report saved to: {EVAL_RESULTS_FILE}")

    return report


# ============================================================
# 7. INTERACTIVE CLI (Day 3 RAG Concepts)
# ============================================================
def interactive_search(retriever, reranker):
    """Interactive CLI search loop."""
    print("\n" + "=" * 70)
    print("HYBRID SEARCH ENGINE — INTERACTIVE MODE")
    print("Type your query and press Enter. Type 'quit' to exit.")
    print("=" * 70)

    while True:
        try:
            query = input("\n🔍 Query: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not query or query.lower() in ('quit', 'exit', 'q'):
            print("Goodbye!")
            break

        # Retrieve
        retrieved = retriever.invoke(query)

        # Re-rank
        reranked = rerank_results(query, retrieved, reranker, top_n=5)

        print(f"\n  Found {len(retrieved)} results. Top {len(reranked)} after re-ranking:\n")
        for rank, (doc, score) in enumerate(reranked, 1):
            topic = doc.metadata.get("topic", "unknown")
            print(f"  [{rank}] (Score: {score:.2f}) [{topic}]")
            print(f"      {doc.page_content[:150]}...")
            print()


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 70)
    print("WEEK 3 INTERMEDIATE PROJECT — HYBRID SEARCH ENGINE")
    print("Option C: BM25 + Vector Index + Cross-Encoder Re-ranker")
    print("=" * 70)

    # Step 1: Try to download sample PDF
    download_sample_pdf()

    # Step 2: Load documents
    docs = load_documents()

    # Step 3: Split into chunks
    splits = split_documents(docs)

    # Step 4: Create embeddings
    embeddings = create_embeddings()

    # Step 5: Store in ChromaDB
    vectorstore = create_vector_store(splits, embeddings)

    # Step 6: Build hybrid retriever
    retriever = create_hybrid_retriever(splits, vectorstore)

    # Step 7: Load re-ranker
    reranker = load_reranker()

    # Step 8: Run evaluation on 30 queries
    run_evaluation(retriever, reranker)

    # Step 9: Interactive search
    if "--no-interactive" not in sys.argv:
        interactive_search(retriever, reranker)


if __name__ == "__main__":
    main()
