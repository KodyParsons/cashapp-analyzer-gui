"""
Test Runner for Cash App Analyzer

This script provides a simple way to run all tests in the test suite.
It can be run directly or used by CI/CD systems.
"""

import sys
import os
import unittest
import logging

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def run_unit_tests():
    """Run all unit tests"""
    loader = unittest.TestLoader()
    suite = loader.discover('unit', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

def run_integration_tests():
    """Run all integration tests"""
    loader = unittest.TestLoader()
    suite = loader.discover('integration', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

def run_all_tests():
    """Run all tests"""
    print("Running Cash App Analyzer Test Suite")
    print("=" * 50)
    
    # Run unit tests
    print("\n🧪 Running Unit Tests...")
    unit_success = run_unit_tests()
    
    # Run integration tests
    print("\n🔗 Running Integration Tests...")
    integration_success = run_integration_tests()
    
    # Summary
    print("\n📊 Test Summary:")
    print("-" * 30)
    print(f"Unit Tests: {'✅ PASSED' if unit_success else '❌ FAILED'}")
    print(f"Integration Tests: {'✅ PASSED' if integration_success else '❌ FAILED'}")
    
    overall_success = unit_success and integration_success
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    return overall_success

if __name__ == '__main__':
    # Change to tests directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run tests based on command line arguments
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type == 'unit':
            success = run_unit_tests()
        elif test_type == 'integration':
            success = run_integration_tests()
        else:
            print(f"Unknown test type: {test_type}")
            print("Usage: python run_tests.py [unit|integration]")
            sys.exit(1)
    else:
        success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
