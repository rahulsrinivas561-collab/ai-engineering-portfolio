# Payments & Fraud Risk Analytics: Hybrid Power BI & MCP Architecture

End-to-end Fintech Fraud & Risk Operations semantic model and executive dashboard built using a traditional **Star Schema** in Power BI Desktop, stored as human-readable **TMDL (Tabular Model Definition Language)** via **Power BI Projects (.pbip)**, and accelerated using **Power BI Authoring MCP**.

---

## Project Overview & Architecture

Modern enterprise analytics teams do not rely solely on manual UI clicking or opaque binary `.pbix` files. This project demonstrates a production-grade hybrid workflow:
1. **The Traditional Core:** Clean 1-Fact, 3-Dimension **Star Schema** with rigorous relationships (`1:*` single-direction filtering) and pre-calculated DAX measures.
2. **Version-Controlled Semantic Models:** Saved as `.pbip` to track every table, relationship, and DAX measure line-by-line in Git using TMDL format.
3. **AI-Assisted Modeling (MCP):** Using VS Code Agent mode with Microsoft's Power BI Authoring MCP server to bulk-generate time-intelligence measures, format strings, and display folders.

---

## Repository File Structure

ai_projects/
└── powerbi_fraud_risk_mcp/
    ├── README.md                          # Project documentation & architecture
    ├── generate_star_schema.py            # Python script generating 10,000+ synthetic transactions
    ├── Fact_Transactions.csv              # Core transaction fact table (amounts, fraud flags, types)
    ├── Dim_Merchant.csv                   # Merchant dimension (categories, cities)
    ├── Dim_User.csv                       # User dimension (account tiers, KYC status)
    ├── FraudRiskReport.pbip               # Power BI Project entry file
    ├── FraudRiskReport.SemanticModel/     # TMDL semantic model definition (Git-tracked)
    └── FraudRiskReport.Report/            # Report visual layouts and JSON definitions (Git-tracked)

---

## Data Model & Schema Design

The dataset simulates high-volume digital payment transactions featuring realistic fraud vectors (`ATO`, `Chargeback`, `OTP_Share`, and `MDI`).

### Tables & Relationships
1. **`Fact_Transactions`** (Grain: 1 row per transaction ID)
   * Columns: `transaction_id`, `txn_date`, `user_id`, `merchant_id`, `payment_method`, `amount_inr`, `fraud_flag`, `fraud_type`
2. **`Dim_Merchant`** (Grain: 1 row per merchant)
   * Connected via `merchant_id` (1-to-Many, Single Direction)
3. **`Dim_User`** (Grain: 1 row per user account)
   * Connected via `user_id` (1-to-Many, Single Direction)
4. **`Dim_Date`** (Calendar table generated via DAX)
   * Connected via `Date` to `Fact_Transactions[txn_date]` (1-to-Many, Single Direction)
5. **`_Measures`** (Dedicated container table for all semantic calculations)

---

## Core & Time-Intelligence DAX Measures

Organized into clean Display Folders for enterprise maintainability:

### Core KPIs
* **`Total GMV`** = `SUM(Fact_Transactions[amount_inr])`
* **`Total Fraud Loss`** = `CALCULATE(SUM(Fact_Transactions[amount_inr]), Fact_Transactions[fraud_flag] = 1)`
* **`Fraud Loss Rate %`** = `DIVIDE([Total Fraud Loss], [Total GMV], 0)`
* **`Fraud Txn Count`** = `CALCULATE(COUNTROWS(Fact_Transactions), Fact_Transactions[fraud_flag] = 1)`

### Time Intelligence
* **`MTD Fraud Loss`** = `TOTALMTD([Total Fraud Loss], Dim_Date[Date])`
* **`Prev Month Fraud Loss`** = `CALCULATE([Total Fraud Loss], PREVIOUSMONTH(Dim_Date[Date]))`
* **`MoM Fraud Loss Change %`** = `DIVIDE([Total Fraud Loss] - [Prev Month Fraud Loss], [Prev Month Fraud Loss], 0)`
* **`7-Day Rolling Fraud Loss`** = `CALCULATE([Total Fraud Loss], DATESINPERIOD(Dim_Date[Date], LASTDATE(Dim_Date[Date]), -7, DAY))`

---

## Automation Workflow

### Power BI Modeling MCP (VS Code Integration)
By connecting the **Power BI Authoring MCP Server** (`analysis-services.powerbi-modeling-mcp`) directly to a running Power BI Desktop instance, developers can prompt AI agents in VS Code to:
* Inspect table schemas, row counts, and active relationship cardinalities.
* Bulk-create complex time-intelligence DAX measures instantly.
* Apply currency and percentage formatting (`$#,##0.00`, `0.00%`) and organize measures into folders.

---

## How to Run This Project Locally

1. **Clone the repository:**
   `git clone https://github.com/rahulsrinivas561-collab/ai_projects.git && cd ai_projects/powerbi_fraud_risk_mcp`
2. **Regenerate data (optional):**
   `python generate_star_schema.py`
3. **Open the project:**
   * Launch **Power BI Desktop** and open `FraudRiskReport.pbip`.
4. **Explore TMDL files:**
   * Open `ai_projects` in **VS Code** to inspect how TMDL text files represent your tables, columns, and DAX measures cleanly in version control.