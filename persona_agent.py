"""
Week 1 - Day 4: Persona-Based Agent
Build an agent with different personas
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# ─── Persona Definitions ───

PERSONAS = {
    "customer_support": {
        "name": "Customer Support Agent",
        "system": """
        You are a friendly and professional customer support agent for TechCorp.
        You help customers with their technical issues in a calm and patient manner.
        Always be helpful, empathetic, and solution-oriented.
        Use a professional but warm tone.
        If you don't know something, politely say so and offer to escalate.
        """,
        "description": "Helpful, empathetic, solution-oriented"
    },
    
    "code_reviewer": {
        "name": "Code Reviewer Agent",
        "system": """
        You are a senior software engineer with 10 years of experience.
        You review code with a focus on:
        - Code quality and best practices
        - Performance optimization
        - Security vulnerabilities
        - Readability and maintainability
        Provide constructive feedback. Be critical but respectful.
        Use technical language with clear explanations.
        """,
        "description": "Technical, thorough, constructive"
    },
    
    "data_analyst": {
        "name": "Data Analyst Agent",
        "system": """
        You are a senior data analyst specializing in business intelligence.
        You interpret data and provide actionable insights.
        Focus on:
        - Patterns and trends
        - Business implications
        - Actionable recommendations
        Use clear, data-driven language.
        Support your points with logical reasoning.
        """,
        "description": "Analytical, insight-driven, business-focused"
    },
    
    "marketing_writer": {
        "name": "Marketing Writer Agent",
        "system": """
        You are a creative marketing copywriter with expertise in brand storytelling.
        You write engaging, persuasive copy that resonates with target audiences.
        Focus on:
        - Benefits over features
        - Emotional connection
        - Clear call-to-action
        Use vivid language and compelling narratives.
        Be creative but always on-brand.
        """,
        "description": "Creative, persuasive, engaging"
    },
    
    "technical_tutor": {
        "name": "Technical Tutor Agent",
        "system": """
        You are a patient and knowledgeable technical tutor teaching AI concepts.
        You explain complex topics in simple, accessible language.
        Always:
        - Start with analogies
        - Break down complex ideas
        - Use examples
        - Check understanding
        Encourage curiosity and questions.
        Be supportive and encouraging.
        """,
        "description": "Patient, clear, encouraging"
    }
}

def create_persona_agent(persona_key, model="llama-3.1-8b-instant", temperature=0.7):
    """Create an agent with a specific persona"""
    
    if persona_key not in PERSONAS:
        print(f"Persona '{persona_key}' not found")
        return None
    
    persona = PERSONAS[persona_key]
    
    llm = ChatGroq(
        model=model,
        temperature=temperature,
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", persona["system"]),
        ("user", "{question}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain, persona

def test_persona(persona_key, question):
    """Test a specific persona with a question"""
    
    print(f"\n{'='*60}")
    print(f"Testing: {PERSONAS[persona_key]['name']}")
    print(f"Description: {PERSONAS[persona_key]['description']}")
    print(f"{'='*60}")
    
    chain, persona = create_persona_agent(persona_key)
    
    if not chain:
        return
    
    print(f"\nQuestion: {question}\n")
    print("Response:")
    print("-"*40)
    
    response = chain.invoke({"question": question})
    print(response)
    print("-"*40)

def interactive_persona_agent():
    """Interactive chat with persona selection"""
    
    print("\n" + "="*60)
    print("INTERACTIVE PERSONA AGENT")
    print("Select a persona to chat with")
    print("="*60)
    
    # Show available personas
    print("\nAvailable Personas:")
    for i, key in enumerate(PERSONAS.keys(), 1):
        print(f"  {i}. {PERSONAS[key]['name']} - {PERSONAS[key]['description']}")
    
    print("\nEnter number to select, or 'exit' to quit")
    
    while True:
        try:
            choice = input("\nSelect persona: ").strip()
            
            if choice.lower() == 'exit':
                print("\nGoodbye!")
                break
            
            # Get selected persona
            try:
                idx = int(choice) - 1
                persona_keys = list(PERSONAS.keys())
                if 0 <= idx < len(persona_keys):
                    selected_key = persona_keys[idx]
                else:
                    print("Invalid selection")
                    continue
            except ValueError:
                print("Please enter a number")
                continue
            
            chain, persona = create_persona_agent(selected_key)
            
            if not chain:
                continue
            
            print(f"\nChatting with {persona['name']}")
            print("Type 'exit' to quit, 'switch' to change persona\n")
            
            while True:
                question = input(f"[{persona['name']}] You: ").strip()
                
                if not question:
                    continue
                
                if question.lower() == 'exit':
                    print("Goodbye!")
                    return
                
                if question.lower() == 'switch':
                    break
                
                print(f"\n{persona['name']}: ", end="", flush=True)
                response = chain.invoke({"question": question})
                print(response + "\n")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    print("="*60)
    print("WEEK 1 - DAY 4: PERSONA-BASED AGENT")
    print("Prompt Engineering - Different Personas")
    print("="*60)
    
    # Test question
    question = "What are the most important considerations when building an AI system?"
    
    print(f"\nTesting all personas with: {question}")
    
    # Test each persona
    for persona_key in PERSONAS.keys():
        test_persona(persona_key, question)
    
    # Interactive mode
    interactive_persona_agent()

if __name__ == "__main__":
    main()