#!/usr/bin/env python3
"""
Simple Deep Dive Analysis of Cash App Transaction Data (without pandas)
Based on user's categorization rules:
- The Energy Auth transactions = Income
- Bitcoin purchases = Savings/Investment
- Savings Internal Transfer = Money movement (neutral)
- Deposits = Money movement (neutral)
- P2P = Expenses
"""

import csv
from datetime import datetime
from collections import defaultdict, Counter

def load_and_analyze_data(csv_path):
    """Load and perform comprehensive analysis of Cash App data"""
    
    print("="*80)
    print("CASH APP TRANSACTION DEEP DIVE ANALYSIS")
    print("="*80)
    
    transactions = []
    
    # Load the data
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            transactions.append(row)
    
    print(f"\nTotal transactions loaded: {len(transactions)}")
    
    # Parse dates and amounts
    for tx in transactions:
        try:
            # Clean date (remove timezone)
            date_str = tx['Date'].split(' EDT')[0].split(' EST')[0]
            tx['parsed_date'] = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            tx['year_month'] = tx['parsed_date'].strftime('%Y-%m')
            
            # Clean amount
            net_amount_str = tx['Net Amount'].replace('$', '').replace(',', '')
            if net_amount_str.startswith('-'):
                tx['net_amount'] = -float(net_amount_str[1:])
            else:
                tx['net_amount'] = float(net_amount_str)
        except:
            tx['parsed_date'] = None
            tx['net_amount'] = 0
    
    # Filter out transactions with parsing errors
    valid_transactions = [tx for tx in transactions if tx['parsed_date'] is not None]
    print(f"Valid transactions after parsing: {len(valid_transactions)}")
    
    if len(valid_transactions) > 0:
        dates = [tx['parsed_date'] for tx in valid_transactions]
        print(f"Date range: {min(dates).strftime('%Y-%m-%d')} to {max(dates).strftime('%Y-%m-%d')}")
    
    # SECTION 1: TRANSACTION TYPE ANALYSIS
    print("\n" + "="*60)
    print("1. TRANSACTION TYPE BREAKDOWN")
    print("="*60)
    
    tx_type_counts = Counter([tx['Transaction Type'] for tx in valid_transactions])
    tx_type_amounts = defaultdict(float)
    
    for tx in valid_transactions:
        tx_type_amounts[tx['Transaction Type']] += tx['net_amount']
    
    print("\nAll Transaction Types:")
    for tx_type, count in tx_type_counts.most_common():
        pct = (count / len(valid_transactions)) * 100
        total_amount = tx_type_amounts[tx_type]
        print(f"  {tx_type:<30} {count:>6} transactions ({pct:>5.1f}%) | Total: ${total_amount:>10,.2f}")
    
    # SECTION 2: INCOME ANALYSIS (The Energy Auth)
    print("\n" + "="*60)
    print("2. INCOME ANALYSIS")
    print("="*60)
    
    income_transactions = [tx for tx in valid_transactions 
                          if 'THE ENERGY AUTHO DIRECT DEP' in tx.get('Notes', '').upper()]
    
    print(f"\nIncome Transactions (Energy Auth): {len(income_transactions)}")
    if len(income_transactions) > 0:
        total_income = sum(tx['net_amount'] for tx in income_transactions)
        avg_income = total_income / len(income_transactions)
        print(f"Total Income: ${total_income:,.2f}")
        print(f"Average per payment: ${avg_income:,.2f}")
        
        # Monthly breakdown
        monthly_income = defaultdict(list)
        for tx in income_transactions:
            monthly_income[tx['year_month']].append(tx['net_amount'])
        
        print("\nIncome by Month:")
        for month in sorted(monthly_income.keys()):
            amounts = monthly_income[month]
            total = sum(amounts)
            count = len(amounts)
            print(f"  {month}: ${total:>10,.2f} ({count} payments)")
    
    # SECTION 3: BITCOIN/SAVINGS ANALYSIS
    print("\n" + "="*60)
    print("3. BITCOIN/SAVINGS ANALYSIS")
    print("="*60)
    
    bitcoin_transactions = [tx for tx in valid_transactions 
                           if tx['Transaction Type'] == 'Bitcoin Buy']
    
    print(f"\nBitcoin Purchase Transactions: {len(bitcoin_transactions)}")
    if len(bitcoin_transactions) > 0:
        bitcoin_amounts = [abs(tx['net_amount']) for tx in bitcoin_transactions]
        total_bitcoin = sum(bitcoin_amounts)
        avg_bitcoin = total_bitcoin / len(bitcoin_amounts)
        
        print(f"Total Bitcoin Investment: ${total_bitcoin:,.2f}")
        print(f"Average per purchase: ${avg_bitcoin:.2f}")
        
        # Monthly breakdown
        monthly_bitcoin = defaultdict(list)
        for tx in bitcoin_transactions:
            monthly_bitcoin[tx['year_month']].append(abs(tx['net_amount']))
        
        print("\nBitcoin Purchases by Month:")
        for month in sorted(monthly_bitcoin.keys()):
            amounts = monthly_bitcoin[month]
            total = sum(amounts)
            count = len(amounts)
            print(f"  {month}: ${total:>10,.2f} ({count} purchases)")
        
        print(f"\nBitcoin Purchase Size Analysis:")
        print(f"  Smallest: ${min(bitcoin_amounts):.2f}")
        print(f"  Largest: ${max(bitcoin_amounts):.2f}")
        print(f"  Median: ${sorted(bitcoin_amounts)[len(bitcoin_amounts)//2]:.2f}")
    
    # SECTION 4: P2P EXPENSES ANALYSIS
    print("\n" + "="*60)
    print("4. P2P EXPENSES ANALYSIS")
    print("="*60)
    
    p2p_transactions = [tx for tx in valid_transactions 
                       if tx['Transaction Type'] == 'P2P']
    
    print(f"\nP2P Transactions: {len(p2p_transactions)}")
    if len(p2p_transactions) > 0:
        p2p_amounts = [abs(tx['net_amount']) for tx in p2p_transactions]
        total_p2p = sum(p2p_amounts)
        avg_p2p = total_p2p / len(p2p_amounts)
        
        print(f"Total P2P Expenses: ${total_p2p:,.2f}")
        print(f"Average per transaction: ${avg_p2p:.2f}")
        
        print("\nP2P Recipients:")
        for tx in p2p_transactions:
            recipient = tx.get('Name of sender/receiver', 'Unknown')
            amount = abs(tx['net_amount'])
            notes = tx.get('Notes', 'No notes')
            date = tx['parsed_date'].strftime('%Y-%m-%d')
            print(f"  {date}: ${amount:>8.2f} to {recipient:<20} ({notes})")
    
    # SECTION 5: CASH CARD EXPENSES ANALYSIS
    print("\n" + "="*60)
    print("5. CASH CARD EXPENSES ANALYSIS")
    print("="*60)
    
    cash_card_transactions = [tx for tx in valid_transactions 
                             if tx['Transaction Type'] == 'Cash Card']
    
    print(f"\nCash Card Transactions: {len(cash_card_transactions)}")
    if len(cash_card_transactions) > 0:
        cash_card_amounts = [abs(tx['net_amount']) for tx in cash_card_transactions 
                            if tx['net_amount'] < 0]  # Only expenses
        total_cash_card = sum(cash_card_amounts)
        avg_cash_card = total_cash_card / len(cash_card_amounts) if cash_card_amounts else 0
        
        print(f"Total Cash Card Expenses: ${total_cash_card:,.2f}")
        print(f"Average per transaction: ${avg_cash_card:.2f}")
        
        # Top merchants
        merchant_spending = defaultdict(lambda: {'total': 0, 'count': 0})
        for tx in cash_card_transactions:
            if tx['net_amount'] < 0:  # Only expenses
                merchant = tx.get('Notes', 'Unknown')
                amount = abs(tx['net_amount'])
                merchant_spending[merchant]['total'] += amount
                merchant_spending[merchant]['count'] += 1
        
        print("\nTop 15 Merchants by Total Spending:")
        sorted_merchants = sorted(merchant_spending.items(), 
                                key=lambda x: x[1]['total'], reverse=True)[:15]
        
        for merchant, data in sorted_merchants:
            print(f"  {merchant:<40} ${data['total']:>8.2f} ({data['count']} visits)")
        
        # Expense categories
        print("\nExpense Categories (based on merchant analysis):")
        categories = categorize_expenses(cash_card_transactions)
        for category, data in categories.items():
            if data['total'] > 0:
                print(f"  {category:<20} ${data['total']:>10,.2f} ({data['count']} transactions)")
    
    # SECTION 6: MONEY MOVEMENT ANALYSIS
    print("\n" + "="*60)
    print("6. MONEY MOVEMENT ANALYSIS")
    print("="*60)
    
    # Savings transfers
    savings_transactions = [tx for tx in valid_transactions 
                           if tx['Transaction Type'] == 'Savings Internal Transfer']
    
    print(f"\nSavings Internal Transfers: {len(savings_transactions)}")
    if len(savings_transactions) > 0:
        savings_to_account = [abs(tx['net_amount']) for tx in savings_transactions if tx['net_amount'] < 0]
        total_to_savings = sum(savings_to_account)
        print(f"Total moved to savings: ${total_to_savings:,.2f}")
        
        # Monthly breakdown
        monthly_savings = defaultdict(float)
        for tx in savings_transactions:
            if tx['net_amount'] < 0:  # Money going to savings
                monthly_savings[tx['year_month']] += abs(tx['net_amount'])
        
        print("\nSavings Transfers by Month:")
        for month in sorted(monthly_savings.keys()):
            print(f"  {month}: ${monthly_savings[month]:>10,.2f}")
    
    # Deposits
    deposit_transactions = [tx for tx in valid_transactions 
                           if tx['Transaction Type'] == 'Deposits']
    
    print(f"\nDeposit Transactions: {len(deposit_transactions)}")
    if len(deposit_transactions) > 0:
        total_deposits = sum(tx['net_amount'] for tx in deposit_transactions)
        print(f"Total deposits: ${total_deposits:,.2f}")
        
        for tx in deposit_transactions:
            amount = tx['net_amount']
            notes = tx.get('Notes', 'No notes')
            date = tx['parsed_date'].strftime('%Y-%m-%d')
            print(f"  {date}: ${amount:>10,.2f} ({notes})")
    
    # SECTION 7: MONTHLY CASH FLOW ANALYSIS
    print("\n" + "="*60)
    print("7. MONTHLY CASH FLOW ANALYSIS")
    print("="*60)
    
    # Group by month
    monthly_data = defaultdict(list)
    for tx in valid_transactions:
        monthly_data[tx['year_month']].append(tx)
    
    for month in sorted(monthly_data.keys()):
        month_transactions = monthly_data[month]
        
        # Income
        month_income = sum(tx['net_amount'] for tx in month_transactions 
                          if 'THE ENERGY AUTHO DIRECT DEP' in tx.get('Notes', '').upper())
        
        # Bitcoin investment
        month_bitcoin = sum(abs(tx['net_amount']) for tx in month_transactions 
                           if tx['Transaction Type'] == 'Bitcoin Buy')
        
        # Cash card expenses
        month_cash_card = sum(abs(tx['net_amount']) for tx in month_transactions 
                             if tx['Transaction Type'] == 'Cash Card' and tx['net_amount'] < 0)
        
        # P2P expenses
        month_p2p = sum(abs(tx['net_amount']) for tx in month_transactions 
                       if tx['Transaction Type'] == 'P2P' and tx['net_amount'] < 0)
        
        # Savings transfers
        month_savings = sum(abs(tx['net_amount']) for tx in month_transactions 
                           if tx['Transaction Type'] == 'Savings Internal Transfer' and tx['net_amount'] < 0)
        
        # Net flow
        month_net = sum(tx['net_amount'] for tx in month_transactions)
        
        print(f"\n{month}:")
        print(f"  Income (Energy Auth): ${month_income:>10,.2f}")
        print(f"  Cash Card Expenses:   ${month_cash_card:>10,.2f}")
        print(f"  P2P Expenses:         ${month_p2p:>10,.2f}")
        print(f"  Bitcoin Investment:   ${month_bitcoin:>10,.2f}")
        print(f"  Savings Transfers:    ${month_savings:>10,.2f}")
        print(f"  Net Cash Flow:        ${month_net:>10,.2f}")
    
    # SECTION 8: SUMMARY STATISTICS
    print("\n" + "="*60)
    print("8. OVERALL SUMMARY STATISTICS")
    print("="*60)
    
    # Calculate totals
    total_income = sum(tx['net_amount'] for tx in valid_transactions 
                      if 'THE ENERGY AUTHO DIRECT DEP' in tx.get('Notes', '').upper())
    
    total_bitcoin = sum(abs(tx['net_amount']) for tx in valid_transactions 
                       if tx['Transaction Type'] == 'Bitcoin Buy')
    
    total_cash_expenses = sum(abs(tx['net_amount']) for tx in valid_transactions 
                             if tx['Transaction Type'] == 'Cash Card' and tx['net_amount'] < 0)
    
    total_p2p_expenses = sum(abs(tx['net_amount']) for tx in valid_transactions 
                            if tx['Transaction Type'] == 'P2P' and tx['net_amount'] < 0)
    
    total_savings_transfers = sum(abs(tx['net_amount']) for tx in valid_transactions 
                                 if tx['Transaction Type'] == 'Savings Internal Transfer' and tx['net_amount'] < 0)
    
    net_position = sum(tx['net_amount'] for tx in valid_transactions)
    
    print(f"\nTOTALS ACROSS ALL TIME:")
    print(f"  Total Income:           ${total_income:>12,.2f}")
    print(f"  Total Cash Expenses:    ${total_cash_expenses:>12,.2f}")
    print(f"  Total P2P Expenses:     ${total_p2p_expenses:>12,.2f}")
    print(f"  Total Bitcoin Investment: ${total_bitcoin:>12,.2f}")
    print(f"  Total Savings Transfers: ${total_savings_transfers:>12,.2f}")
    print(f"  Net Position:           ${net_position:>12,.2f}")
    
    # Ratios
    total_expenses = total_cash_expenses + total_p2p_expenses
    if total_income > 0:
        expense_ratio = (total_expenses / total_income) * 100
        bitcoin_ratio = (total_bitcoin / total_income) * 100
        savings_ratio = (total_savings_transfers / total_income) * 100
        print(f"\nRATIOS:")
        print(f"  Expense Ratio:          {expense_ratio:>12.1f}%")
        print(f"  Bitcoin Investment Rate: {bitcoin_ratio:>12.1f}%")
        print(f"  Savings Transfer Rate:   {savings_ratio:>12.1f}%")
    
    return valid_transactions

def categorize_expenses(cash_card_transactions):
    """Categorize cash card expenses based on merchant names"""
    categories = {
        'Food & Dining': {
            'keywords': ['CHIPOTLE', 'MCDONALD', 'STARBUCKS', 'WAFFLE HOUSE', 'WHATABURGER', 
                        'ZAXBY', 'MARCOS PIZZA', 'JETS PIZZA', 'TROPICAL SMOOTHIE', 'DELI', 
                        'JAX BEACH BRUNCH', 'RESTAURANT', 'QUE ONDA', 'HABERDISH', 'SAKE HOUSE',
                        'CREPE', 'WINN-DIXIE', 'JUICE TAP'], 
            'total': 0, 'count': 0
        },
        'Entertainment & Media': {
            'keywords': ['NETFLIX', 'SPOTIFY', 'YOUTUBE', 'STEAM', 'ROKU', 'MAX.COM', 'DECCA LIVE',
                        'HOPTINGER', 'SURFER THE BAR', 'BRIX TAPHOUSE'], 
            'total': 0, 'count': 0
        },
        'Gas & Travel': {
            'keywords': ['LOVE\'S', '7-ELEVEN', 'AMERICAN AIRLINES'], 
            'total': 0, 'count': 0
        },
        'Healthcare & Fitness': {
            'keywords': ['DENTAL', 'MEDICAL', 'CRUNCH FITNESS'], 
            'total': 0, 'count': 0
        },
        'Golf & Recreation': {
            'keywords': ['GOLF', 'MUNICIPAL', 'WHITEWATER', 'HULAWEENTIX'], 
            'total': 0, 'count': 0
        },
        'Subscriptions & Services': {
            'keywords': ['APPLE.COM', 'GOOGLE', 'MICROSOFT', 'COMCAST', 'OBSIDIAN'], 
            'total': 0, 'count': 0
        },
        'Shopping': {
            'keywords': ['AMAZON', 'WALGREENS', 'SUNRISE SURF', 'ARGYLE'], 
            'total': 0, 'count': 0
        },
        'Transportation': {
            'keywords': ['CDOT PAY BY CELL'], 
            'total': 0, 'count': 0
        },
        'Insurance & Financial': {
            'keywords': ['STATE FARM', 'CAPITAL ONE'], 
            'total': 0, 'count': 0
        },
        'Other': {'keywords': [], 'total': 0, 'count': 0}
    }
    
    for tx in cash_card_transactions:
        if tx['net_amount'] < 0:  # Only expenses
            merchant = str(tx.get('Notes', '')).upper()
            amount = abs(tx['net_amount'])
            categorized = False
            
            for category, data in categories.items():
                if category != 'Other':
                    for keyword in data['keywords']:
                        if keyword in merchant:
                            data['total'] += amount
                            data['count'] += 1
                            categorized = True
                            break
                    if categorized:
                        break
            
            if not categorized:
                categories['Other']['total'] += amount
                categories['Other']['count'] += 1
    
    return categories

if __name__ == "__main__":
    csv_path = "cash_app_transactions.csv"
    try:
        transactions = load_and_analyze_data(csv_path)
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE!")
        print("="*80)
    except FileNotFoundError:
        print(f"Error: Could not find {csv_path}")
        print("Please make sure the CSV file is in the current directory.")
    except Exception as e:
        print(f"Error during analysis: {e}")
