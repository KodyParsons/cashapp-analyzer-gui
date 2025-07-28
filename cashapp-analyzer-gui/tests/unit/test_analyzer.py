"""
Unit tests for CashAppAnalyzer class

These tests focus on individual methods and components of the analyzer,
using mocked data and isolated functionality testing.
"""

import unittest
import pandas as pd
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from analyzer.cashapp_analyzer import CashAppAnalyzer
from fixtures.test_config import TestConfig


class TestCashAppAnalyzer(unittest.TestCase):
    """Test cases for CashAppAnalyzer class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.test_config = TestConfig()
        self.sample_csv_path = self.test_config.create_sample_csv()
        self.analyzer = CashAppAnalyzer(self.sample_csv_path)
    
    def tearDown(self):
        """Clean up after each test method"""
        self.test_config.cleanup()
    
    def test_initialization(self):
        """Test analyzer initialization"""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(self.analyzer.csv_file_path, self.sample_csv_path)
        self.assertIsNone(self.analyzer.df)
        self.assertIsNone(self.analyzer.monthly_data)
    
    def test_load_and_clean_data(self):
        """Test data loading and cleaning"""
        self.analyzer.load_and_clean_data()
        
        # Check that data was loaded
        self.assertIsNotNone(self.analyzer.df)
        self.assertGreater(len(self.analyzer.df), 0)
        
        # Check required columns exist
        required_columns = ['Date', 'Net_Amount', 'Description', 'Month_Year']
        for col in required_columns:
            self.assertIn(col, self.analyzer.df.columns)
        
        # Check data types
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(self.analyzer.df['Date']))
        self.assertTrue(pd.api.types.is_numeric_dtype(self.analyzer.df['Net_Amount']))
    
    def test_categorize_transactions(self):
        """Test transaction categorization"""
        self.analyzer.load_and_clean_data()
        self.analyzer.categorize_transactions()
        
        # Check that categories were assigned
        self.assertIn('Category', self.analyzer.df.columns)
        
        # Check that income is properly categorized
        income_mask = self.analyzer.df['Description'].str.contains('THE ENERGY AUTHO', na=False)
        income_categories = self.analyzer.df.loc[income_mask, 'Category'].unique()
        self.assertIn('Income', income_categories)
        
        # Check that expenses are categorized
        expense_categories = self.analyzer.df[self.analyzer.df['Net_Amount'] < 0]['Category'].unique()
        self.assertTrue(any(cat != 'Other' for cat in expense_categories))
    
    def test_merchant_categorization(self):
        """Test specific merchant categorization logic"""
        # Test food categorization
        self.assertEqual(
            self.analyzer._categorize_cash_card_expense('CHIPOTLE MEXICAN GRILL'),
            'Food & Dining'
        )
        
        # Test entertainment categorization
        self.assertEqual(
            self.analyzer._categorize_cash_card_expense('NETFLIX.COM'),
            'Entertainment & Media'
        )
        
        # Test unknown merchant
        self.assertEqual(
            self.analyzer._categorize_cash_card_expense('UNKNOWN MERCHANT'),
            'Other Expenses'
        )
    
    def test_date_range_filtering(self):
        """Test setting custom date ranges"""
        self.analyzer.load_and_clean_data()
        
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        
        self.analyzer.set_date_range(start_date, end_date)
        
        self.assertEqual(self.analyzer.start_date, start_date)
        self.assertEqual(self.analyzer.end_date, end_date)
    
    def test_monthly_summary_generation(self):
        """Test monthly summary generation"""
        self.analyzer.load_and_clean_data()
        self.analyzer.categorize_transactions()
        
        # Generate summary for a specific period
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 2, 28)
        
        summary = self.analyzer.generate_monthly_summary(
            start_date=start_date, 
            end_date=end_date
        )
        
        self.assertIsNotNone(summary)
        self.assertIn('Total_Amount', summary.columns)
        self.assertIn('Transaction_Count', summary.columns)
    
    def test_empty_data_handling(self):
        """Test handling of empty datasets"""
        # Create analyzer with non-existent file
        empty_analyzer = CashAppAnalyzer()
        
        with self.assertRaises(ValueError):
            empty_analyzer.load_and_clean_data()


class TestDataValidation(unittest.TestCase):
    """Test data validation and edge cases"""
    
    def test_invalid_csv_path(self):
        """Test handling of invalid CSV paths"""
        analyzer = CashAppAnalyzer('nonexistent_file.csv')
        
        with self.assertRaises(FileNotFoundError):
            analyzer.load_and_clean_data()
    
    def test_malformed_dates(self):
        """Test handling of malformed date data"""
        # This would require creating a CSV with bad dates
        # Left as placeholder for future implementation
        pass
    
    def test_missing_amount_column(self):
        """Test handling of missing amount columns"""
        # This would require creating a CSV without amount columns
        # Left as placeholder for future implementation
        pass


if __name__ == '__main__':
    unittest.main()
