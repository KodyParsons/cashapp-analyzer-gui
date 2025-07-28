#!/usr/bin/env python3
"""
Quick test script for the Cash App Analyzer
"""
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analyzer.cashapp_analyzer import CashAppAnalyzer
from datetime import datetime

def test_analyzer():
    """Test the analyzer with sample data"""
    print("Testing Cash App Analyzer...")
    
    # Test with sample data
    csv_path = "sample_data.csv"
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found")
        return False
    
    try:
        # Create analyzer
        analyzer = CashAppAnalyzer(csv_path)
        
        # Load and process data
        print("Loading and cleaning data...")
        analyzer.load_and_clean_data()
        
        print("Categorizing transactions...")
        analyzer.categorize_transactions()
        
        # Set date range for testing
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 3, 31)
        
        print("Generating monthly summary...")
        monthly_summary = analyzer.generate_monthly_summary(
            start_date=start_date,
            end_date=end_date
        )
        
        print("Generating report...")
        report = analyzer.generate_report(
            start_date=start_date,
            end_date=end_date
        )
        
        print("\n" + "="*50)
        print("ANALYSIS RESULTS:")
        print("="*50)
        print(report)
        
        print("\n" + "="*50)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return False

if __name__ == "__main__":
    success = test_analyzer()
    sys.exit(0 if success else 1)
