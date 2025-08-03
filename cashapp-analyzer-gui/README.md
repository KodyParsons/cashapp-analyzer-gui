# Cash App Transaction Analyzer GUI

A comprehensive desktop application for analyzing Cash App transaction data with an intuitive graphical interface.

## Features

- **Drag-and-Drop CSV Import**: Easily import Cash App transaction CSV files
- **Flexible Date Range Selection**: Choose custom date ranges or use quick presets
- **Advanced Data Analysis**: Automatic transaction categorization and spending analysis
- **Interactive Visualizations**: Charts showing spending trends, category breakdowns, and income vs expenses
- **Comprehensive PDF Reports**: Generate detailed PDF reports with multiple chart types:
  - Overall Transaction Analysis Dashboard (6 comprehensive charts)
  - Income Analysis (detailed income patterns and trends)
  - Expense Analysis (spending breakdown and patterns) 
  - Cash Flow Analysis (net cash flow and financial health indicators)
- **Detailed Reports**: Comprehensive text reports with transaction summaries
- **Export Functionality**: Save reports for future reference
- **Configurable Settings**: Customizable chart sizes, DPI, and report parameters
- **Professional Packaging**: Build standalone EXE files for easy distribution

## New Features
- Improved macOS trackpad scrolling
- Enhanced dashboard layout to prevent overlaps
- Consistent theme and styling
- Calendar widgets for date selection
- Refresh button in dashboard
- Enhanced PDF reports with new sections, styling, and custom options

## Screenshots

The application features three main tabs:
1. **Setup & Analysis**: Import CSV, select dates, and run analysis
2. **Results**: View detailed text reports
3. **Visualizations**: Interactive charts and graphs

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
cd src
python main.py
```

## Usage

### 1. Import CSV File
- Drag and drop your Cash App CSV file onto the import area, or
- Click "Browse File" to select your CSV file manually

### 2. Select Date Range
- Use the date picker to select start and end dates, or
- Use quick select buttons for common ranges (3 months, 6 months, 1 year, all time)

### 3. Generate Report
- Click "Generate Report" to analyze your data
- View results in the "Results" and "Visualizations" tabs

## CSV File Requirements

Your Cash App CSV file should contain the following columns:
- **Date**: Transaction date (various formats supported)
- **Amount/Net Amount**: Transaction amount
- **Description/Notes**: Transaction description for categorization

## Supported Transaction Categories

The analyzer automatically categorizes transactions into:
- Food & Dining
- Shopping  
- Transportation
- Entertainment
- Bills & Utilities
- Transfers
- ATM Withdrawals
- Income
- Other

## Troubleshooting

### Common Issues

1. **"tkinterdnd2 not found" error**: 
   - Install with: `pip install tkinterdnd2`
   - The app will still work without drag-and-drop functionality

2. **CSV parsing errors**: 
   - Ensure your CSV has the required columns
   - Check for special characters or formatting issues

3. **Date parsing issues**: 
   - The analyzer supports multiple date formats
   - Ensure dates are in a recognizable format (YYYY-MM-DD, MM/DD/YYYY, etc.)

### Performance Tips

- For large CSV files (>10,000 transactions), analysis may take a few moments
- The progress bar will show analysis status
- Close other applications to free up memory for better performance

1. Run the application:
   ```
   python src/main.py
   ```

2. Import your CSV file by dragging and dropping it into the application window.

3. Select the desired start and end dates for your report.

4. Generate the report to view your transaction analysis.

## PDF Report Generation

The application now supports comprehensive PDF report generation with multiple visualization types:

### Report Types

1. **Comprehensive Report** (includes all visualizations):
   ```python
   analyzer.generate_comprehensive_pdf_report(
       output_path="full_report.pdf",
       month_offset=1,  # Prior month
       include_all_charts=True
   )
   ```

2. **Quick Report** (main dashboard only):
   ```python
   analyzer.generate_comprehensive_pdf_report(
       output_path="quick_report.pdf",
       month_offset=1,
       include_all_charts=False
   )
   ```

### Included Visualizations

- **Overall Dashboard**: 6-chart comprehensive overview
- **Income Analysis**: Daily income trends and patterns
- **Expense Analysis**: Spending categories and merchant analysis
- **Cash Flow Analysis**: Net cash flow and financial health metrics

### Configuration

Chart sizes, DPI, and other settings can be customized in `src/utils/config.py`.

## Building Standalone EXE

To create a standalone executable:

```bash
# Install PyInstaller (if not already installed)
pip install pyinstaller

# Run the build script
python build_exe.py

# Or use the batch file
build.bat
```

The executable will be created in the `dist/` directory and can be distributed without requiring Python installation.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.