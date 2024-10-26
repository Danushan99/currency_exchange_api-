
# import firebase_admin
# from firebase_admin import credentials, firestore
# from fastapi import FastAPI
# import requests
# import re
# from datetime import datetime, timedelta
# from pytz import timezone
# import json
# from auth import google_auth

# # Initialize Firebase
# service_account_credentials = google_auth(
#     name="projects/422741767417/secrets/live-firebase-admin-sdk-credentials-key/versions/1",
#     mode="json",
# )
# with open("fsSdk.json", "w") as f:
#     json.dump(service_account_credentials, f, indent=4)

# cred = credentials.Certificate("fsSdk.json")
# firebase_admin.initialize_app(cred)
# db = firestore.client()

# # Create FastAPI instance
# app = FastAPI()

# # Function to fetch the current exchange rate from a given URL
# def fetch_currency_data(url, regex_pattern):
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Raise an error for bad responses
#         cleaned_response = response.text.replace("&nbsp;", "").strip()

#         # Debugging output to inspect the cleaned response
#         print(f"Cleaned Response for {url}: {cleaned_response[:1000]}")  # Print first 1000 chars

#         match = re.search(regex_pattern, cleaned_response)
#         if match:
#             return float(match.group(1))
#     except Exception as e:
#         print(f"Error fetching data from {url}: {e}")
#     return None

# # Function to get exchange rates for Sri Lanka (CBSL)
# def get_lk_exchange_rates():
#     currencies = {}

#     # URLs and regex patterns to extract selling prices for Sri Lanka
#     urls_patterns = {
#         "USD": ("https://www.cbsl.gov.lk/cbsl_custom/charts/usd/indexsmall.php", r'Sell\s+(\d+(\.\d*)?)'),
#         "GBP": ("https://www.cbsl.gov.lk/cbsl_custom/charts/gbp/indexsmall.php", r'Sell\s+(\d+(\.\d*)?)'),
#         "EUR": ("https://www.cbsl.gov.lk/cbsl_custom/charts/eur/indexsmall.php", r'Sell\s+(\d+(\.\d*)?)'),
#         "JPY": ("https://www.cbsl.gov.lk/cbsl_custom/charts/jpy/indexsmall.php", r'Sell\s+(\d+(\.\d*)?)'),
#         "CNY": ("https://www.cbsl.gov.lk/cbsl_custom/charts/cnh/indexsmall.php", r'Sell\s+(\d+(\.\d*)?)'),
#         "AUD": ("https://www.cbsl.gov.lk/cbsl_custom/charts/aud/indexsmall.php", r'Sell\s+(\d+(\.\d*)?)'),
#     }

#     for currency, (url, pattern) in urls_patterns.items():
#         rate = fetch_currency_data(url, pattern)
#         if rate is not None:
#             currencies[currency] = rate

#     return currencies

# # Function to get exchange rates for Zambia (ZAMB)
# def get_zamb_exchange_rates():
#     currencies = {
#         "USD": 18.67, 
#         "GBP": 24.12,
#         "EUR": 22.32,
#     }
#     return currencies

# # Function to delete outdated data (older than 7 days)
# def delete_outdated_data():
#     # Reference to the 'exchangeRates' collection
#     exchange_rates_ref = db.collection('exchangeRates')

#     # Get the current timestamp and the timestamp 7 days ago
#     current_time = datetime.now(timezone('Asia/Colombo'))
#     seven_days_ago = current_time - timedelta(days=7)

#     # Convert the timestamp 7 days ago to string format for comparison
#     seven_days_ago_str = seven_days_ago.strftime('%Y-%m-%d %H:%M:%S')

#     # Query Firestore to find all documents with a 'scrapedAt' timestamp older than 7 days
#     docs = exchange_rates_ref.where('scrapedAt', '<', seven_days_ago_str).stream()
    
#     deleted_count = 0  # Counter for deleted documents

#     for doc in docs:
#         print(f"Deleting outdated document {doc.id} with timestamp older than 7 days.")
#         exchange_rates_ref.document(doc.id).delete()
#         deleted_count += 1

#     print(f"Deleted {deleted_count} outdated documents from Firestore.")

# # FastAPI endpoint to fetch and store exchange rates in Firestore with a random document ID and timestamp
# @app.get("/scrape-rates")
# async def scrape_and_store():
#     try:
#         # Delete outdated data (older than 7 days)
#         delete_outdated_data()

#         # Generate a random document ID
#         document_id = db.collection('exchangeRates').document().id  # Generates a new random ID

#         # Get exchange rates for Sri Lanka (LK) and Zambia (ZAMB)
#         lk_rates = get_lk_exchange_rates()
#         zamb_rates = get_zamb_exchange_rates()

#         # Check if rates were successfully fetched
#         if not lk_rates:
#             raise ValueError("Failed to fetch Sri Lanka exchange rates.")
#         if not zamb_rates:
#             raise ValueError("Failed to fetch Zambia exchange rates.")

#         # Get the current timestamp in 'Asia/Colombo' timezone
#         timestamp = datetime.now(timezone('Asia/Colombo')).strftime('%Y-%m-%d %H:%M:%S')

#         # Create the data to store in Firestore, including the timestamp
#         new_data = {
#             "scrapedAt": timestamp, 
#             "sellingPrice": {
#                 "LK": lk_rates,
#                 "ZAMB": zamb_rates
#             }
#         }
#         # Store the data in Firestore with the random document ID
#         db.collection('exchangeRates').document(document_id).set(new_data)

#         # Return success message with the document ID and stored data
#         return {
#             "message": "Exchange rates successfully scraped and stored in Firestore.",
#             "document_id": document_id,
#             "data": new_data
#         }
#     except Exception as e:
#         # Log the error for debugging
#         print(f"Error during scraping and storing: {e}")
#         return {
#             "message": "Failed to scrape and store exchange rates.",
#             "error": str(e)
#         }




from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List

app = FastAPI()

# Function to scrape the Bank of Zambia website
def scrape_boz_website() -> Dict[str, Any]:
    url = "https://www.boz.zm/index.htm"
    
    try:
        # Make a request to the Bank of Zambia website
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')

        # Create a dictionary to hold the scraped data
        all_data = {
            "title": soup.title.string if soup.title else "No Title",
            "tables": []
        }

        # Extract the Latest Announcements
        announcements = {
            "table_name": "Latest Announcements",
            "headers": [],
            "rows": []
        }
        
        # Extract latest announcements
        announcement_elements = soup.find_all("table")[0].find_all("tr")
        for announcement in announcement_elements:
            cells = [cell.get_text(strip=True) for cell in announcement.find_all("td")]
            if cells:
                announcements["rows"].append(cells)
        all_data["tables"].append(announcements)

        # Extract Interbank Rates and Retail Rates
        rates_table = {
            "table_name": "Interbank and Retail Rates",
            "headers": [
                "Bank Name",
                "Interbank Buy Rate",
                "Interbank Sell Rate",
                "Retail Buy Rate",
                "Retail Sell Rate"
            ],
            "rows": []
        }

        # Extracting the actual rates from the relevant table
        rates_elements = soup.find_all("table")[1].find_all("tr")
        for rate in rates_elements[2:]:  # Skip header rows
            cells = [cell.get_text(strip=True) for cell in rate.find_all("td")]
            if cells and len(cells) >= 4:  # Ensure we have enough columns
                rates_table["rows"].append(cells)
        all_data["tables"].append(rates_table)

        # Extract Daily ZMW/USD Exchange Rates
        exchange_rates_table = {
            "table_name": "Daily ZMW/USD Exchange Rates",
            "headers": [
                "Time",
                "Buying Rate",
                "Selling Rate"
            ],
            "rows": []
        }

        # Locate the specific table for ZMW/USD exchange rates
        exchange_table = soup.find_all("table")[2]  # Adjust the index based on actual placement
        exchange_elements = exchange_table.find_all("tr")

        for exchange in exchange_elements[1:]:  # Skip header row
            cells = [cell.get_text(strip=True) for cell in exchange.find_all("td")]
            if len(cells) >= 3:  # Ensure we have enough columns
                print(f"Extracted Exchange Rate Row: {cells}")  # Debugging line
                exchange_rates_table["rows"].append(cells)
            else:
                print("Row not valid:", cells)  # Debugging line

        all_data["tables"].append(exchange_rates_table)

        # Extract Average Exchange Rates
        avg_exchange_rates_table = {
            "table_name": "Average Exchange Rates",
            "headers": [
                "Currency",
                "Buying Rate",
                "Selling Rate"
            ],
            "rows": [
                ["USD", "", ""],
                ["GBP", "", ""],
                ["EUR", "", ""],
                ["ZAR", "", ""],
                ["View more"]
            ]
        }
        all_data["tables"].append(avg_exchange_rates_table)

        # Extract Bank of Zambia Policy Rate
        policy_rate_table = {
            "table_name": "Bank of Zambia Policy Rate",
            "headers": ["Date", "Rate"],
            "rows": [
                ["[date]", ""],
                ["View more"]
            ]
        }
        all_data["tables"].append(policy_rate_table)

        # Extract Overnight Lending Facility Rates
        lending_rates_table = {
            "table_name": "Overnight Lending Facility Rates",
            "headers": ["Date", "Rate"],
            "rows": [
                ["[date]", ""],
                ["View more"]
            ]
        }
        all_data["tables"].append(lending_rates_table)

        # Extract Overnight Interbank Interest Rates
        overnight_interest_rates_table = {
            "table_name": "Overnight Interbank Interest Rates",
            "headers": ["Time", "Rate"],
            "rows": [
                ["09:30", ""],
                ["12:30", ""],
                ["15:30", ""],
                ["View more"]
            ]
        }
        all_data["tables"].append(overnight_interest_rates_table)

        # Extract Treasury Bills
        treasury_bills_table = {
            "table_name": "Treasury Bills",
            "headers": ["Tender No", "Tenure", "Yield", "Weighted Average Discount Rate"],
            "rows": [
                ["", "", "", ""],
                ["91 Days", "", ""],
                ["182 Days", "", ""],
                ["273 Days", "", ""],
                ["364 Days", "", ""],
                ["View more"]
            ]
        }
        all_data["tables"].append(treasury_bills_table)

        # Extract Government Bonds
        government_bonds_table = {
            "table_name": "Government Bonds",
            "headers": ["Tender No", "Period", "Yield", "Coupon"],
            "rows": [
                ["", "", "", ""],
                ["2 Years", "", ""],
                ["3 Years", "", ""],
                ["5 Years", "", ""],
                ["7 Years", "", ""],
                ["10 Years", "", ""],
                ["15 Years", "", ""],
                ["View more"]
            ]
        }
        all_data["tables"].append(government_bonds_table)

        return all_data

    except Exception as e:
        print(f"Error fetching data from Bank of Zambia: {e}")
        return {"error": str(e)}

# FastAPI endpoint to scrape and return all data from the Bank of Zambia website
@app.get("/scrape-all")
async def get_all_data():
    all_data = scrape_boz_website()
    if "error" in all_data:
        return {
            "message": "Failed to scrape data.",
            "error": all_data["error"]
        }
    return {
        "message": "Successfully scraped all data from Bank of Zambia website.",
        "data": all_data
    }
