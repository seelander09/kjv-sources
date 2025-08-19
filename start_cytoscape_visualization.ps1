#!/usr/bin/env powershell
<#
.SYNOPSIS
    Start Cytoscape.js visualization for KJV Sources project

.DESCRIPTION
    This script generates network data from KJV sources CSV files and starts
    the Cytoscape.js visualization interface.

.PARAMETER GenerateData
    Force regeneration of network data files

.PARAMETER Port
    Port number for the local server (default: 8000)

.EXAMPLE
    .\start_cytoscape_visualization.ps1
    Start the visualization with default settings

.EXAMPLE
    .\start_cytoscape_visualization.ps1 -GenerateData
    Regenerate network data and start visualization

.EXAMPLE
    .\start_cytoscape_visualization.ps1 -Port 8080
    Start visualization on port 8080
#>

param(
    [switch]$GenerateData,
    [int]$Port = 8000
)

# Set console colors
$Host.UI.RawUI.ForegroundColor = "Cyan"
Write-Host "KJV Sources - Cytoscape.js Network Visualization" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found. Please install Python 3.8+ and try again." -ForegroundColor Red
    exit 1
}

# Check if required Python packages are installed
Write-Host "Checking Python dependencies..." -ForegroundColor Yellow
$requiredPackages = @("pandas", "json", "re", "pathlib", "collections", "logging")

foreach ($package in $requiredPackages) {
    try {
        python -c "import $package" 2>$null
        Write-Host "  $package - OK" -ForegroundColor Green
    } catch {
        Write-Host "  $package - not found" -ForegroundColor Red
    }
}

Write-Host ""

# Check if output directory exists
if (-not (Test-Path "output")) {
    Write-Host "Output directory not found. Please run the pipeline first:" -ForegroundColor Red
    Write-Host "   python parse_wikitext.py pipeline" -ForegroundColor Yellow
    exit 1
}

# Check if CSV files exist
$csvFiles = Get-ChildItem -Path "output" -Recurse -Filter "*.csv"
if ($csvFiles.Count -eq 0) {
    Write-Host "No CSV files found in output directory. Please run the pipeline first:" -ForegroundColor Red
    Write-Host "   python parse_wikitext.py pipeline" -ForegroundColor Yellow
    exit 1
}

Write-Host "Found $($csvFiles.Count) CSV files in output directory" -ForegroundColor Green
Write-Host ""

# Generate network data if requested or if files don't exist
$networkDataFiles = @(
    "cytoscape_network_data.json",
    "cytoscape_source_network.json", 
    "cytoscape_person_network.json",
    "cytoscape_geographic_network.json"
)

$missingFiles = $false
foreach ($file in $networkDataFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles = $true
        break
    }
}

if ($GenerateData -or $missingFiles) {
    Write-Host "Generating Cytoscape.js network data..." -ForegroundColor Yellow
    
    try {
        python cytoscape_data_generator.py
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Network data generated successfully!" -ForegroundColor Green
        } else {
            Write-Host "Error generating network data" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "Error running data generator: $_" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
} else {
    Write-Host "Network data files already exist" -ForegroundColor Green
    Write-Host ""
}

# Check if visualization file exists
if (-not (Test-Path "frontend/cytoscape_visualization.html")) {
    Write-Host "Visualization file not found: frontend/cytoscape_visualization.html" -ForegroundColor Red
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

# Start local server
Write-Host "Starting local server on port $Port..." -ForegroundColor Yellow
Write-Host "Opening Cytoscape.js visualization..." -ForegroundColor Yellow
Write-Host ""

try {
    # Change to frontend directory and start server
    Write-Host "Changing to frontend directory..." -ForegroundColor Yellow
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
    exit 1
} finally {
    # Return to original directory
    Pop-Location
}

Write-Host ""
Write-Host "Cytoscape.js visualization complete!" -ForegroundColor Green
