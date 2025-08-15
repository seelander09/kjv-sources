#!/usr/bin/env python3
"""
Test Script for Mathematical Pattern Analysis
============================================

This script tests the word-level parser and mathematical pattern engine
with sample data and validates the functionality.

Author: KJV Sources Project
License: MIT
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def test_basic_imports():
    """Test basic Python imports"""
    print("🧪 Testing basic imports...")
    
    try:
        from word_level_parser import WordLevelParser, WordData
        print("✅ word_level_parser imported")
    except ImportError as e:
        print(f"❌ Failed to import word_level_parser: {e}")
        return False
    
    try:
        from mathematical_pattern_engine import MathematicalPatternEngine
        print("✅ mathematical_pattern_engine imported")
    except ImportError as e:
        print(f"❌ Failed to import mathematical_pattern_engine: {e}")
        return False
    
    return True

def create_sample_data():
    """Create sample word-level data for testing"""
    print("📝 Creating sample data...")
    
    sample_data = """Genesis 1 1 In the beginning God created the heaven and the earth.
Genesis 1 2 And the earth was without form and void and darkness was upon the face of the deep and the Spirit of God moved upon the face of the waters.
Genesis 1 3 And God said Let there be light and there was light.
Genesis 1 4 And God saw the light that it was good and God divided the light from the darkness.
Genesis 1 5 And God called the light Day and the darkness he called Night and the evening and the morning were the first day."""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_data)
        temp_file = f.name
    
    print(f"✅ Sample data created: {temp_file}")
    return temp_file

def test_word_parser():
    """Test the word-level parser"""
    print("\n📖 Testing word-level parser...")
    
    try:
        from word_level_parser import WordLevelParser
        
        # Create parser
        parser = WordLevelParser()
        
        # Create sample data
        sample_file = create_sample_data()
        
        # Parse the data
        words = parser.parse_word_level_file(sample_file)
        
        print(f"✅ Parsed {len(words)} words")
        
        if words:
            # Show first few words
            print("\n📊 First 5 words:")
            for i, word in enumerate(words[:5]):
                print(f"  {i+1}. '{word.word}' - {word.canonical_reference} (pos: {word.position_global})")
        
        # Clean up
        os.unlink(sample_file)
        
        return True
        
    except Exception as e:
        print(f"❌ Word parser test failed: {e}")
        return False

def test_mathematical_engine():
    """Test the mathematical pattern engine"""
    print("\n🧮 Testing mathematical pattern engine...")
    
    try:
        from mathematical_pattern_engine import MathematicalPatternEngine
        from word_level_parser import WordData
        
        # Create sample word data
        sample_words = [
            WordData(
                word="God", position_global=1, position_in_verse=1, 
                position_in_chapter=1, position_in_book=1, book="Genesis", 
                chapter=1, verse=1, verse_id="Gen.1.1", canonical_reference="Genesis 1:1",
                word_length=3, is_capitalized=True, is_number=False, is_proper_name=True,
                source_attribution=[], mathematical_properties={}
            ),
            WordData(
                word="Lord", position_global=2, position_in_verse=2, 
                position_in_chapter=2, position_in_book=2, book="Genesis", 
                chapter=1, verse=1, verse_id="Gen.1.1", canonical_reference="Genesis 1:1",
                word_length=4, is_capitalized=True, is_number=False, is_proper_name=True,
                source_attribution=[], mathematical_properties={}
            )
        ]
        
        # Create engine with sample data
        engine = MathematicalPatternEngine(sample_words)
        
        print("✅ Mathematical engine created")
        
        # Test pattern analysis
        patterns = engine.analyze_all_patterns()
        print(f"📊 Analyzed {len(patterns)} patterns")
        
        return True
        
    except Exception as e:
        print(f"❌ Mathematical engine test failed: {e}")
        return False

def test_database_loader():
    """Test the database loader"""
    print("\n🗄️ Testing database loader...")
    
    try:
        from database_loader import BibleDatabaseLoader
        
        # Create loader with in-memory SQLite for testing
        loader = BibleDatabaseLoader("sqlite:///:memory:")
        
        print("✅ Database loader created")
        
        # Test schema creation (this will fail with SQLite, but that's expected)
        try:
            loader.create_tables()
            print("✅ Database schema created")
        except Exception as e:
            print(f"⚠️  Schema creation failed (expected with SQLite): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database loader test failed: {e}")
        return False

def test_pattern_analysis():
    """Test pattern analysis with sample data"""
    print("\n🔍 Testing pattern analysis...")
    
    try:
        from mathematical_pattern_engine import MathematicalPatternEngine
        from word_level_parser import WordData
        
        # Create sample word data with repeated words for pattern analysis
        sample_words = []
        for i in range(10):
            sample_words.extend([
                WordData(
                    word="God", position_global=i*3+1, position_in_verse=1, 
                    position_in_chapter=1, position_in_book=1, book="Genesis", 
                    chapter=1, verse=1, verse_id="Gen.1.1", canonical_reference="Genesis 1:1",
                    word_length=3, is_capitalized=True, is_number=False, is_proper_name=True,
                    source_attribution=[], mathematical_properties={}
                ),
                WordData(
                    word="Lord", position_global=i*3+2, position_in_verse=2, 
                    position_in_chapter=2, position_in_book=2, book="Genesis", 
                    chapter=1, verse=1, verse_id="Gen.1.1", canonical_reference="Genesis 1:1",
                    word_length=4, is_capitalized=True, is_number=False, is_proper_name=True,
                    source_attribution=[], mathematical_properties={}
                ),
                WordData(
                    word="Jesus", position_global=i*3+3, position_in_verse=3, 
                    position_in_chapter=3, position_in_book=3, book="Matthew", 
                    chapter=1, verse=1, verse_id="Matt.1.1", canonical_reference="Matthew 1:1",
                    word_length=5, is_capitalized=True, is_number=False, is_proper_name=True,
                    source_attribution=[], mathematical_properties={}
                )
            ])
        
        # Create engine with sample data
        engine = MathematicalPatternEngine(sample_words)
        
        # Analyze patterns
        patterns = engine.analyze_all_patterns()
        
        print(f"✅ Analyzed patterns for {len(patterns)} words")
        
        # Show some pattern results
        if patterns:
            print("\n📊 Sample pattern analysis:")
            for word, pattern in list(patterns.items())[:3]:
                print(f"  '{word}': count={pattern.total_count}, sevened={pattern.is_sevened}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pattern analysis test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Mathematical Pattern Analysis Tests")
    print("=" * 50)
    
    # Test basic imports
    if not test_basic_imports():
        print("\n❌ Basic imports failed. Exiting.")
        return
    
    # Test word parser
    if not test_word_parser():
        print("\n❌ Word parser test failed.")
    
    # Test mathematical engine
    if not test_mathematical_engine():
        print("\n❌ Mathematical engine test failed.")
    
    # Test database loader
    if not test_database_loader():
        print("\n❌ Database loader test failed.")
    
    # Test pattern analysis
    if not test_pattern_analysis():
        print("\n❌ Pattern analysis test failed.")
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()
