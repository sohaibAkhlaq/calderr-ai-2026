"""
Week 1 - Lab 1.1: Your First Groq Agent
CLI Chatbot with Conversation History
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

class GroqChatbot:
    def __init__(self, model="llama-3.3-70b-versatile", temperature=0.7):
        self.llm = ChatGroq(
            model=model,
            temperature=temperature,
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        self.messages = []
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant. You are friendly, knowledgeable, and concise."),
            MessagesPlaceholder(variable_name="history"),
            ("user", "{input}")
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def chat(self, user_input):
        self.messages.append(HumanMessage(content=user_input))
        
        response = self.chain.invoke({
            "history": self.messages[:-1],
            "input": user_input
        })
        
        self.messages.append(AIMessage(content=response))
        return response
    
    def clear(self):
        self.messages = []
        print("\nConversation cleared.\n")
    
    def show_history(self):
        print("\n" + "="*60)
        print("Conversation History")
        print("="*60)
        for msg in self.messages:
            if isinstance(msg, HumanMessage):
                print(f"User: {msg.content}")
            else:
                print(f"AI: {msg.content}")
        print("="*60 + "\n")

def main():
    chatbot = GroqChatbot()
    
    print("="*60)
    print("Welcome to Groq CLI Chatbot")
    print("Commands: /clear, /history, /exit")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() == '/exit':
                print("\nGoodbye!")
                break
            elif user_input.lower() == '/clear':
                chatbot.clear()
                continue
            elif user_input.lower() == '/history':
                chatbot.show_history()
                continue
            
            print("\nAI: ", end="", flush=True)
            response = chatbot.chat(user_input)
            print(response + "\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")

if __name__ == "__main__":
    main()