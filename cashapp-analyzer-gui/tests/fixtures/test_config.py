"""
Test Configuration and Fixtures for Cash App Analyzer Tests

This module provides common test fixtures, sample data, and configuration
for use across all test modules.
"""

import os
import tempfile
import pandas as pd
from datetime import datetime, timedelta


class TestConfig:
    """Configuration for tests"""
    
    # Test data paths
    SAMPLE_CSV_PATH = os.path.join(os.path.dirname(__file__), 'sample_data.csv')
    
    # Test output directory
    TEST_OUTPUT_DIR = tempfile.mkdtemp(prefix='cashapp_test_')
    
    @classmethod
    def get_sample_data(cls):
        """Generate sample transaction data for testing"""
        
        # Create sample transaction data
        sample_data = {
            'Date': [
                '2024-01-15 10:30:00',
                '2024-01-20 14:15:00', 
                '2024-01-25 16:45:00',
                '2024-02-01 09:20:00',
                '2024-02-10 11:30:00',
                '2024-02-15 13:45:00'
            ],
            'Net Amount': [3000.00, -50.25, -1200.00, 3000.00, -75.50, -25.00],
            'Transaction Type': [
                'Deposits',
                'Cash Card', 
                'Savings Internal Transfer',
                'Deposits',
                'Cash Card',
                'Cash Card'
            ],
            'Notes': [
                'THE ENERGY AUTHO DIRECT DEP',
                'CHIPOTLE MEXICAN GRILL',
                'Savings Transfer',
                'THE ENERGY AUTHO DIRECT DEP', 
                'STARBUCKS COFFEE',
                'MCDONALDS'
            ]
        }
        
        return pd.DataFrame(sample_data)
    
    @classmethod
    def create_sample_csv(cls):
        """Create a sample CSV file for testing"""
        df = cls.get_sample_data()
        df.to_csv(cls.SAMPLE_CSV_PATH, index=False)
        return cls.SAMPLE_CSV_PATH
    
    @classmethod
    def cleanup(cls):
        """Clean up test files"""
        import shutil
        if os.path.exists(cls.TEST_OUTPUT_DIR):
            shutil.rmtree(cls.TEST_OUTPUT_DIR)
        if os.path.exists(cls.SAMPLE_CSV_PATH):
            os.remove(cls.SAMPLE_CSV_PATH)


def pytest_configure(config):
    """Configure pytest for the test suite"""
    # Create sample data when tests start
    TestConfig.create_sample_csv()


def pytest_unconfigure(config):
    """Cleanup after tests complete"""
    TestConfig.cleanup()
