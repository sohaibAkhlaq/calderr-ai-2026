"""
Week 4 - Day 1: Lab 4.1 - Document Processing Graph

Builds a LangGraph workflow that loads a real PDF research paper,
validates it, chunks it, embeds it, and confirms processing.
Uses a conditional edge: if the document exceeds the size threshold,
it is split before chunking.

Usage:
    python "Week 4/lab4.1_document_processing.py"
"""

import os
import sys
import urllib.request
import ssl
from typing import TypedDict, List, Annotated

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PDF_URL = "https://arxiv.org/pdf/1706.03762.pdf"
PDF_PATH = os.path.join(os.path.dirname(__file__), "docs", "attention_is_all_you_need.pdf")
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64
LARGE_DOC_THRESHOLD = 5000


# ---------------------------------------------------------------------------
# State Schema
# ---------------------------------------------------------------------------

class DocumentState(TypedDict):
    """State schema for the document processing graph."""

    # Input
    document: str
    filename: str
    source: str

    # Processing
    chunks: List[str]
    embeddings: List[List[float]]

    # Control flags
    is_valid: bool
    is_large: bool
    processed: bool
    chunk_count: int

    # Audit trail
    messages: Annotated[List, add_messages]


# ---------------------------------------------------------------------------
# Utility: download PDF
# ---------------------------------------------------------------------------

def _ensure_pdf_downloaded() -> str:
    """Download the reference PDF if it does not already exist locally."""
    os.makedirs(os.path.dirname(PDF_PATH), exist_ok=True)
    if os.path.exists(PDF_PATH):
        return PDF_PATH

    ssl._create_default_https_context = ssl._create_unverified_context
    print(f"[DOWNLOAD] Fetching PDF from {PDF_URL} ...")
    try:
        urllib.request.urlretrieve(PDF_URL, PDF_PATH)
        print(f"[DOWNLOAD] Saved to {PDF_PATH} ({os.path.getsize(PDF_PATH)} bytes)")
    except Exception as exc:
        raise RuntimeError(f"Failed to download PDF: {exc}") from exc
    return PDF_PATH


def _extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from a PDF file using PyPDFLoader."""
    print(f"[EXTRACT] Loading PDF from {pdf_path} ...")
    try:
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
    except ImportError:
        raise RuntimeError(
            "Missing 'pypdf' package. Install it with: pip install pypdf"
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to load PDF: {exc}") from exc

    if not pages:
        raise RuntimeError("PDF loaded but contains zero pages.")

    text = "\n\n".join(page.page_content for page in pages)
    print(f"[EXTRACT] Extracted {len(text)} characters from {len(pages)} pages")
    return text


# ---------------------------------------------------------------------------
# Graph Node Functions
# ---------------------------------------------------------------------------

def load_document(state: DocumentState) -> dict:
    """Node 1: Load the real PDF document and extract its text content."""
    pdf_path = _ensure_pdf_downloaded()
    text = _extract_text_from_pdf(pdf_path)

    return {
        "document": text,
        "filename": os.path.basename(pdf_path),
        "source": pdf_path,
        "is_valid": True,
        "messages": [
            SystemMessage(content=f"Loaded document: {os.path.basename(pdf_path)}")
        ],
    }


def validate_document(state: DocumentState) -> dict:
    """Node 2: Validate that the document has sufficient content."""
    doc = state.get("document", "")
    is_valid = len(doc.strip()) > 100
    is_large = len(doc) > LARGE_DOC_THRESHOLD

    print(f"[VALIDATE] Document length: {len(doc)} characters")
    print(f"[VALIDATE] Valid: {is_valid} | Large (>{LARGE_DOC_THRESHOLD}): {is_large}")

    return {
        "is_valid": is_valid,
        "is_large": is_large,
        "messages": [
            SystemMessage(
                content=(
                    f"Validation: valid={is_valid}, "
                    f"large={is_large}, "
                    f"length={len(doc)}"
                )
            )
        ],
    }


def split_document(state: DocumentState) -> dict:
    """Node 3: Split a large document into sections before chunking."""
    doc = state["document"]

    sections = doc.split("\n\n")
    section_size = max(1, len(sections) // 5)
    parts = []
    for i in range(0, len(sections), section_size):
        part = "\n\n".join(sections[i:i + section_size])
        parts.append(part)

    combined = "\n\n---SECTION BREAK---\n\n".join(parts)
    print(f"[SPLIT] Document split into {len(parts)} logical sections")

    return {
        "document": combined,
        "messages": [
            SystemMessage(content=f"Split document into {len(parts)} sections")
        ],
    }


def chunk_document(state: DocumentState) -> dict:
    """Node 4: Split the document into smaller chunks for embedding."""
    doc = state["document"]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n---SECTION BREAK---\n\n", "\n\n", "\n", ". ", " "],
    )

    chunks = splitter.split_text(doc)
    print(f"[CHUNK] Created {len(chunks)} chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")

    return {
        "chunks": chunks,
        "chunk_count": len(chunks),
        "messages": [
            SystemMessage(content=f"Chunked into {len(chunks)} pieces")
        ],
    }


def embed_chunks(state: DocumentState) -> dict:
    """Node 5: Convert text chunks into dense vector embeddings."""
    chunks = state.get("chunks", [])
    if not chunks:
        print("[EMBED] No chunks to embed")
        return {
            "messages": [SystemMessage(content="Embedding skipped: no chunks")]
        }

    try:
        embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectors = embedder.embed_documents(chunks)
        print(f"[EMBED] Generated {len(vectors)} embeddings")
        if vectors:
            print(f"[EMBED] Vector dimension: {len(vectors[0])}")
    except Exception as exc:
        print(f"[EMBED] Failed: {exc}")
        return {
            "messages": [SystemMessage(content=f"Embedding failed: {exc}")]
        }

    return {
        "embeddings": vectors,
        "messages": [
            SystemMessage(content=f"Embedded {len(vectors)} chunks")
        ],
    }


def confirm_processing(state: DocumentState) -> dict:
    """Node 6: Display a final summary of the processing pipeline."""
    doc_len = len(state.get("document", ""))
    n_chunks = state.get("chunk_count", 0)
    n_embeddings = len(state.get("embeddings", []))
    vec_dim = len(state["embeddings"][0]) if state.get("embeddings") else 0

    print("=" * 70)
    print("PROCESSING SUMMARY")
    print("=" * 70)
    print(f"  Document length:     {doc_len} characters")
    print(f"  Chunks created:      {n_chunks}")
    print(f"  Embeddings created:  {n_embeddings}")
    print(f"  Vector dimension:    {vec_dim}")
    print(f"  Document source:     {state.get('source', 'N/A')}")
    print("=" * 70)

    return {
        "processed": True,
        "messages": [SystemMessage(content="Processing complete")],
    }


# ---------------------------------------------------------------------------
# Router (Conditional Edge)
# ---------------------------------------------------------------------------

def route_after_validate(state: DocumentState) -> str:
    """Decide whether to split the document first or proceed directly to chunking."""
    if state.get("is_large", False):
        print("[ROUTE] Document exceeds threshold -> routing to split")
        return "split"
    print("[ROUTE] Document within threshold -> routing to chunk")
    return "chunk"


# ---------------------------------------------------------------------------
# Graph Builder
# ---------------------------------------------------------------------------

def build_document_processing_graph() -> StateGraph:
    """Construct the LangGraph document processing pipeline."""
    print("=" * 70)
    print("BUILDING DOCUMENT PROCESSING GRAPH")
    print("=" * 70)

    builder = StateGraph(DocumentState)

    # Register nodes
    builder.add_node("load", load_document)
    builder.add_node("validate", validate_document)
    builder.add_node("split", split_document)
    builder.add_node("chunk", chunk_document)
    builder.add_node("embed", embed_chunks)
    builder.add_node("confirm", confirm_processing)

    # Define edges
    builder.set_entry_point("load")
    builder.add_edge("load", "validate")

    builder.add_conditional_edges(
        "validate",
        route_after_validate,
        {"split": "split", "chunk": "chunk"},
    )

    builder.add_edge("split", "chunk")
    builder.add_edge("chunk", "embed")
    builder.add_edge("embed", "confirm")
    builder.add_edge("confirm", END)

    graph = builder.compile()

    print("[BUILD] Graph compiled successfully")
    print("[BUILD] Pipeline: load -> validate -> [split|chunk] -> embed -> confirm")
    return graph


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def run_document_processing() -> None:
    """Execute the document processing graph end-to-end."""
    print("=" * 70)
    print("RUNNING DOCUMENT PROCESSING GRAPH")
    print("=" * 70)

    graph = build_document_processing_graph()

    initial_state: DocumentState = {
        "document": "",
        "filename": "",
        "source": "",
        "chunks": [],
        "embeddings": [],
        "is_valid": False,
        "is_large": False,
        "processed": False,
        "chunk_count": 0,
        "messages": [],
    }

    print("\nInvoking graph with real PDF document ...\n")
    final_state = graph.invoke(initial_state)

    print("\n" + "=" * 70)
    print("FINAL STATE")
    print("=" * 70)
    print(f"  Valid:       {final_state.get('is_valid', False)}")
    print(f"  Chunks:      {final_state.get('chunk_count', 0)}")
    print(f"  Embeddings:  {len(final_state.get('embeddings', []))}")
    print(f"  Processed:   {final_state.get('processed', False)}")

    print("\nAudit log:")
    for msg in final_state.get("messages", []):
        role = getattr(msg, "type", "system")
        content = getattr(msg, "content", "")
        print(f"  [{role}] {content}")

    print("\n[SUCCESS] Document processing graph completed.\n")


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

def main() -> None:
    """Main entry point for the lab."""
    run_document_processing()


if __name__ == "__main__":
    main()
