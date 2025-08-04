#!/usr/bin/env python3
"""
KJV Sources Data Pipeline
Comprehensive pipeline for downloading, parsing, and preparing KJV sources data
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors gracefully."""
    print(f"\n[COMMAND] {description}...")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
        else:
            print(f"❌ {description} failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False
    
    return True

def check_python():
    """Check if Python is available and working."""
    python_commands = ['python', 'python3', 'py']
    
    for cmd in python_commands:
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Found Python: {result.stdout.strip()}")
                return cmd
        except:
            continue
    
    print("❌ Python not found. Please install Python 3.8+ and ensure it's in your PATH.")
    return None

def install_dependencies(python_cmd):
    """Install required Python dependencies."""
    print("\n[DEPENDENCIES] Installing dependencies...")
    
    requirements = [
        'requests',
        'beautifulsoup4', 
        'lxml',
        'pandas',
        'click',
        'rich'
    ]
    
    for package in requirements:
        print(f"Installing {package}...")
        if not run_command(f"{python_cmd} -m pip install {package}", f"Installing {package}"):
            print(f"Warning: Failed to install {package}")
    
    print("✅ Dependencies installation completed")

def install_qdrant_dependencies(python_cmd):
    """Install Qdrant-related dependencies."""
    print("\n[QDRANT DEPENDENCIES] Installing Qdrant dependencies...")
    
    qdrant_packages = [
        'qdrant-client',
        'sentence-transformers',
        'numpy'
    ]
    
    for package in qdrant_packages:
        print(f"Installing {package}...")
        if not run_command(f"{python_cmd} -m pip install {package}", f"Installing {package}"):
            print(f"Warning: Failed to install {package}")
    
    print("✅ Qdrant dependencies installation completed")

def download_wikiversity_data(python_cmd):
    """Download KJV sources data from Wikiversity."""
    print("\n[DOWNLOAD] Downloading KJV sources data from Wikiversity...")
    
    if os.path.exists("wiki_markdown"):
        print("📁 Wiki markdown directory already exists, skipping download")
        return True
    
    return run_command(f"{python_cmd} download_wikiversity_md.py", "Downloading Wikiversity data")

def process_books(python_cmd, books=None):
    """Process the downloaded books to create CSV and training data."""
    if books is None:
        books = ['genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy']
    
    print(f"\n[PROCESS] Processing books: {', '.join(books)}")
    
    for book in books:
        print(f"\n[BOOK] Processing {book.title()}...")
        if not run_command(f"{python_cmd} parse_wikitext.py {book}", f"Processing {book}"):
            print(f"Warning: Failed to process {book}")
    
    print("✅ Book processing completed")

def create_csv_exports(python_cmd):
    """Create CSV exports for all books."""
    print("\n[CSV EXPORTS] Creating CSV exports...")
    
    books = ['genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy']
    
    for book in books:
        print(f"Exporting {book.title()} to CSV...")
        run_command(f"{python_cmd} kjv_cli.py export-csv {book} --format simple", f"Exporting {book} (simple)")
        run_command(f"{python_cmd} kjv_cli.py export-csv {book} --format llm", f"Exporting {book} (LLM)")
    
    # Create combined CSV
    print("Creating combined CSV...")
    run_command(f"{python_cmd} kjv_cli.py combine --output kjv_sources_combined.csv", "Creating combined CSV")
    
    print("✅ CSV exports completed")

def setup_qdrant(python_cmd):
    """Set up Qdrant vector database."""
    print("\n[QDRANT SETUP] Setting up Qdrant vector database...")
    
    # Install Qdrant dependencies
    install_qdrant_dependencies(python_cmd)
    
    # Set up collection
    if not run_command(f"{python_cmd} kjv_cli.py qdrant setup", "Setting up Qdrant collection"):
        print("❌ Failed to set up Qdrant collection")
        return False
    
    return True

def upload_to_qdrant(python_cmd, books=None):
    """Upload data to Qdrant vector database."""
    if books is None:
        books = ['genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy']
    
    print(f"\n[UPLOAD] Uploading books to Qdrant: {', '.join(books)}")
    
    for book in books:
        print(f"Uploading {book.title()} to Qdrant...")
        if not run_command(f"{python_cmd} kjv_cli.py qdrant upload {book}", f"Uploading {book} to Qdrant"):
            print(f"Warning: Failed to upload {book} to Qdrant")
    
    # Show final stats
    print("\n[QDRANT STATS] Qdrant Collection Statistics:")
    run_command(f"{python_cmd} kjv_cli.py qdrant stats", "Getting Qdrant statistics")
    
    print("✅ Qdrant upload completed")

def show_data_summary(python_cmd):
    """Show a summary of the processed data."""
    print("\n[SUMMARY] Data Summary:")
    run_command(f"{python_cmd} kjv_cli.py list-books", "Listing available books")
    
    books = ['genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy']
    for book in books:
        print(f"\n[STATS] Statistics for {book.title()}:")
        run_command(f"{python_cmd} kjv_cli.py stats {book}", f"Showing stats for {book}")

def main():
    """Main pipeline function."""
    print("[PIPELINE] KJV Sources Data Pipeline")
    print("=" * 50)
    
    # Check Python availability
    python_cmd = check_python()
    if not python_cmd:
        return
    
    # Install dependencies
    install_dependencies(python_cmd)
    
    # Download data
    if not download_wikiversity_data(python_cmd):
        print("❌ Failed to download data. Exiting.")
        return
    
    # Process books
    process_books(python_cmd)
    
    # Create CSV exports
    create_csv_exports(python_cmd)
    
    # Show summary
    show_data_summary(python_cmd)
    
    # Ask about Qdrant setup
    print("\n" + "=" * 50)
    print("[QDRANT SETUP] Qdrant Vector Database Setup")
    print("=" * 50)
    
    setup_qdrant_choice = input("\nWould you like to set up Qdrant vector database for semantic search? (y/n): ").lower().strip()
    
    if setup_qdrant_choice in ['y', 'yes']:
        # Set up Qdrant
        if setup_qdrant(python_cmd):
            # Ask about uploading data
            upload_choice = input("\nWould you like to upload your data to Qdrant? (y/n): ").lower().strip()
            
            if upload_choice in ['y', 'yes']:
                upload_to_qdrant(python_cmd)
                
                print("\n[SUCCESS] Qdrant setup completed!")
                print("\n[SEARCH] Try these semantic searches:")
                print("  python kjv_cli.py qdrant search-semantic 'God created'")
                print("  python kjv_cli.py qdrant search-by-source P")
                print("  python kjv_cli.py qdrant search-semantic 'covenant' --book Genesis")
            else:
                print("\n[INFO] You can upload data later with:")
                print("  python kjv_cli.py qdrant upload-all")
        else:
            print("\n[ERROR] Qdrant setup failed. You can try again later with:")
            print("  python setup_qdrant.py")
    else:
        print("\n[INFO] You can set up Qdrant later with:")
        print("  python setup_qdrant.py")
    
    print("\n[SUCCESS] Pipeline completed successfully!")
    print("\n[FILES] Generated files:")
    print("  - output/ (processed data)")
    print("  - *.csv (CSV exports)")
    print("  - kjv_sources_combined.csv (combined data)")
    print("\n[COMMANDS] Available commands:")
    print("  python kjv_cli.py view <book> -- View data")
    print("  python kjv_cli.py stats <book> -- Show statistics")
    print("  python kjv_cli.py search <book> -- Search verses")
    print("  python kjv_cli.py export-csv <book> -- Export to CSV")
    print("  python kjv_cli.py qdrant search-semantic 'query' -- Semantic search")

if __name__ == "__main__":
    main() 