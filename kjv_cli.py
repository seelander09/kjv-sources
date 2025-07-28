#!/usr/bin/env python3
"""
KJV Sources CLI Launcher
Simple launcher script for the enhanced KJV sources CLI
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from kjv_sources.enhanced_cli import cli
    
    if __name__ == "__main__":
        cli()
        
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install required dependencies:")
    print("pip install click rich pandas")
    sys.exit(1)
except Exception as e:
    print(f"Error running CLI: {e}")
    sys.exit(1) 