#!/usr/bin/env python3
"""
Analyze DCA amounts to see what's being classified as investments
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analyzer.cashapp_analyzer import CashAppAnalyzer
import pandas as pd
from datetime import datetime, timedelta

def analyze_dca_amounts():
    """Analyze what's being classified as DCA Savings"""
    
    # Path to the CSV file
    csv_path = r"w:\Analytics\Dept\Kody Parsons\Personal Vault\cashapp_PF\cash_app_transactions.csv"
    
    # Initialize analyzer
    analyzer = CashAppAnalyzer(csv_path)
    
    # Load and clean data
    print("Loading and cleaning data...")
    analyzer.load_and_clean_data()
    analyzer.categorize_transactions()
    
    # Filter for last month (May 2025)
    last_month = datetime(2025, 5, 1)
    end_month = datetime(2025, 5, 31)
    
    mask = (analyzer.df['Date'] >= last_month) & (analyzer.df['Date'] <= end_month)
    may_data = analyzer.df.loc[mask]
    
    print(f"\nMay 2025 DCA Savings transactions:")
    print("=" * 60)
    
    dca_savings = may_data[may_data['Category'] == 'Investment (DCA Savings)']
    
    if len(dca_savings) > 0:
        print(f"Total DCA Savings transactions: {len(dca_savings)}")
        print(f"Total DCA Savings amount: ${abs(dca_savings['Net_Amount'].sum()):.2f}")
        print("\nDetailed breakdown:")
        
        for _, row in dca_savings.iterrows():
            print(f"  {row['Date'].strftime('%Y-%m-%d')}: ${row['Net_Amount']:.2f} - {row['Transaction Type']} - {row.get('Notes', 'N/A')}")
        
        # Group by amount to see patterns
        amount_groups = dca_savings.groupby('Net_Amount').size().sort_values(ascending=False)
        print(f"\nAmount patterns:")
        for amount, count in amount_groups.items():
            print(f"  ${amount:.2f}: {count} transactions")
    else:
        print("No DCA Savings transactions found for May 2025")
    
    # Also check what specific amounts are in our DCA list
    print(f"\nConfigured DCA amounts in the code:")
    savings_amounts = [318.28, 286, 295, 334, 350, 382]
    for amount in savings_amounts:
        matching_transactions = analyzer.df[analyzer.df['Net_Amount'] == -amount]
        print(f"  ${amount}: {len(matching_transactions)} total transactions across all time")
        if len(matching_transactions) > 0:
            print(f"    Transaction types: {matching_transactions['Transaction Type'].value_counts().to_dict()}")
    
    # Check if there are any large "Savings Internal Transfer" transactions that might not be DCA
    print(f"\nAll 'Savings Internal Transfer' transactions in May 2025:")
    savings_transfers = may_data[
        (may_data['Transaction Type'] == 'Savings Internal Transfer') & 
        (may_data['Net_Amount'] < 0)
    ]
    
    if len(savings_transfers) > 0:
        print(f"Total savings transfers: {len(savings_transfers)}")
        for _, row in savings_transfers.iterrows():
            print(f"  {row['Date'].strftime('%Y-%m-%d')}: ${row['Net_Amount']:.2f} - {row['Category']} - {row.get('Notes', 'N/A')}")
    else:
        print("No savings internal transfers found")

if __name__ == "__main__":
    analyze_dca_amounts()
