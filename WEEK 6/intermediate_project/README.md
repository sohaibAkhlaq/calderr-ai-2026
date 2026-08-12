# Category 1 Intermediate Project: Long-Term Personal Research Assistant (Project 6-I-A)

---

## Executive Overview
Every commercial AI assistant today resets to zero the moment a conversation ends. The **Long-Term Personal Research Assistant** bridges this gap by persisting multi-layer agent memory across sessions. Over repeated interactions, the assistant extracts user preferences, domain interests, preferred communication styles, and active research goals, building a dynamic, structured user profile. As a result, future research queries are automatically personalized: previously explored topics are summarized rather than re-explained, and new findings are proactively connected to past research.

---

## Portfolio Standard: Measurable Improvement
This project demonstrates concrete, empirical proof of learning over time:
- **Session 1 (Zero Memory):** Agent provides generic, verbose 400-word explanations and asks basic setup questions.
- **Session 5 (5-Session Personalization):** Agent references specific prior findings from Session 1 and 3, applies the user's preferred concise bullet format, and automatically filters out topics marked as "already understood".

---

## System Architecture

```mermaid
flowchart TD
    UserSession["User Input (Streamlit UI)"] --> SessionInit["Session Initializer"]
    
    subgraph MemoryRetrieval ["Pre-Session Context Assembly"]
        SessionInit --> |Fetch Episodic History| SQLiteEpisodic["SQLite Episodic Store"]
        SessionInit --> |Fetch Vector Facts| VectorStore["SQLite Vector Store (Cosine Similarity)"]
        SessionInit --> |Fetch User Profile| UserProfileKV["SQLite User Profile (JSON)"]
    end
    
    SessionInit --> |Injected System Prompt| ResearchAgent["Research Agent (Groq / Llama 3.3 70B)"]
    ResearchAgent --> UserOutput["Response to User"]
    
    subgraph PostSessionPipeline ["Post-Session Memory Sync"]
        UserOutput --> FactExtractor["Fact Extractor Agent (Pydantic Schema)"]
        FactExtractor --> |Deterministic Word Index Embeddings| VectorStore
        FactExtractor --> |Synthesize Updated Profile| UserProfileKV
        UserOutput --> Logger["Interaction Logger"] --> SQLiteEpisodic
    end
```

---

## Core Memory System Design

### 1. Episodic Memory Store (SQLite)
- **Table Name:** `episodic_interactions`
- **Fields:** `id` (UUID), `session_id` (str), `timestamp` (ISO 8601), `role` (user/assistant), `content` (text), `importance_score` (float 1.0–10.0).

### 2. Semantic Memory Store (Pure-Python SQLite Vector Store)
- **Table Name:** `semantic_facts`
- **Fields:** `id` (UUID), `document` (text), `category` (preference, goal, skill), `confidence_score` (float), `recency_timestamp` (ISO 8601), `embedding` (JSON 384-dim vector).
- **Embedding Algorithm:** Pure-Python Random Indexing with MD5 hash seeding and L2 normalization (zero external C++ DLL dependencies).

### 3. User Profile Aggregator (SQLite JSON)
- **Structure:**
```json
{
  "user_id": "usr_9981",
  "known_topics": ["PostgreSQL", "FastAPI", "Vector Embeddings"],
  "preferred_depth": "concise_technical",
  "communication_style": "bulleted_with_code",
  "active_research_goals": ["Evaluating GraphRAG vs Vector RAG for enterprise search"],
  "open_questions": []
}
```

---

## Automated Test Suite (16/16 Passed, 100% Coverage)

The application features a built-in **Automated Test Suite** tab in the Streamlit interface with 16 automated integration and component tests:

| Test Group | Test Name | Description | Status |
|---|---|---|---|
| **Group 1: Episodic Memory** | 1.1 Log Interaction | Verifies user and assistant messages are logged to SQLite | ✅ Pass |
| | 1.2 Retrieve History | Verifies chronological retrieval with role separation | ✅ Pass |
| | 1.3 Session Isolation | Verifies conversation data does not leak across sessions | ✅ Pass |
| **Group 2: Semantic Memory** | 2.1 Add Semantic Fact | Verifies fact embedding and storage | ✅ Pass |
| | 2.2 Bulk Fact Storage | Verifies multi-fact indexing and persistence | ✅ Pass |
| | 2.3 Cosine Similarity | Verifies top-k retrieval of relevant facts | ✅ Pass |
| | 2.4 Semantic Ranking | Verifies highest relevance score ranks first | ✅ Pass |
| **Group 3: User Profile** | 3.1 Default Profile Init | Verifies default schema creation on startup | ✅ Pass |
| | 3.2 Update Known Topics | Verifies topic array updates without duplicates | ✅ Pass |
| | 3.3 Update Style | Verifies communication style and depth updates | ✅ Pass |
| | 3.4 Update Goals | Verifies research goal tracking updates | ✅ Pass |
| **Group 4: Fact Extractor** | 4.1 LLM Fact Extraction | Verifies live Pydantic extraction from user statements | ✅ Pass |
| | 4.2 Pydantic Validation | Verifies strict schema enforcement on extracted data | ✅ Pass |
| **Group 5: Integration** | 5.1 Full Pipeline | Verifies end-to-end flow (Query → LLM → Memory Sync) | ✅ Pass |
| | 5.2 Memory Persistence | Verifies state retention across simulated restarts | ✅ Pass |
| | 5.3 Profile Adaptation | Verifies multi-turn learning across multiple interactions | ✅ Pass |

---

## Quick Start & Running

### Prerequisites
- Python 3.11+
- `GROQ_API_KEY` set in your `.env` file

### Installation
```bash
pip install -r requirements.txt
```

### Execution
```bash
streamlit run app.py
```

### Live Demo Instructions
1. Open `http://localhost:8501` in your browser.
2. Click on the **🧪 Automated Test Suite** tab and press **🚀 Run All Tests** to showcase the 100% pass rate.
3. Switch to **💬 Live Interaction** and test persona injection:
   > *"I'm a Senior Backend Engineer. I know PostgreSQL and system design. For all future answers, use concise bullet points and skip basic definitions."*
4. Switch to **🔍 Memory Inspector** and **👤 User Profile Viewer** to see the synthesized persona update live.
