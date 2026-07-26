# Project 4-I-B: Customer Onboarding Agent (LangGraph Intermediate Project)

**Author:** Sohaib Akhlaq  
**Week:** Week 4 Intermediate Project  
**Tech Stack:** Python 3.11 · LangGraph · Streamlit · MemorySaver / SqliteSaver

---

## 📌 Project Overview

The **Customer Onboarding Agent** is an enterprise-grade agentic workflow built using **LangGraph**. It automates multi-step customer onboarding while enforcing governance through **Human-in-the-Loop (HITL)** approval breakpoints for high-value Enterprise accounts.

### **Core Capabilities**
1. **Multi-Stage Graph Execution**: Collect info → Validate data → Route account → Generate Account ID → Send Welcome Package → Schedule CS Check-in.
2. **Conditional Routing**: Automatically routes standard accounts to immediate auto-approval, while Enterprise VIP accounts (ARR ≥ $10,000) are routed to a human review interrupt.
3. **Human-in-the-Loop Interrupts**: Uses native LangGraph `interrupt()` and `Command(resume=...)` to pause graph execution and wait for human manager approval.
4. **State Persistence**: Preserves complete state checkpoints across sessions using `MemorySaver`.
5. **Interactive Streamlit UI**: Fully responsive web app for initiating onboarding, reviewing pending interrupts, and inspecting persistent audit trails.

---

## 📐 Graph Architecture Diagram

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
                │  Auto Approve  │        │ HITL Interrupt│ (Pauses Execution)
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

## 🚀 How to Run the Project

### **Option 1: Streamlit Web UI Mode (Recommended)**

Run the following command in PowerShell inside `calderr-env`:

```powershell
cd C:\Users\USER\Desktop\calderr-ai-2026
.\calderr-env\Scripts\python.exe -m streamlit run "Week 4/intermediate_project/project4_i_b_customer_onboarding.py"
```

1. Open your browser at `http://localhost:8501`.
2. Select a **Sample Customer Profile** from the sidebar dropdown (e.g. `Enterprise VIP`).
3. Click **Start Onboarding Workflow**.
4. Observe the **Workflow Execution Dashboard**. If an Enterprise account is submitted, execution will pause at the **HITL Approval Breakpoint**.
5. Click **Approve Enterprise Account** or **Reject Account** to resume the graph to completion.

---

## 🧪 Verification & Sample Test Cases

| Test Case | Inputs | Expected Behavior |
| :--- | :--- | :--- |
| **Test Case 1: Standard Account** | Acme Widgets Corp, ARR $4,500 | Auto-approved immediately; Account number generated (`ACC-XXXXXX`). |
| **Test Case 2: Enterprise VIP** | Apex Global Enterprise, ARR $25,000 | Execution pauses at `human_review_node`; awaits UI approval. |
| **Test Case 3: Invalid Payload** | Email: `invalid_format`, ARR: -$100 | Fails validation; routes directly to `rejection_notice_node`. |

---

## 🛠️ Week 4 Concepts Applied

- **TypedDict State Schema**: `OnboardingState` explicitly tracks customer data, approval status, and audit logs.
- **Annotated Reducers**: `audit_logs` uses list concatenation reducer `lambda a, b: a + b` to accumulate workflow logs.
- **Conditional Edges**: Dynamic routing function `route_after_validation` selects between standard auto-approval, HITL interrupt, or failure handling.
- **State Checkpointing**: `MemorySaver` preserves thread checkpoints via unique `thread_id`.
