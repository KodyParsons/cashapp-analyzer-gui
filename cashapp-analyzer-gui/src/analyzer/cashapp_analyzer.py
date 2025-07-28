# Import libraries with error handling for environment issues
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: pandas not available: {e}")
    pd = None
    PANDAS_AVAILABLE = False

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    sns = None
    SEABORN_AVAILABLE = False

from datetime import datetime, timedelta
import re
import os
import tempfile

# Import matplotlib with error handling
try:
    import matplotlib
    # Don't set backend here - let it be set by the GUI when needed
    import matplotlib.pyplot as plt
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    plt = None
    np = None
    MATPLOTLIB_AVAILABLE = False

# Import our new utilities
try:
    from utils.config import config
    from utils.logger import logger, log_performance
    UTILS_AVAILABLE = True
except ImportError:
    # Fallback for backwards compatibility
    config = None
    logger = None
    UTILS_AVAILABLE = False
    def log_performance(func):
        return func

class CashAppAnalyzer:
    def __init__(self, csv_file_path=None):
        """Initialize the analyzer with CSV file path"""
        self.csv_file_path = csv_file_path
        self.df = None
        self.monthly_data = None
        self.start_date = None
        self.end_date = None
        
    def load_and_clean_data(self):
        """Load CSV and clean the data"""
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is not available - cannot load CSV data")
            
        if not self.csv_file_path:
            raise ValueError("CSV file path is required")
            
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
        
        # Create Description column from Notes for compatibility
        if 'Notes' in self.df.columns:
            self.df['Description'] = self.df['Notes']
        elif 'Description' not in self.df.columns:
            # If neither Notes nor Description exists, create a generic description
            self.df['Description'] = 'Transaction'
        
        # Extract month-year for grouping
        self.df['Month_Year'] = self.df['Date'].dt.to_period('M')
        
        return self
    
    def categorize_transactions(self):
        """Categorize transactions based on user's rules and transaction types"""
        # Initialize categories based on transaction type and notes
        self.df['Category'] = 'Other'
        
        # Determine which column to use for transaction descriptions
        description_col = None
        if 'Notes' in self.df.columns:
            description_col = 'Notes'
        elif 'Description' in self.df.columns:
            description_col = 'Description'
        
        # Rule 1: Energy Auth transactions = Income (only if description column exists)
        if description_col:
            income_mask = self.df[description_col].str.contains('THE ENERGY AUTHO DIRECT DEP', case=False, na=False)
            self.df.loc[income_mask, 'Category'] = 'Income'
        
        # Rule 2: Bitcoin purchases = Investment (only significant amounts to avoid micro-DCA noise)
        if 'Transaction Type' in self.df.columns:
            bitcoin_mask = (
                ((self.df['Transaction Type'] == 'Bitcoin Buy') | 
                 (self.df['Transaction Type'] == 'Bitcoin Recurring Buy')) &
                (self.df['Net_Amount'].abs() >= 10.0)  # Only count Bitcoin purchases >= $10 as investments
            )
            self.df.loc[bitcoin_mask, 'Category'] = 'Investment (Bitcoin)'
            
            # Small Bitcoin purchases (< $10) are micro-DCA, categorize as regular expenses
            small_bitcoin_mask = (
                ((self.df['Transaction Type'] == 'Bitcoin Buy') | 
                 (self.df['Transaction Type'] == 'Bitcoin Recurring Buy')) &
                (self.df['Net_Amount'].abs() < 10.0)
            )
            self.df.loc[small_bitcoin_mask, 'Category'] = 'Micro-DCA (Bitcoin)'
        
        # Rule 3: Savings Internal Transfer = Investment (DCA strategy) - only for specific amounts
        # Differentiate between regular savings and Bitcoin savings based on description
        if 'Transaction Type' in self.df.columns:
            savings_mask = self.df['Transaction Type'] == 'Savings Internal Transfer'
            
            # Check description column for Bitcoin purchases
            if description_col:
                # Bitcoin savings transfers (contains "purchase of BTC")
                bitcoin_savings_mask = (
                    savings_mask & 
                    self.df[description_col].str.contains('purchase of BTC', case=False, na=False)
                )
                self.df.loc[bitcoin_savings_mask, 'Category'] = 'Investment (Bitcoin Savings)'
                
                # For regular savings transfers, don't automatically make them investments
                # They will be categorized later based on specific amounts
                regular_savings_mask = savings_mask & ~bitcoin_savings_mask
                self.df.loc[regular_savings_mask, 'Category'] = 'Savings Transfer'
            else:
                # If no description column, treat all savings transfers as regular transfers initially
                self.df.loc[savings_mask, 'Category'] = 'Savings Transfer'
        
        # Rule 4: Deposits = Money Movement (neutral) - exclude from income/expense calculations
        if 'Transaction Type' in self.df.columns:
            deposits_mask = self.df['Transaction Type'] == 'Deposits'
            self.df.loc[deposits_mask, 'Category'] = 'Internal Transfer'
        
        # Rule 5: Identify specific DCA savings amounts and mark as investments
        # DCA savings transfers (typically 10% of paycheck, varies with income)
        # Only include specific paycheck-based amounts, not round amounts which are likely temporary transfers
        # BUT exclude Bitcoin transactions which should already be categorized as Bitcoin investments
        savings_amounts = [318.28]  # Conservative: only include confirmed paycheck-based DCA amounts
        
        # Create masks for confirmed DCA amounts - these are investments, not internal transfers
        # Only apply to Savings Internal Transfer transactions that are NOT Bitcoin purchases
        dca_masks = []
        for amount in savings_amounts:
            # Only negative amounts (outflows) should be considered DCA investments
            # AND must be Savings Internal Transfer (not Bitcoin Buy)
            dca_mask = (
                (self.df['Net_Amount'] == -amount) &
                (self.df['Transaction Type'] == 'Savings Internal Transfer') &
                (~self.df['Transaction Type'].isin(['Bitcoin Buy', 'Bitcoin Recurring Buy']))
            )
            dca_masks.append(dca_mask)
        
        # Combine all DCA masks and apply only to transactions not already categorized as Bitcoin
        if dca_masks:
            dca_savings_mask = dca_masks[0]
            for mask in dca_masks[1:]:
                dca_savings_mask = dca_savings_mask | mask
            
            # Only apply to transactions not already categorized as Bitcoin investments
            existing_bitcoin_mask = self.df['Category'].isin(['Investment (Bitcoin)', 'Micro-DCA (Bitcoin)'])
            final_dca_mask = dca_savings_mask & ~existing_bitcoin_mask
            
            self.df.loc[final_dca_mask, 'Category'] = 'Investment (DCA Savings)'
        
        # Rent offset transfer ($1000) - this is fixed and is an internal transfer, not investment
        # Only apply to non-Bitcoin transactions to avoid misclassifying Bitcoin purchases
        rent_offset_mask = (
            ((self.df['Net_Amount'] == -1000.0) | (self.df['Net_Amount'] == 1000.0)) &
            (~self.df['Transaction Type'].isin(['Bitcoin Buy', 'Bitcoin Recurring Buy']))
        )
        self.df.loc[rent_offset_mask, 'Category'] = 'Rent Offset (Internal)'
        
        # Additional pattern: Look for other round investment amounts that might be DCA-based
        # DISABLED: User wants to ignore potential DCA amounts and only track confirmed DCA
        # potential_investment_mask = (
        #     ((self.df['Net_Amount'].abs() >= 250) & (self.df['Net_Amount'].abs() <= 500)) &
        #     (self.df['Transaction Type'] == 'Savings Internal Transfer') &
        #     (self.df['Net_Amount'] < 0)  # Only outflows should be considered investments
        # )
        # # Only apply this to transactions not already categorized as DCA investments
        # existing_investment_mask = self.df['Category'].str.contains('Investment', na=False)
        # self.df.loc[potential_investment_mask & ~existing_investment_mask, 'Category'] = 'Potential DCA (Internal)'
        
        # Rule 6: P2P transactions - need to distinguish between actual expenses and internal transfers
        p2p_mask = self.df['Transaction Type'] == 'P2P'
        # Apply P2P category first, then we'll refine below
        self.df.loc[p2p_mask, 'Category'] = 'P2P Transfer'
        
        # Rule 7: Cash Card transactions - categorize by merchant (these are actual expenses)
        cash_card_mask = self.df['Transaction Type'] == 'Cash Card'
        cash_card_df = self.df[cash_card_mask]
        
        # Enhanced cash card categorization
        for idx, row in cash_card_df.iterrows():
            merchant = str(row.get('Notes', '')).upper()
            category = self._categorize_cash_card_expense(merchant)
            self.df.at[idx, 'Category'] = category
        
        # Handle other transaction types
        withdrawal_mask = self.df['Transaction Type'] == 'Withdrawal'
        self.df.loc[withdrawal_mask, 'Category'] = 'Withdrawal'
        
        interest_mask = self.df['Transaction Type'] == 'Savings Interest Payment'
        self.df.loc[interest_mask, 'Category'] = 'Interest'
        
        print(f"Categorization complete! Categories found: {self.df['Category'].value_counts().to_dict()}")
    
    def _categorize_cash_card_expense(self, merchant_name):
        """Categorize cash card expenses based on merchant name"""
        merchant = merchant_name.upper()
        
        # Food & Dining
        food_keywords = [
            'CHIPOTLE', 'MCDONALD', 'STARBUCKS', 'WAFFLE HOUSE', 'WHATABURGER', 
            'ZAXBY', 'MARCOS PIZZA', 'JETS PIZZA', 'TROPICAL SMOOTHIE', 'DELI', 
            'JAX BEACH BRUNCH', 'RESTAURANT', 'QUE ONDA', 'HABERDISH', 'SAKE HOUSE',
            'CREPE', 'WINN-DIXIE', 'JUICE TAP', 'AKELS DELI', 'ANDREW`S DELI',
            'PENMAN HOSPITALITY', 'GEMMA FISH OYSTER', 'WORKMAN\'S FRIEND',
            'FRENCHY\'S SIP', 'SPO*LACOCINAMEXICANARESTA'
        ]
        for keyword in food_keywords:
            if keyword in merchant:
                return 'Food & Dining'
        
        # Entertainment & Media
        entertainment_keywords = [
            'NETFLIX', 'SPOTIFY', 'YOUTUBE', 'STEAM', 'ROKU', 'MAX.COM', 'DECCA LIVE',
            'HOPTINGER', 'SURFER THE BAR', 'BRIX TAPHOUSE', 'STEAMGAMES.COM'
        ]
        for keyword in entertainment_keywords:
            if keyword in merchant:
                return 'Entertainment & Media'
        
        # Gas & Travel
        travel_keywords = [
            'LOVE\'S', '7-ELEVEN', 'AMERICAN AIRLINES', 'XPRESS SHOP'
        ]
        for keyword in travel_keywords:
            if keyword in merchant:
                return 'Gas & Travel'
        
        # Healthcare & Fitness
        health_keywords = [
            'DENTAL', 'MEDICAL', 'CRUNCH FITNESS', 'WEST BEACHES DENTAL'
        ]
        for keyword in health_keywords:
            if keyword in merchant:
                return 'Healthcare & Fitness'
        
        # Golf & Recreation
        golf_keywords = [
            'GOLF', 'MUNICIPAL', 'WHITEWATER', 'HULAWEENTIX', 'CAROLINA LAKES GOL',
            'ST AUGUSTINE SHORES GC', 'JCKSNVL BCH MUNICPL GL', 'JACKSONVILLE BEACH GOLF',
            'BLUE SKY GOLF CLUB', 'MARSH LANDING COUNTRY CLU'
        ]
        for keyword in golf_keywords:
            if keyword in merchant:
                return 'Golf & Recreation'
        
        # Subscriptions & Services
        subscription_keywords = [
            'APPLE.COM', 'GOOGLE', 'MICROSOFT', 'COMCAST', 'OBSIDIAN', 'KINDLE SVCS',
            'HELP.MAX.COM', 'CLKBANK*VINCHECKUP', 'THE ROKU CHANNEL'
        ]
        for keyword in subscription_keywords:
            if keyword in merchant:
                return 'Subscriptions & Services'
        
        # Shopping
        shopping_keywords = [
            'AMAZON', 'WALGREENS', 'SUNRISE SURF', 'ARGYLE', 'SP FREAK ATHLETE',
            'SP TITAN FITNESS', 'NNT MENS WEARHOUSE'
        ]
        for keyword in shopping_keywords:
            if keyword in merchant:
                return 'Shopping'
        
        # Transportation
        transport_keywords = [
            'CDOT PAY BY CELL'
        ]
        for keyword in transport_keywords:
            if keyword in merchant:
                return 'Transportation'
        
        # Insurance & Financial
        financial_keywords = [
            'STATE FARM', 'CAPITAL ONE', 'APPLE CASH SENT MONEY'
        ]
        for keyword in financial_keywords:
            if keyword in merchant:
                return 'Insurance & Financial'
        
        # Housing (Rent/Utilities)
        housing_keywords = [
            'YSI*PROGRESS RESIDENTIAL', 'PROGRESS RESIDENTIAL'
        ]
        for keyword in housing_keywords:
            if keyword in merchant:
                return 'Housing & Rent'
        
        # Travel & Tourism
        tourism_keywords = [
            'VIATORTRIPADVISOR', 'AIRBNB', 'FGT*HULAWEENTIX'
        ]
        for keyword in tourism_keywords:
            if keyword in merchant:
                return 'Travel & Tourism'
        
        return 'Other Expenses'
    
    def set_date_range(self, start_date, end_date):
        """Set custom date range for analysis"""
        self.start_date = start_date
        self.end_date = end_date
        return self
    
    def generate_monthly_summary(self, months_back=None, start_date=None, end_date=None):
        """Generate monthly summary for the specified period"""
        if start_date and end_date:
            # Use provided date range
            self.start_date = start_date
            self.end_date = end_date
        elif self.start_date and self.end_date:
            # Use previously set date range
            start_date = self.start_date
            end_date = self.end_date
        elif months_back:
            # Use months_back parameter
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months_back * 30)
        else:
            # Default to 6 months
            end_date = datetime.now()
            start_date = end_date - timedelta(days=6 * 30)
        
        # Filter data for the specified period
        mask = (self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)
        filtered_df = self.df.loc[mask]
        
        # Group by month and category
        self.monthly_data = filtered_df.groupby(['Month_Year', 'Category'])['Net_Amount'].sum().unstack(fill_value=0)
        
        # Calculate monthly totals
        monthly_totals = filtered_df.groupby('Month_Year')['Net_Amount'].agg(['sum', 'count'])
        monthly_totals.columns = ['Total_Amount', 'Transaction_Count']
        
        return monthly_totals
    
    def create_visualizations(self, start_date=None, end_date=None):
        """Create comprehensive visualizations for the report"""
        # Filter data if date range is specified
        df_to_plot = self.df
        if start_date and end_date:
            mask = (self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)
            df_to_plot = self.df.loc[mask]
        elif self.start_date and self.end_date:
            mask = (self.df['Date'] >= self.start_date) & (self.df['Date'] <= self.end_date)
            df_to_plot = self.df.loc[mask]
        
        # Use non-interactive backend and create figure
        plt.ioff()  # Turn off interactive mode
        fig = plt.figure(figsize=(20, 16))
        
        # Create a 3x2 grid of subplots
        ax1 = plt.subplot(3, 2, 1)
        ax2 = plt.subplot(3, 2, 2)
        ax3 = plt.subplot(3, 2, 3)
        ax4 = plt.subplot(3, 2, 4)
        ax5 = plt.subplot(3, 2, 5)
        ax6 = plt.subplot(3, 2, 6)
        
        # Add date range to title
        title = 'Cash App Transaction Analysis Dashboard'
        if start_date and end_date:
            title += f'\n({start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")})'
        elif self.start_date and self.end_date:
            title += f'\n({self.start_date.strftime("%Y-%m-%d")} to {self.end_date.strftime("%Y-%m-%d")})'
        
        fig.suptitle(title, fontsize=18, fontweight='bold', y=0.98)
        
        # 1. Monthly Net Amount (Bar chart - better for single months)
        monthly_totals = df_to_plot.groupby('Month_Year')['Net_Amount'].sum()
        if not monthly_totals.empty:
            colors = ['green' if x >= 0 else 'red' for x in monthly_totals.values]
            bars = ax1.bar(range(len(monthly_totals)), monthly_totals.values, color=colors, alpha=0.7)
            ax1.set_xticks(range(len(monthly_totals)))
            ax1.set_xticklabels([str(m) for m in monthly_totals.index], rotation=45)
            ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            # Add value labels on bars
            for bar, value in zip(bars, monthly_totals.values):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + (0.01 * max(abs(monthly_totals.max()), abs(monthly_totals.min()))),
                        f'${value:,.0f}', ha='center', va='bottom' if height >= 0 else 'top', fontsize=9)
        ax1.set_title('Monthly Net Amount', fontweight='bold')
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Net Amount ($)')
        ax1.grid(True, alpha=0.3)
        
        # 2. Spending Categories (Pie chart)
        category_totals = df_to_plot.groupby('Category')['Net_Amount'].sum()
        spending_categories = category_totals[category_totals < 0].abs()
        if not spending_categories.empty:
            # Sort by amount for better visualization
            spending_categories = spending_categories.sort_values(ascending=False)
            colors = plt.cm.Set3(np.linspace(0, 1, len(spending_categories)))
            wedges, texts, autotexts = ax2.pie(spending_categories.values, labels=spending_categories.index, 
                                              autopct='%1.1f%%', colors=colors, startangle=90)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        else:
            ax2.text(0.5, 0.5, 'No spending data\navailable', ha='center', va='center', 
                    transform=ax2.transAxes, fontsize=12)
        ax2.set_title('Spending by Category', fontweight='bold')
        
        # 3. Monthly Income Trend
        monthly_income = df_to_plot[df_to_plot['Net_Amount'] > 0].groupby('Month_Year')['Net_Amount'].sum()
        if not monthly_income.empty:
            if len(monthly_income) == 1:
                # Single data point - use bar chart
                ax3.bar(range(len(monthly_income)), monthly_income.values, color='green', alpha=0.7, width=0.6)
                ax3.set_xticks(range(len(monthly_income)))
                ax3.set_xticklabels([str(m) for m in monthly_income.index])
                # Add value label
                for i, value in enumerate(monthly_income.values):
                    ax3.text(i, value + (0.01 * value), f'${value:,.0f}', ha='center', va='bottom', fontsize=9)
            else:
                # Multiple data points - use line chart
                ax3.plot(range(len(monthly_income)), monthly_income.values, marker='o', linewidth=2.5, 
                        markersize=8, color='green', alpha=0.8)
                ax3.set_xticks(range(len(monthly_income)))
                ax3.set_xticklabels([str(m) for m in monthly_income.index], rotation=45)
                ax3.fill_between(range(len(monthly_income)), monthly_income.values, alpha=0.3, color='green')
        else:
            ax3.text(0.5, 0.5, 'No income data\navailable', ha='center', va='center', 
                    transform=ax3.transAxes, fontsize=12)
        ax3.set_title('Monthly Income Trend', fontweight='bold')
        ax3.set_xlabel('Month')
        ax3.set_ylabel('Income ($)')
        ax3.grid(True, alpha=0.3)
        
        # 4. Monthly Expenses Trend
        monthly_expenses = df_to_plot[df_to_plot['Net_Amount'] < 0].groupby('Month_Year')['Net_Amount'].sum()
        monthly_expenses = monthly_expenses.abs()  # Apply abs() to the Series
        if not monthly_expenses.empty:
            if len(monthly_expenses) == 1:
                # Single data point - use bar chart
                ax4.bar(range(len(monthly_expenses)), monthly_expenses.values, color='red', alpha=0.7, width=0.6)
                ax4.set_xticks(range(len(monthly_expenses)))
                ax4.set_xticklabels([str(m) for m in monthly_expenses.index])
                # Add value label
                for i, value in enumerate(monthly_expenses.values):
                    ax4.text(i, value + (0.01 * value), f'${value:,.0f}', ha='center', va='bottom', fontsize=9)
            else:
                # Multiple data points - use line chart
                ax4.plot(range(len(monthly_expenses)), monthly_expenses.values, marker='o', linewidth=2.5, 
                        markersize=8, color='red', alpha=0.8)
                ax4.set_xticks(range(len(monthly_expenses)))
                ax4.set_xticklabels([str(m) for m in monthly_expenses.index], rotation=45)
                ax4.fill_between(range(len(monthly_expenses)), monthly_expenses.values, alpha=0.3, color='red')
        else:
            ax4.text(0.5, 0.5, 'No expense data\navailable', ha='center', va='center', 
                    transform=ax4.transAxes, fontsize=12)
        ax4.set_title('Monthly Expenses Trend', fontweight='bold')
        ax4.set_xlabel('Month')
        ax4.set_ylabel('Expenses ($)')
        ax4.grid(True, alpha=0.3)
        
        # 5. Income vs Expenses Comparison
        all_months = monthly_income.index.union(monthly_expenses.index).sort_values()
        if not all_months.empty:
            monthly_income_full = monthly_income.reindex(all_months, fill_value=0)
            monthly_expenses_full = monthly_expenses.reindex(all_months, fill_value=0)

            x_pos = np.arange(len(all_months))
            width = 0.35

            income_bars = ax5.bar(x_pos - width/2, monthly_income_full.values, width, 
                                 label='Income', color='green', alpha=0.7)
            expense_bars = ax5.bar(x_pos + width/2, monthly_expenses_full.values, width, 
                                  label='Expenses', color='red', alpha=0.7)
            
            ax5.set_xticks(x_pos)
            ax5.set_xticklabels([str(m) for m in all_months], rotation=45)
            ax5.legend()
            
            # Add value labels on bars
            for bar, value in zip(income_bars, monthly_income_full.values):
                if value > 0:
                    height = bar.get_height()
                    ax5.text(bar.get_x() + bar.get_width()/2., height + (0.01 * max(monthly_income_full.max(), monthly_expenses_full.max())),
                            f'${value:,.0f}', ha='center', va='bottom', fontsize=8)
            
            for bar, value in zip(expense_bars, monthly_expenses_full.values):
                if value > 0:
                    height = bar.get_height()
                    ax5.text(bar.get_x() + bar.get_width()/2., height + (0.01 * max(monthly_income_full.max(), monthly_expenses_full.max())),
                            f'${value:,.0f}', ha='center', va='bottom', fontsize=8)
        else:
            ax5.text(0.5, 0.5, 'No data available\nfor comparison', ha='center', va='center', 
                    transform=ax5.transAxes, fontsize=12)
            
        ax5.set_title('Monthly Income vs Expenses', fontweight='bold')
        ax5.set_xlabel('Month')
        ax5.set_ylabel('Amount ($)')
        ax5.grid(True, alpha=0.3)
        
        # 6. Transaction Activity (Count by Category)
        category_counts = df_to_plot['Category'].value_counts()
        if not category_counts.empty:
            # Only show top 8 categories to avoid overcrowding
            top_categories = category_counts.head(8)
            colors = plt.cm.tab10(np.linspace(0, 1, len(top_categories)))
            bars = ax6.barh(range(len(top_categories)), top_categories.values, color=colors, alpha=0.7)
            ax6.set_yticks(range(len(top_categories)))
            ax6.set_yticklabels(top_categories.index)
            ax6.invert_yaxis()  # Top category at the top
            
            # Add value labels
            for i, (bar, value) in enumerate(zip(bars, top_categories.values)):
                ax6.text(value + (0.01 * top_categories.max()), bar.get_y() + bar.get_height()/2,
                        f'{value}', ha='left', va='center', fontsize=9)
        else:
            ax6.text(0.5, 0.5, 'No transaction data\navailable', ha='center', va='center', 
                    transform=ax6.transAxes, fontsize=12)
        ax6.set_title('Transaction Count by Category', fontweight='bold')
        ax6.set_xlabel('Number of Transactions')
        ax6.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.93)  # Make room for the main title
        plt.savefig('cash_app_report.png', dpi=300, bbox_inches='tight')
        plt.close()  # Close the figure to free memory
        return fig
    
    def generate_report(self, start_date=None, end_date=None):
        """Generate a comprehensive text report"""
        # Filter data if date range is specified
        df_to_report = self.df
        if start_date and end_date:
            mask = (self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)
            df_to_report = self.df.loc[mask]
        elif self.start_date and self.end_date:
            mask = (self.df['Date'] >= self.start_date) & (self.df['Date'] <= self.end_date)
            df_to_report = self.df.loc[mask]
        
        report = []
        report.append("=" * 60)
        report.append("CASH APP MONTHLY TRANSACTION REPORT")
        report.append("=" * 60)
        
        # Basic statistics
        total_transactions = len(df_to_report)
        if total_transactions > 0:
            date_range = f"{df_to_report['Date'].min().strftime('%Y-%m-%d')} to {df_to_report['Date'].max().strftime('%Y-%m-%d')}"
            total_net = df_to_report['Net_Amount'].sum()
        else:
            date_range = "No data in selected range"
            total_net = 0
        
        report.append(f"Analysis Period: {date_range}")
        report.append(f"Total Transactions: {total_transactions}")
        report.append(f"Net Amount: ${total_net:.2f}")
        report.append("")
        
        if total_transactions > 0:
            # Check for bonuses/large payments
            bonus_transactions = df_to_report[
                (df_to_report['Category'].isin(['Bonus/Large Payment', 'Large Income/Payment'])) |
                (df_to_report['Net_Amount'] >= 10000)
            ]
            
            if not bonus_transactions.empty:
                report.append("LARGE PAYMENTS & BONUSES (≥$10,000):")
                report.append("-" * 40)
                for _, transaction in bonus_transactions.iterrows():
                    date_str = transaction['Date'].strftime('%Y-%m-%d')
                    amount = transaction['Net_Amount']
                    description = transaction['Description']
                    category = transaction['Category']
                    report.append(f"{date_str}: ${amount:,.2f} - {description} ({category})")
                report.append("")
            
            # Monthly breakdown
            report.append("MONTHLY SUMMARY:")
            report.append("-" * 40)
            monthly_summary = df_to_report.groupby('Month_Year').agg({
                'Net_Amount': ['sum', 'count'],
                'Category': lambda x: x.value_counts().index[0] if len(x) > 0 else 'N/A'
            }).round(2)
            
            for month in monthly_summary.index:
                net_amount = monthly_summary.loc[month, ('Net_Amount', 'sum')]
                transaction_count = monthly_summary.loc[month, ('Net_Amount', 'count')]
                top_category = monthly_summary.loc[month, ('Category', '<lambda>')]
                
                report.append(f"{month}: ${net_amount:,.2f} ({transaction_count} transactions)")
                report.append(f"  Top Category: {top_category}")
            
            report.append("")
            
            # Enhanced category breakdown with better formatting
            report.append("SPENDING BY CATEGORY:")
            report.append("-" * 40)
            
            # Define internal transfer categories to exclude from income/expense calculations
            internal_categories = [
                'Internal Transfer', 'Rent Offset (Internal)', 'Savings Transfer', 'Deposits'
            ]
            
            # Define investment categories to track separately
            investment_categories = [
                'Investment (Bitcoin)', 'Investment (DCA Savings)', 'Investment (Bitcoin Savings)', 'Investment (Potential DCA)'
            ]
            
            # Separate income, expenses, and investments, excluding internal transfers
            expense_data = df_to_report[
                (df_to_report['Net_Amount'] < 0) & 
                (~df_to_report['Category'].isin(internal_categories)) &
                (~df_to_report['Category'].isin(investment_categories))
            ]
            income_data = df_to_report[
                (df_to_report['Net_Amount'] > 0) & 
                (~df_to_report['Category'].isin(internal_categories))
            ]
            investment_data = df_to_report[
                (df_to_report['Net_Amount'] < 0) &
                (df_to_report['Category'].isin(investment_categories))
            ]
            
            if not expense_data.empty:
                category_spending = expense_data.groupby('Category')['Net_Amount'].sum()
                category_spending = category_spending.abs().sort_values(ascending=False)
                total_spending = category_spending.sum()
                
                for category, amount in category_spending.items():
                    percentage = (amount / total_spending) * 100
                    transaction_count = len(expense_data[expense_data['Category'] == category])
                    avg_amount = amount / transaction_count if transaction_count > 0 else 0
                    report.append(f"{category}: ${amount:,.2f} ({percentage:.1f}%) - {transaction_count} transactions, avg ${avg_amount:.2f}")
            else:
                report.append("No spending data available")
            
            report.append("")
            
            # Investment summary (new section)
            if not investment_data.empty:
                report.append("INVESTMENTS:")
                report.append("-" * 40)
                investment_summary = investment_data.groupby('Category')['Net_Amount'].sum()
                investment_summary = investment_summary.abs().sort_values(ascending=False)
                total_investments = investment_summary.sum()
                
                for category, amount in investment_summary.items():
                    percentage = (amount / total_investments) * 100 if total_investments > 0 else 0
                    transaction_count = len(investment_data[investment_data['Category'] == category])
                    avg_amount = amount / transaction_count if transaction_count > 0 else 0
                    report.append(f"{category}: ${amount:,.2f} ({percentage:.1f}%) - {transaction_count} transactions, avg ${avg_amount:.2f}")
                
                report.append(f"Total Investments: ${total_investments:,.2f}")
                report.append("")
            
            # Internal transfers summary (for transparency)
            internal_data = df_to_report[df_to_report['Category'].isin(internal_categories)]
            if not internal_data.empty:
                report.append("INTERNAL TRANSFERS (excluded from income/expense totals):")
                report.append("-" * 40)
                internal_summary = internal_data.groupby('Category')['Net_Amount'].sum().sort_values(ascending=False)
                for category, amount in internal_summary.items():
                    transaction_count = len(internal_data[internal_data['Category'] == category])
                    report.append(f"{category}: ${amount:,.2f} - {transaction_count} transactions")
                report.append("")
            
            # Summary statistics (excluding internal transfers but including investments)
            report.append("SUMMARY STATISTICS:")
            report.append("-" * 40)
            total_income = income_data['Net_Amount'].sum() if not income_data.empty else 0
            total_expenses = expense_data['Net_Amount'].sum() if not expense_data.empty else 0
            total_investments = abs(investment_data['Net_Amount'].sum()) if not investment_data.empty else 0
            net_amount_excluding_investments = total_income + total_expenses  # expenses are negative
            net_amount_including_investments = net_amount_excluding_investments - total_investments
            
            report.append(f"Total Income (excluding internal transfers): ${total_income:,.2f}")
            report.append(f"Total Expenses (excluding internal transfers and investments): ${abs(total_expenses):,.2f}")
            report.append(f"Total Investments: ${total_investments:,.2f}")
            report.append(f"Net Cash Flow (excluding investments): ${net_amount_excluding_investments:,.2f}")
            report.append(f"Net Cash Flow (including investments): ${net_amount_including_investments:,.2f}")
            
            if total_income > 0:
                savings_rate_excluding_investments = (net_amount_excluding_investments / total_income) * 100
                investment_rate = (total_investments / total_income) * 100
                total_savings_rate = savings_rate_excluding_investments + investment_rate
                report.append(f"Cash Savings Rate (excluding investments): {savings_rate_excluding_investments:.1f}%")
                report.append(f"Investment Rate: {investment_rate:.1f}%")
                report.append(f"Total Savings Rate (cash + investments): {total_savings_rate:.1f}%")
            
            # Category with most transactions
            most_frequent_category = df_to_report['Category'].value_counts().index[0]
            most_frequent_count = df_to_report['Category'].value_counts().iloc[0]
            report.append(f"Most Frequent Category: {most_frequent_category} ({most_frequent_count} transactions)")
            
            # Largest single transaction
            largest_expense = expense_data.loc[expense_data['Net_Amount'].idxmin()] if not expense_data.empty else None
            largest_income = income_data.loc[income_data['Net_Amount'].idxmax()] if not income_data.empty else None
            
            if largest_expense is not None:
                report.append(f"Largest Expense: ${abs(largest_expense['Net_Amount']):,.2f} - {largest_expense['Description']}")
            if largest_income is not None:
                report.append(f"Largest Income: ${largest_income['Net_Amount']:,.2f} - {largest_income['Description']}")
            
            # Top 5 Transactions (by absolute amount)
            report.append("")
            report.append("TOP 5 TRANSACTIONS BY AMOUNT:")
            report.append("-" * 40)
            all_transaction_data = pd.concat([income_data, expense_data, investment_data]) if not (income_data.empty and expense_data.empty and investment_data.empty) else pd.DataFrame()
            if not all_transaction_data.empty:
                # Sort by absolute amount (largest first)
                top_5_transactions = all_transaction_data.loc[all_transaction_data['Net_Amount'].abs().nlargest(5).index]
                for i, (_, transaction) in enumerate(top_5_transactions.iterrows(), 1):
                    date_str = transaction['Date'].strftime('%Y-%m-%d')
                    amount = transaction['Net_Amount']
                    description = transaction['Description']
                    category = transaction['Category']
                    sign = "+" if amount >= 0 else "-"
                    report.append(f"{i}. {date_str}: {sign}${abs(amount):,.2f} - {description} ({category})")
            else:
                report.append("No transactions available")
        
        return "\n".join(report)
    
    def run_analysis(self, start_date=None, end_date=None, months_back=None):
        """Run the complete analysis"""
        print("Loading and cleaning data...")
        self.load_and_clean_data()
        
        print("Categorizing transactions...")
        self.categorize_transactions()
        
        print("Generating monthly summary...")
        self.generate_monthly_summary(months_back=months_back, start_date=start_date, end_date=end_date)
        
        print("Creating visualizations...")
        fig = self.create_visualizations(start_date=start_date, end_date=end_date)
        
        print("Generating report...")
        report = self.generate_report(start_date=start_date, end_date=end_date)
        print(report)
        
        return self.df, fig, report
    
    def create_income_visualizations(self, start_date=None, end_date=None):
        """Create income-focused visualizations"""
        # Check if matplotlib is available
        if not MATPLOTLIB_AVAILABLE or plt is None:
            raise ImportError("Matplotlib is not available for creating visualizations")
        
        # Filter data if date range is specified
        df_to_plot = self.df
        if start_date and end_date:
            mask = (self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)
            df_to_plot = self.df.loc[mask]
        elif self.start_date and self.end_date:
            mask = (self.df['Date'] >= self.start_date) & (self.df['Date'] <= self.end_date)
            df_to_plot = self.df.loc[mask]
        
        # Filter for income transactions only, excluding internal transfers
        internal_categories = [
            'Internal Transfer', 'DCA Savings (Internal)', 'Potential DCA (Internal)', 
            'Rent Offset (Internal)', 'Savings Transfer', 'Deposits'
        ]
        income_df = df_to_plot[
            (df_to_plot['Net_Amount'] > 0) & 
            (~df_to_plot['Category'].isin(internal_categories))
        ]
        
        # Use non-interactive backend and create figure
        current_backend = matplotlib.get_backend()
        if current_backend != 'Agg':
            matplotlib.use('Agg')  # Use non-interactive backend for threading
        plt.ioff()  # Turn off interactive mode
        fig = plt.figure(figsize=(12, 8))
        
        # Create a single chart for daily income trend
        ax1 = plt.subplot(1, 1, 1)
        
        # Add date range to title
        title = 'Daily Income Trend'
        if start_date and end_date:
            title += f'\n({start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")})'
        elif self.start_date and self.end_date:
            title += f'\n({self.start_date.strftime("%Y-%m-%d")} to {self.end_date.strftime("%Y-%m-%d")})'
        
        fig.suptitle(title, fontsize=16, fontweight='bold', y=0.95)
        
        # 1. Daily Income Trend (Scatter Plot)
        daily_income = income_df.groupby('Date')['Net_Amount'].sum().sort_index()
        if not daily_income.empty:
            # Create scatter plot instead of line chart
            ax1.scatter(daily_income.index, daily_income.values, s=60, color='green', alpha=0.7, edgecolors='darkgreen')
            
            # Format x-axis dates properly
            import matplotlib.dates as mdates
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax1.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(daily_income)//10)))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
            
            # Add grid
            ax1.grid(True, alpha=0.3)
            
            # Format y-axis for currency
            ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Add value labels on significant data points (above $1000)
            for date, value in daily_income.items():
                if value > 1000:  # Only label significant income (likely paychecks)
                    ax1.annotate(f'${value:,.0f}', (date, value), 
                               textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)
        else:
            ax1.text(0.5, 0.5, 'No income data\navailable', ha='center', va='center', 
                    transform=ax1.transAxes, fontsize=12)
        ax1.set_title('Daily Income Trend (Scatter Plot)', fontweight='bold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Income ($)')
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.93)
        return fig
    
    def create_expense_visualizations(self, start_date=None, end_date=None):
        """Create expense-focused visualizations"""
        # Check if matplotlib is available
        if not MATPLOTLIB_AVAILABLE or plt is None:
            raise ImportError("Matplotlib is not available for creating visualizations")
        
        # Filter data if date range is specified
        df_to_plot = self.df
        if start_date and end_date:
            mask = (self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)
            df_to_plot = self.df.loc[mask]
        elif self.start_date and self.end_date:
            mask = (self.df['Date'] >= self.start_date) & (self.df['Date'] <= self.end_date)
            df_to_plot = self.df.loc[mask]
        
        # Filter for expense transactions only, excluding internal transfers
        internal_categories = [
            'Internal Transfer', 'DCA Savings (Internal)', 'Potential DCA (Internal)', 
            'Rent Offset (Internal)', 'Savings Transfer', 'Deposits'
        ]
        expense_df = df_to_plot[
            (df_to_plot['Net_Amount'] < 0) & 
            (~df_to_plot['Category'].isin(internal_categories))
        ].copy()
        expense_df['Net_Amount'] = expense_df['Net_Amount'].abs()  # Make positive for easier visualization
        
        # Use non-interactive backend and create figure
        current_backend = matplotlib.get_backend()
        if current_backend != 'Agg':
            matplotlib.use('Agg')  # Use non-interactive backend for threading
        plt.ioff()  # Turn off interactive mode
        fig = plt.figure(figsize=(16, 12))
        
        # Create a 2x2 grid of subplots
        ax1 = plt.subplot(2, 2, 1)
        ax2 = plt.subplot(2, 2, 2)
        ax3 = plt.subplot(2, 2, 3)
        ax4 = plt.subplot(2, 2, 4)
        
        # Add date range to title
        title = 'Expense Analysis Dashboard'
        if start_date and end_date:
            title += f'\n({start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")})'
        elif self.start_date and self.end_date:
            title += f'\n({self.start_date.strftime("%Y-%m-%d")} to {self.end_date.strftime("%Y-%m-%d")})'
        
        fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
        
        # 1. Daily Expense Trend
        daily_expenses = expense_df.groupby('Date')['Net_Amount'].sum()
        if not daily_expenses.empty:
            # Plot line chart with proper date formatting
            ax1.plot(daily_expenses.index, daily_expenses.values, marker='o', linewidth=2, 
                    markersize=4, color='red', alpha=0.8)
            ax1.fill_between(daily_expenses.index, daily_expenses.values, alpha=0.3, color='red')
            
            # Format x-axis dates properly
            import matplotlib.dates as mdates
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax1.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(daily_expenses)//10)))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
            
            # Add grid
            ax1.grid(True, alpha=0.3)
            
            # Format y-axis for currency
            ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        else:
            ax1.text(0.5, 0.5, 'No expense data\navailable', ha='center', va='center', 
                    transform=ax1.transAxes, fontsize=12)
        ax1.set_title('Daily Expense Trend', fontweight='bold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Expenses ($)')
        
        # 2. Expenses by Category
        expense_categories = expense_df.groupby('Category')['Net_Amount'].sum()
        if not expense_categories.empty:
            expense_categories = expense_categories.sort_values(ascending=False)
            colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(expense_categories)))
            wedges, texts, autotexts = ax2.pie(expense_categories.values, labels=expense_categories.index, 
                                              autopct='%1.1f%%', colors=colors, startangle=90)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        else:
            ax2.text(0.5, 0.5, 'No expense categories\navailable', ha='center', va='center', 
                    transform=ax2.transAxes, fontsize=12)
        ax2.set_title('Expenses by Category', fontweight='bold')
        
        # 3. Expense Transaction Count by Category
        expense_counts = expense_df['Category'].value_counts()
        if not expense_counts.empty:
            colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(expense_counts)))
            bars = ax3.barh(range(len(expense_counts)), expense_counts.values, color=colors, alpha=0.8)
            ax3.set_yticks(range(len(expense_counts)))
            ax3.set_yticklabels(expense_counts.index)
            ax3.invert_yaxis()
            
            for i, (bar, value) in enumerate(zip(bars, expense_counts.values)):
                ax3.text(value + (0.01 * expense_counts.max()), bar.get_y() + bar.get_height()/2,
                        f'{value}', ha='left', va='center', fontsize=9)
        else:
            ax3.text(0.5, 0.5, 'No expense transaction\ndata available', ha='center', va='center', 
                    transform=ax3.transAxes, fontsize=12)
        ax3.set_title('Expense Transactions by Category', fontweight='bold')
        ax3.set_xlabel('Number of Transactions')
        ax3.grid(True, alpha=0.3, axis='x')
        
        # 4. Top Spending Categories (showing amounts)
        if not expense_categories.empty:
            top_spending = expense_categories.head(8)
            bars = ax4.barh(range(len(top_spending)), top_spending.values, 
                           color='red', alpha=0.7)
            ax4.set_yticks(range(len(top_spending)))
            ax4.set_yticklabels(top_spending.index)
            ax4.invert_yaxis()
            
            for i, value in enumerate(top_spending.values):
                ax4.text(value + (0.01 * top_spending.max()), i,
                        f'${value:,.0f}', ha='left', va='center', fontsize=9)
        else:
            ax4.text(0.5, 0.5, 'No expense data\navailable', ha='center', va='center', 
                    transform=ax4.transAxes, fontsize=12)
        ax4.set_title('Top Spending Categories', fontweight='bold')
        ax4.set_xlabel('Total Spent ($)')
        ax4.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.93)
        return fig
    
    def create_cash_flow_visualizations(self, start_date=None, end_date=None):
        """Create cash flow visualizations showing net income (income - expenses) over time"""
        # Check if matplotlib is available
        if not MATPLOTLIB_AVAILABLE or plt is None:
            raise ImportError("Matplotlib is not available for creating visualizations")
        
        # Filter data if date range is specified
        df_to_plot = self.df
        if start_date and end_date:
            mask = (self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)
            df_to_plot = self.df.loc[mask]
        elif self.start_date and self.end_date:
            mask = (self.df['Date'] >= self.start_date) & (self.df['Date'] <= self.end_date)
            df_to_plot = self.df.loc[mask]
        
        # Use non-interactive backend and create figure
        current_backend = matplotlib.get_backend()
        if current_backend != 'Agg':
            matplotlib.use('Agg')  # Use non-interactive backend for threading
        plt.ioff()  # Turn off interactive mode
        fig = plt.figure(figsize=(16, 12))
        
        # Create a 2x2 grid of subplots
        ax1 = plt.subplot(2, 2, 1)
        ax2 = plt.subplot(2, 2, 2)
        ax3 = plt.subplot(2, 2, 3)
        ax4 = plt.subplot(2, 2, 4)
        
        # Add date range to title
        title = 'Cash Flow Analysis Dashboard'
        if start_date and end_date:
            title += f'\n({start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")})'
        elif self.start_date and self.end_date:
            title += f'\n({self.start_date.strftime("%Y-%m-%d")} to {self.end_date.strftime("%Y-%m-%d")})'
        
        fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
        
        # Define internal transfer categories to exclude from income/expense calculations
        internal_categories = [
            'Internal Transfer', 'Rent Offset (Internal)', 'Savings Transfer', 'Deposits', 'Potential DCA (Internal)'
        ]
        
        # Define investment categories to track separately (only legitimate DCA and Bitcoin)
        investment_categories = [
            'Investment (Bitcoin)', 'Investment (DCA Savings)'
        ]
        
        # Define categories to treat as regular expenses (not investments)
        expense_categories_additional = [
            'Micro-DCA (Bitcoin)'  # Small Bitcoin purchases are treated as regular expenses
        ]
        
        # Calculate monthly data
        income_data = df_to_plot[
            (df_to_plot['Net_Amount'] > 0) & 
            (~df_to_plot['Category'].isin(internal_categories)) &
            (~df_to_plot['Category'].isin(investment_categories))
        ]
        expense_data = df_to_plot[
            (df_to_plot['Net_Amount'] < 0) & 
            (~df_to_plot['Category'].isin(internal_categories)) &
            (~df_to_plot['Category'].isin(investment_categories))
        ]
        investment_data = df_to_plot[
            (df_to_plot['Net_Amount'] < 0) &  # Investments are outflows (negative amounts)
            (df_to_plot['Category'].isin(investment_categories))
        ]
        
        monthly_income = income_data.groupby('Month_Year')['Net_Amount'].sum()
        monthly_expenses = expense_data.groupby('Month_Year')['Net_Amount'].sum().abs()
        monthly_investments = investment_data.groupby('Month_Year')['Net_Amount'].sum().abs()
        
        # Get all months that have any transactions
        all_months = pd.concat([income_data, expense_data, investment_data]).groupby('Month_Year')['Net_Amount'].count().index
        if len(all_months) == 0:
            # If no transactions, use all months from data
            all_months = df_to_plot.groupby('Month_Year')['Net_Amount'].count().index
        
        monthly_income = monthly_income.reindex(all_months, fill_value=0)
        monthly_expenses = monthly_expenses.reindex(all_months, fill_value=0)
        monthly_investments = monthly_investments.reindex(all_months, fill_value=0)
        monthly_net_flow = monthly_income - monthly_expenses - monthly_investments
        
        # 1. Monthly Cash Flow Trend
        if not monthly_net_flow.empty:
            x_pos = range(len(monthly_net_flow))
            colors = ['green' if x >= 0 else 'red' for x in monthly_net_flow.values]
            bars = ax1.bar(x_pos, monthly_net_flow.values, color=colors, alpha=0.7)
            ax1.set_xticks(x_pos)
            ax1.set_xticklabels([str(m) for m in monthly_net_flow.index], rotation=45)
            ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            # Add value labels on bars
            for i, (value, bar) in enumerate(zip(monthly_net_flow.values, bars)):
                height = bar.get_height()
                if height >= 0:
                    ax1.text(bar.get_x() + bar.get_width()/2., height + (0.01 * abs(height)),
                            f'${value:,.0f}', ha='center', va='bottom', fontsize=9)
                else:
                    ax1.text(bar.get_x() + bar.get_width()/2., height - (0.01 * abs(height)),
                            f'${value:,.0f}', ha='center', va='top', fontsize=9)
        else:
            ax1.text(0.5, 0.5, 'No cash flow data\navailable', ha='center', va='center', 
                    transform=ax1.transAxes, fontsize=12)
        ax1.set_title('Monthly Net Cash Flow', fontweight='bold')
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Net Cash Flow ($)')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 2. Income vs Expenses vs Investments Comparison
        if not monthly_income.empty and not monthly_expenses.empty:
            x_pos = range(len(all_months))
            width = 0.25  # Narrower bars to fit three categories
            
            bars1 = ax2.bar([x - width for x in x_pos], monthly_income.values, 
                           width, label='Income', color='green', alpha=0.7)
            bars2 = ax2.bar([x for x in x_pos], monthly_expenses.values, 
                           width, label='Expenses', color='red', alpha=0.7)
            bars3 = ax2.bar([x + width for x in x_pos], monthly_investments.values, 
                           width, label='Investments', color='blue', alpha=0.7)
            
            ax2.set_xticks(x_pos)
            ax2.set_xticklabels([str(m) for m in all_months], rotation=45)
            ax2.legend()
            
            # Add value labels
            for bar in bars1:
                height = bar.get_height()
                if height > 0:
                    ax2.text(bar.get_x() + bar.get_width()/2., height + (0.01 * height),
                            f'${height:,.0f}', ha='center', va='bottom', fontsize=8)
            
            for bar in bars2:
                height = bar.get_height()
                if height > 0:
                    ax2.text(bar.get_x() + bar.get_width()/2., height + (0.01 * height),
                            f'${height:,.0f}', ha='center', va='bottom', fontsize=8)
            
            for bar in bars3:
                height = bar.get_height()
                if height > 0:
                    ax2.text(bar.get_x() + bar.get_width()/2., height + (0.01 * height),
                            f'${height:,.0f}', ha='center', va='bottom', fontsize=8)
        else:
            ax2.text(0.5, 0.5, 'No income/expense\ndata available', ha='center', va='center', 
                    transform=ax2.transAxes, fontsize=12)
        ax2.set_title('Income vs Expenses vs Investments by Month', fontweight='bold')
        ax2.set_xlabel('Month')
        ax2.set_ylabel('Amount ($)')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. Daily Cumulative Cash Flow (excluding investments to show true cash position)
        # Calculate daily net cash flow excluding both internal transfers and investments
        all_daily_data = df_to_plot[
            (~df_to_plot['Category'].isin(internal_categories)) &
            (~df_to_plot['Category'].isin(investment_categories))
        ]
        daily_net_flow = all_daily_data.groupby('Date')['Net_Amount'].sum().sort_index()
        
        if not daily_net_flow.empty:
            # Calculate cumulative sum
            cumulative_flow = daily_net_flow.cumsum()
            
            # Plot daily cumulative cash flow
            ax3.plot(cumulative_flow.index, cumulative_flow.values, 
                    marker='o', linewidth=2, markersize=3, color='purple', alpha=0.8)
            ax3.fill_between(cumulative_flow.index, cumulative_flow.values, 
                           alpha=0.3, color='purple')
            ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            # Format x-axis dates properly
            import matplotlib.dates as mdates
            ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax3.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(cumulative_flow)//10)))
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
            
            # Format y-axis for currency
            from matplotlib.ticker import FuncFormatter
            ax3.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x:,.0f}'))
        else:
            ax3.text(0.5, 0.5, 'No cumulative data\navailable', ha='center', va='center', 
                    transform=ax3.transAxes, fontsize=12)
        ax3.set_title('Daily Cumulative Cash Flow (Excluding Investments)', fontweight='bold')
        ax3.set_xlabel('Date')
        ax3.set_ylabel('Cumulative Cash Flow ($)')
        ax3.grid(True, alpha=0.3)
        
        # 4. Investment Breakdown by Category
        if not investment_data.empty:
            # Group investments by category
            investment_totals = investment_data.groupby('Category')['Net_Amount'].sum().abs()
            
            if not investment_totals.empty:
                # Create pie chart of investment allocation
                colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']  # Blue, orange, green, red, purple
                wedges, texts, autotexts = ax4.pie(investment_totals.values, 
                                                  labels=investment_totals.index, 
                                                  autopct='%1.1f%%', 
                                                  colors=colors[:len(investment_totals)],
                                                  startangle=90)
                
                # Style the text
                for text in texts:
                    text.set_fontsize(9)
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(8)
                
                # Add total investment amount to title
                total_investments = investment_totals.sum()
                ax4.set_title(f'Investment Allocation\nTotal: ${total_investments:,.0f}', fontweight='bold')
            else:
                ax4.text(0.5, 0.5, 'No investment data\navailable', ha='center', va='center', 
                        transform=ax4.transAxes, fontsize=12)
                ax4.set_title('Investment Allocation', fontweight='bold')
        else:
            ax4.text(0.5, 0.5, 'No investment data\navailable', ha='center', va='center', 
                    transform=ax4.transAxes, fontsize=12)
            ax4.set_title('Investment Allocation', fontweight='bold')
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.93)
        return fig
    
    def generate_pdf_report(self, output_path=None, month_offset=1):
        """
        Generate a PDF report for the specified month (default: prior month)
        
        Args:
            output_path (str): Path where PDF should be saved. If None, uses temp dir.
            month_offset (int): Number of months back from current month (1 = prior month)
        
        Returns:
            str: Path to generated PDF file
        """
        # Import reportlab here to avoid import errors when pandas fails
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
        except ImportError as e:
            raise ImportError(f"ReportLab is required for PDF generation. Please install it: conda install reportlab. Error: {e}")
        
        if self.df is None:
            raise ValueError("No data loaded. Please call load_and_clean_data() first.")
        
        # Calculate date range for the specified month
        today = datetime.now()
        if month_offset == 1:
            # Prior month: from 1st to last day of previous month
            first_day_current_month = today.replace(day=1)
            last_day_prior_month = first_day_current_month - timedelta(days=1)
            first_day_prior_month = last_day_prior_month.replace(day=1)
            start_date = first_day_prior_month
            end_date = last_day_prior_month
            report_title = f"Cash App Report - {start_date.strftime('%B %Y')}"
        else:
            # Custom month offset
            first_day_current_month = today.replace(day=1)
            target_month = first_day_current_month - timedelta(days=32 * (month_offset - 1))
            first_day_target_month = target_month.replace(day=1)
            # Get last day of target month
            if target_month.month == 12:
                next_month = target_month.replace(year=target_month.year + 1, month=1)
            else:
                next_month = target_month.replace(month=target_month.month + 1)
            last_day_target_month = next_month - timedelta(days=1)
            start_date = first_day_target_month  
            end_date = last_day_target_month
            report_title = f"Cash App Report - {start_date.strftime('%B %Y')}"
        
        # Filter data for the specified month
        month_data = self.df[
            (self.df['Date'] >= start_date) & 
            (self.df['Date'] <= end_date)
        ].copy()
        
        if month_data.empty:
            raise ValueError(f"No data found for the period {start_date.strftime('%B %Y')}")
        
        # Set up output path
        if output_path is None:
            output_path = os.path.join(
                tempfile.gettempdir(), 
                f"cash_app_report_{start_date.strftime('%Y_%m')}.pdf"
            )
        
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
        story.append(Paragraph(report_title, title_style))
        story.append(Spacer(1, 12))
        
        # Executive Summary - Define data splits first
        income_data = month_data[month_data['Net_Amount'] > 0]
        expense_data = month_data[month_data['Net_Amount'] < 0]
        
        # Define investment categories for PDF analysis
        investment_categories = [
            'Investment (Bitcoin)', 'Investment (DCA Savings)', 'Investment (Bitcoin Savings)', 'Investment (Potential DCA)'
        ]
        
        # Separate investment data from expense data
        investment_data = month_data[
            (month_data['Net_Amount'] < 0) &
            (month_data['Category'].isin(investment_categories))
        ]
        
        # Recalculate expenses excluding investments
        expense_data = month_data[
            (month_data['Net_Amount'] < 0) &
            (~month_data['Category'].isin(investment_categories))
        ]
        
        total_income = income_data['Net_Amount'].sum()
        total_expenses = expense_data['Net_Amount'].sum()
        total_investments = abs(investment_data['Net_Amount'].sum()) if not investment_data.empty else 0
        net_cash_flow = total_income + total_expenses  # total_expenses is negative, investments excluded
        transaction_count = len(month_data)
        
        summary_text = f"""
        <b>Executive Summary</b><br/>
        <br/>
        Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}<br/>
        Total Transactions: {transaction_count}<br/>
        <br/>
        <b>Financial Summary:</b><br/>
        Total Income: ${total_income:,.2f}<br/>
        Total Expenses: ${abs(total_expenses):,.2f}<br/>
        Total Investments: ${total_investments:,.2f}<br/>
        Net Cash Flow (excluding investments): ${net_cash_flow:,.2f}<br/>
        Net Cash Flow (including investments): ${net_cash_flow - total_investments:,.2f}<br/>
        """
        
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Category Breakdown
        story.append(Paragraph("Category Breakdown", heading_style))
        
        # Income categories
        # Skip income by category breakdown - removed per user request
        story.append(Spacer(1, 12))
        
        # Expense categories
        if not expense_data.empty:
            expense_by_category = expense_data.groupby('Category')['Net_Amount'].sum().sort_values(ascending=False)
            total_expenses = expense_by_category.sum()
            
            expense_table_data = [['Expense Category', 'Amount', 'Percentage']]
            for category, amount in expense_by_category.items():
                percentage = (abs(amount) / abs(total_expenses)) * 100 if total_expenses < 0 else 0
                expense_table_data.append([
                    category, 
                    f"${abs(amount):,.2f}", 
                    f"{percentage:.1f}%"
                ])
            
            expense_table = Table(expense_table_data)
            expense_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            story.append(expense_table)
            story.append(Spacer(1, 20))
        
        # Top Transactions
        story.append(Paragraph("Notable Transactions", heading_style))
        
        # Top 10 largest transactions (by absolute value)
        month_data['abs_amount'] = month_data['Net_Amount'].abs()
        top_transactions = month_data.nlargest(10, 'abs_amount')
        
        trans_table_data = [['Date', 'Description', 'Category', 'Amount']]
        for _, row in top_transactions.iterrows():
            trans_table_data.append([
                row['Date'].strftime('%m/%d/%Y'),
                str(row.get('Description', row.get('Notes', '')))[:40] + ('...' if len(str(row.get('Description', row.get('Notes', '')))) > 40 else ''),
                row['Category'],
                f"${row['Net_Amount']:,.2f}"
            ])
        
        trans_table = Table(trans_table_data)
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),  # Right align amounts
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        story.append(trans_table)
        story.append(Spacer(1, 20))
        
        # Key Insights
        story.append(Paragraph("Key Insights", heading_style))
        
        # Calculate insights
        daily_avg_expense = abs(total_expenses) / (end_date - start_date).days if total_expenses < 0 else 0
        
        # Find top expense category
        top_expense_category = "N/A"
        top_expense_amount = 0
        if not expense_data.empty:
            expense_by_cat = expense_data.groupby('Category')['Net_Amount'].sum()
            top_expense_category = expense_by_cat.abs().idxmax()
            top_expense_amount = abs(expense_by_cat.min())
        
        # Find largest single transaction
        largest_transaction = month_data.loc[month_data['abs_amount'].idxmax()] if not month_data.empty else None
        
        insights_text = f"""
        <b>Key Financial Insights:</b><br/>
        <br/>
        • Average daily expenses: ${daily_avg_expense:.2f}<br/>
        • Highest expense category: {top_expense_category} (${top_expense_amount:,.2f})<br/>
        • Largest single transaction: ${largest_transaction['Net_Amount']:,.2f} ({largest_transaction['Category']})<br/>
        • Cash flow trend: {"Positive" if net_cash_flow > 0 else "Negative"} (${net_cash_flow:,.2f})<br/>
        <br/>
        <b>Transaction Patterns:</b><br/>
        • Total transactions processed: {transaction_count}<br/>
        • Income transactions: {len(income_data)}<br/>
        • Expense transactions: {len(expense_data)}<br/>
        """
        
        story.append(Paragraph(insights_text, styles['Normal']))
        
        # Generate visualizations and add to PDF
        story.append(Spacer(1, 20))
        story.append(Paragraph("Visual Analysis", heading_style))
        
        # Create enhanced visualizations for PDF
        if not MATPLOTLIB_AVAILABLE:
            story.append(Paragraph("Note: Chart generation unavailable (matplotlib not installed)", styles['Italic']))
        else:
            try:
                # Set backend for PDF generation
                import matplotlib
                matplotlib.use('Agg')  # Use non-interactive backend for PDF
                import matplotlib.pyplot as plt
                import numpy as np
                
                # Create a comprehensive chart figure
                fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
                fig.suptitle(f'Cash App Analysis - {start_date.strftime("%B %Y")}', fontsize=16, fontweight='bold')
                
                # Chart 1: Income vs Expenses
                if not income_data.empty and not expense_data.empty:
                    categories = ['Income', 'Expenses']
                    amounts = [total_income, abs(total_expenses)]
                    colors_list = ['#2E8B57', '#DC143C']  # Sea green for income, crimson for expenses
                    
                    bars = ax1.bar(categories, amounts, color=colors_list, alpha=0.7)
                    ax1.set_title('Income vs Expenses', fontweight='bold')
                    ax1.set_ylabel('Amount ($)')
                    
                    # Add value labels on bars
                    for bar, amount in zip(bars, amounts):
                        height = bar.get_height()
                        ax1.text(bar.get_x() + bar.get_width()/2., height + max(amounts) * 0.01,
                                f'${amount:,.0f}', ha='center', va='bottom', fontweight='bold')
                else:
                    ax1.text(0.5, 0.5, 'No income/expense\ndata available', ha='center', va='center', 
                            transform=ax1.transAxes, fontsize=12)
                    ax1.set_title('Income vs Expenses', fontweight='bold')
                
                # Chart 2: Expense Categories Pie Chart
                if not expense_data.empty:
                    expense_by_category = expense_data.groupby('Category')['Net_Amount'].sum().abs()
                    if len(expense_by_category) > 0:
                        # Only show top 6 categories, group others
                        if len(expense_by_category) > 6:
                            top_5 = expense_by_category.nlargest(5)
                            others_sum = expense_by_category.iloc[5:].sum()
                            plot_data = top_5.copy()
                            plot_data['Others'] = others_sum
                        else:
                            plot_data = expense_by_category
                        
                        wedges, texts, autotexts = ax2.pie(plot_data.values, labels=plot_data.index, 
                                                          autopct='%1.1f%%', startangle=90)
                        ax2.set_title('Expense Categories', fontweight='bold')
                        
                        # Make percentage text bold
                        for autotext in autotexts:
                            autotext.set_color('white')
                            autotext.set_fontweight('bold')
                    else:
                        ax2.text(0.5, 0.5, 'No expense\ncategories', ha='center', va='center')
                        ax2.set_title('Expense Categories', fontweight='bold')
                else:
                    ax2.text(0.5, 0.5, 'No expense data', ha='center', va='center')
                    ax2.set_title('Expense Categories', fontweight='bold')
                
                # Chart 3: Daily Spending Trend
                if not month_data.empty:
                    daily_expenses = month_data[month_data['Net_Amount'] < 0].groupby(month_data['Date'].dt.date)['Net_Amount'].sum().abs()
                    if len(daily_expenses) > 0:
                        ax3.plot(daily_expenses.index, daily_expenses.values, marker='o', linewidth=2, markersize=4)
                        ax3.set_title('Daily Spending Trend', fontweight='bold')
                        ax3.set_ylabel('Daily Expenses ($)')
                        ax3.set_xlabel('Date')
                        
                        # Format x-axis dates
                        ax3.tick_params(axis='x', rotation=45)
                        
                        # Add trend line
                        if len(daily_expenses) > 1:
                            z = np.polyfit(range(len(daily_expenses)), daily_expenses.values, 1)
                            p = np.poly1d(z)
                            ax3.plot(daily_expenses.index, p(range(len(daily_expenses))), 
                                    "r--", alpha=0.8, linewidth=1, label='Trend')
                            ax3.legend()
                    else:
                        ax3.text(0.5, 0.5, 'No daily spending\ndata available', ha='center', va='center', 
                                transform=ax3.transAxes, fontsize=12)
                        ax3.set_title('Daily Spending Trend', fontweight='bold')
                else:
                    ax3.text(0.5, 0.5, 'No data available', ha='center', va='center', 
                            transform=ax3.transAxes, fontsize=12)
                    ax3.set_title('Daily Spending Trend', fontweight='bold')
                
                # Chart 4: Top Merchants/Categories
                if not expense_data.empty:
                    # Calculate expense by category for fallback use
                    expense_by_category = expense_data.groupby('Category')['Net_Amount'].sum().abs()
                    
                    # Try to get merchant data from Description/Notes or use categories
                    if 'Description' in month_data.columns or 'Notes' in month_data.columns:
                        # Get top merchants from Cash Card transactions if Transaction Type exists
                        if 'Transaction Type' in month_data.columns:
                            cash_card_data = month_data[(month_data['Transaction Type'] == 'Cash Card') & 
                                                       (month_data['Net_Amount'] < 0)]
                        else:
                            # If no Transaction Type, use all expense data
                            cash_card_data = expense_data
                            
                        if not cash_card_data.empty:
                            # Use Description or Notes for merchant names
                            desc_col = 'Description' if 'Description' in month_data.columns else 'Notes'
                            merchant_spending = cash_card_data.groupby(desc_col)['Net_Amount'].sum().abs().nlargest(8)
                            if len(merchant_spending) > 0:
                                ax4.barh(range(len(merchant_spending)), merchant_spending.values, 
                                        color='skyblue', alpha=0.7)
                                ax4.set_yticks(range(len(merchant_spending)))
                                ax4.set_yticklabels([name[:25] + '...' if len(name) > 25 else name 
                                                   for name in merchant_spending.index])
                                ax4.set_title('Top Merchants/Payees', fontweight='bold')
                                ax4.set_xlabel('Amount Spent ($)')
                            else:
                                ax4.text(0.5, 0.5, 'No merchant\ndata available', ha='center', va='center', 
                                        transform=ax4.transAxes, fontsize=12)
                                ax4.set_title('Top Merchants/Payees', fontweight='bold')
                        else:
                            # Fallback to categories
                            if len(expense_by_category) > 0:
                                top_categories = expense_by_category.nlargest(8)
                                ax4.barh(range(len(top_categories)), top_categories.values, 
                                        color='lightcoral', alpha=0.7)
                                ax4.set_yticks(range(len(top_categories)))
                                ax4.set_yticklabels(top_categories.index)
                                ax4.set_title('Top Expense Categories', fontweight='bold')
                                ax4.set_xlabel('Amount Spent ($)')
                            else:
                                ax4.text(0.5, 0.5, 'No expense\ncategories', ha='center', va='center', 
                                        transform=ax4.transAxes, fontsize=12)
                                ax4.set_title('Top Expense Categories', fontweight='bold')
                    else:
                        # Fallback to categories when no Description/Notes column
                        if len(expense_by_category) > 0:
                            top_categories = expense_by_category.nlargest(8)
                            ax4.barh(range(len(top_categories)), top_categories.values, 
                                    color='lightcoral', alpha=0.7)
                            ax4.set_yticks(range(len(top_categories)))
                            ax4.set_yticklabels(top_categories.index)
                            ax4.set_title('Top Expense Categories', fontweight='bold')
                            ax4.set_xlabel('Amount Spent ($)')
                        else:
                            ax4.text(0.5, 0.5, 'No expense\ncategories', ha='center', va='center', 
                                    transform=ax4.transAxes, fontsize=12)
                            ax4.set_title('Top Expense Categories', fontweight='bold')
                else:
                    ax4.text(0.5, 0.5, 'No expense data', ha='center', va='center', 
                            transform=ax4.transAxes, fontsize=12)
                    ax4.set_title('Top Merchants', fontweight='bold')
                
                plt.tight_layout()
                plt.subplots_adjust(top=0.93)
                
                # Save chart as temporary image
                chart_path = os.path.join(tempfile.gettempdir(), 
                                        f"cash_app_chart_{start_date.strftime('%Y_%m')}.png")
                fig.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
                plt.close(fig)
                
                # Add chart to PDF
                story.append(Image(chart_path, width=7.5*inch, height=6*inch))
                
                # Clean up temp file
                if os.path.exists(chart_path):
                    os.remove(chart_path)
                
            except Exception as e:
                # If visualization fails, add a note
                story.append(Paragraph(f"Note: Chart generation unavailable ({str(e)})", styles['Italic']))
        
        # Build PDF
        doc.build(story)
        
        print(f"PDF report generated successfully: {output_path}")
        return output_path
    
    def generate_comprehensive_pdf_report(self, output_path=None, month_offset=1, include_all_charts=True):
        """
        Generate a comprehensive PDF report using the new enhanced PDF generator
        
        Args:
            output_path (str): Path where PDF should be saved. If None, uses temp dir.
            month_offset (int): Number of months back from current month (1 = prior month)
            include_all_charts (bool): Whether to include income, expense, and cash flow analysis charts
        
        Returns:
            str: Path to generated PDF file
        """
        if not UTILS_AVAILABLE:
            # Fallback to original method if new utilities aren't available
            if logger:
                logger.warning("New utilities not available, falling back to original PDF generation")
            return self.generate_pdf_report(output_path=output_path, month_offset=month_offset)
        
        try:
            from core.pdf_generator import PDFGenerator
        except ImportError as e:
            if logger:
                logger.warning(f"Enhanced PDF generator not available, falling back to original: {e}")
            return self.generate_pdf_report(output_path=output_path, month_offset=month_offset)
        
        # Use the new comprehensive PDF generator
        pdf_gen = PDFGenerator(self)
        
        if include_all_charts:
            return pdf_gen.generate_comprehensive_pdf(
                output_path=output_path,
                month_offset=month_offset,
                include_all_charts=True
            )
        else:
            return pdf_gen.generate_quick_pdf(
                output_path=output_path,
                month_offset=month_offset
            )
    
    def create_top_expenses_visualizations(self, start_date=None, end_date=None):
        """Create top expenses visualization excluding rent"""
        # Check if matplotlib is available
        if not MATPLOTLIB_AVAILABLE or plt is None:
            raise ImportError("Matplotlib is not available for creating visualizations")
        
        # Filter data if date range is specified
        df_to_plot = self.df
        if start_date and end_date:
            mask = (self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)
            df_to_plot = self.df.loc[mask]
        elif self.start_date and self.end_date:
            mask = (self.df['Date'] >= self.start_date) & (self.df['Date'] <= self.end_date)
            df_to_plot = self.df.loc[mask]
        
        # Define categories to exclude from expense analysis
        excluded_categories = [
            'Internal Transfer', 'Rent Offset (Internal)', 'Savings Transfer', 'Deposits',
            'Investment (Bitcoin)', 'Investment (DCA Savings)', 'Investment (Bitcoin Savings)', 'Investment (Potential DCA)',
            'Housing & Rent'  # Exclude rent from top expenses
        ]
        
        # Filter for expense transactions only, excluding internal transfers, investments, and rent
        expense_df = df_to_plot[
            (df_to_plot['Net_Amount'] < 0) & 
            (~df_to_plot['Category'].isin(excluded_categories))
        ].copy()
        expense_df['Net_Amount'] = expense_df['Net_Amount'].abs()  # Make positive for easier visualization
        
        # Use non-interactive backend and create figure
        current_backend = matplotlib.get_backend()
        if current_backend != 'Agg':
            matplotlib.use('Agg')  # Use non-interactive backend for threading
        plt.ioff()  # Turn off interactive mode
        fig = plt.figure(figsize=(14, 10))
        
        # Create a 2x2 grid of subplots
        ax1 = plt.subplot(2, 2, 1)
        ax2 = plt.subplot(2, 2, 2)
        ax3 = plt.subplot(2, 2, 3)
        ax4 = plt.subplot(2, 2, 4)
        
        # Add date range to title
        title = 'Top Expenses Analysis (Excluding Rent)'
        if start_date and end_date:
            title += f'\n({start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")})'
        elif self.start_date and self.end_date:
            title += f'\n({self.start_date.strftime("%Y-%m-%d")} to {self.end_date.strftime("%Y-%m-%d")})'
        
        fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
        
        # 1. Top 5 Expense Categories (Bar Chart)
        expense_categories = expense_df.groupby('Category')['Net_Amount'].sum()
        if not expense_categories.empty:
            top_5_categories = expense_categories.sort_values(ascending=False).head(5)
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']  # Nice color palette
            
            bars = ax1.barh(range(len(top_5_categories)), top_5_categories.values, 
                           color=colors[:len(top_5_categories)], alpha=0.8)
            ax1.set_yticks(range(len(top_5_categories)))
            ax1.set_yticklabels(top_5_categories.index)
            ax1.invert_yaxis()  # Top category at the top
            
            # Add value labels on bars
            for i, (bar, value) in enumerate(zip(bars, top_5_categories.values)):
                ax1.text(value + (0.02 * top_5_categories.max()), bar.get_y() + bar.get_height()/2,
                        f'${value:,.0f}', ha='left', va='center', fontsize=10, fontweight='bold')
        else:
            ax1.text(0.5, 0.5, 'No expense data\navailable', ha='center', va='center', 
                    transform=ax1.transAxes, fontsize=12)
        ax1.set_title('Top 5 Expense Categories', fontweight='bold', fontsize=14)
        ax1.set_xlabel('Total Amount ($)')
        ax1.grid(True, alpha=0.3, axis='x')
        
        # 2. Top 5 Individual Transactions (Bar Chart)
        if not expense_df.empty:
            top_5_transactions = expense_df.nlargest(5, 'Net_Amount')
            
            # Create labels for transactions (truncate long descriptions)
            labels = []
            for _, row in top_5_transactions.iterrows():
                desc = str(row.get('Description', row.get('Notes', 'Unknown')))
                if len(desc) > 20:
                    desc = desc[:17] + '...'
                labels.append(f"{desc}\n({row['Category']})")
            
            bars = ax2.bar(range(len(top_5_transactions)), top_5_transactions['Net_Amount'].values, 
                          color='lightcoral', alpha=0.8)
            ax2.set_xticks(range(len(top_5_transactions)))
            ax2.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
            
            # Add value labels on bars
            for bar, value in zip(bars, top_5_transactions['Net_Amount'].values):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + (0.01 * height),
                        f'${value:,.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        else:
            ax2.text(0.5, 0.5, 'No transaction data\navailable', ha='center', va='center', 
                    transform=ax2.transAxes, fontsize=12)
        ax2.set_title('Top 5 Individual Transactions', fontweight='bold', fontsize=14)
        ax2.set_ylabel('Amount ($)')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. Monthly Trend of Top Category
        if not expense_categories.empty:
            top_category = expense_categories.idxmax()
            top_category_data = expense_df[expense_df['Category'] == top_category]
            monthly_trend = top_category_data.groupby('Month_Year')['Net_Amount'].sum().sort_index()
            
            if len(monthly_trend) > 1:
                ax3.plot(range(len(monthly_trend)), monthly_trend.values, marker='o', 
                        linewidth=3, markersize=8, color='#FF6B6B', alpha=0.8)
                ax3.fill_between(range(len(monthly_trend)), monthly_trend.values, alpha=0.3, color='#FF6B6B')
                ax3.set_xticks(range(len(monthly_trend)))
                ax3.set_xticklabels([str(m) for m in monthly_trend.index], rotation=45)
            elif len(monthly_trend) == 1:
                ax3.bar(range(len(monthly_trend)), monthly_trend.values, color='#FF6B6B', alpha=0.8, width=0.6)
                ax3.set_xticks(range(len(monthly_trend)))
                ax3.set_xticklabels([str(m) for m in monthly_trend.index])
            else:
                ax3.text(0.5, 0.5, f'No data for\n{top_category}', ha='center', va='center', 
                        transform=ax3.transAxes, fontsize=12)
        else:
            ax3.text(0.5, 0.5, 'No category data\navailable', ha='center', va='center', 
                    transform=ax3.transAxes, fontsize=12)
        ax3.set_title(f'Monthly Trend: {top_category if not expense_categories.empty else "N/A"}', 
                     fontweight='bold', fontsize=12)
        ax3.set_xlabel('Month')
        ax3.set_ylabel('Amount ($)')
        ax3.grid(True, alpha=0.3)
        
        # 4. Expense Distribution Pie Chart (Top 5 + Others)
        if not expense_categories.empty:
            if len(expense_categories) > 5:
                top_4_categories = expense_categories.sort_values(ascending=False).head(4)
                others_sum = expense_categories.sort_values(ascending=False).iloc[4:].sum()
                plot_data = top_4_categories.copy()
                plot_data['Others'] = others_sum
            else:
                plot_data = expense_categories.sort_values(ascending=False)
            
            colors_pie = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
            wedges, texts, autotexts = ax4.pie(plot_data.values, labels=plot_data.index, 
                                              autopct='%1.1f%%', colors=colors_pie[:len(plot_data)],
                                              startangle=90)
            
            # Style the text
            for text in texts:
                text.set_fontsize(10)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
                
            total_expenses = plot_data.sum()
            ax4.set_title(f'Expense Distribution\nTotal: ${total_expenses:,.0f}', 
                         fontweight='bold', fontsize=12)
        else:
            ax4.text(0.5, 0.5, 'No expense data\navailable', ha='center', va='center', 
                    transform=ax4.transAxes, fontsize=12)
            ax4.set_title('Expense Distribution', fontweight='bold', fontsize=12)
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.93)
        return fig