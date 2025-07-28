#!/usr/bin/env python3
"""
Test comprehensive PDF generation with charts when pandas IS available
This script simulates the enhanced PDF with charts functionality
"""

import os
import sys
import tempfile
from datetime import datetime, timedelta

def test_pdf_with_charts():
    """Create a comprehensive PDF report with charts using reportlab directly"""
    
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        
        # Try to import matplotlib for chart generation
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
        import numpy as np
        
    except ImportError as e:
        print(f"❌ Required libraries not available: {e}")
        return False
    
    # Set up output path
    output_path = os.path.join(tempfile.gettempdir(), "cash_app_enhanced_report_demo.pdf")
    
    print("Creating enhanced PDF report with charts...")
    
    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    # Title
    report_title = "Cash App Report - Enhanced with Charts (Demo)"
    story.append(Paragraph(report_title, title_style))
    story.append(Spacer(1, 12))
    
    # Executive Summary
    summary_text = """
    <b>Executive Summary</b><br/>
    <br/>
    This demo showcases the enhanced PDF generation capabilities of the Cash App Analyzer.<br/>
    When pandas and matplotlib are available, the system generates comprehensive<br/>
    visualizations and detailed analysis.<br/>
    <br/>
    <b>Enhanced Features:</b><br/>
    • Income vs Expenses Bar Chart<br/>
    • Expense Categories Pie Chart<br/>
    • Daily Spending Trend Line<br/>
    • Top Merchants/Categories Analysis<br/>
    • Professional Tables and Formatting<br/>
    • Automatic PDF Generation and Opening<br/>
    """
    
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Create sample charts
    story.append(Paragraph("Sample Visualizations", heading_style))
    
    try:
        # Create a comprehensive chart figure
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Cash App Analysis - Sample Charts', fontsize=16, fontweight='bold')
        
        # Chart 1: Income vs Expenses
        categories = ['Income', 'Expenses']
        amounts = [3250.75, 2185.40]
        colors_list = ['#2E8B57', '#DC143C']  # Sea green for income, crimson for expenses
        
        bars = ax1.bar(categories, amounts, color=colors_list, alpha=0.7)
        ax1.set_title('Income vs Expenses', fontweight='bold')
        ax1.set_ylabel('Amount ($)')
        
        # Add value labels on bars
        for bar, amount in zip(bars, amounts):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + max(amounts) * 0.01,
                    f'${amount:,.0f}', ha='center', va='bottom', fontweight='bold')
        
        # Chart 2: Expense Categories Pie Chart
        expense_categories = ['Shopping', 'Dining', 'Transportation', 'Bills', 'Entertainment']
        expense_amounts = [650, 420, 280, 520, 315]
        
        wedges, texts, autotexts = ax2.pie(expense_amounts, labels=expense_categories, 
                                          autopct='%1.1f%%', startangle=90)
        ax2.set_title('Expense Categories', fontweight='bold')
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        # Chart 3: Daily Spending Trend
        days = np.arange(1, 31)
        daily_spending = np.random.normal(70, 25, 30)  # Random but realistic spending pattern
        daily_spending = np.maximum(daily_spending, 0)  # Ensure non-negative
        
        ax3.plot(days, daily_spending, marker='o', linewidth=2, markersize=4)
        ax3.set_title('Daily Spending Trend', fontweight='bold')
        ax3.set_ylabel('Daily Expenses ($)')
        ax3.set_xlabel('Day of Month')
        
        # Add trend line
        z = np.polyfit(days, daily_spending, 1)
        p = np.poly1d(z)
        ax3.plot(days, p(days), "r--", alpha=0.8, linewidth=1, label='Trend')
        ax3.legend()
        
        # Chart 4: Top Merchants
        merchants = ['Amazon', 'Starbucks', 'Gas Station', 'Grocery Store', 'Restaurant']
        merchant_spending = [280, 125, 95, 180, 145]
        
        ax4.barh(range(len(merchants)), merchant_spending, color='skyblue', alpha=0.7)
        ax4.set_yticks(range(len(merchants)))
        ax4.set_yticklabels(merchants)
        ax4.set_title('Top Merchants', fontweight='bold')
        ax4.set_xlabel('Amount Spent ($)')
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.93)
        
        # Save chart as temporary image
        chart_path = os.path.join(tempfile.gettempdir(), "cash_app_demo_chart.png")
        fig.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        # Add chart to PDF
        story.append(Image(chart_path, width=7.5*inch, height=6*inch))
        
        # Clean up temp file
        if os.path.exists(chart_path):
            os.remove(chart_path)
            
    except Exception as e:
        story.append(Paragraph(f"Chart generation error: {str(e)}", styles['Italic']))
    
    story.append(Spacer(1, 20))
    
    # Technical Details
    story.append(Paragraph("Technical Implementation", heading_style))
    
    tech_text = """
    <b>Implementation Details:</b><br/>
    <br/>
    The Cash App Analyzer now includes:<br/>
    <br/>
    • <b>Dual-mode PDF Generation:</b> Full-featured with pandas/matplotlib, or fallback mode with pure Python<br/>
    • <b>Error-resistant GUI:</b> Handles missing dependencies gracefully<br/>
    • <b>Chart Integration:</b> Professional visualizations embedded in PDF reports<br/>
    • <b>Threading Support:</b> Non-blocking PDF generation with progress updates<br/>
    • <b>Custom Categorization:</b> Smart transaction classification (Energy Auth = Income, Bitcoin = Investment)<br/>
    • <b>Professional Formatting:</b> Tables, colors, and layout optimized for readability<br/>
    <br/>
    The system automatically detects environment capabilities and adapts accordingly.
    """
    
    story.append(Paragraph(tech_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    
    print(f"✅ Enhanced PDF demo created: {output_path}")
    
    try:
        import subprocess
        subprocess.run(['start', output_path], shell=True, check=True)
        print("✅ Enhanced PDF opened successfully")
        return True
    except:
        print("⚠️  Could not automatically open PDF, but file was created")
        return True

def main():
    print("Cash App Enhanced PDF Generation Demo")
    print("=" * 45)
    
    success = test_pdf_with_charts()
    
    print("\n" + "=" * 45)
    if success:
        print("✅ Enhanced PDF generation demo completed!")
        print("\nThis demonstrates the full capabilities when all dependencies are available.")
    else:
        print("❌ Demo failed - missing required libraries")

if __name__ == "__main__":
    main()
