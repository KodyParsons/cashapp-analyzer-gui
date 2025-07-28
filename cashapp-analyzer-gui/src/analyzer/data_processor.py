def generate_monthly_summary(df, start_date, end_date):
    """Generate a monthly summary of transactions within the specified date range."""
    mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
    filtered_df = df.loc[mask]
    
    monthly_summary = filtered_df.groupby('Month_Year').agg({
        'Net_Amount': ['sum', 'count'],
        'Category': lambda x: x.value_counts().index[0]  # Most common category
    }).round(2)
    
    return monthly_summary

def process_csv_data(file_path):
    """Load and process CSV data from the given file path."""
    df = pd.read_csv(file_path)
    # Additional processing steps can be added here
    return df

def validate_csv_structure(df):
    """Validate the structure of the CSV data."""
    required_columns = ['Date', 'Net Amount', 'Category']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    return True

def summarize_category_spending(df):
    """Summarize spending by category."""
    category_spending = df[df['Net_Amount'] < 0].groupby('Category')['Net_Amount'].sum().abs().sort_values(ascending=False)
    return category_spending