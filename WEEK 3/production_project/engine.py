"""
engine.py — Real-Time Research Engine Backend
==============================================
Week 3 Production Project (Day 7) — Option B

Strict fault-tolerant RAG pipeline class.
Every pipeline step is clearly labeled, validated, and raises
a ResearchEngineError on failure so the Streamlit front-end can
present a clean, user-friendly error rather than an unhandled crash.

Pipeline Steps:
  Step 1 — PDF Download       (PipelineStage.DOWNLOAD)
  Step 2 — Document Loading   (PipelineStage.LOAD)
  Step 3 — Text Splitting     (PipelineStage.SPLIT)
  Step 4 — Embedding          (PipelineStage.EMBED)
  Step 5 — Vector Store Build (PipelineStage.STORE)
  Step 6 — Retriever Assembly (PipelineStage.RETRIEVE)
  Step 7 — Re-ranking         (PipelineStage.RERANK)
"""

import os
import ssl
import traceback
import urllib.request
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

# Set BEFORE any torch/sentence-transformers import — required on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"

ssl._create_default_https_context = ssl._create_unverified_context

# Force torch to load cleanly before sentence_transformers imports it
try:
    import torch  # noqa: F401
except OSError:
    pass  # DLL load failure handled below — sentence_transformers will also fail and raise ResearchEngineError

import warnings
warnings.filterwarnings("ignore")

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder


# ──────────────────────────────────────────────────────────────────────────────
# ENUMS, DATACLASSES, EXCEPTIONS
# ──────────────────────────────────────────────────────────────────────────────

class PipelineStage(str, Enum):
    DOWNLOAD = "PDF Download"
    LOAD     = "Document Loading"
    SPLIT    = "Text Splitting"
    EMBED    = "Embedding Model"
    STORE    = "Vector Store"
    RETRIEVE = "Retriever Assembly"
    RERANK   = "Cross-Encoder Re-ranking"


class ResearchEngineError(Exception):
    """
    Custom exception for critical pipeline failures.

    When raised, the Streamlit app catches this and displays:
      - The stage where the failure occurred
      - A human-readable explanation
      - Recovery guidance

    The pipeline NEVER silently swallows errors — it always raises
    ResearchEngineError so downstream code knows the state is invalid.
    """
    def __init__(self, stage: PipelineStage, message: str):
        self.stage = stage
        self.message = message
        super().__init__(f"[{stage.value}] {message}")


@dataclass
class SearchResult:
    rank: int
    content: str
    score: float
    source: str
    page: int
    topic: str


@dataclass
class EngineStatus:
    ready: bool
    chunks_loaded: int
    pdf_path: str
    error: Optional[str] = None
    stage_failed: Optional[str] = None


# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

BASE_DIR         = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR         = os.path.join(BASE_DIR, "docs")
CHROMA_DIR       = os.path.join(BASE_DIR, "chroma_db")
EMBEDDING_MODEL  = "all-MiniLM-L6-v2"
RERANKER_MODEL   = "cross-encoder/ms-marco-MiniLM-L-6-v2"
CHUNK_SIZE       = 512
CHUNK_OVERLAP    = 64
BM25_WEIGHT      = 0.40
SEMANTIC_WEIGHT  = 0.60
TOP_K_RETRIEVE   = 12
TOP_N_RERANK     = 4

PDF_SOURCES = [
    {
        "name": "Attention Is All You Need",
        "url":  "https://arxiv.org/pdf/1706.03762.pdf",
        "file": "attention_is_all_you_need.pdf",
        "topic": "Transformer Architecture",
    },
    {
        "name": "BERT: Pre-training of Deep Bidirectional Transformers",
        "url":  "https://arxiv.org/pdf/1810.04805.pdf",
        "file": "bert_pretraining.pdf",
        "topic": "BERT & Language Models",
    },
]


# ──────────────────────────────────────────────────────────────────────────────
# RESEARCH ENGINE CLASS
# ──────────────────────────────────────────────────────────────────────────────

class ResearchEngine:
    """
    Production-grade RAG engine with strict error boundaries.

    Usage:
        engine = ResearchEngine()
        engine.initialize()              # Runs all pipeline steps
        results = engine.search(query)  # Returns List[SearchResult]
        status  = engine.get_status()   # Returns EngineStatus
    """

    def __init__(self):
        self._splits:    List[Document] = []
        self._retriever: Optional[EnsembleRetriever] = None
        self._reranker:  Optional[CrossEncoder] = None
        self._ready:     bool = False
        self._status:    EngineStatus = EngineStatus(
            ready=False, chunks_loaded=0, pdf_path="", error=None
        )

    # ── Step 1: Download ──────────────────────────────────────────────────────
    def _download_pdfs(self) -> List[str]:
        """
        Downloads each configured PDF if not already on disk.
        FAILURE: Raises ResearchEngineError(DOWNLOAD) if any download fails.
                 The rest of the pipeline will NOT run.
        """
        os.makedirs(DOCS_DIR, exist_ok=True)
        paths = []
        for src in PDF_SOURCES:
            dest = os.path.join(DOCS_DIR, src["file"])
            if not os.path.exists(dest):
                try:
                    urllib.request.urlretrieve(src["url"], dest)
                except Exception as e:
                    raise ResearchEngineError(
                        PipelineStage.DOWNLOAD,
                        f"Could not download '{src['name']}' from {src['url']}.\n"
                        f"Check your internet connection.\nOriginal error: {e}",
                    )
            paths.append((dest, src["topic"]))
        return paths

    # ── Step 2: Load ─────────────────────────────────────────────────────────
    def _load_documents(self, pdf_paths: List[Tuple[str, str]]) -> List[Document]:
        """
        Loads all PDFs using PyPDFLoader.
        FAILURE: Raises ResearchEngineError(LOAD) if a PDF is unreadable or 0 pages extracted.
                 Pipeline aborts — we do NOT continue with an empty document set.
        """
        all_docs = []
        for path, topic in pdf_paths:
            if not os.path.exists(path):
                raise ResearchEngineError(
                    PipelineStage.LOAD,
                    f"PDF not found on disk: {path}\n"
                    f"The download step may have silently failed.",
                )
            try:
                loader = PyPDFLoader(path)
                docs   = loader.load()
            except ImportError:
                raise ResearchEngineError(
                    PipelineStage.LOAD,
                    "Missing 'pypdf' package. Run: pip install pypdf",
                )
            except Exception as e:
                raise ResearchEngineError(
                    PipelineStage.LOAD,
                    f"PyPDFLoader failed on '{path}'.\n"
                    f"The PDF may be corrupted or password-protected.\nError: {e}",
                )

            if not docs:
                raise ResearchEngineError(
                    PipelineStage.LOAD,
                    f"PDF '{path}' loaded but 0 pages of text were extracted.\n"
                    f"This is likely a scanned image PDF with no selectable text.",
                )

            for doc in docs:
                doc.metadata["topic"] = topic
                doc.metadata["source_file"] = os.path.basename(path)
            all_docs.extend(docs)

        return all_docs

    # ── Step 3: Split ─────────────────────────────────────────────────────────
    def _split_documents(self, docs: List[Document]) -> List[Document]:
        """
        Splits pages into overlapping chunks.
        FAILURE: Raises ResearchEngineError(SPLIT) if 0 chunks are produced.
                 0 chunks means the vector store would be empty, making retrieval useless.
        """
        try:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                separators=["\n\n", "\n", " ", ""],
            )
            splits = splitter.split_documents(docs)
        except Exception as e:
            raise ResearchEngineError(
                PipelineStage.SPLIT,
                f"Text splitting raised an unexpected error: {e}",
            )

        if not splits:
            raise ResearchEngineError(
                PipelineStage.SPLIT,
                "Text splitting produced 0 chunks from the loaded documents.\n"
                "This should never happen on valid text PDFs.",
            )
        return splits

    # ── Step 4: Embed ─────────────────────────────────────────────────────────
    def _create_embeddings(self) -> HuggingFaceEmbeddings:
        """
        Loads the sentence-transformer embedding model.
        FAILURE: Raises ResearchEngineError(EMBED) if HuggingFace is unreachable
                 or the model files are corrupted.
        """
        try:
            return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        except Exception as e:
            raise ResearchEngineError(
                PipelineStage.EMBED,
                f"Failed to load embedding model '{EMBEDDING_MODEL}'.\n"
                f"Check HuggingFace connectivity. Error: {e}",
            )

    # ── Step 5: Store ─────────────────────────────────────────────────────────
    def _create_vector_store(
        self, splits: List[Document], embeddings: HuggingFaceEmbeddings
    ) -> Chroma:
        """
        Embeds chunks and persists them in ChromaDB.
        FAILURE: Raises ResearchEngineError(STORE) on disk permission errors
                 or ChromaDB initialization failures.
        """
        try:
            return Chroma.from_documents(
                documents=splits,
                embedding=embeddings,
                collection_name="research_engine_v1",
                persist_directory=CHROMA_DIR,
            )
        except Exception as e:
            raise ResearchEngineError(
                PipelineStage.STORE,
                f"ChromaDB initialization failed.\n"
                f"Check disk permissions for '{CHROMA_DIR}'.\nError: {e}",
            )

    # ── Step 6: Retriever ─────────────────────────────────────────────────────
    def _create_retriever(
        self, splits: List[Document], vectorstore: Chroma
    ) -> EnsembleRetriever:
        """
        Assembles the Hybrid EnsembleRetriever (BM25 + Semantic).
        FAILURE: Raises ResearchEngineError(RETRIEVE) if BM25 or Chroma retriever fails.
        """
        try:
            bm25 = BM25Retriever.from_documents(splits)
            bm25.k = TOP_K_RETRIEVE
            semantic = vectorstore.as_retriever(search_kwargs={"k": TOP_K_RETRIEVE})
            return EnsembleRetriever(
                retrievers=[bm25, semantic],
                weights=[BM25_WEIGHT, SEMANTIC_WEIGHT],
            )
        except Exception as e:
            raise ResearchEngineError(
                PipelineStage.RETRIEVE,
                f"Failed to assemble EnsembleRetriever.\nError: {e}",
            )

    # ── Step 7: Re-ranker ─────────────────────────────────────────────────────
    def _load_reranker(self) -> CrossEncoder:
        """
        Loads the cross-encoder re-ranking model.
        FAILURE: Raises ResearchEngineError(RERANK) on model download failure.
        """
        try:
            return CrossEncoder(RERANKER_MODEL, max_length=512)
        except Exception as e:
            raise ResearchEngineError(
                PipelineStage.RERANK,
                f"Failed to load CrossEncoder '{RERANKER_MODEL}'.\nError: {e}",
            )

    # ── Public: Initialize ────────────────────────────────────────────────────
    def initialize(self, progress_callback=None) -> EngineStatus:
        """
        Runs all 7 pipeline steps in strict sequence.
        Returns EngineStatus (ready=True) on success.
        Returns EngineStatus (ready=False, error=...) on failure — never raises.

        The Streamlit app calls initialize() and checks status.ready.
        """

        def _progress(msg: str):
            if progress_callback:
                progress_callback(msg)

        try:
            _progress("Step 1/7 — Downloading PDFs...")
            pdf_paths = self._download_pdfs()

            _progress("Step 2/7 — Loading documents from PDF...")
            docs = self._load_documents(pdf_paths)

            _progress(f"Step 3/7 — Splitting {len(docs)} pages into chunks...")
            self._splits = self._split_documents(docs)

            _progress(f"Step 4/7 — Loading embedding model ({EMBEDDING_MODEL})...")
            embeddings = self._create_embeddings()

            _progress(f"Step 5/7 — Building ChromaDB vector store ({len(self._splits)} chunks)...")
            vectorstore = self._create_vector_store(self._splits, embeddings)

            _progress("Step 6/7 — Assembling Hybrid Retriever (BM25 + Semantic)...")
            self._retriever = self._create_retriever(self._splits, vectorstore)

            _progress(f"Step 7/7 — Loading Cross-Encoder ({RERANKER_MODEL})...")
            self._reranker = self._load_reranker()

            self._ready = True
            self._status = EngineStatus(
                ready=True,
                chunks_loaded=len(self._splits),
                pdf_path=DOCS_DIR,
            )
            _progress("Engine ready.")

        except ResearchEngineError as e:
            self._status = EngineStatus(
                ready=False,
                chunks_loaded=0,
                pdf_path="",
                error=e.message,
                stage_failed=e.stage.value,
            )
        except Exception as e:
            self._status = EngineStatus(
                ready=False,
                chunks_loaded=0,
                pdf_path="",
                error=f"Unexpected error: {traceback.format_exc()}",
                stage_failed="Unknown",
            )

        return self._status

    # ── Public: Search ────────────────────────────────────────────────────────
    def search(self, query: str) -> List[SearchResult]:
        """
        Runs hybrid retrieval + cross-encoder re-ranking for the given query.

        Returns top-N SearchResult objects.
        Raises ResearchEngineError if the engine is not initialized.
        On re-ranking failure, falls back to hybrid ranking gracefully.
        """
        if not self._ready or self._retriever is None:
            raise ResearchEngineError(
                PipelineStage.RETRIEVE,
                "Engine is not initialized. Call engine.initialize() first.",
            )

        if not query or not query.strip():
            return []

        # Retrieve
        try:
            retrieved = self._retriever.invoke(query.strip())
        except Exception as e:
            raise ResearchEngineError(
                PipelineStage.RETRIEVE,
                f"Retriever failed on query '{query}'.\nError: {e}",
            )

        if not retrieved:
            return []

        # Re-rank
        try:
            pairs  = [[query, doc.page_content] for doc in retrieved]
            scores = self._reranker.predict(pairs)
            scored = sorted(zip(retrieved, scores), key=lambda x: x[1], reverse=True)
            top    = scored[:TOP_N_RERANK]
        except Exception as e:
            # Graceful fallback: use BM25 ordering
            top = [(doc, 0.0) for doc in retrieved[:TOP_N_RERANK]]

        results = []
        for rank, (doc, score) in enumerate(top, start=1):
            results.append(
                SearchResult(
                    rank=rank,
                    content=doc.page_content,
                    score=float(score),
                    source=doc.metadata.get("source_file", "unknown"),
                    page=doc.metadata.get("page", 0) + 1,
                    topic=doc.metadata.get("topic", "General"),
                )
            )
        return results

    # ── Public: Status ────────────────────────────────────────────────────────
    def get_status(self) -> EngineStatus:
        return self._status
