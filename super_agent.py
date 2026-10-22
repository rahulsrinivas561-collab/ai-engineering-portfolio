import os
import json
import chromadb
from dotenv import load_dotenv
from groq import Groq

# 1. Load environment variables & Initialize Clients securely
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="company_master_kb")

# Add some company knowledge for RAG
collection.add(
    documents=[
        "Company Policy: Remote employees are allowed a $500 home office stipend per year.",
        "Project Delta is scheduled for beta release on December 1, 2026.",
    ],
    ids=["doc1", "doc2"]
)

# 2. Define Custom Tools (Functions)
def get_order_status(order_id: str):
    """Check the shipping status of a customer order ID."""
    database = {
        "ORD-1001": {"status": "Shipped", "delivery_date": "October 22, 2026"},
        "ORD-1002": {"status": "Processing", "delivery_date": "Pending"},
    }
    return json.dumps(database.get(order_id, {"error": "Order not found"}))

def search_internal_knowledge(query: str):
    """Search company policy documents and knowledge base using vector search (RAG)."""
    results = collection.query(query_texts=[query], n_results=1)
    chunks = results['documents'][0]
    return json.dumps({"retrieved_context": chunks})

available_tools = {
    "get_order_status": get_order_status,
    "search_internal_knowledge": search_internal_knowledge
}

tools_metadata = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Get shipping status and delivery date for a customer order ID.",
            "parameters": {
                "type": "object",
                "properties": {"order_id": {"type": "string", "description": "Order ID like ORD-1001"}},
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_internal_knowledge",
            "description": "Search company policies, guidelines, and project documents.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "The search topic or question"}},
                "required": ["query"],
            },
        },
    }
]

# 3. User Query requiring BOTH document search AND order lookup!
user_input = "What is the policy for remote office stipends, and can you also check the status of order ORD-1001?"
messages = [
    {
        "role": "system",
        "content": "You are an enterprise AI assistant with access to company documents and database tools. Use them to answer the user accurately."
    },
    {"role": "user", "content": user_input}
]

print(f"User Request: {user_input}\n")

# 4. Run the Agentic Loop
for iteration in range(3):
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        tools=tools_metadata,
        tool_choice="auto",
    )
    
    response_message = response.choices[0].message
    messages.append(response_message)
    
    if not response_message.tool_calls:
        print("\n--- Final Capstone Agent Answer ---")
        print(response_message.content)
        break
        
    for tool_call in response_message.tool_calls:
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)
        
        print(f"Agent invoked tool: [{func_name}] with args: {func_args}")
        
        if func_name in available_tools:
            tool_output = available_tools[func_name](**func_args)
            print(f"Tool Result: {tool_output}\n")
            
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": func_name,
                "content": tool_output,
            })