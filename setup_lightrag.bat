@echo off
echo ========================================
echo KJV Sources LightRAG Setup Script
echo ========================================
echo.

echo [1/4] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

echo.
echo [2/4] Installing LightRAG dependencies...
pip install -r lightrag_requirements.txt
if %errorlevel% neq 0 (
    echo WARNING: Some dependencies may not have installed correctly.
    echo You can try installing manually: pip install lightrag sentence-transformers torch transformers rich pandas
)

echo.
echo [3/4] Running LightRAG ingestion...
python lightrag_ingestion.py
if %errorlevel% neq 0 (
    echo WARNING: Ingestion may have encountered issues.
    echo Check the output above for details.
)

echo.
echo [4/4] Setup complete!
echo.
echo Next steps:
echo 1. Run: python lightrag_query.py
echo 2. Type 'help' for available commands
echo 3. Try: source:J or book:Genesis
echo.
echo Press any key to exit...
pause > nul 