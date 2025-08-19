# Setup Additional Sources Pipeline
# =================================
# This script runs the complete pipeline to add the Deuteronomist source
# and additional Wikiversity pages to the KJV Sources project.

param(
    [switch]$SkipDownload,
    [switch]$SkipProcessing,
    [switch]$SkipIngestion,
    [int]$Priority = 4
)

Write-Host "🚀 KJV Sources - Additional Sources Pipeline" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "parse_wikitext.py")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

# Step 1: Download additional Wikiversity pages
if (-not $SkipDownload) {
    Write-Host "📥 Step 1: Downloading additional Wikiversity pages..." -ForegroundColor Yellow
    
    if (-not (Test-Path "download_additional_sources.py")) {
        Write-Host "❌ Error: download_additional_sources.py not found" -ForegroundColor Red
        exit 1
    }
    
    try {
        python download_additional_sources.py
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Additional sources downloaded successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Error downloading additional sources" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ Error running download script: $_" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
} else {
    Write-Host "⏭️  Skipping download step" -ForegroundColor Cyan
}

# Step 2: Process Deuteronomist source
if (-not $SkipProcessing) {
    Write-Host "🔧 Step 2: Processing Deuteronomist source..." -ForegroundColor Yellow
    
    if (-not (Test-Path "process_deuteronomist_source.py")) {
        Write-Host "❌ Error: process_deuteronomist_source.py not found" -ForegroundColor Red
        exit 1
    }
    
    try {
        python process_deuteronomist_source.py
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Deuteronomist source processed successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Error processing Deuteronomist source" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ Error running processing script: $_" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
} else {
    Write-Host "⏭️  Skipping processing step" -ForegroundColor Cyan
}

# Step 3: Ingest additional sources into vector database
if (-not $SkipIngestion) {
    Write-Host "🗄️  Step 3: Ingesting additional sources into vector database..." -ForegroundColor Yellow
    
    if (-not (Test-Path "ingest_additional_sources.py")) {
        Write-Host "❌ Error: ingest_additional_sources.py not found" -ForegroundColor Red
        exit 1
    }
    
    try {
        python ingest_additional_sources.py
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Additional sources ingested successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Error ingesting additional sources" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ Error running ingestion script: $_" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
} else {
    Write-Host "⏭️  Skipping ingestion step" -ForegroundColor Cyan
}

# Step 4: Update existing data with Deuteronomist source
Write-Host "🔄 Step 4: Updating existing data with Deuteronomist source..." -ForegroundColor Yellow

try {
    # Process Deuteronomy with updated color mapping
    python parse_wikitext.py deuteronomy
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Deuteronomy updated with Deuteronomist source" -ForegroundColor Green
    } else {
        Write-Host "❌ Error updating Deuteronomy" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error updating Deuteronomy: $_" -ForegroundColor Red
}

Write-Host ""

# Step 5: Generate summary report
Write-Host "📊 Step 5: Generating summary report..." -ForegroundColor Yellow

$summary = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    steps_completed = @()
    files_created = @()
    errors = @()
}

if (-not $SkipDownload) {
    $summary.steps_completed += "Download additional Wikiversity pages"
    if (Test-Path "wiki_markdown/additional_sources_metadata.json") {
        $summary.files_created += "additional_sources_metadata.json"
    }
}

if (-not $SkipProcessing) {
    $summary.steps_completed += "Process Deuteronomist source"
    if (Test-Path "output/deuteronomist_verses.csv") {
        $summary.files_created += "deuteronomist_verses.csv"
    }
    if (Test-Path "output/deuteronomist_analysis.jsonl") {
        $summary.files_created += "deuteronomist_analysis.jsonl"
    }
}

if (-not $SkipIngestion) {
    $summary.steps_completed += "Ingest additional sources into vector database"
    if (Test-Path "lightrag_data/additional_sources_ingestion_summary.json") {
        $summary.files_created += "additional_sources_ingestion_summary.json"
    }
}

# Save summary
$summary | ConvertTo-Json -Depth 3 | Out-File -FilePath "additional_sources_pipeline_summary.json" -Encoding UTF8

Write-Host "✅ Pipeline completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "  Steps completed: $($summary.steps_completed.Count)" -ForegroundColor White
Write-Host "  Files created: $($summary.files_created.Count)" -ForegroundColor White
Write-Host "  Summary saved to: additional_sources_pipeline_summary.json" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Test the updated CLI with: python -m src.kjv_sources.cli rich-preview deuteronomy --source D" -ForegroundColor White
Write-Host "  2. Check the vector database with: python lightrag_query.py" -ForegroundColor White
Write-Host "  3. Run the RAG API server: python rag_api_server.py" -ForegroundColor White
Write-Host ""
