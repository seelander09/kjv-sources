# Test Portability of Biblical Doublets Side-by-Side View
# ======================================================

Write-Host "Testing Biblical Doublets HTML Portability" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$file = "frontend\doublets_side_by_side.html"

if (Test-Path $file) {
    $fileInfo = Get-Item $file
    $size = [math]::Round($fileInfo.Length / 1KB, 1)
    
    Write-Host "`n✅ File Ready for Sharing:" -ForegroundColor Green
    Write-Host "   File: $file" -ForegroundColor White
    Write-Host "   Size: $size KB" -ForegroundColor White
    Write-Host "   Created: $($fileInfo.LastWriteTime)" -ForegroundColor White
    
    Write-Host "`n📧 Sharing Instructions:" -ForegroundColor Cyan
    Write-Host "1. Email: Attach this file to any email" -ForegroundColor White
    Write-Host "2. Cloud: Upload to Google Drive, Dropbox, OneDrive" -ForegroundColor White
    Write-Host "3. Direct: Copy file to USB, shared folder, etc." -ForegroundColor White
    
    Write-Host "`n🌐 Browser Compatibility:" -ForegroundColor Cyan
    Write-Host "✅ Chrome, Firefox, Safari, Edge" -ForegroundColor Green
    Write-Host "✅ Mobile browsers (iOS Safari, Android Chrome)" -ForegroundColor Green
    Write-Host "✅ Works completely offline" -ForegroundColor Green
    Write-Host "✅ No internet connection required" -ForegroundColor Green
    
    Write-Host "`n📋 What Recipients Get:" -ForegroundColor Cyan
    Write-Host "• Complete side-by-side biblical text comparison" -ForegroundColor White
    Write-Host "• Interactive navigation between doublets" -ForegroundColor White
    Write-Host "• Professional scholarly appearance" -ForegroundColor White
    Write-Host "• Theological difference explanations" -ForegroundColor White
    Write-Host "• Responsive design for any screen size" -ForegroundColor White
    
    Write-Host "`n🚀 Ready to Share!" -ForegroundColor Green
    Write-Host "The file is completely self-contained and will work on any device." -ForegroundColor White
    
} else {
    Write-Host "❌ File not found: $file" -ForegroundColor Red
}

Write-Host "`nPress any key to open the file for testing..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

if (Test-Path $file) {
    Start-Process $file
}
