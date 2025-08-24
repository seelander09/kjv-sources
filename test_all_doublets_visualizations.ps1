# Comprehensive Biblical Doublets Visualization Testing Script
# ============================================================
# Tests all doublet visualization tools and opens the results

Write-Host "🔬 Biblical Doublets Visualization Testing Suite" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"

# Function to test command success
function Test-CommandSuccess {
    param($Command, $Description)
    Write-Host "`n🧪 Testing: $Description" -ForegroundColor Yellow
    try {
        Invoke-Expression $Command
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $Description - SUCCESS" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ $Description - FAILED (Exit code: $LASTEXITCODE)" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ $Description - ERROR: $_" -ForegroundColor Red
        return $false
    }
}

# Test 1: Simple Doublets Overview
$test1 = Test-CommandSuccess "python simple_doublets_overview.py" "Simple Doublets Overview (HTML + Text)"

# Test 2: Minimal Heat Map
$test2 = Test-CommandSuccess "python minimal_heatmap_test.py" "Minimal Heat Map (Data Processing + CSV)"

# Test 3: Cytoscape Doublets Integration
$test3 = Test-CommandSuccess "python cytoscape_doublets_integration.py" "Cytoscape Doublets Integration (Interactive Network)"

# Test 4: Check for matplotlib and full heat map
Write-Host "`n🧪 Testing: Full Matplotlib Heat Map" -ForegroundColor Yellow
try {
    python -c "import matplotlib; print('Matplotlib available')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        $test4 = Test-CommandSuccess "python biblical_doublets_heatmap.py" "Full Matplotlib Heat Map (PNG Graphics)"
    } else {
        Write-Host "⚠️  Matplotlib not available - Skipping full heat map" -ForegroundColor Yellow
        Write-Host "   To install: pip install matplotlib seaborn" -ForegroundColor Cyan
        $test4 = $false
    }
} catch {
    Write-Host "⚠️  Python/matplotlib check failed - Skipping full heat map" -ForegroundColor Yellow
    $test4 = $false
}

# Results Summary
Write-Host "`n📊 TEST RESULTS SUMMARY" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

$results = @(
    @{ Name = "Simple Overview (HTML)"; Success = $test1; File = "doublets_overview.html" },
    @{ Name = "Heat Map Data (CSV)"; Success = $test2; File = "doublets_heatmap_data.csv" },
    @{ Name = "Cytoscape Network"; Success = $test3; File = "frontend\doublets_cytoscape.html" },
    @{ Name = "Matplotlib Graphics"; Success = $test4; File = "biblical_doublets_*.png" }
)

foreach ($result in $results) {
    $status = if ($result.Success) { "✅ PASS" } else { "❌ FAIL" }
    Write-Host "$status - $($result.Name)" -ForegroundColor $(if ($result.Success) { "Green" } else { "Red" })
}

# Open Generated Visualizations
Write-Host "`n🚀 OPENING GENERATED VISUALIZATIONS" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# 1. HTML Overview
if (Test-Path "doublets_overview.html") {
    Write-Host "📂 Opening: Simple HTML Overview" -ForegroundColor Green
    Start-Process "doublets_overview.html"
    Start-Sleep -Seconds 2
} else {
    Write-Host "❌ HTML Overview not found" -ForegroundColor Red
}

# 2. Enhanced Cytoscape Network
$cytoscapeFile = "frontend\doublets_cytoscape.html"
if (Test-Path $cytoscapeFile) {
    Write-Host "📂 Opening: Enhanced Cytoscape Network" -ForegroundColor Green
    Start-Process $cytoscapeFile
    Start-Sleep -Seconds 2
} else {
    Write-Host "❌ Cytoscape network not found" -ForegroundColor Red
}

# 3. Original Cytoscape (for comparison)
$originalCytoscape = "frontend\cytoscape_visualization.html"
if (Test-Path $originalCytoscape) {
    Write-Host "📂 Available: Original Cytoscape Visualization" -ForegroundColor Cyan
    Write-Host "   (Run manually if needed: Start-Process '$originalCytoscape')" -ForegroundColor Gray
}

# 4. Check for PNG files
$pngFiles = Get-ChildItem -Filter "biblical_doublets_*.png" -ErrorAction SilentlyContinue
if ($pngFiles.Count -gt 0) {
    Write-Host "📂 Opening: Matplotlib PNG Graphics" -ForegroundColor Green
    foreach ($file in $pngFiles) {
        Start-Process $file.FullName
        Start-Sleep -Seconds 1
    }
} else {
    Write-Host "⚠️  No PNG files found (requires matplotlib)" -ForegroundColor Yellow
}

# File Inventory
Write-Host "`n📁 GENERATED FILES INVENTORY" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

$files = @(
    @{ Path = "doublets_overview.html"; Description = "Simple HTML overview with timeline" },
    @{ Path = "doublets_heatmap_data.csv"; Description = "Raw data for external analysis" },
    @{ Path = "frontend\doublets_cytoscape.html"; Description = "Enhanced interactive network" },
    @{ Path = "frontend\cytoscape_doublets_network.json"; Description = "Network data file" },
    @{ Path = "biblical_doublets_overview.png"; Description = "Overview heat map graphic" },
    @{ Path = "biblical_doublets_detailed.png"; Description = "Detailed heat map graphic" }
)

foreach ($file in $files) {
    if (Test-Path $file.Path) {
        $size = [math]::Round((Get-Item $file.Path).Length / 1KB, 1)
        Write-Host "✅ $($file.Path) ($size KB) - $($file.Description)" -ForegroundColor Green
    } else {
        Write-Host "❌ $($file.Path) - $($file.Description)" -ForegroundColor Red
    }
}

# Usage Instructions
Write-Host "`n🎯 USAGE INSTRUCTIONS" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan

Write-Host "`n1. 🌐 Web-Based Visualizations:" -ForegroundColor White
Write-Host "   • doublets_overview.html - Bird's eye view with timeline" -ForegroundColor Gray
Write-Host "   • frontend\doublets_cytoscape.html - Interactive network analysis" -ForegroundColor Gray

Write-Host "`n2. 📊 Data Files:" -ForegroundColor White
Write-Host "   • doublets_heatmap_data.csv - Import to Excel/Google Sheets" -ForegroundColor Gray
Write-Host "   • frontend\cytoscape_doublets_network.json - Network data for analysis" -ForegroundColor Gray

Write-Host "`n3. 🎨 Graphics (if matplotlib installed):" -ForegroundColor White
Write-Host "   • biblical_doublets_overview.png - Publication-ready overview" -ForegroundColor Gray
Write-Host "   • biblical_doublets_detailed.png - Detailed dual-view heat map" -ForegroundColor Gray

Write-Host "`n🔧 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Explore the interactive Cytoscape network for detailed analysis" -ForegroundColor White
Write-Host "2. Use the HTML timeline to see doublet distribution patterns" -ForegroundColor White
Write-Host "3. Import CSV data into your preferred analysis tool" -ForegroundColor White
Write-Host "4. For publication graphics, install: pip install matplotlib seaborn" -ForegroundColor Yellow

# Integration Analysis
Write-Host "`n🔗 INTEGRATION FEATURES" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

Write-Host "The enhanced Cytoscape visualization includes:" -ForegroundColor White
Write-Host "  * Doublet nodes (diamond shapes) with category colors" -ForegroundColor Gray
Write-Host "  * Passage nodes (circles) with source colors" -ForegroundColor Gray
Write-Host "  * Book and chapter nodes for context" -ForegroundColor Gray
Write-Host "  * Interactive filtering by category and source" -ForegroundColor Gray
Write-Host "  * Node selection with detailed information panels" -ForegroundColor Gray
Write-Host "  * Multiple layout algorithms (Cose-Bilkent, Dagre, etc.)" -ForegroundColor Gray
Write-Host "  * Export capabilities (PNG, JSON)" -ForegroundColor Gray
Write-Host "  * Responsive design with sidebar controls" -ForegroundColor Gray

Write-Host "`nPress any key to continue..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
