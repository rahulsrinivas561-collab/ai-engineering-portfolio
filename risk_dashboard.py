import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field
import json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Page Configuration
st.set_page_config(
    page_title="Risk & Fraud Operations Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# 1. Load the 1 Million Rows from Parquet using Caching
@st.cache_data
def load_risk_data():
    return pd.read_parquet("fraud_million_rows.parquet")

df = load_risk_data()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Filter Risk Controls")
selected_risk = st.sidebar.selectbox("Filter by Risk Level", ["All", "High", "Medium", "Low"])
search_id = st.sidebar.text_input("Search Transaction ID Prefix", "")

# Filter Dataframe based on inputs (Handling large data efficiently)
filtered_df = df.copy()
if selected_risk == "High":
    filtered_df = filtered_df[filtered_df["risk_score"] > 0.7]
elif selected_risk == "Medium":
    filtered_df = filtered_df[(filtered_df["risk_score"] > 0.4) & (filtered_df["risk_score"] <= 0.7)]
elif selected_risk == "Low":
    filtered_df = filtered_df[filtered_df["risk_score"] <= 0.4]

if search_id:
    filtered_df = filtered_df[filtered_df["transaction_id"].str.contains(search_id.upper())]

# --- MAIN DASHBOARD HEADER ---
st.title("🛡️ Enterprise Risk & Fraud Intelligence Dashboard")
st.markdown("Real-time transaction monitoring across **1 Million Rows**, risk anomaly detection, and automated LLM audits.")
st.markdown("---")

# --- TOP METRICS ROW ---
total_txns = len(df)
high_risk_df = df[df["risk_score"] > 0.7]
high_risk_count = len(high_risk_df)
total_high_risk_volume = high_risk_df["amount"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Monitored Transactions", f"{total_txns:,}")
col2.metric("High Risk Alerts (>0.7)", f"{high_risk_count:,}")
col3.metric("High Risk Volume (INR)", f"₹{total_high_risk_volume:,.2f}")
col4.metric("System Status", "🟢 Operational", "DuckDB + Parquet Active")

st.markdown("### 📊 Live Transaction Audit Log (Showing Filtered Subset)")
st.dataframe(filtered_df.head(100), use_container_width=True) # Displaying first 100 rows of filtered data for snappy UI rendering

# --- VISUALIZATION SECTION ---
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Risk Exposure by Category")
    cat_summary = high_risk_df.groupby("category")["amount"].sum().reset_index()
    fig_pie = px.pie(cat_summary, names="category", values="amount", title="High-Risk Volume by Category", hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_chart2:
    st.subheader("Transaction Amount vs Risk Score Sample")
    sample_chart_df = df.sample(n=1000, random_state=42) # Sample 1000 for smooth scatter plot
    fig_scatter = px.scatter(sample_chart_df, x="risk_score", y="amount", color="category", title="Risk Score vs Amount (Sampled)")
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# --- LLM AUTOMATED AUDIT INSPECTOR ---
st.subheader("🤖 AI Risk Auditor & Automated Note Parser")
st.markdown("Select a sample transaction ID to generate an instant structured Pydantic audit report.")

sample_tx_id = high_risk_df["transaction_id"].iloc[0] if not high_risk_df.empty else "TXN_0000001"
user_note_input = st.text_area("Transaction Risk Notes:", value=f"ALERT: Transaction {sample_tx_id} flagged for abnormal payment velocity and unrecognized device fingerprint.", height=100)

class PydanticAuditSchema(BaseModel):
    transaction_id: str = Field(description="The transaction ID")
    is_fraudulent: bool = Field(description="True if high risk")
    recommended_action: str = Field(description="Action like 'Block account', 'Manual Review', or 'Approve'")
    rationale: str = Field(description="Brief reason for the decision")

if st.button("🚀 Run AI Audit Inspection"):
    with st.spinner("Analyzing risk notes with LLM + Pydantic..."):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a strict risk analyst. Extract data into this exact JSON schema: {json.dumps(PydanticAuditSchema.model_json_schema())}"
                    },
                    {"role": "user", "content": user_note_input}
                ],
                response_format={"type": "json_object"}
            )
            
            raw_json = response.choices[0].message.content
            audit_result = PydanticAuditSchema.model_validate_json(raw_json)
            
            st.success("Audit Complete!")
            st.json(audit_result.model_dump())
            
        except Exception as e:
            st.error(f"Error executing LLM audit: {e}")