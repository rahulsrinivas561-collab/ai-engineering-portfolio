import os
import streamlit as st
import chromadb
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Load environment variables & Initialize Clients securely
load_dotenv()

st.set_page_config(page_title="Enterprise RAG Assistant", layout="wide")
st.title("🛡️ Enterprise AI: Smart Chunking & Guardrailed RAG")

chroma_client = chromadb.PersistentClient(path="./chroma_db")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

collection = chroma_client.get_or_create_collection(name="enterprise_kb")

# 2. Sidebar File Ingestion with Smart Text Splitter
st.sidebar.header("1. Upload Knowledge Source")
uploaded_file = st.sidebar.file_uploader("Upload .txt or .pdf file", type=["txt", "pdf"])

if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    extracted_text = ""
    
    # Extract text from files
    if file_extension == "txt":
        extracted_text = uploaded_file.read().decode("utf-8")
    elif file_extension == "pdf":
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
    
    if extracted_text:
        # Smart Chunking with Overlap (Chunk size = 500 characters, Overlap = 100 characters)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len
        )
        chunks = text_splitter.split_text(extracted_text)
        
        # Add to ChromaDB with unique IDs
        ids = [f"{uploaded_file.name}_chunk_{i}" for i in range(len(chunks))]
        collection.add(documents=chunks, ids=ids)
        st.sidebar.success(f"Processed into {len(chunks)} smart overlapping chunks!")

# 3. Main Area Q&A
st.header("2. Ask Your Knowledge Base")
user_query = st.text_input("Enter your question:")

if st.button("Query AI Engine"):
    if user_query:
        if collection.count() == 0:
            st.warning("Database is empty. Please upload a file first.")
        else:
            # Vector Search - Retrieve Top 3 Chunks
            search_results = collection.query(query_texts=[user_query], n_results=3)
            retrieved_chunks = search_results['documents'][0]
            retrieved_context = "\n---\n".join(retrieved_chunks)
            
            # System Prompt with Strict Guardrails
            system_prompt = (
                "You are an enterprise AI assistant. Answer the user's question using ONLY the provided context.\n"
                "If the answer cannot be found in the context, respond strictly with: "
                "'I cannot answer this based on the provided documents.' Do not guess or use outside knowledge."
            )
            
            user_prompt = f"Context:\n{retrieved_context}\n\nQuestion: {user_query}"
            
            # Request LLM Completion
            response = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1  # Low temperature for precise, non-creative answers
            )
            
            # Output Display
            st.success("### AI Answer:")
            st.write(response.choices[0].message.content)
            
            with st.expander("🔍 View Retrieved Context & Chunks"):
                st.code(retrieved_context)
    else:
        st.warning("Please type a question.")