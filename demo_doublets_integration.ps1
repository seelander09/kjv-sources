# Biblical Doublets Integration Demo
# ==================================
# Simple demonstration of the enhanced visualization system

Write-Host "Biblical Doublets Visualization Integration Demo" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Check what we have
Write-Host "`nChecking generated files..." -ForegroundColor Yellow

$files = @(
    @{ Path = "doublets_overview.html"; Name = "Simple HTML Overview" },
    @{ Path = "frontend\doublets_cytoscape.html"; Name = "Enhanced Cytoscape Network" },
    @{ Path = "frontend\cytoscape_doublets_network.json"; Name = "Network Data" },
    @{ Path = "doublets_heatmap_data.csv"; Name = "Heat Map Data" }
)

foreach ($file in $files) {
    if (Test-Path $file.Path) {
        $size = [math]::Round((Get-Item $file.Path).Length / 1KB, 1)
        Write-Host "✅ $($file.Name): $($file.Path) ($size KB)" -ForegroundColor Green
    } else {
        Write-Host "❌ $($file.Name): $($file.Path)" -ForegroundColor Red
    }
}

Write-Host "`nAvailable Visualizations:" -ForegroundColor Cyan
Write-Host "1. Enhanced Cytoscape Network - frontend\doublets_cytoscape.html" -ForegroundColor White
Write-Host "2. Simple HTML Overview - doublets_overview.html" -ForegroundColor White
Write-Host "3. Original Cytoscape - frontend\cytoscape_visualization.html" -ForegroundColor White

Write-Host "`nKey Features of the Enhanced Integration:" -ForegroundColor Cyan
Write-Host "- Interactive network visualization with doublet focus" -ForegroundColor Gray
Write-Host "- Diamond-shaped doublet nodes with category colors" -ForegroundColor Gray
Write-Host "- Circular passage nodes with source colors" -ForegroundColor Gray
Write-Host "- Filtering by category and documentary source" -ForegroundColor Gray
Write-Host "- Multiple layout algorithms" -ForegroundColor Gray
Write-Host "- Export capabilities (PNG, JSON)" -ForegroundColor Gray
Write-Host "- Responsive sidebar with controls and statistics" -ForegroundColor Gray

Write-Host "`nPress Enter to open the enhanced Cytoscape visualization..." -ForegroundColor Green
Read-Host

if (Test-Path "frontend\doublets_cytoscape.html") {
    Start-Process "frontend\doublets_cytoscape.html"
    Write-Host "Opening enhanced Cytoscape visualization..." -ForegroundColor Green
} else {
    Write-Host "Enhanced visualization not found. Run: python cytoscape_doublets_integration.py" -ForegroundColor Red
}
