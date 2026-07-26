# Project 4-P-A: AI-Powered Hiring Pipeline Platform

**Author:** Sohaib Akhlaq  
**Week:** Week 4 Production Project  
**Tech Stack:** Python 3.11 · LangGraph · LangChain · FastAPI · Streamlit · SQLite · Plotly · Pydantic v2  

---

## 🎯 1. Rationale: Why I Chose This Project

The recruitment and hiring process across modern tech enterprises suffers from three major flaws:
1. **Manual Resume Screening Bottlenecks**: HR teams waste hundreds of hours manually scoring candidate qualifications against job descriptions.
2. **Unconscious Demographic & Elitism Bias**: Resumes often trigger age, gender, location, or elitist university biases during initial filtering.
3. **Lack of Governance & Audit Trails**: Fully autonomous AI screeners pose compliance risks if decisions are executed without human oversight or persistent audit trails.

I chose **Project 4-P-A: AI-Powered Hiring Pipeline** because it provides an ideal real-world production testbed for **LangGraph stateful graph orchestration**, **bias detection guardrails**, **Human-in-the-Loop (HITL) manager approval interrupts**, and **durable SQLite persistent audit logging**.

---

## 🛠️ 2. Comprehensive Tech Stack

| Layer | Technology | Purpose / Role |
| :--- | :--- | :--- |
| **Graph Orchestration** | `LangGraph` (`StateGraph`, `MemorySaver`, `interrupt`) | Manages cyclic states, node transitions, bias evaluation, and manager interrupts. |
| **REST API Backend** | `FastAPI` + `Uvicorn` | Exposes enterprise REST endpoints for ingesting candidates and submitting review decisions. |
| **User Interface** | `Streamlit` | Provides HR teams with an interactive web portal, live graph logs, and manager portals. |
| **Data Visualization** | `Plotly Express` | Generates dynamic candidate match score histograms and analytics. |
| **Persistent Storage** | `SQLite` | Stores audit logs, candidate scores, bias flags, and manager review notes. |
| **Validation & Schema** | `Pydantic v2` + `TypedDict` | Enforces strong typing for candidate states and REST request payloads. |

---

## 📋 3. PDF Requirement Mapping & Feature Matrix

Every core requirement specified in the Week 4 internship PDF for Category 2 Production Projects has been implemented:

| PDF Requirement | Implementation Detail | Location in Code |
| :--- | :--- | :--- |
| **Ingest Resumes** | Parses candidate skills, experience years, and full resume text. | `ingest_resume_node()` in `hiring_engine.py` |
| **Score Candidates** | Deterministically scores candidates against target job role requirements (0–100 scale). | `score_candidate_node()` in `hiring_engine.py` |
| **Bias Check Node** | Scans resume text for age, gender, location, and elitism bias keywords. | `bias_check_node()` in `hiring_engine.py` |
| **Generate Interview Questions** | Customizes technical and behavioral interview questions for shortlisted applicants. | `generate_questions_node()` in `hiring_engine.py` |
| **Human Review (HITL)** | Pauses graph execution at shortlisted resumes via `interrupt()`; resumes via `Command(resume=...)`. | `human_review_node()` in `hiring_engine.py` |
| **Hiring Decision & Audit** | Records final hire/reject status and manager notes to persistent SQLite table. | `final_hire_node()` & `_save_to_sqlite()` |
| **FastAPI + SQLite** | Provides full REST API with `/api/candidates/ingest` and `/api/candidates/review`. | `app_api.py` & `hiring_pipeline_audit.db` |

---

## 📐 4. LangGraph System Architecture

```
[Ingest Resume] ──> [Score Candidate] ──> [Bias Check Node] ──(Conditional Router)
                                                                    ├── Shortlisted ──> [Generate Questions] ──> [HITL Human Review]
                                                                    │                                                      ├── Approved ──> [Final Hire] ──> [SQLite Export] ──> END
                                                                    │                                                      └── Rejected ──> [Final Reject] ─> [SQLite Export] ──> END
                                                                    └── Not Shortlisted ───────────────────────────────> [Final Reject] ─> [SQLite Export] ──> END
```

---

## 🛡️ 5. Error Flows & Edge Cases Handled

1. **Unhandled Schema Fields & Null Inputs**: Handled via Pydantic schema validation and default fallbacks in `CandidateState`.
2. **SQLite Concurrent Locks**: Uses dedicated connection lifecycles (`conn.close()` after transactions) to prevent database file locking.
3. **Interrupt Desynchronization**: Isolates each candidate workflow using a unique `thread_id` (`thread_CAND-XXX`), ensuring concurrent reviews do not overwrite each other.
4. **Accessible Theme Contrast**: Restructured custom CSS to dynamically adapt to both Streamlit Dark Mode and Light Mode without low-contrast text artifacts.

---

## 🏛️ 6. System Design Principles Applied

- **Separation of Concerns**: Core LangGraph logic is strictly decoupled in `hiring_engine.py`, serving both `app_streamlit.py` and `app_api.py`.
- **State Immutability & Traceability**: Node state updates strictly yield dict patches, while audit logs concatenate chronologically.
- **Fail-Safe Governance**: High-scoring candidates cannot bypass human review; the graph enforces a mandatory interrupt breakpoint.

---

## 🚀 7. Future Scalability Roadmap

1. **Vector-Based Semantic Resume Parsing**: Integrate ChromaDB or Pinecone for semantic similarity matching beyond keyword scoring.
2. **Distributed Queue Processing**: Replace SQLite checkpointer with Redis or Postgres `SqliteSaver` / `PostgresSaver` for enterprise scale.
3. **Multi-Model LLM Guardrails**: Add LLM-as-a-judge nodes to review generated interview questions for clarity and relevance.

---

## 💡 8. Challenges Faced & Solutions

| Challenge | Root Cause | Solution |
| :--- | :--- | :--- |
| **Theme Color Mismatch** | Custom hardcoded hex values caused white text on white cards in dark mode. | Removed static card backgrounds and used native Streamlit containers with adaptive standard colors. |
| **State Loss Across REST Calls** | Re-instantiating state graphs erased in-memory threads across HTTP requests. | Used global compiled state graph with thread-bound `MemorySaver` checkpointing. |
| **Pydantic V2 Deprecation Warnings** | Legacy `Field(..., example=...)` usage in FastAPI models. | Replaced deprecated kwargs with updated Pydantic V2 syntax. |

---

## 🏃 How to Run

### Streamlit UI Mode:
```powershell
calderr-env\Scripts\python.exe -m streamlit run "Week 4/production_project/app_streamlit.py"
```

### FastAPI REST API Mode:
```powershell
calderr-env\Scripts\python.exe "Week 4/production_project/app_api.py"
```
