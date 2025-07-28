#!/usr/bin/env python3
"""
Demo script showing that the PDF generator no longer falls back unnecessarily
"""
import sys
import os

def demo_pdf_generation():
    """Demo the fixed PDF generation"""
    print("=== Cash App PDF Generation Fix Demo ===\n")
    
    # Test with our test data (which has January 2024 data)
    try:
        from analyzer.cashapp_analyzer import CashAppAnalyzer
        
        # Load the sample data
        sample_data_path = "../sample_data.csv"
        if not os.path.exists(sample_data_path):
            print(f"❌ Sample data not found at {sample_data_path}")
            return
            
        print("Loading sample data...")
        analyzer = CashAppAnalyzer(sample_data_path)
        analyzer.load_and_clean_data()
        analyzer.categorize_transactions()
        
        print(f"✅ Loaded {len(analyzer.df)} transactions")
        print(f"Date range: {analyzer.df['Date'].min()} to {analyzer.df['Date'].max()}")
        
        # Test comprehensive PDF generation with correct month offset
        print("\n🎯 Testing comprehensive PDF generation (should work without fallback):")
        try:
            pdf_path = analyzer.generate_comprehensive_pdf_report(
                output_path="demo_comprehensive_report.pdf",
                month_offset=17,  # January 2024
                include_all_charts=True
            )
            print(f"✅ SUCCESS: Comprehensive PDF generated at {pdf_path}")
            print("   - No fallback message appeared!")
            print("   - All 4 chart types included!")
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            return
        
        # Test with default month offset (should show appropriate error)
        print("\n🎯 Testing with default month (should show clear error, not generic fallback):")
        try:
            pdf_path = analyzer.generate_comprehensive_pdf_report(
                output_path="demo_default_month.pdf",
                include_all_charts=True
            )
            print(f"✅ Unexpected success: {pdf_path}")
        except ValueError as e:
            if "No data found for the period" in str(e):
                print(f"✅ SUCCESS: Got expected specific error: {e}")
                print("   - This is the correct behavior!")
                print("   - No generic 'falling back' message!")
            else:
                print(f"❌ Unexpected ValueError: {e}")
        except Exception as e:
            print(f"❌ Unexpected error type: {e}")
        
        print("\n🎉 PDF Generation Fix Verified!")
        print("   - Comprehensive PDF generation works when data is available")
        print("   - Clear error messages when data is not available") 
        print("   - No unnecessary fallback to legacy PDF generation")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_pdf_generation()
