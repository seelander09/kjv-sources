#!/usr/bin/env powershell
<#
.SYNOPSIS
    Generate Biblical Doublets Bird's Eye View Visualization

.DESCRIPTION
    This script generates comprehensive visualizations showing the distribution
    of biblical doublets (repeated passages) across the Torah. It creates both
    text-based analysis and interactive HTML visualizations to provide a 
    bird's eye view of patterns in the Documentary Hypothesis.

.PARAMETER OpenHtml
    Automatically open the generated HTML visualization in the default browser

.PARAMETER GenerateAdvanced
    Generate advanced heat map visualization (requires matplotlib)

.PARAMETER OutputDir
    Directory to save visualization files (default: current directory)

.EXAMPLE
    .\start_doublets_visualization.ps1
    Generate basic doublets visualization

.EXAMPLE
    .\start_doublets_visualization.ps1 -OpenHtml
    Generate visualization and open HTML file automatically

.EXAMPLE
    .\start_doublets_visualization.ps1 -GenerateAdvanced
    Generate both basic and advanced heat map visualizations
#>

param(
    [switch]$OpenHtml,
    [switch]$GenerateAdvanced,
    [string]$OutputDir = "."
)

# Set console colors
$Host.UI.RawUI.ForegroundColor = "Cyan"
Write-Host "KJV Sources - Biblical Doublets Bird's Eye View" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python3 --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python3 not found. Please install Python 3.8+ and try again." -ForegroundColor Red
    exit 1
}

# Check if doublets data file exists
if (-not (Test-Path "doublets_data.json")) {
    Write-Host "Doublets data file not found: doublets_data.json" -ForegroundColor Red
    Write-Host "Please ensure you're running this script from the project root directory." -ForegroundColor Yellow
    exit 1
}

Write-Host "Found doublets data file: doublets_data.json" -ForegroundColor Green
Write-Host ""

# Generate basic visualization
Write-Host "Generating Biblical Doublets Overview..." -ForegroundColor Yellow
Write-Host "This will create both text analysis and HTML visualization" -ForegroundColor Cyan
Write-Host ""

try {
    python3 simple_doublets_overview.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Basic visualization generated successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Error generating basic visualization" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error running basic visualization: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Generate advanced heat map if requested
if ($GenerateAdvanced) {
    Write-Host "Generating Advanced Heat Map Visualization..." -ForegroundColor Yellow
    
    # Check if matplotlib is available
    try {
        python3 -c "import matplotlib.pyplot as plt; import seaborn as sns; import pandas as pd" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Matplotlib dependencies found" -ForegroundColor Green
            
            try {
                python3 biblical_doublets_heatmap.py
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✅ Advanced heat map generated successfully!" -ForegroundColor Green
                } else {
                    Write-Host "⚠️ Error generating advanced heat map" -ForegroundColor Yellow
                }
            } catch {
                Write-Host "⚠️ Error running advanced heat map: $_" -ForegroundColor Yellow
            }
        } else {
            Write-Host "⚠️ Matplotlib not available for advanced visualization" -ForegroundColor Yellow
            Write-Host "Install with: pip install matplotlib seaborn pandas" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "⚠️ Could not check matplotlib dependencies" -ForegroundColor Yellow
    }
    
    Write-Host ""
}

# List generated files
Write-Host "📁 Generated Files:" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Green

$generatedFiles = @()

if (Test-Path "doublets_overview.html") {
    $generatedFiles += "doublets_overview.html"
    $fileSize = (Get-Item "doublets_overview.html").Length
    Write-Host "  📊 doublets_overview.html ($([math]::Round($fileSize/1KB, 1)) KB)" -ForegroundColor Cyan
    Write-Host "      Interactive HTML visualization with timeline and statistics" -ForegroundColor Gray
}

if (Test-Path "biblical_doublets_overview.png") {
    $generatedFiles += "biblical_doublets_overview.png"
    Write-Host "  🖼️ biblical_doublets_overview.png" -ForegroundColor Cyan
    Write-Host "      Overview heat map showing doublet distribution" -ForegroundColor Gray
}

if (Test-Path "biblical_doublets_detailed.png") {
    $generatedFiles += "biblical_doublets_detailed.png"
    Write-Host "  🖼️ biblical_doublets_detailed.png" -ForegroundColor Cyan
    Write-Host "      Detailed heat map by category and source" -ForegroundColor Gray
}

if ($generatedFiles.Count -eq 0) {
    Write-Host "  ⚠️ No visualization files found" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "📈 Analysis Summary:" -ForegroundColor Green
    Write-Host "===================" -ForegroundColor Green
    Write-Host "  • Bird's eye view of biblical doublets across the Torah" -ForegroundColor White
    Write-Host "  • Visual distribution patterns by book and category" -ForegroundColor White
    Write-Host "  • Documentary source analysis (J, E, P, D, R)" -ForegroundColor White
    Write-Host "  • Interactive timeline showing doublet clustering" -ForegroundColor White
    Write-Host "  • Statistical breakdown of doublet patterns" -ForegroundColor White
}

Write-Host ""

# Open HTML file if requested
if ($OpenHtml -and (Test-Path "doublets_overview.html")) {
    Write-Host "🌐 Opening HTML visualization..." -ForegroundColor Yellow
    
    try {
        # Cross-platform approach to open HTML file
        if ($IsWindows) {
            Start-Process "doublets_overview.html"
        } elseif ($IsMacOS) {
            Start-Process "open" -ArgumentList "doublets_overview.html"
        } else {
            # Linux
            Start-Process "xdg-open" -ArgumentList "doublets_overview.html"
        }
        
        Write-Host "✅ HTML visualization opened in default browser" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Could not auto-open HTML file: $_" -ForegroundColor Yellow
        Write-Host "Please manually open: doublets_overview.html" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "🎯 Key Insights Available:" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green
Write-Host "  1. Visual patterns show clustering of doublets in Genesis" -ForegroundColor White
Write-Host "  2. Different categories (creation, genealogy, law) have distinct distributions" -ForegroundColor White
Write-Host "  3. Source analysis reveals documentary hypothesis patterns" -ForegroundColor White
Write-Host "  4. Timeline view helps identify narrative development patterns" -ForegroundColor White
Write-Host "  5. Statistical analysis quantifies doublet frequency and distribution" -ForegroundColor White

Write-Host ""
Write-Host "📖 Usage Tips:" -ForegroundColor Green
Write-Host "=============" -ForegroundColor Green
Write-Host "  • Use the HTML visualization for interactive exploration" -ForegroundColor White
Write-Host "  • Timeline view provides the best 'bird's eye view'" -ForegroundColor White
Write-Host "  • Color coding helps identify different doublet categories" -ForegroundColor White
Write-Host "  • Statistics section provides quantitative analysis" -ForegroundColor White

Write-Host ""
Write-Host "✅ Biblical Doublets Visualization Complete!" -ForegroundColor Green

# Additional integration suggestions
Write-Host ""
Write-Host "🔗 Integration Opportunities:" -ForegroundColor Yellow
Write-Host "============================" -ForegroundColor Yellow
Write-Host "  • Combine with existing Cytoscape.js network visualization" -ForegroundColor White
Write-Host "  • Integrate with LightRAG for semantic search of doublets" -ForegroundColor White
Write-Host "  • Export data for further analysis in specialized tools" -ForegroundColor White
Write-Host "  • Use as foundation for scholarly research presentations" -ForegroundColor White

Write-Host ""
Write-Host "For more advanced analysis, consider:" -ForegroundColor Cyan
Write-Host "  • Bible Analyzer for detailed text comparison" -ForegroundColor Gray
Write-Host "  • Logos Bible Software for cross-reference analysis" -ForegroundColor Gray
Write-Host "  • Custom D3.js implementation for web deployment" -ForegroundColor Gray