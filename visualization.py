import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import requests
import pandas as pd

API_URL = "http://localhost:5050/api"

st.set_page_config(page_title="Company Data Dashboard", layout="wide")
st.title("Company Data Dashboard")

@st.cache_data
def fetch_data(endpoint):
    response = requests.get(f"{API_URL}/{endpoint}")
    return response.json()

# Company Size Distribution
def plot_company_size_distribution():
    data = fetch_data("company_size_distribution")
    fig = px.pie(values=list(data.values()), names=list(data.keys()), title="Company Size Distribution")
    st.plotly_chart(fig)

# Industry Breakdown
def plot_industry_breakdown():
    data = fetch_data("industry_breakdown")
    fig = px.treemap(names=list(data.keys()), parents=[""] * len(data), values=list(data.values()), title="Industry Breakdown")
    st.plotly_chart(fig)

# Geographical Distribution
def plot_geographical_distribution():
    data = fetch_data("geographical_distribution")
    fig = px.choropleth(locations=list(data.keys()), locationmode="country names", color=list(data.values()), 
                        title="Geographical Distribution", color_continuous_scale=px.colors.sequential.Plasma)
    st.plotly_chart(fig)

# Follower Count Analysis
def plot_follower_count_analysis():
    data = fetch_data("follower_count_analysis")
    fig = px.histogram(x=data, title="Follower Count Distribution")
    st.plotly_chart(fig)

# Founded Year Timeline
def plot_founded_year_timeline():
    data = fetch_data("founded_year_timeline")
    fig = px.line(x=list(data.keys()), y=list(data.values()), title="Companies Founded by Year")
    st.plotly_chart(fig)

# Top Companies by Follower Count
def plot_top_companies_followers():
    data = fetch_data("top_companies_followers")
    df = pd.DataFrame(data)
    fig = px.bar(df, x='name', y='follower_count', title="Top Companies by Follower Count")
    st.plotly_chart(fig)

# Specialties Word Cloud
def plot_specialties_wordcloud():
    data = fetch_data("specialties_wordcloud")
    words = list(data.keys())
    frequencies = list(data.values())
    fig = go.Figure(data=[go.Scatter(x=[0,1], y=[0,1], mode="text", text=words, 
                                     marker=dict(opacity=[freq/max(frequencies) for freq in frequencies]),
                                     textfont=dict(size=[freq/max(frequencies)*50 for freq in frequencies]))])
    fig.update_layout(title="Specialties Word Cloud")
    st.plotly_chart(fig)

# Company Type Distribution
def plot_company_type_distribution():
    data = fetch_data("company_type_distribution")
    fig = px.pie(values=list(data.values()), names=list(data.keys()), title="Company Type Distribution")
    st.plotly_chart(fig)

# Funding Analysis
def plot_funding_analysis():
    data = fetch_data("funding_analysis")
    df = pd.DataFrame(data)
    fig = px.scatter(df, x='extra_number_of_funding_rounds', y='extra_total_funding_amount', 
                     hover_name='name', title="Funding Analysis")
    st.plotly_chart(fig)

# Employee Count vs Follower Count
def plot_employee_follower_correlation():
    data = fetch_data("employee_follower_correlation")
    df = pd.DataFrame(data)
    fig = px.scatter(df, x='company_size', y='follower_count', title="Employee Count vs Follower Count")
    st.plotly_chart(fig)

# Main app
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Company Size", "Industry", "Geography", "Followers", "Founded Year", 
                                      "Top Companies", "Specialties", "Company Type", "Funding", "Employee vs Followers"])

    if page == "Company Size":
        plot_company_size_distribution()
    elif page == "Industry":
        plot_industry_breakdown()
    elif page == "Geography":
        plot_geographical_distribution()
    elif page == "Followers":
        plot_follower_count_analysis()
    elif page == "Founded Year":
        plot_founded_year_timeline()
    elif page == "Top Companies":
        plot_top_companies_followers()
    elif page == "Specialties":
        plot_specialties_wordcloud()
    elif page == "Company Type":
        plot_company_type_distribution()
    elif page == "Funding":
        plot_funding_analysis()
    elif page == "Employee vs Followers":
        plot_employee_follower_correlation()

if __name__ == "__main__":
    main()