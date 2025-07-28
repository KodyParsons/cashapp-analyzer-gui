"""Build script for creating EXE package of Cash App Analyzer"""
import os
import sys
import subprocess
import shutil

def setup_build_environment():
    """Setup the build environment"""
    print("Setting up build environment...")
    
    # Create build directory
    build_dir = "build_exe"
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    
    return build_dir

def create_pyinstaller_spec():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/utils', 'utils'),
        ('src/core', 'core'),
        ('src/analyzer', 'analyzer'),
        ('src/gui', 'gui'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinterdnd2',
        'pandas',
        'numpy',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends.backend_agg',
        'matplotlib.figure',
        'matplotlib.pyplot',
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.lib.pagesizes',
        'reportlab.platypus',
        'reportlab.lib.styles',
        'reportlab.lib.units',
        'reportlab.lib.colors',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PIL',
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
        'matplotlib.tests',
        'pandas.tests',
        'numpy.tests',
        'tkinter.test',
        'unittest',
        'test',
        'tests',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CashAppAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('CashAppAnalyzer.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ PyInstaller spec file created")

def build_exe():
    """Build the executable"""
    print("Building executable...")
    
    try:
        # Build using PyInstaller
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            'CashAppAnalyzer.spec',
            '--clean',
            '--noconfirm'
        ], check=True, capture_output=True, text=True)
        
        print("✅ Executable built successfully")
        
        # Check if exe exists
        exe_path = os.path.join('dist', 'CashAppAnalyzer.exe')
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # Convert to MB
            print(f"✅ Executable created: {exe_path} ({file_size:.1f} MB)")
            return exe_path
        else:
            print("❌ Executable not found after build")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return None

def create_distribution_package(exe_path):
    """Create distribution package"""
    if not exe_path or not os.path.exists(exe_path):
        print("❌ No executable to package")
        return
    
    print("Creating distribution package...")
    
    # Create distribution directory
    dist_dir = "CashAppAnalyzer_Distribution"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Copy executable
    shutil.copy2(exe_path, dist_dir)
    
    # Create README for distribution
    readme_content = """# Cash App Analyzer - Standalone Application

## Quick Start
1. Double-click CashAppAnalyzer.exe to launch the application
2. Drag and drop your Cash App CSV file into the application
3. Select your desired date range
4. Click "Generate Report" to analyze your transactions
5. View results in the "Results" and "Visualizations" tabs
6. Generate PDF reports with comprehensive charts

## Features
- Automatic transaction categorization
- Income, expense, and cash flow analysis
- Interactive visualizations
- Comprehensive PDF reports with multiple chart types
- Date range filtering
- Export functionality

## System Requirements
- Windows 7 or higher
- No additional software installation required

## Support
For support or questions, please contact the developer.

## Version
Built on: """ + str(os.path.getmtime(exe_path)) + """
"""
    
    with open(os.path.join(dist_dir, 'README.txt'), 'w') as f:
        f.write(readme_content)
    
    # Copy sample data if available
    sample_files = ['sample_data.csv', 'cash_app_transactions.csv']
    for sample_file in sample_files:
        if os.path.exists(sample_file):
            shutil.copy2(sample_file, dist_dir)
            print(f"✅ Copied sample file: {sample_file}")
    
    print(f"✅ Distribution package created: {dist_dir}")

def main():
    """Main build process"""
    print("🚀 Starting Cash App Analyzer EXE build process...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✅ PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found. Install with: pip install pyinstaller")
        return
    
    # Setup build environment
    build_dir = setup_build_environment()
    
    # Create spec file
    create_pyinstaller_spec()
    
    # Build executable
    exe_path = build_exe()
    
    if exe_path:
        # Create distribution package
        create_distribution_package(exe_path)
        print("🎉 Build process completed successfully!")
        print(f"📦 Distribution ready in: CashAppAnalyzer_Distribution/")
    else:
        print("❌ Build process failed")

if __name__ == "__main__":
    main()
