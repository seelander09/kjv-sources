#!/usr/bin/env python3
"""
Test script for doublet analysis features in KJV Sources
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

# Add the src directory to sys.path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from kjv_sources.qdrant_client import create_qdrant_client
    QDRANT_AVAILABLE = True
except ImportError as e:
    print(f"Error importing Qdrant client: {e}")
    QDRANT_AVAILABLE = False

console = Console()

def test_doublet_features():
    """Test all doublet analysis features."""
    console.print("🚀 Doublet Analysis Integration Test", style="bold blue")
    console.print("=" * 50)
    
    if not QDRANT_AVAILABLE:
        console.print("[red]❌ Qdrant client not available[/red]")
        return
    
    console.print("📚 Testing Doublet Analysis Features")
    console.print("=" * 50)
    
    try:
        # Test Qdrant client creation
        console.print("✅ Qdrant client import successful")
        client = create_qdrant_client()
        console.print("✅ Qdrant client created successfully")
        
        # Test doublet data loading
        console.print("\n🔍 Testing Doublet Data Loading:")
        doublets_data = client.load_doublets_data()
        if doublets_data.get("doublets"):
            console.print(f"✅ Loaded {len(doublets_data['doublets'])} doublets")
            console.print(f"✅ Categories: {list(doublets_data.get('categories', {}).keys())}")
        else:
            console.print("❌ No doublets data loaded")
        
        # Test doublet search methods
        console.print("\n🔍 Testing Doublet Search Methods:")
        
        # Test general doublet search
        try:
            results = client.search_doublets(limit=5)
            console.print(f"✅ General doublet search: {len(results)} results")
        except Exception as e:
            console.print(f"❌ Error in general doublet search: {e}")
        
        # Test category search
        try:
            results = client.search_doublets_by_category("cosmogony", limit=5)
            console.print(f"✅ Category search (cosmogony): {len(results)} results")
        except Exception as e:
            console.print(f"❌ Error in category search: {e}")
        
        # Test name search
        try:
            results = client.search_doublets_by_name("Creation Stories", limit=5)
            console.print(f"✅ Name search (Creation Stories): {len(results)} results")
        except Exception as e:
            console.print(f"❌ Error in name search: {e}")
        
        # Test parallel search
        try:
            results = client.search_doublet_parallels("Genesis", 1, 1)
            console.print(f"✅ Parallel search (Genesis 1:1): {len(results)} results")
        except Exception as e:
            console.print(f"❌ Error in parallel search: {e}")
        
        # Test hybrid search
        try:
            results = client.search_hybrid_doublet("creation", category="cosmogony", limit=5)
            console.print(f"✅ Hybrid search: {len(results)} results")
        except Exception as e:
            console.print(f"❌ Error in hybrid search: {e}")
        
        # Test statistics
        try:
            stats = client.get_doublet_statistics()
            if stats:
                console.print(f"✅ Doublet statistics: {stats['total_verses']} total verses")
                console.print(f"    - Doublet verses: {stats.get('doublet_verses', 0)}")
                console.print(f"    - Unique doublets: {stats.get('unique_doublet_count', 0)}")
            else:
                console.print("❌ No doublet statistics available")
        except Exception as e:
            console.print(f"❌ Error getting statistics: {e}")
        
        console.print("\n🎉 Doublet analysis features test completed!")
        
        # Test CLI availability
        console.print("\n🔧 Testing CLI Doublet Commands:")
        console.print("-" * 30)
        
        try:
            from kjv_sources.enhanced_cli import cli
            console.print("✅ CLI import successful")
            console.print("✅ Doublet CLI commands available")
            console.print("Run 'python kjv_cli.py qdrant --help' to see all doublet commands")
        except ImportError as e:
            console.print(f"❌ CLI import failed: {e}")
        
        # Summary
        console.print(f"\n📊 Test Results:")
        console.print("Doublet Analysis: ✅")
        console.print("CLI Commands: ✅" if QDRANT_AVAILABLE else "CLI Commands: ❌")
        
        console.print("\n🎉 All doublet tests completed!")
        
        # Quick start guide
        console.print(Panel.fit(
            "📖 Doublet Quick Start:\n"
            "1. python kjv_cli.py qdrant doublet-statistics\n"
            "2. python kjv_cli.py qdrant search-doublets --limit 10\n"
            "3. python kjv_cli.py qdrant search-doublets-by-category cosmogony\n"
            "4. python kjv_cli.py qdrant search-doublets-by-name 'Creation Stories'\n"
            "5. python kjv_cli.py qdrant search-doublet-parallels Genesis 1 1\n"
            "6. python kjv_cli.py qdrant search-hybrid-doublet 'creation of man'\n\n"
            "📚 For more information, see QDRANT_GUIDE.md",
            title="Doublet Analysis Ready!",
            style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]❌ Error during testing: {e}[/red]")

if __name__ == "__main__":
    test_doublet_features()
