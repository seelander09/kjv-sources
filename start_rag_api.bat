@echo off
REM Start RAG API Server for KJPBS Integration
REM ==========================================

echo 🚀 KJV Sources RAG API Server Startup
echo =====================================

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo ⚠️  No virtual environment detected
    echo 💡 Activating sources-env...
    call sources-env\Scripts\activate.bat
    if errorlevel 1 (
        echo ❌ Failed to activate virtual environment
        echo 💡 Please run: python -m venv sources-env
        pause
        exit /b 1
    )
)

echo ✅ Virtual environment: %VIRTUAL_ENV%

REM Check if FastAPI is installed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo 📦 Installing FastAPI requirements...
    pip install -r api_requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install requirements
        pause
        exit /b 1
    )
)

REM Check if Qdrant client is available
python -c "from src.kjv_sources.qdrant_client import QdrantClient" 2>nul
if errorlevel 1 (
    echo ❌ Cannot import QdrantClient
    echo 💡 Make sure you're in the kjv-sources project directory
    echo 💡 And that your existing modules are properly installed
    pause
    exit /b 1
)

echo 🔧 Starting RAG API Server...
echo 📡 API will be available at: http://127.0.0.1:8000
echo 📖 Documentation at: http://127.0.0.1:8000/docs
echo 🧪 Test the API with: python test_rag_api.py
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python rag_api_server.py

pause
