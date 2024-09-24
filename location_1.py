import time
import pandas as pd
import requests
from typing import List, Dict
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

def geocode_company(geolocator, company_name: str) -> Dict:
    """Geocode a company name using Nominatim."""
    try:
        location = geolocator.geocode(f"{company_name}, Australia", timeout=10)
        if location:
            return {"latitude": location.latitude, "longitude": location.longitude}
    except (GeocoderTimedOut, GeocoderUnavailable):
        print(f"Geocoding failed for {company_name}. Retrying...")
        time.sleep(1)
        return geocode_company(geolocator, company_name)
    return None

def get_nearby_places(lat: float, lon: float, amenity: str) -> List[Dict]:
    """Get nearby places using Overpass API."""
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (node["amenity"="{amenity}"](around:1000,{lat},{lon});
     way["amenity"="{amenity}"](around:1000,{lat},{lon});
     rel["amenity"="{amenity}"](around:1000,{lat},{lon});
    );
    out center;
    """
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()
    return [{'name': element.get('tags', {}).get('name', 'Unknown'), 'type': amenity} for element in data['elements']]

def main(companies: List[str]):
    geolocator = Nominatim(user_agent="australian_companies_app")
    results = []

    for company in companies:
        print(f"Processing {company}...")
        location = geocode_company(geolocator, company)
        
        if location:
            lat, lon = location['latitude'], location['longitude']
            
            malls = get_nearby_places(lat, lon, "mall")
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
        
        time.sleep(1)  # To avoid hitting API rate limits

    # Save results to Excel file
    df = pd.DataFrame(results)
    df.to_excel("australian_companies_data.xlsx", index=False)
    print("Data saved to australian_companies_data.xlsx")

if __name__ == "__main__":
    australian_companies = [
        "The Recruitment Company", "Entourage", "TrainTheCrowd", "Atarix", "Glaukos Corporation",
        "Belloy Avenue Dental", "Tiliter", "Propel Ventures", "Quorum Systems", "Moddex Group",
        # ... (rest of the company list)
        "Marriott International Australia", "DHL Supply Chain", "Specsavers", "Capgemini Australia", "Story House Early Learning"
    ]
    
    main(australian_companies)