import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import calendar

from tkcalendar import Calendar

class DatePickerFrame(ttk.Frame):
    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.start_date = None
        self.end_date = None
        self.range_type_var = tk.StringVar(value="Last 6 Months")  # Default to Last 6 Months
        self.manual_enabled = False
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title_label = ttk.Label(self, text="Select Date Range", font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=4, pady=10, sticky='w')
        
        # Predefined range dropdown
        range_label = ttk.Label(self, text="Quick Select:", font=('Arial', 10, 'bold'))
        range_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        range_combo = ttk.Combobox(self, textvariable=self.range_type_var,
                                   values=["Custom", "Last Month", "Last 3 Months", "Last 6 Months", "Last Year", "All Time"],
                                   state='readonly', width=20)
        range_combo.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky='w')
        range_combo.bind('<<ComboboxSelected>>', self.on_range_selected)
        
        # Start date section
        self.start_label = ttk.Label(self, text="Start Date:", font=('Arial', 10, 'bold'))
        self.start_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        
        # Start date inputs
        self.start_month_var = tk.StringVar()
        self.start_day_var = tk.StringVar()
        self.start_year_var = tk.StringVar()
        
        self.start_month_combo = ttk.Combobox(self, textvariable=self.start_month_var, 
                                             values=list(calendar.month_name)[1:], width=10, state='readonly')
        self.start_month_combo.grid(row=3, column=0, padx=2, pady=5)
        self.start_month_combo.bind('<<ComboboxSelected>>', self.on_date_change)
        
        self.start_day_combo = ttk.Combobox(self, textvariable=self.start_day_var, 
                                           values=list(range(1, 32)), width=5, state='readonly')
        self.start_day_combo.grid(row=3, column=1, padx=2, pady=5)
        self.start_day_combo.bind('<<ComboboxSelected>>', self.on_date_change)
        
        current_year = datetime.now().year
        years = list(range(current_year - 10, current_year + 2))
        self.start_year_combo = ttk.Combobox(self, textvariable=self.start_year_var, 
                                            values=years, width=8, state='readonly')
        self.start_year_combo.grid(row=3, column=2, padx=2, pady=5)
        self.start_year_combo.bind('<<ComboboxSelected>>', self.on_date_change)
        
        # End date section
        self.end_label = ttk.Label(self, text="End Date:", font=('Arial', 10, 'bold'))
        self.end_label.grid(row=4, column=0, padx=5, pady=5, sticky='w')
        
        # End date inputs
        self.end_month_var = tk.StringVar()
        self.end_day_var = tk.StringVar()
        self.end_year_var = tk.StringVar()
        
        self.end_month_combo = ttk.Combobox(self, textvariable=self.end_month_var, 
                                           values=list(calendar.month_name)[1:], width=10, state='readonly')
        self.end_month_combo.grid(row=5, column=0, padx=2, pady=5)
        self.end_month_combo.bind('<<ComboboxSelected>>', self.on_date_change)
        
        self.end_day_combo = ttk.Combobox(self, textvariable=self.end_day_var, 
                                         values=list(range(1, 32)), width=5, state='readonly')
        self.end_day_combo.grid(row=5, column=1, padx=2, pady=5)
        self.end_day_combo.bind('<<ComboboxSelected>>', self.on_date_change)
        
        self.end_year_combo = ttk.Combobox(self, textvariable=self.end_year_var, 
                                          values=years, width=8, state='readonly')
        self.end_year_combo.grid(row=5, column=2, padx=2, pady=5)
        self.end_year_combo.bind('<<ComboboxSelected>>', self.on_date_change)
        
        # Current selection display
        self.selection_var = tk.StringVar()
        self.selection_label = ttk.Label(self, textvariable=self.selection_var, 
                                       font=('Arial', 9), foreground='blue')
        self.selection_label.grid(row=6, column=0, columnspan=4, pady=10, sticky='w')
        
        # Clear button
        clear_button = ttk.Button(self, text="Clear Selection", command=self.clear_dates)
        clear_button.grid(row=7, column=0, pady=5, sticky='w')
        
        # Calendar buttons
        start_cal_btn = ttk.Button(self, text="📅 Start", command=self.show_start_calendar, width=8)
        start_cal_btn.grid(row=3, column=3, padx=5, pady=5)
        
        end_cal_btn = ttk.Button(self, text="📅 End", command=self.show_end_calendar, width=8)
        end_cal_btn.grid(row=5, column=3, padx=5, pady=5)
        
        # Set default to last 6 months
        self.after(100, self.on_range_selected)
        
        # Initially disable manual pickers
        self.toggle_manual_pickers(False)
    
    def toggle_manual_pickers(self, enable):
        state = 'normal' if enable else 'disabled'
        self.start_month_combo.config(state=state)
        self.start_day_combo.config(state=state)
        self.start_year_combo.config(state=state)
        self.end_month_combo.config(state=state)
        self.end_day_combo.config(state=state)
        self.end_year_combo.config(state=state)
        self.manual_enabled = enable

    def on_range_selected(self, event=None):
        range_type = self.range_type_var.get()
        if range_type == "Custom":
            self.toggle_manual_pickers(True)
            self.clear_dates()
        else:
            self.toggle_manual_pickers(False)
            if range_type == "Last Month":
                self.set_last_month()
            elif range_type == "Last 3 Months":
                self.set_quick_range(3)
            elif range_type == "Last 6 Months":
                self.set_quick_range(6)
            elif range_type == "Last Year":
                self.set_quick_range(12)
            elif range_type == "All Time":
                self.set_all_time()
    
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

    def show_start_calendar(self):
        self.show_calendar(is_start=True)
    
    def show_end_calendar(self):
        self.show_calendar(is_start=False)
    
    def show_calendar(self, is_start):
        top = tk.Toplevel(self)
        top.title("Select Date")
        
        cal = Calendar(top, selectmode='day', year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
        cal.pack(pady=10)
        
        def select_date():
            selected = cal.get_date()
            try:
                date_obj = datetime.strptime(selected, '%m/%d/%y')
                if is_start:
                    self.start_date = date_obj
                    self.start_month_var.set(calendar.month_name[date_obj.month])
                    self.start_day_var.set(str(date_obj.day))
                    self.start_year_var.set(str(date_obj.year))
                else:
                    self.end_date = date_obj
                    self.end_month_var.set(calendar.month_name[date_obj.month])
                    self.end_day_var.set(str(date_obj.day))
                    self.end_year_var.set(str(date_obj.year))
                self.update_display()
            except ValueError:
                pass
            top.destroy()
        
        ttk.Button(top, text="Select", command=select_date).pack(pady=5)