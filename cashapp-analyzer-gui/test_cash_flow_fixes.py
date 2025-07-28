#!/usr/bin/env python3
"""
Test script to verify cash flow fixes for rent offset and investment categorization
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analyzer.cashapp_analyzer import CashAppAnalyzer
import pandas as pd
from datetime import datetime, timedelta

def test_cash_flow_fixes():
    """Test the cash flow calculation fixes"""
    
    # Path to the CSV file
    csv_path = r"w:\Analytics\Dept\Kody Parsons\Personal Vault\cashapp_PF\cash_app_transactions.csv"
    
    # Initialize analyzer
    analyzer = CashAppAnalyzer(csv_path)
    
    # Load and clean data
    print("Loading and cleaning data...")
    analyzer.load_and_clean_data()
    
    print(f"Total transactions loaded: {len(analyzer.df)}")
    
    # Apply categorization rules
    print("Applying categorization rules...")
    analyzer.categorize_transactions()
    
    # Check categories
    print("\nCategory breakdown:")
    category_counts = analyzer.df['Category'].value_counts()
    print(category_counts)
    
    # Check rent offset categorization
    rent_offset_transactions = analyzer.df[analyzer.df['Category'] == 'Rent Offset (Internal)']
    print(f"\nRent Offset transactions: {len(rent_offset_transactions)}")
    if len(rent_offset_transactions) > 0:
        print("Rent offset amounts:")
        for _, row in rent_offset_transactions.head(10).iterrows():
            print(f"  {row['Date']}: ${row['Net_Amount']:.2f} - {row['Transaction Type']}")
    
    # Check Bitcoin categorization
    bitcoin_investments = analyzer.df[analyzer.df['Category'] == 'Investment (Bitcoin)']
    micro_dca = analyzer.df[analyzer.df['Category'] == 'Micro-DCA (Bitcoin)']
    
    print(f"\nBitcoin Investment transactions (>= $10): {len(bitcoin_investments)}")
    if len(bitcoin_investments) > 0:
        print("Sample Bitcoin investments:")
        for _, row in bitcoin_investments.head(5).iterrows():
            print(f"  {row['Date']}: ${row['Net_Amount']:.2f}")
    
    print(f"\nMicro-DCA transactions (< $10): {len(micro_dca)}")
    if len(micro_dca) > 0:
        print("Sample micro-DCA amounts:")
        for _, row in micro_dca.head(5).iterrows():
            print(f"  {row['Date']}: ${row['Net_Amount']:.2f}")
    
    # Test monthly investment calculations for last month
    last_month = datetime.now().replace(day=1) - timedelta(days=1)
    analyzer.start_date = last_month.replace(day=1)
    analyzer.end_date = last_month
    
    # Filter data for last month
    mask = (analyzer.df['Date'] >= analyzer.start_date) & (analyzer.df['Date'] <= analyzer.end_date)
    monthly_data = analyzer.df.loc[mask]
    
    print(f"\nLast month ({last_month.strftime('%Y-%m')}) analysis:")
    print(f"Total transactions: {len(monthly_data)}")
    
    # Calculate investment amounts
    investment_categories = [
        'Investment (Bitcoin)', 'Investment (DCA Savings)', 'Investment (Bitcoin Savings)', 'Investment (Potential DCA)'
    ]
    
    monthly_investments = monthly_data[
        (monthly_data['Net_Amount'] < 0) &  # Outflows
        (monthly_data['Category'].isin(investment_categories))
    ]
    
    total_investments = monthly_investments['Net_Amount'].sum()
    print(f"Total investments: ${abs(total_investments):.2f}")
    
    # Break down by category
    for category in investment_categories:
        cat_data = monthly_investments[monthly_investments['Category'] == category]
        if len(cat_data) > 0:
            cat_total = cat_data['Net_Amount'].sum()
            print(f"  {category}: ${abs(cat_total):.2f} ({len(cat_data)} transactions)")
    
    # Check micro-DCA amounts (should not be counted as investments)
    monthly_micro_dca = monthly_data[monthly_data['Category'] == 'Micro-DCA (Bitcoin)']
    if len(monthly_micro_dca) > 0:
        micro_total = monthly_micro_dca['Net_Amount'].sum()
        print(f"Micro-DCA (excluded from investments): ${abs(micro_total):.2f} ({len(monthly_micro_dca)} transactions)")
    
    return analyzer

if __name__ == "__main__":
    analyzer = test_cash_flow_fixes()
    print("\nTest completed successfully!")
