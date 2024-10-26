import pandas as pd
import requests
import csv
import os
from datetime import datetime
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

API_KEY = "YOUR FMP API KEY"
BASE_URL = "https://financialmodelingprep.com/api/v3"

# Prioritized list of stock exchanges
PREFERRED_EXCHANGES = ["NASDAQ", "NYSE", "TSX", "TSXV", "LSE", "ASX", "PNK"]

# Rate limiting
MAX_CALLS_PER_MINUTE = 300
CALL_INTERVAL = 60 / MAX_CALLS_PER_MINUTE

def read_excel_file(file_path: str) -> List[str]:
    """Read company names from an Excel file."""
    df = pd.read_excel(file_path)
    return df["Company Name"].tolist()

def search_company(company_name: str) -> List[Dict[str, Any]]:
    """Search for a company using the FMP API."""
    endpoint = f"{BASE_URL}/search?query={company_name}&limit=10&apikey={API_KEY}"
    response = requests.get(endpoint)
    if response.status_code == 200:
        return response.json()
    print(f"Error searching for {company_name}: Status code {response.status_code}")
    return []

def get_financial_data(symbol: str) -> List[Dict[str, Any]]:
    """Fetch financial data for a company from 2021 onwards."""
    endpoints = [
        f"{BASE_URL}/income-statement/{symbol}?apikey={API_KEY}",
        f"{BASE_URL}/balance-sheet-statement/{symbol}?apikey={API_KEY}",
        f"{BASE_URL}/cash-flow-statement/{symbol}?apikey={API_KEY}"
    ]
    financial_data = []
    for endpoint in endpoints:
        response = requests.get(endpoint)
        if response.status_code == 200:
            data = response.json()
            # Filter data from 2021 onwards
            filtered_data = [item for item in data if datetime.strptime(item['date'], '%Y-%m-%d').year >= 2021]
            financial_data.extend(filtered_data)
        else:
            print(f"Error fetching data for {symbol} from {endpoint}: Status code {response.status_code}")
    return financial_data

def find_best_match(search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Find the best matching company from search results based on preferred exchanges."""
    if not search_results:
        return None
    
    for exchange in PREFERRED_EXCHANGES:
        for result in search_results:
            if result['exchangeShortName'] == exchange:
                return result
    
    # If no preferred exchange is found, return the first result
    return search_results[0]

def process_company(company: str) -> List[Dict[str, Any]]:
    """Process a single company and return its financial data."""
    search_results = search_company(company)
    best_match = find_best_match(search_results)
    
    if best_match:
        symbol = best_match['symbol']
        financial_data = get_financial_data(symbol)
        if financial_data:
            for item in financial_data:
                item.update({
                    'company_name': company,
                    'matched_name': best_match['name'],
                    'symbol': symbol,
                    'exchange': best_match['exchangeShortName'],
                    'currency': best_match['currency']
                })
            return financial_data
        else:
            return [{
                'company_name': company,
                'matched_name': best_match['name'],
                'symbol': symbol,
                'exchange': best_match['exchangeShortName'],
                'currency': best_match['currency'],
                'error': 'No financial data'
            }]
    else:
        return [{
            'company_name': company,
            'error': 'No match found'
        }]

def main(file_path: str, output_dir: str):
    companies = read_excel_file(file_path)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "consolidated_financial_data.csv")
    
    all_data = []
    
    with ThreadPoolExecutor(max_workers=30) as executor:
        future_to_company = {executor.submit(process_company, company): company for company in companies}
        
        for future in as_completed(future_to_company):
            company = future_to_company[future]
            try:
                result = future.result()
                all_data.extend(result)
                print(f"Processed {company}")
            except Exception as exc:
                print(f'{company} generated an exception: {exc}')

    # Write all data to a single CSV file
    if all_data:
        keys = set().union(*(d.keys() for d in all_data))
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted(keys))
            writer.writeheader()
            for row in all_data:
                writer.writerow(row)
        
        print(f"All financial data saved to {output_file}")
    else:
        print("No data to write.")

if __name__ == "__main__":
    excel_file_path = "cleaned_state_data.xlsx"
    output_directory = "financial_data_output"
    main(excel_file_path, output_directory)