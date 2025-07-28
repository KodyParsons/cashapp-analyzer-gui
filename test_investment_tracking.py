#!/usr/bin/env python3
"""
Test script to verify investment tracking and numpy.float64 fixes
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Add the analyzer directory to path
sys.path.append(str(Path(__file__).parent / "cashapp-analyzer-gui" / "src"))

from analyzer.cashapp_analyzer import CashAppAnalyzer

def test_analyzer():
    """Test the analyzer with a sample CSV file"""
    print("Testing Cash App Analyzer...")
    
    # Get available CSV files
    csv_files = [
        "cash_app_transactions.csv",
        "cleaned_cash_app_data.csv", 
        "cash_app_report_1750080626301.csv",
        "export_test.csv"
    ]
    
    test_file = None
    for csv_file in csv_files:
        csv_path = Path(__file__).parent / csv_file
        if csv_path.exists():
            test_file = str(csv_path)
            print(f"Using test file: {csv_file}")
            break
    
    if not test_file:
        print("No CSV files found for testing")
        return False
    
    try:
        # Initialize analyzer
        analyzer = CashAppAnalyzer()
        
        # Load data
        print("Loading CSV data...")
        result = analyzer.load_csv(test_file)
        if not result:
            print("Failed to load CSV file")
            return False
        
        print(f"Loaded {len(analyzer.df)} transactions")
        
        # Test categorization
        print("\nTesting categorization...")
        analyzer.categorize_transactions()
        
        # Check for investment categories
        categories = analyzer.df['Category'].unique()
        investment_categories = [cat for cat in categories if 'Investment' in str(cat)]
        print(f"Investment categories found: {investment_categories}")
        
        # Test cash flow analysis
        print("\nTesting cash flow analysis...")
        try:
            analyzer.analyze_cash_flow()
            print("✓ Cash flow analysis completed successfully")
        except Exception as e:
            print(f"✗ Cash flow analysis failed: {e}")
            return False
        
        # Test comprehensive report generation
        print("\nTesting comprehensive report generation...")
        try:
            output_dir = Path(__file__).parent / "test_output"
            output_dir.mkdir(exist_ok=True)
            
            result = analyzer.generate_comprehensive_report(
                output_path=str(output_dir / "test_report.pdf"),
                include_visualizations=True
            )
            
            if result:
                print("✓ Comprehensive report generated successfully")
            else:
                print("✗ Comprehensive report generation failed")
                return False
            
        except Exception as e:
            print(f"✗ Comprehensive report generation failed: {e}")
            return False
        
        # Test investment summary
        print("\nTesting investment tracking...")
        try:
            investment_data = analyzer.df[
                (analyzer.df['Net_Amount'] < 0) &  # Outflows
                (analyzer.df['Category'].str.contains('Investment', na=False))
            ]
            
            if not investment_data.empty:
                total_investments = abs(investment_data['Net_Amount'].sum())
                print(f"✓ Total investments tracked: ${total_investments:,.2f}")
                
                # Test by category
                investment_by_category = investment_data.groupby('Category')['Net_Amount'].sum().abs()
                print("Investment breakdown:")
                for category, amount in investment_by_category.items():
                    print(f"  - {category}: ${amount:,.2f}")
            else:
                print("No investment transactions found in test data")
        
        except Exception as e:
            print(f"✗ Investment tracking failed: {e}")
            return False
        
        print("\n✓ All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_analyzer()
    sys.exit(0 if success else 1)
