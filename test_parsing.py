#!/usr/bin/env python3
"""
Simple test script to verify parsing works after Unicode fixes
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_genesis_parsing():
    """Test parsing Genesis file."""
    print("Testing Genesis parsing...")
    
    try:
        # Import the parsing function
        from parse_wikitext import parse_wikitext_file
        
        # Check if file exists
        file_path = "wiki_markdown/Genesis.wikitext"
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return False
        
        # Parse the file
        print("Parsing Genesis.wikitext...")
        verses = parse_wikitext_file(file_path)
        
        if verses:
            print(f"Success! Found {len(verses)} verses")
            print(f"First verse: {verses[0]['text'][:100]}...")
            print(f"Sources in first verse: {verses[0]['source']}")
            return True
        else:
            print("Error: No verses found")
            return False
            
    except Exception as e:
        print(f"Error during parsing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_single_book_processing():
    """Test processing a single book."""
    print("\nTesting single book processing...")
    
    try:
        # Import the processing function
        from parse_wikitext import process_single_book
        
        # This will be interactive, so we'll just test the import
        print("Import successful - process_single_book function available")
        return True
        
    except Exception as e:
        print(f"Error importing process_single_book: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("KJV Sources Parsing Test")
    print("=" * 50)
    
    # Test 1: Basic parsing
    success1 = test_genesis_parsing()
    
    # Test 2: Function import
    success2 = test_single_book_processing()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Parsing test: {'PASSED' if success1 else 'FAILED'}")
    print(f"Function import: {'PASSED' if success2 else 'FAILED'}")
    
    if success1 and success2:
        print("\n✅ All tests passed! The Unicode fixes worked.")
        print("You can now run the full pipeline.")
    else:
        print("\n❌ Some tests failed. Check the errors above.") 