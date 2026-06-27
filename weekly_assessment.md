# Week 1 Weekly Assessment

## Overview

This assessment summarizes the key concepts learned during Week 1 of the CalderR AI internship. The responses below are written in a clear, professional format and reflect the main ideas from the lectures and practical exercises.

---

## Conceptual Questions

### 1. Difference Between a Language Model and an Agent

A language model is a system that generates text by predicting the next token based on patterns learned from training data. It is primarily focused on language generation and response creation.

An agent extends this capability by adding:

- Tool use for tasks such as searching, calculation, or database access
- Planning to decide the next best action
- Memory to maintain context across steps or conversations
- Decision-making to choose among available actions
- Autonomy to carry out tasks with limited human guidance

In short, a language model can answer questions, while an agent can reason, act, and interact with external systems.

---

### 2. Context Window in Agentic Systems

The context window is the maximum amount of information a model can process at one time, usually measured in tokens.

It matters because it affects:

- How much conversation history the model can remember
- How much tool output can be included in a single step
- The maximum size of documents or prompts that can be processed
- The overall cost and latency of the model

For agentic systems, a larger context window allows longer reasoning chains and better handling of multi-step tasks.

---

### 3. ReAct Pattern

The ReAct pattern combines reasoning and acting in an iterative loop. The model observes the situation, reasons about the best next step, takes an action using a tool, and then observes the result before continuing.

Typical loop:

1. Perceive the input
2. Reason about the goal
3. Plan the next action
4. Act using a tool or function
5. Observe the result
6. Repeat if necessary

Use ReAct when a task is complex, multi-step, or requires external tools. Use a simple chain when the workflow is fixed and predictable.

---

## Technical Questions

### 4. LCEL in LangChain

LCEL, or LangChain Expression Language, is a declarative way to compose LangChain workflows using the pipe operator (`|`). It makes chains readable, modular, and easy to extend.

Example:

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

prompt = ChatPromptTemplate.from_template("Answer: {question}")
llm = ChatGroq(model="llama-3.1-8b-instant")
parser = StrOutputParser()

chain = prompt | llm | parser
response = chain.invoke({"question": "What is AI?"})
```

This example shows a simple pipeline:

- Prompt: formats the user input
- LLM: generates the answer
- Parser: extracts the final response text

---

### 5. Temperature in LLM Sampling

Temperature controls the randomness of the model’s output.

| Temperature | Effect | Typical Use |
|---|---|---|
| 0.0 | Deterministic and consistent | Math, code, factual extraction |
| 0.3–0.5 | Slightly creative but still controlled | Classification and structured tasks |
| 0.7 | Balanced and natural | General chat and everyday use |
| 1.0+ | More creative and varied | Brainstorming and storytelling |
| 2.0 | Highly random and potentially inconsistent | Experimental creative writing |

Temperature should be set to 0 when the task requires repeatable, precise, and stable results.

---

### 6. Simple Agent Architecture for a Customer Support Chatbot

A simple customer support agent can be designed with the following flow:

User Input → Intent Classifier → Tool Selector → Tool Execution → Response Generator → User

Suggested components:

- Intent Classifier: identifies the user’s goal
- Tool Selector: decides which tool to use
- Memory: keeps track of the conversation history
- Response Generator: creates the final answer
- Escalation Handler: transfers to a human if required

Useful tools:

- Knowledge Base Search for FAQs and documentation
- Order Lookup for tracking and delivery status
- Account Management for profile and password tasks
- Product Database for product information
- Status Check for outages and service issues

This architecture allows the bot to answer routine requests efficiently while knowing when to escalate complex cases.

---

## Final Reflection

Week 1 provided a strong foundation in both the theory and implementation of modern AI systems. The most important lessons were understanding how LLMs work, how agents extend them with tools and reasoning, and how prompt design can shape output quality and behavior.
