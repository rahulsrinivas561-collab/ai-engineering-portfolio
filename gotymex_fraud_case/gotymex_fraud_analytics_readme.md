# GoTymeX Fraud & Transaction Risk Analytics Hub

[![Streamlit App](https://img.shields.io/badge/Streamlit-Live%20Dashboard-FF4B4B?logo=streamlit&logoColor=white)](https://ai-engineering-portfolio-gotymexdashboard.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Data Audit](https://img.shields.io/badge/Records%20Audited-100%2C000-0F4C81)](#key-findings--metrics)
[![Data Retention](https://img.shields.io/badge/Row%20Loss-0%25%20(Non--Destructive)-16A34A)](#data-cleaning--feature-engineering)

An end-to-end transaction risk auditing pipeline and interactive decision-intelligence application built for **GoTymeX**. This project audits **100,000 banking transactions ($249.13M gross volume)**, engineers **27 reconciliation and risk-flag features** with zero data loss, and delivers a self-serve **Streamlit** hub for Operations, Risk, Finance, Product, and Marketing teams.

- **Live Interactive Dashboard:** [https://ai-engineering-portfolio-gotymexdashboard.streamlit.app](https://ai-engineering-portfolio-gotymexdashboard.streamlit.app)
- **Repository Directory:** [gotymex_fraud_case](https://github.com/rahulsrinivas561-collab/ai-engineering-portfolio/tree/c07b5d243f7eff52f096e2e9d28456d41ec0f5a8/gotymex_fraud_case)

---

## Executive Summary & Problem Statement

High-volume digital banking teams often rely on static spreadsheets that slow down at scale, introduce manual formula drift, and mask underlying risk signals behind flat top-line averages. 

This solution replaces ad-hoc manual reporting with:
1. **A reproducible, non-destructive Python cleaning & feature-engineering pipeline** that preserves all 100,000 raw records while tagging anomalies via binary flags.
2. **A 4-tab Streamlit analytics hub** enabling non-technical stakeholders to filter segments, ask plain-English questions, isolate high-lift risk flags, and size statistically sound A/B experiments before rolling out new fraud rules.

---

## Key Findings & Metrics

| Metric | Value | Analytical Takeaway |
| :--- | :--- | :--- |
| **Total Transactions** | `100,000` | Audited across 200 joined customers and 100 linked merchants with **0 rows dropped**. |
| **Gross Transaction Volume** | `$249.13M` | Mean transaction size of `~$2,491` (median `~$2,490`). |
| **Balanced Fraud Baseline** | `50.11%` | `50,112` fraudulent vs. `49,888` legitimate transactions (`~$124.8M` fraud exposure). |
| **Channel Distribution** | `~$62M` / channel | Evenly split across **Withdrawals** (`$62.50M`), **Transfers** (`$62.47M`), **Purchases** (`$62.22M`), and **Deposits** (`$61.93M`)—requiring targeted anomaly flags rather than broad channel blocks. |
| **Data Sparsity Mapped** | `28` / `109` | `28` missing transaction timestamps (excluded from time-series charts) and `109/200` customers missing demographic age fields (mitigated via account tenure cohorts). |

---

## Data Cleaning & Feature Engineering (`13` → `40` Columns)

Rather than deleting messy or anomalous records, the pipeline follows a **Flag-Over-Delete** governance approach and retains original raw strings (`*_raw`) for full auditability:

| Feature Domain | Engineered Columns | Purpose |
| :--- | :--- | :--- |
| **Volume & Throughput** | `abs_transaction_amount` (`gross_vol_usd`) | Measures positive dollar throughput across channels, rails, and cohorts. |
| **Ledger Reconciliation** | `expected_balance_after`, `balance_diff` | Verifies whether `opening_balance + transaction_amount == closing_balance`. |
| **Risk & Quality Flags** | `flag_overdraft_attempt`, `flag_ledger_mismatch`, `flag_negative_amount`, `flag_negative_bal_before`, `flag_casing_anomaly`, `flag_missing_timestamp` | Binary (`1/0`) indicators isolating high-lift fraud signals and data hygiene exceptions without row loss. |
| **Temporal Keys** | `transaction_dt`, `year`, `month`, `day_of_week` | Powers monthly baseline comparisons and weekday vs. weekend cadence analysis. |
| **Cohort & Entity Enrichment** | `tenure_cohort`, `age_group`, `has_demographics`, `merchant_category`, `*_raw` | Segments newer vs. established accounts, retail categories (`25,012` purchases), and preserves raw text. |

---

## Application Architecture (4 Interactive Tabs)

The Streamlit dashboard (`app.py`) combines global sidebar slicers (Transaction Type, Payment Method, Device, Fraud Status) with four dedicated analytical workspaces:

1. **NLP Ask-the-Data**
   - Supports natural-language questions (e.g., *"Which payment method has the highest fraud exposure?"* or *"Show overdraft fraud lift"*).
   - Uses **optional Groq LLM intent routing** when an API key is configured, with an automatic **zero-key deterministic keyword fallback** so the app works reliably offline or without credentials.
   - All numerical aggregations remain strictly computed in Python (`pandas`)—never hallucinated by an LLM.
2. **Business KPIs & Behavioral Deep-Dives**
   - Tracks headline KPIs (`Transactions`, `Gross Volume`, `Fraud Rate`, `Fraud Exposure`, `Overdraft Attempts`).
   - Provides dedicated views for **Customer Behavior** (tenure cohorts vs. sparse demographics), **Product Usage** (payment rails, merchant categories, and **Flag Fraud Lift** tables), and **Market Trends** (weekday cadence and monthly benchmarks).
3. **A/B Test Sample-Size Planner**
   - Implements a **two-proportion z-test** (`scipy.stats`) to size controlled experiments between **Group A (Control)** and **Group B (Treatment)**.
   - Configurable target fraud-rate reduction slider (`1–10 pp`) anchored at `α = 0.05` (two-sided) and `80% statistical power` (e.g., a `5 pp` drop from a `50.11%` baseline requires `~1,565` transactions per arm / `~3,130` total).
4. **Data Quality & Governance**
   - Surfaces automated reconciliation checks, null-value audits, PII removal verification (raw IPs and sensitive personal strings stripped), and schema validation logs.

---

## Cross-Functional Impact

- **Operations & Risk:** Apply step-up verification (e.g., OTP) selectively on high-lift flags such as overdraft attempts, validating rule changes via A/B tests before full rollout.
- **Finance:** Size daily liquidity and chargeback reserves using `$249.13M` channel throughput and resolve ledger math mismatches prior to close.
- **Product:** Introduce low-balance UX nudges where overdraft attempts spike and streamline checkout flows on high-volume payment rails.
- **Marketing:** Time promotional campaigns around peak weekdays and tenure cohorts without over-relying on incomplete demographic age fields.

---

## Repository Structure

```text
gotymex_fraud_case/
├── app.py                              # Main 4-tab Streamlit application
├── cleaned_analytics_transactions.csv  # Cleaned & enriched 100,000-row dataset (40 columns)
├── cleaned_customers.csv               # Cleaned customer master table (200 accounts)
├── cleaned_merchants.csv               # Cleaned merchant lookup table (100 stores)
├── requirements.txt                    # Python dependencies
└── README.md                           # Project documentation
```

---

## Local Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rahulsrinivas561-collab/ai-engineering-portfolio.git
   cd ai-engineering-portfolio/gotymex_fraud_case
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **(Optional) Configure Groq API key for enhanced NLP routing:**
   Create a `.streamlit/secrets.toml` file (or export as an environment variable). *Note: The app runs out-of-the-box without this key using its built-in keyword router.*
   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   ```

4. **Run the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

---

## Author

**Rahul Srinivas**  
- Live Dashboard: [GoTymeX Analytics Hub](https://ai-engineering-portfolio-gotymexdashboard.streamlit.app)
- GitHub: [@rahulsrinivas561-collab](https://github.com/rahulsrinivas561-collab)