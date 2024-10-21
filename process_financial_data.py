import csv
import pandas as pd

def process_financial_data(input_file, output_file):
    # Read the CSV file
    df = pd.read_csv(input_file)

    # Remove rows where all financial data is empty or zero
    financial_columns = df.columns.drop(['company_name', 'matched_name', 'symbol', 'exchange', 'currency', 'date', 'calendarYear', 'period', 'link', 'finalLink', 'error'])
    df['has_data'] = df[financial_columns].apply(lambda x: x.notna().any() and (x != 0).any(), axis=1)
    df = df[df['has_data']].drop(columns=['has_data'])

    # Sort the dataframe by company name and date
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.sort_values(['company_name', 'date'])

    # Write to CSV
    df.to_csv(output_file, index=False)

    print(f"Processed data has been written to {output_file}")

    # Print companies with data
    companies_with_data = df['company_name'].unique()
    print("\nCompanies with financial data:")
    for company in companies_with_data:
        print(company)

    # Print companies without data
    all_companies = set(pd.read_csv(input_file)['company_name'].unique())
    companies_without_data = all_companies - set(companies_with_data)
    print("\nCompanies without financial data:")
    for company in companies_without_data:
        print(company)

# Use the function
input_file = 'financial_data_output/consolidated_financial_data.csv'
output_file = 'processed_financial_data.csv'
process_financial_data(input_file, output_file)