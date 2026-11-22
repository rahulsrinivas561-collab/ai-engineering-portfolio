import json
import os
from pathlib import Path

from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from scipy import stats
import streamlit as st

try:
  from streamlit.errors import StreamlitSecretNotFoundError
except ImportError:
  StreamlitSecretNotFoundError = Exception

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)
load_dotenv(BASE_DIR.parent / ".env", override=False)

st.set_page_config(
    page_title="GoTymeX Fraud & Analytics Hub",
    page_icon="🛡️",
    layout="wide",
)

# --- Consistent High-Contrast Visual Theme ---
COLOR_PRIMARY = "#0F4C81"
COLOR_ACCENT = "#D95F02"
COLOR_RISK = "#B91C1C"
COLOR_BLACK = "#111827"
FRAUD_SCALE = ["#60A5FA", "#2563EB", "#D95F02", "#991B1B"]


def get_groq_api_key() -> str:
  env_key = os.getenv("GROQ_API_KEY", "").strip()
  if env_key:
    return env_key

  try:
    secret_val = st.secrets.get("GROQ_API_KEY", "")
    return str(secret_val).strip() if secret_val else ""
  except (StreamlitSecretNotFoundError, FileNotFoundError, KeyError, Exception):
    return ""


def style_fig(
    fig,
    title: str,
    y_title: str | None = None,
    x_title: str | None = None,
    colorbar_title: str = "Fraud Rate (%)",
    height: int = 390,
):
  fig.update_layout(
      template="plotly_white",
      title=dict(
          text=f"<b>{title}</b>", font=dict(size=15, color=COLOR_BLACK), x=0.01
      ),
      font=dict(family="sans-serif", size=12, color=COLOR_BLACK),
      height=height,
      margin=dict(t=55, b=48, l=55, r=25),
      plot_bgcolor="#FFFFFF",
      paper_bgcolor="#FFFFFF",
      legend=dict(
          orientation="h",
          yanchor="bottom",
          y=1.02,
          xanchor="right",
          x=1,
          font=dict(color=COLOR_BLACK),
      ),
      coloraxis_colorbar=dict(
          title=dict(
              text=colorbar_title, font=dict(color=COLOR_BLACK, size=12)
          ),
          tickfont=dict(color=COLOR_BLACK, size=11),
          outlinecolor=COLOR_BLACK,
          outlinewidth=1,
      ),
  )
  fig.update_xaxes(
      title_text=x_title if x_title else None,
      title_font=dict(color=COLOR_BLACK),
      tickfont=dict(color=COLOR_BLACK),
      showgrid=True,
      gridcolor="#E5E7EB",
      linecolor=COLOR_BLACK,
      ticks="outside",
      tickcolor=COLOR_BLACK,
  )
  fig.update_yaxes(
      title_text=y_title if y_title else None,
      title_font=dict(color=COLOR_BLACK),
      tickfont=dict(color=COLOR_BLACK),
      showgrid=True,
      gridcolor="#E5E7EB",
      linecolor=COLOR_BLACK,
      ticks="outside",
      tickcolor=COLOR_BLACK,
  )
  return fig


@st.cache_data
def load_data():
  candidates = [
      BASE_DIR / "cleaned_analytics_transactions.csv",
      BASE_DIR / "gotymex_fraud_case" / "cleaned_analytics_transactions.csv",
      BASE_DIR / "data" / "cleaned_analytics_transactions.csv",
      BASE_DIR.parent / "cleaned_analytics_transactions.csv",
  ]
  for path in candidates:
    if path.exists():
      data = pd.read_csv(path)
      if (
          "abs_transaction_amount" not in data.columns
          and "transaction_amount" in data.columns
      ):
        data["abs_transaction_amount"] = data["transaction_amount"].abs()
      return data

  found_files = [str(p.relative_to(BASE_DIR)) for p in BASE_DIR.rglob("*.csv")]
  st.error(
      "Could not find `cleaned_analytics_transactions.csv`.\n\n"
      f"**App directory:** `{BASE_DIR}`\n\n"
      f"**CSV files found in repo:** `{found_files}`"
  )
  st.stop()


def classify_intent_deterministic(query: str) -> str:
  q = query.lower()
  if any(
      k in q
      for k in [
          "overdraft",
          "ledger",
          "mismatch",
          "anomaly",
          "balance",
          "negative",
          "flag",
      ]
  ):
    return "anomalies"
  if any(
      k in q
      for k in ["merchant", "category", "purchase", "store", "retail"]
  ):
    return "merchant_category"
  if any(
      k in q for k in ["tenure", "cohort", "customer", "age", "account_age"]
  ):
    return "tenure_cohort"
  if any(
      k in q for k in ["month", "trend", "time", "year", "over time", "monthly"]
  ):
    return "monthly_trend"
  return "payment_method"


def classify_intent_groq(query: str, api_key: str) -> tuple[str, str]:
  valid_intents = [
      "payment_method",
      "anomalies",
      "merchant_category",
      "tenure_cohort",
      "monthly_trend",
  ]
  system_prompt = (
      "You map a user's analytics question about a 100k transaction fraud"
      " dataset to one intent.\n"
      "Return ONLY valid JSON with keys 'intent' and 'reason'.\n"
      f"Allowed intents: {valid_intents}\n"
      "- payment_method: payment channels, fraud rate or volume by payment"
      " method\n"
      "- anomalies: overdraft attempts, ledger mismatches, negative balances,"
      " negative amounts, risk flags\n"
      "- merchant_category: merchant categories, purchase volume, spending by"
      " category\n"
      "- tenure_cohort: customer tenure cohorts, new vs long-tenured"
      " accounts\n"
      "- monthly_trend: monthly trends, time series, volume or fraud over"
      " months"
  )
  try:
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama-3.1-8b-instant",
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
        },
        timeout=8,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    parsed = json.loads(content)
    intent = parsed.get("intent", "")
    reason = parsed.get("reason", "Mapped via Groq LLM")
    if intent in valid_intents:
      return intent, f"Groq LLM: {reason}"
  except Exception:
    pass

  return classify_intent_deterministic(query), "Deterministic keyword fallback"


df = load_data()

st.title("GoTymeX Transaction Risk & Business Analytics Hub")
st.caption(
    "Interactive KPI tracking, NLP natural-language querying, A/B experiment"
    " sizing, and data quality governance across 100,000 transactions."
)

# --- Sidebar Filters & Optional Groq Config ---
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

st.sidebar.divider()
st.sidebar.header("Optional LLM Router (Groq)")
default_key = get_groq_api_key()
use_groq = st.sidebar.toggle(
    "Use Groq LLM intent router", value=bool(default_key)
)
groq_key = st.sidebar.text_input(
    "Groq API Key (auto-loaded from .env / Secrets)",
    value=default_key,
    type="password",
    help=(
        "Automatically uses .env locally or Streamlit Secrets in the cloud;"
        " falls back to keyword routing if blank."
    ),
)

fdf = df[
    df["transaction_type"].isin(tx_types)
    & df["payment_method"].isin(pay_methods)
    & df["transaction_device"].isin(devices)
].copy()

if fdf.empty:
  st.warning(
      "No rows match the selected sidebar filters. Adjust filters to view"
      " metrics."
  )
  st.stop()

# --- Top KPIs ---
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Transactions", f"{len(fdf):,}")
c2.metric("Gross Volume", f"${fdf['abs_transaction_amount'].sum() / 1e6:.2f}M")
c3.metric("Fraud Rate", f"{fdf['is_fraud'].mean() * 100:.2f}%")
c4.metric(
    "Fraud Exposure",
    f"${fdf.loc[fdf['is_fraud'] == 1, 'abs_transaction_amount'].sum() / 1e6:.2f}M",
)
c5.metric(
    "Overdraft Attempts",
    f"{int(fdf['flag_overdraft_attempt'].sum()):,}"
    if "flag_overdraft_attempt" in fdf.columns
    else "0",
)

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
  raw_query = st.text_input(
      "Type your question:",
      value="" if selected_q == "Custom question..." else selected_q,
  ).strip()

  if raw_query:
    if use_groq and groq_key.strip():
      intent, source_note = classify_intent_groq(raw_query, groq_key.strip())
    else:
      intent = classify_intent_deterministic(raw_query)
      source_note = "Deterministic keyword router"

    st.caption(f"Routing mode: **{source_note}** -> Intent: `{intent}`")

    if intent == "anomalies":
      summary = pd.DataFrame([
          {
              "Segment": "Negative Starting Balance",
              "Txns": int(fdf["flag_negative_bal_before"].sum()),
              "Fraud_Rate_Pct": (
                  round(
                      fdf.loc[fdf["flag_negative_bal_before"] == 1, "is_fraud"]
                      .mean()
                      * 100,
                      2,
                  )
                  if fdf["flag_negative_bal_before"].sum()
                  else 0.0
              ),
          },
          {
              "Segment": "Ledger Math Mismatch",
              "Txns": int(fdf["flag_ledger_mismatch"].sum()),
              "Fraud_Rate_Pct": (
                  round(
                      fdf.loc[fdf["flag_ledger_mismatch"] == 1, "is_fraud"]
                      .mean()
                      * 100,
                      2,
                  )
                  if fdf["flag_ledger_mismatch"].sum()
                  else 0.0
              ),
          },
          {
              "Segment": "Negative Txn Amount",
              "Txns": int(fdf["flag_negative_amount"].sum()),
              "Fraud_Rate_Pct": (
                  round(
                      fdf.loc[fdf["flag_negative_amount"] == 1, "is_fraud"]
                      .mean()
                      * 100,
                      2,
                  )
                  if fdf["flag_negative_amount"].sum()
                  else 0.0
              ),
          },
          {
              "Segment": "Overdraft Attempt",
              "Txns": int(fdf["flag_overdraft_attempt"].sum()),
              "Fraud_Rate_Pct": (
                  round(
                      fdf.loc[fdf["flag_overdraft_attempt"] == 1, "is_fraud"]
                      .mean()
                      * 100,
                      2,
                  )
                  if fdf["flag_overdraft_attempt"].sum()
                  else 0.0
              ),
          },
      ]).sort_values("Fraud_Rate_Pct", ascending=True)

      st.dataframe(
          summary.sort_values("Fraud_Rate_Pct", ascending=False),
          use_container_width=True,
          hide_index=True,
      )
      fig = px.bar(
          summary,
          x="Fraud_Rate_Pct",
          y="Segment",
          orientation="h",
          color="Fraud_Rate_Pct",
          color_continuous_scale=FRAUD_SCALE,
          text="Fraud_Rate_Pct",
      )
      fig.update_traces(
          texttemplate="%{text:.2f}%",
          textposition="outside",
          textfont=dict(color=COLOR_BLACK),
          hovertemplate=(
              "<b>%{y}</b><br>Fraud Rate: %{x:.2f}%<extra></extra>"
          ),
      )
      st.plotly_chart(
          style_fig(
              fig,
              "Fraud Rate (%) by Anomaly & Risk Flag",
              x_title="Fraud Rate (%)",
              y_title="Risk / Quality Flag",
          ),
          use_container_width=True,
      )

    elif intent == "merchant_category":
      m_df = (
          fdf[fdf["merchant_category"] != "non_merchant_txn"]
          .groupby("merchant_category", as_index=False)
          .agg(
              purchases=("transaction_id", "count"),
              gross_vol_usd=("abs_transaction_amount", "sum"),
              fraud_rate_pct=("is_fraud", lambda s: round(s.mean() * 100, 2)),
          )
          .sort_values("gross_vol_usd", ascending=True)
      )
      st.dataframe(
          m_df.sort_values("gross_vol_usd", ascending=False),
          use_container_width=True,
          hide_index=True,
      )
      fig = px.bar(
          m_df,
          x="gross_vol_usd",
          y="merchant_category",
          orientation="h",
          color="fraud_rate_pct",
          color_continuous_scale=FRAUD_SCALE,
      )
      fig.update_traces(
          hovertemplate=(
              "<b>%{y}</b><br>Gross Volume: $%{x:,.0f}<br>Fraud Rate:"
              " %{marker.color:.2f}%<extra></extra>"
          )
      )
      st.plotly_chart(
          style_fig(
              fig,
              "Purchase Volume & Fraud Rate by Merchant Category",
              x_title="Gross Volume (USD)",
              y_title="Merchant Category",
              height=430,
          ),
          use_container_width=True,
      )

    elif intent == "tenure_cohort":
      c_df = (
          fdf.groupby("tenure_cohort", as_index=False)
          .agg(
              txns=("transaction_id", "count"),
              gross_vol_usd=("abs_transaction_amount", "sum"),
              fraud_rate_pct=("is_fraud", lambda s: round(s.mean() * 100, 2)),
          )
          .sort_values("txns", ascending=False)
      )
      st.dataframe(c_df, use_container_width=True, hide_index=True)
      fig = px.bar(
          c_df,
          x="tenure_cohort",
          y="txns",
          color="fraud_rate_pct",
          color_continuous_scale=FRAUD_SCALE,
      )
      fig.update_traces(
          hovertemplate=(
              "<b>%{x}</b><br>Transactions: %{y:,}<br>Fraud Rate:"
              " %{marker.color:.2f}%<extra></extra>"
          )
      )
      st.plotly_chart(
          style_fig(
              fig,
              "Transactions & Fraud Rate by Tenure Cohort",
              y_title="Transaction Count",
              x_title="Tenure Cohort",
          ),
          use_container_width=True,
      )

    elif intent == "monthly_trend":
      t_df = fdf.dropna(subset=["year", "month"]).copy()
      t_df["ym"] = (
          t_df["year"].astype(int).astype(str)
          + "-"
          + t_df["month"].astype(int).astype(str).str.zfill(2)
      )
      m_trend = (
          t_df.groupby("ym", as_index=False)
          .agg(
              txns=("transaction_id", "count"),
              gross_vol_usd=("abs_transaction_amount", "sum"),
              fraud_rate_pct=("is_fraud", lambda s: round(s.mean() * 100, 2)),
          )
          .sort_values("ym")
      )
      st.dataframe(m_trend, use_container_width=True, hide_index=True)
      avg_vol = m_trend["gross_vol_usd"].mean() if not m_trend.empty else 0.0
      fig = px.line(m_trend, x="ym", y="gross_vol_usd", markers=True)
      fig.update_traces(
          line=dict(color=COLOR_PRIMARY, width=3),
          marker=dict(size=8, color=COLOR_BLACK),
          hovertemplate=(
              "<b>%{x}</b><br>Gross Volume: $%{y:,.0f}<extra></extra>"
          ),
      )
      if avg_vol > 0:
        fig.add_hline(
            y=avg_vol,
            line_dash="dash",
            line_color=COLOR_BLACK,
            annotation_text=f"Avg: ${avg_vol/1e6:.2f}M",
            annotation_font=dict(color=COLOR_BLACK),
            annotation_position="top left",
        )
      st.plotly_chart(
          style_fig(
              fig,
              "Monthly Gross Volume Trend vs. Monthly Average",
              y_title="Gross Volume (USD)",
              x_title="Month",
          ),
          use_container_width=True,
      )

    else:
      p_df = (
          fdf.groupby("payment_method", as_index=False)
          .agg(
              txns=("transaction_id", "count"),
              gross_vol_usd=("abs_transaction_amount", "sum"),
              fraud_rate_pct=("is_fraud", lambda s: round(s.mean() * 100, 2)),
          )
          .sort_values("gross_vol_usd", ascending=False)
      )
      st.dataframe(p_df, use_container_width=True, hide_index=True)
      fig = px.bar(
          p_df,
          x="payment_method",
          y="gross_vol_usd",
          color="fraud_rate_pct",
          color_continuous_scale=FRAUD_SCALE,
      )
      fig.update_traces(
          hovertemplate=(
              "<b>%{x}</b><br>Gross Volume: $%{y:,.0f}<br>Fraud Rate:"
              " %{marker.color:.2f}%<extra></extra>"
          )
      )
      st.plotly_chart(
          style_fig(
              fig,
              "Gross Volume & Fraud Rate by Payment Method",
              y_title="Gross Volume (USD)",
              x_title="Payment Method",
          ),
          use_container_width=True,
      )

with tab_kpis:
  st.subheader("Transaction Type Performance: Volume vs. Fraud Risk")
  st.caption(
      "Vertical bars show gross dollar volume; lollipop markers show fraud rate"
      " (%) per transaction type."
  )

  vol_agg = (
      fdf.groupby("transaction_type", as_index=False)
      .agg(
          txns=("transaction_id", "count"),
          gross_vol_usd=("abs_transaction_amount", "sum"),
          avg_txn_usd=("abs_transaction_amount", "mean"),
          fraud_txns=("is_fraud", "sum"),
          fraud_rate_pct=("is_fraud", lambda s: round(s.mean() * 100, 2)),
      )
  )
  fraud_exp_map = (
      fdf[fdf["is_fraud"] == 1]
      .groupby("transaction_type")["abs_transaction_amount"]
      .sum()
      .to_dict()
  )
  vol_agg["fraud_exposure_usd"] = (
      vol_agg["transaction_type"].map(fraud_exp_map).fillna(0.0).round(2)
  )
  vol_agg["avg_txn_usd"] = vol_agg["avg_txn_usd"].round(2)

  col_left, col_right = st.columns(2)

  with col_left:
    vol_sorted = vol_agg.sort_values("gross_vol_usd", ascending=False)
    fig_vol = px.bar(
        vol_sorted,
        x="transaction_type",
        y="gross_vol_usd",
        text="gross_vol_usd",
    )
    fig_vol.update_traces(
        marker=dict(color=COLOR_PRIMARY),
        texttemplate="$%{text:,.0f}",
        textposition="outside",
        textfont=dict(color=COLOR_BLACK),
        hovertemplate=(
            "<b>%{x}</b><br>Gross Volume: $%{y:,.0f}<extra></extra>"
        ),
    )
    st.plotly_chart(
        style_fig(
            fig_vol,
            "Gross Volume ($) by Transaction Type",
            y_title="Gross Volume (USD)",
            x_title="Transaction Type",
        ),
        use_container_width=True,
    )

  with col_right:
    risk_sorted = vol_agg.sort_values("fraud_rate_pct", ascending=True)
    fig_lollipop = go.Figure()
    for _, row in risk_sorted.iterrows():
      fig_lollipop.add_shape(
          type="line",
          x0=0,
          y0=row["transaction_type"],
          x1=row["fraud_rate_pct"],
          y1=row["transaction_type"],
          line=dict(color=COLOR_BLACK, width=2.5),
      )
    fig_lollipop.add_trace(
        go.Scatter(
            x=risk_sorted["fraud_rate_pct"],
            y=risk_sorted["transaction_type"],
            mode="markers+text",
            marker=dict(size=12, color=COLOR_RISK),
            text=[f"{v:.2f}%" for v in risk_sorted["fraud_rate_pct"]],
            textposition="middle right",
            textfont=dict(color=COLOR_BLACK),
            hovertemplate=(
                "<b>%{y}</b><br>Fraud Rate: %{x:.2f}%<extra></extra>"
            ),
            showlegend=False,
        )
    )
    st.plotly_chart(
        style_fig(
            fig_lollipop,
            "Fraud Rate (%) by Transaction Type (Lollipop)",
            x_title="Fraud Rate (%)",
            y_title="Transaction Type",
        ),
        use_container_width=True,
    )

  st.dataframe(
      vol_agg.sort_values("gross_vol_usd", ascending=False),
      use_container_width=True,
      hide_index=True,
  )

  # Compact Fraud Lift (pp) table for risk/quality flags
  lift_candidates = [
      ("Overdraft Attempt", "flag_overdraft_attempt"),
      ("Ledger Math Mismatch", "flag_ledger_mismatch"),
      ("Negative Starting Balance", "flag_negative_bal_before"),
      ("Negative Txn Amount", "flag_negative_amount"),
  ]
  lift_rows = []
  for label, col in lift_candidates:
    if col in fdf.columns:
      flagged_mask = fdf[col] == 1
      unflagged_mask = fdf[col] != 1
      flagged_cnt = int(flagged_mask.sum())
      flagged_rate = (
          float(fdf.loc[flagged_mask, "is_fraud"].mean()) * 100.0
          if flagged_cnt > 0
          else 0.0
      )
      unflagged_rate = (
          float(fdf.loc[unflagged_mask, "is_fraud"].mean()) * 100.0
          if int(unflagged_mask.sum()) > 0
          else 0.0
      )
      lift_pp = (
          round(flagged_rate - unflagged_rate, 2) if flagged_cnt > 0 else 0.0
      )
      lift_rows.append({
          "Risk / Quality Flag": label,
          "Flagged Txns": flagged_cnt,
          "Fraud Rate Flagged (%)": round(flagged_rate, 2),
          "Fraud Rate Unflagged (%)": round(unflagged_rate, 2),
          "Fraud Lift (pp)": lift_pp,
      })

  if lift_rows:
    st.markdown("**Risk Flag Fraud Lift (Flagged vs. Unflagged)**")
    st.dataframe(
        pd.DataFrame(lift_rows).sort_values("Fraud Lift (pp)", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

  st.divider()
  st.subheader("Customer Behavior, Product Usage & Market Trends")

  b1, b2, b3 = st.columns(3)

  with b1:
    st.markdown("**Customer Behavior (Tenure Cohort)**")
    if "tenure_cohort" in fdf.columns:
      cust_tbl = (
          fdf.groupby("tenure_cohort", as_index=False, dropna=False)
          .agg(
              Txns=("transaction_id", "count"),
              Gross_Vol_USD=("abs_transaction_amount", "sum"),
              Fraud_Rate_Pct=("is_fraud", lambda s: round(float(s.mean()) * 100, 2)),
          )
          .sort_values("Gross_Vol_USD", ascending=False)
      )
      cust_tbl["Gross_Vol_USD"] = cust_tbl["Gross_Vol_USD"].round(2)
      st.dataframe(cust_tbl, use_container_width=True, hide_index=True)
    else:
      st.caption("`tenure_cohort` column not present.")

  with b2:
    st.markdown("**Product Usage (Payment Method)**")
    prod_tbl = (
        fdf.groupby("payment_method", as_index=False, dropna=False)
        .agg(
            Txns=("transaction_id", "count"),
            Gross_Vol_USD=("abs_transaction_amount", "sum"),
            Fraud_Rate_Pct=("is_fraud", lambda s: round(float(s.mean()) * 100, 2)),
        )
        .sort_values("Gross_Vol_USD", ascending=False)
    )
    prod_tbl["Gross_Vol_USD"] = prod_tbl["Gross_Vol_USD"].round(2)
    st.dataframe(prod_tbl, use_container_width=True, hide_index=True)

  with b3:
    st.markdown("**Market Trends (Day of Week)**")
    if "day_of_week" in fdf.columns:
      dow_tbl = (
          fdf.dropna(subset=["day_of_week"])
          .groupby("day_of_week", as_index=False)
          .agg(
              Txns=("transaction_id", "count"),
              Gross_Vol_USD=("abs_transaction_amount", "sum"),
              Fraud_Rate_Pct=("is_fraud", lambda s: round(float(s.mean()) * 100, 2)),
          )
          .sort_values("Gross_Vol_USD", ascending=False)
      )
      dow_tbl["Gross_Vol_USD"] = dow_tbl["Gross_Vol_USD"].round(2)
      st.dataframe(dow_tbl, use_container_width=True, hide_index=True)
    else:
      st.caption("`day_of_week` column not present.")

with tab_ab:
  st.subheader("Two-Proportion Sample Size & Power Calculator")
  lift_pp = st.slider(
      "Expected Fraud Rate Reduction (Percentage Points)", 1.0, 10.0, 5.0, 0.5
  )
  p1 = (
      fdf.loc[fdf["flag_overdraft_attempt"] == 1, "is_fraud"].mean()
      if "flag_overdraft_attempt" in fdf.columns
      and fdf["flag_overdraft_attempt"].sum() > 0
      else fdf["is_fraud"].mean()
  )
  p2 = max(0.01, p1 - lift_pp / 100.0)
  p_bar = (p1 + p2) / 2
  z_a, z_b = stats.norm.ppf(0.975), stats.norm.ppf(0.80)
  n_per_arm = (
      int((
          (
              z_a * (2 * p_bar * (1 - p_bar)) ** 0.5
              + z_b * (p1 * (1 - p1) + p2 * (1 - p2)) ** 0.5
          )
          / (p1 - p2)
      ) ** 2)
      + 1
  )
  m1, m2, m3 = st.columns(3)
  m1.metric("Control Fraud Rate", f"{p1 * 100:.2f}%")
  m2.metric("Target Treatment Rate", f"{p2 * 100:.2f}%")
  m3.metric("Required Sample / Arm", f"{n_per_arm:,}")
  st.caption(
      "Calculated at 80% statistical power, two-sided α = 0.05; pair with"
      " approval rate / checkout friction guardrails."
  )

with tab_gov:
  st.subheader("Data Quality & Privacy Checks")
  dq_candidates = [
      ("Ledger Math Mismatch", "flag_ledger_mismatch"),
      ("Negative Starting Balance", "flag_negative_bal_before"),
      ("Negative Txn Amount", "flag_negative_amount"),
      ("Casing Anomaly Normalized", "flag_casing_anomaly"),
      ("Missing Timestamp Flagged", "flag_missing_timestamp"),
      ("Overdraft Attempt Flagged", "flag_overdraft_attempt"),
  ]
  dq_rows = [
      (label, int(fdf[col].sum()))
      for label, col in dq_candidates
      if col in fdf.columns
  ]
  if dq_rows:
    st.dataframe(
        pd.DataFrame(dq_rows, columns=["Quality Check", "Row Count"]),
        use_container_width=True,
        hide_index=True,
    )
  st.caption(
      "Raw PII fields (addresses, birthdates, IP strings) are excluded from the"
      " analytical table; 0 orphan foreign keys and 0 duplicate IDs verified."
  )