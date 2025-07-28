@echo off
echo Building Cash App Analyzer EXE...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found in PATH
    echo Please install Python and add it to your PATH
    pause
    exit /b 1
)

REM Install PyInstaller if not available
echo Checking for PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo Error: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Run the build script
echo Running build script...
python build_exe.py

echo.
echo Build process complete!
pause
