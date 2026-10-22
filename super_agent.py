import os
import sys
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ Error: GROQ_API_KEY not found.")
    sys.exit(1)

client = Groq(api_key=api_key)

def execute_secure_agent_task(prompt: str, model: str = "openai/gpt-oss-20b") -> str:
    print(f"🤖 Agent executing task with model {model}...")
    try:
        # Note: Reasoning models require instructions inside the user prompt (no system role)
        formatted_prompt = f"You are an expert autonomous AI engineering assistant. Provide a structured analysis for the following:\n\n{prompt}"
        
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": formatted_prompt}
            ],
            temperature=0.3,
            max_completion_tokens=1024,
        )
        return completion.choices[0].message.content
        
    except Exception as e:
        error_msg = str(e)
        print(f"⚠️ API Exception caught: {error_msg}")
        return f"❌ Agent Execution Failed: {error_msg}"

if __name__ == "__main__":
    print("\n--- Running Super Agent ---")
    result = execute_secure_agent_task("Analyze the top risks of multi-agent systems in production environments.")
    print(result)