AI Engineering & Generative AI Portfolio
A production-grade collection of generative AI applications, autonomous multi-agent systems, Retrieval-Augmented Generation (RAG) pipelines, and interactive financial intelligence tools built using Python, Groq LLMs, and Streamlit.

Key Projects & Architecture
1. Interactive Fintech AI App (fintech_app.py)
Description: An interactive Streamlit web application designed for financial data analysis, live market query handling, and conversational intelligence.

Key Features: Clean UI state management, real-time response generation, and structured financial query processing.

2. Autonomous Multi-Agent Systems (super_agent.py & ai_agent.py)
Description: Specialized multi-agent architectures capable of multi-step task execution, automated reasoning loops, and tool orchestration.

Key Features: Structured tool-calling execution, robust exception handling, and low-latency inference.

3. Retrieval-Augmented Generation Pipeline (rag_pipeline.py)
Description: A vector-backed knowledge retrieval system designed to ground LLM responses in factual, domain-specific document contexts.

Key Features: Local vector embedding storage (ChromaDB), efficient context injection, and precise document chunking.

Tech Stack & Tools
Core Language: Python

LLM & Inference: Groq API (High-speed LLM inference engine)

Frameworks & UI: Streamlit, Custom Agent Workflows

Vector Database: ChromaDB

Configuration & Security: python-dotenv (Environment-secured secret management)

Version Control: Git & GitHub

Repository Structure

`ai_projects/
│
├── fintech_app.py        # Streamlit financial intelligence dashboard
├── super_agent.py        # Advanced multi-agent orchestrator
├── ai_agent.py           # Core tool-calling agent implementation
├── rag_pipeline.py       # RAG retrieval and vector generation pipeline
├── test_ai.py            # API connection and model validation script
├── requirements.txt      # Project dependencies
├── .env.example          # Template for environment variables
└── README.md             # Project documentation

⚙️ Getting Started & Installation Instructions
Anyone who wants to clone, set up, and run this repository locally can execute the following steps in their terminal:

Step 1: Clone the Repository

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
Create a file named .env in the root folder and add your Groq API key:

GROQ_API_KEY=your_actual_groq_api_key_here

Step 4: Run the Applications
Run the Streamlit Fintech Web App:

python -m streamlit run fintech_app.py

Run Multi-Agent or RAG Pipelines:

python super_agent.py
python ai_agent.py
python rag_pipeline.py

Verify API Connection:

python test_ai.py
