"""Test script for the new comprehensive PDF generation"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzer.cashapp_analyzer import CashAppAnalyzer

def test_comprehensive_pdf():
    """Test the new comprehensive PDF generation"""
    print("Testing comprehensive PDF generation...")
      # You'll need to update this path to your actual CSV file
    csv_file = "sample_data.csv"  # Using the sample data file
    
    if not os.path.exists(csv_file):
        # Try alternative paths
        alternative_paths = [
            "../sample_data.csv",
            "../../cash_app_transactions.csv",
            "../cash_app_transactions.csv"
        ]
        
        for alt_path in alternative_paths:
            if os.path.exists(alt_path):
                csv_file = alt_path
                break
        else:
            print(f"CSV file not found: {csv_file}")
            print("Tried alternative paths:", alternative_paths)
            print("Please update the csv_file path in this script")
            return
    
    try:
        # Initialize analyzer
        analyzer = CashAppAnalyzer(csv_file)
        
        # Load and process data
        print("Loading and cleaning data...")
        analyzer.load_and_clean_data()
        
        print("Categorizing transactions...")
        analyzer.categorize_transactions()
          # Generate comprehensive PDF with all charts
        print("Generating comprehensive PDF report...")
        pdf_path = analyzer.generate_comprehensive_pdf_report(
            output_path="test_comprehensive_report.pdf",
            month_offset=17,  # Go back to January 2024 for sample data
            include_all_charts=True
        )
        
        print(f"✅ Comprehensive PDF generated successfully: {pdf_path}")
        
        # Generate quick PDF (just main dashboard)
        print("Generating quick PDF report...")
        quick_pdf_path = analyzer.generate_comprehensive_pdf_report(
            output_path="test_quick_report.pdf",
            month_offset=17,  # Same month for consistency
            include_all_charts=False
        )
        
        print(f"✅ Quick PDF generated successfully: {quick_pdf_path}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_comprehensive_pdf()
