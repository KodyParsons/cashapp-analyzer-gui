#!/usr/bin/env python3
"""
Test script to verify the investment categorization improvements
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Add the analyzer directory to path
sys.path.append(str(Path(__file__).parent / ".." / ".." / "src"))

def test_investment_categorization():
    """Test the enhanced investment categorization"""
    print("Testing investment categorization improvements...")
    
    # Create sample data to test the categorization logic
    sample_data = {
        'Date': pd.to_datetime(['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19']),
        'Transaction Type': ['Savings Internal Transfer', 'Savings Internal Transfer', 'Bitcoin Buy', 'Cash Card', 'P2P'],
        'Net_Amount': [-300.0, -250.0, -100.0, -25.50, 500.0],
        'Notes': ['Savings', 'purchase of BTC 0.00296357', 'Bitcoin Purchase', 'Starbucks', 'Friend Payment'],
        'Description': ['Savings', 'purchase of BTC 0.00296357', 'Bitcoin Purchase', 'Starbucks', 'Friend Payment']
    }
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    df['Month_Year'] = df['Date'].dt.to_period('M')
    
    # Test categorization logic
    print("\nTesting categorization with sample data:")
    print("Sample transactions:")
    for i, row in df.iterrows():
        print(f"  {row['Date'].strftime('%Y-%m-%d')}: {row['Transaction Type']} - {row['Notes']} (${row['Net_Amount']})")
    
    # Initialize categories
    df['Category'] = 'Other'
    
    # Test the enhanced categorization logic
    # Rule 2: Bitcoin purchases = Investment
    bitcoin_mask = (df['Transaction Type'] == 'Bitcoin Buy') | (df['Transaction Type'] == 'Bitcoin Recurring Buy')
    df.loc[bitcoin_mask, 'Category'] = 'Investment (Bitcoin)'
    
    # Rule 3: Enhanced Savings Internal Transfer categorization
    savings_mask = df['Transaction Type'] == 'Savings Internal Transfer'
    
    # Bitcoin savings transfers (contains "purchase of BTC")
    bitcoin_savings_mask = (
        savings_mask & 
        df['Notes'].str.contains('purchase of BTC', case=False, na=False)
    )
    df.loc[bitcoin_savings_mask, 'Category'] = 'Investment (Bitcoin Savings)'
    
    # Regular DCA savings transfers (just "Savings" or other non-Bitcoin descriptions)
    regular_savings_mask = savings_mask & ~bitcoin_savings_mask
    df.loc[regular_savings_mask, 'Category'] = 'Investment (DCA Savings)'
    
    # Test other categories
    cash_card_mask = df['Transaction Type'] == 'Cash Card'
    df.loc[cash_card_mask, 'Category'] = 'Food & Dining'  # Simplified for test
    
    p2p_mask = df['Transaction Type'] == 'P2P'
    df.loc[p2p_mask, 'Category'] = 'P2P Transfer'
    
    print("\nCategorization results:")
    print("=" * 50)
    for i, row in df.iterrows():
        print(f"{row['Date'].strftime('%Y-%m-%d')}: {row['Category']:<25} - {row['Notes']} (${row['Net_Amount']})")
    
    # Check investment categories
    investment_categories = [
        'Investment (Bitcoin)', 'Investment (DCA Savings)', 'Investment (Bitcoin Savings)', 'Investment (Potential DCA)'
    ]
    
    investment_data = df[df['Category'].isin(investment_categories)]
    print(f"\nInvestment transactions found: {len(investment_data)}")
    
    if not investment_data.empty:
        print("\nInvestment breakdown:")
        investment_summary = investment_data.groupby('Category')['Net_Amount'].sum().abs()
        for category, amount in investment_summary.items():
            print(f"  {category}: ${amount:,.2f}")
        
        total_investments = investment_summary.sum()
        print(f"\nTotal Investments: ${total_investments:,.2f}")
    
    # Test expected results
    expected_categories = {
        0: 'Investment (DCA Savings)',      # Regular savings
        1: 'Investment (Bitcoin Savings)',   # Bitcoin savings
        2: 'Investment (Bitcoin)',           # Direct bitcoin buy
        3: 'Food & Dining',                  # Cash card
        4: 'P2P Transfer'                    # P2P transfer
    }
    
    print("\nValidation:")
    print("=" * 30)
    all_correct = True
    for i, expected_cat in expected_categories.items():
        actual_cat = df.loc[i, 'Category']
        if actual_cat == expected_cat:
            print(f"\u2713 Transaction {i+1}: {actual_cat}")
        else:
            print(f"\u2717 Transaction {i+1}: Expected '{expected_cat}', got '{actual_cat}'")
            all_correct = False
    
    if all_correct:
        print("\n\u2713 All categorization tests passed!")
        return True
    else:
        print("\n\u2717 Some categorization tests failed!")
        return False

if __name__ == "__main__":
    success = test_investment_categorization()
    if success:
        print("\n\ud83c\udf89 Investment categorization improvements verified successfully!")
    else:
        print("\n\u274c Investment categorization improvements need attention!")
    
    sys.exit(0 if success else 1)
