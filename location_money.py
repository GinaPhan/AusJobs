import os
import time
import pandas as pd
import requests
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Google API key from environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def geocode_company(company_name: str) -> Dict:
    """Geocode a company name using Google Geocoding API."""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": f"{company_name}, Australia",
        "key": GOOGLE_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        return {"latitude": location['lat'], "longitude": location['lng']}
    return None

def get_nearby_places(lat: float, lon: float, place_type: str) -> List[Dict]:
    """Get nearby places using Google Places API."""
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lon}",
        "radius": 1000,
        "type": place_type,
        "key": GOOGLE_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    return [{'name': place['name'], 'type': place_type} for place in data.get('results', [])]

def main(companies: List[str]):
    results = []

    for company in companies:
        print(f"Processing {company}...")
        location = geocode_company(company)
        
        if location:
            lat, lon = location['latitude'], location['longitude']
            
            malls = get_nearby_places(lat, lon, "shopping_mall")
            restaurants = get_nearby_places(lat, lon, "restaurant")
            bus_stations = get_nearby_places(lat, lon, "bus_station")
            train_stations = get_nearby_places(lat, lon, "train_station")
            
            results.append({
                "Company": company,
                "Latitude": lat,
                "Longitude": lon,
                "Nearby Malls": len(malls),
                "Nearby Restaurants": len(restaurants),
                "Nearby Bus Stations": len(bus_stations),
                "Nearby Train Stations": len(train_stations),
                "Mall Names": ", ".join([mall['name'] for mall in malls]),
                "Restaurant Names": ", ".join([restaurant['name'] for restaurant in restaurants]),
                "Bus Station Names": ", ".join([station['name'] for station in bus_stations]),
                "Train Station Names": ", ".join([station['name'] for station in train_stations])
            })
            
            print(f"Added {company} with {len(malls)} nearby malls, {len(restaurants)} nearby restaurants, "
                  f"{len(bus_stations)} nearby bus stations, and {len(train_stations)} nearby train stations.")
        else:
            print(f"Couldn't find location for {company}")
        
        time.sleep(0.5)  # To avoid hitting API rate limits

    # Save results to Excel file
    df = pd.DataFrame(results)
    df.to_excel("australian_companies_data.xlsx", index=False)
    print("Data saved to australian_companies_data.xlsx")

if __name__ == "__main__":
    australian_companies = [
        "The Recruitment Company", "The Entourage", "TrainTheCrowd", "Atarix", "Glaukos Corporation",
        "Belloy Avenue Dental", "Tiliter", "Propel Ventures", "Quorum Systems", "Moddex Group",
        "Green Building Council of Australia", "WW", "DEWC Services", "Sophos", "Kaine Mathrick Tech",
        # ... (rest of the company list)
        "Marriott International Australia", "DHL Supply Chain", "Specsavers", "Capgemini Australia", "Story House Early Learning"
    ]
    
    main(australian_companies)