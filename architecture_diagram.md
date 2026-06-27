# Week 1 – Architecture Diagram
This document provides a comprehensive overview of the chatbot architecture, agent loop, LangChain chain patterns, technology stack, and data flow, presented with clear diagrams and structured tables for easy reference.
## Chatbot Architecture

```mermaid
flowchart TB
    subgraph USER_LAYER[User Layer]
        UI[User Input]
    end
    subgraph INTENT_LAYER[Intent Layer]
        IC[Intents Classification]
    end
    subgraph TOOL_LAYER[Tool Layer]
        TS[Tool Selection]
    end
    subgraph ACTION_LAYER[Action Layer]
        AE[Action Execution]
    end
    subgraph RESPONSE_LAYER[Response Layer]
        OR[Observe Result]
        GR[Generate Response]
        FR[Response Formatting]
    end
    subgraph MEMORY_LAYER[Memory Layer]
        MEM[Conversation History • Context • Session State]
    end
    subgraph TOOLS_LAYER[Tools Layer]
        S[Search]
        C[Calculate]
        KB[Knowledge Base]
        DB[Database]
    end
    UI --> IC --> TS --> AE --> OR --> GR --> FR --> UI
    OR --> GR
    style USER_LAYER fill:#f0f8ff,stroke:#333,stroke-width:1px;
    style INTENT_LAYER fill:#e6f7ff,stroke:#333,stroke-width:1px;
    style TOOL_LAYER fill:#d9f7be,stroke:#333,stroke-width:1px;
    style ACTION_LAYER fill:#fff1b8,stroke:#333,stroke-width:1px;
    style RESPONSE_LAYER fill:#ffd6e7,stroke:#333,stroke-width:1px;
    style MEMORY_LAYER fill:#f9f0ff,stroke:#333,stroke-width:1px;
    style TOOLS_LAYER fill:#fff2e8,stroke:#333,stroke-width:1px;
```

**Explanation** – The diagram illustrates the forward flow of a user request through intent classification, tool selection, action execution, result observation and response generation. The memory layer stores conversational context, while the tools layer provides auxiliary capabilities such as search, calculation, knowledge‑base lookup and database access.

---

## Agent Loop

```mermaid
stateDiagram-v2
    [*] --> Perceive: Receive Input
    Perceive --> Reason: Analyze Problem
    Reason --> Plan: Decide Action
    Plan --> Act: Execute Action
    Act --> Observe: See Result
    Observe --> Perceive: Loop Until Goal Achieved
```

---

## LangChain Chain Patterns

### Pattern 1: Simple Chain
```
prompt | llm | parser
```

### Pattern 2: RunnablePassthrough
```
{ "context": retriever, "question": RunnablePassthrough() } | prompt | llm | parser
```

### Pattern 3: RunnableParallel
```
RunnableParallel({ "a": chain1, "b": chain2 })
```

---

## Technology Stack

| Layer          | Technology                              |
|----------------|------------------------------------------|
| **LLM**       | Groq (llama‑3.3‑70b, llama‑3.1‑8b)      |
| **Framework** | LangChain LCEL                           |
| **Memory**    | In‑memory conversation buffer            |
| **Retrieval** | BM25 (keyword‑based)                    |
| **UI**        | Rich (terminal)                         |
| **Environment**| Python 3.11.9                           |

---

## Data Flow
1. **User Input** → 2. **Intent Classification** → 3. **Tool Selection** → 4. **Action Execution** → 5. **Result Observation** → 6. **Response Generation** → 7. **User Output**

---

*Document generated on 2026‑06‑28.*
