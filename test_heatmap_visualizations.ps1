# Test Heatmap Visualizations PowerShell Script
# =============================================
# This script tests the doublet visualization tools and opens the results

Write-Host "Biblical Doublets Heatmap Testing Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Test 1: Run the simple overview (no external dependencies)
Write-Host "`n1. Testing Simple Doublets Overview..." -ForegroundColor Yellow
try {
    python simple_doublets_overview.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Simple overview completed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Simple overview failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error running simple overview: $_" -ForegroundColor Red
}

# Test 2: Run the minimal heatmap test
Write-Host "`n2. Testing Minimal Heatmap..." -ForegroundColor Yellow
try {
    python minimal_heatmap_test.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Minimal heatmap test completed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Minimal heatmap test failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error running minimal heatmap: $_" -ForegroundColor Red
}

# Test 3: Check for matplotlib and try full heatmap
Write-Host "`n3. Testing Full Matplotlib Heatmap..." -ForegroundColor Yellow
try {
    python test_visualization_libs.py
    
    # Try to run the full heatmap if matplotlib is available
    python -c "import matplotlib; print('Matplotlib available, testing full heatmap...')"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Matplotlib is available, running full heatmap..." -ForegroundColor Green
        python biblical_doublets_heatmap.py
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Full heatmap completed successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Full heatmap failed" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️  Matplotlib not available. To install:" -ForegroundColor Yellow
        Write-Host "   pip install matplotlib pandas numpy seaborn" -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ Error testing matplotlib: $_" -ForegroundColor Red
}

# Open generated files
Write-Host "`n4. Opening Generated Visualizations..." -ForegroundColor Yellow

# Check and open HTML file
if (Test-Path "doublets_overview.html") {
    Write-Host "✅ Opening HTML overview..." -ForegroundColor Green
    Start-Process "doublets_overview.html"
} else {
    Write-Host "❌ HTML overview not found" -ForegroundColor Red
}

# Check and open CSV file
if (Test-Path "doublets_heatmap_data.csv") {
    Write-Host "✅ CSV data file created" -ForegroundColor Green
    Write-Host "   You can open doublets_heatmap_data.csv in Excel for further analysis" -ForegroundColor Cyan
} else {
    Write-Host "❌ CSV data file not found" -ForegroundColor Red
}

# Check for matplotlib PNG files
$pngFiles = Get-ChildItem -Filter "biblical_doublets_*.png" -ErrorAction SilentlyContinue
if ($pngFiles.Count -gt 0) {
    Write-Host "✅ Found matplotlib PNG files:" -ForegroundColor Green
    foreach ($file in $pngFiles) {
        Write-Host "   $($file.Name)" -ForegroundColor Cyan
        Start-Process $file.FullName
    }
} else {
    Write-Host "⚠️  No matplotlib PNG files found (install matplotlib for graphics)" -ForegroundColor Yellow
}

Write-Host "`n📊 Summary of Available Visualizations:" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "1. 🌐 HTML Interactive Overview: doublets_overview.html" -ForegroundColor White
Write-Host "2. 📊 CSV Data Export: doublets_heatmap_data.csv" -ForegroundColor White
Write-Host "3. 📈 Text-based Console Output: See above" -ForegroundColor White
Write-Host "4. 🎨 Matplotlib Graphics: biblical_doublets_*.png (if available)" -ForegroundColor White

Write-Host "`n🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "1. View the HTML file for interactive exploration" -ForegroundColor White
Write-Host "2. Open CSV in Excel/Google Sheets for custom analysis" -ForegroundColor White
Write-Host "3. Install matplotlib for publication-quality graphics:" -ForegroundColor White
Write-Host "   pip install matplotlib seaborn numpy" -ForegroundColor Yellow

Write-Host "`nPress any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
