#!/usr/bin/env python3
"""
Test PDF generation with charts and fallback capabilities
"""

import os
import sys

# Set up the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'cashapp-analyzer-gui', 'src')
sys.path.insert(0, src_dir)

def test_full_analyzer_pdf():
    """Test PDF generation with full analyzer (pandas-based)"""
    print("Testing full analyzer PDF generation...")
    
    try:
        from analyzer.cashapp_analyzer import CashAppAnalyzer
        
        csv_path = os.path.join(current_dir, 'cash_app_transactions.csv')
        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            return False
            
        analyzer = CashAppAnalyzer(csv_path)
        analyzer.load_and_clean_data()
        analyzer.categorize_transactions()
        
        pdf_path = analyzer.generate_pdf_report()
        
        if os.path.exists(pdf_path):
            print(f"✅ Full analyzer PDF generated successfully: {pdf_path}")
            
            # Try to open the PDF
            try:
                import subprocess
                subprocess.run(['start', pdf_path], shell=True, check=True)
                print("✅ PDF opened successfully")
            except:
                print("⚠️  Could not automatically open PDF, but file was created")
            
            return True
        else:
            print("❌ PDF file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Full analyzer PDF generation failed: {e}")
        return False

def test_fallback_pdf():
    """Test fallback PDF generation (pure Python)"""
    print("\nTesting fallback PDF generation...")
    
    try:
        from analyzer.cashapp_analyzer import CashAppAnalyzer
        
        csv_path = os.path.join(current_dir, 'cash_app_transactions.csv')
        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            return False
            
        pdf_path = CashAppAnalyzer.generate_fallback_pdf_report(csv_path)
        
        if os.path.exists(pdf_path):
            print(f"✅ Fallback PDF generated successfully: {pdf_path}")
            
            # Try to open the PDF
            try:
                import subprocess
                subprocess.run(['start', pdf_path], shell=True, check=True)
                print("✅ Fallback PDF opened successfully")
            except:
                print("⚠️  Could not automatically open fallback PDF, but file was created")
            
            return True
        else:
            print("❌ Fallback PDF file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Fallback PDF generation failed: {e}")
        return False

def main():
    print("Cash App PDF Generation Test")
    print("=" * 40)
    
    # Test full analyzer first
    full_success = test_full_analyzer_pdf()
    
    # Test fallback
    fallback_success = test_fallback_pdf()
    
    print("\n" + "=" * 40)
    print("Test Results:")
    print(f"Full Analyzer PDF: {'✅ PASS' if full_success else '❌ FAIL'}")
    print(f"Fallback PDF: {'✅ PASS' if fallback_success else '❌ FAIL'}")
    
    if full_success or fallback_success:
        print("\n✅ At least one PDF generation method works!")
    else:
        print("\n❌ Both PDF generation methods failed")

if __name__ == "__main__":
    main()
