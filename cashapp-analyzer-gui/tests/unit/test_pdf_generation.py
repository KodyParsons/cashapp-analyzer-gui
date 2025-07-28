#!/usr/bin/env python3
"""
Test script for PDF generation functionality
This tests the PDF report generation without the GUI
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from analyzer.cashapp_analyzer import CashAppAnalyzer

def test_pdf_generation():
    """Test the PDF generation functionality"""
    
    print("="*60)
    print("TESTING PDF GENERATION")
    print("="*60)
    
    # Path to the CSV file
    csv_path = "cash_app_transactions.csv"
    
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found at {csv_path}")
        return
    
    try:
        print("1. Creating analyzer...")
        analyzer = CashAppAnalyzer(csv_path)
        
        print("2. Loading and cleaning data...")
        analyzer.load_and_clean_data()
        
        print("3. Categorizing transactions...")
        analyzer.categorize_transactions()
        
        print("4. Generating PDF report for prior month...")
        pdf_path = analyzer.generate_pdf_report()
        
        print(f"SUCCESS! PDF report generated at: {pdf_path}")
        
        # Check if file exists
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path) / 1024  # Size in KB
            print(f"PDF file size: {file_size:.1f} KB")
        else:
            print("ERROR: PDF file was not created!")
        
        return pdf_path
        
    except Exception as e:
        print(f"ERROR: PDF generation failed - {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    pdf_path = test_pdf_generation()
    
    if pdf_path:
        print("\n" + "="*60)
        print("PDF GENERATION TEST COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"You can find your PDF report at: {pdf_path}")
        
        # Try to open the PDF
        try:
            os.startfile(pdf_path)
            print("Opening PDF report...")
        except:
            print("Note: Please open the PDF manually.")
    else:
        print("\n" + "="*60)
        print("PDF GENERATION TEST FAILED!")
        print("="*60)
