# Project 4-I-B: Customer Onboarding Agent

**Author:** Sohaib Akhlaq  
**Week:** Week 4 Intermediate Project  
**Tech Stack:** Python 3.11 · LangGraph · Streamlit · MemorySaver / SqliteSaver  

---

## 🎯 1. Rationale: Why I Chose This Project

Enterprise customer onboarding requires multi-step coordination across data validation, account creation, welcome package dispatching, and follow-up scheduling. 

Standard accounts can be auto-approved, but high-value Enterprise VIP accounts (ARR ≥ $10,000) carry significant financial and SLA risks that necessitate mandatory human authorization.

I chose **Project 4-I-B: Customer Onboarding Agent** to demonstrate how **LangGraph** can seamlessly combine automated background pipelines with **Human-in-the-Loop (HITL)** approval breakpoints in an intuitive web portal.

---

## 🛠️ 2. Comprehensive Tech Stack

- **Graph Engine**: `LangGraph` (`StateGraph`, `MemorySaver`, `interrupt`, `Command`)
- **Frontend Framework**: `Streamlit` (Interactive onboarding portal & manager review panel)
- **Data Model**: Python `TypedDict` schema with custom reducer annotations
- **Runtime Environment**: Python 3.11 (`calderr-env`)

---

## 📋 3. PDF Requirement Mapping

| PDF Requirement | Implementation Detail | Location in Code |
| :--- | :--- | :--- |
| **Collect Info** | Ingests company name, email, ARR, and target tier. | `collect_info_node()` |
| **Validate Info** | Validates email syntax, company length, and ARR bounds. | `validate_info_node()` |
| **Routing Gate** | Standard tier auto-approved; VIP routed to HITL interrupt. | `route_after_validation()` |
| **Human Review (HITL)** | Interrupts graph for manager decision (`approved` / `rejected`). | `human_review_node()` |
| **Create Account & Notify** | Generates account ID (`ACC-XXXXXX`), sends welcome notice, schedules check-in. | `create_account_node()`, `send_welcome_node()`, `schedule_followup_node()` |

---

## 📐 4. LangGraph Workflow Architecture

```
                             ┌────────────────┐
                             │  Collect Info  │
                             └───────┬────────┘
                                     │
                             ┌───────▼────────┐
                             │ Validate Info  │
                             └───────┬────────┘
                                     │
                           (Conditional Router)
                            /                 \
        [Standard Tier / Low ARR]          [Enterprise VIP / High ARR]
                          /                     \
                ┌────────▼───────┐        ┌──────▼────────┐
                │  Auto Approve  │        │ HITL Interrupt│ (Pauses Graph)
                └────────┬───────┘        └──────┬────────┘
                         │                       │
                         │               [Manager Decision]
                         │                /              \
                         │           (Approved)       (Rejected)
                         │              /                  \
                         ┌─────────────▼──┐             ┌───▼──────────────┐
                         │ Create Account │             │ Rejection Notice │
                         └─────────────┬──┘             └───┬──────────────┘
                                       │                    │
                         ┌─────────────▼──┐                 ▼
                         │  Send Welcome  │                END
                         └─────────────┬──┘
                                       │
                         ┌─────────────▼──┐
                         │Schedule Checkin│
                         └─────────────┬──┘
                                       │
                                       ▼
                                      END
```

---

## 🛡️ 5. Error Flows & System Design Principles

- **Validation Error Handling**: Invalid emails or negative ARR inputs immediately route the graph to `rejection_notice_node` without attempting account creation.
- **State Isolation**: Each customer submission runs on an isolated `thread_id` to prevent session data collision.
- **Accessible UI Design**: Theme colors adapt seamlessly to dark mode and light mode without low-contrast text artifacts.

---

## 💡 6. Challenges Faced & Solutions

| Challenge | Solution |
| :--- | :--- |
| **Handling Streamlit Reruns on Resumption** | Used `st.session_state` thread tracking to reload snapshots cleanly after calling `graph.invoke(Command(resume=...))`. |
| **Contrast Visibility on Metric Cards** | Removed hardcoded background cards and used transparent border containers. |

---

## 🏃 How to Run

```powershell
calderr-env\Scripts\python.exe -m streamlit run "Week 4/intermediate_project/project4_i_b_customer_onboarding.py"
```
