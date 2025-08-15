#!/usr/bin/env powershell
<#
.SYNOPSIS
    Start the KJV Bible Reader with Mathematical Analysis

.DESCRIPTION
    This script starts the web API server and opens the Bible reader interface
    in your default web browser.

.AUTHOR
    KJV Sources Project

.LICENSE
    MIT
#>

Write-Host "🔢 Starting KJV Bible Reader..." -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ and try again." -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "sources-env")) {
    Write-Host "❌ Virtual environment not found. Please run setup first." -ForegroundColor Red
    exit 1
}

# Check if required files exist
$requiredFiles = @("web_api_server.py", "word_level_parser.py", "mathematical_pattern_engine.py", "csv_data_loader.py")
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "❌ Required file not found: $file" -ForegroundColor Red
        exit 1
    }
}

# Check if frontend directory exists
if (-not (Test-Path "frontend")) {
    Write-Host "❌ Frontend directory not found. Please ensure the frontend folder exists." -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& "sources-env\Scripts\Activate.ps1"

# Check if FastAPI is installed
try {
    python -c "import fastapi" 2>$null
    Write-Host "✅ FastAPI found" -ForegroundColor Green
} catch {
    Write-Host "📦 Installing FastAPI..." -ForegroundColor Yellow
    pip install fastapi uvicorn
}

# Start the server in background
Write-Host "🚀 Starting web server..." -ForegroundColor Yellow
Start-Process python -ArgumentList "web_api_server.py" -WindowStyle Hidden

# Wait a moment for server to start
Write-Host "⏳ Waiting for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Check if server is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Server is running!" -ForegroundColor Green
} catch {
    Write-Host "❌ Server failed to start. Please check the console for errors." -ForegroundColor Red
    exit 1
}

# Load Bible data
Write-Host "📖 Loading Bible data..." -ForegroundColor Yellow
try {
    $loadResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/load-data" -UseBasicParsing
    $loadData = $loadResponse.Content | ConvertFrom-Json
    Write-Host "✅ Loaded $($loadData.words_loaded) words from $($loadData.statistics.total_books) books" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Warning: Could not load Bible data automatically" -ForegroundColor Yellow
}

# Open Bible reader in browser
Write-Host "🌐 Opening Bible reader in your browser..." -ForegroundColor Yellow
Start-Process "http://localhost:8000/frontend/bible_reader.html"

Write-Host ""
Write-Host "🎉 Bible Reader is now running!" -ForegroundColor Green
Write-Host ""
Write-Host "📖 Bible Reader: http://localhost:8000/frontend/bible_reader.html" -ForegroundColor Cyan
Write-Host "📚 API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🏠 Home Page: http://localhost:8000/" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "   • Select a book and chapter to start reading" -ForegroundColor White
Write-Host "   • Click on any word to see its mathematical patterns" -ForegroundColor White
Write-Host "   • Use the search box to find specific words" -ForegroundColor White
Write-Host "   • Words are color-coded by source (J, E, P, R)" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop the server, press Ctrl+C in this window" -ForegroundColor Red
Write-Host ""

# Keep the script running
try {
    while ($true) {
        Start-Sleep -Seconds 10
        # Check if server is still running
        try {
            Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 2 | Out-Null
        } catch {
            Write-Host "❌ Server stopped unexpectedly" -ForegroundColor Red
            break
        }
    }
} catch {
    Write-Host "🛑 Stopping server..." -ForegroundColor Yellow
}
