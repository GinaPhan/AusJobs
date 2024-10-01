from flask import Flask, jsonify, request
import pandas as pd
from collections import Counter
import re

app = Flask(__name__)

# Load the data
df = pd.read_excel('company_information_full.xlsx')

@app.route('/api/company_size_distribution')
def company_size_distribution():
    size_distribution = df['company_size'].value_counts().to_dict()
    return jsonify(size_distribution)

@app.route('/api/industry_breakdown')
def industry_breakdown():
    industry_breakdown = df['industry'].value_counts().to_dict()
    return jsonify(industry_breakdown)

@app.route('/api/geographical_distribution')
def geographical_distribution():
    country_distribution = df['hq_country'].value_counts().to_dict()
    return jsonify(country_distribution)

@app.route('/api/follower_count_analysis')
def follower_count_analysis():
    follower_counts = df['follower_count'].dropna().tolist()
    return jsonify(follower_counts)

@app.route('/api/founded_year_timeline')
def founded_year_timeline():
    year_counts = df['founded_year'].value_counts().sort_index().to_dict()
    return jsonify(year_counts)

@app.route('/api/top_companies_followers')
def top_companies_followers():
    top_n = request.args.get('n', default=10, type=int)
    top_companies = df.nlargest(top_n, 'follower_count')[['name', 'follower_count']]
    return jsonify(top_companies.to_dict(orient='records'))

@app.route('/api/specialties_wordcloud')
def specialties_wordcloud():
    all_specialties = ' '.join(df['specialities'].dropna())
    words = re.findall(r'\w+', all_specialties.lower())
    word_freq = Counter(words).most_common(100)
    return jsonify(dict(word_freq))

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

@app.route('/api/company_details/<company_name>')
def company_details(company_name):
    company = df[df['name'] == company_name].to_dict(orient='records')
    if company:
        return jsonify(company[0])
    else:
        return jsonify({"error": "Company not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)