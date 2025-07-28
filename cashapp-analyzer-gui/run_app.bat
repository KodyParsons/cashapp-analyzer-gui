@echo off
echo Starting Cash App Analyzer GUI...
echo Activating conda base environment...

REM Set environment variable to fix Intel MKL issue
set KMP_DUPLICATE_LIB_OK=TRUE

call conda activate base
cd /d "%~dp0src"
python main.py
pause
