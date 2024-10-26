# Company Data Analytics Dashboard

A full-stack web application that analyzes and visualizes company data from LinkedIn, focusing on Best Places to Work. The project consists of a Flask backend API for data processing and a Streamlit frontend for interactive data visualization.

## 🌟 Features

- **Company Size Analysis**: Distribution of companies by employee count
- **Industry Breakdown**: Interactive treemap of company industries
- **Geographical Distribution**: 
  - World map visualization of company locations
  - Detailed Australian state-level analysis
- **Performance Metrics**:
  - LinkedIn follower count analysis
  - Founded year timeline
  - Specialties word cloud
- **Company Comparison**: Direct comparison of company metrics against industry averages
- **Advanced Analytics**:
  - Funding analysis
  - Employee count vs. follower count correlation
  - Company type distribution

## 🛠️ Tech Stack

- **Backend**: 
  - Flask (Python web framework)
  - Pandas (Data processing)
  - NumPy (Numerical operations)
- **Frontend**:
  - Streamlit (Interactive dashboard)
  - Plotly (Data visualization)
  - Matplotlib (Word cloud visualization)
- **Data Source**:
  - ProxyCurl API (LinkedIn data)
    - Company Lookup endpoint
    - Company Profile endpoint

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/GinaPhan/AusJobs.git
cd AusJobs
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Create a .env file in the root directory and add your ProxyCurl API key:
```bash
PROXYCURL_API=your_api_key
```

## 🎯 Usage

1. Start the Flask backend:
```bash
python app.py
```
The API will be available at `http://localhost:5050`

2. In a new terminal, start the Streamlit frontend:
```bash
streamlit run visualization.py
```
The dashboard will open in your default web browser.

## 📊 API Endpoints

- `/api/company_size_distribution`: Get company size distribution
- `/api/industry_breakdown`: Get industry distribution
- `/api/geographical_distribution`: Get company location data
- `/api/follower_count_analysis`: Get follower count statistics
- `/api/top_companies_by_followers`: Get top companies by follower count
- `/api/founded_year_timeline`: Get company founding timeline
- `/api/specialties_wordcloud`: Get specialty analysis
- `/api/company_type_distribution`: Get company type distribution
- `/api/funding_analysis`: Get funding statistics
- `/api/employee_follower_correlation`: Get employee vs follower correlation
- `/api/company_details/<company_name>`: Get detailed company information
- `/api/company_names`: Get list of all company names

## 📁 Project Structure

```
company-data-analytics/
├── app.py                  # Flask backend
├── visualization.py        # Streamlit frontend
├── data/
│   ├── processed_data/    # Processed company data
│   └── map/              # Map data for visualizations
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
└── README.md             # Project documentation
```

## 🔍 Data Sources

The application uses the ProxyCurl API to fetch LinkedIn company data:
- `LOOKUP_ENDPOINT`: "https://nubela.co/proxycurl/api/linkedin/company/resolve"
- `PROFILE_ENDPOINT`: "https://nubela.co/proxycurl/api/linkedin/company"

## 🛡️ License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

Gina Phan - [thaihongngoc.phan@students.mq.edu.au](mailto:thaihongngoc.phan@students.mq.edu.au)

Project Link: [https://github.com/GinaPhan/AusJobs](https://github.com/GinaPhan/AusJobs)