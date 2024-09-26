import pandas as pd
import requests
import os
from openpyxl import load_workbook
import re
from dotenv import load_dotenv
import xml.etree.ElementTree as ET

# Load environment variables
load_dotenv()

def sanitize_filename(filename):
    return re.sub(r'[^\w\-_\. ]', '_', filename)

def get_company_logo_proxycurl(company_name):
    url = "https://nubela.co/proxycurl/api/linkedin/company/profile-picture/"
    headers = {
        "Authorization": f"Bearer {os.getenv('PROXYCURL_API')}"
    }
    params = {
        "company_name": company_name
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json().get('logo')
    else:
        print(f"Proxycurl: No logo found for {company_name}")
        return None

def download_logo(img_url, company_name, folder_path):
    try:
        response = requests.get(img_url, stream=True)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'image' in content_type:
                ext = content_type.split('/')[-1]
                if ext == 'jpeg':
                    ext = 'jpg'
                safe_company_name = sanitize_filename(company_name)
                file_name = f"{safe_company_name}.{ext}"
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(8192):
                        f.write(chunk)
                print(f"Logo saved for {company_name}")
                return True
            else:
                print(f"Content is not an image for {company_name}")
        elif response.status_code == 403:
            # Check if it's an XML response indicating expired URL
            root = ET.fromstring(response.content)
            if root.find('Code').text == 'UnauthorizedAccess' and 'expired' in root.find('Message').text:
                print(f"URL expired for {company_name}, will fetch new URL")
                return False
        else:
            print(f"Failed to download logo for {company_name}: HTTP {response.status_code}")
    except ET.ParseError:
        print(f"Unexpected response format for {company_name}")
    except Exception as e:
        print(f"Error downloading logo for {company_name}: {str(e)}")
    return False

def main():
    # Load the Excel file
    excel_file = 'company_information_full.xlsx'
    sheet_name = 'Company Information'
    column_name = 'A'  # Assuming company names are still in column A
    
    workbook = load_workbook(excel_file)
    sheet = workbook[sheet_name]
    
    company_names = [cell.value for cell in sheet[column_name] if cell.value]
    
    # Create a folder to save logos
    folder_path = 'company_logos'
    os.makedirs(folder_path, exist_ok=True)
    
    # Find and download logos for each company
    for company_name in company_names:
        attempts = 0
        while attempts < 2:  # Try up to 2 times (original attempt + 1 retry)
            logo_url = get_company_logo_proxycurl(company_name)
            if logo_url:
                if download_logo(logo_url, company_name, folder_path):
                    break  # Successfully downloaded, move to next company
                else:
                    attempts += 1  # URL might have expired, retry
            else:
                print(f"No logo URL found for {company_name}")
                break  # No URL found, move to next company
        
        if attempts == 2:
            print(f"Failed to download logo for {company_name} after retry")

if __name__ == "__main__":
    main()