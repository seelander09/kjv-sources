#!/usr/bin/env powershell
<#
.SYNOPSIS
    Direct Cytoscape.js visualization launcher for KJV Sources project

.DESCRIPTION
    This script prepares the environment and opens the browser to the visualization.
    It provides clear instructions for starting the server manually.

.PARAMETER Port
    Port number for the local server (default: 8000)

.EXAMPLE
    .\start_cytoscape_direct.ps1
    Prepare environment and open browser with default settings

.EXAMPLE
    .\start_cytoscape_direct.ps1 -Port 8080
    Use port 8080 for the server
#>

param(
    [int]$Port = 8000
)

# Set console colors
$Host.UI.RawUI.ForegroundColor = "Cyan"
Write-Host "KJV Sources - Direct Cytoscape.js Launcher" -ForegroundColor Green
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
Write-Host "Preparing Cytoscape.js visualization..." -ForegroundColor Yellow
Write-Host ""

# Open browser to the visualization URL
$url = "http://localhost:$Port/cytoscape_visualization.html"
Write-Host "Opening browser to: $url" -ForegroundColor Cyan
Start-Process $url

Write-Host ""
Write-Host "IMPORTANT: The server is not running yet!" -ForegroundColor Red
Write-Host ""
Write-Host "To start the server, open a NEW PowerShell window and run:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   cd frontend" -ForegroundColor White
Write-Host "   python -m http.server $Port" -ForegroundColor White
Write-Host ""
Write-Host "Or use the simple launcher:" -ForegroundColor Yellow
Write-Host "   .\start_cytoscape_simple.ps1" -ForegroundColor White
Write-Host ""
Write-Host "The visualization will load once the server is running." -ForegroundColor Green
Write-Host ""
Write-Host "Available Network Views:" -ForegroundColor Yellow
Write-Host "   • Complete Network - All entities and relationships" -ForegroundColor White
Write-Host "   • Source Analysis - Focus on J, E, P, D, R sources" -ForegroundColor White
Write-Host "   • Person Network - Biblical characters and their connections" -ForegroundColor White
Write-Host "   • Geographic Network - Cities, locations, and directions" -ForegroundColor White
Write-Host ""
Write-Host "Interactive Features:" -ForegroundColor Yellow
Write-Host "   • Zoom and pan with mouse/touch" -ForegroundColor White
Write-Host "   • Click nodes for detailed information" -ForegroundColor White
Write-Host "   • Search for specific entities" -ForegroundColor White
Write-Host "   • Filter by entity type or source" -ForegroundColor White
Write-Host "   • Change layout algorithms" -ForegroundColor White
