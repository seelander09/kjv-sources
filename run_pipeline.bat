@echo off
echo ========================================
echo    KJV Sources Data Pipeline
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Trying python3...
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Python not found. Trying py...
        py --version >nul 2>&1
        if %errorlevel% neq 0 (
            echo ERROR: Python not found!
            echo Please install Python 3.8+ and ensure it's in your PATH.
            pause
            exit /b 1
        ) else (
            set PYTHON_CMD=py
        )
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

echo Found Python: %PYTHON_CMD%
echo.

echo Starting KJV Sources Pipeline...
%PYTHON_CMD% kjv_pipeline.py

echo.
echo Pipeline completed!
echo.
echo Available commands:
echo   %PYTHON_CMD% kjv_cli.py view genesis
echo   %PYTHON_CMD% kjv_cli.py stats genesis  
echo   %PYTHON_CMD% kjv_cli.py search genesis --text "God"
echo   %PYTHON_CMD% kjv_cli.py export-csv genesis
echo.
pause 