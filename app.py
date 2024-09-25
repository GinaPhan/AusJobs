from flask import Flask, jsonify, render_template
import pandas as pd
from urllib.parse import unquote
import json
import numpy as np

app = Flask(__name__)

# Custom JSON encoder to handle NaN values
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        return super(CustomJSONEncoder, self).default(obj)

app.json_encoder = CustomJSONEncoder

# Load the Excel file
df = pd.read_excel('company_information_full.xlsx')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/companies', methods=['GET'])
def get_companies():
    # Convert the dataframe to a list of dictionaries
    companies = df.to_dict('records')
    
    # Limit the data sent to just what's needed for the company cards
    limited_data = [
        {
            'name': company['Company Name'],
            'industry': company['industry'] if pd.notna(company['industry']) else None,
            'profilePicUrl': company['profile_pic_url'] if pd.notna(company['profile_pic_url']) else None
        }
        for company in companies
    ]
    
    return jsonify(limited_data)

@app.route('/api/company/<path:name>', methods=['GET'])
def get_company(name):
    # Decode the URL-encoded company name
    decoded_name = unquote(name)
    
    # Find the company by name
    company = df[df['Company Name'] == decoded_name].to_dict('records')
    
    if company:
        # Replace NaN values with None
        company_data = {k: (v if pd.notna(v) else None) for k, v in company[0].items()}
        return jsonify(company_data)
    else:
        return jsonify({'error': 'Company not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)