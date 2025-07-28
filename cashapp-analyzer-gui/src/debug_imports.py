"""Debug script to check import issues"""
import sys
import os

print("Current working directory:", os.getcwd())
print("Python path:", sys.path)
print()

try:
    from utils.config import config
    from utils.logger import logger, log_performance
    print("✅ Utils import successful")
    print(f"Config: {config}")
    print(f"Logger: {logger}")
    UTILS_AVAILABLE = True
except ImportError as e:
    print(f"❌ Utils import failed: {e}")
    UTILS_AVAILABLE = False

print(f"UTILS_AVAILABLE: {UTILS_AVAILABLE}")
print()

try:
    from core.pdf_generator import PDFGenerator
    print("✅ PDFGenerator import successful")
except ImportError as e:
    print(f"❌ PDFGenerator import failed: {e}")

print()

# Test the analyzer import
try:
    from analyzer.cashapp_analyzer import CashAppAnalyzer
    print("✅ CashAppAnalyzer import successful")
    
    # Check if UTILS_AVAILABLE is set correctly in the module
    import analyzer.cashapp_analyzer as ca_module
    print(f"UTILS_AVAILABLE in module: {getattr(ca_module, 'UTILS_AVAILABLE', 'Not found')}")
    
except ImportError as e:
    print(f"❌ CashAppAnalyzer import failed: {e}")
