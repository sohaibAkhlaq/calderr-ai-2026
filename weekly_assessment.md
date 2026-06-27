# Week 1 - Weekly Assessment

## Conceptual Questions

### Q1: Explain the difference between a language model and an agent. What capabilities does an agent add?

**Answer:**
A **language model** is a neural network trained to predict the next token given previous tokens. It generates text based on learned patterns from training data.

An **agent** builds on a language model by adding:
- **Tools**: Ability to call external functions (search, calculator, database, APIs)
- **Planning**: Deciding what actions to take to achieve a goal
- **Memory**: Maintaining and using context across conversations
- **Decision-making**: Choosing which tools to use and when
- **Autonomy**: Taking actions without explicit step-by-step instructions
- **Reflection**: Evaluating results and adjusting approach

The key difference is that a language model only generates text, while an agent takes action in the world.

---

### Q2: What is the 'context window' and why does it matter for agentic systems?

**Answer:**
The **context window** is the maximum number of tokens a model can process in a single request.

**Why it matters for agents:**
- **Memory**: Agents can only "remember" what fits in the context window
- **Tool usage**: Tool outputs must fit within the context window
- **Conversation length**: Limits how long a conversation can be
- **Document processing**: Limits how much information can be processed at once
- **Cost**: Larger context windows are more expensive

**Example:**
- llama-3.3-70b: 128,000 tokens → can process entire books
- Smaller models: 4,096 tokens → limited to short documents

---

### Q3: Describe the ReAct pattern. When would you use it versus a simple chain?

**Answer:**
**ReAct** = Reasoning + Acting pattern where the agent alternates between thinking and doing.

**The Loop:**

Perceive → Reason → Plan → Act → Observe → Repeat

**When to use ReAct vs Simple Chain:**

| Simple Chain | ReAct Pattern |
|--------------|---------------|
| Fixed sequence of steps | Dynamic decision-making |
| Predictable tasks | Complex, open-ended tasks |
| No tool usage | Heavy tool usage |
| One-shot tasks | Multi-step reasoning |
| Example: Q&A with static docs | Example: Research assistant |

**Use ReAct when:** You need the agent to think, use tools, and adapt based on results.

**Use Simple Chain when:** You have a fixed process that never changes.

---

## Technical Questions

### Q4: What is LCEL in LangChain? Write a 5-line example using the pipe operator.

**Answer:**
**LCEL** (LangChain Expression Language) is a declarative way to compose chains using the pipe operator `|`.

**Example:**
```python
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template("Answer: {question}")
llm = ChatGroq(model="llama-3.1-8b-instant")
parser = StrOutputParser()

chain = prompt | llm | parser
response = chain.invoke({"question": "What is AI?"})
```

This chains three components:

1. **Prompt** → formats the input
2. **LLM** → processes the prompt
3. **Parser** → extracts the string response

---

### Q5: Explain the role of temperature in LLM sampling. When would you set it to 0?

**Answer:**
**Temperature** controls the randomness of the model's output by scaling the logits before softmax.

| Temperature | Effect | Use Case |
|---|---|---|
| 0.0 | Deterministic, always same output | Math, code, exact answers, testing |
| 0.3–0.5 | Slightly creative, predictable | Data extraction, classification |
| 0.7 | Balanced, creative but coherent | General chat, most tasks |
| 1.0+ | Creative, varied responses | Storytelling, brainstorming |
| 2.0 | Highly random, may be incoherent | Creative writing experiments |

**When to set temperature to 0:**

- When you need **consistent, repeatable answers**
- For tasks requiring **exact precision** (math, code, fact extraction)
- For **testing and evaluation** (same input → same output)
- When you want **deterministic behavior**

---

## Design Question

### Q6: Design a simple agent architecture for a customer support chatbot. What tools would it need?

**Answer:**

**Architecture:**

```text
User Input → Intent Classifier → Tool Selector → Execution → Response Generator → User
```

**Components:**

1. **Intent Classifier**: Determines what the user wants
2. **Tool Selector**: Chooses which tool to use
3. **Memory**: Stores conversation history
4. **Response Generator**: Creates final response

**Tools Needed:**

- **Knowledge Base Search**: Search FAQ, documentation, help articles
- **Order Lookup**: Check order status, tracking numbers
- **Account Management**: Update preferences, reset passwords
- **Escalation**: Transfer to human agent when needed
- **Product Database**: Search product information, pricing
- **Status Check**: Check system status, outages

**Workflow:**

1. User: "Where is my order #12345?"
2. Agent: Classifies intent → Selects Order Lookup tool
3. Tool: Returns order status
4. Agent: Generates response with tracking info
5. Follow-up: "Is there anything else I can help with?"

**Guardrails:**

- Never share personal information
- Escalate if user is frustrated
- Stay within scope (don't answer off-topic questions)

---

## Week 1 Completion Checklist

- [ ] All 5 daily learning sessions completed (Mon–Fri)
- [ ] Lab 1.1 - Groq CLI chatbot built and working
- [ ] Lab 1.2 - Manual ReAct loop implemented without a framework
- [ ] Lab 1.3 - Prompt A/B test completed with documented findings
- [ ] Weekly Assessment questions answered in writing
- [ ] One Intermediate project chosen, built, and pushed to GitHub
- [ ] One Production project chosen, built, and pushed to GitHub
- [ ] Both projects have complete README files with setup instructions
- [ ] Architecture diagram prepared for Friday's standup review
- [ ] Demo rehearsed and ready to present in under 2 minutes

---

## Standup Preparation

### 1. Demo Script (2 minutes)

Demo: Professional Chatbot

1. "I built a professional CLI chatbot with 5 different personas"
2. Show: Persona selection (general, technical, creative, academic, mentor)
3. Show: Conversation with memory
4. Show: /history command
5. Show: /stats command
6. Show: Response quality

### 2. Technical Question

**"What surprised you most this week?"**

> "The biggest surprise was how much prompt engineering impacts output quality. The same LLM can produce completely different responses based on the system prompt. A concise prompt gives brief answers, while a detailed prompt gives comprehensive responses. This means the LLM's capability is fixed, but we can dramatically change its behavior through prompting."

### 3. Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────┐
│ CHATBOT ARCHITECTURE                                       │
│                                                             │
│ ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌────────┐            │
│ │ User    │──▶│ Intent   │──▶│ Tool    │──▶│ Action │            │
│ │ Input   │  │ Classify │  │ Select  │  │ Exec   │            │
│ └─────────┘ └──────────┘ └─────────┘ └────────┘            │
│ ▲                                                           │
│ │                                                           │
│ ▼                                                           │
│ ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌────────┐            │
│ │ User    │◀──│ Response │◀──│ Generate│◀──│ Observe│            │
│ │ Output  │  │ Format   │  │ Response│  │ Result │            │
│ └─────────┘ └──────────┘ └─────────┘ └────────┘            │
│                                                             │
│ ┌─────────────────────────────────────────────────────┐       │
│ │ MEMORY LAYER                                      │       │
│ │ Conversation History · Context · Session State     │       │
│ └─────────────────────────────────────────────────────┘       │
│                                                             │
│ ┌─────────────────────────────────────────────────────┐       │
│ │ TOOLS LAYER                                       │       │
│ │ Search · Calculate · Knowledge Base · Database     │       │
│ └─────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 4. Code Review Snippet

```python
# Most interesting code: Persona-based agent with memory

class ProfessionalChatbot:
    def __init__(self, persona="general"):
        self.personas = {
            "general": "You are a helpful AI assistant.",
            "technical": "You are a senior software engineer.",
            "creative": "You are a creative writer.",
            "academic": "You are a university professor.",
            "mentor": "You are a patient mentor."
        }

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.personas[persona]),
            MessagesPlaceholder(variable_name="history"),
            ("user", "{input}")
        ])

        self.chain = self.prompt | llm | StrOutputParser()

    def chat(self, user_input):
        self.messages.append(HumanMessage(content=user_input))
        response = self.chain.invoke({
            "history": self.messages[:-1],
            "input": user_input
        })
        self.messages.append(AIMessage(content=response))
        return response
```

### 5. Blockers

**Technical Challenge:** PyTorch DLL error on Windows

**Solution:**

- Switched from sentence-transformers to BM25 retriever
- No embeddings needed for keyword-based retrieval
- Cleaner, faster, Windows-compatible
