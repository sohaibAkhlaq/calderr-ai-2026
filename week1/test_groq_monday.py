"""
Week 1 - Day 1: LLM Foundations - Groq API Exploration
Testing different models and temperature settings
"""

import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

def test_model(model_name, temperature, question):
    """Test a specific model with given temperature"""
    print(f"\n{'='*60}")
    print(f"Model: {model_name}")
    print(f"Temperature: {temperature}")
    print(f"{'='*60}")
    
    try:
        llm = ChatGroq(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Provide concise, accurate answers."),
            ("user", "{question}")
        ])
        
        chain = prompt | llm | StrOutputParser()
        
        start_time = time.time()
        response = chain.invoke({"question": question})
        end_time = time.time()
        
        print(f"Question: {question}\n")
        print(f"Response: {response}\n")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        print(f"{'='*60}\n")
        
        return {
            "model": model_name,
            "temperature": temperature,
            "time": end_time - start_time,
            "response": response
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("Week 1 - Day 1: LLM Foundations")
    print("Testing Groq Models with Different Temperatures\n")
    
    question = "What is a transformer architecture and why is it important for AI?"
    
    models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768"
    ]
    
    temperatures = [0.0, 0.7, 1.5]
    
    results = []
    
    for model in models:
        for temp in temperatures:
            result = test_model(model, temp, question)
            if result:
                results.append(result)
    
    print("\n" + "="*60)
    print("SUMMARY - Model Performance Comparison")
    print("="*60)
    print(f"{'Model':<30} {'Temp':<10} {'Time (s)':<10}")
    print("-"*60)
    for r in results:
        print(f"{r['model']:<30} {r['temperature']:<10} {r['time']:<10.2f}")
    print("="*60)

if __name__ == "__main__":
    main()