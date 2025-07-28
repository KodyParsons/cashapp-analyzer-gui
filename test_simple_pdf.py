"""
Simple PDF generation test using minimal dependencies
Tests the PDF generation with basic data processing
"""

import csv
from datetime import datetime, timedelta
import os
import tempfile

# PDF generation imports
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    print("ReportLab successfully imported!")
except ImportError as e:
    print(f"ReportLab import failed: {e}")
    exit(1)

def process_csv_data(csv_path):
    """Process CSV data without pandas"""
    transactions = []
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Clean and process the row
            try:
                # Parse date (remove timezone and parse ISO format)
                date_str = row['Date'].strip()
                # Remove timezone abbreviation (EDT, EST)
                date_str = date_str.split(' ')[0] + ' ' + date_str.split(' ')[1]  # Just date and time
                date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                
                # Parse amount
                net_amount_str = row['Net Amount'].replace('$', '').replace(',', '')
                net_amount = float(net_amount_str)
                
                # Categorize based on our rules
                category = categorize_transaction(row)
                
                transactions.append({
                    'date': date_obj,
                    'amount': net_amount,
                    'notes': row.get('Notes', ''),
                    'transaction_type': row.get('Transaction Type', ''),
                    'category': category,
                    'merchant': row.get('Name of sender/receiver', '')
                })
            except Exception as e:
                print(f"Error processing row: {e}")
                continue
    
    return transactions

def categorize_transaction(row):
    """Apply our custom categorization rules"""
    transaction_type = row.get('Transaction Type', '')
    notes = row.get('Notes', '').upper()
    
    # Rule 1: Energy Auth transactions = Income
    if 'THE ENERGY AUTHO DIRECT DEP' in notes:
        return 'Income'
    
    # Rule 2: Bitcoin purchases = Investment/Savings
    if transaction_type in ['Bitcoin Buy', 'Bitcoin Recurring Buy']:
        return 'Investment (Bitcoin)'
    
    # Rule 3: Savings Internal Transfer = Money Movement
    if transaction_type == 'Savings Internal Transfer':
        return 'Savings Transfer'
    
    # Rule 4: Deposits = Money Movement
    if transaction_type == 'Deposits':
        return 'Deposits'
    
    # Rule 5: P2P = Expenses
    if transaction_type == 'P2P':
        return 'P2P Expenses'
    
    # Rule 6: Cash Card transactions - categorize by merchant
    if transaction_type == 'Cash Card':
        return categorize_merchant(notes)
    
    return 'Other'

def categorize_merchant(notes):
    """Categorize cash card expenses by merchant"""
    notes_upper = notes.upper()
    
    # Food & Dining
    food_keywords = ['CHIPOTLE', 'MCDONALD', 'STARBUCKS', 'WAFFLE HOUSE', 'WHATABURGER']
    if any(keyword in notes_upper for keyword in food_keywords):
        return 'Food & Dining'
    
    # Entertainment
    entertainment_keywords = ['NETFLIX', 'SPOTIFY', 'YOUTUBE']
    if any(keyword in notes_upper for keyword in entertainment_keywords):
        return 'Entertainment & Media'
    
    # Default
    return 'Other Expenses'

def generate_simple_pdf_report(transactions, output_path=None):
    """Generate a PDF report from transaction data"""
    
    # Calculate date range for prior month
    today = datetime.now()
    first_day_current_month = today.replace(day=1)
    last_day_prior_month = first_day_current_month - timedelta(days=1)
    first_day_prior_month = last_day_prior_month.replace(day=1)
    
    # Filter transactions for prior month
    prior_month_transactions = [
        t for t in transactions 
        if first_day_prior_month <= t['date'] <= last_day_prior_month
    ]
    
    if not prior_month_transactions:
        print("No transactions found for prior month")
        return None
    
    # Set up output path
    if output_path is None:
        output_path = os.path.join(
            tempfile.gettempdir(), 
            f"cash_app_simple_report_{first_day_prior_month.strftime('%Y_%m')}.pdf"
        )
    
    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    title = f"Cash App Report - {first_day_prior_month.strftime('%B %Y')}"
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 12))
    
    # Summary statistics
    total_income = sum(t['amount'] for t in prior_month_transactions if t['amount'] > 0)
    total_expenses = sum(t['amount'] for t in prior_month_transactions if t['amount'] < 0)
    net_cash_flow = total_income + total_expenses
    
    summary_text = f"""
    <b>Summary for {first_day_prior_month.strftime('%B %Y')}</b><br/>
    <br/>
    Total Transactions: {len(prior_month_transactions)}<br/>
    Total Income: ${total_income:,.2f}<br/>
    Total Expenses: ${abs(total_expenses):,.2f}<br/>
    Net Cash Flow: ${net_cash_flow:,.2f}<br/>
    """
    
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Category breakdown
    category_summary = {}
    for t in prior_month_transactions:
        category = t['category']
        if category not in category_summary:
            category_summary[category] = {'count': 0, 'total': 0}
        category_summary[category]['count'] += 1
        category_summary[category]['total'] += t['amount']
    
    # Create category table
    story.append(Paragraph("<b>Category Breakdown</b>", styles['Heading2']))
    
    table_data = [['Category', 'Transactions', 'Total Amount']]
    for category, data in sorted(category_summary.items()):
        table_data.append([
            category,
            str(data['count']),
            f"${data['total']:,.2f}"
        ])
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(table)
    
    # Build PDF
    doc.build(story)
    
    return output_path

def main():
    """Main test function"""
    print("="*60)
    print("SIMPLE PDF GENERATION TEST")
    print("="*60)
    
    csv_path = "cash_app_transactions.csv"
    
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found at {csv_path}")
        return
    
    try:
        print("1. Processing CSV data...")
        transactions = process_csv_data(csv_path)
        print(f"   Loaded {len(transactions)} transactions")
        
        print("2. Generating PDF report...")
        pdf_path = generate_simple_pdf_report(transactions)
        
        if pdf_path and os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path) / 1024
            print(f"SUCCESS! PDF generated: {pdf_path}")
            print(f"File size: {file_size:.1f} KB")
            
            # Try to open the PDF
            try:
                os.startfile(pdf_path)
                print("Opening PDF...")
            except:
                print("Note: Please open the PDF manually.")
                
        else:
            print("ERROR: PDF generation failed")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

