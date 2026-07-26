# Project 4-P-A: AI-Powered Hiring Pipeline Platform

**Author:** Sohaib Akhlaq  
**Week:** Week 4 Production Project  
**Tech Stack:** Python 3.11 · LangGraph · FastAPI · Streamlit · SQLite · Pydantic v2 · Docker

---

## 📌 Project Overview

The **AI-Powered Hiring Pipeline Platform** is a production-grade hiring and resume evaluation engine engineered using **LangGraph**, **FastAPI**, **Streamlit**, and **SQLite**.

It automates end-to-end recruitment workflows with enterprise governance:
1. **Resume Ingestion**: Ingests candidate profiles and skill matrices.
2. **AI Match Scoring**: Evaluates candidate qualifications against target job role requirements.
3. **Bias Detection Node**: Scans candidate resumes for potential demographic, age, gender, location, or elitism bias indicators.
4. **Tailored Question Generation**: Dynamically creates technical and behavioral interview questions for shortlisted candidates.
5. **Human-in-the-Loop (HITL) Interrupts**: Halts execution at the HR review breakpoint for manager approval.
6. **SQLite Persistent Audit Trail**: Writes full execution records, scores, bias flags, and manager notes to a durable SQLite database.

---

## 📐 Graph Architecture Diagram

```
[Ingest Resume] ──> [Score Candidate] ──> [Bias Check Node] ──(Conditional Router)
                                                                    ├── Shortlisted ──> [Generate Questions] ──> [HITL Human Review]
                                                                    │                                                  ├── Approved ──> [Final Hire] ──> [SQLite Export] ──> END
                                                                    │                                                  └── Rejected ──> [Final Reject] ─> [SQLite Export] ──> END
                                                                    └── Not Shortlisted ───────────────────────────────> [Final Reject] ─> [SQLite Export] ──> END
```

---

## 🚀 Deployment & How to Run

### **Option 1: Streamlit Dashboard UI Mode (Recommended)**

```powershell
cd C:\Users\USER\Desktop\calderr-ai-2026
.\calderr-env\Scripts\python.exe -m streamlit run "Week 4/production_project/app_streamlit.py"
```

Open `http://localhost:8501` to access the 4-tab interactive HR portal:
- **Ingest Candidate**: Test with 10 benchmark resumes or enter custom resumes.
- **HR Approval Portal**: View pending interrupted threads and approve/reject candidates.
- **Pipeline Audit Analytics**: Interactive Plotly score distributions and full audit table.
- **Graph Architecture**: Visual architecture diagram.

### **Option 2: FastAPI REST API Mode**

```powershell
cd C:\Users\USER\Desktop\calderr-ai-2026
.\calderr-env\Scripts\python.exe "Week 4/production_project/app_api.py"
```

Open `http://localhost:8000/docs` to view the interactive OpenAPI documentation:
- `POST /api/candidates/ingest`: Ingest candidate and trigger graph.
- `POST /api/candidates/review`: Resume interrupted graph with human review decision.
- `GET /api/audit-logs`: Fetch SQLite audit records.

---

## 🧪 Verification & Benchmark Results

Included with the system are **10 Benchmark Resumes** covering edge cases:
- High match score candidates (e.g. `Sohaib Akhlaq`, `Marcus Vance`).
- Low match score candidates (e.g. `James O'Connor`).
- Candidates triggering bias detection flags (e.g. `David Miller`, `Elena Rostova`, `Robert Chen`).

All outcomes are logged into `hiring_pipeline_audit.db`.
