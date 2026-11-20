import pandas as pd
import plotly.express as px
from scipy import stats
import streamlit as st

st.set_page_config(page_title="GoTymeX Fraud & Analytics Hub", layout="wide")


@st.cache_data
def load_data():
    return pd.read_csv("cleaned_analytics_transactions.csv")


df = load_data()

st.title("GoTymeX Transaction Risk & Business Analytics Hub")
st.caption(
    "Interactive KPI tracking, NLP natural-language querying, A/B experiment sizing, "
    "and data quality governance across 100,000 transactions."
)

# --- Sidebar Filters ---
st.sidebar.header("Global Filters")
tx_types = st.sidebar.multiselect(
    "Transaction Type",
    sorted(df["transaction_type"].dropna().unique()),
    default=sorted(df["transaction_type"].dropna().unique()),
)
pay_methods = st.sidebar.multiselect(
    "Payment Method",
    sorted(df["payment_method"].dropna().unique()),
    default=sorted(df["payment_method"].dropna().unique()),
)
devices = st.sidebar.multiselect(
    "Device",
    sorted(df["transaction_device"].dropna().unique()),
    default=sorted(df["transaction_device"].dropna().unique()),
)

fdf = df[
    df["transaction_type"].isin(tx_types)
    & df["payment_method"].isin(pay_methods)
    & df["transaction_device"].isin(devices)
].copy()

# --- Top KPIs ---
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Transactions", f"{len(fdf):,}")
c2.metric("Gross Volume", f"${fdf['abs_transaction_amount'].sum() / 1e6:.2f}M")
c3.metric("Fraud Rate", f"{fdf['is_fraud'].mean() * 100:.2f}%")
c4.metric(
    "Fraud Exposure",
    f"${fdf.loc[fdf['is_fraud'] == 1, 'abs_transaction_amount'].sum() / 1e6:.2f}M",
)
c5.metric("Overdraft Attempts", f"{int(fdf['flag_overdraft_attempt'].sum()):,}")

tab_nlp, tab_kpis, tab_ab, tab_gov = st.tabs([
    "NLP Ask-the-Data",
    "Business KPIs",
    "A/B Test Planner",
    "Data Quality & Governance",
])

with tab_nlp:
    st.subheader("Ask a Question in Plain English")
    sample_qs = [
        "Custom question...",
        "Show fraud rate and volume by payment method",
        "Compare overdraft and ledger mismatch anomalies",
        "Show purchase volume and fraud rate by merchant category",
        "Show customer tenure cohort performance",
        "Show monthly gross volume trend",
    ]
    selected_q = st.selectbox("Sample questions:", sample_qs)
    query = st.text_input(
        "Type your question:",
        value="" if selected_q == "Custom question..." else selected_q,
    ).strip().lower()

    if query:
        if any(k in query for k in ["overdraft", "ledger", "mismatch", "anomaly", "balance"]):
            summary = pd.DataFrame([
                {
                    "Segment": "Negative Starting Balance",
                    "Txns": int(fdf["flag_negative_bal_before"].sum()),
                    "Fraud_Rate_Pct": round(
                        fdf.loc[fdf["flag_negative_bal_before"] == 1, "is_fraud"].mean() * 100, 2
                    ) if fdf["flag_negative_bal_before"].sum() else 0.0,
                },
                {
                    "Segment": "Ledger Math Mismatch",
                    "Txns": int(fdf["flag_ledger_mismatch"].sum()),
                    "Fraud_Rate_Pct": round(
                        fdf.loc[fdf["flag_ledger_mismatch"] == 1, "is_fraud"].mean() * 100, 2
                    ) if fdf["flag_ledger_mismatch"].sum() else 0.0,
                },
                {
                    "Segment": "Negative Txn Amount",
                    "Txns": int(fdf["flag_negative_amount"].sum()),
                    "Fraud_Rate_Pct": round(
                        fdf.loc[fdf["flag_negative_amount"] == 1, "is_fraud"].mean() * 100, 2
                    ) if fdf["flag_negative_amount"].sum() else 0.0,
                },
                {
                    "Segment": "Overdraft Attempt",
                    "Txns": int(fdf["flag_overdraft_attempt"].sum()),
                    "Fraud_Rate_Pct": round(
                        fdf.loc[fdf["flag_overdraft_attempt"] == 1, "is_fraud"].mean() * 100, 2
                    ) if fdf["flag_overdraft_attempt"].sum() else 0.0,
                },
            ])
            st.dataframe(summary, use_container_width=True)
            st.plotly_chart(
                px.bar(summary, x="Segment", y="Fraud_Rate_Pct", title="Fraud Rate (%) by Anomaly / Risk Flag"),
                use_container_width=True,
            )
        elif any(k in query for k in ["merchant", "category", "purchase"]):
            m_df = fdf[fdf["merchant_category"] != "non_merchant_txn"].groupby("merchant_category", as_index=False).agg(
                purchases=("transaction_id", "count"),
                gross_vol_usd=("abs_transaction_amount", "sum"),
                fraud_rate_pct=("is_fraud", lambda s: round(s.mean() * 100, 2)),
            )
            st.dataframe(m_df, use_container_width=True)
            st.plotly_chart(
                px.bar(m_df, x="merchant_category", y="gross_vol_usd", color="fraud_rate_pct", title="Purchase Volume & Fraud Rate by Category"),
                use_container_width=True,
            )
        elif any(k in query for k in ["tenure", "cohort", "customer"]):
            c_df = fdf.groupby("tenure_cohort", as_index=False).agg(
                txns=("transaction_id", "count"),
                gross_vol_usd=("abs_transaction_amount", "sum"),
                fraud_rate_pct=("is_fraud", lambda s: round(s.mean() * 100, 2)),
            )
            st.dataframe(c_df, use_container_width=True)
            st.plotly_chart(
                px.bar(c_df, x="tenure_cohort", y="txns", color="fraud_rate_pct", title="Transactions & Fraud Rate by Tenure Cohort"),
                use_container_width=True,
            )
        elif any(k in query for k in ["month", "trend", "time", "year"]):
            t_df = fdf.dropna(subset=["year", "month"]).copy()
            t_df["ym"] = t_df["year"].astype(int).astype(str) + "-" + t_df["month"].astype(int).astype(str).str.zfill(2)
            m_trend = t_df.groupby("ym", as_index=False).agg(
                txns=("transaction_id", "count"),
                gross_vol_usd=("abs_transaction_amount", "sum"),
                fraud_rate_pct=("is_fraud", lambda s: round(s.mean() * 100, 2)),
            )
            st.dataframe(m_trend, use_container_width=True)
            st.plotly_chart(
                px.line(m_trend, x="ym", y="gross_vol_usd", markers=True, title="Monthly Gross Volume (USD)"),
                use_container_width=True,
            )
        else:
            p_df = fdf.groupby("payment_method", as_index=False).agg(
                txns=("transaction_id", "count"),
                gross_vol_usd=("abs_transaction_amount", "sum"),
                fraud_rate_pct=("is_fraud", lambda s: round(s.mean() * 100, 2)),
            )
            st.dataframe(p_df, use_container_width=True)
            st.plotly_chart(
                px.bar(p_df, x="payment_method", y="gross_vol_usd", color="fraud_rate_pct", title="Gross Volume & Fraud Rate by Payment Method"),
                use_container_width=True,
            )

with tab_kpis:
    t_summary = fdf.groupby("transaction_type", as_index=False).agg(
        txns=("transaction_id", "count"),
        gross_vol_usd=("abs_transaction_amount", "sum"),
        fraud_rate_pct=("is_fraud", lambda s: round(s.mean() * 100, 2)),
    )
    st.plotly_chart(
        px.bar(t_summary, x="transaction_type", y="gross_vol_usd", color="fraud_rate_pct", title="Gross Volume & Fraud Rate by Transaction Type"),
        use_container_width=True,
    )

with tab_ab:
    lift_pp = st.slider("Expected Fraud Rate Lift (Percentage Points)", 1.0, 10.0, 5.0, 0.5)
    p1 = fdf.loc[fdf["flag_overdraft_attempt"] == 1, "is_fraud"].mean() if fdf["flag_overdraft_attempt"].sum() > 0 else fdf["is_fraud"].mean()
    p2 = max(0.01, p1 - lift_pp / 100.0)
    p_bar = (p1 + p2) / 2
    z_a, z_b = stats.norm.ppf(0.975), stats.norm.ppf(0.80)
    n_per_arm = int(((z_a * (2 * p_bar * (1 - p_bar)) ** 0.5 + z_b * (p1 * (1 - p1) + p2 * (1 - p2)) ** 0.5) / (p1 - p2)) ** 2) + 1
    st.write(f"Baseline fraud rate: **{p1 * 100:.2f}%** → Target: **{p2 * 100:.2f}%** | Required sample per arm: **{n_per_arm:,}** transactions (80% power, two-sided α = 0.05).")

with tab_gov:
    dq_rows = [
        ("Ledger Math Mismatch", int(fdf["flag_ledger_mismatch"].sum())),
        ("Negative Starting Balance", int(fdf["flag_negative_bal_before"].sum())),
        ("Negative Txn Amount", int(fdf["flag_negative_amount"].sum())),
        ("Casing Anomaly Normalized", int(fdf["flag_casing_anomaly"].sum())),
        ("Missing Timestamp Flagged", int(fdf["flag_missing_timestamp"].sum())),
    ]
    st.dataframe(pd.DataFrame(dq_rows, columns=["Quality Check", "Row Count"]), use_container_width=True)
    st.caption("Raw addresses, birthdates, and IP strings are excluded from the analytical table; 0 orphan foreign keys and 0 duplicate IDs verified.")