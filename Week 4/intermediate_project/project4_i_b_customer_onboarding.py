"""
Project 4-I-B: Customer Onboarding Agent (Streamlit & CLI Interface)
Week 4 Intermediate Project - LangGraph Orchestration & HITL Workflow

Architecture:
  [Collect Info] -> [Validate Info] -> Conditional Router:
                                        ├── Standard (Auto-Approve) ──> [Create Account] -> [Send Welcome] -> [Schedule Follow-up]
                                        └── Large/VIP (HITL Interrupted) ──> [Human Review Interrupt]
                                                                                  ├── Approved ──> [Create Account] -> [Send Welcome] -> [Schedule Follow-up]
                                                                                  └── Rejected ──> [Rejection Notice] -> END
"""

import os
import time
from typing import Annotated, List, Literal, TypedDict
import streamlit as st

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Command, interrupt


# ---------------------------------------------------------------------------
# State Schema
# ---------------------------------------------------------------------------

class OnboardingState(TypedDict):
    """TypedDict state schema for Customer Onboarding Workflow."""
    customer_id: str
    company_name: str
    contact_email: str
    account_tier: Literal["Standard", "Enterprise VIP"]
    monthly_arr: float
    validation_status: Literal["pending", "passed", "failed"]
    validation_errors: List[str]
    human_approval_required: bool
    human_decision: Literal["pending", "approved", "rejected"]
    human_notes: str
    account_created: bool
    account_number: str
    welcome_email_sent: bool
    follow_up_scheduled: bool
    is_complete: bool
    audit_logs: Annotated[List[str], lambda a, b: a + b]
    messages: Annotated[List[dict], add_messages]


# ---------------------------------------------------------------------------
# Node Functions
# ---------------------------------------------------------------------------

def collect_info_node(state: OnboardingState) -> dict:
    """Ingest customer onboarding payload and log registration."""
    log_msg = f"Collected registration info for '{state['company_name']}' (Tier: {state['account_tier']}, ARR: ${state['monthly_arr']:,.2f})."
    return {
        "audit_logs": [log_msg],
        "messages": [{"role": "system", "content": log_msg}]
    }


def validate_info_node(state: OnboardingState) -> dict:
    """Validate customer data payload for completeness and tier thresholds."""
    errors = []
    if "@" not in state.get("contact_email", ""):
        errors.append("Invalid email address format.")
    if len(state.get("company_name", "")) < 2:
        errors.append("Company name too short.")
    if state.get("monthly_arr", 0) < 0:
        errors.append("Monthly ARR cannot be negative.")

    status = "failed" if errors else "passed"
    is_large_account = state.get("account_tier") == "Enterprise VIP" or state.get("monthly_arr", 0) >= 10000.0
    
    log_msg = f"Validation result: {status.upper()}. Errors: {errors if errors else 'None'}. HITL Gate: {is_large_account}."
    
    return {
        "validation_status": status,
        "validation_errors": errors,
        "human_approval_required": is_large_account,
        "audit_logs": [log_msg],
        "messages": [{"role": "system", "content": log_msg}]
    }


def auto_approve_node(state: OnboardingState) -> dict:
    """Auto-approve standard accounts."""
    log_msg = f"Standard tier auto-approved for '{state['company_name']}'."
    return {
        "human_decision": "approved",
        "audit_logs": [log_msg],
        "messages": [{"role": "system", "content": log_msg}]
    }


def human_review_node(state: OnboardingState) -> dict:
    """
    Human Review Interrupt Node for Large/VIP accounts.
    Pauses graph execution and requests human decision input.
    """
    # LangGraph explicit interrupt
    human_input = interrupt({
        "instruction": f"Enterprise VIP Approval Required for '{state['company_name']}' (ARR: ${state['monthly_arr']:,.2f}).",
        "company_name": state["company_name"],
        "monthly_arr": state["monthly_arr"],
        "customer_id": state["customer_id"]
    })

    decision = human_input.get("decision", "rejected")
    notes = human_input.get("notes", "No notes provided.")

    log_msg = f"Human Review completed. Decision: {decision.upper()}. Reviewer Notes: '{notes}'."
    
    return {
        "human_decision": decision,
        "human_notes": notes,
        "audit_logs": [log_msg],
        "messages": [{"role": "human", "content": log_msg}]
    }


def create_account_node(state: OnboardingState) -> dict:
    """Generate official customer account number."""
    account_num = f"ACC-{abs(hash(state['customer_id'])) % 1000000:06d}"
    log_msg = f"Account successfully created: {account_num}."
    return {
        "account_created": True,
        "account_number": account_num,
        "audit_logs": [log_msg],
        "messages": [{"role": "system", "content": log_msg}]
    }


def send_welcome_node(state: OnboardingState) -> dict:
    """Simulate dispatching personalized welcome package."""
    log_msg = f"Personalized welcome onboarding package dispatched to '{state['contact_email']}'."
    return {
        "welcome_email_sent": True,
        "audit_logs": [log_msg],
        "messages": [{"role": "system", "content": log_msg}]
    }


def schedule_followup_node(state: OnboardingState) -> dict:
    """Schedule dedicated Customer Success follow-up call."""
    log_msg = "30-Day Customer Success Onboarding Check-in call scheduled."
    return {
        "follow_up_scheduled": True,
        "is_complete": True,
        "audit_logs": [log_msg],
        "messages": [{"role": "system", "content": log_msg}]
    }


def rejection_notice_node(state: OnboardingState) -> dict:
    """Handle account rejection notification."""
    log_msg = f"Rejection notice dispatched to '{state['company_name']}'. Reason: Failed validation or Human Review rejection."
    return {
        "is_complete": True,
        "audit_logs": [log_msg],
        "messages": [{"role": "system", "content": log_msg}]
    }


# ---------------------------------------------------------------------------
# Routing Functions
# ---------------------------------------------------------------------------

def route_after_validation(state: OnboardingState) -> str:
    """Route after validation based on validation status and account size."""
    if state["validation_status"] == "failed":
        return "rejection_notice"
    if state["human_approval_required"]:
        return "human_review"
    return "auto_approve"


def route_after_approval(state: OnboardingState) -> str:
    """Route after human review evaluation."""
    if state["human_decision"] == "approved":
        return "create_account"
    return "rejection_notice"


# ---------------------------------------------------------------------------
# Graph Builder
# ---------------------------------------------------------------------------

@st.cache_resource
def get_compiled_graph():
    """Build and compile the Customer Onboarding StateGraph."""
    builder = StateGraph(OnboardingState)

    builder.add_node("collect_info", collect_info_node)
    builder.add_node("validate_info", validate_info_node)
    builder.add_node("auto_approve", auto_approve_node)
    builder.add_node("human_review", human_review_node)
    builder.add_node("create_account", create_account_node)
    builder.add_node("send_welcome", send_welcome_node)
    builder.add_node("schedule_followup", schedule_followup_node)
    builder.add_node("rejection_notice", rejection_notice_node)

    builder.set_entry_point("collect_info")
    builder.add_edge("collect_info", "validate_info")

    builder.add_conditional_edges(
        "validate_info",
        route_after_validation,
        {
            "rejection_notice": "rejection_notice",
            "human_review": "human_review",
            "auto_approve": "auto_approve"
        }
    )

    builder.add_conditional_edges(
        "human_review",
        route_after_approval,
        {
            "create_account": "create_account",
            "rejection_notice": "rejection_notice"
        }
    )

    builder.add_edge("auto_approve", "create_account")
    builder.add_edge("create_account", "send_welcome")
    builder.add_edge("send_welcome", "schedule_followup")
    builder.add_edge("schedule_followup", END)
    builder.add_edge("rejection_notice", END)

    memory = InMemorySaver()
    return builder.compile(checkpointer=memory)


# ---------------------------------------------------------------------------
# Streamlit Web Application Interface
# ---------------------------------------------------------------------------

def run_streamlit_ui():
    st.set_page_config(
        page_title="Customer Onboarding Agent | LangGraph",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
        <style>
        .main-header { font-size: 2.2rem; color: #4F46E5; font-weight: 700; }
        .sub-header { font-size: 1.1rem; color: #6B7280; margin-bottom: 20px; }
        .stButton>button { width: 100%; background-color: #4F46E5; color: white; font-weight: 600; border-radius: 8px; }
        .card { background-color: #F9FAFB; padding: 20px; border-radius: 10px; border: 1px solid #E5E7EB; margin-bottom: 15px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-header">🚀 Customer Onboarding Agent Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Week 4 Project 4-I-B: LangGraph Stateful Orchestration with Human-in-the-Loop Interrupts</div>', unsafe_allow_html=True)

    graph = get_compiled_graph()

    # Session State Initialization
    if "current_thread_id" not in st.session_state:
        st.session_state.current_thread_id = "thread_cust_001"
    if "workflow_interrupted" not in st.session_state:
        st.session_state.workflow_interrupted = False
    if "interrupted_payload" not in st.session_state:
        st.session_state.interrupted_payload = {}

    sidebar = st.sidebar
    sidebar.header("📋 Workflow Configuration")
    preset = sidebar.selectbox(
        "Load Sample Customer Profile",
        ["Custom Input", "Standard Account (Auto-Approve)", "Enterprise VIP (Triggers Human Review)", "Invalid Account (Validation Fail)"]
    )

    if preset == "Standard Account (Auto-Approve)":
        default_company = "Acme Widgets Corp"
        default_email = "onboarding@acme.com"
        default_tier = "Standard"
        default_arr = 4500.0
    elif preset == "Enterprise VIP (Triggers Human Review)":
        default_company = "Apex Global Enterprise"
        default_email = "vip@apexglobal.com"
        default_tier = "Enterprise VIP"
        default_arr = 25000.0
    elif preset == "Invalid Account (Validation Fail)":
        default_company = "X"
        default_email = "invalid_email_at_domain"
        default_tier = "Standard"
        default_arr = -100.0
    else:
        default_company = "TechStart Solutions"
        default_email = "contact@techstart.io"
        default_tier = "Enterprise VIP"
        default_arr = 12500.0

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📝 Customer Registration Form")
        with st.form("onboarding_form"):
            customer_id = st.text_input("Customer ID", value="CUST-88392")
            company_name = st.text_input("Company Name", value=default_company)
            contact_email = st.text_input("Contact Email", value=default_email)
            account_tier = st.selectbox("Account Tier", ["Standard", "Enterprise VIP"], index=0 if default_tier == "Standard" else 1)
            monthly_arr = st.number_input("Monthly ARR ($)", value=default_arr, step=500.0)

            submit_btn = st.form_submit_button("Start Onboarding Workflow")

        if submit_btn:
            thread_id = f"thread_{customer_id}_{int(time.time())}"
            st.session_state.current_thread_id = thread_id
            st.session_state.workflow_interrupted = False

            init_state: OnboardingState = {
                "customer_id": customer_id,
                "company_name": company_name,
                "contact_email": contact_email,
                "account_tier": account_tier,
                "monthly_arr": monthly_arr,
                "validation_status": "pending",
                "validation_errors": [],
                "human_approval_required": False,
                "human_decision": "pending",
                "human_notes": "",
                "account_created": False,
                "account_number": "",
                "welcome_email_sent": False,
                "follow_up_scheduled": False,
                "is_complete": False,
                "audit_logs": [],
                "messages": []
            }

            config = {"configurable": {"thread_id": thread_id}}
            graph.invoke(init_state, config)

            # Check snapshot after execution attempt
            snapshot = graph.get_state(config)
            if snapshot.next and "human_review" in snapshot.next:
                st.session_state.workflow_interrupted = True
                st.session_state.interrupted_payload = snapshot.tasks[0].interrupts[0].value
                st.warning("⚠️ Workflow Interrupted! Human Manager Approval Required for Enterprise Account.")
            else:
                st.success("✅ Onboarding Workflow Completed Successfully!")

    with col2:
        st.markdown("### 📊 Workflow Execution & Audit Dashboard")
        config = {"configurable": {"thread_id": st.session_state.current_thread_id}}
        snapshot = graph.get_state(config)

        if snapshot and snapshot.values:
            curr_state = snapshot.values
            
            # Key Metrics Display
            m1, m2, m3 = st.columns(3)
            m1.metric("Validation", curr_state.get("validation_status", "pending").upper())
            m2.metric("Human Approval", curr_state.get("human_decision", "pending").upper())
            m3.metric("Account No", curr_state.get("account_number", "N/A"))

            # Audit Trail Display
            st.markdown("#### 📜 Persistent Audit Trail")
            for idx, log in enumerate(curr_state.get("audit_logs", []), 1):
                st.info(f"**Step {idx}:** {log}")

            # Human-in-the-Loop Management Interface
            if snapshot.next and "human_review" in snapshot.next:
                st.markdown("---")
                st.error("🛑 **HUMAN APPROVAL BREAKPOINT DETECTED**")
                st.write(f"**Company:** {curr_state.get('company_name')}")
                st.write(f"**Monthly ARR:** ${curr_state.get('monthly_arr', 0):,.2f}")
                st.write(f"**Tier:** {curr_state.get('account_tier')}")

                review_notes = st.text_area("Reviewer Rationale / Notes", value="Approved based on Enterprise contract terms.")
                
                c_app, c_rej = st.columns(2)
                if c_app.button("✅ Approve Enterprise Account"):
                    graph.invoke(Command(resume={"decision": "approved", "notes": review_notes}), config)
                    st.session_state.workflow_interrupted = False
                    st.rerun()

                if c_rej.button("❌ Reject Account"):
                    graph.invoke(Command(resume={"decision": "rejected", "notes": review_notes}), config)
                    st.session_state.workflow_interrupted = False
                    st.rerun()
        else:
            st.info("Submit the customer registration form to initiate the LangGraph workflow.")

    # Architecture Diagram Footer
    st.markdown("---")
    st.markdown("### 📐 LangGraph Workflow Architecture")
    st.code("""
    [Collect Info] ──> [Validate Info] ──(Conditional Router)
                                              ├── Standard ──> [Auto Approve] ──┐
                                              └── Large/VIP ─> [HITL Interrupt] ┼──> [Create Account] ──> [Send Welcome] ──> [Schedule Follow-up] ──> END
                                                                    └── Rejected ──> [Rejection Notice] ──> END
    """, language="text")


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_streamlit_ui()
