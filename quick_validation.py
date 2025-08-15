#!/usr/bin/env python3
"""
Quick Validation Script
======================

Quick validation of the mathematical pattern analysis system.

Author: KJV Sources Project
License: MIT
"""

import sys
from pathlib import Path

def main():
    """Quick validation of the system"""
    print("🔍 Quick Validation of Mathematical Pattern Analysis System")
    print("=" * 60)
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Check if files exist
    files_to_check = [
        "word_level_parser.py",
        "mathematical_pattern_engine.py",
        "database_loader.py",
        "database_schema.sql"
    ]
    
    print("\n📁 File existence check:")
    for file in files_to_check:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
    
    # Try to import modules
    print("\n📦 Module import check:")
    try:
        from word_level_parser import WordLevelParser
        print("  ✅ word_level_parser")
    except ImportError as e:
        print(f"  ❌ word_level_parser: {e}")
    
    try:
        from mathematical_pattern_engine import MathematicalPatternEngine
        print("  ✅ mathematical_pattern_engine")
    except ImportError as e:
        print(f"  ❌ mathematical_pattern_engine: {e}")
    
    try:
        from database_loader import BibleDatabaseLoader
        print("  ✅ database_loader")
    except ImportError as e:
        print(f"  ❌ database_loader: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Quick validation completed!")

if __name__ == "__main__":
    main()
