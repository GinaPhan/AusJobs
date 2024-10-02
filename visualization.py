import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import requests
from urllib.parse import quote
from plotly.subplots import make_subplots
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

API_URL = "http://localhost:5050/api"

st.set_page_config(page_title="Company Data Dashboard", layout="wide")

@st.cache_data
def fetch_data(endpoint):
    response = requests.get(f"{API_URL}/{endpoint}")
    return response.json()

def fetch_company_names():
    response = requests.get(f"{API_URL}/company_names")
    return response.json()

def fetch_company_details(company_name):
    encoded_name = quote(company_name)
    response = requests.get(f"{API_URL}/company_details/{encoded_name}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching company details: {response.text}")
        return None

# Company Size Distribution
def plot_company_size_distribution():
    data = fetch_data("company_size_distribution")
    
    categories = list(data.keys())
    values = list(data.values())
    
    color_map = {
        "Micro (< 30)": "#FFA07A",
        "Small (30-99)": "#98FB98",
        "Medium (100-499)": "#87CEFA",
        "Large (500+)": "#DDA0DD"
    }
    
    fig = px.pie(
        values=values,
        names=categories,
        title="Company Size Distribution",
        color=categories,
        color_discrete_map=color_map
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        height=600,
        legend_title_text='Company Size',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Industry Breakdown
def plot_industry_breakdown():
    data = fetch_data("industry_breakdown")
    fig = px.treemap(names=list(data.keys()), parents=[""] * len(data), values=list(data.values()), title="Industry Breakdown")
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

# Geographical Distribution
def plot_geographical_distribution():
    data = fetch_data("geographical_distribution")
    
    if not data:
        st.error("Failed to fetch geographical distribution data.")
        return

    df_countries = pd.DataFrame(data['countries'])
    df_australia_states = pd.DataFrame(data['australia_states'])
    australia_geojson = data['australia_geojson']

    # Create a dropdown for selecting the view
    view_options = ['World', 'Australia']
    selected_view = st.selectbox("Select view", view_options)

    # Create a dropdown for attribute selection
    attributes = {
        'Company Count': 'company_count',
        'Average Follower Count': 'avg_follower_count',
        'Average Company Size': 'avg_company_size',
        'Median Founding Year': 'median_founding_year'
    }
    selected_attribute = st.selectbox("Select attribute to visualize", list(attributes.keys()))

    if selected_view == 'World':
        fig = px.choropleth(
            df_countries,
            locations='country',
            locationmode="country names",
            color=attributes[selected_attribute], 
            hover_name='country',
            color_continuous_scale="YlOrRd",
            title=f"{selected_attribute} by Country",
            range_color=[df_countries[attributes[selected_attribute]].min(), df_countries[attributes[selected_attribute]].max()]
        )
    else:
        fig = px.choropleth(
            df_australia_states,
            geojson=australia_geojson,
            locations='state_code',
            featureidkey="properties.STATE_CODE",
            color=attributes[selected_attribute],
            hover_name='state_name',
            color_continuous_scale="YlOrRd",
            title=f"{selected_attribute} by Australian State",
            range_color=[df_australia_states[attributes[selected_attribute]].min(), df_australia_states[attributes[selected_attribute]].max()]
        )
        fig.update_geos(fitbounds="locations", visible=False)

    fig.update_layout(
        height=600,
        geo=dict(showframe=False, showcoastlines=True),
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Display statistics
    if selected_view == 'World':
        df = df_countries
        location_column = 'country'
    else:
        df = df_australia_states
        location_column = 'state_name'

    st.subheader(f"Top 10 {location_column.title()}s by {selected_attribute}")
    top_10 = df.sort_values(attributes[selected_attribute], ascending=False).head(10)
    for _, row in top_10.iterrows():
        st.write(f"{row[location_column]}: {row[attributes[selected_attribute]]}")

    st.write(f"Average {selected_attribute.lower()}: {df[attributes[selected_attribute]].mean():.2f}")

# Founded Year Timeline
def plot_founded_year_timeline():
    data = fetch_data("founded_year_timeline")
    fig = px.line(x=list(data.keys()), y=list(data.values()), title="Companies Founded by Year")
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)
    
def plot_top_companies_by_followers():
    data = fetch_data("top_companies_followers")
    
    if not data:
        st.error("Failed to fetch top companies by followers data.")
        return

    df = pd.DataFrame(data)
    df = df.drop_duplicates()
    
    # Create the bar chart
    fig = px.bar(
        df,
        x='name',
        y='follower_count',
        title="Top Companies by LinkedIn Follower Count",
        labels={'name': 'Company Name', 'follower_count': 'Follower Count'},
        # hover_data=['industry']
    )
    
    fig.update_layout(
        height=600,
        xaxis_title="Company",
        yaxis_title="Follower Count",
        xaxis={'categoryorder':'total descending'}
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Display statistics
    st.subheader("Top 10 Companies by Follower Count")
    for _, row in df.head(10).iterrows():
        st.write(f"{row['name']}: {row['follower_count']:,} followers")

    st.write(f"Average follower count: {df['follower_count'].mean():,.0f}")

# Specialties Word Cloud
def plot_specialties_wordcloud():
    data = fetch_data("specialties_wordcloud")
    
    if not data:
        st.warning("No specialty data available.")
        return
    
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(data)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Specialties Word Cloud')
    
    st.pyplot(plt.gcf())
    
    top_20 = dict(sorted(data.items(), key=lambda x: x[1], reverse=True)[:20])
    
    fig = px.bar(
        x=list(top_20.values()),
        y=list(top_20.keys()),
        orientation='h',
        labels={'x': 'Frequency', 'y': 'Specialty'},
        title="Top 20 Specialties"
    )
    
    fig.update_layout(height=600)
    
    st.plotly_chart(fig, use_container_width=True)

# Company Type Distribution
def plot_company_type_distribution():
    data = fetch_data("company_type_distribution")
    fig = px.pie(values=list(data.values()), names=list(data.keys()), title="Company Type Distribution")
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

# Funding Analysis
def plot_funding_analysis():
    data = fetch_data("funding_analysis")
    df = pd.DataFrame(data)
    fig = px.scatter(df, x='extra_number_of_funding_rounds', y='extra_total_funding_amount', 
                     hover_name='name', title="Funding Analysis")
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

# Employee Count vs Follower Count
def plot_employee_follower_correlation():
    data = fetch_data("employee_follower_correlation")
    df = pd.DataFrame(data)
    fig = px.scatter(df, x='company_size', y='follower_count', title="Employee Count vs Follower Count")
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)
    
def plot_company_comparison(company_data):
    # Create subplots
    fig = make_subplots(rows=2, cols=2, subplot_titles=("Follower Count", "Company Size", "Founded Year", "Specialties and Countries"))

    # Follower Count
    fig.add_trace(go.Bar(x=['Company', 'Average'], 
                         y=[company_data['follower_count'], company_data['avg_follower_count']],
                         name='Follower Count'), row=1, col=1)

    # Company Size
    fig.add_trace(go.Bar(x=['Company', 'Average'], 
                         y=[company_data['company_size'], company_data['avg_company_size']],
                         name='Company Size'), row=1, col=2)

    # Founded Year
    fig.add_trace(go.Bar(x=['Company', 'Average'], 
                         y=[company_data['founded_year'], company_data['avg_founded_year']],
                         name='Founded Year'), row=2, col=1)

    # Number of Specialties and Countries
    fig.add_trace(go.Bar(x=['Specialties', 'Countries'], 
                         y=[company_data['num_specialties'], company_data['num_countries']],
                         name='Company'), row=2, col=2)
    fig.add_trace(go.Bar(x=['Specialties', 'Countries'], 
                         y=[company_data['avg_num_specialties'], company_data['avg_num_countries']],
                         name='Average'), row=2, col=2)

    # Update layout
    fig.update_layout(height=700, width=1000, title_text="Company Comparison", showlegend=False)
    fig.update_traces(marker_color='#636EFA', selector=dict(name='Company'))
    fig.update_traces(marker_color='#EF553B', selector=dict(name='Average'))

    return fig

def company_comparison_page():
    st.title("Company Comparison")
    
    company_names = fetch_company_names()
    selected_company = st.selectbox("Select a company", company_names)
    
    if selected_company:
        company_data = fetch_company_details(selected_company)
        
        if company_data:
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if company_data.get('Image_Path'):
                    st.image(company_data['Image_Path'], width=200)
                
                st.subheader(company_data['name'])
                st.write(f"Industry: {company_data.get('industry', 'N/A')}")
                st.write(f"Website: {company_data.get('website', 'N/A')}")
            
            with col2:
                description = company_data.get('description', '')
                if description:
                    if len(description) > 300:
                        st.write(description[:300] + "...")
                        if st.button('Read more'):
                            st.write(description)
                    else:
                        st.write(description)
                else:
                    st.write("No description available.")
            
            fig = plot_company_comparison(company_data)
            st.plotly_chart(fig, use_container_width=True)
            
            metrics = [
                ("Follower Count", 'follower_count', 'avg_follower_count'),
                ("Company Size", 'company_size', 'avg_company_size'),
                ("Founded Year", 'founded_year', 'avg_founded_year'),
                ("Number of Specialties", 'num_specialties', 'avg_num_specialties'),
                ("Number of Countries", 'num_countries', 'avg_num_countries')
            ]
            
            cols = st.columns(len(metrics))
            for col, (label, company_key, avg_key) in zip(cols, metrics):
                company_value = company_data.get(company_key)
                avg_value = company_data.get(avg_key)
                if company_value is not None and avg_value is not None:
                    diff = company_value - avg_value
                    col.metric(
                        label,
                        f"{company_value:,}",
                        f"{diff:+,.0f} compared to average"
                    )
                else:
                    col.metric(label, "N/A", "N/A")
        else:
            st.error("Failed to fetch company details. Please try again.")
                
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Company Comparison", "Company Size", "Industry", "Geography", 
                                      "Top Companies by Followers", "Founded Year", "Specialties", 
                                      "Company Type", "Funding", "Employee vs Followers"])

    if page == "Company Comparison":
        company_comparison_page()
    elif page == "Company Size":
        plot_company_size_distribution()
    elif page == "Industry":
        plot_industry_breakdown()
    elif page == "Geography":
        plot_geographical_distribution()
    elif page == "Top Companies by Followers":
        plot_top_companies_by_followers()
    elif page == "Founded Year":
        plot_founded_year_timeline()
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