"""
Week 4 - Day 2: Lab 4.2 - Self-Correcting Agent Loop

Implements a generate -> validate -> respond/regenerate loop with bounded retries.
Uses conditional edge routing for dynamic decision-making within the LangGraph.

Key patterns demonstrated:
  - Conditional edges (if-else routing based on validation result)
  - Bounded retry loop (max 3 attempts with counter tracking)
  - Classification router for query type detection
  - Self-correction via iterative improvement with feedback

Usage:
    python "Week 4/lab4.2_self_correcting_loop.py"
"""

import os
import json
import re
from typing import TypedDict, List, Annotated

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_ATTEMPTS = 3
MODEL = "llama-3.1-8b-instant"
GENERATION_TEMPERATURE = 0.3
VALIDATION_TEMPERATURE = 0.0


# ---------------------------------------------------------------------------
# State Schema
# ---------------------------------------------------------------------------

class AgentLoopState(TypedDict):
    """State for the self-correcting agent loop with bounded retries."""

    user_input: str
    task_description: str

    classification: str
    response: str
    validation_result: str
    attempts: int
    max_attempts: int
    is_success: bool

    messages: Annotated[List, add_messages]


# ---------------------------------------------------------------------------
# LLM Helpers
# ---------------------------------------------------------------------------

def _get_llm(temperature: float = GENERATION_TEMPERATURE) -> ChatGroq:
    """Return a configured Groq LLM instance."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY not found in environment. "
            "Add it to a .env file or set the environment variable."
        )
    return ChatGroq(model=MODEL, temperature=temperature, api_key=api_key)


# ---------------------------------------------------------------------------
# Graph Node Functions
# ---------------------------------------------------------------------------

def generate_response(state: AgentLoopState) -> dict:
    """Node 1: Generate an initial response using the LLM."""
    current_attempt = state.get("attempts", 0) + 1
    print(f"[GENERATE] Attempt {current_attempt}/{MAX_ATTEMPTS}")

    llm = _get_llm()

    prompt = ChatPromptTemplate.from_template(
        "You are a helpful AI assistant. Provide a clear, accurate response.\n\n"
        "Task: {task}\n\n"
        "Response must be:\n"
        "1. Accurate and factual\n"
        "2. Clear and well-structured\n"
        "3. Directly answers the question\n\n"
        "Previous attempts (if any):\n{history}\n\n"
        "Response:"
    )

    chain = prompt | llm | StrOutputParser()

    history = ""
    for msg in state.get("messages", [])[-6:]:
        if hasattr(msg, "content"):
            history += f"{msg.content}\n"

    try:
        response = chain.invoke({
            "task": state["task_description"],
            "history": history,
        })
        print(f"[GENERATE] Response generated ({len(response)} characters)")
    except Exception as exc:
        print(f"[GENERATE] Failed: {exc}")
        response = f"Error during generation: {exc}"

    return {
        "response": response,
        "attempts": current_attempt,
        "messages": [
            SystemMessage(
                content=f"Generated response (attempt {current_attempt})"
            )
        ],
    }


def validate_response(state: AgentLoopState) -> dict:
    """Node 2: Validate the generated response for quality metrics."""
    response = state.get("response", "")
    task = state.get("task_description", "")

    print(f"[VALIDATE] Checking response quality ...")

    if not response or len(response.strip()) < 10:
        print(f"[VALIDATE] Response too short ({len(response.strip())} chars)")
        return {
            "is_success": False,
            "validation_result": "Response too short (minimum 10 characters)",
            "messages": [
                SystemMessage(content="Validation failed: response too short")
            ],
        }

    try:
        llm = _get_llm(temperature=VALIDATION_TEMPERATURE)

        validation_prompt = ChatPromptTemplate.from_template(
            "You are a response validator. Evaluate whether the response "
            "correctly answers the task.\n\n"
            "Task: {task}\n\n"
            "Response:\n{response}\n\n"
            "Evaluate on:\n"
            "1. Accuracy: Does it correctly answer the question? (0-10)\n"
            "2. Completeness: Does it cover all aspects? (0-10)\n"
            "3. Clarity: Is it clear and well-structured? (0-10)\n\n"
            "Respond ONLY with a JSON object:\n"
            '{{"accuracy": 0-10, "completeness": 0-10, "clarity": 0-10, '
            '"pass": true/false, "reason": "brief explanation"}}'
        )

        chain = validation_prompt | llm | StrOutputParser()
        result = chain.invoke({"task": task, "response": response})

        json_match = re.search(r"\{.*\}", result, re.DOTALL)
        if not json_match:
            print("[VALIDATE] Could not parse validation result")
            return {
                "is_success": False,
                "validation_result": "Validation parsing failed",
                "messages": [
                    SystemMessage(content="Validation parsing failed")
                ],
            }

        data = json.loads(json_match.group())
        is_success = data.get("pass", False)
        reason = data.get("reason", "No reason provided")
        accuracy = data.get("accuracy", 0)
        completeness = data.get("completeness", 0)
        clarity = data.get("clarity", 0)

        print(f"  Accuracy: {accuracy}/10")
        print(f"  Completeness: {completeness}/10")
        print(f"  Clarity: {clarity}/10")
        print(f"  Pass: {is_success}")
        if not is_success:
            print(f"  Reason: {reason}")

        summary = (
            f"Accuracy: {accuracy}, Completeness: {completeness}, "
            f"Clarity: {clarity} - {reason}"
        )

        return {
            "is_success": is_success,
            "validation_result": summary,
            "messages": [
                SystemMessage(
                    content=f"Validation: {'PASS' if is_success else 'FAIL'} - {reason}"
                )
            ],
        }

    except Exception as exc:
        print(f"[VALIDATE] Error: {exc}")
        return {
            "is_success": False,
            "validation_result": f"Validation error: {exc}",
            "messages": [
                SystemMessage(content=f"Validation error: {exc}")
            ],
        }


def regenerate_response(state: AgentLoopState) -> dict:
    """Node 3: Generate an improved response based on validation feedback."""
    print(f"[REGENERATE] Improving response (attempt {state.get('attempts', 0) + 1})")

    llm = _get_llm()

    prompt = ChatPromptTemplate.from_template(
        "You are a helpful AI assistant. Your previous response was not "
        "good enough.\n\n"
        "Task: {task}\n\n"
        "Previous Response:\n{response}\n\n"
        "Validation Feedback:\n{validation}\n\n"
        "Improve your response by addressing the feedback. Make it:\n"
        "1. More accurate and factual\n"
        "2. More complete\n"
        "3. Clearer and better structured\n\n"
        "Improved Response:"
    )

    chain = prompt | llm | StrOutputParser()

    try:
        response = chain.invoke({
            "task": state["task_description"],
            "response": state.get("response", ""),
            "validation": state.get(
                "validation_result", "Quality needs improvement"
            ),
        })
        print(f"[REGENERATE] Improved response ({len(response)} characters)")
    except Exception as exc:
        print(f"[REGENERATE] Failed: {exc}")
        response = f"Error during regeneration: {exc}"

    return {
        "response": response,
        "messages": [
            SystemMessage(
                content=f"Regenerated response (attempt {state.get('attempts', 0) + 1})"
            )
        ],
    }


def respond(state: AgentLoopState) -> dict:
    """Node 4: Deliver the final successful response."""
    print(f"[RESPOND] Returning successful response after {state.get('attempts', 0)} attempt(s)")
    return {
        "messages": [
            SystemMessage(
                content=f"Response delivered after {state.get('attempts', 0)} attempt(s)"
            )
        ],
    }


def handle_max_attempts(state: AgentLoopState) -> dict:
    """Node 5: Fallback handler when maximum retry count is reached."""
    print(f"[MAX_ATTEMPTS] Reached limit of {MAX_ATTEMPTS} attempts")
    last = state.get("response", "")
    print(f"[MAX_ATTEMPTS] Returning best available response ({len(last)} chars)")
    return {
        "messages": [
            SystemMessage(
                content=f"Max attempts ({MAX_ATTEMPTS}) reached. Returning best response."
            )
        ],
    }


# ---------------------------------------------------------------------------
# Classification Router
# ---------------------------------------------------------------------------

def classify_query(state: AgentLoopState) -> dict:
    """
    Node: Classify the user query and store the category in state.
    """
    query = state.get("user_input", "").lower()

    sensitive_keywords = [
        "hack", "bypass", "exploit", "illegal", "malware", "virus",
        "crack", "steal", "fraud",
    ]
    technical_keywords = [
        "transformer", "attention", "neural", "gradient", "embedding",
        "tokenizer", "backpropagation", "architecture", "algorithm",
        "langgraph", "langchain", "vector database", "rag",
    ]

    if any(kw in query for kw in sensitive_keywords):
        classification = "sensitive"
    elif any(kw in query for kw in technical_keywords):
        classification = "technical"
    else:
        classification = "general"

    print(f"[CLASSIFY] Query classified as {classification.upper()}")
    return {
        "classification": classification,
        "messages": [
            SystemMessage(content=f"Query classified as {classification}")
        ],
    }


def route_after_classify(state: AgentLoopState) -> str:
    """
    Conditional edge router: send the query to the appropriate handler
    based on its classification.
    """
    cat = state.get("classification", "general")
    if cat == "sensitive":
        return "sensitive_handler"
    elif cat == "technical":
        return "generate"
    return "generate"


def handle_sensitive(state: AgentLoopState) -> dict:
    """Handler for sensitive / safety-related queries."""
    print(f"[SENSITIVE] Routing to safety-aware handler")
    return {
        "response": (
            "I cannot provide instructions for activities that may be harmful "
            "or illegal. Please consult appropriate resources or authorities "
            "for assistance with this matter."
        ),
        "is_success": True,
        "messages": [
            SystemMessage(content="Routed through sensitive query handler")
        ],
    }


def route_after_validate(state: AgentLoopState) -> str:
    """
    Conditional routing after validation.

    Returns:
        "respond"      - success path
        "regenerate"   - retry path (loop back)
        "max_attempts" - fallback when retries exhausted
    """
    if state.get("is_success", False):
        print("[ROUTE] Validation passed -> respond")
        return "respond"
    elif state.get("attempts", 0) >= state.get("max_attempts", MAX_ATTEMPTS):
        print("[ROUTE] Max attempts reached -> fallback")
        return "max_attempts"
    else:
        print("[ROUTE] Validation failed -> regenerate")
        return "regenerate"


# ---------------------------------------------------------------------------
# Graph Builder
# ---------------------------------------------------------------------------

def build_self_correcting_loop() -> StateGraph:
    """Construct the self-correcting agent loop graph."""
    print("=" * 70)
    print("SELF-CORRECTING AGENT LOOP")
    print("=" * 70)
    print(f"  Max attempts:  {MAX_ATTEMPTS}")
    print(f"  Model:         {MODEL}")
    print(f"  Temperature:   {GENERATION_TEMPERATURE}")
    print("=" * 70)

    builder = StateGraph(AgentLoopState)

    # Core loop nodes
    builder.add_node("generate", generate_response)
    builder.add_node("validate", validate_response)
    builder.add_node("regenerate", regenerate_response)
    builder.add_node("respond", respond)
    builder.add_node("max_attempts", handle_max_attempts)

    # Classification nodes
    builder.add_node("classify", classify_query)
    builder.add_node("sensitive_handler", handle_sensitive)

    # Entry point
    builder.set_entry_point("classify")

    # Classification routing
    builder.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "generate": "generate",
            "sensitive_handler": "sensitive_handler",
        },
    )

    # Sensitive handler ends the graph immediately
    builder.add_edge("sensitive_handler", END)

    # Core loop edges
    builder.add_edge("generate", "validate")

    builder.add_conditional_edges(
        "validate",
        route_after_validate,
        {
            "respond": "respond",
            "regenerate": "regenerate",
            "max_attempts": "max_attempts",
        },
    )

    builder.add_edge("regenerate", "validate")
    builder.add_edge("respond", END)
    builder.add_edge("max_attempts", END)

    graph = builder.compile()

    print("[BUILD] Graph compiled successfully")
    print("[BUILD] Flow: classify -> [sensitive_handler|generate] -> validate -> [respond|regenerate|max_attempts]")
    print("[BUILD] Loop: regenerate -> validate (up to {MAX_ATTEMPTS} times)")

    return graph


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------

TEST_QUESTIONS = [
    {
        "input": "What is an AI agent and why does it matter?",
        "category": "general",
    },
    {
        "input": "How does the transformer architecture work?",
        "category": "technical",
    },
    {
        "input": "What are vector embeddings and how are they used in RAG?",
        "category": "technical",
    },
    {
        "input": "Explain the concept of attention mechanisms in deep learning.",
        "category": "technical",
    },
    {
        "input": "How do LangGraph conditional edges enable dynamic workflows?",
        "category": "technical",
    },
]


def run_test(graph: StateGraph, question: str) -> dict:
    """Execute a single test through the agent loop graph."""
    print("=" * 70)
    print(f"TEST: {question[:70]}")
    print("=" * 70)

    initial_state: AgentLoopState = {
        "user_input": question,
        "task_description": question,
        "classification": "",
        "response": "",
        "validation_result": "",
        "attempts": 0,
        "max_attempts": MAX_ATTEMPTS,
        "is_success": False,
        "messages": [HumanMessage(content=question)],
    }

    try:
        final_state = graph.invoke(initial_state)

        success = final_state.get("is_success", False)
        attempts = final_state.get("attempts", 0)
        response_len = len(final_state.get("response", ""))

        print(f"  Success:  {success}")
        print(f"  Attempts: {attempts}/{MAX_ATTEMPTS}")
        print(f"  Response: {response_len} characters")
        print(f"  Validation: {final_state.get('validation_result', 'N/A')}")

        return final_state

    except Exception as exc:
        print(f"  Error: {exc}")
        return {"is_success": False, "attempts": 0, "error": str(exc)}


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

def main() -> None:
    """Build the graph and run the full test suite."""
    print("=" * 70)
    print("LAB 4.2: SELF-CORRECTING AGENT LOOP")
    print("=" * 70)

    graph = build_self_correcting_loop()

    print("\n" + "=" * 70)
    print(f"RUNNING {len(TEST_QUESTIONS)} TESTS")
    print("=" * 70)

    results = []
    for i, item in enumerate(TEST_QUESTIONS, 1):
        print(f"\n[Test {i}/{len(TEST_QUESTIONS)}]")
        result = run_test(graph, item["input"])
        results.append(result)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Tests run:          {len(results)}")
    success_count = sum(
        1 for r in results if r.get("is_success", False)
    )
    avg_attempts = (
        sum(r.get("attempts", 0) for r in results) / len(results)
        if results
        else 0
    )
    print(f"  Successful:         {success_count}/{len(results)}")
    if success_count:
        print(f"  Success rate:       {success_count / len(results) * 100:.1f}%")
    print(f"  Avg attempts/test:  {avg_attempts:.1f}")
    print("=" * 70)
    print("[SUCCESS] Lab 4.2 completed.\n")


if __name__ == "__main__":
    main()
