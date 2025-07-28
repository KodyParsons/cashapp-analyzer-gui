def validate_csv_file(file_path):
    """Validate the CSV file format and contents."""
    try:
        df = pd.read_csv(file_path)
        # Check for required columns (example: 'Date', 'Net Amount')
        required_columns = ['Date', 'Net Amount']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"CSV file must contain the following columns: {', '.join(required_columns)}")
        return df
    except Exception as e:
        raise ValueError(f"Error validating CSV file: {e}")

def format_date(date_str):
    """Format a date string to a standard format (YYYY-MM-DD)."""
    try:
        return pd.to_datetime(date_str).strftime('%Y-%m-%d')
    except Exception as e:
        raise ValueError(f"Error formatting date: {e}")

def calculate_date_range(start_date, end_date):
    """Calculate the range of dates between start and end dates."""
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    return pd.date_range(start=start, end=end)