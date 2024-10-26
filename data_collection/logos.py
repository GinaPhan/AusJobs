import pandas as pd
import requests
import os
import time
import logging
import json
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Load environment variables
load_dotenv()

# Configuration
EXCEL_FILE = 'company_information_full.xlsx'
API_ENDPOINT = 'https://nubela.co/proxycurl/api/linkedin/company/profile-picture'
PROXYCURL_API = os.getenv("PROXYCURL_API")
OUTPUT_FOLDER = 'company_images'
MAX_WORKERS = 1
RATE_LIMIT_PER_MINUTE = 5
RETRY_STRATEGY = Retry(
    total=5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"],
    backoff_factor=1
)

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure the output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def create_session():
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=RETRY_STRATEGY)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

session = create_session()

def get_company_image(row):
    linkedin_url = row['LinkedIn URL']
    company_id = row.name  # Assuming the index is the company ID
    
    logging.info(f"Processing company {company_id}: {linkedin_url}")
    
    params = {'linkedin_company_profile_url': linkedin_url}
    headers = {'Authorization': f'Bearer {PROXYCURL_API}'}
    
    try:
        response = session.get(API_ENDPOINT, params=params, headers=headers)
        response.raise_for_status()
        
        # Log the raw response content
        logging.debug(f"Raw API Response for company {company_id}: {response.content}")
        
        # Attempt to parse JSON response
        try:
            response_json = response.json()
            logging.debug(f"Parsed API Response for company {company_id}: {json.dumps(response_json, indent=2)}")
        except json.JSONDecodeError:
            logging.error(f"Failed to parse JSON response for company {company_id}")
            return company_id, None
        
        image_url = response_json.get('tmp_profile_pic_url')  # Changed from 'image' to 'tmp_profile_pic_url'
        if image_url:
            logging.info(f"Image URL found for company {company_id}: {image_url}")
            # Download the image
            image_response = session.get(image_url)
            image_response.raise_for_status()
            
            # Parse the filename from the URL
            parsed_url = urlparse(image_url)
            file_name = os.path.basename(parsed_url.path)
            file_extension = os.path.splitext(file_name)[1] or '.jpg'
            
            # Save the image
            image_path = os.path.join(OUTPUT_FOLDER, f'{company_id}{file_extension}')
            with open(image_path, 'wb') as f:
                f.write(image_response.content)
            
            logging.info(f"Image saved for company {company_id}: {image_path}")
            return company_id, image_path
        else:
            logging.warning(f"No image URL found in the response for company {company_id}")
            return company_id, None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error processing company {company_id}: {str(e)}")
        return company_id, None

def rate_limited_api_call(row):
    time.sleep(60 / RATE_LIMIT_PER_MINUTE)  # Wait to respect rate limit
    return get_company_image(row)

def main():
    logging.info(f"Starting process. Reading Excel file: {EXCEL_FILE}")
    # Read the Excel file
    df = pd.read_excel(EXCEL_FILE)
    
    logging.info(f"Total companies to process: {len(df)}")
    
    # Create a new column for image paths
    df['Image Path'] = ''
    
    # Use ThreadPoolExecutor for concurrent API calls
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_company = {executor.submit(rate_limited_api_call, row): row for _, row in df.iterrows()}
        
        for future in as_completed(future_to_company):
            company_id, image_path = future.result()
            if image_path:
                df.at[company_id, 'Image Path'] = image_path
    
    # Save the updated DataFrame back to Excel
    df.to_excel(EXCEL_FILE, index=False)
    logging.info(f"Updated Excel file saved: {EXCEL_FILE}")
    
    # Print summary
    total_companies = len(df)
    companies_with_images = df['Image Path'].notna().sum()
    logging.info(f"Process completed. Images found for {companies_with_images} out of {total_companies} companies.")

if __name__ == "__main__":
    main()