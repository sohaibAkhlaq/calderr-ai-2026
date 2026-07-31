# Week 5 Weekly Assessment

## Question 1 (Conceptual)
**Question:** Explain the difference between a supervisor pattern and a peer network. What problem does each solve best?

**Answer:**
- **Supervisor Pattern:**
  - *Structure:* Centralized hierarchy where a top-level Supervisor Agent manages worker/specialist agents. The supervisor decomposes user tasks, delegates work, monitors execution, handles timeouts/failures, and aggregates final outputs.
  - *Best Solved Problem:* Structured workflows with clear delegation hierarchies, strict task boundaries, centralized failure recovery, and deterministic routing (e.g., enterprise research systems, software release pipelines).
- **Peer Network:**
  - *Structure:* Decentralized architecture where equal agents communicate directly with one another via shared state or message buses without centralized orchestrator control.
  - *Best Solved Problem:* Open-ended multi-agent negotiation, multi-perspective debate, collaborative consensus building, and decentralized problem solving where no single agent possesses complete authority.

---

## Question 2 (Conceptual)
**Question:** How does typed message passing between agents improve system reliability compared to passing raw strings or dicts?

**Answer:**
- **Schema Validation at Ingestion:** Pydantic schemas enforce type validation, bounds checking, and required field existence before any handler logic is invoked. Malformed payloads are rejected immediately at the bus boundary rather than causing silent data corruption deep inside execution loops.
- **Contract Enforcement & IDE Safety:** Eliminates string key typos (`"task_id"` vs `"taskId"`), guarantees non-null primitives, and enforces deterministic data structures across asynchronous agent channels.
- **Traceability & Auditing:** Typed message models naturally serialize to structured JSON logs (`model_dump()`), enabling automated per-agent token tracking, cost attribution, and transparent decision audit trails.

---

## Question 3 (Conceptual)
**Question:** When does splitting a task across multiple agents hurt rather than help? Give two concrete failure scenarios.

**Answer:**
Splitting a task hurts when inter-agent communication overhead, context leakage, or cascade errors outweigh the benefits of specialization.
- **Failure Scenario 1: Information Bottleneck and Context Loss (Telephone Game)**
  - When a task requires fine-grained context, chaining multiple agents (e.g., Agent A -> Agent B -> Agent C) causes cumulative context loss at each handoff boundary. The final synthesis misses critical nuances present in the original input.
- **Failure Scenario 2: Latency & Cost Explosion in Tightly Coupled Dependencies**
  - Splitting sequential sub-tasks that depend heavily on shared memory across multiple agent LLM calls increases token latency 5-10x and incurs unnecessary API token costs without adding domain specialization value.

---

## Question 4 (Technical)
**Question:** Write the Pydantic schema for a Handoff message between a Research Agent and a Synthesis Agent. What fields are essential?

**Answer:**
```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional

class HandoffMessage(BaseModel):
    """
    Typed message schema transferring task state from ResearchAgent to SynthesisAgent.
    """
    task_id: str = Field(..., description="Unique task identifier for traceability")
    from_agent: str = Field("ResearchAgent", description="Source agent name")
    to_agent: str = Field("SynthesisAgent", description="Target recipient agent name")
    context: str = Field(..., description="Structured research context and gathered evidence")
    source_citations: List[str] = Field(default_factory=list, description="Verified references or data sources")
    priority: int = Field(default=3, description="Task priority (1-5)")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    @field_validator('task_id', 'context')
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field must not be empty or blank")
        return v.strip()

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("Priority must be between 1 and 5")
        return v
```
**Essential Fields:**
1. `task_id`: Ensures correlation across agent traces.
2. `from_agent` / `to_agent`: Enforces explicit routing contracts.
3. `context`: The core data payload transferred between agents.
4. `priority` & `timestamp`: Required for queue handling and audit logging.

---

## Question 5 (Technical)
**Question:** How would you detect and handle a situation where two agents in a consensus system produce directly contradictory outputs with equal confidence?

**Answer:**
1. **Detection:**
   - Group opinions by normalized answer strings.
   - Compare pairwise similarity and compute weighted confidence scores ($Score_i = \sum Conf_i / Total\_Conf$).
   - If two opposing options have identical normalized scores (e.g., 50% vs 50%) or if top options contradict with confidence delta $< 0.05$, trigger a contradiction flag.
2. **Handling Strategy:**
   - **Step 1 (Debate Round 2):** Trigger a targeted 1-on-1 challenge round where each agent receives the opponent's reasoning and must explicitly defend or refine its stance.
   - **Step 2 (Tie-Breaker Arbiter Node):** If equal confidence persists after Round 2, dispatch a third-party Arbiter Agent with higher domain authority or expanded context parameters to issue a binding ruling.
   - **Step 3 (Dissent Audit Summary):** Record both perspectives in a transparent Dissent Log so human supervisors can inspect the trade-offs.

---

## Question 6 (Design)
**Question:** You are building a multi-agent customer support system. Design the agent hierarchy: who talks to whom, what each agent knows, and what happens when the top-level agent is unavailable.

**Answer:**
### 1. Hierarchy & Topology:
- **Level 1 (Top Level): Support Router Agent (Supervisor)**
  - *Role:* Classifies customer intent (Billing, Technical, Account) and delegates queries.
  - *Scope:* Knows customer identity, account tier, and routing taxonomy.
- **Level 2 (Specialist Domain Leads):**
  - **Billing Agent:** Accesses invoice DB, payment gateway API, refund policies.
  - **Technical Support Agent:** Accesses system logs, API docs, service status page.
  - **Account Management Agent:** Accesses user profile DB and permission controls.
- **Level 3 (Worker Tier):**
  - **Refund Processor Worker:** Executes payment refunds under threshold bounds.
  - **Log Diagnostics Worker:** Parses backend stack traces and error codes.

### 2. Information Scoping & Context Isolation:
- Lower-level workers receive only query-specific tokens (e.g. refund worker gets transaction ID, not full user chat history), maintaining privacy and preventing token bloat.

### 3. Failover Protocol (Top-Level Unavailable):
- **Fallback Circuit Breaker:** If the Support Router Agent fails or times out:
  1. Requests bypass the router and hit a deterministic Rule-Based Emergency Gateway (regex/keyword matching).
  2. Directs billing queries to Billing Agent and technical errors to Technical Support Agent.
  3. If intent is ambiguous, returns a structured Graceful Degradation message asking the user to select their inquiry category from a menu, maintaining zero downtime.
