#!/usr/bin/env python3
"""
Test the Top Expenses visualization functionality
"""

import sys
import os
import tempfile
import pandas as pd
from datetime import datetime, timedelta

# Add the src directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from analyzer.cashapp_analyzer import CashAppAnalyzer
    print("✓ Successfully imported CashAppAnalyzer")
except ImportError as e:
    print(f"✗ Failed to import CashAppAnalyzer: {e}")
    sys.exit(1)

def test_top_expenses_visualization():
    """Test the top expenses visualization functionality"""
    print("\n" + "="*60)
    print("TESTING TOP EXPENSES VISUALIZATION")
    print("="*60)
    
    # Create sample data for testing
    sample_data = [
        {'Date': '2024-01-15', 'Description': 'Grocery Store', 'Amount': -75.50, 'Transaction Type': 'Cash Card', 'Category': 'Food & Dining'},
        {'Date': '2024-01-16', 'Description': 'Gas Station', 'Amount': -45.00, 'Transaction Type': 'Cash Card', 'Category': 'Transportation'},
        {'Date': '2024-01-17', 'Description': 'Coffee Shop', 'Amount': -8.50, 'Transaction Type': 'Cash Card', 'Category': 'Food & Dining'},
        {'Date': '2024-01-18', 'Description': 'Apartment Rent', 'Amount': -1200.00, 'Transaction Type': 'Payment', 'Category': 'Housing & Rent'},
        {'Date': '2024-01-19', 'Description': 'Online Shopping', 'Amount': -125.00, 'Transaction Type': 'Cash Card', 'Category': 'Shopping'},
        {'Date': '2024-01-20', 'Description': 'Restaurant', 'Amount': -65.00, 'Transaction Type': 'Cash Card', 'Category': 'Food & Dining'},
        {'Date': '2024-01-21', 'Description': 'Utilities Bill', 'Amount': -85.00, 'Transaction Type': 'Payment', 'Category': 'Utilities'},
        {'Date': '2024-01-22', 'Description': 'Subscription Service', 'Amount': -12.99, 'Transaction Type': 'Payment', 'Category': 'Entertainment'},
        {'Date': '2024-01-23', 'Description': 'Paycheck', 'Amount': 2500.00, 'Transaction Type': 'Payment', 'Category': 'Income'},
        {'Date': '2024-01-24', 'Description': 'Movie Theater', 'Amount': -25.00, 'Transaction Type': 'Cash Card', 'Category': 'Entertainment'},
    ]
    
    # Save to temporary CSV
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        temp_csv_path = temp_file.name
        
        # Write CSV headers and data
        temp_file.write('Date,Description,Amount,Transaction Type\n')
        for row in sample_data:
            temp_file.write(f"{row['Date']},{row['Description']},{row['Amount']},{row['Transaction Type']}\n")
    
    try:
        # Initialize analyzer
        print(f"Creating analyzer with test data: {temp_csv_path}")
        analyzer = CashAppAnalyzer(temp_csv_path)
        
        # Load and categorize data
        print("Loading and cleaning data...")
        analyzer.load_and_clean_data()
        
        print("Categorizing transactions...")
        analyzer.categorize_transactions()
        
        print(f"Total transactions loaded: {len(analyzer.df)}")
        print(f"Categories found: {analyzer.df['Category'].unique()}")
        
        # Test the top expenses visualization
        print("\nTesting create_top_expenses_visualizations method...")
        try:
            fig = analyzer.create_top_expenses_visualizations()
            print("✓ Successfully created top expenses visualization")
            
            # Save the figure for verification
            output_path = os.path.join(os.path.dirname(__file__), 'test_top_expenses_chart.png')
            fig.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"✓ Chart saved to: {output_path}")
            
            # Test with date range
            start_date = datetime(2024, 1, 15)
            end_date = datetime(2024, 1, 25)
            fig_with_dates = analyzer.create_top_expenses_visualizations(start_date=start_date, end_date=end_date)
            print("✓ Successfully created top expenses visualization with date range")
            
            # Clean up matplotlib
            import matplotlib.pyplot as plt
            plt.close('all')
            
        except Exception as e:
            print(f"✗ Error creating top expenses visualization: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Verify expense data (excluding rent)
        expense_data = analyzer.df[
            (analyzer.df['Net_Amount'] < 0) &
            (~analyzer.df['Category'].isin(['Housing & Rent']))
        ]
        
        print(f"\nExpense analysis (excluding rent):")
        print(f"Total expenses (excluding rent): {len(expense_data)} transactions")
        print(f"Top expense categories (excluding rent):")
        expense_categories = expense_data.groupby('Category')['Net_Amount'].sum().abs().sort_values(ascending=False)
        for i, (category, amount) in enumerate(expense_categories.head(5).items(), 1):
            print(f"  {i}. {category}: ${amount:.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_csv_path):
            os.unlink(temp_csv_path)

if __name__ == "__main__":
    success = test_top_expenses_visualization()
    if success:
        print("\n✅ TOP EXPENSES VISUALIZATION TEST PASSED!")
    else:
        print("\n❌ TOP EXPENSES VISUALIZATION TEST FAILED!")
        sys.exit(1)
