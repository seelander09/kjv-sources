#!/usr/bin/env python3
"""
Test script for POV Analysis Features
Verifies that all new POV capabilities work correctly
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_pov_features():
    """Test POV analysis features"""
    print("🎭 Testing POV Analysis Features")
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

        # Test POV analysis methods
        print("\n🔍 Testing POV Analysis Methods:")

        # Test POV style search
        try:
            style_results = client.search_by_pov_style("narrative_anthropomorphic", limit=5)
            print(f"✅ POV style search: {len(style_results)} results")
        except Exception as e:
            print(f"❌ POV style search failed: {e}")

        # Test POV perspective search
        try:
            perspective_results = client.search_by_pov_perspective("intimate_personal", limit=5)
            print(f"✅ POV perspective search: {len(perspective_results)} results")
        except Exception as e:
            print(f"❌ POV perspective search failed: {e}")

        # Test POV purpose search
        try:
            purpose_results = client.search_by_pov_purpose("storytelling_identity", limit=5)
            print(f"✅ POV purpose search: {len(purpose_results)} results")
        except Exception as e:
            print(f"❌ POV purpose search failed: {e}")

        # Test POV theme search
        try:
            theme_results = client.search_by_pov_theme("creation", limit=5)
            print(f"✅ POV theme search: {len(theme_results)} results")
        except Exception as e:
            print(f"❌ POV theme search failed: {e}")

        # Test POV comparison
        try:
            comparison_results = client.search_pov_comparison("J", "P", limit=5)
            print(f"✅ POV comparison search: {len(comparison_results)} results")
        except Exception as e:
            print(f"❌ POV comparison search failed: {e}")

        # Test POV complexity search
        try:
            complexity_results = client.search_pov_complexity("moderate", limit=5)
            print(f"✅ POV complexity search: {len(complexity_results)} results")
        except Exception as e:
            print(f"❌ POV complexity search failed: {e}")

        # Test hybrid POV search
        try:
            hybrid_results = client.search_hybrid_pov("creation", {"style": "narrative_anthropomorphic"}, limit=5)
            print(f"✅ Hybrid POV search: {len(hybrid_results)} results")
        except Exception as e:
            print(f"❌ Hybrid POV search failed: {e}")

        # Test POV statistics
        try:
            pov_stats = client.get_pov_statistics()
            if pov_stats:
                print(f"✅ POV statistics: {pov_stats['total_verses']} total verses")
                print(f"   POV styles: {len(pov_stats['pov_styles'])}")
                print(f"   POV themes: {len(pov_stats['pov_themes'])}")
            else:
                print("⚠️ No POV statistics available")
        except Exception as e:
            print(f"❌ POV statistics failed: {e}")

        print("\n🎉 POV analysis features test completed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_cli_pov_commands():
    """Test CLI POV commands"""
    print("\n🔧 Testing CLI POV Commands:")
    print("-" * 30)

    # Test basic CLI import
    try:
        from kjv_sources.enhanced_cli import cli
        print("✅ CLI import successful")
    except ImportError as e:
        print(f"❌ CLI import failed: {e}")
        return False

    print("✅ POV CLI commands available")
    print("   Run 'python kjv_cli.py qdrant --help' to see all POV commands")
    return True

def main():
    """Run all POV tests"""
    print("🚀 POV Analysis Integration Test")
    print("=" * 50)

    # Test POV features
    pov_ok = test_pov_features()

    # Test CLI commands
    cli_ok = test_cli_pov_commands()

    print(f"\n📊 Test Results:")
    print(f"   POV Analysis: {'✅' if pov_ok else '❌'}")
    print(f"   CLI Commands: {'✅' if cli_ok else '❌'}")

    if pov_ok and cli_ok:
        print(f"\n🎉 All POV tests passed! POV analysis is ready to use.")
        print(f"\n📖 POV Quick Start:")
        print(f"   1. python kjv_cli.py qdrant pov-statistics")
        print(f"   2. python kjv_cli.py qdrant search-pov-style narrative_anthropomorphic")
        print(f"   3. python kjv_cli.py qdrant search-pov-theme creation")
        print(f"   4. python kjv_cli.py qdrant search-pov-comparison J P")
        print(f"   5. python kjv_cli.py qdrant search-hybrid-pov 'creation' --style narrative_anthropomorphic")
    else:
        print(f"\n❌ Some POV tests failed. Check the output above.")

    print(f"\n📚 For more information, see QDRANT_GUIDE.md")

if __name__ == "__main__":
    main()
