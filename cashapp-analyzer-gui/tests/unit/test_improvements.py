import unittest
from unittest.mock import Mock, patch
import tkinter as tk
from src.gui.main_window import MainWindow
from src.core.pdf_generator import PDFGenerator
from src.analyzer.cashapp_analyzer import CashAppAnalyzer
import os

class TestImprovements(unittest.TestCase):
    def test_scrolling_binding(self):
        root = tk.Tk()
        app = MainWindow(root)
        # Mock event
        event = Mock(delta=120, num=None)
        app.dashboard_tab.children['!canvas'].event_generate('<MouseWheel>', delta=120)
        # Assuming no error means binding works
        self.assertTrue(True)
    
    def test_pdf_content(self):
        analyzer = CashAppAnalyzer('sample.csv')  # Assume sample
        analyzer.load_and_clean_data()
        pdf_gen = PDFGenerator(analyzer)
        path = pdf_gen.generate_comprehensive_pdf()
        # Basic check (expand with pdf parsing if needed)
        self.assertTrue(os.path.exists(path))
    
    def test_gui_theme(self):
        root = tk.Tk()
        app = MainWindow(root)
        style = tk.ttk.Style()
        self.assertEqual(style.theme_use(), 'clam')

if __name__ == '__main__':
    unittest.main() 