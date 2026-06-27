"""
Week 1 - Day 4: Prompt Engineering Lab
Lab 1.3 - Prompt Engineering A/B Test
Testing 5 different system prompts for summarization
"""

import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# ─── Test Article ───
SAMPLE_ARTICLE = """
Artificial Intelligence (AI) has made significant progress in recent years, 
transforming industries and reshaping how we work. From healthcare to finance, 
AI-powered tools are helping professionals make faster, more accurate decisions. 
Machine learning models can now process vast amounts of data in seconds, 
identifying patterns that would take humans weeks to find. 
However, these advancements also raise important ethical questions about job displacement, 
data privacy, and algorithmic bias. Experts suggest that the future of AI depends on 
developing systems that are transparent, fair, and aligned with human values.
"""

# ─── 5 Different System Prompts ───

SYSTEM_PROMPTS = {
    "1_concise": """
    You are a summarization assistant. 
    Summarize the given article in exactly 2 sentences.
    Be concise and clear. 
    Focus only on the most important points.
    """,
    
    "2_detailed": """
    You are a professional analyst writing a summary for executives.
    Provide a comprehensive 3-paragraph summary covering:
    - Key developments
    - Implications
    - Expert opinions
    Use professional language. Be thorough and complete.
    """,
    
    "3_bullet_points": """
    You are a research assistant preparing a briefing note.
    Summarize the article using bullet points.
    Include 4-5 key takeaways.
    Each bullet should be a complete sentence.
    Use this format:
    • Point 1
    • Point 2
    • Point 3
    """,
    
    "4_beginner_friendly": """
    You are a teacher explaining AI concepts to students.
    Summarize the article in simple, easy-to-understand language.
    Avoid technical jargon.
    Use analogies where helpful.
    Make it engaging and accessible.
    """,
    
    "5_critical": """
    You are a research analyst writing a critical review.
    Summarize the article AND highlight potential issues.
    Include:
    1. Main points
    2. What the article doesn't address
    3. Unanswered questions
    4. Potential risks or concerns
    Be balanced but thorough.
    """
}

def test_prompt(prompt_name, system_prompt, article):
    """Test a specific prompt and return results"""
    
    print(f"\n{'='*60}")
    print(f"Testing: {prompt_name}")
    print(f"{'='*60}")
    
    try:
        # Initialize LLM
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        # Create prompt
        template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "Article: {article}\n\nPlease summarize this article.")
        ])
        
        # Create chain
        chain = template | llm | StrOutputParser()
        
        # Measure time
        start_time = time.time()
        response = chain.invoke({"article": article})
        end_time = time.time()
        
        # Calculate metrics
        word_count = len(response.split())
        char_count = len(response)
        time_taken = end_time - start_time
        
        # Print results
        print(f"\nResponse:\n{response}\n")
        print(f"Metrics:")
        print(f"  - Word count: {word_count}")
        print(f"  - Character count: {char_count}")
        print(f"  - Time taken: {time_taken:.2f}s")
        
        return {
            "name": prompt_name,
            "response": response,
            "word_count": word_count,
            "char_count": char_count,
            "time": time_taken
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def evaluate_responses(results):
    """Evaluate and compare the responses"""
    
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)
    
    print(f"{'Prompt':<15} {'Words':<10} {'Chars':<10} {'Time (s)':<10}")
    print("-"*60)
    
    for r in results:
        if r:
            print(f"{r['name']:<15} {r['word_count']:<10} {r['char_count']:<10} {r['time']:<10.2f}")
    
    print("\n" + "="*60)
    print("OBSERVATIONS:")
    print("="*60)
    print("1. Concise Prompt: Shortest summary, good for quick overview")
    print("2. Detailed Prompt: Most comprehensive, best for executives")
    print("3. Bullet Points: Easy to scan, good for busy readers")
    print("4. Beginner Friendly: Most accessible, good for general audience")
    print("5. Critical Prompt: Most balanced, includes risks and concerns")
    print("="*60)

def interactive_prompt_test():
    """Allow user to test their own prompts"""
    
    print("\n" + "="*60)
    print("INTERACTIVE PROMPT TEST")
    print("Test your own system prompt")
    print("="*60)
    
    print("\nSample Article:")
    print("-"*60)
    print(SAMPLE_ARTICLE)
    print("-"*60)
    
    print("\nEnter your system prompt (type 'exit' to stop):")
    
    while True:
        print("\n" + "="*60)
        prompt_text = input("System Prompt: ").strip()
        
        if prompt_text.lower() == 'exit':
            break
        
        if not prompt_text:
            continue
        
        result = test_prompt("Custom", prompt_text, SAMPLE_ARTICLE)
        
        if result:
            print("\nWant to test another? (yes/no)")
            choice = input().strip().lower()
            if choice != 'yes':
                break

def main():
    print("="*60)
    print("WEEK 1 - DAY 4: PROMPT ENGINEERING LAB")
    print("Lab 1.3 - Prompt Engineering A/B Test")
    print("="*60)
    
    print("\nTesting 5 different system prompts for summarization...")
    
    results = []
    
    # Test all prompts
    for name, prompt in SYSTEM_PROMPTS.items():
        result = test_prompt(name, prompt, SAMPLE_ARTICLE)
        if result:
            results.append(result)
    
    # Compare results
    if results:
        evaluate_responses(results)
    
    # Interactive test
    interactive_prompt_test()

if __name__ == "__main__":
    main()