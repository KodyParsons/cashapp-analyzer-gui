"""
Migration Script for Legacy Test Files

This script helps migrate existing test files from various locations
into the new organized test structure.
"""

import os
import shutil
import glob
from pathlib import Path

# Define the project root and new test directory
PROJECT_ROOT = Path(__file__).parent.parent
TESTS_DIR = Path(__file__).parent
LEGACY_TESTS_DIR = TESTS_DIR / "legacy"

# Create legacy directory to store old files temporarily
LEGACY_TESTS_DIR.mkdir(exist_ok=True)

# Define mapping of old test files to new locations/purposes
TEST_FILE_MAPPING = {
    # Root directory tests
    'test_viz_fixes.py': 'unit/test_visualizations.py',
    'test_simple_pdf.py': 'unit/test_pdf_generation.py', 
    'test_final_fixes.py': 'integration/test_bug_fixes.py',
    'test_enhanced_pdf.py': 'integration/test_pdf_enhanced.py',
    'test_pdf_demo.py': 'demos/pdf_generation_demo.py',
    'test_visualizations.py': 'unit/test_chart_generation.py',
    'test_pdf_comprehensive.py': 'integration/test_pdf_comprehensive.py',
    'test_pdf_generation.py': 'unit/test_pdf_core.py',
    'test_income_debug.py': 'unit/test_income_analysis.py',
    
    # GUI directory tests
    'test_last_month_viz.py': 'integration/test_monthly_reports.py',
    'test_large_transactions.py': 'unit/test_transaction_filtering.py',
    'test_enhanced_app.py': 'integration/test_gui_workflow.py',
    'test_analyzer.py': 'unit/test_analyzer_core.py',
    
    # Src directory tests  
    'test_pdf_fix.py': 'unit/test_pdf_fixes.py',
    'test_comprehensive_pdf.py': 'integration/test_pdf_reports.py',
    'demo_pdf_fix.py': 'demos/pdf_fix_demo.py'
}

def find_legacy_test_files():
    """Find all legacy test files in the project"""
    test_files = []
    
    # Search in project root
    root_tests = glob.glob(str(PROJECT_ROOT / "test_*.py"))
    test_files.extend([(f, 'root') for f in root_tests])
    
    # Search in GUI directory  
    gui_tests = glob.glob(str(PROJECT_ROOT / "test_*.py"))
    test_files.extend([(f, 'gui') for f in gui_tests])
    
    # Search in src directory
    src_tests = glob.glob(str(PROJECT_ROOT / "src" / "test_*.py"))
    test_files.extend([(f, 'src') for f in src_tests])
    
    # Search for demo files
    demo_files = glob.glob(str(PROJECT_ROOT / "src" / "demo_*.py"))
    test_files.extend([(f, 'src') for f in demo_files])
    
    return test_files

def backup_legacy_files():
    """Create backups of all legacy test files"""
    legacy_files = find_legacy_test_files()
    
    print("📁 Creating backups of legacy test files...")
    
    for file_path, location in legacy_files:
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            backup_path = LEGACY_TESTS_DIR / f"{location}_{filename}"
            
            try:
                shutil.copy2(file_path, backup_path)
                print(f"   ✅ Backed up: {filename} -> {backup_path}")
            except Exception as e:
                print(f"   ❌ Failed to backup {filename}: {e}")

def generate_migration_plan():
    """Generate a migration plan for legacy test files"""
    legacy_files = find_legacy_test_files()
    
    print("\n📋 Migration Plan:")
    print("=" * 60)
    
    for file_path, location in legacy_files:
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            
            # Check if we have a mapping for this file
            if filename in TEST_FILE_MAPPING:
                new_location = TEST_FILE_MAPPING[filename]
                print(f"📄 {filename}")
                print(f"   From: {location}/{filename}")
                print(f"   To: tests/{new_location}")
                print(f"   Purpose: {get_file_purpose(filename)}")
                print()
            else:
                print(f"❓ {filename}")
                print(f"   From: {location}/{filename}")
                print(f"   To: ⚠️  NEEDS MANUAL REVIEW")
                print(f"   Purpose: Unknown - requires analysis")
                print()

def get_file_purpose(filename):
    """Get the inferred purpose of a test file based on its name"""
    purpose_map = {
        'test_viz_fixes.py': 'Tests for visualization bug fixes',
        'test_simple_pdf.py': 'Basic PDF generation tests',
        'test_final_fixes.py': 'Tests for final bug fixes',
        'test_enhanced_pdf.py': 'Enhanced PDF feature tests',
        'test_pdf_demo.py': 'PDF generation demonstration',
        'test_visualizations.py': 'Chart and visualization tests',
        'test_pdf_comprehensive.py': 'Comprehensive PDF workflow tests',
        'test_pdf_generation.py': 'Core PDF generation tests',
        'test_income_debug.py': 'Income analysis debugging tests',
        'test_last_month_viz.py': 'Monthly visualization tests',
        'test_large_transactions.py': 'Large transaction handling tests',
        'test_enhanced_app.py': 'Enhanced application feature tests',
        'test_analyzer.py': 'Core analyzer functionality tests',
        'test_pdf_fix.py': 'PDF bug fix tests',
        'test_comprehensive_pdf.py': 'Complete PDF report tests',
        'demo_pdf_fix.py': 'PDF fix demonstration'
    }
    
    return purpose_map.get(filename, 'Unknown purpose')

def analyze_test_file(file_path):
    """Analyze a test file to understand its contents"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic analysis
        lines = content.split('\n')
        imports = [line for line in lines if line.strip().startswith('import') or line.strip().startswith('from')]
        functions = [line for line in lines if line.strip().startswith('def ')]
        classes = [line for line in lines if line.strip().startswith('class ')]
        
        return {
            'lines': len(lines),
            'imports': len(imports),
            'functions': len(functions),
            'classes': len(classes),
            'has_unittest': 'unittest' in content,
            'has_matplotlib': 'matplotlib' in content or 'plt' in content,
            'has_pdf': 'pdf' in content.lower() or 'reportlab' in content,
            'sample_imports': imports[:3],
            'sample_functions': functions[:3]
        }
    except Exception as e:
        return {'error': str(e)}

def create_analysis_report():
    """Create a detailed analysis report of all legacy test files"""
    legacy_files = find_legacy_test_files()
    
    print("\n🔍 Detailed Analysis Report:")
    print("=" * 80)
    
    for file_path, location in legacy_files:
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            analysis = analyze_test_file(file_path)
            
            print(f"\n📄 {filename} ({location})")
            print("-" * 50)
            
            if 'error' in analysis:
                print(f"   ❌ Error analyzing file: {analysis['error']}")
                continue
            
            print(f"   📊 Lines of code: {analysis['lines']}")
            print(f"   📦 Import statements: {analysis['imports']}")
            print(f"   🔧 Functions: {analysis['functions']}")
            print(f"   🏗️  Classes: {analysis['classes']}")
            print(f"   🧪 Uses unittest: {'Yes' if analysis['has_unittest'] else 'No'}")
            print(f"   📈 Uses matplotlib: {'Yes' if analysis['has_matplotlib'] else 'No'}")
            print(f"   📄 Uses PDF: {'Yes' if analysis['has_pdf'] else 'No'}")
            
            if analysis['sample_imports']:
                print(f"   📝 Sample imports:")
                for imp in analysis['sample_imports']:
                    print(f"      {imp.strip()}")
            
            if analysis['sample_functions']:
                print(f"   🔧 Sample functions:")
                for func in analysis['sample_functions']:
                    print(f"      {func.strip()}")

def main():
    """Main migration script"""
    print("🚀 Cash App Analyzer - Test Migration Script")
    print("=" * 60)
    
    # Step 1: Backup legacy files
    backup_legacy_files()
    
    # Step 2: Generate migration plan
    generate_migration_plan()
    
    # Step 3: Create detailed analysis
    create_analysis_report()
    
    print("\n✅ Migration analysis complete!")
    print(f"📁 Legacy files backed up to: {LEGACY_TESTS_DIR}")
    print("\n📋 Next Steps:")
    print("1. Review the migration plan above")
    print("2. Manually migrate valuable test cases to new structure")
    print("3. Update import statements and paths")
    print("4. Run new test suite to verify functionality")
    print("5. Remove old test files after successful migration")

if __name__ == '__main__':
    main()
