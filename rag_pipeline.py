import os
import chromadb
from dotenv import load_dotenv
from groq import Groq

# 1. Load environment variables & Initialize Clients securely
load_dotenv()

chroma_client = chromadb.Client()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 2. Setup Vector Database
collection = chroma_client.create_collection(name="company_kb")
collection.add(
    documents=[
        "Project Alpha deadline is November 15, 2026.",
        "The lead AI engineer on Project Alpha is Rahul.",
        "Groq provides low-latency inference for real-time applications."
    ],
    ids=["id1", "id2", "id3"]
)

# 3. User Query
user_query = "Who is leading Project Alpha and when is the deadline?"

# 4. Retrieve Context from ChromaDB
search_results = collection.query(query_texts=[user_query], n_results=2)
retrieved_context = " ".join(search_results['documents'][0])

# 5. Pass Context to LLM
prompt = f"Context: {retrieved_context}\n\nQuestion: {user_query}\nAnswer:"

response = groq_client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": prompt}]
)

print("\n--- AI Answer ---")
print(response.choices[0].message.content)