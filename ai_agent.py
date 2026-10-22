import os
import sys
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ Error: GROQ_API_KEY not found.")
    sys.exit(1)

client = Groq(api_key=api_key)

class CachedAIAgent:
    def __init__(self, model: str = "openai/gpt-oss-20b"):
        self.model = model
        self.cache = {} # In-memory cache dictionary

    def run_query(self, prompt: str) -> str:
        cleaned_prompt = prompt.strip().lower()
        
        # Check cache first
        if cleaned_prompt in self.cache:
            print("⚡ [Cache Hit]: Returning cached response instantly.")
            return self.cache[cleaned_prompt]
        
        print(f"🤖 [Cache Miss]: Querying Groq LLM using {self.model}...")
        try:
            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a high-performance financial and AI engineering assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
            )
            response = completion.choices[0].message.content
            
            # Save to cache
            self.cache[cleaned_prompt] = response
            return response

        except Exception as e:
            return f"❌ Agent Error: {str(e)}"

if __name__ == "__main__":
    agent = CachedAIAgent()
    query = "What are the core benefits of caching in LLM applications?"
    
    print("--- First Execution (Cache Miss) ---")
    print(agent.run_query(query))
    
    print("\n--- Second Execution (Cache Hit) ---")
    print(agent.run_query(query))