"""Quick CSV inspection script"""
import pandas as pd
import os

def inspect_csv():
    csv_files = ["sample_data.csv", "../sample_data.csv", "../../cash_app_transactions.csv"]
    
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            print(f"Inspecting: {csv_file}")
            try:
                df = pd.read_csv(csv_file)
                print(f"Shape: {df.shape}")
                print(f"Columns: {list(df.columns)}")
                print(f"First few rows:")
                print(df.head())
                print("-" * 50)
                break
            except Exception as e:
                print(f"Error reading {csv_file}: {e}")
    else:
        print("No CSV files found")

if __name__ == "__main__":
    inspect_csv()
