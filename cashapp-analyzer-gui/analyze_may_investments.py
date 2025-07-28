#!/usr/bin/env python3
"""
Detailed analysis of May 2025 investment categorization
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analyzer.cashapp_analyzer import CashAppAnalyzer
import pandas as pd
from datetime import datetime, timedelta

def analyze_may_investments():
    """Analyze May 2025 investment categorization in detail"""
    
    csv_path = r"w:\Analytics\Dept\Kody Parsons\Personal Vault\cashapp_PF\cash_app_transactions.csv"
    analyzer = CashAppAnalyzer(csv_path)
    
    analyzer.load_and_clean_data()
    analyzer.categorize_transactions()
    
    # Filter for May 2025
    may_2025_start = datetime(2025, 5, 1)
    may_2025_end = datetime(2025, 5, 31)
    
    mask = (analyzer.df['Date'] >= may_2025_start) & (analyzer.df['Date'] <= may_2025_end)
    may_data = analyzer.df.loc[mask]
    
    print(f"May 2025 detailed analysis ({len(may_data)} transactions):")
    print("="*60)
    
    # Check all investment categories
    investment_categories = [
        'Investment (Bitcoin)', 'Investment (DCA Savings)', 'Investment (Bitcoin Savings)', 'Investment (Potential DCA)'
    ]
    
    for category in investment_categories:
        cat_data = may_data[may_data['Category'] == category]
        if len(cat_data) > 0:
            total = cat_data['Net_Amount'].sum()
            print(f"\n{category}: ${abs(total):.2f} ({len(cat_data)} transactions)")
            
            # Show individual transactions
            for _, row in cat_data.iterrows():
                description = row.get('Notes', row.get('Description', ''))
                print(f"  {row['Date'].strftime('%Y-%m-%d')}: ${row['Net_Amount']:.2f} - {row['Transaction Type']} - {description}")
    
    # Check if any Bitcoin transactions got misclassified as rent offset
    print(f"\nChecking for Bitcoin transactions in Rent Offset category:")
    rent_offset_data = may_data[may_data['Category'] == 'Rent Offset (Internal)']
    bitcoin_in_rent = rent_offset_data[rent_offset_data['Transaction Type'].str.contains('Bitcoin', na=False)]
    
    if len(bitcoin_in_rent) > 0:
        print("WARNING: Bitcoin transactions found in Rent Offset category!")
        for _, row in bitcoin_in_rent.iterrows():
            print(f"  {row['Date']}: ${row['Net_Amount']:.2f} - {row['Transaction Type']}")
    else:
        print("✓ No Bitcoin transactions misclassified as rent offset")
    
    # Check DCA savings amounts - these might be too high
    print(f"\nDCA Savings transactions detail:")
    dca_data = may_data[may_data['Category'] == 'Investment (DCA Savings)']
    if len(dca_data) > 0:
        amounts = dca_data['Net_Amount'].values
        unique_amounts = sorted(set(amounts))
        print(f"Unique DCA amounts: {[f'${abs(amt):.2f}' for amt in unique_amounts]}")
        
        # Group by amount to see frequency
        amount_counts = dca_data.groupby('Net_Amount').size()
        print("Amount frequency:")
        for amount, count in amount_counts.items():
            print(f"  ${abs(amount):.2f}: {count} transactions")
    
    # Show total cash flow impact
    print(f"\nCash flow impact summary:")
    
    # Internal transfers (should net to zero)
    internal_data = may_data[may_data['Category'].isin(['Internal Transfer', 'Rent Offset (Internal)'])]
    internal_total = internal_data['Net_Amount'].sum()
    print(f"Internal transfers (should be ~$0): ${internal_total:.2f}")
    
    # Investments (actual outflow)
    investment_data = may_data[may_data['Category'].isin(investment_categories)]
    investment_total = investment_data['Net_Amount'].sum()
    print(f"Total investments (actual outflow): ${abs(investment_total):.2f}")
    
    # Regular expenses
    regular_expenses = may_data[
        (may_data['Net_Amount'] < 0) & 
        (~may_data['Category'].isin(investment_categories + ['Internal Transfer', 'Rent Offset (Internal)']))
    ]
    expense_total = regular_expenses['Net_Amount'].sum()
    print(f"Regular expenses: ${abs(expense_total):.2f}")
    
    # Income
    income_data = may_data[may_data['Net_Amount'] > 0]
    income_total = income_data['Net_Amount'].sum()
    print(f"Income: ${income_total:.2f}")
    
    net_cash_flow = income_total + expense_total + investment_total
    print(f"Net cash flow (Income - Expenses - Investments): ${net_cash_flow:.2f}")

if __name__ == "__main__":
    analyze_may_investments()
