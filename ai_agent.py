import os
import json
from dotenv import load_dotenv
from groq import Groq

# 1. Load environment variables and Initialize Groq Client securely
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 2. Define Multiple Tools
def get_order_status(order_id: str):
    """Check the shipping status of a customer order ID."""
    database = {
        "ORD-1001": {"status": "Shipped", "delivery_date": "October 22, 2026"},
        "ORD-1002": {"status": "Processing", "delivery_date": "Pending"},
    }
    return json.dumps(database.get(order_id, {"error": "Order not found"}))

def check_inventory(product_name: str):
    """Check live stock availability for a product."""
    stock_db = {
        "laptop": {"in_stock": True, "quantity": 14, "price": 1200},
        "mouse": {"in_stock": False, "quantity": 0, "price": 25},
    }
    return json.dumps(stock_db.get(product_name.lower(), {"error": "Product not found"}))

# Map function names to actual Python functions
available_tools = {
    "get_order_status": get_order_status,
    "check_inventory": check_inventory
}

# Define Tool Metadata for Groq
tools_metadata = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Get shipping status and delivery date for an order ID.",
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
            "name": "check_inventory",
            "description": "Check stock quantity and price for a product name.",
            "parameters": {
                "type": "object",
                "properties": {"product_name": {"type": "string", "description": "Product name like laptop or mouse"}},
                "required": ["product_name"],
            },
        },
    }
]

# 3. User Query requiring multi-domain tools
messages = [
    {
        "role": "system", 
        "content": "You are an autonomous enterprise AI agent. You have access to tools to check orders and inventory. Use them iteratively if needed."
    },
    {
        "role": "user", 
        "content": "Can you check if the laptop is in stock, and also check the status of order ORD-1002?"
    }
]

print(f"User Request: {messages[1]['content']}\n")

# 4. Agentic Loop (ReAct Loop)
max_iterations = 5
for iteration in range(max_iterations):
    print(f"--- Agent Loop Iteration {iteration + 1} ---")
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        tools=tools_metadata,
        tool_choice="auto",
    )
    
    response_message = response.choices[0].message
    messages.append(response_message)
    
    # If the model didn't call any more tools, it means it has its final answer!
    if not response_message.tool_calls:
        print("\n--- Final Agent Answer ---")
        print(response_message.content)
        break
        
    # If tools were requested, execute them all
    for tool_call in response_message.tool_calls:
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)
        
        print(f"Agent decided to call tool: [{func_name}] with args: {func_args}")
        
        # Execute the Python function dynamically
        if func_name in available_tools:
            tool_function = available_tools[func_name]
            tool_output = tool_function(**func_args)
            
            print(f"Tool Output Received: {tool_output}")
            
            # Feed result back into message history for the next loop iteration
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": func_name,
                "content": tool_output,
            })