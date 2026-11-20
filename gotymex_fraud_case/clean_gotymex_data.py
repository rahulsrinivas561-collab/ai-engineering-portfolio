import ast
import numpy as np
import pandas as pd

# 1. Load raw CSV files
customers = pd.read_csv('customers.csv')
merchants = pd.read_csv('merchants.csv')
transactions = pd.read_csv('transactions.csv')


# 2. Clean customers.csv (extract coarse attributes without exposing raw PII)
def parse_demographics(val):
  if pd.isna(val) or str(val).strip() == '':
    return {
        'gender': 'Unknown',
        'state': 'Unknown',
        'birth_year': np.nan,
        'has_demographics': False,
    }
  try:
    parsed = ast.literal_eval(val) if isinstance(val, str) else val
  except Exception:
    return {
        'gender': 'Unknown',
        'state': 'Unknown',
        'birth_year': np.nan,
        'has_demographics': False,
    }

  gender = str(parsed.get('sex', 'Unknown')).strip().upper()
  if gender not in ['M', 'F']:
    gender = 'Unknown'

  address = str(parsed.get('address', ''))
  state = 'Unknown'
  if ',' in address:
    after_comma = address.split(',')[-1].strip()
    parts = after_comma.split()
    if parts:
      state = parts[0].strip().upper()

  bdate = str(parsed.get('birthdate', ''))
  birth_year = np.nan
  if '-' in bdate:
    yr_str = bdate.split('-')[0].strip()
    if yr_str.isdigit():
      birth_year = int(yr_str)

  return {
      'gender': gender,
      'state': state,
      'birth_year': birth_year,
      'has_demographics': True,
  }


demo_parsed = pd.DataFrame(
    customers['customer_demographics'].apply(parse_demographics).tolist()
)
customers_clean = pd.concat(
    [customers[['customer_id', 'account_age']].copy(), demo_parsed], axis=1
)
customers_clean['age_as_of_2023'] = np.where(
    customers_clean['birth_year'].notna(),
    2023 - customers_clean['birth_year'],
    np.nan,
)
customers_clean['age_group'] = (
    pd.cut(
        customers_clean['age_as_of_2023'],
        bins=[0, 29, 44, 59, 120],
        labels=['18-29', '30-44', '45-59', '60+'],
    )
    .astype(str)
    .replace('nan', 'Unknown')
)
customers_clean['tenure_cohort'] = pd.cut(
    customers_clean['account_age'],
    bins=[-1, 180, 365, 730, 1460, 10000],
    labels=['0-6m', '6-12m', '1-2y', '2-4y', '4y+'],
).astype(str)

# 3. Clean merchants.csv
merchants_clean = merchants.copy()
merchants_clean['merchant_category'] = (
    merchants_clean['merchant_category'].astype(str).str.lower().str.strip()
)

# 4. Clean transactions.csv & add data quality / risk flags
tx = transactions.copy()
for col in ['transaction_type', 'payment_method', 'transaction_device']:
  tx[f'{col}_raw'] = tx[col]
  tx[col] = tx[col].astype(str).str.lower().str.strip()

tx['transaction_dt'] = pd.to_datetime(
    tx['transaction_timestamp'], errors='coerce'
)
tx['transaction_date'] = tx['transaction_dt'].dt.date
tx['year'] = tx['transaction_dt'].dt.year
tx['month'] = tx['transaction_dt'].dt.month
tx['day_of_week'] = tx['transaction_dt'].dt.day_name()

tx['abs_transaction_amount'] = tx['transaction_amount'].abs()
tx['expected_balance_after'] = np.where(
    tx['transaction_type'].isin(['deposit', 'transfer']),
    tx['account_balance_before'] + tx['transaction_amount'],
    tx['account_balance_before'] - tx['transaction_amount'],
)
tx['balance_diff'] = (
    tx['account_balance_after'] - tx['expected_balance_after']
).round(4)

tx['flag_missing_timestamp'] = tx['transaction_dt'].isna().astype(int)
tx['flag_negative_amount'] = (tx['transaction_amount'] < 0).astype(int)
tx['flag_negative_bal_before'] = (tx['account_balance_before'] < 0).astype(int)
tx['flag_negative_bal_after'] = (tx['account_balance_after'] < 0).astype(int)
tx['flag_ledger_mismatch'] = (tx['balance_diff'].abs() > 0.02).astype(int)
tx['flag_overdraft_attempt'] = (
    tx['transaction_type'].isin(['purchase', 'withdrawal'])
    & (tx['transaction_amount'] > tx['account_balance_before'])
).astype(int)
tx['flag_casing_anomaly'] = (
    (tx['transaction_type_raw'] != tx['transaction_type'])
    | (tx['payment_method_raw'] != tx['payment_method'])
    | (tx['transaction_device_raw'] != tx['transaction_device'])
).astype(int)

# 5. Build joined analytical table
analytics_df = tx.merge(customers_clean, on='customer_id', how='left')
analytics_df = analytics_df.merge(merchants_clean, on='merchant_id', how='left')
analytics_df['merchant_category'] = analytics_df['merchant_category'].fillna(
    'non_merchant_txn'
)

# 6. Export cleaned CSVs
customers_clean.to_csv('cleaned_customers.csv', index=False)
merchants_clean.to_csv('cleaned_merchants.csv', index=False)
analytics_df.to_csv('cleaned_analytics_transactions.csv', index=False)

print(
    'Done! Generated cleaned_customers.csv, cleaned_merchants.csv, and'
    ' cleaned_analytics_transactions.csv.'
)