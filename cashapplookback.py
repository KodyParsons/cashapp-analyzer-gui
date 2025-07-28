import pandas as pd
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np
import re

import matplotlib.pyplot as plt

class CashAppAnalyzer:
    def __init__(self, csv_file_path):
        """Initialize the analyzer with CSV file path"""
        self.csv_file_path = csv_file_path
        self.df = None
        self.monthly_data = None
        
    def load_and_clean_data(self):
        """Load CSV and clean the data"""
        # Read CSV file
        self.df = pd.read_csv(self.csv_file_path)
        
        # Clean date format
        date_columns = ['Date', 'Transaction Date', 'date', 'transaction_date']
        date_col = None
        for col in date_columns:
            if col in self.df.columns:
                date_col = col
                break

        if date_col:
            # Remove unrecognized timezones (e.g. "EDT", "EST") and convert to datetime
            self.df['Date'] = pd.to_datetime(
                self.df[date_col].str.replace(r'\s+[A-Z]{3}$', '', regex=True),
                errors='coerce'
            )
        else:
            for col in self.df.columns:
                if 'date' in col.lower():
                    self.df['Date'] = pd.to_datetime(
                        self.df[col].str.replace(r'\s+[A-Z]{3}$', '', regex=True),
                        errors='coerce'
                    )
                    break
        
        # Clean amount columns - look for net amount, amount, etc.
        amount_columns = ['Net Amount', 'Amount', 'net_amount', 'amount', 'Net', 'Total']
        amount_col = None
        for col in amount_columns:
            if col in self.df.columns:
                amount_col = col
                break
        
        if amount_col:
            # Clean amount column - remove $ signs and convert to float
            self.df['Net_Amount'] = self.df[amount_col].astype(str).str.replace('$', '').str.replace(',', '')
            self.df['Net_Amount'] = pd.to_numeric(self.df['Net_Amount'], errors='coerce')
        
        # Extract month-year for grouping
        self.df['Month_Year'] = self.df['Date'].dt.to_period('M')
        
        return self
    
    def categorize_transactions(self):
        """Categorize transactions based on description/notes"""
        # Look for description/notes column
        desc_columns = ['Description', 'Notes', 'Transaction Type', 'description', 'notes']
        desc_col = None
        for col in desc_columns:
            if col in self.df.columns:
                desc_col = col
                break
        
        if desc_col:
            self.df['Description'] = self.df[desc_col].fillna('Unknown')
        else:
            self.df['Description'] = 'Unknown'
        
        # Define category mapping
        categories = {
            'Food & Dining': ['restaurant', 'food', 'coffee', 'pizza', 'burger', 'lunch', 'dinner', 'starbucks', 'mcdonald'],
            'Shopping': ['amazon', 'target', 'walmart', 'store', 'shopping', 'purchase', 'buy'],
            'Transportation': ['uber', 'lyft', 'gas', 'fuel', 'parking', 'taxi', 'transit'],
            'Entertainment': ['movie', 'game', 'spotify', 'netflix', 'entertainment', 'ticket'],
            'Bills & Utilities': ['bill', 'utility', 'electric', 'water', 'internet', 'phone', 'rent'],
            'Transfer': ['transfer', 'sent', 'received', 'cash out', 'cash in'],
            'ATM': ['atm', 'withdrawal', 'cash'],
            'Income': ['payroll', 'salary', 'deposit', 'income', 'payment received']
        }
        
        def categorize_transaction(description):
            description_lower = str(description).lower()
            for category, keywords in categories.items():
                if any(keyword in description_lower for keyword in keywords):
                    return category
            return 'Other'
        
        self.df['Category'] = self.df['Description'].apply(categorize_transaction)
        return self
    
    def generate_monthly_summary(self, months_back=6):
        """Generate monthly summary for the last N months"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months_back * 30)
        
        # Filter data for the specified period
        mask = (self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)
        filtered_df = self.df.loc[mask]
        
        # Group by month and category
        self.monthly_data = filtered_df.groupby(['Month_Year', 'Category'])['Net_Amount'].sum().unstack(fill_value=0)
        
        # Calculate monthly totals
        monthly_totals = filtered_df.groupby('Month_Year')['Net_Amount'].agg(['sum', 'count'])
        monthly_totals.columns = ['Total_Amount', 'Transaction_Count']
        
        return monthly_totals
    
    def create_visualizations(self):
        """Create various graphs for the report"""
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Cash App Monthly Transaction Report', fontsize=16, fontweight='bold')
        
        # 1. Monthly spending trend
        monthly_totals = self.df.groupby('Month_Year')['Net_Amount'].sum()
        axes[0, 0].plot(monthly_totals.index.astype(str), monthly_totals.values, marker='o', linewidth=2)
        axes[0, 0].set_title('Monthly Net Amount Trend')
        axes[0, 0].set_xlabel('Month')
        axes[0, 0].set_ylabel('Net Amount ($)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Category breakdown (pie chart)
        category_totals = self.df.groupby('Category')['Net_Amount'].sum()
        # Only show spending categories (negative amounts)
        spending_categories = category_totals[category_totals < 0].abs()
        if not spending_categories.empty:
            axes[0, 1].pie(spending_categories.values, labels=spending_categories.index, autopct='%1.1f%%')
            axes[0, 1].set_title('Spending by Category')
        
        # 3. Transaction count by month
        transaction_counts = self.df.groupby('Month_Year').size()
        axes[1, 0].bar(transaction_counts.index.astype(str), transaction_counts.values)
        axes[1, 0].set_title('Transaction Count by Month')
        axes[1, 0].set_xlabel('Month')
        axes[1, 0].set_ylabel('Number of Transactions')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 4. Income vs Expenses
        monthly_income = self.df[self.df['Net_Amount'] > 0].groupby('Month_Year')['Net_Amount'].sum()
        monthly_expenses = self.df[self.df['Net_Amount'] < 0].groupby('Month_Year')['Net_Amount'].sum().abs()

        # Reindex to a common index
        all_months = monthly_income.index.union(monthly_expenses.index).sort_values()
        monthly_income = monthly_income.reindex(all_months, fill_value=0)
        monthly_expenses = monthly_expenses.reindex(all_months, fill_value=0)

        x_pos = np.arange(len(all_months))
        width = 0.35

        axes[1, 1].bar(x_pos - width/2, monthly_income.values, width, label='Income', color='green', alpha=0.7)
        axes[1, 1].bar(x_pos + width/2, monthly_expenses.values, width, label='Expenses', color='red', alpha=0.7)
        axes[1, 1].set_title('Monthly Income vs Expenses')
        axes[1, 1].set_xlabel('Month')
        axes[1, 1].set_ylabel('Amount ($)')
        axes[1, 1].set_xticks(x_pos)
        axes[1, 1].set_xticklabels([str(m) for m in all_months], rotation=45)
        axes[1, 1].legend()
        
        plt.tight_layout()
        plt.savefig('cash_app_report.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_report(self):
        """Generate a comprehensive text report"""
        print("=" * 60)
        print("CASH APP MONTHLY TRANSACTION REPORT")
        print("=" * 60)
        
        # Basic statistics
        total_transactions = len(self.df)
        date_range = f"{self.df['Date'].min().strftime('%Y-%m-%d')} to {self.df['Date'].max().strftime('%Y-%m-%d')}"
        total_net = self.df['Net_Amount'].sum()
        
        print(f"Analysis Period: {date_range}")
        print(f"Total Transactions: {total_transactions}")
        print(f"Net Amount: ${total_net:.2f}")
        print()
        
        # Monthly breakdown
        print("MONTHLY SUMMARY:")
        print("-" * 40)
        monthly_summary = self.df.groupby('Month_Year').agg({
            'Net_Amount': ['sum', 'count'],
            'Category': lambda x: x.value_counts().index[0]  # Most common category
        }).round(2)
        
        for month in monthly_summary.index:
            net_amount = monthly_summary.loc[month, ('Net_Amount', 'sum')]
            transaction_count = monthly_summary.loc[month, ('Net_Amount', 'count')]
            top_category = monthly_summary.loc[month, ('Category', '<lambda>')]
            
            print(f"{month}: ${net_amount:.2f} ({transaction_count} transactions)")
            print(f"  Top Category: {top_category}")
        
        print()
        
        # Category breakdown
        print("SPENDING BY CATEGORY:")
        print("-" * 40)
        category_spending = self.df[self.df['Net_Amount'] < 0].groupby('Category')['Net_Amount'].sum().abs().sort_values(ascending=False)
        
        for category, amount in category_spending.items():
            percentage = (amount / category_spending.sum()) * 100
            print(f"{category}: ${amount:.2f} ({percentage:.1f}%)")
    
    def run_analysis(self):
        """Run the complete analysis"""
        print("Loading and cleaning data...")
        self.load_and_clean_data()
        
        print("Categorizing transactions...")
        self.categorize_transactions()
        
        print("Generating monthly summary...")
        self.generate_monthly_summary()
        
        print("Creating visualizations...")
        self.create_visualizations()
        
        print("Generating report...")
        self.generate_report()
        
        return self.df

# Usage example
if __name__ == "__main__":
    # Replace with your actual CSV file path
    csv_file_path = "cash_app_transactions.csv"
    
    analyzer = CashAppAnalyzer(csv_file_path)
    df_result = analyzer.run_analysis()
    
    # Optional: Save cleaned data to new CSV
    df_result.to_csv("cleaned_cash_app_data.csv", index=False)
    print("\nAnalysis complete! Check 'cash_app_report.png' for visualizations.")