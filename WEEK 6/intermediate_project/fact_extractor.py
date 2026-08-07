import os
import json
from pydantic import BaseModel, Field
from typing import List, Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class Fact(BaseModel):
    fact: str = Field(description="The atomic fact extracted from the interaction.")
    category: str = Field(description="The category of the fact: preference, goal, or skill.")

class ProfileUpdate(BaseModel):
    known_topics: List[str] = Field(default_factory=list, description="New technical topics the user is familiar with.")
    active_research_goals: List[str] = Field(default_factory=list, description="New active goals the user is working on.")
    preferred_depth: Optional[str] = Field(default=None, description="Preferred depth of explanation (e.g., concise, detailed, balanced).")
    communication_style: Optional[str] = Field(default=None, description="Preferred style (e.g., bulleted, code-heavy, formal).")

class ExtractionResult(BaseModel):
    facts: List[Fact] = Field(default_factory=list)
    profile_updates: Optional[ProfileUpdate] = None

class FactExtractor:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        # Using a reliable model for JSON extraction
        self.model = "llama-3.1-8b-instant" 

    def extract_information(self, user_message: str, assistant_message: str) -> ExtractionResult:
        prompt = f"""
        Analyze the following conversation turn between a user and an AI assistant.
        Extract any new atomic facts about the user (preferences, skills, goals) and suggest updates to their profile.
        
        User: {user_message}
        Assistant: {assistant_message}
        
        Return the result as a JSON object matching this schema:
        {{
            "facts": [{{"fact": "...", "category": "..."}}],
            "profile_updates": {{
                "known_topics": ["..."],
                "active_research_goals": ["..."],
                "preferred_depth": "...",
                "communication_style": "..."
            }}
        }}
        If there is no new information, return empty arrays and null/empty values. Do not output anything other than the JSON object.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a precise data extraction system. Only output valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result_json = json.loads(response.choices[0].message.content)
            return ExtractionResult(**result_json)
        except Exception as e:
            print(f"Extraction error: {e}")
            return ExtractionResult()
