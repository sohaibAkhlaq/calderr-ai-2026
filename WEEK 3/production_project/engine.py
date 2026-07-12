"""
engine.py -- Real-Time Research Engine Backend
==============================================
Week 3 Production Project (Day 7) -- Option B

All ML-heavy imports (torch, sentence_transformers, HuggingFace) are
LAZY -- they only load when initialize() is called, NOT at module startup.
This prevents the Windows WinError 1114 DLL crash when Streamlit imports
this module at launch time.

Pipeline Steps:
  Step 1 -- PDF Download       (PipelineStage.DOWNLOAD)
  Step 2 -- Document Loading   (PipelineStage.LOAD)
  Step 3 -- Text Splitting     (PipelineStage.SPLIT)
  Step 4 -- Embedding          (PipelineStage.EMBED)
  Step 5 -- Vector Store Build (PipelineStage.STORE)
  Step 6 -- Retriever Assembly (PipelineStage.RETRIEVE)
  Step 7 -- Re-ranking         (PipelineStage.RERANK)
"""

# ── Safe system imports only (no torch, no sentence_transformers) ─────────────
import os
import ssl
import traceback
import urllib.request
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

ssl._create_default_https_context = ssl._create_unverified_context

import warnings
warnings.filterwarnings("ignore")

# ── Pure-Python LangChain imports (safe -- no torch dependency) ───────────────
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

# NOTE: HuggingFaceEmbeddings, Chroma, BM25Retriever, EnsembleRetriever,
#       and CrossEncoder are imported LAZILY inside each method to avoid
#       loading torch at module import time.


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
    Raised when a critical pipeline step fails.

    Attributes:
        stage   -- Which PipelineStage failed (shown to user in Streamlit)
        message -- Human-readable explanation + recovery guidance
    """
    def __init__(self, stage: PipelineStage, message: str):
        self.stage = stage
        self.message = message
        super().__init__(f"[{stage.value}] {message}")


@dataclass
class SearchResult:
    rank:    int
    content: str
    score:   float
    source:  str
    page:    int
    topic:   str


@dataclass
class EngineStatus:
    ready:        bool
    chunks_loaded: int
    pdf_path:     str
    error:        Optional[str] = None
    stage_failed: Optional[str] = None


# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR        = os.path.join(BASE_DIR, "docs")
CHROMA_DIR      = os.path.join(BASE_DIR, "chroma_db")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
RERANKER_MODEL  = "cross-encoder/ms-marco-MiniLM-L-6-v2"
CHUNK_SIZE      = 512
CHUNK_OVERLAP   = 64
BM25_WEIGHT     = 0.40
SEMANTIC_WEIGHT = 0.60
TOP_K_RETRIEVE  = 12
TOP_N_RERANK    = 4

PDF_SOURCES = [
    {
        "name":  "Attention Is All You Need",
        "url":   "https://arxiv.org/pdf/1706.03762.pdf",
        "file":  "attention_is_all_you_need.pdf",
        "topic": "Transformer Architecture",
    },
    {
        "name":  "BERT: Pre-training of Deep Bidirectional Transformers",
        "url":   "https://arxiv.org/pdf/1810.04805.pdf",
        "file":  "bert_pretraining.pdf",
        "topic": "BERT & Language Models",
    },
]


# ──────────────────────────────────────────────────────────────────────────────
# RESEARCH ENGINE CLASS
# ──────────────────────────────────────────────────────────────────────────────

class ResearchEngine:
    """
    Production-grade RAG engine with strict error boundaries and lazy ML imports.

    Usage:
        engine = ResearchEngine()          # Safe -- no torch loaded yet
        engine.initialize(progress_cb)     # Loads all ML models on demand
        results = engine.search(query)     # Returns List[SearchResult]
        status  = engine.get_status()      # Returns EngineStatus
    """

    def __init__(self):
        self._splits    = []
        self._retriever = None
        self._reranker  = None
        self._ready     = False
        self._status    = EngineStatus(ready=False, chunks_loaded=0, pdf_path="")

    # ── Step 1: Download ──────────────────────────────────────────────────────
    def _download_pdfs(self) -> List[Tuple[str, str]]:
        """
        Downloads each configured PDF if not already on disk.
        FAILURE: Raises ResearchEngineError(DOWNLOAD) -- pipeline ABORTS.
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

    # ── Step 2: Load ──────────────────────────────────────────────────────────
    def _load_documents(self, pdf_paths: List[Tuple[str, str]]) -> List[Document]:
        """
        Loads all PDFs using PyPDFLoader.
        FAILURE: Raises ResearchEngineError(LOAD) -- pipeline ABORTS.
        """
        all_docs = []
        for path, topic in pdf_paths:
            if not os.path.exists(path):
                raise ResearchEngineError(
                    PipelineStage.LOAD,
                    f"PDF not found on disk: {path}",
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
                doc.metadata["topic"]       = topic
                doc.metadata["source_file"] = os.path.basename(path)
            all_docs.extend(docs)
        return all_docs

    # ── Step 3: Split ─────────────────────────────────────────────────────────
    def _split_documents(self, docs: List[Document]) -> List[Document]:
        """
        Splits pages into overlapping chunks.
        FAILURE: Raises ResearchEngineError(SPLIT) -- pipeline ABORTS.
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
                "Text splitting produced 0 chunks from the loaded documents.",
            )
        return splits

    # ── Step 4: Embed (LAZY IMPORT) ───────────────────────────────────────────
    def _create_embeddings(self):
        """
        Loads the sentence-transformer embedding model.
        LAZY IMPORT: HuggingFaceEmbeddings is imported HERE, not at module level.
        FAILURE: Raises ResearchEngineError(EMBED).
        """
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        except Exception as e:
            raise ResearchEngineError(
                PipelineStage.EMBED,
                f"Failed to load embedding model '{EMBEDDING_MODEL}'.\n"
                f"Check HuggingFace connectivity. Error: {e}",
            )

    # ── Step 5: Store (LAZY IMPORT) ───────────────────────────────────────────
    def _create_vector_store(self, splits: List[Document], embeddings):
        """
        Embeds chunks and persists them in ChromaDB.
        LAZY IMPORT: Chroma is imported HERE.
        FAILURE: Raises ResearchEngineError(STORE).
        """
        try:
            from langchain_chroma import Chroma
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

    # ── Step 6: Retriever (LAZY IMPORT) ───────────────────────────────────────
    def _create_retriever(self, splits: List[Document], vectorstore):
        """
        Assembles the Hybrid EnsembleRetriever (BM25 + Semantic).
        LAZY IMPORT: BM25Retriever and EnsembleRetriever imported HERE.
        FAILURE: Raises ResearchEngineError(RETRIEVE).
        """
        try:
            from langchain_community.retrievers import BM25Retriever
            from langchain.retrievers import EnsembleRetriever
            bm25          = BM25Retriever.from_documents(splits)
            bm25.k        = TOP_K_RETRIEVE
            semantic      = vectorstore.as_retriever(search_kwargs={"k": TOP_K_RETRIEVE})
            return EnsembleRetriever(
                retrievers=[bm25, semantic],
                weights=[BM25_WEIGHT, SEMANTIC_WEIGHT],
            )
        except Exception as e:
            raise ResearchEngineError(
                PipelineStage.RETRIEVE,
                f"Failed to assemble EnsembleRetriever.\nError: {e}",
            )

    # ── Step 7: Re-ranker (LAZY IMPORT) ───────────────────────────────────────
    def _load_reranker(self):
        """
        Loads the cross-encoder re-ranking model.
        LAZY IMPORT: CrossEncoder imported HERE (this is where torch first loads).
        FAILURE: Raises ResearchEngineError(RERANK).
        """
        try:
            from sentence_transformers import CrossEncoder
            return CrossEncoder(RERANKER_MODEL, max_length=512)
        except Exception as e:
            raise ResearchEngineError(
                PipelineStage.RERANK,
                f"Failed to load CrossEncoder '{RERANKER_MODEL}'.\nError: {e}",
            )

    # ── Public: Initialize ────────────────────────────────────────────────────
    def initialize(self, progress_callback=None) -> "EngineStatus":
        """
        Runs all 7 pipeline steps in strict sequence.
        Returns EngineStatus(ready=True) on success.
        Returns EngineStatus(ready=False, error=...) on failure -- never raises.
        """
        def _progress(msg: str):
            if progress_callback:
                progress_callback(msg)

        try:
            _progress("Step 1/7 -- Checking / downloading PDFs...")
            pdf_paths = self._download_pdfs()

            _progress("Step 2/7 -- Loading documents from PDF...")
            docs = self._load_documents(pdf_paths)

            _progress(f"Step 3/7 -- Splitting {len(docs)} pages into chunks...")
            self._splits = self._split_documents(docs)

            _progress(f"Step 4/7 -- Loading embedding model ({EMBEDDING_MODEL})...")
            embeddings = self._create_embeddings()

            _progress(f"Step 5/7 -- Building ChromaDB ({len(self._splits)} chunks)...")
            vectorstore = self._create_vector_store(self._splits, embeddings)

            _progress("Step 6/7 -- Assembling Hybrid Retriever (BM25 + Semantic)...")
            self._retriever = self._create_retriever(self._splits, vectorstore)

            _progress(f"Step 7/7 -- Loading Cross-Encoder ({RERANKER_MODEL})...")
            self._reranker = self._load_reranker()

            self._ready  = True
            self._status = EngineStatus(
                ready=True,
                chunks_loaded=len(self._splits),
                pdf_path=DOCS_DIR,
            )
            _progress("Engine ready!")

        except ResearchEngineError as e:
            self._status = EngineStatus(
                ready=False, chunks_loaded=0, pdf_path="",
                error=e.message, stage_failed=e.stage.value,
            )
        except Exception as e:
            self._status = EngineStatus(
                ready=False, chunks_loaded=0, pdf_path="",
                error=traceback.format_exc(), stage_failed="Unknown",
            )

        return self._status

    # ── Public: Search ────────────────────────────────────────────────────────
    def search(self, query: str) -> List[SearchResult]:
        """
        Runs hybrid retrieval + cross-encoder re-ranking.
        Raises ResearchEngineError if engine is not initialized.
        On re-ranking failure, degrades gracefully to hybrid order.
        """
        if not self._ready or self._retriever is None:
            raise ResearchEngineError(
                PipelineStage.RETRIEVE,
                "Engine is not initialized. Call engine.initialize() first.",
            )
        if not query or not query.strip():
            return []

        try:
            retrieved = self._retriever.invoke(query.strip())
        except Exception as e:
            raise ResearchEngineError(
                PipelineStage.RETRIEVE,
                f"Retriever failed on query '{query}'.\nError: {e}",
            )

        if not retrieved:
            return []

        # Re-rank (graceful fallback on failure)
        try:
            pairs  = [[query, doc.page_content] for doc in retrieved]
            scores = self._reranker.predict(pairs)
            scored = sorted(zip(retrieved, scores), key=lambda x: x[1], reverse=True)
            top    = scored[:TOP_N_RERANK]
        except Exception:
            top = [(doc, 0.0) for doc in retrieved[:TOP_N_RERANK]]

        return [
            SearchResult(
                rank=rank,
                content=doc.page_content,
                score=float(score),
                source=doc.metadata.get("source_file", "unknown"),
                page=doc.metadata.get("page", 0) + 1,
                topic=doc.metadata.get("topic", "General"),
            )
            for rank, (doc, score) in enumerate(top, start=1)
        ]

    # ── Public: Status ────────────────────────────────────────────────────────
    def get_status(self) -> EngineStatus:
        return self._status
