"""
Week 2 - Day 5: Project 2-P-C
Automated Financial Data Analysis Agent — Streamlit Production App

Architecture:
    CSV Upload
        -> Schema Analyzer (Pydantic, Day 2)
        -> Question Parser
        -> Code Generator (Groq LLM with CoT prompt, Day 1)
        -> Safe Code Executor (subprocess sandbox, Day 3 tool pattern)
        -> Chart Builder (Plotly)
        -> Report Builder (LLM narrative, Day 1 CoT)
        -> Currency Enrichment (live API with retry, Day 4)
        -> Download buttons

Week 2 Learning Integrated:
    Day 1 — Chain-of-thought prompts for code and report generation
    Day 2 — Pydantic AnalysisResult + ColumnSchema structured output
    Day 3 — Five named analysis tools (describe, plot, correlate, filter, stats)
    Day 4 — Exponential backoff for live currency rate fetch
"""

import os
import sys
import asyncio
import random
import subprocess
import tempfile
import json
import re
from datetime import datetime
from io import StringIO
from typing import Any, Dict, List, Literal, Optional, Tuple

import httpx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

load_dotenv()

# ─── Page Config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Financial Data Analysis Agent",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global Stylesheet ───────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    /* ── Base ── */
    html, body, [data-testid="stAppViewContainer"] {
        background: #0d1117;
        color: #c9d1d9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #161b22;
        border-right: 1px solid #21262d;
    }
    [data-testid="stSidebar"] .block-container { padding-top: 24px; }

    /* ── Metric cards ── */
    [data-testid="metric-container"] {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 10px;
        padding: 16px 20px;
    }
    [data-testid="stMetricValue"] { color: #58a6ff; font-size: 1.6rem; font-weight: 700; }
    [data-testid="stMetricLabel"] { color: #8b949e; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; }
    [data-testid="stMetricDelta"] { font-size: 0.8rem; }

    /* ── Headings ── */
    h1, h2, h3 { color: #e6edf3; letter-spacing: -0.01em; }
    h1 { font-size: 1.7rem; border-bottom: 2px solid #21262d; padding-bottom: 12px; margin-bottom: 20px; }
    h2 { font-size: 1.2rem; color: #58a6ff; margin-top: 32px; margin-bottom: 12px; }
    h3 { font-size: 1rem; color: #8b949e; }

    /* ── Dividers ── */
    hr { border-color: #21262d; margin: 24px 0; }

    /* ── Buttons ── */
    .stButton > button {
        background: #1f6feb;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 10px 24px;
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 0.02em;
        transition: background 0.2s, transform 0.1s;
    }
    .stButton > button:hover { background: #388bfd; transform: translateY(-1px); }

    /* ── Text input ── */
    .stTextInput > div > div > input {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        color: #c9d1d9;
        padding: 10px 14px;
    }
    .stTextInput > div > div > input:focus { border-color: #58a6ff; box-shadow: 0 0 0 3px rgba(88,166,255,0.15); }

    /* ── Select box ── */
    .stSelectbox > div > div {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        color: #c9d1d9;
    }

    /* ── Expander ── */
    details { background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 4px; margin-bottom: 12px; }
    summary { color: #8b949e; cursor: pointer; padding: 10px 14px; font-size: 0.88rem; }

    /* ── Code blocks ── */
    .stCodeBlock { border-radius: 8px; border: 1px solid #21262d; }

    /* ── Info / warning ── */
    .stAlert { border-radius: 8px; }

    /* ── Dataframe ── */
    [data-testid="stDataFrame"] { border-radius: 8px; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] { background: #161b22; border-radius: 8px 8px 0 0; border-bottom: 1px solid #21262d; }
    .stTabs [data-baseweb="tab"] { color: #8b949e; font-size: 0.88rem; }
    .stTabs [aria-selected="true"] { color: #58a6ff; border-bottom: 2px solid #58a6ff; }

    /* ── Download button ── */
    .stDownloadButton > button {
        background: #238636;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 8px 18px;
    }
    .stDownloadButton > button:hover { background: #2ea043; }

    /* ── Spinner ── */
    .stSpinner { color: #58a6ff; }

    /* ── File uploader ── */
    [data-testid="stFileUploadDropzone"] {
        background: #161b22;
        border: 2px dashed #30363d;
        border-radius: 10px;
    }
    [data-testid="stFileUploadDropzone"]:hover { border-color: #58a6ff; }

    /* ── Section label pill ── */
    .section-label {
        display: inline-block;
        background: #1f2d3d;
        color: #58a6ff;
        border: 1px solid #2a4a6e;
        border-radius: 4px;
        padding: 2px 10px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    /* ── Status badge ── */
    .badge-success { color: #3fb950; font-weight: 600; }
    .badge-warn    { color: #e3b341; font-weight: 600; }
    .badge-error   { color: #f85149; font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Pydantic Schemas (Day 2 - Structured Outputs) ───────────────────────────

class ColumnSchema(BaseModel):
    name:   str
    dtype:  str
    nulls:  int
    unique: int
    sample: Optional[str] = None

class DatasetProfile(BaseModel):
    rows:    int
    columns: int
    nulls:   int
    col_schema: List[ColumnSchema]

class AnalysisResult(BaseModel):
    question:    str
    tool_used:   Literal["describe", "plot", "correlate", "filter", "stats", "general"]
    code:        str
    output_text: Optional[str] = None
    has_figure:  bool = False
    report:      Optional[str] = None
    timestamp:   str = Field(default_factory=lambda: datetime.now().isoformat())

# ─── Retry Utilities (Day 4) ─────────────────────────────────────────────────

def _backoff(attempt: int, base: float = 1.0, cap: float = 16.0) -> float:
    return min(base * (2 ** attempt), cap) + random.uniform(0, 0.5)

def fetch_live_rates() -> Dict[str, float]:
    """Fetch current USD exchange rates with exponential backoff."""
    mock = {"USD": 1.0, "EUR": 0.92, "GBP": 0.79, "PKR": 279.5, "JPY": 157.4, "CAD": 1.36}

    for attempt in range(3):
        try:
            response = httpx.get(
                "https://api.exchangerate-api.com/v4/latest/USD",
                timeout=10.0,
            )
            if response.status_code == 200:
                data = response.json()
                rates = data.get("rates", {})
                return {k: rates[k] for k in mock if k in rates}
        except Exception:
            import time
            time.sleep(_backoff(attempt))
    return mock

# ─── Dataset Profiler ────────────────────────────────────────────────────────

def profile_dataset(df: pd.DataFrame) -> DatasetProfile:
    cols = []
    for col in df.columns:
        sample_vals = df[col].dropna().head(3).tolist()
        cols.append(ColumnSchema(
            name=col,
            dtype=str(df[col].dtype),
            nulls=int(df[col].isnull().sum()),
            unique=int(df[col].nunique()),
            sample=", ".join(str(v) for v in sample_vals),
        ))
    return DatasetProfile(
        rows=len(df),
        columns=len(df.columns),
        nulls=int(df.isnull().sum().sum()),
        col_schema=cols,
    )

# ─── Tool Registry (Day 3 — Tool Calling Pattern) ───────────────────────────

TOOL_REGISTRY = {
    "describe":  {"keywords": ["describe", "overview", "summary", "info", "profile", "what columns"]},
    "plot":      {"keywords": ["plot", "chart", "graph", "visualise", "visualize", "bar", "line", "scatter", "histogram", "distribution", "trend"]},
    "correlate": {"keywords": ["correlat", "relationship", "heatmap", "between", "depend"]},
    "filter":    {"keywords": ["filter", "where", "rows where", "subset", "select rows", "show only"]},
    "stats":     {"keywords": ["average", "mean", "median", "max", "min", "sum", "count", "total", "statistic", "std"]},
}

def select_tool(question: str) -> str:
    ql = question.lower()
    best, best_score = "general", 0
    for tool_name, info in TOOL_REGISTRY.items():
        score = sum(1 for kw in info["keywords"] if kw in ql)
        if score > best_score:
            best, best_score = tool_name, score
    return best

# ─── Code Generator (Day 1 CoT + Day 3 Tool Calling) ────────────────────────

class CodeGenerator:
    """Generates pandas / plotly code using a chain-of-thought prompt."""

    def __init__(self) -> None:
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            api_key=os.getenv("GROQ_API_KEY"),
        )

    def generate(self, df: pd.DataFrame, question: str, tool_hint: str) -> Tuple[str, Optional[str]]:
        profile_str = self._schema_str(df)

        prompt = ChatPromptTemplate.from_template(
            """You are a senior data scientist. Reason step-by-step, then write the code.

DATASET SCHEMA:
{schema}

FIRST 5 ROWS:
{head}

ANALYSIS TOOL HINT: {tool_hint}

QUESTION: {question}

Step 1 — Understand what columns are relevant.
Step 2 — Choose the right pandas or plotly operation.
Step 3 — Write clean, minimal Python code.

RULES:
- The dataframe is already loaded as the variable `df`.
- Store final textual results in `result` (string or printed output).
- If creating a chart, store the Plotly figure in `fig` and call `fig.write_json('_fig.json')`.
- Use plotly.express or plotly.graph_objects for all charts.
- Do NOT use matplotlib or seaborn.
- Do not use emojis.
- Return ONLY the Python code block, no explanation.

CODE:
"""
        )

        chain = prompt | self.llm | StrOutputParser()
        try:
            raw = chain.invoke({
                "schema":    profile_str,
                "head":      df.head().to_string(),
                "tool_hint": tool_hint,
                "question":  question,
            })
            code = self._clean_code(raw)
            return code, None
        except Exception as exc:
            return "", str(exc)

    @staticmethod
    def _schema_str(df: pd.DataFrame) -> str:
        lines = []
        for col in df.columns:
            lines.append(f"  - {col}: {df[col].dtype} | nulls={df[col].isnull().sum()} | unique={df[col].nunique()}")
        return "\n".join(lines)

    @staticmethod
    def _clean_code(raw: str) -> str:
        """Strip markdown fences if the LLM wraps output."""
        raw = re.sub(r"^```(?:python)?\n?", "", raw.strip(), flags=re.MULTILINE)
        raw = re.sub(r"\n?```$", "", raw.strip())
        return raw.strip()

# ─── Code Executor (subprocess sandbox) ─────────────────────────────────────

class CodeExecutor:
    """Executes generated code in an isolated subprocess."""

    @staticmethod
    def execute(
        code: str, df: pd.DataFrame
    ) -> Tuple[Optional[str], Optional[go.Figure], Optional[str]]:
        """
        Returns (output_text, plotly_fig, error_message).
        Figures are serialised through a temp JSON file.
        """
        fig_path = tempfile.mktemp(suffix=".json")

        preamble = (
            "import pandas as pd\n"
            "import plotly.express as px\n"
            "import plotly.graph_objects as go\n"
            "import numpy as np\n"
            "import json, sys, warnings, io\n"
            "warnings.filterwarnings('ignore')\n"
            f"df = pd.read_json(io.StringIO({json.dumps(df.to_json())}))\n"
            f"_fig_path = {json.dumps(fig_path)}\n\n"
        )

        full_code = preamble + code + "\n"
        full_code += """
if 'fig' in dir():
    import plotly.io as pio
    pio.write_json(fig, _fig_path)
if 'result' in dir():
    print(result)
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as fh:
            fh.write(full_code)
            script = fh.name

        try:
            proc = subprocess.run(
                [sys.executable, script],
                capture_output=True, text=True, timeout=30,
            )
            output  = proc.stdout.strip() or None
            err     = proc.stderr.strip() or None

            if proc.returncode != 0:
                return output, None, err or "Execution failed with non-zero exit."

            fig: Optional[go.Figure] = None
            if os.path.exists(fig_path):
                try:
                    import plotly.io as pio
                    fig = pio.read_json(fig_path)
                except Exception:
                    pass

            return output, fig, None

        except subprocess.TimeoutExpired:
            return None, None, "Execution timed out (30s limit)."
        except Exception as exc:
            return None, None, str(exc)
        finally:
            for path in [script, fig_path]:
                try:
                    os.unlink(path)
                except Exception:
                    pass

# ─── Report Builder (Day 1 CoT) ──────────────────────────────────────────────

class ReportBuilder:
    """Generates a professional narrative from the analysis results."""

    def __init__(self) -> None:
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY"),
        )

    def build(self, df: pd.DataFrame, question: str, output: Optional[str]) -> str:
        prompt = ChatPromptTemplate.from_template(
            """You are a professional financial data analyst.

Think step-by-step:
1. Interpret the analysis output in the context of the question.
2. Identify key findings and anomalies.
3. Frame actionable recommendations.

Dataset: {shape} rows x {cols} columns | Columns: {column_names}
Question: {question}
Analysis Output: {output}

Write a concise professional report in Markdown with:
## Executive Summary
## Key Findings
## Recommendations

Do not use emojis. Keep it under 300 words.
"""
        )
        chain = prompt | self.llm | StrOutputParser()
        try:
            return chain.invoke({
                "shape":        df.shape[0],
                "cols":         df.shape[1],
                "column_names": ", ".join(df.columns.tolist()),
                "question":     question,
                "output":       output or "No textual output produced.",
            })
        except Exception as exc:
            return f"Report generation failed: {exc}"

# ─── Sidebar ─────────────────────────────────────────────────────────────────

def render_sidebar(rates: Dict[str, float]) -> None:
    with st.sidebar:
        st.markdown('<div class="section-label">Live Rates</div>', unsafe_allow_html=True)
        st.markdown("**USD Exchange Rates**")
        for code, rate in rates.items():
            if code != "USD":
                st.markdown(f"1 USD = **{rate:.4f}** {code}")

        st.markdown("---")
        st.markdown('<div class="section-label">About</div>', unsafe_allow_html=True)
        st.markdown(
            "**Financial Data Analysis Agent**  \n"
            "Week 2, Day 5 — CalderR AI Internship  \n\n"
            "Upload any CSV with financial data and ask questions in plain English. "
            "The agent generates, executes, and explains analysis code automatically."
        )
        st.markdown("---")
        st.markdown('<div class="section-label">Week 2 Learning</div>', unsafe_allow_html=True)
        st.markdown(
            "- **Day 1:** Chain-of-thought prompting  \n"
            "- **Day 2:** Pydantic structured output  \n"
            "- **Day 3:** Multi-tool agent pattern  \n"
            "- **Day 4:** External APIs + retry logic  \n"
            "- **Day 5:** Integration and deployment  "
        )

# ─── Main App ────────────────────────────────────────────────────────────────

def main() -> None:
    # Live currency rates (Day 4 — external API with retry)
    if "rates" not in st.session_state:
        st.session_state["rates"] = fetch_live_rates()

    render_sidebar(st.session_state["rates"])

    # Header
    st.markdown("# Financial Data Analysis Agent")
    st.markdown(
        "Upload a CSV file containing financial data. "
        "The agent will profile your dataset, generate analysis code, "
        "execute it safely, and produce a professional report — all from a plain-English question."
    )
    st.markdown("---")

    # ── File Upload ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Step 1 — Upload Data</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Upload a CSV file",
        type=["csv"],
        label_visibility="collapsed",
        help="Supported: any CSV with headers.",
    )

    if uploaded is None:
        st.info("Upload a CSV file to begin. Sample datasets: stock prices, portfolio returns, transaction ledgers, or any tabular financial data.")
        return

    # ── Dataset Profile ──────────────────────────────────────────────────────
    try:
        df = pd.read_csv(uploaded)
    except Exception as exc:
        st.error(f"Could not parse CSV: {exc}")
        return

    profile = profile_dataset(df)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Rows",    f"{profile.rows:,}")
    with col2:
        st.metric("Columns", profile.columns)
    with col3:
        st.metric("Null Cells", f"{profile.nulls:,}")
    with col4:
        numeric_cols = df.select_dtypes(include="number").columns
        st.metric("Numeric Columns", len(numeric_cols))

    st.markdown("---")

    # ── Dataset Preview Tab ──────────────────────────────────────────────────
    tab_preview, tab_schema, tab_stats = st.tabs(["Preview", "Schema", "Descriptive Statistics"])

    with tab_preview:
        st.dataframe(df.head(20), width='stretch', height=320)

    with tab_schema:
        schema_rows = [
            {
                "Column": c.name,
                "Type":   c.dtype,
                "Nulls":  c.nulls,
                "Unique": c.unique,
                "Sample Values": c.sample,
            }
            for c in profile.col_schema
        ]
        st.dataframe(pd.DataFrame(schema_rows), width='stretch')

    with tab_stats:
        try:
            st.dataframe(df.describe(include="all").T, width='stretch')
        except Exception:
            st.warning("Descriptive statistics could not be computed for this dataset.")

    st.markdown("---")

    # ── Question Input ───────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Step 2 — Ask a Question</div>', unsafe_allow_html=True)

    question = st.text_input(
        "Question",
        label_visibility="collapsed",
        placeholder="e.g.  Plot the distribution of the 'Close' column over time.",
        key="user_question",
    )

    col_btn, col_tool = st.columns([2, 3])
    with col_btn:
        analyse = st.button("Run Analysis", type="primary")
    with col_tool:
        if question:
            tool_selected = select_tool(question)
            st.markdown(
                f'Tool selected: <span class="badge-success">{tool_selected}</span>',
                unsafe_allow_html=True,
            )

    if not analyse or not question.strip():
        return

    # ── Analysis Pipeline ────────────────────────────────────────────────────
    with st.spinner("Generating analysis code..."):
        tool_used = select_tool(question)
        gen = CodeGenerator()
        code, gen_err = gen.generate(df, question, tool_used)

    if gen_err or not code:
        st.error(f"Code generation failed: {gen_err or 'No code returned.'}")
        return

    st.markdown("---")
    st.markdown('<div class="section-label">Generated Code</div>', unsafe_allow_html=True)
    st.code(code, language="python")

    with st.spinner("Executing code in sandbox..."):
        executor = CodeExecutor()
        output_text, fig, exec_err = executor.execute(code, df)

    st.markdown("---")
    st.markdown('<div class="section-label">Step 3 — Results</div>', unsafe_allow_html=True)

    if exec_err:
        st.error(f"Execution error: {exec_err}")
        st.warning("The code could not run. Try rephrasing your question or check the generated code above.")

    # Chart
    if fig is not None:
        fig.update_layout(
            paper_bgcolor="#161b22",
            plot_bgcolor="#0d1117",
            font=dict(color="#c9d1d9", size=12),
            margin=dict(t=40, l=20, r=20, b=20),
            xaxis=dict(gridcolor="#21262d", zerolinecolor="#21262d"),
            yaxis=dict(gridcolor="#21262d", zerolinecolor="#21262d"),
        )
        st.plotly_chart(fig, width='stretch')

    # Text output
    if output_text:
        st.markdown("**Analysis Output**")
        st.markdown(f"```\n{output_text}\n```")

    if not fig and not output_text and not exec_err:
        st.info("The code ran without textual output. Check the generated code for print statements.")

    # ── Narrative Report ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-label">Step 4 — Analysis Report</div>', unsafe_allow_html=True)

    with st.spinner("Building narrative report..."):
        builder = ReportBuilder()
        report_text = builder.build(df, question, output_text)

    st.markdown(report_text)

    # ── Structured Result (Pydantic, Day 2) ─────────────────────────────────
    result = AnalysisResult(
        question=question,
        tool_used=tool_used,
        code=code,
        output_text=output_text,
        has_figure=fig is not None,
        report=report_text,
    )

    # ── Downloads ────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-label">Step 5 — Download</div>', unsafe_allow_html=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    d1, d2, d3 = st.columns(3)

    with d1:
        st.download_button(
            label="Download Report (Markdown)",
            data=report_text.encode("utf-8"),
            file_name=f"financial_report_{ts}.md",
            mime="text/markdown",
        )
    with d2:
        st.download_button(
            label="Download Analysis Code",
            data=code.encode("utf-8"),
            file_name=f"analysis_{ts}.py",
            mime="text/plain",
        )
    with d3:
        result_json = result.model_dump_json(indent=2)
        st.download_button(
            label="Download Structured Result (JSON)",
            data=result_json.encode("utf-8"),
            file_name=f"result_{ts}.json",
            mime="application/json",
        )

    # ── Session History ──────────────────────────────────────────────────────
    if "history" not in st.session_state:
        st.session_state["history"] = []
    st.session_state["history"].append(result)

    with st.expander(f"Session History ({len(st.session_state['history'])} analyses)"):
        for i, past in enumerate(reversed(st.session_state["history"]), 1):
            st.markdown(f"**{i}.** {past.question} — *tool: {past.tool_used}*")


if __name__ == "__main__":
    main()
