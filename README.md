# Cash App Transaction Analyzer

A comprehensive Python application for analyzing Cash App transaction data with advanced visualizations, categorization, and reporting features.

## Features

### 🎯 Core Functionality
- **Automated Transaction Categorization**: Smart categorization of transactions based on merchant names and patterns
- **Investment Tracking**: Separate tracking for Bitcoin purchases, DCA savings, and other investments
- **Multi-Tab GUI Interface**: User-friendly interface with dedicated tabs for different analysis types
- **PDF Report Generation**: Professional PDF reports with charts and detailed analysis
- **Date Range Filtering**: Analyze specific time periods

### 📊 Visualization Tabs
1. **Setup & Analysis**: Import CSV files and configure analysis parameters
2. **Summary Report**: Overview with key metrics and transaction summary
3. **Income Analysis**: Detailed income tracking and visualization
4. **Expense Analysis**: Comprehensive expense breakdown and trends
5. **Cash Flow Analysis**: Net cash flow tracking with investment separation
6. **Top Expenses**: Top 5 expenses analysis (excluding rent) with multiple chart types
7. **Transaction Data**: Searchable and filterable transaction viewer

### 💡 Advanced Features
- **Investment Categories**: 
  - Bitcoin purchases
  - DCA (Dollar Cost Averaging) savings
  - Bitcoin savings from DCA
  - Potential DCA investments
- **Smart Exclusions**: Automatically excludes internal transfers and rent from expense analysis
- **Interactive Charts**: Zoom, pan, and export capabilities
- **Data Export**: Export filtered transaction data
- **Threading Support**: Non-blocking GUI operations

## Installation

### Prerequisites
- Python 3.8+
- Required packages (install via conda or pip):

```bash
# Using conda (recommended)
conda install pandas matplotlib tkinter reportlab numpy

# Using pip
pip install pandas matplotlib reportlab numpy
```

### Setup
1. Clone or download this repository
2. Navigate to the project directory
3. Install dependencies
4. Run the application:

```bash
cd cashapp-analyzer-gui
python src/main.py
```

## Usage

### 1. Data Import
1. Export your Cash App transaction data as CSV
2. Open the application
3. Go to "Setup & Analysis" tab
4. Click "Browse" to select your CSV file
5. Configure date range (optional)
6. Click "Run Analysis"

### 2. Viewing Results
- Navigate through different tabs to view various analyses
- Use the interactive chart controls to zoom and explore
- Export data or save charts as needed

### 3. PDF Reports
- Generate comprehensive PDF reports from the Setup tab
- Choose between quick reports or comprehensive reports with all charts
- Reports include financial summaries, category breakdowns, and visualizations

## Project Structure

```
cashapp_PF/
├── cashapp-analyzer-gui/
│   ├── src/
│   │   ├── analyzer/
│   │   │   ├── cashapp_analyzer.py    # Main analysis engine
│   │   │   └── data_processor.py      # Data processing utilities
│   │   ├── core/
│   │   │   └── pdf_generator.py       # Enhanced PDF generation
│   │   ├── gui/
│   │   │   ├── main_window.py         # Main GUI application
│   │   │   └── components/            # GUI components
│   │   ├── utils/
│   │   │   ├── config.py              # Configuration management
│   │   │   ├── helpers.py             # Utility functions
│   │   │   └── logger.py              # Logging utilities
│   │   └── main.py                    # Application entry point
│   ├── tests/                         # Test suite
│   ├── requirements.txt               # Dependencies
│   └── README.md                      # GUI-specific documentation
├── test_*.py                          # Test scripts
├── *.md                              # Documentation files
└── README.md                         # This file
```

## Key Enhancements

### Investment Tracking
- **Enhanced Categorization**: Distinguishes between different types of investments
- **Separate Reporting**: Investment totals are tracked separately from regular expenses
- **DCA Analysis**: Special handling for Dollar Cost Averaging transactions

### Top Expenses Analysis
- **Rent Exclusion**: Automatically excludes housing/rent from top expenses
- **4-Chart Dashboard**: 
  - Top 5 expense categories
  - Top 5 individual transactions
  - Monthly trend of top category
  - Expense distribution pie chart

### Technical Improvements
- **Error Handling**: Robust error handling with graceful fallbacks
- **Threading**: Non-blocking operations for better user experience
- **Memory Management**: Proper cleanup of matplotlib figures
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Testing

Run the test suite to verify functionality:

```bash
# Test core analyzer functionality
python test_investment_categories.py
python test_investment_tracking.py

# Test GUI functionality
python test_gui_top_expenses.py

# Test visualizations
python test_top_expenses_viz.py

# Integration tests
python test_top_expenses_integration.py
```

## Configuration

### CSV Format
The application expects CSV files with these columns:
- `Date`
- `Description` or `Notes`
- `Amount` (negative for expenses, positive for income)
- `Transaction Type` (optional)

### Customization
- Modify category rules in `cashapp_analyzer.py`
- Adjust visualization styles in the respective visualization methods
- Configure exclusion categories as needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is for personal use. Please respect Cash App's terms of service when using this tool.

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all dependencies are installed
2. **CSV Format**: Check that your CSV file matches the expected format
3. **Display Issues**: Try updating matplotlib or switching to a different backend
4. **Memory Issues**: Close unused charts and restart the application

### Support
- Check the test files for usage examples
- Review the documentation files (*.md) for detailed information
- Examine the code comments for implementation details

## Version History

- **v1.0**: Initial release with basic analysis
- **v2.0**: Added GUI interface and multiple visualization tabs
- **v3.0**: Enhanced investment tracking and categorization
- **v4.0**: Added Top Expenses analysis and comprehensive PDF reports
- **Current**: Full-featured application with advanced analytics

---

**Note**: This tool is designed for personal financial analysis. Always verify results against your official Cash App statements.
