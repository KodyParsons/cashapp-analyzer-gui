#!/usr/bin/env python3
"""
Test script to check income and cash flow visualization fixes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    # Test with actual data
    csv_files = [
        'cash_app_report_1750080626301.csv',
        'cash_app_transactions.csv',  
        'cleaned_cash_app_data.csv'
    ]
    
    test_csv = None
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            test_csv = csv_file
            break
    
    if test_csv:
        print(f"Testing with CSV file: {test_csv}")
        
        from analyzer.cashapp_analyzer import CashAppAnalyzer
        
        # Create analyzer
        analyzer = CashAppAnalyzer(test_csv)
        analyzer.load_and_clean_data()
        analyzer.categorize_transactions()
        
        print(f"\nTotal transactions loaded: {len(analyzer.df)}")
        print(f"Date range: {analyzer.df['Date'].min()} to {analyzer.df['Date'].max()}")
        print(f"Categories found: {analyzer.df['Category'].value_counts()}")
        
        # Check for income transactions
        income_transactions = analyzer.df[analyzer.df['Net_Amount'] > 0]
        print(f"\nIncome transactions: {len(income_transactions)}")
        if not income_transactions.empty:
            print("Income by category:")
            print(income_transactions.groupby('Category')['Net_Amount'].agg(['count', 'sum']))
        
        # Test income visualization with debugging
        print("\n" + "="*50)
        print("TESTING INCOME VISUALIZATION:")
        print("="*50)
        income_fig = analyzer.create_income_visualizations()
        
        print("\n" + "="*50)
        print("TESTING CASH FLOW VISUALIZATION:")
        print("="*50)
        cash_flow_fig = analyzer.create_cash_flow_visualizations()
        
        print("\n Tests completed!")
        
    else:
        print("No CSV files found for testing")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
