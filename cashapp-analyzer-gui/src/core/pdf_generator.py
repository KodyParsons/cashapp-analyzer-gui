"""Enhanced PDF Generator for Cash App Analyzer"""
import os
import tempfile
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
import matplotlib.pyplot as plt

# Import ReportLab components that we'll need throughout
try:
    from reportlab.lib.units import inch as INCH_UNIT
    REPORTLAB_AVAILABLE = True
except ImportError:
    INCH_UNIT = 72  # Fallback: 72 points = 1 inch
    REPORTLAB_AVAILABLE = False

from utils.config import config
from utils.logger import logger, log_performance

class PDFGenerator:
    """Enhanced PDF generator that reuses existing visualization methods"""
    
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.temp_files = []  # Track temp files for cleanup
    
    def __del__(self):
        """Cleanup temp files"""
        self.cleanup_temp_files()
    
    def cleanup_temp_files(self):
        """Remove temporary files"""
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"Could not remove temp file {file_path}: {e}")
        self.temp_files.clear()
    
    @log_performance
    def generate_comprehensive_pdf(self, 
                                 output_path: Optional[str] = None,
                                 month_offset: int = 1,
                                 include_all_charts: bool = True) -> str:
        """
        Generate a comprehensive PDF report with all visualization types
        
        Args:
            output_path: Where to save the PDF
            month_offset: Number of months back from current (1 = prior month)
            include_all_charts: Whether to include income, expense, and cash flow charts
          Returns:
            Path to generated PDF file
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
        except ImportError as e:
            raise ImportError(f"ReportLab is required for PDF generation. Install with: pip install reportlab. Error: {e}")
        
        if self.analyzer.df is None:
            raise ValueError("No data loaded. Please load data first.")
        
        # Calculate date range
        start_date, end_date = self._calculate_date_range(month_offset)
        logger.info(f"Generating PDF report for {start_date.strftime('%B %Y')}")
        
        # Filter data for the period
        month_data = self._filter_data_by_date(start_date, end_date)
        if month_data.empty:
            raise ValueError(f"No data found for the period {start_date.strftime('%B %Y')}")
        
        # Set up output path
        if output_path is None:
            output_path = config.get_temp_file_path(f"cash_app_comprehensive_report_{start_date.strftime('%Y_%m')}.pdf")
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = self._create_title_style(styles)
        heading_style = self._create_heading_style(styles)
        
        # Build PDF content
        story.extend(self._create_title_section(start_date, end_date, title_style))
        story.extend(self._create_executive_summary(month_data, styles))
        story.extend(self._create_detailed_analysis(month_data, heading_style, styles))
        
        if include_all_charts:
            story.extend(self._create_comprehensive_visualizations(start_date, end_date, heading_style))
        
        # Build PDF
        doc.build(story)
        
        # Cleanup
        self.cleanup_temp_files()
        
        logger.info(f"PDF report generated successfully: {output_path}")
        return output_path
    
    def _calculate_date_range(self, month_offset: int) -> Tuple[datetime, datetime]:
        """Calculate date range for the report"""
        today = datetime.now()
        
        if month_offset == 1:
            # Prior month: from 1st to last day of previous month
            first_day_current_month = today.replace(day=1)
            last_day_prior_month = first_day_current_month - timedelta(days=1)
            first_day_prior_month = last_day_prior_month.replace(day=1)
            return first_day_prior_month, last_day_prior_month
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
            
            return first_day_target_month, last_day_target_month
    
    def _filter_data_by_date(self, start_date: datetime, end_date: datetime):
        """Filter analyzer data by date range"""
        return self.analyzer.df[
            (self.analyzer.df['Date'] >= start_date) & 
            (self.analyzer.df['Date'] <= end_date)
        ].copy()
    
    def _create_title_style(self, styles):
        """Create custom title style"""
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib import colors
        
        return ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=config.pdf_title_font_size,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
    
    def _create_heading_style(self, styles):
        """Create custom heading style"""
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib import colors
        
        return ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=12,
            textColor=colors.darkblue
        )
    
    def _create_title_section(self, start_date: datetime, end_date: datetime, title_style) -> List:
        """Create title section"""
        from reportlab.platypus import Paragraph, Spacer
        
        title = f"Cash App Comprehensive Analysis Report - {start_date.strftime('%B %Y')}"
        return [
            Paragraph(title, title_style),
            Spacer(1, 12)
        ]
    
    def _create_executive_summary(self, month_data, styles) -> List:
        """Create executive summary section"""
        from reportlab.platypus import Paragraph, Spacer
        
        # Calculate summary stats
        income_data = month_data[month_data['Net_Amount'] > 0]
        expense_data = month_data[month_data['Net_Amount'] < 0]
        
        total_income = income_data['Net_Amount'].sum()
        total_expenses = expense_data['Net_Amount'].sum()
        net_cash_flow = total_income + total_expenses
        transaction_count = len(month_data)
        
        start_date = month_data['Date'].min()
        end_date = month_data['Date'].max()
        
        summary_text = f"""
        <b>Executive Summary</b><br/>
        <br/>
        Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}<br/>
        Total Transactions: {transaction_count}<br/>
        <br/>
        <b>Financial Summary:</b><br/>
        Total Income: ${total_income:,.2f}<br/>
        Total Expenses: ${abs(total_expenses):,.2f}<br/>
        Net Cash Flow: ${net_cash_flow:,.2f}<br/>
        <br/>
        <b>Analysis includes:</b><br/>
        • Comprehensive transaction analysis<br/>
        • Income trend analysis<br/>
        • Expense breakdown and patterns<br/>
        • Cash flow analysis<br/>
        • Interactive visualizations<br/>
        """
        
        return [
            Paragraph(summary_text, styles['Normal']),
            Spacer(1, 20)
        ]
    
    def _create_detailed_analysis(self, month_data, heading_style, styles) -> List:
        """Create detailed analysis tables"""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        
        story = []
        
        # Category Breakdown
        story.append(Paragraph("Category Breakdown", heading_style))
        
        expense_data = month_data[month_data['Net_Amount'] < 0]
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
        
        return story
    
    def _create_comprehensive_visualizations(self, start_date: datetime, end_date: datetime, heading_style) -> List:
        """Create comprehensive visualizations using existing analyzer methods"""
        from reportlab.platypus import Paragraph, Spacer, Image, PageBreak
        
        story = []
        story.append(Paragraph("Comprehensive Visual Analysis", heading_style))
        story.append(Spacer(1, 12))
        
        # Generate and add each visualization type
        chart_configs = [
            {
                'title': 'Overall Transaction Analysis Dashboard',
                'method': 'create_visualizations',
                'description': 'Complete overview of all transactions, categories, and trends'
            },
            {
                'title': 'Income Analysis',
                'method': 'create_income_visualizations', 
                'description': 'Detailed analysis of income patterns and trends'
            },
            {
                'title': 'Expense Analysis',
                'method': 'create_expense_visualizations',
                'description': 'Comprehensive expense breakdown and spending patterns'
            },
            {
                'title': 'Cash Flow Analysis',
                'method': 'create_cash_flow_visualizations',
                'description': 'Net cash flow trends and financial health indicators'
            }
        ]
        
        for i, chart_config in enumerate(chart_configs):
            try:
                # Add chart description
                story.append(Paragraph(f"<b>{chart_config['title']}</b>", heading_style))
                story.append(Paragraph(chart_config['description'], heading_style))
                story.append(Spacer(1, 12))
                
                # Generate chart using analyzer's existing methods
                method = getattr(self.analyzer, chart_config['method'])
                fig = method(start_date=start_date, end_date=end_date)
                
                # Save chart as temporary image
                chart_filename = f"chart_{chart_config['method']}_{start_date.strftime('%Y_%m')}.png"
                chart_path = config.get_temp_file_path(chart_filename)
                
                fig.savefig(chart_path, dpi=config.chart_dpi, bbox_inches='tight', facecolor='white')
                plt.close(fig)  # Important: close figure to free memory
                
                # Track temp file for cleanup
                self.temp_files.append(chart_path)
                  # Add chart to PDF
                story.append(Image(chart_path, 
                                 width=config.pdf_chart_width*INCH_UNIT, 
                                 height=config.pdf_chart_height*INCH_UNIT))
                story.append(Spacer(1, 20))
                
                # Add page break between charts (except for the last one)
                if i < len(chart_configs) - 1:
                    story.append(PageBreak())
                
                logger.info(f"Added {chart_config['title']} to PDF")
                
            except Exception as e:
                logger.error(f"Failed to generate {chart_config['title']}: {str(e)}")
                error_msg = f"Note: {chart_config['title']} could not be generated ({str(e)})"
                from reportlab.platypus import Paragraph
                story.append(Paragraph(error_msg, heading_style))
                story.append(Spacer(1, 20))
        
        return story
    
    @log_performance
    def generate_quick_pdf(self, output_path: Optional[str] = None, month_offset: int = 1) -> str:
        """
        Generate a quick PDF with just the main dashboard chart
        
        Args:
            output_path: Where to save the PDF
            month_offset: Number of months back from current
            
        Returns:
            Path to generated PDF file
        """
        return self.generate_comprehensive_pdf(
            output_path=output_path,
            month_offset=month_offset,
            include_all_charts=False
        )
