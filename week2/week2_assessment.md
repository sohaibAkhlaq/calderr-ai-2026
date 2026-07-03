# Week 2 — Weekly Assessment

**CalderR AI Internship | Week 2 | Completed: July 2026**

---

## Conceptual Questions

### Q1: What is the difference between Chain-of-Thought and Tree-of-Thought prompting? When would you use each?

**Chain-of-Thought (CoT)** instructs the model to reason sequentially — step 1, step 2, step 3 — before producing a final answer. The reasoning path is linear and deterministic.

**Tree-of-Thought (ToT)** instructs the model to branch into multiple candidate reasoning paths simultaneously, evaluate each branch, and converge on the most promising one.

| Dimension | Chain-of-Thought | Tree-of-Thought |
|---|---|---|
| Reasoning shape | Linear | Branching / tree |
| Exploration | Single path | Multiple paths |
| Cost | Low | High (multiple LLM calls) |
| Best for | Math, logic, sequential tasks | Planning, strategy, open-ended problems |

**Use CoT when** the problem has a clear, linear solution path (e.g., arithmetic, step-by-step code generation, structured extraction).

**Use ToT when** the problem is open-ended, has multiple valid approaches, or benefits from exploring alternatives (e.g., complex reasoning, creative writing, strategic planning).

---

### Q2: Why does structured output matter for production AI systems? What problems does it solve?

Structured output constrains the model to emit data in a machine-readable format (JSON, validated Pydantic schema) rather than free-form prose.

**Problems it solves:**

1. **Reliability** — Downstream code can parse the output without fragile string matching.
2. **Validation** — Pydantic validators enforce type correctness, value ranges, and cross-field constraints at parse time, not after the fact.
3. **Automation** — Structured data can be inserted directly into databases, APIs, or workflows without manual intervention.
4. **Consistency** — The model cannot silently change field names or omit required keys between calls.
5. **Auditability** — Every output is a typed record that can be logged, diffed, and reproduced.

In financial systems specifically, incorrect data types or missing fields in an unvalidated LLM response can propagate into calculations, producing silent but critical errors.

---

### Q3: Explain the tool-calling lifecycle. How does a model decide to call a tool, and what happens after?

```
User Input
   |
   v
Model Reasoning
   |
   +-- Detects that the query requires external capability
   |   (based on fine-tuning + tool descriptions in system prompt)
   |
   v
Tool Selection  <-- selects tool by highest relevance to query
   |
   v
Parameter Extraction  <-- model populates tool arguments from user context
   |
   v
Tool Execution  <-- host environment calls the actual function
   |
   v
Result Injection  <-- tool result appended to conversation context
   |
   v
Response Generation  <-- model generates user-facing answer, grounded in tool result
```

The model decides to call a tool when:
- The query contains signals matching a tool description (semantic similarity from fine-tuning).
- The query requires real-time data, computation, or external state that the model cannot answer from memory alone.
- The tool descriptions in the system prompt are well-written and specific.

After execution, the tool result is injected into the context window as a `tool` role message. The model then generates its final response grounded in that result.

---

## Technical Questions

### Q4: Write a Pydantic model for extracting a job posting's title, salary range, and required skills.

```python
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Literal


class JobPosting(BaseModel):
    title: str = Field(description="Job title / position name")
    salary_min: Optional[int] = Field(None, ge=0, description="Minimum annual salary")
    salary_max: Optional[int] = Field(None, ge=0, description="Maximum annual salary")
    salary_currency: Literal["USD", "EUR", "GBP", "PKR"] = Field(
        "USD", description="ISO 4217 currency code"
    )
    required_skills: List[str] = Field(
        min_length=1, description="List of required technical or domain skills"
    )

    @field_validator("salary_min", "salary_max")
    @classmethod
    def non_negative(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("Salary values must be non-negative.")
        return v

    @model_validator(mode="after")
    def salary_range_coherent(self) -> "JobPosting":
        if self.salary_min is not None and self.salary_max is not None:
            if self.salary_max < self.salary_min:
                raise ValueError(
                    f"salary_max ({self.salary_max}) must be >= salary_min ({self.salary_min})."
                )
        return self
```

---

### Q5: What is exponential backoff and why is it used when calling external APIs?

**Exponential backoff** is a retry strategy where the wait time between successive retry attempts grows exponentially rather than remaining constant.

**Formula:**

```
delay = min(base_delay * 2^attempt, max_delay) + jitter
```

Where `jitter` is a small random offset added to prevent the **thundering herd problem** — multiple clients retrying in perfect synchrony and overwhelming the server simultaneously.

**Why it is used:**

| Reason | Explanation |
|---|---|
| Rate limit compliance | Backing off respects HTTP 429 (Too Many Requests) semantics. |
| Server pressure relief | Spreading retries reduces load on a recovering server. |
| Graceful degradation | The client handles transient failures without crashing. |
| Cost efficiency | Fewer wasted requests means lower API spend. |
| Deterministic ceiling | `max_delay` prevents unbounded waits while still being adaptive. |

Typical parameters: `base_delay=1s`, `max_delay=60s`, `max_retries=3-5`, jitter factor `0–10%`.

---

### Q6: Design a tool schema for a `send_email` function.

```python
SEND_EMAIL_SCHEMA = {
    "name": "send_email",
    "description": (
        "Send a formatted email to one or more recipients. "
        "Use this tool when the user explicitly requests to send, compose, or forward an email."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "to": {
                "type": "string",
                "description": "Primary recipient email address. Must be a valid RFC 5322 address."
            },
            "subject": {
                "type": "string",
                "description": "Subject line of the email. Keep under 80 characters."
            },
            "body": {
                "type": "string",
                "description": (
                    "Body of the email in plain text or Markdown. "
                    "Must be non-empty."
                )
            },
            "cc": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of CC recipient email addresses.",
                "default": []
            },
            "bcc": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of BCC recipient email addresses.",
                "default": []
            },
            "priority": {
                "type": "string",
                "enum": ["low", "normal", "high"],
                "description": "Email priority level. Defaults to 'normal'.",
                "default": "normal"
            },
            "attachments": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of absolute file paths or URLs to attach.",
                "default": []
            },
            "reply_to": {
                "type": "string",
                "description": "Optional reply-to address if different from the sender."
            }
        },
        "required": ["to", "subject", "body"],
        "additionalProperties": False
    }
}
```

**Design decisions:**
- `to` accepts a single address (use `cc` for multiple recipients) to keep the primary recipient clear.
- `priority` uses an enum to prevent arbitrary values from leaking into mail headers.
- `attachments` accepts paths or URLs to support both local files and remote assets.
- `reply_to` is optional but included because it is a common enterprise requirement.
- `additionalProperties: False` prevents the model from inventing undocumented parameters.

---

## Standup Preparation — Demo Script (2 minutes)

"Good morning. This is my Week 2 summary from the CalderR AI internship.

**Day 1 — Advanced Prompting:** I implemented a chain-of-thought pipeline using LangChain and Groq. I compared answer quality with and without CoT and also explored Tree-of-Thought and meta-prompting patterns.

**Day 2 — Structured Outputs:** I built a job posting extractor backed by five Pydantic models, including cross-field validators and nested schema composition.

**Day 3 — Tool Calling Basics:** I built a five-tool agent — search, calculate, format_date, convert_currency, and summarize_text — with keyword-based tool routing.

**Day 4 — External APIs as Tools:** I integrated real external APIs for weather, news, and currency, adding exponential backoff, retry logic, and fallback mock data for resilience.

**Day 5 — Integration:** My intermediate project is the API Aggregator Agent, which fetches weather, financial news, and currency data in parallel using `asyncio.gather` and synthesises a morning briefing via a CoT prompt. My production project is the Financial Data Analysis Agent — a Streamlit app where users upload a CSV, ask natural-language questions, and receive generated code, Plotly charts, and a narrative report.

Key learning: tool calling transforms LLMs from conversational systems into actionable agents that interact with the real world."

---

## Week 2 Completion Checklist

- [x] Day 1 — Advanced Prompting (CoT, ToT, Self-Consistency, Meta-Prompting)
- [x] Day 2 — Structured Outputs (Pydantic models, PydanticOutputParser)
- [x] Day 3 — Tool Calling Basics (5-tool agent, tool routing)
- [x] Day 4 — External APIs as Tools (retry, backoff, fallbacks)
- [x] Day 5 — Integration and Deployment
- [x] Lab 2.1 — Structured output extractor (job postings)
- [x] Lab 2.2 — Multi-tool research agent
- [x] Lab 2.3 — Error recovery agent with real APIs
- [x] Weekly assessment (all 6 Q&A)
- [x] Intermediate Project — API Aggregator Agent (`project2_i_c_api_aggregator.py`)
- [x] Production Project — Financial Data Analysis Agent (`project2_p_c_financial_analysis.py`)
- [x] Streamlit deployment configured (`requirements-streamlit.txt`)
- [x] README complete (`week2/README.md`)
