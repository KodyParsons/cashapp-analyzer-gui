import tkinter as tk
import sys
import os

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(__file__))

from gui.main_window import MainWindow

def main():
    """Main entry point for the Cash App Analyzer GUI"""
    # Try to use tkinterdnd2 for drag and drop if available
    try:
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
        print("Drag and drop functionality enabled")
    except ImportError:
        root = tk.Tk()
        print("Drag and drop functionality not available (tkinterdnd2 not installed)")
    
    # Set window icon if available
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    app = MainWindow(root)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()