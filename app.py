from flask import Flask, jsonify, request
import pandas as pd
from collections import Counter
import re
from urllib.parse import unquote
import numpy as np
import csv
import json

app = Flask(__name__)

# Load the data
df = pd.read_excel('cleaned_state_data.xlsx')

import pandas as pd
import csv
from flask import jsonify
from urllib.parse import unquote
import json
import numpy as np

@app.route('/api/create_csv_files')
def create_csv_files():
    # Dictionary for capital/major cities to handle null cities
    capital_cities = {
        'AU': 'Sydney',
        'NZ': 'Wellington',
        'GB': 'London',
        'BR': 'Brasília',
        'SG': 'Singapore',
        'IE': 'Dublin',
        'DE': 'Berlin',
        'CH': 'Zurich',
        'IT': 'Rome',
        'US': 'Washington D.C.',
        'CA': 'Ottawa',
        'FR': 'Paris',
        'ES': 'Madrid',
        'BE': 'Brussels',
        'NL': 'Amsterdam',
        'AT': 'Vienna',
        'PL': 'Warsaw',
        'SE': 'Stockholm',
        'DK': 'Copenhagen',
        'NO': 'Oslo',
        'FI': 'Helsinki',
        'JP': 'Tokyo',
        'KR': 'Seoul',
        'CN': 'Beijing',
        'IN': 'New Delhi',
        'RU': 'Moscow',
        'ZA': 'Pretoria',
        'AE': 'Abu Dhabi',
        'SA': 'Riyadh',
        'TR': 'Ankara',
        'IL': 'Jerusalem',
        'EG': 'Cairo',
        'MY': 'Kuala Lumpur',
        'TH': 'Bangkok',
        'ID': 'Jakarta',
        'PH': 'Manila',
        'VN': 'Hanoi',
        'MX': 'Mexico City',
        'AR': 'Buenos Aires',
        'CL': 'Santiago',
        'CO': 'Bogotá',
        'PE': 'Lima',
        'HK': 'Hong Kong'
    }

    # Helper functions from the geographical distribution endpoint
    def extract_locations(row):
        if pd.isna(row['locations']):
            return []
        try:
            locations_list = json.loads(row['locations']) if isinstance(row['locations'], str) else row['locations']
            return [(country_map.get(loc['country'], loc['country']), loc.get('state'))
                    for loc in locations_list if isinstance(loc, dict) and 'country' in loc]
        except json.JSONDecodeError:
            return []
        except Exception as e:
            print(f"Error processing location: {row['locations']}. Error: {str(e)}")
            return []

    def count_specialties(specialties):
        if pd.isna(specialties):
            return 0
        return len(str(specialties).split(','))
    
    def specialties_list(specialties):
        if pd.isna(specialties):
            return ''
        return str(specialties).replace('"', '')

    def count_countries(locations):
        if pd.isna(locations):
            return 0
        try:
            locations_list = json.loads(locations)
        except json.JSONDecodeError:
            return len(set(str(locations).split(',')))
        
        if isinstance(locations_list, list):
            return len(set(loc.get('country') for loc in locations_list if isinstance(loc, dict) and 'country' in loc))
        else:
            return 1
        
    def countries_list(locations):
        if pd.isna(locations):
            return ''
        try:
            locations_list = json.loads(locations)
        except json.JSONDecodeError:
            return ','.join(locations)
        
        if isinstance(locations_list, list):
            try: 
                return ','.join(set(loc.get('country') for loc in locations_list if isinstance(loc, dict) and 'country' in loc))
            except:
                return ''
        else:
            return ','.join(locations)

    def safe_int(value):
        try:
            if pd.isna(value):
                return 0
            return int(round(value))
        except:
            return 0
        
    def safe_str(value):
        try:
            if pd.isna(value):
                return ''
            return value
        except:
            return ''

    # New function to extract city data
    def extract_city_data(row):
        if pd.isna(row['locations']):
            return []
        try:
            locations_list = json.loads(row['locations']) if isinstance(row['locations'], str) else row['locations']
            city_data = []
            for loc in locations_list:
                if isinstance(loc, dict) and 'country' in loc:
                    city = loc.get('city')
                    country = loc['country']
                    
                    # If city is null or empty, use capital city of the country
                    if not city and country in capital_cities:
                        city = capital_cities[country]
                        
                    if city:  # Only add if we have a city (either original or capital)
                        city_data.append({
                            'Company': row['name'],
                            'City': city.strip(),
                            'Country': country
                        })
            return city_data
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error processing location for city data: {row['locations']}. Error: {str(e)}")
            return []

    # 1. Create company_data.csv
    columns_to_include = [
        'follower_count',
        'company_size_on_linkedin',
        'founded_year',
    ]

    # Add specialty and country counts to DataFrame
    df['specialties_list'] = df['specialities'].apply(specialties_list)
    df['countries_list'] = df['locations'].apply(countries_list)
    df['num_specialties'] = df['specialities'].apply(count_specialties)
    df['num_countries'] = df['locations'].apply(count_countries)
    columns_to_include.extend(['num_specialties', 'num_countries', 'specialties_list', 'countries_list'])

    df.drop_duplicates()

    # Create company data CSV
    company_data = []
    for _, company in df.iterrows():
        company_name = company['name']
        for column in columns_to_include:
            if pd.notnull(company[column]) and column not in ['specialties_list', 'countries_list']:
                company_data.append({
                    'Company': company_name,
                    'Value': safe_int(company[column]),
                    'Type': column
                })
            elif pd.notnull(company[column]) and column in ['specialties_list', 'countries_list']:
                company_data.append({
                    'Company': company_name,
                    'Value': safe_str(company[column]),
                    'Type': column
                })

    # 2. Create world_data.csv
    df['extracted_locations'] = df.apply(extract_locations, axis=1)
    exploded_df = df.explode('extracted_locations')
    exploded_df[['country', 'state']] = pd.DataFrame(exploded_df['extracted_locations'].tolist(), index=exploded_df.index)

    # Group by country
    grouped = exploded_df.groupby('country').agg({
        'name': 'count',
        'follower_count': 'mean',
        'company_size_on_linkedin': 'mean',
        'founded_year': 'median'
    }).reset_index()

    # Create world data CSV
    world_data = []
    for _, row in grouped.iterrows():
        world_data.extend([
            {'Entity': row['country'], 'Value': safe_int(row['name']), 'Type': 'company_count'},
            {'Entity': row['country'], 'Value': safe_int(row['follower_count']), 'Type': 'avg_follower_count'},
            {'Entity': row['country'], 'Value': safe_int(row['company_size_on_linkedin']), 'Type': 'avg_company_size'},
            {'Entity': row['country'], 'Value': safe_int(row['founded_year']), 'Type': 'median_founding_year'}
        ])

    # 3. Create australia_data.csv
    australia_df = exploded_df[exploded_df['country'] == 'Australia']
    australia_df['state_code'] = australia_df['state'].map(state_name_mapping)

    state_grouped = australia_df.groupby('state_code').agg({
        'name': 'count',
        'follower_count': 'mean',
        'company_size_on_linkedin': 'mean',
        'founded_year': 'median'
    }).reset_index()

    # Create Australia data CSV
    australia_data = []
    for _, row in state_grouped.iterrows():
        state_name = state_code_to_name.get(row['state_code'], row['state_code'])
        australia_data.extend([
            {'Entity': state_name, 'Value': safe_int(row['name']), 'Type': 'company_count'},
            {'Entity': state_name, 'Value': safe_int(row['follower_count']), 'Type': 'avg_follower_count'},
            {'Entity': state_name, 'Value': safe_int(row['company_size_on_linkedin']), 'Type': 'avg_company_size'},
            {'Entity': state_name, 'Value': safe_int(row['founded_year']), 'Type': 'median_founding_year'}
        ])

    # 4. Generate city data
    city_data = []
    for _, row in df.iterrows():
        city_data.extend(extract_city_data(row))

    # Write all CSV files
    files_to_write = [
        ('company_data.csv', company_data, ['Company', 'Value', 'Type']),
        ('world_data.csv', world_data, ['Entity', 'Value', 'Type']),
        ('australia_data.csv', australia_data, ['Entity', 'Value', 'Type']),
        ('city_locations.csv', city_data, ['Company', 'City', 'Country'])
    ]

    for filename, data, fieldnames in files_to_write:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    return jsonify({
        "message": "CSV files created successfully",
        "files": ["company_data.csv", "world_data.csv", "australia_data.csv", "city_locations.csv"]
    }), 200

# Load Australian states GeoJSON
with open('data/map/australian-states.json', 'r') as f:
    australia_geojson = json.load(f)

# Mapping of state codes to names
state_code_to_name = {
    feature['properties']['STATE_CODE']: feature['properties']['STATE_NAME']
    for feature in australia_geojson['features']
}

# Reverse mapping of state names to codes
state_name_to_code = {v: k for k, v in state_code_to_name.items()}

# Additional mappings for state names
state_name_mapping = {
    'ACT': '8',
    'Australian Capital Territory': '8',
    'NSW': '1',
    'New South Wales': '1',
    'New South Wales,': '1',
    'VIC': '2',
    'Victoria': '2',
    'QLD': '3',
    'Queensland': '3',
    'SA': '4',
    'South Australia': '4',
    'WA': '5',
    'Western Australia': '5',
    'TAS': '6',
    'Tasmania': '6',
    'NT': '7',
    'Northern Territory': '7'
}

# Mapping of country codes to Plotly-compatible country names
country_map = {
    'AU': 'Australia',
    'US': 'United States',
    'GB': 'United Kingdom',
    'IE': 'Ireland',
    'SG': 'Singapore',
    'DE': 'Germany',
    'CH': 'Switzerland',
    'IT': 'Italy',
    'CA': 'Canada',
    'NZ': 'New Zealand',
    'BR': 'Brazil',
    'ES': 'Spain',
    'FR': 'France',
    'NL': 'Netherlands',
    'BE': 'Belgium',
    'DK': 'Denmark',
    'SE': 'Sweden',
    'NO': 'Norway',
    'FI': 'Finland',
    'JP': 'Japan',
    'KR': 'South Korea',
    'CN': 'China',
    'HK': 'Hong Kong',
    'TW': 'Taiwan',
    'IN': 'India',
    'MY': 'Malaysia',
    'TH': 'Thailand',
    'ID': 'Indonesia',
    'PH': 'Philippines',
    'VN': 'Vietnam',
    'ZA': 'South Africa',
    'AE': 'United Arab Emirates',
    'SA': 'Saudi Arabia',
    'TR': 'Turkey',
    'IL': 'Israel',
    'RU': 'Russia',
    'PL': 'Poland',
    'CZ': 'Czech Republic',
    'HU': 'Hungary',
    'RO': 'Romania',
    'AT': 'Austria',
    'PT': 'Portugal',
    'GR': 'Greece',
    'LU': 'Luxembourg',
    'MX': 'Mexico',
    'AR': 'Argentina',
    'CL': 'Chile',
    'CO': 'Colombia',
    'PE': 'Peru',
    'EG': 'Egypt',
    'MA': 'Morocco',
    'QA': 'Qatar',
    'BH': 'Bahrain',
    'KW': 'Kuwait',
    'OM': 'Oman',
    'LB': 'Lebanon',
    'JO': 'Jordan',
    'UA': 'Ukraine',
    'RS': 'Serbia',
    'HR': 'Croatia',
    'SI': 'Slovenia',
    'SK': 'Slovakia',
    'BG': 'Bulgaria',
    'LT': 'Lithuania',
    'LV': 'Latvia',
    'EE': 'Estonia',
    'CY': 'Cyprus',
    'MT': 'Malta',
    'IS': 'Iceland',
    'AM': 'Armenia',
    'KZ': 'Kazakhstan',
    'UY': 'Uruguay',
    'DO': 'Dominican Republic',
    'CR': 'Costa Rica',
    'PA': 'Panama',
    'TT': 'Trinidad and Tobago',
    'JM': 'Jamaica',
    'BS': 'Bahamas',
    'BB': 'Barbados',
    'PS': 'Palestine',
    'LK': 'Sri Lanka',
    'BD': 'Bangladesh',
    'PK': 'Pakistan',
    'NP': 'Nepal',
    'MM': 'Myanmar',
    'KH': 'Cambodia',
    'LA': 'Laos',
    'BN': 'Brunei',
    'MO': 'Macau',
    'MV': 'Maldives',
    'FJ': 'Fiji',
    'PG': 'Papua New Guinea',
    'YE': 'Yemen'
}

@app.route('/api/company_size_distribution')
def company_size_distribution():
    def categorize_size(size):
        if size < 30:
            return "Micro (< 30)"
        elif size < 100:
            return "Small (30-99)"
        elif size < 500:
            return "Medium (100-499)"
        else:
            return "Large (500+)"

    # Use company_size_on_linkedin and convert to numeric, ignoring non-numeric values
    sizes = pd.to_numeric(df['company_size_on_linkedin'], errors='coerce')
    
    # Categorize sizes
    categorized_sizes = sizes.apply(categorize_size)
    
    # Count occurrences of each category
    size_distribution = categorized_sizes.value_counts().sort_index().to_dict()
    
    return jsonify(size_distribution)

@app.route('/api/industry_breakdown')
def industry_breakdown():
    industry_breakdown = df['industry'].value_counts().to_dict()
    return jsonify(industry_breakdown)

@app.route('/api/geographical_distribution')
def geographical_distribution():
    def extract_locations(row):
        if pd.isna(row['locations']):
            return []
        try:
            locations_list = json.loads(row['locations']) if isinstance(row['locations'], str) else row['locations']
            return [(country_map.get(loc['country'], loc['country']), loc.get('state')) 
                    for loc in locations_list if isinstance(loc, dict) and 'country' in loc]
        except json.JSONDecodeError:
            return []
        except Exception as e:
            print(f"Error processing location: {row['locations']}. Error: {str(e)}")
            return []

    # Apply the function to create a new column with extracted countries and states
    df['extracted_locations'] = df.apply(extract_locations, axis=1)

    # Explode the dataframe so each location is on a separate row
    exploded_df = df.explode('extracted_locations')

    # Split the extracted_locations into separate columns
    exploded_df[['country', 'state']] = pd.DataFrame(exploded_df['extracted_locations'].tolist(), index=exploded_df.index)

    # Group by country and aggregate
    grouped = exploded_df.groupby('country').agg({
        'name': 'count',
        'follower_count': 'mean',
        'company_size_on_linkedin': 'mean',
        'founded_year': 'median'
    }).reset_index()

    # Rename columns
    grouped.columns = ['country', 'company_count', 'avg_follower_count', 'avg_company_size', 'median_founding_year']

    # Round numerical values and handle NaN
    grouped['avg_follower_count'] = grouped['avg_follower_count'].round().fillna(0).astype(int)
    grouped['avg_company_size'] = grouped['avg_company_size'].round().fillna(0).astype(int)
    grouped['median_founding_year'] = grouped['median_founding_year'].round().fillna(0).astype(int)

    # Group by state for Australia and aggregate
    australia_df = exploded_df[exploded_df['country'] == 'Australia']
    australia_df['state_code'] = australia_df['state'].map(state_name_mapping)
    
    state_grouped = australia_df.groupby('state_code').agg({
        'name': 'count',
        'follower_count': 'mean',
        'company_size_on_linkedin': 'mean',
        'founded_year': 'median'
    }).reset_index()

    # Rename columns
    state_grouped.columns = ['state_code', 'company_count', 'avg_follower_count', 'avg_company_size', 'median_founding_year']

    # Round numerical values and handle NaN
    state_grouped['avg_follower_count'] = state_grouped['avg_follower_count'].round().fillna(0).astype(int)
    state_grouped['avg_company_size'] = state_grouped['avg_company_size'].round().fillna(0).astype(int)
    state_grouped['median_founding_year'] = state_grouped['median_founding_year'].round().fillna(0).astype(int)

    # Map state codes to names
    state_grouped['state_name'] = state_grouped['state_code'].map(state_code_to_name)

    return jsonify({
        'countries': grouped.to_dict(orient='records'),
        'australia_states': state_grouped.to_dict(orient='records'),
        'australia_geojson': australia_geojson
    })

@app.route('/api/follower_count_analysis')
def follower_count_analysis():
    follower_counts = df['follower_count'].dropna().tolist()
    return jsonify(follower_counts)

@app.route('/api/top_companies_by_followers')
def top_companies_by_followers():
    # Sort companies by follower count and get top 20
    top_companies = df.sort_values('follower_count', ascending=False).head(20)
    
    # Prepare data for API response
    result = top_companies[['name', 'follower_count', 'industry']].to_dict('records')
    
    return jsonify(result)

@app.route('/api/founded_year_timeline')
def founded_year_timeline():
    year_counts = df['founded_year'].value_counts().sort_index().to_dict()
    return jsonify(year_counts)

@app.route('/api/top_companies_followers')
def top_companies_followers():
    top_n = request.args.get('n', default=10, type=int)
    top_companies = df.nlargest(top_n, 'follower_count')[['name', 'follower_count']]
    return jsonify(top_companies.to_dict(orient='records'))

from flask import jsonify
from collections import Counter
import re
import pandas as pd
import numpy as np

@app.route('/api/specialties_wordcloud')
def specialties_wordcloud():
    # Common stop words (you can expand this list)
    stop_words = set(['and', 'the', 'to', 'of', 'in', 'for', 'a', 'an'])
    
    # Dictionary to store word clouds for each industry
    industry_wordclouds = {}
    
    # List to store rows for CSV
    csv_rows = []
    
    # Clean industry values: replace NaN with 'Unknown' and convert to string
    df['industry_clean'] = df['industry'].fillna('Unknown').astype(str)
    
    # Group the dataframe by cleaned industry
    for industry in df['industry_clean'].unique():
        # Skip empty or whitespace-only industry names
        if not industry.strip():
            continue
            
        # Filter dataframe for current industry
        industry_df = df[df['industry_clean'] == industry]
        
        # Combine all specialties for this industry into a single string
        industry_specialties = ' '.join(industry_df['specialities'].dropna().astype(str))
        
        # Clean the text: remove special characters and convert to lowercase
        cleaned_text = re.sub(r'[^\w\s]', '', industry_specialties.lower())
        
        # Split into words
        words = cleaned_text.split()
        
        # Count word frequencies
        word_freq = Counter(words)
        
        # Remove stop words
        word_freq = {word: count for word, count in word_freq.items() 
                    if word not in stop_words}
        
        # Sort by frequency and take top 100 for each industry
        top_100 = dict(sorted(word_freq.items(), 
                            key=lambda x: x[1], 
                            reverse=True)[:100])
        
        # Only add to results if we have words for this industry
        if top_100:
            industry_wordclouds[industry] = top_100
            
            # Add rows to CSV data
            for keyword, count in top_100.items():
                csv_rows.append([industry, keyword, count])
    
    # Write to CSV file
    csv_filename = 'industry_keywords.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(['Industry', 'Keyword', 'Count'])
        # Write data rows
        writer.writerows(csv_rows)
    
    return jsonify(industry_wordclouds)

@app.route('/api/company_type_distribution')
def company_type_distribution():
    type_distribution = df['company_type'].value_counts().to_dict()
    return jsonify(type_distribution)

@app.route('/api/funding_analysis')
def funding_analysis():
    funding_data = df[['name', 'extra_number_of_funding_rounds', 'extra_total_funding_amount']].dropna()
    return jsonify(funding_data.to_dict(orient='records'))

@app.route('/api/employee_follower_correlation')
def employee_follower_correlation():
    correlation_data = df[['company_size', 'follower_count']].dropna()
    return jsonify(correlation_data.to_dict(orient='records'))

@app.route('/api/company_details/<path:company_name>')
def company_details(company_name):
    decoded_name = unquote(company_name)
    
    company = df[df['name'] == decoded_name]
    
    if company.empty:
        return jsonify({"error": "Company not found"}), 404
    
    company = company.iloc[0]
    
    # Calculate mean of numeric columns only
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    avg_data = df[numeric_columns].mean()
    
    def safe_int(value):
        try:
            return int(value) if pd.notnull(value) else None
        except:
            return None

    def count_specialties(specialties):
        if pd.isna(specialties):
            return 0
        return len(str(specialties).split(','))

    def count_countries(locations):
        if pd.isna(locations):
            return 0
        try:
            # Try parsing as JSON
            locations_list = json.loads(locations)
        except json.JSONDecodeError:
            # If not JSON, try splitting by comma
            return len(set(str(locations).split(',')))
        
        if isinstance(locations_list, list):
            return len(set(loc.get('country') for loc in locations_list if isinstance(loc, dict) and 'country' in loc))
        else:
            return 1  # If it's not a list, assume it's a single location

    # Calculate average number of specialties and countries
    df['num_specialties'] = df['specialities'].apply(count_specialties)
    df['num_countries'] = df['locations'].apply(count_countries)
    avg_specialties = df['num_specialties'].mean()
    avg_countries = df['num_countries'].mean()

    details = {
        'name': company['name'],
        'industry': company['industry'],
        'description': company['description'],
        'website': company['website'],
        'follower_count': safe_int(company['follower_count']),
        'avg_follower_count': safe_int(avg_data.get('follower_count')),
        'company_size': safe_int(company['company_size_on_linkedin']),
        'avg_company_size': safe_int(avg_data.get('company_size_on_linkedin')),
        'founded_year': safe_int(company['founded_year']),
        'avg_founded_year': safe_int(avg_data.get('founded_year')),
        'num_specialties': count_specialties(company['specialities']),
        'avg_num_specialties': round(avg_specialties),  # Rounded to integer
        'num_countries': count_countries(company['locations']),
        'avg_num_countries': round(avg_countries),  # Rounded to integer
        'Image_Path': company['Image_Path'] if pd.notnull(company['Image_Path']) else None
    }
    
    return jsonify(details)

@app.route('/api/company_names')
def company_names():
    names = df['name'].tolist()
    return jsonify(names)

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)