"""
Integration tests for full Cash App Analyzer workflows

These tests focus on end-to-end functionality, testing the complete
workflow from data loading to report generation.
"""

import unittest
import pandas as pd
import sys
import os
import tempfile
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from analyzer.cashapp_analyzer import CashAppAnalyzer
    from fixtures.test_config import TestConfig
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure the src directory is properly structured")


class TestFullWorkflow(unittest.TestCase):
    """Test complete analyzer workflows"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_config = TestConfig()
        self.sample_csv_path = self.test_config.create_sample_csv()
        self.output_dir = tempfile.mkdtemp(prefix='cashapp_integration_test_')
    
    def tearDown(self):
        """Clean up test files"""
        self.test_config.cleanup()
        import shutil
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
    
    def test_complete_analysis_workflow(self):
        """Test the complete analysis from start to finish"""
        analyzer = CashAppAnalyzer(self.sample_csv_path)
        
        # Run complete analysis
        df, fig, report = analyzer.run_analysis()
        
        # Verify results
        self.assertIsNotNone(df)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)
        
        # Verify report is generated
        self.assertIsNotNone(report)
        self.assertIsInstance(report, str)
        self.assertIn('CASH APP MONTHLY TRANSACTION REPORT', report)
        
        # Verify visualization is created
        self.assertIsNotNone(fig)
    
    def test_pdf_generation_workflow(self):
        """Test PDF report generation"""
        analyzer = CashAppAnalyzer(self.sample_csv_path)
        analyzer.load_and_clean_data()
        analyzer.categorize_transactions()
        
        # Generate PDF report
        pdf_path = os.path.join(self.output_dir, 'test_report.pdf')
        
        try:
            result_path = analyzer.generate_pdf_report(pdf_path)
            
            # Verify PDF was created
            self.assertTrue(os.path.exists(result_path))
            self.assertGreater(os.path.getsize(result_path), 0)
            
        except ImportError:
            # Skip test if ReportLab not available
            self.skipTest("ReportLab not available for PDF generation")
    
    def test_visualization_generation_workflow(self):
        """Test visualization generation"""
        analyzer = CashAppAnalyzer(self.sample_csv_path)
        analyzer.load_and_clean_data()
        analyzer.categorize_transactions()
        
        try:
            # Test main dashboard
            fig = analyzer.create_visualizations()
            self.assertIsNotNone(fig)
            
            # Test income visualizations
            income_fig = analyzer.create_income_visualizations()
            self.assertIsNotNone(income_fig)
            
            # Test expense visualizations
            expense_fig = analyzer.create_expense_visualizations()
            self.assertIsNotNone(expense_fig)
            
            # Test cash flow visualizations
            cashflow_fig = analyzer.create_cash_flow_visualizations()
            self.assertIsNotNone(cashflow_fig)
            
        except ImportError:
            # Skip test if matplotlib not available
            self.skipTest("Matplotlib not available for visualization generation")
    
    def test_date_range_analysis_workflow(self):
        """Test analysis with custom date ranges"""
        analyzer = CashAppAnalyzer(self.sample_csv_path)
        
        # Test with specific date range
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        
        df, fig, report = analyzer.run_analysis(
            start_date=start_date,
            end_date=end_date
        )
        
        # Verify results are filtered to date range
        self.assertIsNotNone(df)
        
        # Check that report mentions the date range
        self.assertIn('2024-01', report)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in integration scenarios"""
    
    def test_missing_csv_file(self):
        """Test handling when CSV file doesn't exist"""
        analyzer = CashAppAnalyzer('nonexistent_file.csv')
        
        with self.assertRaises(FileNotFoundError):
            analyzer.run_analysis()
    
    def test_empty_csv_file(self):
        """Test handling of empty CSV files"""
        # Create empty CSV
        empty_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        empty_csv.write('Date,Net Amount,Transaction Type,Notes\n')  # Just headers
        empty_csv.close()
        
        try:
            analyzer = CashAppAnalyzer(empty_csv.name)
            analyzer.load_and_clean_data()
            
            # Should handle empty data gracefully
            self.assertEqual(len(analyzer.df), 0)
            
        finally:
            os.unlink(empty_csv.name)
    
    def test_invalid_date_format(self):
        """Test handling of invalid date formats"""
        # Create CSV with bad dates
        bad_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        bad_csv.write('Date,Net Amount,Transaction Type,Notes\n')
        bad_csv.write('invalid_date,100.00,Deposits,Test\n')
        bad_csv.close()
        
        try:
            analyzer = CashAppAnalyzer(bad_csv.name)
            analyzer.load_and_clean_data()
            
            # Should handle invalid dates by converting to NaT
            self.assertTrue(analyzer.df['Date'].isna().any())
            
        finally:
            os.unlink(bad_csv.name)


if __name__ == '__main__':
    unittest.main()
