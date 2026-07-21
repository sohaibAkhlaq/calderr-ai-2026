"""
Week 4 - Day 1: Lab 4.1 - Document Processing Graph
Build a LangGraph workflow: load → validate → chunk → embed → confirm
With conditional edge: if doc too large, split into parts first
"""

import os
from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pprint

# ─── State Schema ───

class DocumentState(TypedDict):
    """State for document processing graph."""
    
    # Input
    document: str
    filename: str
    
    # Processing
    chunks: List[str]
    embeddings: List[List[float]]
    
    # Control
    is_valid: bool
    is_large: bool
    processed: bool
    chunk_count: int
    
    # Messages (for logging)
    messages: Annotated[List[dict], add_messages]

# ─── Node Functions ───

def load_document(state: DocumentState) -> dict:
    """
    Node 1: Load the document.
    Simulates loading from file.
    """
    print("\n📄 [LOAD] Loading document...")
    
    # Simulate loading
    filename = state.get("filename", "unknown.txt")
    
    # Sample document content (if not provided)
    if "document" not in state or not state["document"]:
        state["document"] = """
        LangGraph is a library for building stateful, multi-agent applications 
        using graph-based orchestration. It extends the concept of chains to 
        graph-based workflows where nodes represent steps and edges represent 
        the flow of control. LangGraph supports conditional routing, loops, 
        and human-in-the-loop patterns.
        
        The StateGraph class is the main entry point. You define nodes (functions) 
        and edges (connections). Each node receives the current state and returns 
        updates. The state is a TypedDict that defines the schema of data flowing 
        through the graph.
        
        Conditional edges allow branching based on the state. This enables 
        decision-making within the graph. For example, you can route to different 
        nodes based on the quality of intermediate results.
        
        LangGraph also supports persistence through checkpointers. This allows 
        the graph to pause and resume, enabling human-in-the-loop workflows 
        where a human reviews and approves actions.
        """
    
    return {
        "document": state["document"],
        "is_valid": True,
        "messages": [{"role": "system", "content": f"Loaded document: {filename}"}]
    }

def validate_document(state: DocumentState) -> dict:
    """
    Node 2: Validate the document.
    Check if document exists and has content.
    """
    print("\n✅ [VALIDATE] Validating document...")
    
    doc = state.get("document", "")
    is_valid = len(doc.strip()) > 50
    
    if is_valid:
        print(f"  Document valid: {len(doc)} characters")
    else:
        print(f"  Document too short: {len(doc)} characters")
    
    # Check if document is large (> 2000 chars)
    is_large = len(doc) > 2000
    
    return {
        "is_valid": is_valid,
        "is_large": is_large,
        "messages": [{"role": "system", "content": f"Validation: valid={is_valid}, large={is_large}"}]
    }

def split_document(state: DocumentState) -> dict:
    """
    Node 3: Split large document into parts.
    Only executed if document is large.
    """
    print("\n✂️ [SPLIT] Splitting large document...")
    
    doc = state["document"]
    parts = []
    
    # Split by double newlines into paragraphs
    paragraphs = doc.split("\n\n")
    
    # Group paragraphs into parts (max 2 paragraphs per part)
    part_size = 2
    for i in range(0, len(paragraphs), part_size):
        part = "\n\n".join(paragraphs[i:i+part_size])
        parts.append(part)
    
    print(f"  Split into {len(parts)} parts")
    
    return {
        "document": doc,
        "messages": [{"role": "system", "content": f"Split document into {len(parts)} parts"}]
    }

def chunk_document(state: DocumentState) -> dict:
    """
    Node 4: Chunk the document.
    Split into smaller chunks for embedding.
    """
    print("\n📦 [CHUNK] Chunking document...")
    
    doc = state["document"]
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = splitter.split_text(doc)
    
    print(f"  Created {len(chunks)} chunks")
    
    return {
        "chunks": chunks,
        "chunk_count": len(chunks),
        "messages": [{"role": "system", "content": f"Created {len(chunks)} chunks"}]
    }

def embed_chunks(state: DocumentState) -> dict:
    """
    Node 5: Embed the chunks.
    Convert chunks to vectors using embedding model.
    """
    print("\n🧠 [EMBED] Embedding chunks...")
    
    chunks = state.get("chunks", [])
    
    if not chunks:
        print("  No chunks to embed")
        return {}
    
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        
        embedding_vectors = embeddings.embed_documents(chunks)
        
        print(f"  Embedded {len(embedding_vectors)} chunks")
        print(f"  Vector dimension: {len(embedding_vectors[0]) if embedding_vectors else 0}")
        
        return {
            "embeddings": embedding_vectors,
            "messages": [{"role": "system", "content": f"Embedded {len(embedding_vectors)} chunks"}]
        }
    except Exception as e:
        print(f"  Embedding failed: {e}")
        return {
            "messages": [{"role": "system", "content": f"Embedding failed: {e}"}]
        }

def confirm_processing(state: DocumentState) -> dict:
    """
    Node 6: Confirm processing complete.
    Final node that displays results.
    """
    print("\n✅ [CONFIRM] Processing complete!")
    print("=" * 60)
    print("📊 PROCESSING SUMMARY")
    print("=" * 60)
    print(f"  Document length: {len(state.get('document', ''))} characters")
    print(f"  Chunks created: {state.get('chunk_count', 0)}")
    print(f"  Embeddings created: {len(state.get('embeddings', []))}")
    
    if state.get('embeddings'):
        vec_dim = len(state['embeddings'][0])
        print(f"  Vector dimension: {vec_dim}")
    
    print("=" * 60)
    
    return {
        "processed": True,
        "messages": [{"role": "system", "content": "Processing complete"}]
    }

# ─── Router Function (Conditional Edge) ───

def route_after_validate(state: DocumentState) -> str:
    """
    Conditional routing function.
    Decides whether to split or proceed to chunking.
    """
    if state.get("is_large", False):
        print("\n🔀 [ROUTING] Document is large → Splitting first")
        return "split"
    else:
        print("\n🔀 [ROUTING] Document is normal → Chunking directly")
        return "chunk"

# ─── Build the Graph ───

def build_document_processing_graph():
    """Build the document processing graph."""
    
    print("=" * 60)
    print("🏗️ BUILDING DOCUMENT PROCESSING GRAPH")
    print("=" * 60)
    
    # 1. Create StateGraph
    builder = StateGraph(DocumentState)
    
    # 2. Add nodes
    builder.add_node("load", load_document)
    builder.add_node("validate", validate_document)
    builder.add_node("split", split_document)
    builder.add_node("chunk", chunk_document)
    builder.add_node("embed", embed_chunks)
    builder.add_node("confirm", confirm_processing)
    
    # 3. Add entry point
    builder.set_entry_point("load")
    
    # 4. Add regular edges
    builder.add_edge("load", "validate")
    
    # 5. Add conditional edge (the key part!)
    builder.add_conditional_edges(
        "validate",
        route_after_validate,
        {
            "split": "split",
            "chunk": "chunk"
        }
    )
    
    # 6. Continue from split to chunk
    builder.add_edge("split", "chunk")
    
    # 7. Add remaining edges
    builder.add_edge("chunk", "embed")
    builder.add_edge("embed", "confirm")
    builder.add_edge("confirm", END)
    
    # 8. Compile the graph
    graph = builder.compile()
    
    print("\n✅ Graph compiled successfully!")
    print("   Nodes: load → validate → [split → chunk] → embed → confirm")
    print("   Conditional: if large → split first, else → chunk directly")
    
    return graph

# ─── Run the Graph ───

def run_document_processing():
    """Run the document processing graph."""
    
    print("\n" + "=" * 60)
    print("🚀 RUNNING DOCUMENT PROCESSING GRAPH")
    print("=" * 60)
    
    # Build graph
    graph = build_document_processing_graph()
    
    # Initial state
    initial_state = {
        "filename": "langgraph_intro.txt",
        "document": "",  # Will be loaded from sample
        "chunks": [],
        "embeddings": [],
        "is_valid": False,
        "is_large": False,
        "processed": False,
        "chunk_count": 0,
        "messages": []
    }
    
    # Run the graph
    print("\n📝 Running with sample document...")
    final_state = graph.invoke(initial_state)
    
    print("\n" + "=" * 60)
    print("📋 FINAL STATE")
    print("=" * 60)
    
    # Show summary
    print(f"✓ Document loaded: {final_state.get('is_valid', False)}")
    print(f"✓ Chunks: {final_state.get('chunk_count', 0)}")
    print(f"✓ Embeddings: {len(final_state.get('embeddings', []))}")
    print(f"✓ Processed: {final_state.get('processed', False)}")
    
    # Show messages
    print("\n📨 LOG MESSAGES:")
    for msg in final_state.get("messages", []):
        if isinstance(msg, dict):
            print(f"  [{msg.get('role', 'system')}] {msg.get('content', '')}")
        else:
            print(f"  [{getattr(msg, 'type', 'system')}] {getattr(msg, 'content', '')}")

# ─── Main ───

def main():
    """Main entry point."""
    run_document_processing()

if __name__ == "__main__":
    main()
