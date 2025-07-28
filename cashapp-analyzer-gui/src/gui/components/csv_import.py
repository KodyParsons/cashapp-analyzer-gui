import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

class CSVImportFrame(ttk.Frame):
    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.csv_file_path = None
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title_label = ttk.Label(self, text="Import CSV File", font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
        
        # Drag and drop area
        self.drop_frame = tk.Frame(self, bg='lightblue', relief='solid', bd=2, height=100)
        self.drop_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky='ew')
        self.drop_frame.grid_propagate(False)
        
        # Drop label
        self.drop_label = tk.Label(
            self.drop_frame, 
            text="Drag and drop CSV file here\nor click to browse",
            bg='lightblue', 
            font=('Arial', 12)
        )
        self.drop_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Bind events for drag and drop (if tkinterdnd2 is available)
        if DND_AVAILABLE:
            try:
                self.drop_frame.drop_target_register(DND_FILES)
                self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)
            except:
                pass
        
        # Bind click event for browsing
        self.drop_frame.bind('<Button-1>', self.browse_file)
        self.drop_label.bind('<Button-1>', self.browse_file)
        
        # File path display
        self.file_path_var = tk.StringVar()
        self.file_path_label = ttk.Label(self, textvariable=self.file_path_var, foreground='blue')
        self.file_path_label.grid(row=2, column=0, columnspan=2, pady=5, sticky='w')
        
        # Browse button
        browse_button = ttk.Button(self, text="Browse File", command=self.browse_file)
        browse_button.grid(row=3, column=0, pady=10, sticky='w')
        
        # Clear button
        clear_button = ttk.Button(self, text="Clear", command=self.clear_file)
        clear_button.grid(row=3, column=1, pady=10, sticky='w')
        
        # Configure column weights
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
    
    def on_drop(self, event):
        """Handle file drop event"""
        try:
            files = self.tk.splitlist(event.data)
            if files:
                file_path = files[0]
                if file_path.lower().endswith('.csv'):
                    self.set_file_path(file_path)
                else:
                    messagebox.showerror("Error", "Please select a CSV file")
        except Exception as e:
            messagebox.showerror("Error", f"Drop error: {e}")
    
    def browse_file(self, event=None):
        """Open file browser to select CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.set_file_path(file_path)
    
    def set_file_path(self, file_path):
        """Set the selected file path"""
        self.csv_file_path = file_path
        self.file_path_var.set(f"Selected: {os.path.basename(file_path)}")
        self.drop_label.config(text=f"Selected: {os.path.basename(file_path)}")
        self.drop_frame.config(bg='lightgreen')
        self.drop_label.config(bg='lightgreen')
        
        # Call callback if provided
        if self.callback:
            self.callback(file_path)
    
    def clear_file(self):
        """Clear the selected file"""
        self.csv_file_path = None
        self.file_path_var.set("")
        self.drop_label.config(text="Drag and drop CSV file here\nor click to browse")
        self.drop_frame.config(bg='lightblue')
        self.drop_label.config(bg='lightblue')
        
        # Call callback with None
        if self.callback:
            self.callback(None)
    
    def get_file_path(self):
        """Get the currently selected file path"""
        return self.csv_file_path