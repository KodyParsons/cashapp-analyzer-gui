import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import os

# Import pandas here instead of in methods to avoid repeated imports
try:
    import pandas as pd
except ImportError:
    pd = None

# Add the src directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from gui.components.csv_import import CSVImportFrame
from gui.components.date_picker import DatePickerFrame

# Import analyzer with error handling
try:
    from analyzer.cashapp_analyzer import CashAppAnalyzer
    ANALYZER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: CashApp analyzer not available: {e}")
    CashAppAnalyzer = None
    ANALYZER_AVAILABLE = False

class MainWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Cash App Transaction Analyzer")
        self.master.geometry("1000x700")
        self.master.state('zoomed')  # Maximize window on Windows
        
        # Variables
        self.csv_file_path = None
        self.start_date = None
        self.end_date = None
        self.analyzer = None
        self.current_figure = None
        self.report_type_var = tk.StringVar(value="Summary Report")  # New variable for report type
        
        self.setup_ui()
    
    def setup_ui(self):
        # Create main container with notebook for tabs
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Setup tab
        self.setup_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.setup_tab, text="Setup & Analysis")
        
        # Results tab (text summary)
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text="Summary Report")
        
        # Dashboard tab (consolidated visualizations)
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        
        # Data viewer tab
        self.data_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.data_tab, text="Transaction Data")
        
        self.setup_setup_tab()
        self.setup_results_tab()
        self.setup_dashboard_tab()
        self.setup_data_tab()
    
    def setup_setup_tab(self):
        # Main frame with scrollbar
        canvas = tk.Canvas(self.setup_tab)
        scrollbar = ttk.Scrollbar(self.setup_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title
        title_label = ttk.Label(scrollable_frame, text="Cash App Transaction Analyzer", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=20)
        
        # Welcome message
        welcome_text = ttk.Label(scrollable_frame, text="Welcome! Follow the steps below to analyze your Cash App transactions.", 
                                 font=('Arial', 12))
        welcome_text.pack(pady=10)
        
        # CSV Import Section
        csv_frame = ttk.LabelFrame(scrollable_frame, text="Step 1: Import CSV File", padding=10)
        csv_frame.pack(fill='x', padx=20, pady=10)
        
        self.csv_import = CSVImportFrame(csv_frame, callback=self.on_csv_selected)
        self.csv_import.pack(fill='x')
        
        # Date Range Section
        date_frame = ttk.LabelFrame(scrollable_frame, text="Step 2: Select Date Range", padding=10)
        date_frame.pack(fill='x', padx=20, pady=10)
        
        self.date_picker = DatePickerFrame(date_frame, callback=self.on_date_range_selected)
        self.date_picker.pack(fill='x')
        
        # Analysis Section
        analysis_frame = ttk.LabelFrame(scrollable_frame, text="Step 3: Run Analysis", padding=10)
        analysis_frame.pack(fill='x', padx=20, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(analysis_frame, variable=self.progress_var, 
                                          mode='indeterminate')
        self.progress_bar.pack(fill='x', pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to analyze")
        self.status_label = ttk.Label(analysis_frame, textvariable=self.status_var)
        self.status_label.pack(pady=5)
        
        # Report type selection and generate button
        button_frame = ttk.Frame(analysis_frame)
        button_frame.pack(pady=10)
        
        report_combo = ttk.Combobox(button_frame, textvariable=self.report_type_var,
                                    values=["Summary Report", "Comprehensive PDF Report"], 
                                    state='readonly', width=30)
        report_combo.pack(side='left', padx=5)
        
        self.generate_button = ttk.Button(button_frame, text="Generate", 
                                        command=self.generate_selected_report, state='disabled')
        self.generate_button.pack(side='left', padx=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def setup_results_tab(self):
        # Results text area
        self.results_text = scrolledtext.ScrolledText(self.results_tab, wrap=tk.WORD, 
                                                     font=('Courier', 10))
        self.results_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Export button
        export_frame = ttk.Frame(self.results_tab)
        export_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(export_frame, text="Export Report", 
                  command=self.export_report).pack(side='right')
    
    def setup_dashboard_tab(self):
        # Scrollable frame for dashboard
        canvas = tk.Canvas(self.dashboard_tab)
        scrollbar = ttk.Scrollbar(self.dashboard_tab, orient="vertical", command=canvas.yview)
        self.dashboard_frame = ttk.Frame(canvas)
        
        self.dashboard_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.dashboard_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Placeholder label
        self.dashboard_placeholder = ttk.Label(self.dashboard_frame, 
                                             text="Visualizations will appear here after analysis",
                                             font=('Arial', 12))
        self.dashboard_placeholder.pack(expand=True, pady=20)

    def setup_data_tab(self):
        # Data viewer with search and filtering
        data_container = ttk.Frame(self.data_tab)
        data_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Search and filter frame
        filter_frame = ttk.Frame(data_container)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        # Search box
        ttk.Label(filter_frame, text="Search:").pack(side='left', padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.filter_data)
        
        # Category filter
        ttk.Label(filter_frame, text="Category:").pack(side='left', padx=(10, 5))
        self.category_filter_var = tk.StringVar()
        self.category_filter = ttk.Combobox(filter_frame, textvariable=self.category_filter_var, 
                                          values=['All'], width=20, state='readonly')
        self.category_filter.pack(side='left', padx=(0, 10))
        self.category_filter.bind('<<ComboboxSelected>>', self.filter_data)
        self.category_filter.set('All')
        
        # Clear filters button
        ttk.Button(filter_frame, text="Clear Filters", 
                  command=self.clear_filters).pack(side='left', padx=(10, 0))
        
        # Export data button
        ttk.Button(filter_frame, text="Export Data", 
                  command=self.export_data).pack(side='right', padx=(0, 10))
        
        # Results count label
        self.data_count_var = tk.StringVar()
        self.data_count_label = ttk.Label(filter_frame, textvariable=self.data_count_var)
        self.data_count_label.pack(side='right', padx=(0, 20))
        
        # Treeview for data display
        columns = ('Date', 'Description', 'Amount', 'Category', 'Month')
        self.data_tree = ttk.Treeview(data_container, columns=columns, show='headings', height=20)
        
        # Configure column headings and widths
        self.data_tree.heading('Date', text='Date')
        self.data_tree.heading('Description', text='Description')
        self.data_tree.heading('Amount', text='Amount')
        self.data_tree.heading('Category', text='Category')
        self.data_tree.heading('Month', text='Month')
        
        self.data_tree.column('Date', width=100)
        self.data_tree.column('Description', width=300)
        self.data_tree.column('Amount', width=100)
        self.data_tree.column('Category', width=150)
        self.data_tree.column('Month', width=100)
        
        # Scrollbars for treeview
        data_scrollbar_v = ttk.Scrollbar(data_container, orient='vertical', command=self.data_tree.yview)
        data_scrollbar_h = ttk.Scrollbar(data_container, orient='horizontal', command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=data_scrollbar_v.set, xscrollcommand=data_scrollbar_h.set)
        
        # Pack treeview and scrollbars
        self.data_tree.pack(side='left', fill='both', expand=True)
        data_scrollbar_v.pack(side='right', fill='y')
        data_scrollbar_h.pack(side='bottom', fill='x')
        
        # Placeholder label (will be hidden when data is loaded)
        self.data_placeholder = ttk.Label(data_container, 
                                        text="Transaction data will appear here after analysis",
                                        font=('Arial', 12))
        self.data_placeholder.place(relx=0.5, rely=0.5, anchor='center')
    
    def on_csv_selected(self, file_path):
        """Handle CSV file selection"""
        self.csv_file_path = file_path
        # Only update button state if it exists
        if hasattr(self, 'generate_button'):
            self.update_generate_button_state()
        if file_path and hasattr(self, 'status_var'):
            self.status_var.set(f"CSV loaded: {os.path.basename(file_path)}")
        elif hasattr(self, 'status_var'):
            self.status_var.set("No CSV selected")
    
    def on_date_range_selected(self, start_date, end_date):
        """Handle date range selection"""
        self.start_date = start_date
        self.end_date = end_date
        # Only update button state if it exists
        if hasattr(self, 'generate_button'):
            self.update_generate_button_state()
        if start_date and end_date and hasattr(self, 'status_var'):
            self.status_var.set(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    def update_generate_button_state(self):
        """Enable/disable generate button based on requirements"""
        if hasattr(self, 'generate_button'):
            if self.csv_file_path:
                self.generate_button.config(state='normal')
            else:
                self.generate_button.config(state='disabled')
    
    def generate_report(self):
        """Generate the analysis report"""
        if not self.csv_file_path:
            messagebox.showerror("Error", "Please select a CSV file")
            return
        
        # Disable button and start progress bar
        self.generate_button.config(state='disabled')
        self.progress_bar.start()
        self.status_var.set("Analyzing data...")
        
        # Run analysis in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self._run_analysis)
        thread.daemon = True
        thread.start()
    
    def _run_analysis(self):
        """Run the analysis in a separate thread"""
        try:
            # Check if analyzer is available
            if not ANALYZER_AVAILABLE:
                error_msg = "CashApp analyzer not available due to missing dependencies (pandas/numpy)"
                self.master.after(0, lambda: self._on_analysis_error(error_msg))
                return
                
            # Create analyzer
            self.analyzer = CashAppAnalyzer(self.csv_file_path)
            
            # Update status
            self.master.after(0, lambda: self.status_var.set("Loading and cleaning data..."))
            
            # Load and process data (without creating visualizations yet)
            self.analyzer.load_and_clean_data()
            self.analyzer.categorize_transactions()
            
            # Generate monthly summary
            monthly_summary = self.analyzer.generate_monthly_summary(
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            # Generate text report
            report = self.analyzer.generate_report(
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            # Update GUI in main thread (without figure for now)
            self.master.after(0, lambda: self._on_analysis_complete(self.analyzer.df, None, report))
            
        except Exception as e:
            # Handle errors
            error_msg = str(e)
            self.master.after(0, lambda: self._on_analysis_error(error_msg))
    
    def _on_analysis_complete(self, df, fig, report):
        """Handle successful analysis completion"""
        # Stop progress bar
        self.progress_bar.stop()
        self.status_var.set("Creating visualizations...")
        
        # Display results
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, report)
        
        # Populate data viewer
        self.populate_data_viewer()
        
        # Create visualizations in main thread
        try:
            # Create all figures
            income_fig = self.analyzer.create_income_visualizations(
                start_date=self.start_date,
                end_date=self.end_date
            )
            expense_fig = self.analyzer.create_expense_visualizations(
                start_date=self.start_date,
                end_date=self.end_date
            )
            cash_flow_fig = self.analyzer.create_cash_flow_visualizations(
                start_date=self.start_date,
                end_date=self.end_date
            )
            top_expenses_fig = self.analyzer.create_top_expenses_visualizations(
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            # Display in dashboard
            self._display_dashboard_visualizations([
                ("Income Analysis", income_fig),
                ("Expense Analysis", expense_fig),
                ("Cash Flow Analysis", cash_flow_fig),
                ("Top Expenses", top_expenses_fig)
            ])
            
        except Exception as e:
            print(f"Error creating visualizations: {e}")
            import traceback
            traceback.print_exc()
            # Show error in dashboard
            for widget in self.dashboard_frame.winfo_children():
                widget.destroy()
            error_label = ttk.Label(self.dashboard_frame, 
                                  text=f"Error creating visualizations: {str(e)}")
            error_label.pack(expand=True)
        
        # Final status update
        self.status_var.set("Analysis complete!")
        self.generate_button.config(state='normal')
        
        # Switch to results tab
        self.notebook.select(1)
        
        messagebox.showinfo("Success", "Analysis completed successfully! Check all tabs for detailed insights.")
    
    def _on_analysis_error(self, error_message):
        """Handle analysis errors"""
        self.progress_bar.stop()
        self.status_var.set("Analysis failed")
        self.generate_button.config(state='normal')
        
        messagebox.showerror("Analysis Error", f"An error occurred during analysis:\n\n{error_message}")
    
    def _display_dashboard_visualizations(self, viz_list):
        """Display all visualizations in the scrollable dashboard tab"""
        # Import matplotlib here to avoid startup errors
        try:
            import matplotlib
            if matplotlib.get_backend() != 'TkAgg':
                matplotlib.use('TkAgg')
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
        except ImportError:
            error_label = ttk.Label(self.dashboard_frame, text="Matplotlib not available for visualizations")
            error_label.pack(pady=20)
            return
        
        # Clear existing content
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()
        
        for title, fig in viz_list:
            if fig is None:
                continue
            
            # Section frame
            section_frame = ttk.LabelFrame(self.dashboard_frame, text=title, padding=10)
            section_frame.pack(fill='x', pady=10, expand=True)
            
            # Create canvas
            canvas = FigureCanvasTkAgg(fig, section_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
            # Add toolbar
            toolbar_frame = ttk.Frame(section_frame)
            toolbar_frame.pack(fill='x')
            try:
                toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
                toolbar.update()
            except Exception as e:
                print(f"Could not create navigation toolbar: {e}")

    def export_report(self):
        """Export the analysis report to a text file"""
        if not hasattr(self, 'analyzer') or not self.analyzer:
            messagebox.showwarning("Warning", "No analysis results to export")
            return
        
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Report As"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.results_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Report exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report:\n{e}")
    
    def generate_pdf_report(self):
        """Generate PDF report for the prior month's activities"""
        if not self.csv_file_path:
            messagebox.showerror("Error", "Please select a CSV file")
            return
        
        # Disable button and start progress bar
        self.generate_button.config(state='disabled')
        self.progress_bar.start()
        self.status_var.set("Generating PDF report...")
        
        # Run PDF generation in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self._run_pdf_generation)
        thread.daemon = True
        thread.start()
    
    def _run_pdf_generation(self):
        """Run PDF generation in a separate thread"""
        try:
            # Create analyzer if not already created
            if not hasattr(self, 'analyzer') or not self.analyzer:
                self.analyzer = CashAppAnalyzer(self.csv_file_path)
                self.analyzer.load_and_clean_data()
                self.analyzer.categorize_transactions()
            
            # Update status
            self.master.after(0, lambda: self.status_var.set("Creating comprehensive PDF report..."))
            
            # Try comprehensive PDF generation first (defaults to prior month)
            pdf_path = self.analyzer.generate_comprehensive_pdf_report(
                include_all_charts=True  # Include all 4 chart types
            )
            
            # Success callback
            self.master.after(0, lambda: self._on_pdf_complete(pdf_path))
            
        except ValueError as ve:
            # Handle specific data issues (like no data for the period)
            error_msg = str(ve)
            if "No data found for the period" in error_msg:
                self.master.after(0, lambda: self._on_pdf_error(f"No data available for the requested time period. {error_msg}"))
            else:
                # Try fallback to original PDF generation
                try:
                    self.master.after(0, lambda: self.status_var.set("Trying fallback PDF generation..."))
                    pdf_path = self.analyzer.generate_pdf_report()  # Use original method as fallback
                    self.master.after(0, lambda: self._on_pdf_complete(pdf_path))
                except Exception as fallback_error:
                    # Handle errors  
                    self.master.after(0, lambda: self._on_pdf_error(f"PDF generation failed: {error_msg}. Fallback also failed: {str(fallback_error)}"))
        except Exception as e:
            # Try fallback to original PDF generation for other errors
            try:
                self.master.after(0, lambda: self.status_var.set("Trying fallback PDF generation..."))
                pdf_path = self.analyzer.generate_pdf_report()  # Use original method as fallback
                self.master.after(0, lambda: self._on_pdf_complete(pdf_path))
            except Exception as fallback_error:
                # Handle errors  
                self.master.after(0, lambda: self._on_pdf_error(f"PDF generation failed: {str(e)}. Fallback also failed: {str(fallback_error)}"))
    
    def _on_pdf_complete(self, pdf_path):
        """Handle successful PDF generation"""
        # Stop progress bar
        self.progress_bar.stop()
        self.generate_button.config(state='normal')
        self.status_var.set("PDF report generated successfully!")
        
        # Show success message with option to open
        from tkinter import messagebox
        result = messagebox.askyesno(
            "PDF Generated", 
            f"PDF report saved to:\n{pdf_path}\n\nWould you like to open it?",
            icon='question'
        )
        
        if result:
            # Try to open the PDF
            try:
                import os
                os.startfile(pdf_path)  # Windows
            except:
                try:
                    import subprocess
                    subprocess.run(['open', pdf_path])  # macOS
                except:
                    messagebox.showinfo("PDF Location", 
                                      f"Please open the PDF manually at:\n{pdf_path}")
    
    def _on_pdf_error(self, error_message):
        """Handle PDF generation error"""
        # Stop progress bar and re-enable button
        self.progress_bar.stop()
        self.generate_button.config(state='normal')
        self.status_var.set("PDF generation failed")
        
        messagebox.showerror("PDF Generation Error", 
                           f"Failed to generate PDF report:\n{error_message}")
    
    def filter_data(self, event=None):
        """Filter the data based on search and category selection"""
        if not hasattr(self, 'analyzer') or not self.analyzer or self.analyzer.df is None:
            return
        
        # Get filter values
        search_text = self.search_var.get().lower()
        category_filter = self.category_filter_var.get()
        
        # Start with all data
        filtered_df = self.analyzer.df.copy()
        
        # Apply search filter
        if search_text:
            filtered_df = filtered_df[
                filtered_df['Description'].str.lower().str.contains(search_text, na=False)
            ]
        
        # Apply category filter
        if category_filter and category_filter != 'All':
            filtered_df = filtered_df[filtered_df['Category'] == category_filter]
        
        # Apply date range filter if set
        if hasattr(self, 'start_date') and hasattr(self, 'end_date'):
            if self.start_date and self.end_date:
                mask = (filtered_df['Date'] >= self.start_date) & (filtered_df['Date'] <= self.end_date)
                filtered_df = filtered_df.loc[mask]
        
        self.populate_data_tree(filtered_df)
    
    def clear_filters(self):
        """Clear all filters and show all data"""
        self.search_var.set('')
        self.category_filter_var.set('All')
        self.filter_data()
    
    def export_data(self):
        """Export the currently filtered data to CSV"""
        if not hasattr(self, 'analyzer') or not self.analyzer:
            messagebox.showwarning("Warning", "No data to export")
            return
        
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Filtered Data"
        )
        
        if file_path:
            try:
                # Get currently filtered data
                self.filter_data()  # Apply current filters
                
                # Get the data from the tree view
                tree_data = []
                for child in self.data_tree.get_children():
                    values = self.data_tree.item(child)['values']
                    tree_data.append(values)
                
                # Create DataFrame from tree data
                df_export = pd.DataFrame(tree_data, columns=['Date', 'Description', 'Amount', 'Category', 'Month'])
                df_export.to_csv(file_path, index=False)
                
                messagebox.showinfo("Success", f"Data exported successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data:\n{str(e)}")
    
    def populate_data_tree(self, df):
        """Populate the data tree with transaction data"""
        # Clear existing data
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # Hide placeholder
        self.data_placeholder.place_forget()
        
        # Sort by date (most recent first)
        df_sorted = df.sort_values('Date', ascending=False)
        
        # Add data to tree
        for _, row in df_sorted.iterrows():
            # Format amount with color coding
            amount = f"${row['Net_Amount']:,.2f}"
            
            # Format date
            date_str = row['Date'].strftime('%Y-%m-%d') if pd.notna(row['Date']) else 'N/A'
            
            # Insert row
            # Use safe access to Description column
            description_text = ''
            if 'Description' in df_sorted.columns:
                description_text = str(row['Description'])
            elif 'Notes' in df_sorted.columns:
                description_text = str(row['Notes'])
            else:
                description_text = 'N/A'
            
            # Truncate description if too long
            if len(description_text) > 50:
                description_text = description_text[:50] + '...'
            
            item = self.data_tree.insert('', 'end', values=(
                date_str,
                description_text,
                amount,
                row['Category'],
                row['Month_Year']
            ))
            
            # Color code based on amount
            if row['Net_Amount'] < 0:
                self.data_tree.set(item, 'Amount', f"-${abs(row['Net_Amount']):,.2f}")
                # Note: Treeview styling would require additional configuration
            else:
                self.data_tree.set(item, 'Amount', f"${row['Net_Amount']:,.2f}")
        
        # Update count
        self.data_count_var.set(f"Showing {len(df_sorted)} transactions")
    
    def populate_data_viewer(self):
        """Populate the data viewer with transaction data"""
        if not hasattr(self, 'analyzer') or not self.analyzer or self.analyzer.df is None:
            return
        
        # Update category filter options
        categories = ['All'] + sorted(self.analyzer.df['Category'].unique().tolist())
        self.category_filter['values'] = categories
        
        # Populate tree with all data
        self.populate_data_tree(self.analyzer.df)

    def generate_selected_report(self):
        report_type = self.report_type_var.get()
        if report_type == "Summary Report":
            self.generate_report()
        elif report_type == "Comprehensive PDF Report":
            self.generate_pdf_report()

def main():
    # Try to use tkinterdnd2 for drag and drop if available
    try:
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
    except ImportError:
        root = tk.Tk()
    
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()