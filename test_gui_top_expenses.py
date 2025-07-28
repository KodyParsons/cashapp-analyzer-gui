#!/usr/bin/env python3
"""
Test the GUI Top Expenses tab functionality
"""

import sys
import os
import tempfile
import tkinter as tk
from tkinter import ttk

# Add the src directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'cashapp-analyzer-gui', 'src'))

try:
    from gui.main_window import MainWindow
    print("✓ Successfully imported MainWindow")
except ImportError as e:
    print(f"✗ Failed to import MainWindow: {e}")
    sys.exit(1)

def test_gui_top_expenses_tab():
    """Test the GUI top expenses tab functionality"""
    print("\n" + "="*60)
    print("TESTING GUI TOP EXPENSES TAB")
    print("="*60)
    
    try:
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide the window for testing
        
        # Create main window
        app = MainWindow(root)
        print("✓ Successfully created MainWindow")
        
        # Check if the top expenses tab exists
        tab_texts = []
        for i in range(app.notebook.index("end")):
            tab_texts.append(app.notebook.tab(i, "text"))
        
        print(f"Available tabs: {tab_texts}")
        
        if "Top Expenses" in tab_texts:
            print("✓ Top Expenses tab found")
        else:
            print("✗ Top Expenses tab not found")
            return False
        
        # Check if the top expenses frame exists
        if hasattr(app, 'top_expenses_frame'):
            print("✓ Top expenses frame exists")
        else:
            print("✗ Top expenses frame not found")
            return False
        
        # Check if the display method exists
        if hasattr(app, '_display_top_expenses_visualizations'):
            print("✓ _display_top_expenses_visualizations method exists")
        else:
            print("✗ _display_top_expenses_visualizations method not found")
            return False
        
        # Test method signature
        import inspect
        sig = inspect.signature(app._display_top_expenses_visualizations)
        params = list(sig.parameters.keys())
        if 'fig' in params:
            print("✓ _display_top_expenses_visualizations has correct signature")
        else:
            print(f"✗ _display_top_expenses_visualizations has wrong signature: {params}")
            return False
        
        print("✓ All GUI top expenses components are properly configured")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Error during GUI testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gui_top_expenses_tab()
    if success:
        print("\n✅ GUI TOP EXPENSES TAB TEST PASSED!")
    else:
        print("\n❌ GUI TOP EXPENSES TAB TEST FAILED!")
        sys.exit(1)
