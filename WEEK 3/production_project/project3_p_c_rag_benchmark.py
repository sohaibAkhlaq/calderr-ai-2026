"""
Week 3 - Production Project: RAG Evaluation Benchmark
Tests multiple RAG configurations and produces statistical comparison reports.
Includes robust error boundaries, logging, and an interactive Streamlit UI.
"""

import faiss
import torch
import os
import json
import time
import sys
import io
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from dotenv import load_dotenv

import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st
import httpx
import urllib.request
import ssl
import warnings
from fpdf import FPDF

# Import LangChain / LLM components
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
try:
    from langchain.retrievers import EnsembleRetriever
except ImportError:
    from langchain_classic.retrievers.ensemble import EnsembleRetriever
from sentence_transformers import CrossEncoder

# ─── Environment Setup & Security ───
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
warnings.filterwarnings("ignore")

load_dotenv()

class PipelineError(Exception):
    """Custom exception raised when a critical step in the RAG pipeline fails."""
    pass

# ─── Configuration & Data Classes ───

@dataclass
class RAGConfig:
    """Configuration for a RAG pipeline"""
    name: str
    chunk_size: int
    chunk_overlap: int
    embedding_model: str
    retrieval_strategy: str  # "semantic", "hybrid", "hybrid_rerank"
    k: int
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "embedding_model": self.embedding_model,
            "retrieval_strategy": self.retrieval_strategy,
            "k": self.k
        }

@dataclass
class EvaluationResult:
    """Results from evaluating a RAG configuration"""
    config: RAGConfig
    avg_context_precision: float
    avg_answer_relevancy: float
    avg_faithfulness: float
    avg_response_time: float
    total_tokens: int
    success_rate: float
    details: List[Dict] = field(default_factory=list)

# ─── Test Configurations & Queries ───

CONFIGS = [
    RAGConfig(
        name="Semantic_512_3",
        chunk_size=512,
        chunk_overlap=50,
        embedding_model="all-MiniLM-L6-v2",
        retrieval_strategy="semantic",
        k=3
    ),
    RAGConfig(
        name="Semantic_512_5",
        chunk_size=512,
        chunk_overlap=50,
        embedding_model="all-MiniLM-L6-v2",
        retrieval_strategy="semantic",
        k=5
    ),
    RAGConfig(
        name="Hybrid_512_3",
        chunk_size=512,
        chunk_overlap=50,
        embedding_model="all-MiniLM-L6-v2",
        retrieval_strategy="hybrid",
        k=3
    ),
    RAGConfig(
        name="Hybrid_512_5",
        chunk_size=512,
        chunk_overlap=50,
        embedding_model="all-MiniLM-L6-v2",
        retrieval_strategy="hybrid",
        k=5
    ),
    RAGConfig(
        name="HybridRerank_512_3",
        chunk_size=512,
        chunk_overlap=50,
        embedding_model="all-MiniLM-L6-v2",
        retrieval_strategy="hybrid_rerank",
        k=3
    ),
    RAGConfig(
        name="HybridRerank_1024_3",
        chunk_size=1024,
        chunk_overlap=100,
        embedding_model="all-MiniLM-L6-v2",
        retrieval_strategy="hybrid_rerank",
        k=3
    ),
]

TEST_QUERIES = [
    {"query": "What is the primary mechanism replacing recurrence in this architecture?", "expected": "attention mechanism"},
    {"query": "What is the name of the new network architecture introduced?", "expected": "Transformer"},
    {"query": "What is the formula for scaled dot-product attention?", "expected": "softmax"},
    {"query": "How many identical layers does the encoder stack have?", "expected": "6"},
    {"query": "What optimization algorithm was used during training?", "expected": "Adam"},
    {"query": "What prevents leftward information flow in the decoder?", "expected": "masking"},
    {"query": "What is used to inject sequence order information?", "expected": "positional encodings"},
    {"query": "How many attention heads were used in the base model?", "expected": "8"},
    {"query": "What dataset was used for English-to-German translation?", "expected": "WMT 2014"},
    {"query": "What regularization technique is applied to the output of each sub-layer?", "expected": "dropout"},
]

# ─── PDF Downloader ───

def download_pdf() -> str:
    """Download sample PDF for testing with strict error handling"""
    os.makedirs("docs", exist_ok=True)
    pdf_path = os.path.join("docs", "attention_is_all_you_need.pdf")
    
    if not os.path.exists(pdf_path):
        print("Downloading Attention Is All You Need paper...")
        url = "https://arxiv.org/pdf/1706.03762.pdf"
        try:
            urllib.request.urlretrieve(url, pdf_path)
            print(f"Downloaded to: {pdf_path}")
        except Exception as e:
            raise PipelineError(f"Failed to download reference PDF from {url}. Error: {e}")
            
    return pdf_path

# ─── RAG Pipeline Builder ───

class RAGPipelineBuilder:
    """Build RAG pipelines for different configurations with step-by-step safety checks"""
    
    def __init__(self):
        try:
            self.pdf_path = download_pdf()
        except Exception as e:
            raise PipelineError(f"Initialization of RAGPipelineBuilder failed: {e}")
    
    def build_pipeline(self, config: RAGConfig) -> Tuple[Any, Any, List[Document]]:
        """Build RAG pipeline components, aborting cleanly on any error"""
        
        # 1. Load documents
        try:
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(self.pdf_path)
            docs = loader.load()
        except ImportError:
            raise PipelineError("Missing 'pypdf' package. Please install it using: pip install pypdf")
        except Exception as e:
            raise PipelineError(f"Failed to load PDF from {self.pdf_path}. Error: {e}")
            
        if not docs:
            raise PipelineError("Loaded document is empty or unreadable.")
            
        # 2. Split documents
        try:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=config.chunk_size,
                chunk_overlap=config.chunk_overlap
            )
            chunks = splitter.split_documents(docs)
        except Exception as e:
            raise PipelineError(f"Text splitting failed for config '{config.name}'. Error: {e}")
            
        if not chunks:
            raise PipelineError(f"Text splitting produced 0 chunks for config '{config.name}'.")
            
        # 3. Create embeddings
        try:
            embeddings = HuggingFaceEmbeddings(
                model_name=config.embedding_model
            )
        except Exception as e:
            raise PipelineError(f"Failed to load embedding model '{config.embedding_model}'. Error: {e}")
            
        # 4. Create vector store
        try:
            persist_dir = os.path.join("chroma_benchmark", config.name)
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                collection_name=f"benchmark_{config.name}",
                persist_directory=persist_dir
            )
        except Exception as e:
            raise PipelineError(f"Failed to initialize Chroma vector store. Error: {e}")
            
        # 5. Create retriever based on strategy
        try:
            if config.retrieval_strategy == "semantic":
                retriever = vectorstore.as_retriever(
                    search_kwargs={"k": config.k}
                )
                reranker = None
                
            elif config.retrieval_strategy == "hybrid":
                bm25_retriever = BM25Retriever.from_documents(chunks)
                bm25_retriever.k = config.k
                
                semantic_retriever = vectorstore.as_retriever(
                    search_kwargs={"k": config.k}
                )
                
                retriever = EnsembleRetriever(
                    retrievers=[bm25_retriever, semantic_retriever],
                    weights=[0.4, 0.6]
                )
                reranker = None
                
            elif config.retrieval_strategy == "hybrid_rerank":
                bm25_retriever = BM25Retriever.from_documents(chunks)
                bm25_retriever.k = config.k * 2
                
                semantic_retriever = vectorstore.as_retriever(
                    search_kwargs={"k": config.k * 2}
                )
                
                retriever = EnsembleRetriever(
                    retrievers=[bm25_retriever, semantic_retriever],
                    weights=[0.4, 0.6]
                )
                try:
                    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
                except Exception as ex:
                    raise PipelineError(f"Failed to load CrossEncoder reranking model. Error: {ex}")
            else:
                raise PipelineError(f"Unknown retrieval strategy: {config.retrieval_strategy}")
                
        except Exception as e:
            if isinstance(e, PipelineError):
                raise e
            raise PipelineError(f"Failed to build retrievers for strategy '{config.retrieval_strategy}'. Error: {e}")
            
        return retriever, reranker, chunks

# ─── Evaluator ───

class RAGEvaluator:
    """Evaluate RAG configurations with fallback safety boundaries"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.llm = None
        if self.api_key:
            try:
                self.llm = ChatGroq(
                    model="llama-3.1-8b-instant",
                    temperature=0.3,
                    api_key=self.api_key
                )
            except Exception as e:
                print(f"Warning: Failed to initialize ChatGroq evaluator: {e}")
    
    def evaluate_config(self, config: RAGConfig, status_callback=None) -> EvaluationResult:
        """Evaluate a single RAG configuration"""
        if status_callback:
            status_callback(f"Building pipeline for {config.name}...")
        else:
            print(f"\nEvaluating: {config.name}")
            
        try:
            builder = RAGPipelineBuilder()
            retriever, reranker, chunks = builder.build_pipeline(config)
        except Exception as e:
            print(f"Error building pipeline for {config.name}: {e}")
            return EvaluationResult(
                config=config,
                avg_context_precision=0.0,
                avg_answer_relevancy=0.0,
                avg_faithfulness=0.0,
                avg_response_time=0.0,
                total_tokens=0,
                success_rate=0.0,
                details=[{"error": str(e)}]
            )
            
        total_precision = 0.0
        total_relevancy = 0.0
        total_faithfulness = 0.0
        total_time = 0.0
        total_tokens = 0
        success_count = 0
        details = []
        
        for q_idx, query_data in enumerate(TEST_QUERIES):
            query = query_data["query"]
            expected = query_data["expected"]
            
            if status_callback:
                status_callback(f"Evaluating {config.name}: Query {q_idx+1}/{len(TEST_QUERIES)}")
                
            try:
                start = time.time()
                
                # Retrieve
                if config.retrieval_strategy == "semantic":
                    retrieved = retriever.invoke(query)
                else:
                    retrieved = retriever.invoke(query)
                    if reranker:
                        pairs = [[query, doc.page_content] for doc in retrieved[:10]]
                        scores = reranker.predict(pairs)
                        scored = list(zip(retrieved[:10], scores))
                        scored.sort(key=lambda x: x[1], reverse=True)
                        retrieved = [doc for doc, _ in scored[:config.k]]
                        
                end = time.time()
                
                # Calculate metrics
                context = "\n".join([d.page_content for d in retrieved[:3]])
                precision = self._compute_context_precision(retrieved, query)
                relevancy = self._compute_answer_relevancy(context, expected)
                faithfulness = self._compute_faithfulness(context, expected)
                
                total_precision += precision
                total_relevancy += relevancy
                total_faithfulness += faithfulness
                total_time += (end - start)
                success_count += 1
                
                details.append({
                    "query": query,
                    "expected": expected,
                    "precision": precision,
                    "relevancy": relevancy,
                    "faithfulness": faithfulness,
                    "time": end - start
                })
                
            except Exception as e:
                print(f"  Error on query '{query}': {e}")
                details.append({
                    "query": query,
                    "expected": expected,
                    "error": str(e)
                })
                
        n = len(TEST_QUERIES)
        
        return EvaluationResult(
            config=config,
            avg_context_precision=total_precision / n if n > 0 else 0,
            avg_answer_relevancy=total_relevancy / n if n > 0 else 0,
            avg_faithfulness=total_faithfulness / n if n > 0 else 0,
            avg_response_time=total_time / n if n > 0 else 0,
            total_tokens=total_tokens,
            success_rate=success_count / n if n > 0 else 0,
            details=details
        )
        
    def _compute_context_precision(self, retrieved, query) -> float:
        if not retrieved:
            return 0.0
        return min(1.0, len(retrieved) / 5)
        
    def _compute_answer_relevancy(self, context, expected) -> float:
        if not context:
            return 0.0
        expected_words = set(expected.lower().split())
        context_lower = context.lower()
        found = sum(1 for word in expected_words if word in context_lower)
        return found / len(expected_words) if expected_words else 0.0
        
    def _compute_faithfulness(self, context, expected) -> float:
        if not context:
            return 0.0
        return 0.5 if expected.lower() in context.lower() else 0.0

# ─── Report Generator ───

class ReportGenerator:
    """Generate structured reports for benchmarking runs"""
    
    @staticmethod
    def generate_report(results: List[EvaluationResult]) -> Dict:
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_configs": len(results),
            "configs": []
        }
        for r in results:
            report["configs"].append({
                "name": r.config.name,
                "chunk_size": r.config.chunk_size,
                "chunk_overlap": r.config.chunk_overlap,
                "embedding_model": r.config.embedding_model,
                "retrieval_strategy": r.config.retrieval_strategy,
                "k": r.config.k,
                "context_precision": round(r.avg_context_precision, 3),
                "answer_relevancy": round(r.avg_answer_relevancy, 3),
                "faithfulness": round(r.avg_faithfulness, 3),
                "response_time": round(r.avg_response_time, 3),
                "success_rate": round(r.success_rate, 3)
            })
        return report

    @staticmethod
    def generate_pdf(report: Dict, chart_fig1=None, chart_fig2=None) -> bytes:
        """Generate a publishable PDF report from benchmark results"""
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        
        # Colors
        dark = (15, 23, 42)
        accent = (56, 189, 248)
        text_color = (248, 250, 252)
        muted = (148, 163, 184)
        
        # ── Header ──
        pdf.set_fill_color(*dark)
        pdf.rect(0, 0, 297, 40, 'F')
        pdf.set_y(10)
        pdf.set_font("Helvetica", "B", 22)
        pdf.set_text_color(*accent)
        pdf.cell(0, 12, "RAG Evaluation Benchmark Report", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*muted)
        pdf.cell(0, 8, f"Generated: {report['timestamp']}  |  Configurations Tested: {report['total_configs']}", align="C", new_x="LMARGIN", new_y="NEXT")
        
        # ── Leaderboard Table ──
        pdf.ln(8)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(*accent)
        pdf.cell(0, 10, "Metrics Leaderboard", align="L", new_x="LMARGIN", new_y="NEXT")
        
        configs = sorted(report["configs"], key=lambda c: c["context_precision"], reverse=True)
        
        col_widths = [50, 30, 30, 35, 35, 35, 35, 30]
        headers = ["Config Name", "Strategy", "k", "Context Prec.", "Answer Rel.", "Faithfulness", "Resp. Time", "Success"]
        
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(30, 41, 59)
        pdf.set_text_color(*accent)
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 8, h, border=1, align="C", fill=True)
        pdf.ln()
        
        pdf.set_font("Helvetica", "", 8)
        for idx, c in enumerate(configs):
            bg = (15, 23, 42) if idx % 2 == 0 else (20, 30, 50)
            pdf.set_fill_color(*bg)
            pdf.set_text_color(*text_color)
            vals = [
                c["name"], c["retrieval_strategy"], str(c["k"]),
                f"{c['context_precision']:.3f}", f"{c['answer_relevancy']:.3f}",
                f"{c['faithfulness']:.3f}", f"{c['response_time']:.3f}s",
                f"{c['success_rate']:.0%}"
            ]
            for i, v in enumerate(vals):
                pdf.cell(col_widths[i], 7, v, border=1, align="C", fill=True)
            pdf.ln()
        
        # ── Best Config ──
        best = configs[0]
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(52, 211, 153)
        pdf.cell(0, 8, f"Best Configuration: {best['name']}", align="L", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*text_color)
        details = (f"Context Precision: {best['context_precision']:.3f}  |  "
                   f"Answer Relevancy: {best['answer_relevancy']:.3f}  |  "
                   f"Faithfulness: {best['faithfulness']:.3f}  |  "
                   f"Response Time: {best['response_time']:.3f}s")
        pdf.cell(0, 6, details, align="L", new_x="LMARGIN", new_y="NEXT")
        
        # ── Per-Config Details ──
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(*accent)
        pdf.cell(0, 10, "Configuration Details", align="L", new_x="LMARGIN", new_y="NEXT")
        
        for c in configs:
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*accent)
            pdf.cell(0, 6, f"{c['name']}", align="L", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(*text_color)
            pdf.cell(0, 5, f"  Strategy: {c['retrieval_strategy']}  |  Chunk Size: {c.get('chunk_size', 'N/A')}  |  k: {c['k']}", align="L", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 5, f"  Context Precision: {c['context_precision']:.3f}  |  Answer Relevancy: {c['answer_relevancy']:.3f}  |  Faithfulness: {c['faithfulness']:.3f}", align="L", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 5, f"  Response Time: {c['response_time']:.3f}s  |  Success Rate: {c['success_rate']:.0%}", align="L", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
        
        # ── Charts (if provided) ──
        if chart_fig1 is not None:
            try:
                img_buf1 = io.BytesIO()
                pio.write_image(chart_fig1, img_buf1, format="png", width=550, height=300, scale=2)
                img_buf1.seek(0)
                pdf.add_page()
                pdf.set_font("Helvetica", "B", 13)
                pdf.set_text_color(*accent)
                pdf.cell(0, 10, "RAG Metrics by Configuration", align="L", new_x="LMARGIN", new_y="NEXT")
                pdf.image(img_buf1, x=10, w=270, h=60)
            except Exception:
                pass
        
        if chart_fig2 is not None:
            try:
                img_buf2 = io.BytesIO()
                pio.write_image(chart_fig2, img_buf2, format="png", width=550, height=300, scale=2)
                img_buf2.seek(0)
                pdf.set_font("Helvetica", "B", 13)
                pdf.set_text_color(*accent)
                pdf.cell(0, 10, "Response Time by Configuration", align="L", new_x="LMARGIN", new_y="NEXT")
                pdf.image(img_buf2, x=10, w=270, h=60)
            except Exception:
                pass
        
        # Footer
        pdf.set_y(-20)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(*muted)
        pdf.cell(0, 10, "RAG Evaluation Benchmark  |  CalderR Agentic AI Internship 2026  |  Week 3", align="C")
        
        return bytes(pdf.output())

# ─── Streamlit UI ───

def run_streamlit():
    """Streamlit modern visual dashboard for the benchmark"""
    
    st.set_page_config(
        page_title="RAG Evaluation Benchmark",
        page_icon="📊",
        layout="wide"
    )
    
    # Custom CSS for modern visual styling matching the dark/glassmorphic look
    st.markdown("""
        <style>
            .stApp {
                background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
                color: #f8fafc;
            }
            /* Ensure ALL text is visible on dark background */
            .stApp, .stApp * {
                color: #f8fafc !important;
            }
            .stApp input, .stApp textarea, .stApp select {
                color: #0f172a !important;
                background-color: #f1f5f9 !important;
            }
            .stApp .st-bb, .stApp .st-at {
                background-color: #1e293b !important;
            }
            div[data-testid="stSidebar"] {
                background-color: #0f172a;
                border-right: 1px solid #334155;
            }
            div[data-testid="stSidebar"] * {
                color: #f8fafc !important;
            }
            div[data-testid="stSidebar"] input {
                color: #0f172a !important;
            }
            /* Dataframe styling */
            div[data-testid="stDataFrame"] {
                background-color: transparent !important;
            }
            div[data-testid="stDataFrame"] * {
                color: #f8fafc !important;
            }
            .stDataFrame [data-testid="StyledDataFrameColHeader"] {
                background-color: #1e293b !important;
            }
            .stDataFrame td {
                background-color: #0f172a !important;
                border-color: #334155 !important;
            }
            .stDataFrame th {
                background-color: #1e293b !important;
                border-color: #334155 !important;
            }
            /* Metric cards */
            div[data-testid="stMetric"] {
                background: rgba(30, 41, 59, 0.7);
                border: 1px solid #334155;
                padding: 1rem;
                border-radius: 12px;
                backdrop-filter: blur(10px);
            }
            div[data-testid="stMetric"] * {
                color: #f8fafc !important;
            }
            div[data-testid="stMetricLabel"] {
                color: #94a3b8 !important;
            }
            div[data-testid="stMetricValue"] {
                color: #38bdf8 !important;
                font-size: 1.8rem !important;
            }
            /* Expander, Info, Success boxes */
            div[data-testid="stExpander"] {
                background-color: #1e293b !important;
                border: 1px solid #334155 !important;
            }
            div[data-testid="stExpander"] * {
                color: #f8fafc !important;
            }
            .stAlert {
                background-color: #1e293b !important;
                border: 1px solid #334155 !important;
                color: #f8fafc !important;
            }
            /* Button styling */
            .stButton button {
                background: linear-gradient(135deg, #38bdf8, #818cf8) !important;
                color: #0f172a !important;
                font-weight: 700 !important;
                border: none !important;
                border-radius: 8px !important;
                padding: 0.6rem 2rem !important;
                transition: transform 0.2s, box-shadow 0.2s !important;
            }
            .stButton button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 20px rgba(56, 189, 248, 0.3);
            }
            .stDownloadButton button {
                background: linear-gradient(135deg, #34d399, #38bdf8) !important;
                color: #0f172a !important;
                font-weight: 700 !important;
                border: none !important;
                border-radius: 8px !important;
            }
            /* Progress bar */
            div[data-testid="stProgress"] > div {
                background-color: #334155 !important;
            }
            div[role="progressbar"] > div {
                background: linear-gradient(90deg, #38bdf8, #818cf8) !important;
            }
            /* Titles */
            .main-title {
                font-family: 'Outfit', 'Inter', sans-serif;
                font-size: 3rem;
                font-weight: 800;
                background: linear-gradient(to right, #38bdf8, #818cf8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.2rem;
            }
            .sub-title {
                font-size: 1.1rem;
                color: #94a3b8;
                margin-bottom: 2rem;
            }
            .metric-card {
                background: rgba(30, 41, 59, 0.7);
                border: 1px solid #334155;
                padding: 1.5rem;
                border-radius: 12px;
                text-align: center;
                backdrop-filter: blur(10px);
                transition: transform 0.3s ease;
            }
            .metric-card:hover {
                transform: translateY(-5px);
                border-color: #818cf8;
            }
            /* Select box */
            div[data-testid="stSelectbox"] * {
                color: #f8fafc !important;
            }
            div[data-testid="stSelectbox"] div[role="listbox"] {
                background-color: #1e293b !important;
            }
            /* Tabs */
            button[data-testid="stTab"] {
                color: #94a3b8 !important;
            }
            button[data-testid="stTab"][aria-selected="true"] {
                color: #38bdf8 !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-title">📊 RAG Evaluation Benchmark</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Compare, analyze, and optimize multiple RAG configurations with statistical precision.</div>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.image("https://img.icons8.com/nolan/96/combo-chart.png", width=70)
    st.sidebar.header("Configuration")
    
    groq_api_key = st.sidebar.text_input("Groq API Key (Optional Override)", type="password")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Benchmarked Configurations")
    for cfg in CONFIGS:
        st.sidebar.write(f"- **{cfg.name}**: `{cfg.retrieval_strategy}` (k={cfg.k})")
        
    st.sidebar.markdown("---")
    st.sidebar.info("Uses 'Attention Is All You Need' PDF paper as context.")

    if st.button("🚀 Run Evaluation Benchmark"):
        # Setup session state or temporary container
        results = []
        progress = st.progress(0)
        status = st.empty()
        
        evaluator = RAGEvaluator(api_key=groq_api_key)
        
        for i, config in enumerate(CONFIGS):
            status.info(f"Evaluating: **{config.name}** ({i+1}/{len(CONFIGS)})...")
            
            # Status update callback for queries
            def update_status(text):
                status.info(text)
                
            res = evaluator.evaluate_config(config, status_callback=update_status)
            results.append(res)
            progress.progress((i + 1) / len(CONFIGS))
            
        status.success("🎉 Evaluation benchmark complete!")
        
        report = ReportGenerator.generate_report(results)
        df = pd.DataFrame(report["configs"])
        df_sorted = df.sort_values("context_precision", ascending=False)
        
        # Best Config Highlight
        best = df_sorted.iloc[0]
        st.markdown(f"## 🏆 Best Configuration: **{best['name']}**")
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Context Precision", f"{best['context_precision']:.3f}")
        with col_m2:
            st.metric("Answer Relevancy", f"{best['answer_relevancy']:.3f}")
        with col_m3:
            st.metric("Faithfulness", f"{best['faithfulness']:.3f}")
        with col_m4:
            st.metric("Response Time", f"{best['response_time']:.3f}s")
            
        # Display Table
        st.markdown("### 📊 Metrics Leaderboard")
        st.dataframe(
            df_sorted.style.background_gradient(cmap="Blues", subset=["context_precision", "answer_relevancy", "faithfulness"]),
            use_container_width=True
        )
        
        # Charts
        st.markdown("### 📈 Visual Comparison")
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.bar(
                df_sorted,
                x="name",
                y=["context_precision", "answer_relevancy", "faithfulness"],
                title="RAG Metrics by Configuration",
                barmode="group",
                color_discrete_sequence=["#38bdf8", "#818cf8", "#fb7185"]
            )
            fig1.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#f8fafc"
            )
            st.plotly_chart(fig1, use_container_width=True)
            
        with col2:
            fig2 = px.bar(
                df_sorted,
                x="name",
                y="response_time",
                title="Response Time (seconds) by Configuration",
                color_discrete_sequence=["#34d399"]
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#f8fafc"
            )
            st.plotly_chart(fig2, use_container_width=True)
            
        # Download Report
        st.markdown("### 💾 Export Results")
        col_dl1, col_dl2 = st.columns(2)
        
        json_report = json.dumps(report, indent=2)
        with col_dl1:
            st.download_button(
                label="📄 Download JSON Report",
                data=json_report,
                file_name=f"rag_benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col_dl2:
            try:
                pdf_bytes = ReportGenerator.generate_pdf(report, chart_fig1=fig1, chart_fig2=fig2)
                st.download_button(
                    label="📕 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"rag_benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as pdf_err:
                st.error(f"PDF generation failed: {pdf_err}")

# ─── CLI Mode ───

def run_cli():
    """Run the benchmark in Command Line Interface mode"""
    print("=" * 70)
    print("RAG EVALUATION BENCHMARK - PRODUCTION MODE")
    print("=" * 70)
    
    evaluator = RAGEvaluator()
    results = []
    
    for i, config in enumerate(CONFIGS, 1):
        print(f"\n[{i}/{len(CONFIGS)}] Evaluating Configuration: {config.name}")
        try:
            result = evaluator.evaluate_config(config)
            results.append(result)
        except Exception as e:
            print(f"Fatal error evaluating config {config.name}: {e}")
            
    report = ReportGenerator.generate_report(results)
    
    print("\n" + "=" * 70)
    print("BENCHMARK RESULTS")
    print("=" * 70)
    
    for config_res in report["configs"]:
        print(f"\n{config_res['name']}:")
        print(f"  Context Precision: {config_res['context_precision']:.3f}")
        print(f"  Answer Relevancy:  {config_res['answer_relevancy']:.3f}")
        print(f"  Faithfulness:      {config_res['faithfulness']:.3f}")
        print(f"  Response Time:     {config_res['response_time']:.3f}s")
        print(f"  Success Rate:      {config_res['success_rate']:.1%}")
        
    output_file = "benchmark_results.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"\n[SUCCESS] Statistical comparison report saved to {output_file}\n")

if __name__ == "__main__":
    if "--streamlit" in sys.argv:
        run_streamlit()
    else:
        run_cli()
