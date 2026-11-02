import os
import time
from dotenv import load_dotenv
from groq import Groq
from langfuse import observe  # <--- Updated import path

load_dotenv()

# Initialize API Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 1. Traceable Helper Function: RAG Retrieval Step
@observe(name="retrieve_fraud_context")
def mock_retrieval(user_id: int):
    time.sleep(0.3)
    return f"User {user_id} has 3 flagged account logins from unverified IP addresses in the past 24 hours."

# 2. Traceable Helper Function: LLM Generation Step
@observe(name="generate_fraud_audit")
def generate_audit(user_id: int, context: str):
    start_time = time.time()
    
    prompt = f"Analyze risk for User {user_id} given this context: {context}"
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": "You are a Trust & Safety Risk Assessor. Be concise."},
            {"role": "user", "content": prompt}
        ]
    )
    
    latency = time.time() - start_time
    output_text = response.choices[0].message.content
    return output_text

# 3. Main End-to-End Traced Pipeline
@observe(name="fraud_investigation_pipeline")
def run_investigation(user_id: int):
    print(f"🕵️ Starting investigation trace for User ID: {user_id}...")
    
    # Step A: Retrieve Context
    context = mock_retrieval(user_id)
    
    # Step B: LLM Risk Assessment
    audit_report = generate_audit(user_id, context)
    
    return audit_report

if __name__ == "__main__":
    result = run_investigation(user_id=88402)
    print("\n✅ Final Audit Output:")
    print(result)
    print("\n📊 Trace Observation logged successfully via @observe decorator!")