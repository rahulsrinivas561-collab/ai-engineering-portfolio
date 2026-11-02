import time
import duckdb
import pandas as pd
import numpy as np

print("🚀 Initializing Big Data Generation (1 Million Rows)...")
start_time = time.time()
num_rows = 1_000_000

# 1. Generate 1 Million Rows of Risk & Transaction Data
df = pd.DataFrame({
    "transaction_id": [f"TXN_{i:07d}" for i in range(num_rows)],
    "user_id": np.random.randint(10000, 99999, size=num_rows),
    "amount": np.random.uniform(50.0, 50000.0, size=num_rows).round(2),
    "risk_score": np.random.uniform(0.0, 1.0, size=num_rows).round(3),
    "category": np.random.choice(["Account Takeover", "Device Spoofing", "Late Delivery", "Normal Order"], size=num_rows),
    "transaction_date": pd.to_datetime(np.random.choice(pd.date_range("2026-01-01", "2026-10-31"), size=num_rows))
})

print(f"⏱️ Generated {num_rows:,} rows in {time.time() - start_time:.2f} seconds.")

# 2. Connect to DuckDB and Register Data
print("\n📊 Loading data into DuckDB analytical engine...")
con = duckdb.connect(database=':memory:')
con.register('transactions_table', df)

# 3. Fully Updated High-Performance SQL Query
print("\n🔍 Executing Big Data SQL Aggregation (High-Risk Filter > 0.7)...")
query_start = time.time()

query = """
    SELECT 
        category,
        COUNT(*) as total_transactions,
        ROUND(AVG(amount), 2) as avg_amount,
        ROUND(SUM(amount), 2) as total_volume,
        ROUND(AVG(risk_score), 3) as avg_risk_score
    FROM transactions_table
    WHERE risk_score > 0.7
    GROUP BY category
    ORDER BY total_volume DESC;
"""

result_df = con.execute(query).fetchdf()
query_time = time.time() - query_start

print(f"\n✅ Big Data Query Completed in {query_time:.4f} seconds!")
print("\n--- Aggregated Risk Summary (High Risk > 0.7) ---")
print(result_df.to_string(index=False))

# 4. Export to Parquet for Power BI
print("\n📦 Exporting dataset to Parquet format for Power BI...")
con.execute("COPY transactions_table TO 'fraud_million_rows.parquet' (FORMAT PARQUET);")
con.close()

print("🎉 Success! Generated 'fraud_million_rows.parquet'. Ready to drag and drop into Power BI.")