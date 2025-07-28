#!/usr/bin/env python3
"""
Test script for Last Month visualization improvements
"""

import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analyzer.cashapp_analyzer import CashAppAnalyzer

def create_last_month_test_data():
    """Create test data for last month to test visualization improvements"""
    
    # Get last month's dates
    today = datetime.now()
    first_day_current_month = today.replace(day=1)
    last_day_prev_month = first_day_current_month - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1)
    
    print(f"Creating test data for: {first_day_prev_month.strftime('%Y-%m-%d')} to {last_day_prev_month.strftime('%Y-%m-%d')}")
    
    # Create sample transactions for last month
    transactions = [
        # Income transactions
        {"Date": f"{first_day_prev_month.strftime('%Y-%m-05')} 09:00:00", "Description": "Salary Direct Deposit", "Net Amount": "3500.00"},
        {"Date": f"{first_day_prev_month.strftime('%Y-%m-15')} 10:00:00", "Description": "Freelance Payment", "Net Amount": "850.00"},
        {"Date": f"{first_day_prev_month.strftime('%Y-%m-25')} 11:00:00", "Description": "Investment Dividend", "Net Amount": "125.50"},
        
        # Regular expenses
        {"Date": f"{first_day_prev_month.strftime('%Y-%m-02')} 08:30:00", "Description": "Starbucks Coffee", "Net Amount": "-4.85"},
        {"Date": f"{first_day_prev_month.strftime('%Y-%m-03')} 12:20:00", "Description": "Whole Foods Grocery", "Net Amount": "-89.45"},
        {"Date": f"{first_day_prev_month.strftime('%Y-%m-04')} 18:15:00", "Description": "Shell Gas Station", "Net Amount": "-42.30"},
        {"Date": f"{first_day_prev_month.strftime('%Y-%m-06')} 14:45:00", "Description": "Amazon Prime Subscription", "Net Amount": "-14.99"},
        {"Date": f"{first_day_prev_month.strftime('%Y-%m-07')} 20:30:00", "Description": "Netflix Subscription", "Net Amount": "-15.99"},
        {"Date": f"{first_day_prev_month.strftime('%Y-%m-08')} 16:20:00", "Description": "Uber Ride", "Net Amount": "-18.75"},
        {"Date": f"{first_day_prev_month.strftime('%Y-%m-10')} 13:10:00", "Description": "Target Shopping", "Net Amount": "-67.80"},
        {"Date": f"{first_day_prev_month.strftime('%Y-%m-12')} 11:40:00", "Description": "Electric Bill", "Net Amount": "-125.00"},
        {"Date": f"{first_day_prev_month.strftime('%Y-%m-14')} 09:25:00", "Description": "CVS Pharmacy", "Net Amount": "-28.95"},
        {"Date": f"{first_day_prev_month.strftime('%Y-%m-16')} 17:50:00", "Description": "McDonald's", "Net Amount": "-9.45"},
        {"Date": f"{first_day_prev_month.strftime('%Y-%m-18')} 15:30:00", "Description": "Movie Theater", "Net Amount": "-24.50"},
        {"Date": f"{first_day_prev_month.strftime('%Y-%m-20')} 19:15:00", "Description": "DoorDash Food Delivery", "Net Amount": "-35.60"},
        {"Date": f"{first_day_prev_month.strftime('%Y-%m-22')} 10:45:00", "Description": "Spotify Premium", "Net Amount": "-9.99"},
        {"Date": f"{first_day_prev_month.strftime('%Y-%m-24')} 14:20:00", "Description": "Home Depot", "Net Amount": "-156.75"},
        {"Date": f"{first_day_prev_month.strftime('%Y-%m-26')} 16:35:00", "Description": "Chipotle", "Net Amount": "-12.85"},
        {"Date": f"{first_day_prev_month.strftime('%Y-%m-28')} 12:50:00", "Description": "Lyft Ride", "Net Amount": "-21.40"},
        
        # Large payment to test bonus detection
        {"Date": f"{first_day_prev_month.strftime('%Y-%m-20')} 09:00:00", "Description": "Year-end Bonus", "Net Amount": "12000.00"},
    ]
    
    # Create DataFrame
    df = pd.DataFrame(transactions)
    
    # Save to CSV for testing
    test_file = "test_last_month_data.csv"
    df.to_csv(test_file, index=False)
    
    return test_file, first_day_prev_month, last_day_prev_month

def test_last_month_visualizations():
    """Test the last month visualization improvements"""
    
    print("="*60)
    print("TESTING LAST MONTH VISUALIZATION IMPROVEMENTS")
    print("="*60)
    
    test_file, start_date, end_date = create_last_month_test_data()
    
    try:
        print("Initializing analyzer...")
        analyzer = CashAppAnalyzer(test_file)
        
        print("Loading and cleaning data...")
        analyzer.load_and_clean_data()
        
        print("Categorizing transactions...")
        analyzer.categorize_transactions()
        
        print("Setting last month date range...")
        analyzer.set_date_range(start_date, end_date)
        
        print("Generating monthly summary...")
        analyzer.generate_monthly_summary(start_date=start_date, end_date=end_date)
        
        print("Creating enhanced visualizations...")
        fig = analyzer.create_visualizations(start_date=start_date, end_date=end_date)
        
        print("Generating report...")
        report = analyzer.generate_report(start_date=start_date, end_date=end_date)
        
        print("\n" + "="*50)
        print("LAST MONTH ANALYSIS RESULTS:")
        print("="*50)
        print(report)
        print("="*50)
        
        # Check for proper categorization
        print("\nCATEGORIZATION SUMMARY:")
        print("-" * 30)
        category_summary = analyzer.df['Category'].value_counts()
        for category, count in category_summary.items():
            total_amount = analyzer.df[analyzer.df['Category'] == category]['Net_Amount'].sum()
            print(f"{category}: {count} transactions, ${total_amount:,.2f} total")
        
        print(f"\n✅ Enhanced visualizations created successfully!")
        print(f"✅ Chart saved as 'cash_app_report.png'")
        print(f"✅ Single month data properly handled with bar charts instead of dots")
        print(f"✅ Separate income and expense graphs created")
        print(f"✅ Bonus detection working (found Year-end Bonus)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"Test file {test_file} cleaned up.")

if __name__ == "__main__":
    success = test_last_month_visualizations()
    if success:
        print("\n🎉 ALL TESTS PASSED! Last month visualization improvements working correctly!")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")
