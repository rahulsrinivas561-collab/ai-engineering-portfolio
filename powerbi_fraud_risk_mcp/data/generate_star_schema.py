import os
import numpy as np
import pandas as pd

# Ensure data directory exists
os.makedirs("data", exist_ok=True)
print(f"Target data directory: {os.path.abspath('data')}")

np.random.seed(42)

# 1. Dimension: Merchants
merchants = pd.DataFrame({
    "merchant_id": range(101, 121),
    "merchant_name": [f"Merchant_{i}" for i in range(1, 21)],
    "category": np.random.choice(["Food Delivery", "Quick Commerce", "Electronics", "Travel"], 20),
    "city": np.random.choice(["Bengaluru", "Mumbai", "Delhi", "Hyderabad"], 20)
})

# 2. Dimension: Users
users = pd.DataFrame({
    "user_id": range(1001, 1501),
    "account_tier": np.random.choice(["Standard", "Gold", "Platinum"], 500, p=[0.6, 0.3, 0.1]),
    "kyc_verified": np.random.choice([True, False], 500, p=[0.85, 0.15])
})

# 3. Fact: Transactions (10,000 rows)
n = 10000
dates = pd.date_range("2026-07-01", "2026-10-31", freq="h")
fraud_flags = np.random.choice([0, 1], n, p=[0.965, 0.035])
fraud_types = np.where(
    fraud_flags == 1,
    np.random.choice(["ATO", "Chargeback", "OTP_Share", "MDI"], n, p=[0.35, 0.30, 0.20, 0.15]),
    "None"
)

fact = pd.DataFrame({
    "transaction_id": range(1, n + 1),
    "txn_date": np.random.choice(dates, n).astype("datetime64[D]"),
    "user_id": np.random.choice(users["user_id"], n),
    "merchant_id": np.random.choice(merchants["merchant_id"], n),
    "payment_method": np.random.choice(["UPI", "Credit Card", "Wallet", "BNPL"], n, p=[0.5, 0.25, 0.15, 0.1]),
    "amount_inr": np.round(np.random.exponential(scale=1200, size=n) + 100, 2),
    "fraud_flag": fraud_flags,
    "fraud_type": fraud_types
})

# Save CSVs
merchants.to_csv("data/Dim_Merchant.csv", index=False)
users.to_csv("data/Dim_User.csv", index=False)
fact.to_csv("data/Fact_Transactions.csv", index=False)

print("Successfully generated files:", os.listdir("data"))