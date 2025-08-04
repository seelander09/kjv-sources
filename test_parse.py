#!/usr/bin/env python3
"""
Test script to verify parsing works without Unicode issues
"""

import sys
import os
from pathlib import Path

def test_parse_genesis():
    """Test parsing Genesis to see if it works."""
    print("Testing Genesis parsing...")
    
    try:
        # Import the parse function
        sys.path.append(str(Path(__file__).parent))
        from parse_wikitext import parse_wikitext_file
        
        # Test file path
        file_path = "wiki_markdown/Genesis.wikitext"
        
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return False
        
        # Parse the file
        verses = parse_wikitext_file(file_path)
        
        if verses:
            print(f"Success! Found {len(verses)} verses in Genesis")
            print(f"First verse: {verses[0]['text'][:100]}...")
            return True
        else:
            print("Error: No verses found")
            return False
            
    except Exception as e:
        print(f"Error during parsing: {e}")
        return False

if __name__ == "__main__":
    success = test_parse_genesis()
    if success:
        print("✅ Parsing test passed!")
    else:
        print("❌ Parsing test failed!") 