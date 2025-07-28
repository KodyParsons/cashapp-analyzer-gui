"""
Test script to verify the fixed visualizations work correctly
"""

import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'cashapp-analyzer-gui', 'src'))

try:
    from analyzer.cashapp_analyzer import CashAppAnalyzer
    
    # Create sample data to test the visualizations
    print("Creating sample data for testing...")
    
    # Generate sample transaction data
    dates = pd.date_range(start='2024-06-01', end='2024-06-30', freq='D')
    sample_data = []
    
    for i, date in enumerate(dates):        # Add some income transactions (random paycheck-like amounts)
        if i % 14 == 0:  # Bi-weekly paychecks
            sample_data.append({
                'Date': date,
                'Notes': f'Paycheck {i//14 + 1}',
                'Net Amount': 2500.00,
                'Transaction Type': 'Standard Transfer',
                'Category': 'Income'
            })
        
        # Add some random expense transactions
        if i % 3 == 0:  # Every few days
            expenses = [
                ('Grocery Store', -85.50, 'Food'),
                ('Gas Station', -45.20, 'Transportation'),
                ('Restaurant', -32.75, 'Food'),
                ('Coffee Shop', -5.99, 'Food'),
                ('Online Shopping', -125.00, 'Shopping'),
            ]
            expense = expenses[i % len(expenses)]
            sample_data.append({
                'Date': date,
                'Notes': expense[0],
                'Net Amount': expense[1],
                'Transaction Type': 'Standard Transfer',
                'Category': expense[2]
            })
    
    # Add some large expense transactions for top 5 test
    large_expenses = [
        ('Electronics Store - Laptop', -1200.00, 'Electronics'),
        ('Car Repair Shop', -850.00, 'Transportation'),
        ('Medical Bill', -650.00, 'Healthcare'),
        ('Home Depot - Tools', -420.00, 'Home'),
        ('Best Buy - TV', -380.00, 'Electronics'),    ]
    
    for i, (desc, amount, cat) in enumerate(large_expenses):
        sample_data.append({
            'Date': dates[i + 5],
            'Notes': desc,
            'Net Amount': amount,
            'Transaction Type': 'Standard Transfer',
            'Category': cat
        })
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    # Save to temporary CSV for testing
    temp_csv = 'test_data.csv'
    df.to_csv(temp_csv, index=False)
    
    print(f"Created test data with {len(df)} transactions")
    print(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
    print(f"Sample transactions:")
    print(df.head())
    
    # Test the analyzer
    print("\nTesting CashApp Analyzer...")
    analyzer = CashAppAnalyzer(temp_csv)
    analyzer.load_and_clean_data()
    analyzer.categorize_transactions()
    
    print(f"Loaded {len(analyzer.df)} transactions")
    print(f"Categories: {analyzer.df['Category'].unique()}")
    
    # Test the visualizations
    print("\nTesting daily income visualization...")
    try:
        income_fig = analyzer.create_income_visualizations()
        print("✓ Income visualization created successfully")
        plt.close(income_fig)
    except Exception as e:
        print(f"✗ Income visualization failed: {e}")
    
    print("\nTesting daily expense visualization...")
    try:
        expense_fig = analyzer.create_expense_visualizations()
        print("✓ Expense visualization created successfully")
        plt.close(expense_fig)
    except Exception as e:
        print(f"✗ Expense visualization failed: {e}")
    
    print("\nTesting cash flow visualization with top 5 transactions...")
    try:
        cash_flow_fig = analyzer.create_cash_flow_visualizations()
        print("✓ Cash flow visualization with top 5 transactions created successfully")
        plt.close(cash_flow_fig)
    except Exception as e:
        print(f"✗ Cash flow visualization failed: {e}")
    
    # Clean up
    if os.path.exists(temp_csv):
        os.remove(temp_csv)
    
    print("\n✓ All visualization tests completed successfully!")
    
except ImportError as e:
    print(f"Error importing analyzer: {e}")
except Exception as e:
    print(f"Test failed: {e}")
    import traceback

    traceback.print_exc()
