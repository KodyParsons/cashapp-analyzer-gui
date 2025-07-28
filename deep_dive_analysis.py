#!/usr/bin/env python3
"""
Deep Dive Analysis of Cash App Transaction Data
Based on user's categorization rules:
- The Energy Auth transactions = Income
- Bitcoin purchases = Savings/Investment
- Savings Internal Transfer = Money movement (neutral)
- Deposits = Money movement (neutral)
- P2P = Expenses
"""

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

def load_and_analyze_data(csv_path):
    """Load and perform comprehensive analysis of Cash App data"""
    
    print("="*80)
    print("CASH APP TRANSACTION DEEP DIVE ANALYSIS")
    print("="*80)
    
    # Load the data
    df = pd.read_csv(csv_path)
    print(f"\nTotal transactions loaded: {len(df)}")
    
    # Clean and prepare data
    df['Date'] = pd.to_datetime(df['Date'].str.replace(r'\s+[A-Z]{3}$', '', regex=True), errors='coerce')
    df['Net_Amount'] = pd.to_numeric(df['Net Amount'].str.replace('[$,]', '', regex=True), errors='coerce')
    df['Amount_Value'] = pd.to_numeric(df['Amount'].str.replace('[$,-]', '', regex=True), errors='coerce')
    
    # Add month/year for grouping
    df['Month_Year'] = df['Date'].dt.to_period('M')
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    
    # SECTION 1: TRANSACTION TYPE ANALYSIS
    print("\n" + "="*60)
    print("1. TRANSACTION TYPE BREAKDOWN")
    print("="*60)
    
    transaction_types = df['Transaction Type'].value_counts()
    print("\nAll Transaction Types:")
    for tx_type, count in transaction_types.items():
        pct = (count / len(df)) * 100
        total_amount = df[df['Transaction Type'] == tx_type]['Net_Amount'].sum()
        print(f"  {tx_type:<30} {count:>6} transactions ({pct:>5.1f}%) | Total: ${total_amount:>10,.2f}")
    
    # SECTION 2: INCOME ANALYSIS (The Energy Auth)
    print("\n" + "="*60)
    print("2. INCOME ANALYSIS")
    print("="*60)
    
    # Income from Energy Auth
    income_mask = df['Notes'].str.contains('THE ENERGY AUTHO DIRECT DEP', case=False, na=False)
    income_df = df[income_mask]
    
    print(f"\nIncome Transactions (Energy Auth): {len(income_df)}")
    if len(income_df) > 0:
        total_income = income_df['Net_Amount'].sum()
        avg_income = income_df['Net_Amount'].mean()
        print(f"Total Income: ${total_income:,.2f}")
        print(f"Average per payment: ${avg_income:,.2f}")
        
        print("\nIncome by Month:")
        monthly_income = income_df.groupby('Month_Year')['Net_Amount'].agg(['sum', 'count'])
        for month, row in monthly_income.iterrows():
            print(f"  {month}: ${row['sum']:>10,.2f} ({row['count']} payments)")
    
    # SECTION 3: BITCOIN/SAVINGS ANALYSIS
    print("\n" + "="*60)
    print("3. BITCOIN/SAVINGS ANALYSIS")
    print("="*60)
    
    bitcoin_mask = df['Transaction Type'] == 'Bitcoin Buy'
    bitcoin_df = df[bitcoin_mask]
    
    print(f"\nBitcoin Purchase Transactions: {len(bitcoin_df)}")
    if len(bitcoin_df) > 0:
        total_bitcoin = abs(bitcoin_df['Net_Amount'].sum())
        avg_bitcoin = abs(bitcoin_df['Net_Amount'].mean())
        print(f"Total Bitcoin Investment: ${total_bitcoin:,.2f}")
        print(f"Average per purchase: ${avg_bitcoin:.2f}")
        
        print("\nBitcoin Purchases by Month:")
        monthly_bitcoin = bitcoin_df.groupby('Month_Year')['Net_Amount'].agg(['sum', 'count'])
        for month, row in monthly_bitcoin.iterrows():
            print(f"  {month}: ${abs(row['sum']):>10,.2f} ({row['count']} purchases)")
        
        # Bitcoin purchase size distribution
        bitcoin_amounts = abs(bitcoin_df['Net_Amount'])
        print(f"\nBitcoin Purchase Size Analysis:")
        print(f"  Smallest: ${bitcoin_amounts.min():.2f}")
        print(f"  Largest: ${bitcoin_amounts.max():.2f}")
        print(f"  Median: ${bitcoin_amounts.median():.2f}")
        print(f"  Most frequent range: ${bitcoin_amounts.mode().iloc[0]:.2f}")
    
    # SECTION 4: P2P EXPENSES ANALYSIS
    print("\n" + "="*60)
    print("4. P2P EXPENSES ANALYSIS")
    print("="*60)
    
    p2p_mask = df['Transaction Type'] == 'P2P'
    p2p_df = df[p2p_mask]
    
    print(f"\nP2P Transactions: {len(p2p_df)}")
    if len(p2p_df) > 0:
        total_p2p = abs(p2p_df['Net_Amount'].sum())
        avg_p2p = abs(p2p_df['Net_Amount'].mean())
        print(f"Total P2P Expenses: ${total_p2p:,.2f}")
        print(f"Average per transaction: ${avg_p2p:.2f}")
        
        print("\nP2P Recipients:")
        for _, row in p2p_df.iterrows():
            recipient = row['Name of sender/receiver']
            amount = abs(row['Net_Amount'])
            notes = row['Notes']
            date = row['Date'].strftime('%Y-%m-%d')
            print(f"  {date}: ${amount:>8.2f} to {recipient:<20} ({notes})")
    
    # SECTION 5: CASH CARD EXPENSES ANALYSIS
    print("\n" + "="*60)
    print("5. CASH CARD EXPENSES ANALYSIS")
    print("="*60)
    
    cash_card_mask = df['Transaction Type'] == 'Cash Card'
    cash_card_df = df[cash_card_mask]
    
    print(f"\nCash Card Transactions: {len(cash_card_df)}")
    if len(cash_card_df) > 0:
        total_cash_card = abs(cash_card_df['Net_Amount'].sum())
        avg_cash_card = abs(cash_card_df['Net_Amount'].mean())
        print(f"Total Cash Card Expenses: ${total_cash_card:,.2f}")
        print(f"Average per transaction: ${avg_cash_card:.2f}")
        
        # Top merchants
        print("\nTop 10 Merchants by Total Spending:")
        merchant_spending = cash_card_df.groupby('Notes')['Net_Amount'].agg(['sum', 'count'])
        merchant_spending['abs_sum'] = abs(merchant_spending['sum'])
        top_merchants = merchant_spending.sort_values('abs_sum', ascending=False).head(10)
        
        for merchant, row in top_merchants.iterrows():
            print(f"  {merchant:<35} ${row['abs_sum']:>8.2f} ({row['count']} visits)")
        
        # Expense categories based on merchant names
        print("\nExpense Categories (based on merchant analysis):")
        categories = categorize_expenses(cash_card_df)
        for category, data in categories.items():
            print(f"  {category:<20} ${data['total']:>10,.2f} ({data['count']} transactions)")
    
    # SECTION 6: MONEY MOVEMENT ANALYSIS
    print("\n" + "="*60)
    print("6. MONEY MOVEMENT ANALYSIS")
    print("="*60)
    
    # Savings transfers
    savings_mask = df['Transaction Type'] == 'Savings Internal Transfer'
    savings_df = df[savings_mask]
    
    print(f"\nSavings Internal Transfers: {len(savings_df)}")
    if len(savings_df) > 0:
        total_to_savings = abs(savings_df[savings_df['Net_Amount'] < 0]['Net_Amount'].sum())
        print(f"Total moved to savings: ${total_to_savings:,.2f}")
        
        print("\nSavings Transfers by Month:")
        monthly_savings = savings_df.groupby('Month_Year')['Net_Amount'].sum()
        for month, amount in monthly_savings.items():
            print(f"  {month}: ${abs(amount):>10,.2f}")
    
    # Deposits
    deposits_mask = df['Transaction Type'] == 'Deposits'
    deposits_df = df[deposits_mask]
    
    print(f"\nDeposit Transactions: {len(deposits_df)}")
    if len(deposits_df) > 0:
        total_deposits = deposits_df['Net_Amount'].sum()
        print(f"Total deposits: ${total_deposits:,.2f}")
        
        for _, row in deposits_df.iterrows():
            amount = row['Net_Amount']
            notes = row['Notes']
            date = row['Date'].strftime('%Y-%m-%d')
            print(f"  {date}: ${amount:>10,.2f} ({notes})")
    
    # SECTION 7: MONTHLY CASH FLOW ANALYSIS
    print("\n" + "="*60)
    print("7. MONTHLY CASH FLOW ANALYSIS")
    print("="*60)
    
    # Calculate monthly cash flow
    monthly_analysis = df.groupby('Month_Year').agg({
        'Net_Amount': 'sum'
    }).round(2)
    
    # Break down by category for each month
    for month in monthly_analysis.index:
        month_data = df[df['Month_Year'] == month]
        
        # Income
        month_income = month_data[month_data['Notes'].str.contains('THE ENERGY AUTHO DIRECT DEP', case=False, na=False)]['Net_Amount'].sum()
        
        # Bitcoin investment
        month_bitcoin = abs(month_data[month_data['Transaction Type'] == 'Bitcoin Buy']['Net_Amount'].sum())
        
        # Cash card expenses
        month_cash_card = abs(month_data[month_data['Transaction Type'] == 'Cash Card']['Net_Amount'].sum())
        
        # P2P expenses
        month_p2p = abs(month_data[month_data['Transaction Type'] == 'P2P']['Net_Amount'].sum())
        
        # Savings transfers
        month_savings = abs(month_data[month_data['Transaction Type'] == 'Savings Internal Transfer']['Net_Amount'].sum())
        
        print(f"\n{month}:")
        print(f"  Income (Energy Auth): ${month_income:>10,.2f}")
        print(f"  Cash Card Expenses:   ${month_cash_card:>10,.2f}")
        print(f"  P2P Expenses:         ${month_p2p:>10,.2f}")
        print(f"  Bitcoin Investment:   ${month_bitcoin:>10,.2f}")
        print(f"  Savings Transfers:    ${month_savings:>10,.2f}")
        print(f"  Net Cash Flow:        ${monthly_analysis.loc[month, 'Net_Amount']:>10,.2f}")
    
    # SECTION 8: SUMMARY STATISTICS
    print("\n" + "="*60)
    print("8. OVERALL SUMMARY STATISTICS")
    print("="*60)
    
    # Calculate totals
    total_income = df[df['Notes'].str.contains('THE ENERGY AUTHO DIRECT DEP', case=False, na=False)]['Net_Amount'].sum()
    total_bitcoin = abs(df[df['Transaction Type'] == 'Bitcoin Buy']['Net_Amount'].sum())
    total_cash_expenses = abs(df[df['Transaction Type'] == 'Cash Card']['Net_Amount'].sum())
    total_p2p_expenses = abs(df[df['Transaction Type'] == 'P2P']['Net_Amount'].sum())
    total_savings_transfers = abs(df[df['Transaction Type'] == 'Savings Internal Transfer']['Net_Amount'].sum())
    
    print(f"\nTOTALS ACROSS ALL TIME:")
    print(f"  Total Income:           ${total_income:>12,.2f}")
    print(f"  Total Cash Expenses:    ${total_cash_expenses:>12,.2f}")
    print(f"  Total P2P Expenses:     ${total_p2p_expenses:>12,.2f}")
    print(f"  Total Bitcoin Investment: ${total_bitcoin:>12,.2f}")
    print(f"  Total Savings Transfers: ${total_savings_transfers:>12,.2f}")
    print(f"  Net Position:           ${df['Net_Amount'].sum():>12,.2f}")
    
    # Savings rate
    total_expenses = total_cash_expenses + total_p2p_expenses
    if total_income > 0:
        expense_ratio = (total_expenses / total_income) * 100
        bitcoin_ratio = (total_bitcoin / total_income) * 100
        print(f"\nRATIOS:")
        print(f"  Expense Ratio:          {expense_ratio:>12.1f}%")
        print(f"  Bitcoin Investment Rate: {bitcoin_ratio:>12.1f}%")
    
    return df

def categorize_expenses(cash_card_df):
    """Categorize cash card expenses based on merchant names"""
    categories = {
        'Food & Dining': {'keywords': ['CHIPOTLE', 'MCDONALD', 'STARBUCKS', 'WAFFLE HOUSE', 'WHATABURGER', 
                                      'ZAXBY', 'AMAZON MKTPLACE', 'MARCOS PIZZA', 'JETS PIZZA', 
                                      'TROPICAL SMOOTHIE', 'DELI', 'JAX BEACH BRUNCH', 'RESTAURANT'], 
                         'total': 0, 'count': 0},
        'Entertainment': {'keywords': ['NETFLIX', 'SPOTIFY', 'YOUTUBE', 'STEAM', 'ROKU', 'MAX.COM'], 
                         'total': 0, 'count': 0},
        'Gas & Travel': {'keywords': ['LOVE\'S', '7-ELEVEN', 'AMERICAN AIRLINES'], 
                        'total': 0, 'count': 0},
        'Healthcare': {'keywords': ['DENTAL', 'MEDICAL'], 
                      'total': 0, 'count': 0},
        'Golf & Recreation': {'keywords': ['GOLF', 'MUNICIPAL'], 
                             'total': 0, 'count': 0},
        'Subscriptions': {'keywords': ['APPLE.COM', 'GOOGLE', 'MICROSOFT', 'COMCAST'], 
                         'total': 0, 'count': 0},
        'Other': {'keywords': [], 'total': 0, 'count': 0}
    }
    
    for _, row in cash_card_df.iterrows():
        merchant = str(row['Notes']).upper()
        amount = abs(row['Net_Amount'])
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
    df = load_and_analyze_data(csv_path)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
