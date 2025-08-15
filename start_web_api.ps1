# Start Web API Server for KJV Sources Mathematical Analysis
# ========================================================

Write-Host "🚀 Starting KJV Sources Mathematical Analysis Web API" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

# Check if Python is available
Write-Host "🐍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check if virtual environment is activated
Write-Host "`n🔧 Checking virtual environment..." -ForegroundColor Yellow
if ($env:VIRTUAL_ENV) {
    Write-Host "✅ Virtual environment active: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "⚠️  No virtual environment detected. Consider activating sources-env" -ForegroundColor Yellow
}

# Check if required files exist
Write-Host "`n📁 Checking required files..." -ForegroundColor Yellow
$requiredFiles = @(
    "web_api_server.py",
    "word_level_parser.py",
    "mathematical_pattern_engine.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file exists" -ForegroundColor Green
    } else {
        Write-Host "❌ $file missing" -ForegroundColor Red
    }
}

# Check if frontend exists
if (Test-Path "frontend/index.html") {
    Write-Host "✅ Frontend interface exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  Frontend interface not found" -ForegroundColor Yellow
}

Write-Host "`n🌐 Starting Web API Server..." -ForegroundColor Yellow
Write-Host "   API will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   Frontend Interface: http://localhost:8000/frontend/" -ForegroundColor Cyan

Write-Host "`n📋 Available endpoints:" -ForegroundColor Yellow
Write-Host "   • GET /api/health - Health check" -ForegroundColor White
Write-Host "   • GET /api/search?q=word - Search for words" -ForegroundColor White
Write-Host "   • GET /api/patterns/word - Get word patterns" -ForegroundColor White
Write-Host "   • GET /api/verse/reference - Get verse data" -ForegroundColor White
Write-Host "   • GET /api/global-analysis - Global analysis" -ForegroundColor White
Write-Host "   • GET /api/load-data - Load sample data" -ForegroundColor White

Write-Host "`n💡 Tips:" -ForegroundColor Yellow
Write-Host "   • Press Ctrl+C to stop the server" -ForegroundColor White
Write-Host "   • Visit http://localhost:8000/docs for interactive API docs" -ForegroundColor White
Write-Host "   • Use the frontend at http://localhost:8000/frontend/ for easy testing" -ForegroundColor White

Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
Write-Host "🎯 Starting server..." -ForegroundColor Green

# Start the web API server
try {
    python web_api_server.py
} catch {
    Write-Host "`n❌ Failed to start server: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n🔧 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "   1. Make sure all dependencies are installed: pip install fastapi uvicorn" -ForegroundColor White
    Write-Host "   2. Check if port 8000 is available" -ForegroundColor White
    Write-Host "   3. Ensure all required files are present" -ForegroundColor White
}
