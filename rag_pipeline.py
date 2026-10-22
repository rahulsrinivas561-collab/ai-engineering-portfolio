import os
import sys

# SQLite compatibility fix for ChromaDB
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import chromadb
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ Error: GROQ_API_KEY not found.")
    sys.exit(1)

client = Groq(api_key=api_key)

class ProductionRAGPipeline:
    def __init__(self, collection_name="portfolio_knowledge_base"):
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)

    def seed_documents(self):
        """Seeds initial vector records if collection is empty."""
        if self.collection.count() == 0:
            documents = [
                "The Fintech AI app uses Streamlit for interactive dashboards and Groq for high-speed inference.",
                "ChromaDB is used as a local persistent vector database for Retrieval-Augmented Generation pipelines.",
                "Production error handling in multi-agent systems ensures graceful degradation during rate limits."
            ]
            ids = ["doc1", "doc2", "doc3"]
            self.collection.add(documents=documents, ids=ids)
            print("✅ Vector database seeded with domain context.")

    def query_rag(self, query: str, n_results: int = 2) -> dict:
        results = self.collection.query(query_texts=[query], n_results=n_results)
        retrieved_docs = results['documents'][0] if results['documents'] else []
        context = "\n---\n".join(retrieved_docs)
        
        prompt = f"""You are a precise AI assistant. Answer the user query strictly using the provided context below.

Context:
{context}

User Query: {query}"""

        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return {"query": query, "retrieved_context": retrieved_docs, "answer": completion.choices[0].message.content}

if __name__ == "__main__":
    rag = ProductionRAGPipeline()
    rag.seed_documents()
    
    res = rag.query_rag("What is ChromaDB used for in this project?")
    print("\n--- RAG Output ---")
    print(f"Retrieved Context: {res['retrieved_context']}")
    print(f"Grounded Answer: {res['answer']}")