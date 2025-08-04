#!/usr/bin/env python3
"""
Qdrant Setup Script for KJV Sources
Helps set up Qdrant vector database for storing and searching biblical data
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors gracefully."""
    print(f"\n🔄 {description}...")
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

def install_qdrant_dependencies(python_cmd):
    """Install Qdrant-related dependencies."""
    print("\n📦 Installing Qdrant dependencies...")
    
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

def setup_qdrant_collection(python_cmd):
    """Set up the Qdrant collection."""
    print("\n🔧 Setting up Qdrant collection...")
    
    # Set up the collection
    if not run_command(f"{python_cmd} kjv_cli.py qdrant setup", "Setting up Qdrant collection"):
        print("❌ Failed to set up Qdrant collection")
        return False
    
    return True

def upload_sample_data(python_cmd):
    """Upload sample data to test the setup."""
    print("\n📤 Uploading sample data to Qdrant...")
    
    # Upload Genesis as a test
    if not run_command(f"{python_cmd} kjv_cli.py qdrant upload genesis", "Uploading Genesis to Qdrant"):
        print("❌ Failed to upload sample data")
        return False
    
    return True

def test_qdrant_search(python_cmd):
    """Test Qdrant search functionality."""
    print("\n🔍 Testing Qdrant search functionality...")
    
    # Test semantic search
    if not run_command(f"{python_cmd} kjv_cli.py qdrant search-semantic 'God created' --limit 3", "Testing semantic search"):
        print("❌ Failed to test semantic search")
        return False
    
    # Test source search
    if not run_command(f"{python_cmd} kjv_cli.py qdrant search-by-source P --limit 3", "Testing source search"):
        print("❌ Failed to test source search")
        return False
    
    return True

def show_qdrant_stats(python_cmd):
    """Show Qdrant collection statistics."""
    print("\n📊 Qdrant Collection Statistics:")
    run_command(f"{python_cmd} kjv_cli.py qdrant stats", "Getting collection statistics")

def main():
    """Main setup function."""
    print("🚀 Qdrant Setup for KJV Sources")
    print("=" * 50)
    
    # Check Python availability
    python_cmd = check_python()
    if not python_cmd:
        return
    
    # Install Qdrant dependencies
    install_qdrant_dependencies(python_cmd)
    
    # Set up Qdrant collection
    if not setup_qdrant_collection(python_cmd):
        print("❌ Failed to set up Qdrant collection. Exiting.")
        return
    
    # Upload sample data
    if not upload_sample_data(python_cmd):
        print("❌ Failed to upload sample data. Exiting.")
        return
    
    # Test search functionality
    if not test_qdrant_search(python_cmd):
        print("❌ Failed to test search functionality.")
        return
    
    # Show final statistics
    show_qdrant_stats(python_cmd)
    
    print("\n🎉 Qdrant setup completed successfully!")
    print("\n📁 Your KJV sources data is now stored in Qdrant vector database")
    print("\n🔧 Available Qdrant commands:")
    print("  python kjv_cli.py qdrant setup --force     # Recreate collection")
    print("  python kjv_cli.py qdrant upload <book>     # Upload specific book")
    print("  python kjv_cli.py qdrant upload-all        # Upload all books")
    print("  python kjv_cli.py qdrant search-semantic 'query'  # Semantic search")
    print("  python kjv_cli.py qdrant search-by-source P       # Search by source")
    print("  python kjv_cli.py qdrant stats             # Show statistics")
    print("  python kjv_cli.py qdrant delete --force    # Delete collection")
    
    print("\n💡 Example searches:")
    print("  python kjv_cli.py qdrant search-semantic 'creation of the world'")
    print("  python kjv_cli.py qdrant search-semantic 'God said' --book Genesis")
    print("  python kjv_cli.py qdrant search-by-source J --limit 10")

if __name__ == "__main__":
    main() 