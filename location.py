import os
import requests
import sqlite3
import time
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API")
POSITIONSTACK_API_KEY = os.getenv("POSITIONSTACK_API")

def geocode_company(company_name: str) -> Dict:
    """Geocode a company name using PositionStack API."""
    url = f"http://api.positionstack.com/v1/forward"
    params = {
        "access_key": POSITIONSTACK_API_KEY,
        "query": company_name,
        "country": "AU",
        "limit": 1
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if data.get("data"):
        return data["data"][0]
    return None

def get_nearby_places(lat: float, lon: float, category: str) -> List[Dict]:
    """Get nearby places using Foursquare API."""
    url = "https://api.foursquare.com/v3/places/search"
    headers = {
        "Accept": "application/json",
        "Authorization": FOURSQUARE_API_KEY
    }
    params = {
        "ll": f"{lat},{lon}",
        "radius": 1000,
        "categories": category,
        "limit": 5
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    return data.get("results", [])

def create_database():
    """Create SQLite database and tables."""
    conn = sqlite3.connect('australian_companies.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS companies
                 (id INTEGER PRIMARY KEY, name TEXT, latitude REAL, longitude REAL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS nearby_places
                 (id INTEGER PRIMARY KEY, company_id INTEGER, name TEXT, category TEXT,
                  FOREIGN KEY (company_id) REFERENCES companies (id))''')
    
    conn.commit()
    conn.close()

def insert_data(company_name: str, lat: float, lon: float, nearby_places: List[Dict]):
    """Insert data into the database."""
    conn = sqlite3.connect('australian_companies.db')
    c = conn.cursor()
    
    c.execute("INSERT INTO companies (name, latitude, longitude) VALUES (?, ?, ?)",
              (company_name, lat, lon))
    company_id = c.lastrowid
    
    for place in nearby_places:
        c.execute("INSERT INTO nearby_places (company_id, name, category) VALUES (?, ?, ?)",
                  (company_id, place['name'], place['categories'][0]['name']))
    
    conn.commit()
    conn.close()

def main(companies: List[str]):
    create_database()
    
    for company in companies:
        print(f"Processing {company}...")
        location = geocode_company(company)
        
        if location:
            lat, lon = location['latitude'], location['longitude']
            
            malls = get_nearby_places(lat, lon, "17069")  # 17069 is the Foursquare category ID for Shopping Malls
            restaurants = get_nearby_places(lat, lon, "13065")  # 13065 is the Foursquare category ID for Restaurants
            
            insert_data(company, lat, lon, malls + restaurants)
            
            print(f"Added {company} with {len(malls)} nearby malls and {len(restaurants)} nearby restaurants.")
        else:
            print(f"Couldn't find location for {company}")
        
        time.sleep(1)  # To avoid hitting API rate limits

if __name__ == "__main__":
    australian_companies = [
        "The Recruitment Company", "Entourage", "TrainTheCrowd", "Atarix", "Glaukos Corporation",
        "Belloy Avenue Dental", "Tiliter", "Propel Ventures", "Quorum Systems", "Moddex Group",
        "Green Building Council of Australia", "WW", "DEWC Services", "Sophos", "Kaine Mathrick Tech",
        "SEDA College (Victoria)", "Informatica Australia", "Cordelta", "Sentrian", "Luminary",
        "Hub Australia", "Charterhouse", "Cobild", "Biogen", "Mantel Group",
        "BPAY Group", "OMD Australia", "Thoughtworks", "Canstar", "InfoTrack",
        "UKG", "Adobe", "AbbVie", "Carnival Australia", "Novo Nordisk",
        "Medtronic Australasia", "General Mills", "BlueRock", "Insight", "Aussie Broadband",
        "Swisse Wellness Australia", "Yahoo (Formerly Verizon Media)", "Jaybro Group", "NeuroRehab Allied Health Network",
        "Macquarie Cloud Services", "Coleman Greig Lawyers", "Crowdstrike", "Finder", "4 Pines Brewing Company",
        "Cisco Systems Australia", "DHL Express Australia", "Salesforce", "REA Group", "Atlassian",
        "SustainAbility Consulting", "This Is Flow", "Lotus People", "Cullen Jewellery", "Stamford Capital Australia",
        "Pragmateam", "Amstelveen", "Inspire Accountants", "ICD Property", "HiBob",
        "Four Drunk Parrots", "SEIVA", "Pendula", "CreativeCubes.co", "Engaging.io",
        "NEOLINK", "Banna Property Group", "Howden Insurance Brokers (Australia)", "Response Security Services",
        "EFCOMM", "Bravure", "Miro", "Displayr", "Dovetail",
        "SixPivot", "AvePoint", "Attach2 Pty Ltd", "FSC Group", "Kasada",
        "Commission Factory", "Beaumont People", "TKV Group", "Scalapay", "Struber",
        "PhoenixDX", "Meltwater Australia", "EstimateOne", "Zoom Recruitment", "Baringa Partners",
        "Sensei Project Solutions", "Cloudwerx", "SafetyCulture", "Robert Half", "Alluvium",
        "Intuit", "DiUS", "Red Hat", "Bristol Myers Squibb", "Healthengine",
        "HP", "Tic Toc Online", "Centorrino Technologies", "Henry Schein", "Swyftx",
        "Smokeball", "Carlisle Homes", "Ansarada", "Avenue Dental", "Hilton",
        "TRC Group", "Katana1", "Gridware", "Seatram", "The Network",
        "SCALERR", "WELCOME", "Tectum Group", "triSearch", "The Drive Group",
        "Sensible", "Cox Purtell Staffing Services", "Tapanda Pty Ltd", "Corporeal Health", "Volvo Financial Services",
        "i-Pharm Consulting", "Goodman Private Wealth", "IBC Recruitment", "Hero Head Quarters",
        "Education and Migration Services Australia", "Spaceful", "The Media Store", "I'ara Specialist Support Coordination",
        "intelia", "Decision Inc Australia Pty Ltd", "The Being Group", "Mapien Workplace Strategists",
        "Parker Precision", "LEGO Australia Pty Ltd", "ATEO", "Slalom", "Sparro & Jack Nimble",
        "carsales.com.au", "Mastercard Australia", "Prospa", "Nous Group", "Uber Australia PTY LTD",
        "ServiceNow", "Nurse Next Door Home Care Services", "Frontline Recruitment & Express", "PageGroup Australia",
        "Marriott International Australia", "DHL Supply Chain", "Specsavers", "Capgemini Australia", "Story House Early Learning"
    ]
    
    main(australian_companies)