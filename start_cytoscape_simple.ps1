#!/usr/bin/env powershell
<#
.SYNOPSIS
    Simple Cytoscape.js visualization launcher for KJV Sources project

.DESCRIPTION
    This script starts the Cytoscape.js visualization with a simple approach
    that's more reliable than the complex background job method.

.PARAMETER Port
    Port number for the local server (default: 8000)

.EXAMPLE
    .\start_cytoscape_simple.ps1
    Start the visualization with default settings

.EXAMPLE
    .\start_cytoscape_simple.ps1 -Port 8080
    Start visualization on port 8080
#>

param(
    [int]$Port = 8000
)

# Set console colors
$Host.UI.RawUI.ForegroundColor = "Cyan"
Write-Host "KJV Sources - Simple Cytoscape.js Launcher" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found. Please install Python 3.8+ and try again." -ForegroundColor Red
    exit 1
}

# Check if visualization file exists
if (-not (Test-Path "frontend/cytoscape_visualization.html")) {
    Write-Host "Visualization file not found: frontend/cytoscape_visualization.html" -ForegroundColor Red
    Write-Host "Please run the data generation first:" -ForegroundColor Yellow
    Write-Host "   python cytoscape_data_generator.py" -ForegroundColor Yellow
    exit 1
}

# Check if network data files exist
$networkDataFiles = @(
    "cytoscape_network_data.json",
    "cytoscape_source_network.json", 
    "cytoscape_person_network.json",
    "cytoscape_geographic_network.json"
)

$missingFiles = @()
foreach ($file in $networkDataFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "Missing network data files:" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "   $file" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Please run the data generation first:" -ForegroundColor Yellow
    Write-Host "   python cytoscape_data_generator.py" -ForegroundColor Yellow
    exit 1
}

# Copy network data files to frontend directory for web access
Write-Host "Copying network data to frontend directory..." -ForegroundColor Yellow
try {
    Copy-Item "cytoscape_*.json" -Destination "frontend/" -Force
    Write-Host "Network data copied to frontend directory" -ForegroundColor Green
} catch {
    Write-Host "Error copying network data: $_" -ForegroundColor Red
}

Write-Host ""

# Check if port is available
try {
    $testConnection = New-Object System.Net.Sockets.TcpClient
    $testConnection.Connect("localhost", $Port)
    $testConnection.Close()
    Write-Host "Port $Port is already in use. Please choose a different port." -ForegroundColor Red
    exit 1
} catch {
    Write-Host "Port $Port is available" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting Cytoscape.js visualization..." -ForegroundColor Yellow
Write-Host ""

# Change to frontend directory and start server
try {
    Push-Location "frontend"
    
    Write-Host "Starting HTTP server on port $Port..." -ForegroundColor Yellow
    Write-Host "Server will be accessible at: http://localhost:$Port/cytoscape_visualization.html" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red
    Write-Host ""
    
    # Start Python HTTP server (this will block until Ctrl+C)
    python -m http.server $Port
    
} catch {
    Write-Host "Error starting server: $_" -ForegroundColor Red
} finally {
    # Return to original directory
    Pop-Location
}

Write-Host ""
Write-Host "Server stopped" -ForegroundColor Yellow
