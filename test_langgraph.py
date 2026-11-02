import os
from typing import TypedDict, List
from dotenv import load_dotenv
from groq import Groq
from langgraph.graph import StateGraph, END

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 1. Define the Shared State Schema
class RiskWorkflowState(TypedDict):
    raw_query: str
    generated_sql: str
    audit_feedback: str
    is_approved: bool
    iterations: int

# 2. Node A: SQL Generator Agent
def sql_generator_node(state: RiskWorkflowState) -> RiskWorkflowState:
    print(f"\n🤖 [Agent 1: SQL Generator] Writing query for: '{state['raw_query']}'...")
    
    prompt = f"Convert this business request into a safe, clean Snowflake SQL query. Return ONLY the SQL query string: {state['raw_query']}"
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}]
    )
    sql = response.choices[0].message.content.strip()
    
    return {
        "generated_sql": sql,
        "iterations": state["iterations"] + 1
    }

# 3. Node B: Risk Auditor Agent (The Reviewer)
def risk_auditor_node(state: RiskWorkflowState) -> RiskWorkflowState:
    print(f"🔍 [Agent 2: Risk Auditor] Auditing SQL query:\n{state['generated_sql']}")
    
    # Simple logic check: look for dangerous commands or validate structure
    sql = state["generated_sql"].upper()
    if "DROP" in sql or "DELETE" in sql or "TRUNCATE" in sql:
        feedback = "REJECTED: Destructive operation detected (DROP/DELETE/TRUNCATE)."
        approved = False
    else:
        feedback = "APPROVED: Query is safe and read-only."
        approved = True
        
    return {
        "audit_feedback": feedback,
        "is_approved": approved
    }

# 4. Conditional Router Edge
def should_continue(state: RiskWorkflowState) -> str:
    if state["is_approved"] or state["iterations"] >= 2:
        return "end"
    return "regenerate"

# 5. Build the LangGraph State Machine
workflow = StateGraph(RiskWorkflowState)

# Add nodes
workflow.add_node("generator", sql_generator_node)
workflow.add_node("auditor", risk_auditor_node)

# Set entry point
workflow.set_entry_point("generator")

# Add edges (with a loop back if audit fails)
workflow.add_edge("generator", "auditor")

workflow.add_conditional_edges(
    "auditor",
    should_continue,
    {
        "regenerate": "generator",
        "end": END
    }
)

# Compile the graph into an executable application
app = workflow.compile()

if __name__ == "__main__":
    # Test input request
    initial_input = {
        "raw_query": "SELECT * FROM users_fraud_log WHERE risk_score > 0.8",
        "generated_sql": "",
        "audit_feedback": "",
        "is_approved": False,
        "iterations": 0
    }
    
    print("🚀 Starting LangGraph Multi-Agent Pipeline Execution...")
    final_state = app.invoke(initial_input)
    
    print("\n================ FINISHED ================")
    print(f"Final SQL Output:\n{final_state['generated_sql']}")
    print(f"Audit Status: {final_state['audit_feedback']}")
    print(f"Total Iterations: {final_state['iterations']}")