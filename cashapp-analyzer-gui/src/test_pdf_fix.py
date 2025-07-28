#!/usr/bin/env python3
"""
Test script to verify the PDF generation fix
"""
import os
import sys

def test_pdf_generation():
    """Test that PDF generation works without falling back unnecessarily"""
    print("Testing PDF generation fix...")
    
    # Import the analyzer
    try:
        from analyzer.cashapp_analyzer import CashAppAnalyzer
        print("✅ CashAppAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import CashAppAnalyzer: {e}")
        return False
    
    # Check if sample data exists
    sample_data_path = "../sample_data.csv"
    if not os.path.exists(sample_data_path):
        print(f"❌ Sample data not found at {sample_data_path}")
        return False
    
    print(f"✅ Sample data found: {sample_data_path}")
    
    # Test the analyzer
    try:
        analyzer = CashAppAnalyzer(sample_data_path)
        analyzer.load_and_clean_data()
        analyzer.categorize_transactions()
        print("✅ Data loaded and categorized successfully")
          # Test comprehensive PDF generation
        print("Testing comprehensive PDF generation...")
        pdf_path = analyzer.generate_comprehensive_pdf_report(
            output_path="test_fix_comprehensive.pdf",
            month_offset=17,  # January 2024 (17 months back from June 2025)
            include_all_charts=True
        )
        print(f"✅ Comprehensive PDF generated: {pdf_path}")
        
        # Test that the original method also works
        print("Testing original PDF generation...")
        original_pdf_path = analyzer.generate_pdf_report(
            output_path="test_fix_original.pdf",
            month_offset=17  # January 2024
        )
        print(f"✅ Original PDF generated: {original_pdf_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_generation()
    if success:
        print("\n🎉 All PDF generation tests passed!")
    else:
        print("\n💥 PDF generation tests failed!")
        sys.exit(1)
