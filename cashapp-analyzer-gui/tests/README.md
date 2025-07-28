# Cash App Analyzer - Test Suite

This directory contains the organized test suite for the Cash App Analyzer project.

## Test Structure

```
tests/
├── __init__.py
├── run_tests.py          # Main test runner script
├── unit/                 # Unit tests for individual components
│   ├── __init__.py
│   └── test_analyzer.py  # Tests for CashAppAnalyzer class
├── integration/          # Integration tests for full workflows
│   ├── __init__.py
│   └── test_full_workflow.py  # End-to-end workflow tests
├── demos/               # Demo scripts and examples
│   └── __init__.py
└── fixtures/            # Test configuration and sample data
    └── test_config.py   # Test fixtures and configuration
```

## Running Tests

### Run All Tests
```bash
cd tests
python run_tests.py
```

### Run Specific Test Types
```bash
# Run only unit tests
python run_tests.py unit

# Run only integration tests  
python run_tests.py integration
```

### Run Individual Test Files
```bash
# Run specific test file
python -m unittest unit.test_analyzer

# Run with verbose output
python -m unittest unit.test_analyzer -v
```

## Test Categories

### Unit Tests (`unit/`)
- Test individual methods and components in isolation
- Use mocked data and dependencies
- Fast execution
- Focus on edge cases and error handling

### Integration Tests (`integration/`)
- Test complete workflows from start to finish
- Use real sample data
- Test interaction between components
- Verify end-to-end functionality

### Demo Scripts (`demos/`)
- Example usage scripts
- Performance tests
- Visual demonstrations
- Documentation examples

## Test Data

The `fixtures/test_config.py` module provides:
- Sample CSV data for testing
- Configuration constants
- Helper functions for test setup/teardown
- Common test utilities

## Legacy Test Files

The following test files were previously scattered throughout the project and should be reviewed for consolidation:

**Root Directory:**
- `test_viz_fixes.py`
- `test_simple_pdf.py`
- `test_final_fixes.py`
- `test_enhanced_pdf.py`
- `test_pdf_demo.py`
- `test_visualizations.py`
- `test_pdf_comprehensive.py`
- `test_pdf_generation.py`
- `test_income_debug.py`

**GUI Directory:**
- `test_last_month_viz.py`
- `test_large_transactions.py`
- `test_enhanced_app.py`
- `test_analyzer.py`

**Src Directory:**
- `test_pdf_fix.py`
- `test_comprehensive_pdf.py`
- `demo_pdf_fix.py`

## Migration Plan

1. **Review Legacy Tests**: Examine each legacy test file to understand its purpose
2. **Extract Useful Tests**: Move valuable test cases to the appropriate new test files
3. **Consolidate Duplicates**: Combine similar tests and remove redundant ones
4. **Update Imports**: Fix import paths to work with the new structure
5. **Clean Up**: Remove obsolete test files after migration

## Adding New Tests

When adding new tests:

1. **Unit Tests**: Add to `unit/` directory, test individual methods/classes
2. **Integration Tests**: Add to `integration/` directory, test complete workflows
3. **Follow Naming**: Use `test_*.py` naming convention
4. **Use Fixtures**: Leverage `fixtures/test_config.py` for common test data
5. **Document**: Add docstrings explaining what the test validates

## Dependencies

Tests may require additional packages:
- `unittest` (standard library)
- `pandas` (for data manipulation)
- `matplotlib` (for visualization tests)
- `reportlab` (for PDF generation tests)

## Continuous Integration

This test structure is designed to be CI/CD friendly:
- `run_tests.py` returns appropriate exit codes
- Tests are isolated and don't depend on external state
- Sample data is generated programmatically
- Test output is clearly formatted

## Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Always clean up temporary files and resources
3. **Clear Names**: Use descriptive test method names
4. **Documentation**: Include docstrings explaining test purpose
5. **Edge Cases**: Test boundary conditions and error scenarios
6. **Performance**: Keep unit tests fast, integration tests comprehensive
