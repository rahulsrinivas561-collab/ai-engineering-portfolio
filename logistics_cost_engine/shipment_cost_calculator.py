import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

def run_logistics_cost_engine():
    # 1. Authenticate with Google Sheets API
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)

    # 2. Open Your Google Sheet (Replace with your actual Google Sheet ID from the URL)
    SPREADSHEET_ID = "1aQVUsQM7RHC1ErKmYA8PTa_m75fRV8wQuDxmGeAww7o"
    workbook = client.open_by_key(SPREADSHEET_ID)
    
    shipment_sheet = workbook.worksheet("Shipment Data")
    rate_sheet = workbook.worksheet("Rate Card")

    # 3. Read Data into Pandas DataFrames
    shipment_df = pd.DataFrame(shipment_sheet.get_all_records())
    rate_df = pd.DataFrame(rate_sheet.get_all_records())

    # 4. Data Cleaning & Normalization
    shipment_df['Pincode'] = shipment_df['Pincode'].astype(str).str.strip()
    rate_df['Pincode'] = rate_df['Pincode'].astype(str).str.strip()

    shipment_df['Shipment Weight'] = pd.to_numeric(shipment_df['Shipment Weight'], errors='coerce').fillna(0)
    rate_df['Rates at Per Kg Level'] = pd.to_numeric(rate_df['Rates at Per Kg Level'], errors='coerce').fillna(0)
    rate_df['LR Charges'] = pd.to_numeric(rate_df['LR Charges'], errors='coerce').fillna(0)

    # 5. Relational Merge using Pincode as Key (Left Join)
    merged_df = pd.merge(shipment_df, rate_df, on='Pincode', how='left')

    # Handle missing rate card matches by filling 0
    merged_df['Rates at Per Kg Level'] = merged_df['Rates at Per Kg Level'].fillna(0)
    merged_df['LR Charges'] = merged_df['LR Charges'].fillna(0)

    # 6. Calculate Cost: (Weight * Rate) + LR Charges
    merged_df['Calculated Cost'] = (
        (merged_df['Shipment Weight'] * merged_df['Rates at Per Kg Level']) + merged_df['LR Charges']
    ).round(2)

    # 7. Write Calculated Cost Back to Google Sheet
    # Ensure header exists
    shipment_sheet.update_cell(1, 6, "Calculated Cost")
    
    # Push cost values back to column F
    cost_values = [[val] for val in merged_df['Calculated Cost'].tolist()]
    shipment_sheet.update(f"F2:F{len(cost_values) + 1}", cost_values)
    
    print("Shipment cost calculation completed and updated successfully in Google Sheets!")

if __name__ == "__main__":
    run_logistics_cost_engine()