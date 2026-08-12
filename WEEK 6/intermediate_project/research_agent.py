import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class ResearchAgent:
    def __init__(self, memory_engine, fact_extractor):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        # Use a highly capable model for general chat and reasoning
        self.model = "llama-3.3-70b-versatile"
        self.memory = memory_engine
        self.extractor = fact_extractor
        
    def get_response(self, user_input: str, session_id: str) -> str:
        # 1. Pre-Session Context Assembly
        recent_history = self.memory.get_recent_history(session_id, limit=6)
        
        # Retrieve semantic facts
        relevant_facts_raw = self.memory.retrieve_relevant_facts(user_input)
        facts_str = "\n".join([f"- {f['fact']} (Category: {f['metadata']['category']})" for f in relevant_facts_raw])
        
        # Retrieve user profile
        user_profile = self.memory.get_user_profile()
        profile_str = f"""
        Known Topics: {', '.join(user_profile.get('known_topics', []))}
        Preferred Depth: {user_profile.get('preferred_depth', 'balanced')}
        Communication Style: {user_profile.get('communication_style', 'standard')}
        Active Goals: {', '.join(user_profile.get('active_research_goals', []))}
        """
        
        # 2. Construct System Prompt
        system_prompt = f"""You are an advanced Long-Term Personal Research Assistant.
        You have a persistent memory of the user. Adapt your responses based on their profile and past facts.
        
        --- USER PROFILE ---
        {profile_str}
        
        --- RELEVANT PAST FACTS ---
        {facts_str if facts_str else "No specific past facts retrieved for this query."}
        
        Instructions:
        - Do not explain basic concepts if the user profile says they are familiar with them.
        - Adopt their preferred communication style and depth.
        - Directly answer the query.
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add history
        for msg in recent_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
            
        messages.append({"role": "user", "content": user_input})
        
        # 3. Generate Response
        assistant_reply = ""
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.4
            )
            assistant_reply = response.choices[0].message.content
        except Exception as e:
            assistant_reply = f"I encountered an error connecting to my core processing node: {e}"
            
        # 4. Post-Session Memory Sync (Always log interaction)
        self.memory.log_interaction(session_id, "user", user_input)
        self.memory.log_interaction(session_id, "assistant", assistant_reply)
        
        # Only try to extract facts if there was no error generating the response
        if not assistant_reply.startswith("I encountered an error"):
            try:
                # Extract facts based on the new turn
                extraction = self.extractor.extract_information(user_input, assistant_reply)
                
                # Update semantic memory
                for fact in extraction.facts:
                    self.memory.add_fact(fact.fact, fact.category)
                    
                # Update user profile
                if extraction.profile_updates:
                    updates = extraction.profile_updates
                    
                    # Merge updates intelligently
                    if updates.known_topics:
                        user_profile["known_topics"] = list(set(user_profile.get("known_topics", []) + updates.known_topics))
                    if updates.active_research_goals:
                        user_profile["active_research_goals"] = list(set(user_profile.get("active_research_goals", []) + updates.active_research_goals))
                    if updates.preferred_depth:
                        user_profile["preferred_depth"] = updates.preferred_depth
                    if updates.communication_style:
                        user_profile["communication_style"] = updates.communication_style
                        
                    self.memory.update_user_profile(user_profile)
            except Exception as extract_error:
                with open("debug_agent.txt", "a", encoding="utf-8") as f:
                    f.write(f"Fact extraction failed: {str(extract_error)}\n")
                print(f"Fact extraction failed: {extract_error}")
                
        return assistant_reply
