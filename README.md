# 🚀 Production AI Engineering & Generative AI Portfolio

A production-grade collection of generative AI applications, autonomous multi-agent systems, hybrid Retrieval-Augmented Generation (RAG) pipelines, Model Context Protocol (MCP) servers, and interactive financial/risk intelligence dashboards built using Python, Groq LLMs, ChromaDB, LangGraph, and Streamlit.

🌐 **Live Demos:** 
* [Interactive Fintech AI App](https://ai-engineering-portfolio-561.streamlit.app/) *(Live Streamlit Cloud Deployment)*
* [Risk & Fraud Analytics Dashboard](https://ai-engineering-portfolio-riskdashboard561.streamlit.app/) *(Live Streamlit Cloud Deployment)*

---

## 🏗️ Key Projects & Architecture

### 1. Interactive Fintech AI App (`fintech_app.py`)
* **Description:** An interactive Streamlit web application designed for financial data analysis, live market query handling, and conversational intelligence.
* **Key Features:** Clean UI state management, real-time response generation, and structured financial query processing over portfolio datasets (`fintech_portfolio.csv`).
* **🌐 Live URL:** [View Deployed App](https://ai-engineering-portfolio-561.streamlit.app/)

### 2. Risk & Fraud Analytics Dashboard (`risk_dashboard.py`)
* **Description:** An automated executive risk dashboard rendering real-time Plotly visualizations for transaction anomaly metrics, Account Takeover (ATO) trends, and fraud operational controls.
* **Key Features:** Large-scale Pandas aggregation, dynamic metric filtering, and live chart rendering.
* **🌐 Live URL:** [View Deployed App](https://ai-engineering-portfolio-riskdashboard561.streamlit.app/)

### 3. Autonomous Multi-Agent Systems (`super_agent.py` & `ai_agent.py`)
* **Description:** Specialized multi-agent architectures capable of multi-step task execution, automated reasoning loops, and tool orchestration.
* **Key Features:** Structured tool-calling execution, robust exception handling, and low-latency inference.

### 4. Hybrid RAG & Advanced Search Pipeline (`rag_pipeline.py` & `test_hybrid_search.py`)
* **Description:** High-precision retrieval engine combining ChromaDB vector search with BM25 keyword matching via Reciprocal Rank Fusion (RRF).
* **Key Features:** Dense and sparse retrieval integration, local embedding storage, and precise document chunking.

### 5. MCP Server & Observability (`fraud_mcp_server.py` & `test_observability.py`)
* **Description:** Production Model Context Protocol (MCP) server implementation and Langfuse LLM telemetry integration.
* **Key Features:** Secure tool endpoint exposure, token cost tracking, and execution latency tracing.

---

## 🛠️ Tech Stack & Tools

* **Core Language:** Python (3.10+)
* **LLM & Inference:** Groq API (High-speed Llama 3 inference engine)
* **Agent Frameworks & Protocols:** LangGraph, Model Context Protocol (MCP), Custom Tool-Calling
* **Vector Database & Search:** ChromaDB, BM25, Reciprocal Rank Fusion (RRF)
* **Data Engineering & Big Data:** Pandas, NumPy, Apache Parquet (1M+ rows)
* **Observability & Tracing:** Langfuse
* **Frameworks & UI:** Streamlit, Plotly
* **Configuration & Security:** `python-dotenv` (Environment-secured secret management)
* **Version Control:** Git & GitHub

---

## 📂 Repository Structure

ai_engineering_portfolio/
│
├── app.py                           # Core application entry point & router
├── fintech_app.py                   # Streamlit financial intelligence dashboard
├── risk_dashboard.py                # Live risk and fraud analytics dashboard
│
├── ai_agent.py                      # Core tool-calling agent implementation
├── super_agent.py                   # Advanced multi-agent orchestrator
├── fraud_mcp_server.py              # Model Context Protocol (MCP) server
├── tool_calling.py                  # Function calling schemas and utilities
│
├── rag_pipeline.py                  # RAG retrieval and vector generation pipeline
├── test_hybrid_search.py            # BM25 + ChromaDB Hybrid Search with RRF
├── test_chroma.py                   # Vector store diagnostics and test script
├── test_langgraph.py                # Stateful graph agent validation
├── test_observability.py            # Langfuse LLM telemetry and tracing test
│
├── generate_and_analyze_bigdata.py  # Big data generator and processing pipeline
├── fraud_million_rows.parquet       # 1M+ row columnar dataset for performance testing
├── fintech_portfolio.csv            # Financial portfolio sample dataset
│
├── test_ai.py                       # API connection and model validation script
├── requirements.txt                 # Project dependencies
├── .env.example                     # Template for environment variables
└── README.md                        # Documentation

## ⚙️ Getting Started & Installation Instructions

Anyone who wants to clone, set up, and run this repository locally can execute the following steps in their terminal:

### Step 1: Clone the Repository

```bash
git clone [https://github.com/rahulsrinivas561-collab/ai-engineering-portfolio.git](https://github.com/rahulsrinivas561-collab/ai-engineering-portfolio.git)

cd ai-engineering-portfolio

Step 2: Set Up Virtual Environment & Install Dependencies

# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell):
venv\Scripts\Activate.ps1

# Activate on macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt

Step 3: Configure Environment Variables
Create a file named .env in the root folder and add your API keys:

GROQ_API_KEY=your_actual_groq_api_key_here
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key_here
LANGFUSE_SECRET_KEY=your_langfuse_secret_key_here





