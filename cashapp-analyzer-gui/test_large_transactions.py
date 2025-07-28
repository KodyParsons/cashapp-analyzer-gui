#!/usr/bin/env python3
"""
Test script for Cash App Analyzer with large transactions and bonus detection
"""

import pandas as pd
from datetime import datetime, timedelta
import random
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analyzer.cashapp_analyzer import CashAppAnalyzer

def create_test_data_with_bonuses():
    """Create test data with large transactions and bonuses"""
    
    # Sample transactions with large payments and bonuses
    transactions = [
        # Regular transactions
        {"Date": "2024-03-01 10:30:00", "Description": "Starbucks Coffee", "Net Amount": "-5.50"},
        {"Date": "2024-03-02 14:20:00", "Description": "Uber Ride", "Net Amount": "-15.75"},
        {"Date": "2024-03-03 09:15:00", "Description": "Amazon Purchase", "Net Amount": "-89.99"},
        {"Date": "2024-03-04 16:45:00", "Description": "Target Shopping", "Net Amount": "-125.60"},
        {"Date": "2024-03-05 11:30:00", "Description": "Shell Gas Station", "Net Amount": "-45.20"},
        
        # Large income/bonus transactions
        {"Date": "2024-03-06 09:00:00", "Description": "Annual Performance Bonus", "Net Amount": "15000.00"},
        {"Date": "2024-03-07 10:00:00", "Description": "Quarterly Sales Commission", "Net Amount": "12500.00"},
        {"Date": "2024-03-08 11:00:00", "Description": "Large Client Payment", "Net Amount": "25000.00"},
        {"Date": "2024-03-09 12:00:00", "Description": "Investment Dividend", "Net Amount": "8500.00"},
        {"Date": "2024-03-10 13:00:00", "Description": "Freelance Project Payment", "Net Amount": "18000.00"},
        
        # More regular transactions
        {"Date": "2024-03-11 08:30:00", "Description": "Netflix Subscription", "Net Amount": "-15.99"},
        {"Date": "2024-03-12 17:20:00", "Description": "Whole Foods Grocery", "Net Amount": "-85.45"},
        {"Date": "2024-03-13 13:15:00", "Description": "Electric Bill Payment", "Net Amount": "-120.00"},
        {"Date": "2024-03-14 19:30:00", "Description": "Movie Theater Tickets", "Net Amount": "-28.50"},
        {"Date": "2024-03-15 20:45:00", "Description": "DoorDash Food Delivery", "Net Amount": "-32.75"},
        
        # Edge case - large payment without bonus keywords
        {"Date": "2024-03-16 14:00:00", "Description": "Real Estate Transaction", "Net Amount": "50000.00"},
        {"Date": "2024-03-17 15:00:00", "Description": "Business Sale Proceeds", "Net Amount": "75000.00"},
        
        # More regular transactions to balance
        {"Date": "2024-03-18 09:45:00", "Description": "CVS Pharmacy", "Net Amount": "-24.99"},
        {"Date": "2024-03-19 11:20:00", "Description": "McDonald's", "Net Amount": "-8.75"},
        {"Date": "2024-03-20 16:30:00", "Description": "Spotify Premium", "Net Amount": "-9.99"},
    ]
    
    # Create DataFrame
    df = pd.DataFrame(transactions)
    
    # Save to CSV for testing
    test_file = "test_large_transactions.csv"
    df.to_csv(test_file, index=False)
    
    return test_file

def test_analyzer_with_bonuses():
    """Test the analyzer with large transactions and bonus detection"""
    
    print("Creating test data with large transactions and bonuses...")
    test_file = create_test_data_with_bonuses()
    
    try:
        print("Testing Cash App Analyzer with large transactions...")
        
        # Initialize analyzer
        analyzer = CashAppAnalyzer(test_file)
        
        print("Loading and cleaning data...")
        analyzer.load_and_clean_data()
        
        print("Categorizing transactions...")
        analyzer.categorize_transactions()
        
        print("Generating monthly summary...")
        analyzer.generate_monthly_summary()
        
        print("Generating report...")
        report = analyzer.generate_report()
        
        print("\n" + "="*50)
        print("ANALYSIS RESULTS:")
        print("="*50)
        print(report)
        print("="*50)
        
        # Test specific bonus categorization
        print("\nBONUS/LARGE PAYMENT CATEGORIZATION TEST:")
        print("-" * 50)
        
        bonus_transactions = analyzer.df[analyzer.df['Category'].isin(['Bonus/Large Payment', 'Large Income/Payment'])]
        
        if not bonus_transactions.empty:
            print(f"Found {len(bonus_transactions)} large payment transactions:")
            for _, row in bonus_transactions.iterrows():
                print(f"  • ${row['Net_Amount']:,.2f} - {row['Description']} → {row['Category']}")
        else:
            print("No large payment transactions found.")
        
        # Category distribution
        print("\nCATEGORY DISTRIBUTION:")
        print("-" * 30)
        category_counts = analyzer.df['Category'].value_counts()
        for category, count in category_counts.items():
            total_amount = analyzer.df[analyzer.df['Category'] == category]['Net_Amount'].sum()
            print(f"{category}: {count} transactions, ${total_amount:,.2f} total")
        
        print("\n" + "="*50)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("="*50)
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"Test file {test_file} cleaned up.")

if __name__ == "__main__":
    test_analyzer_with_bonuses()
