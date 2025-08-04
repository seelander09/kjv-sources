@echo off
echo ========================================
echo    KJV Sources Data Pipeline (Fixed)
echo ========================================
echo.

echo Activating conda environment...
call conda activate kjv-sources-env

if %errorlevel% neq 0 (
    echo ERROR: Failed to activate conda environment
    echo Please make sure conda is installed and the environment exists
    pause
    exit /b 1
)

echo.
echo Running fixed pipeline...
python kjv_pipeline.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Pipeline failed
    pause
    exit /b 1
)

echo.
echo Pipeline completed successfully!
pause 