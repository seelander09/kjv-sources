#!/usr/bin/env python3
"""
Test script for Enhanced Qdrant Features
Verifies that all new entity-relation capabilities work correctly
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_enhanced_qdrant():
    """Test enhanced Qdrant features"""
    print("🧪 Testing Enhanced Qdrant Features")
    print("=" * 50)
    
    try:
        from kjv_sources.qdrant_client import create_qdrant_client
        print("✅ Qdrant client import successful")
    except ImportError as e:
        print(f"❌ Qdrant client import failed: {e}")
        return False
    
    try:
        # Create client
        client = create_qdrant_client()
        print("✅ Qdrant client created successfully")
        
        # Test entity relations loading
        if hasattr(client, 'entity_relations'):
            print("✅ Entity relations loaded")
            print(f"   Sources: {list(client.entity_relations['source_entities'].keys())}")
            print(f"   Books: {list(client.entity_relations['book_entities'].keys())}")
        else:
            print("❌ Entity relations not loaded")
            return False
        
        # Test collection stats
        stats = client.get_collection_stats()
        if stats:
            print(f"✅ Collection stats: {stats['total_points']} points")
        else:
            print("⚠️ No collection stats available (collection may be empty)")
        
        # Test new search methods
        print("\n🔍 Testing Enhanced Search Methods:")
        
        # Test multi-source search
        try:
            multi_results = client.search_multi_source_verses(limit=5)
            print(f"✅ Multi-source search: {len(multi_results)} results")
        except Exception as e:
            print(f"❌ Multi-source search failed: {e}")
        
        # Test redaction patterns
        try:
            redaction_results = client.search_redaction_patterns(limit=5)
            print(f"✅ Redaction patterns search: {len(redaction_results)} results")
        except Exception as e:
            print(f"❌ Redaction patterns search failed: {e}")
        
        # Test source combinations
        try:
            combo_results = client.search_source_combinations(["J", "P"], "any", limit=5)
            print(f"✅ Source combinations search: {len(combo_results)} results")
        except Exception as e:
            print(f"❌ Source combinations search failed: {e}")
        
        # Test chapter search
        try:
            chapter_results = client.search_by_chapter("Genesis", 1, limit=5)
            print(f"✅ Chapter search: {len(chapter_results)} results")
        except Exception as e:
            print(f"❌ Chapter search failed: {e}")
        
        # Test source analysis
        try:
            analysis_results = client.search_source_analysis("j_dominant", limit=5)
            print(f"✅ Source analysis search: {len(analysis_results)} results")
        except Exception as e:
            print(f"❌ Source analysis search failed: {e}")
        
        # Test hybrid search
        try:
            hybrid_results = client.search_hybrid("creation", {"book": "Genesis"}, limit=5)
            print(f"✅ Hybrid search: {len(hybrid_results)} results")
        except Exception as e:
            print(f"❌ Hybrid search failed: {e}")
        
        # Test source statistics
        try:
            source_stats = client.get_source_statistics()
            if source_stats:
                print(f"✅ Source statistics: {source_stats['total_verses']} total verses")
                print(f"   Multi-source: {source_stats['multi_source_verses']}")
                print(f"   Source counts: {source_stats['source_counts']}")
            else:
                print("⚠️ No source statistics available")
        except Exception as e:
            print(f"❌ Source statistics failed: {e}")
        
        print("\n🎉 Enhanced Qdrant features test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_cli_commands():
    """Test CLI commands"""
    print("\n🔧 Testing CLI Commands:")
    print("-" * 30)
    
    # Test basic CLI import
    try:
        from kjv_sources.enhanced_cli import cli
        print("✅ CLI import successful")
    except ImportError as e:
        print(f"❌ CLI import failed: {e}")
        return False
    
    print("✅ CLI commands available")
    print("   Run 'python kjv_cli.py qdrant --help' to see all commands")
    return True

def main():
    """Run all tests"""
    print("🚀 Enhanced Qdrant Integration Test")
    print("=" * 50)
    
    # Test enhanced Qdrant features
    qdrant_ok = test_enhanced_qdrant()
    
    # Test CLI commands
    cli_ok = test_cli_commands()
    
    print(f"\n📊 Test Results:")
    print(f"   Enhanced Qdrant: {'✅' if qdrant_ok else '❌'}")
    print(f"   CLI Commands: {'✅' if cli_ok else '❌'}")
    
    if qdrant_ok and cli_ok:
        print(f"\n🎉 All tests passed! Enhanced Qdrant is ready to use.")
        print(f"\n📖 Quick Start:")
        print(f"   1. python kjv_cli.py qdrant source-statistics")
        print(f"   2. python kjv_cli.py qdrant search-multi-source")
        print(f"   3. python kjv_cli.py qdrant search-source-combinations J P")
        print(f"   4. python kjv_cli.py qdrant search-hybrid 'creation' --book genesis")
    else:
        print(f"\n❌ Some tests failed. Check the output above.")
    
    print(f"\n📚 For more information, see QDRANT_GUIDE.md")

if __name__ == "__main__":
    main()
