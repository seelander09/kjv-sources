# View Biblical Doublets Visualizations
# =====================================
# Simple script to open all available visualizations

Write-Host "Biblical Doublets Visualizations" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check what files exist
Write-Host "`nChecking available visualization files..." -ForegroundColor Yellow

$visualizations = @(
    @{ 
        Name = "Simple HTML Overview"
        File = "doublets_overview.html"
        Description = "Timeline view with statistics"
    },
    @{ 
        Name = "Simple Network View"
        File = "frontend\simple_doublets_network.html"
        Description = "Card-based network layout (RELIABLE)"
    },
    @{ 
        Name = "Enhanced Cytoscape Network"
        File = "frontend\doublets_cytoscape.html"
        Description = "Interactive network (requires internet)"
    },
    @{ 
        Name = "Original Cytoscape Visualization"
        File = "frontend\cytoscape_visualization.html"
        Description = "Full KJV sources network"
    }
)

foreach ($viz in $visualizations) {
    if (Test-Path $viz.File) {
        $size = [math]::Round((Get-Item $viz.File).Length / 1KB, 1)
        Write-Host "✅ $($viz.Name)" -ForegroundColor Green
        Write-Host "   File: $($viz.File) ($size KB)" -ForegroundColor Gray
        Write-Host "   Description: $($viz.Description)" -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host "❌ $($viz.Name)" -ForegroundColor Red
        Write-Host "   Missing: $($viz.File)" -ForegroundColor Gray
        Write-Host ""
    }
}

# Open available visualizations
Write-Host "Opening available visualizations..." -ForegroundColor Green

# 1. Simple HTML Overview
if (Test-Path "doublets_overview.html") {
    Write-Host "Opening: Simple HTML Overview..." -ForegroundColor Cyan
    Start-Process "doublets_overview.html"
    Start-Sleep -Seconds 2
}

# 2. Simple Network View (most reliable)
if (Test-Path "frontend\simple_doublets_network.html") {
    Write-Host "Opening: Simple Network View..." -ForegroundColor Cyan
    Start-Process "frontend\simple_doublets_network.html"
    Start-Sleep -Seconds 2
}

Write-Host "`n🎯 RECOMMENDED: Use the Simple Network View" -ForegroundColor Green
Write-Host "   This version works offline and shows all doublet connections" -ForegroundColor Gray

Write-Host "`n📋 What Each Visualization Shows:" -ForegroundColor Cyan
Write-Host "1. Simple HTML Overview - Bird's eye timeline across Torah books" -ForegroundColor White
Write-Host "2. Simple Network View - Card layout with connections and colors" -ForegroundColor White
Write-Host "3. Enhanced Cytoscape - Interactive network (may need internet)" -ForegroundColor White

Write-Host "`nPress any key to continue..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
