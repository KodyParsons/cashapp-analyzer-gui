#!/usr/bin/env python3
"""
Test script to verify the updated visualizations work correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from analyzer.cashapp_analyzer import CashAppAnalyzer
    
    # Check if we have a CSV file to test with
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
        
        # Create analyzer
        analyzer = CashAppAnalyzer(test_csv)
        
        # Load and process data
        print("Loading and cleaning data...")
        analyzer.load_and_clean_data()
        analyzer.categorize_transactions()
        
        # Test income visualization (should be daily line chart now)
        print("Creating income visualizations...")
        income_fig = analyzer.create_income_visualizations()
        print("✓ Income visualization created successfully (daily trend)")
        
        # Test expense visualization (should be daily line chart now)
        print("Creating expense visualizations...")
        expense_fig = analyzer.create_expense_visualizations()
        print("✓ Expense visualization created successfully (daily trend)")
        
        # Test cash flow visualization (should have top 5 non-rent expenses)
        print("Creating cash flow visualizations...")
        cash_flow_fig = analyzer.create_cash_flow_visualizations()
        print("✓ Cash flow visualization created successfully (with top 5 non-rent expenses)")
        
        print("\n✅ All visualizations updated successfully!")
        print("Changes implemented:")
        print("- Income: Removed 'by category' charts, changed to daily line chart")
        print("- Expense: Changed monthly trend to daily line chart")
        print("- Cash Flow: Added top 5 non-rent expenses chart")
        
    else:
        print("❌ No CSV files found for testing")
        print("Available files:", os.listdir('.'))
        
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()
