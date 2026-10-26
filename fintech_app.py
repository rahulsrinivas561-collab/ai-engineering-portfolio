import os
import json
import pandas as pd
import sys

try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import streamlit as st
import chromadb
from dotenv import load_dotenv
from groq import Groq

# 1. Load environment variables & Page Configuration
load_dotenv()

st.set_page_config(
    page_title="FintechOS AI Copilot",
    page_icon="📈",
    layout="wide"
)

# 2. Initialize Groq & Chroma Clients Securely
@st.cache_resource
def init_clients():
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    # Use persistent client to align with project RAG storage
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(name="fintech_audit_kb")
    
    # Pre-load sample financial audit notes into ChromaDB (RAG)
    if collection.count() == 0:
        collection.add(
            documents=[
                "Audit Note 2026-Q3: PayPulse shows a negative operating cash flow (-$8.2M) and a high default risk score of 0.62. Requires strict credit monitoring.",
                "Compliance Policy: Any corporate entity with a Debt-to-Equity ratio exceeding 1.0 must submit a quarterly liquidity mitigation plan.",
                "TechCorp and CloudGrid maintain strong SaaS margins with low default risk scores under 0.15."
            ],
            ids=["audit1", "audit2", "audit3"]
        )
    return groq_client, collection

client, collection = init_clients()

# Load CSV dataset safely
@st.cache_data
def load_data():
    try:
        return pd.read_csv("fintech_portfolio.csv")
    except FileNotFoundError:
        return None

df = load_data()

# 3. Streamlit UI Layout
st.title("📈 FintechOS: Enterprise AI Financial Copilot")
st.markdown("Advanced financial risk analysis, quantitative portfolio screening, and document auditing powered by **Groq**, **Pandas**, and **ChromaDB**.")

tab1, tab2 = st.tabs(["📊 Quantitative Portfolio Copilot", "📑 Audit Document RAG Search"])

# --- TAB 1: QUANTITATIVE PANDAS AGENT ---
with tab1:
    st.subheader("Interactive Financial Data Analysis")
    st.markdown("Ask complex questions about company revenue, debt ratios, net income, or default risk scores.")
    
    if df is not None:
        with st.expander("🔍 View Raw Portfolio Dataset"):
            st.dataframe(df, use_container_width=True)
            
        user_query = st.text_input(
            "Enter your financial query:", 
            value="Identify all companies with a Debt-to-Equity ratio greater than 1.0, and calculate their average Default_Risk_Score."
        )
        
        if st.button("Run Quantitative Analysis", type="primary"):
            with st.spinner("AI analyst is writing and executing Python code..."):
                
                # Define execution tool
                def run_financial_analysis(python_code: str):
                    try:
                        local_vars = {"df": df, "pd": pd}
                        exec(python_code, {}, local_vars)
                        return str(local_vars.get("result", "Code executed successfully, no 'result' variable found."))
                    except Exception as e:
                        return f"Error executing code: {str(e)}"
                
                tools_metadata = [
                    {
                        "type": "function",
                        "function": {
                            "name": "run_financial_analysis",
                            "description": "Execute pandas code on financial dataframe 'df'. Columns: Company, Sector, Quarter, Revenue_Millions, Net_Income_Millions, Total_Debt_Millions, Total_Equity_Millions, Operating_Cash_Flow_M, Default_Risk_Score. Assign output to 'result'.",
                            "parameters": {
                                "type": "object",
                                "properties": {"python_code": {"type": "string"}},
                                "required": ["python_code"],
                            },
                        },
                    }
                ]
                
                messages = [
                    {"role": "system", "content": "You are a Senior FinTech Quantitative Analyst AI. Write clean pandas code to answer financial queries."},
                    {"role": "user", "content": user_query}
                ]
                
                # Agent loop
                output_answer = ""
                executed_code = ""
                for _ in range(3):
                    response = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=messages,
                        tools=tools_metadata,
                        tool_choice="auto",
                    )
                    msg = response.choices[0].message
                    messages.append(msg)
                    
                    if not msg.tool_calls:
                        output_answer = msg.content
                        break
                        
                    for tool_call in msg.tool_calls:
                        args = json.loads(tool_call.function.arguments)
                        executed_code = args.get("python_code")
                        tool_res = run_financial_analysis(**args)
                        
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_call.function.name,
                            "content": tool_res
                        })
                
                if executed_code:
                    st.code(executed_code, language="python")
                st.success("Analysis Complete!")
                st.markdown("### Executive Risk Report")
                st.write(output_answer)
    else:
        st.error("Dataset `fintech_portfolio.csv` not found in your workspace folder!")

# --- TAB 2: AUDIT DOCUMENT RAG SEARCH ---
with tab2:
    st.subheader("Corporate Audit & Compliance Knowledge Base")
    st.markdown("Search through confidential auditor notes, compliance guidelines, and risk memos using semantic vector search.")
    
    rag_query = st.text_input("Ask a compliance or audit question:", value="What are the audit findings for PayPulse?")
    
    if st.button("Search Audit Records", type="primary"):
        with st.spinner("Searching vector database..."):
            results = collection.query(query_texts=[rag_query], n_results=2)
            retrieved_docs = results['documents'][0] if results['documents'] else []
            
            # Generate grounded response
            rag_prompt = f"Answer the user question strictly using the following audit documents:\n\nDocuments:\n" + "\n".join(retrieved_docs) + f"\n\nQuestion: {rag_query}"
            
            completion = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role": "user", "content": rag_prompt}]
            )
            
            st.markdown("### 📋 Retrieved Audit Evidence")
            for i, doc in enumerate(retrieved_docs):
                st.info(f"**Evidence Chunk {i+1}:** {doc}")
                
            st.markdown("### 💡 AI Compliance Summary")
            st.write(completion.choices[0].message.content)