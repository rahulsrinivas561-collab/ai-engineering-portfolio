# Automated Logistics Intelligence & Cost Engine

## Live Data Source & Dashboard

You can inspect the live automated Google Sheet used by this pipeline here:
- 📊 **[View-Only Logistics Cost Sheet](https://docs.google.com/spreadsheets/d/1aQVUsQM7RHC1ErKmYA8PTa_m75fRV8wQuDxmGeAww7o/edit?usp=sharing)**

An end-to-end automated data pipeline and low-code system design built using **AppSheet**, **Google Apps Script**, **Python (Pandas & gspread)**, and **Google Sheets**.

This project solves two key logistics workflows:
1. **Real-time Geographic Lookup:** Captures pincode inputs via an intuitive mobile/web app (AppSheet) and asynchronously populates postal geographic details (District, State, Region) using Google Apps Script and the India Post REST API.
2. **Automated Cost Calculation Engine:** Extracts shipment logs and rate cards, performs a relational join, normalizes datatypes, calculates final delivery costs via a vectorized Python pipeline, and writes the output back to Google Sheets.

---

## 🏗️ Architecture & System Overview

```text
[ User Data Entry ] ──> AppSheet UI ──> Google Sheet (Pincode Input)
                                                │
                                       (Installable Trigger)
                                                ▼
                                    Google Apps Script (Code.gs)
                                                │
                                       (Fetch API Metadata)
                                                ▼
                                    India Post REST API Sync
                                                │
                                                ▼
                                  Google Sheet (Pincode Details)
                                                
───────────────────────────────────────────────────────────────────────

[ Python ETL Engine ] ──> Fetch Shipment Data & Rate Card via gspread
                                                │
                                     (Pandas Normalization & Join)
                                                ▼
                                 Vectorized Cost Calculation:
                             (Weight * Rate) + LR Charges
                                                │
                                                ▼
                                Update "Calculated Cost" Column
```

---

## 🛠️ Tech Stack & Requirements

- **Frontend / Data Capture:** AppSheet
- **Backend Automation:** Google Apps Script (`Code.gs`)
- **Third-Party API:** India Post REST API (`api.postalpincode.in`)
- **Data Engineering & Processing:** Python 3.x, `pandas`, `gspread`, `google-auth`
- **Database / Cloud Storage:** Google Sheets API & Google Drive API

---

## 📁 Repository Structure

```text
logistics-case-study/
├── appscript/
│   └── Code.gs                         # Apps Script for automatic REST API fetching
├── python/
│   ├── shipment_cost_calculator.py     # Python ETL cost engine
│   └── requirements.txt                # Python dependencies
├── .gitignore                          # Prevents sensitive credentials from being committed
└── README.md                           # Documentation
```

---

## 🚀 Setup & Execution Guide

### 1. Google Sheets Setup
Create a Google Sheet workbook with the following tabs and schemas:

- **`Pincode Input`**: `Pincode` (Column 3)
- **`Pincode Details`**: `Pincode`, `District`, `State`, `Region`, `Timestamp`
- **`Shipment Data`**: `Pincode`, `Shipment Weight`, `Boxes`, `AWB`, `GMV`
- **`Rate Card`**: `Pincode`, `Rates at Per Kg Level`, `LR Charges`, `TC%`

---

### 2. Apps Script Automation (Question 1)

1. Open **Extensions > Apps Script** in your Google Sheet.
2. Paste the contents of `appscript/Code.gs`.
3. Set up an Installable Trigger:
   - Go to **Triggers (⏰ icon)** on the left menu.
   - Click **+ Add Trigger**.
   - **Function to run:** `watchPincodeSheet`
   - **Event Source:** `From spreadsheet`
   - **Event Type:** `On change`
4. Connect the Google Sheet to **AppSheet** to create the user input form.

---

### 3. Python Cost Calculator (Question 2)

#### Step 1: Install Dependencies
Navigate to the `python/` directory and install the required packages:

```bash
pip install -r requirements.txt
```

*(Or manually run: `pip install pandas gspread google-auth`)*

#### Step 2: Configure Service Account Credentials
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Sheets API** and **Google Drive API**.
3. Create a **Service Account** and download the JSON key.
4. Save the file as `credentials.json` inside your Python project folder.
5. **Crucial:** Copy the service account email and share your Google Sheet with it as **Editor**.

#### Step 3: Run the Script
Open `shipment_cost_calculator.py`, insert your `SPREADSHEET_ID`, and execute:

```bash
python shipment_cost_calculator.py
```

---

## 🧮 Mathematical Model

The Python engine computes logistics shipment costs using the vectorized formula:

$$\text{Calculated Cost} = (\text{Shipment Weight} \times \text{Rates at Per Kg Level}) + \text{LR Charges}$$

Missing values and unregistered rate card pincodes are safely handled and defaulted to prevent runtime pipeline crashes.

---

## 🔒 Security Best Practices

- `credentials.json` is explicitly ignored via `.gitignore` to prevent secret key leakage.
- Service Account permissions are restricted only to necessary Google Drive spreadsheet scopes.
