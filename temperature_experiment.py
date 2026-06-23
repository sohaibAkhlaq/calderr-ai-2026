"""
Week 1 - Day 1: Temperature Experiment
Testing temperature effects on LLM output
0 = Deterministic, 1 = Creative, 2 = Highly Random
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

def experiment_temperature():
    print("="*60)
    print("Temperature Experiment - Week 1 Day 1")
    print("="*60)
    
    question = "Tell me a creative story about a robot learning to paint"
    
    temperatures = [0.0, 0.3, 0.7, 1.0, 1.5, 2.0]
    
    results = []
    
    for temp in temperatures:
        print(f"\n{'='*60}")
        print(f"Temperature: {temp}")
        print(f"{'='*60}")
        
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=temp,
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a creative storyteller."),
            ("user", "{question}")
        ])
        
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"question": question})
        
        word_count = len(response.split())
        char_count = len(response)
        
        print(f"Response length: {char_count} characters")
        print(f"Word count: {word_count}")
        print(f"First 200 chars: {response[:200]}...")
        
        results.append({
            "temperature": temp,
            "word_count": word_count,
            "char_count": char_count,
            "response": response
        })
    
    print("\n" + "="*60)
    print("SUMMARY - Temperature Observations")
    print("="*60)
    print(f"{'Temp':<10} {'Words':<10} {'Chars':<10}")
    print("-"*60)
    for r in results:
        print(f"{r['temperature']:<10} {r['word_count']:<10} {r['char_count']:<10}")
    
    print("\n" + "="*60)
    print("Key Takeaways:")
    print("- Temperature 0.0: Most consistent, repetitive, deterministic")
    print("- Temperature 0.7: Good balance of creativity and coherence")
    print("- Temperature 1.5+: More creative but may become incoherent")
    print("- Temperature 2.0: Highly random, may produce nonsensical output")
    print("="*60)

if __name__ == "__main__":
    experiment_temperature()