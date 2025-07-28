import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import calendar

class DatePickerFrame(ttk.Frame):
    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.start_date = None
        self.end_date = None
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title_label = ttk.Label(self, text="Select Date Range", font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=4, pady=10, sticky='w')
        
        # Start date section
        start_label = ttk.Label(self, text="Start Date:", font=('Arial', 10, 'bold'))
        start_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        # Start date inputs
        self.start_month_var = tk.StringVar()
        self.start_day_var = tk.StringVar()
        self.start_year_var = tk.StringVar()
        
        start_month_combo = ttk.Combobox(self, textvariable=self.start_month_var, 
                                       values=list(calendar.month_name)[1:], width=10, state='readonly')
        start_month_combo.grid(row=2, column=0, padx=2, pady=5)
        start_month_combo.bind('<<ComboboxSelected>>', self.on_date_change)
        
        start_day_combo = ttk.Combobox(self, textvariable=self.start_day_var, 
                                     values=list(range(1, 32)), width=5, state='readonly')
        start_day_combo.grid(row=2, column=1, padx=2, pady=5)
        start_day_combo.bind('<<ComboboxSelected>>', self.on_date_change)
        
        current_year = datetime.now().year
        years = list(range(current_year - 10, current_year + 2))
        start_year_combo = ttk.Combobox(self, textvariable=self.start_year_var, 
                                      values=years, width=8, state='readonly')
        start_year_combo.grid(row=2, column=2, padx=2, pady=5)
        start_year_combo.bind('<<ComboboxSelected>>', self.on_date_change)
        
        # End date section
        end_label = ttk.Label(self, text="End Date:", font=('Arial', 10, 'bold'))
        end_label.grid(row=3, column=0, padx=5, pady=5, sticky='w')
        
        # End date inputs
        self.end_month_var = tk.StringVar()
        self.end_day_var = tk.StringVar()
        self.end_year_var = tk.StringVar()
        
        end_month_combo = ttk.Combobox(self, textvariable=self.end_month_var, 
                                     values=list(calendar.month_name)[1:], width=10, state='readonly')
        end_month_combo.grid(row=4, column=0, padx=2, pady=5)
        end_month_combo.bind('<<ComboboxSelected>>', self.on_date_change)
        
        end_day_combo = ttk.Combobox(self, textvariable=self.end_day_var, 
                                   values=list(range(1, 32)), width=5, state='readonly')
        end_day_combo.grid(row=4, column=1, padx=2, pady=5)
        end_day_combo.bind('<<ComboboxSelected>>', self.on_date_change)
        
        end_year_combo = ttk.Combobox(self, textvariable=self.end_year_var, 
                                    values=years, width=8, state='readonly')
        end_year_combo.grid(row=4, column=2, padx=2, pady=5)
        end_year_combo.bind('<<ComboboxSelected>>', self.on_date_change)
        
        # Quick select buttons
        quick_label = ttk.Label(self, text="Quick Select:", font=('Arial', 10, 'bold'))
        quick_label.grid(row=5, column=0, padx=5, pady=(15, 5), sticky='w')
        
        button_frame = ttk.Frame(self)
        button_frame.grid(row=6, column=0, columnspan=4, pady=5, sticky='ew')
        
        ttk.Button(button_frame, text="Last Month", 
                  command=self.set_last_month).pack(side='left', padx=2)
        ttk.Button(button_frame, text="Last 3 Months", 
                  command=lambda: self.set_quick_range(3)).pack(side='left', padx=2)
        ttk.Button(button_frame, text="Last 6 Months", 
                  command=lambda: self.set_quick_range(6)).pack(side='left', padx=2)
        ttk.Button(button_frame, text="Last Year", 
                  command=lambda: self.set_quick_range(12)).pack(side='left', padx=2)
        ttk.Button(button_frame, text="All Time", 
                  command=self.set_all_time).pack(side='left', padx=2)
        
        # Current selection display
        self.selection_var = tk.StringVar()
        self.selection_label = ttk.Label(self, textvariable=self.selection_var, 
                                       font=('Arial', 9), foreground='blue')
        self.selection_label.grid(row=7, column=0, columnspan=4, pady=10, sticky='w')
        
        # Clear and set default
        clear_button = ttk.Button(self, text="Clear Selection", command=self.clear_dates)
        clear_button.grid(row=8, column=0, pady=5, sticky='w')
        
        # Set default to last 6 months after a short delay to ensure parent is initialized
        self.after(100, lambda: self.set_quick_range(6))
    
    def on_date_change(self, event=None):
        """Handle date change events"""
        try:
            # Validate and set start date
            if (self.start_month_var.get() and self.start_day_var.get() and 
                self.start_year_var.get()):
                month_num = list(calendar.month_name).index(self.start_month_var.get())
                self.start_date = datetime(
                    int(self.start_year_var.get()),
                    month_num,
                    int(self.start_day_var.get())
                )
            
            # Validate and set end date
            if (self.end_month_var.get() and self.end_day_var.get() and 
                self.end_year_var.get()):
                month_num = list(calendar.month_name).index(self.end_month_var.get())
                self.end_date = datetime(
                    int(self.end_year_var.get()),
                    month_num,
                    int(self.end_day_var.get())
                )
            
            self.update_display()
            
        except (ValueError, IndexError):
            # Invalid date combination
            pass
    
    def set_last_month(self):
        """Set date range to the complete previous month"""
        today = datetime.now()
        
        # Get first day of current month
        first_day_current_month = today.replace(day=1)
        
        # Get last day of previous month
        end_date = first_day_current_month - timedelta(days=1)
        
        # Get first day of previous month
        start_date = end_date.replace(day=1)
        
        self.set_dates(start_date, end_date)
    
    def set_quick_range(self, months):
        """Set a quick date range"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        self.set_dates(start_date, end_date)
    
    def set_all_time(self):
        """Clear date restrictions for all-time analysis"""
        self.clear_dates()
        self.selection_var.set("All available data will be analyzed")
    
    def set_dates(self, start_date, end_date):
        """Set specific start and end dates"""
        self.start_date = start_date
        self.end_date = end_date
        
        # Update UI
        self.start_month_var.set(calendar.month_name[start_date.month])
        self.start_day_var.set(str(start_date.day))
        self.start_year_var.set(str(start_date.year))
        
        self.end_month_var.set(calendar.month_name[end_date.month])
        self.end_day_var.set(str(end_date.day))
        self.end_year_var.set(str(end_date.year))
        
        self.update_display()
    
    def clear_dates(self):
        """Clear all date selections"""
        self.start_date = None
        self.end_date = None
        
        # Clear UI
        self.start_month_var.set("")
        self.start_day_var.set("")
        self.start_year_var.set("")
        
        self.end_month_var.set("")
        self.end_day_var.set("")
        self.end_year_var.set("")
        
        self.selection_var.set("No date range selected")
        
        if self.callback:
            self.callback(None, None)
    
    def update_display(self):
        """Update the display of current selection"""
        if self.start_date and self.end_date:
            if self.start_date <= self.end_date:
                self.selection_var.set(
                    f"Selected: {self.start_date.strftime('%Y-%m-%d')} to "
                    f"{self.end_date.strftime('%Y-%m-%d')}"
                )
                if self.callback:
                    self.callback(self.start_date, self.end_date)
            else:
                self.selection_var.set("Error: Start date must be before end date")
        else:
            self.selection_var.set("Please select both start and end dates")
    
    def get_date_range(self):
        """Get the currently selected date range"""
        return self.start_date, self.end_date