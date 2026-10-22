import os
import json
from dotenv import load_dotenv
from groq import Groq

# 1. Load environment variables & Initialize Groq Client securely
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 2. Define a Custom Python Function (The "Tool")
def get_order_status(order_id: str):
    """Check the shipping status of a customer order ID."""
    # Mock database lookup
    database = {
        "ORD-1001": {"status": "Shipped", "delivery_date": "October 22, 2026"},
        "ORD-1002": {"status": "Processing", "delivery_date": "Pending"},
    }
    return json.dumps(database.get(order_id, {"error": "Order not found"}))

# 3. Define the Tool Metadata for the LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Get the shipping status and delivery date for a given customer order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The customer order ID, e.g. ORD-1001",
                    }
                },
                "required": ["order_id"],
            },
        },
    }
]

# 4. User Query requiring external data
messages = [{"role": "user", "content": "Can you check the status of order ORD-1001 for me?"}]

print(f"User Query: {messages[0]['content']}\n")

# 5. First LLM Call: Ask model if it needs to use a tool
response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

response_message = response.choices[0].message
print(f"LLM Tool Call Requested: {response_message.tool_calls is not None}")

# 6. Handle Tool Execution if requested by model
if response_message.tool_calls:
    # Append model's assistant response to message history
    messages.append(response_message)
    
    for tool_call in response_message.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        print(f"Executing Python Function: {function_name} with arguments: {function_args}")
        
        # Execute our local Python function
        if function_name == "get_order_status":
            function_output = get_order_status(order_id=function_args.get("order_id"))
            
            # Append tool execution result back to message history
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_output,
                }
            )

    # 7. Second LLM Call: Send tool output back to model to write the final response
    final_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
    )
    
    print("\n--- Final AI Response ---")
    print(final_response.choices[0].message.content)