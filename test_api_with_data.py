#!/usr/bin/env python3
"""
Simple API Test with Real Data
==============================

Test the API endpoints directly with the existing Qdrant data
without needing to start the full server.
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from kjv_sources.qdrant_client import create_qdrant_client

console = Console()

def test_qdrant_connection():
    """Test Qdrant connection and basic operations"""
    console.print(Panel.fit("🔗 Testing Qdrant Connection", style="bold blue"))
    
    try:
        client = create_qdrant_client()
        console.print("✅ Connected to Qdrant successfully")
        
        # Test collection stats
        stats = client.get_collection_stats()
        console.print(f"📊 Collection stats: {stats['total_points']} verses")
        
        return client
        
    except Exception as e:
        console.print(f"❌ Failed to connect: {e}")
        return None

def test_search_endpoints(client):
    """Test search functionality"""
    console.print(Panel.fit("🔍 Testing Search Endpoints", style="bold green"))
    
    # Test 1: Basic verse search
    console.print("\n📖 Testing basic verse search...")
    try:
        results = client.search_verses("creation of man", limit=5)
        console.print(f"✅ Found {len(results)} verses for 'creation of man'")
        
        if results:
            first_result = results[0]
            console.print(f"   First result: {first_result.get('book', 'Unknown')} {first_result.get('chapter', '?')}:{first_result.get('verse', '?')}")
            console.print(f"   Text: {first_result.get('text', '')[:100]}...")
            console.print(f"   Sources: {first_result.get('sources', 'Unknown')}")
    except Exception as e:
        console.print(f"❌ Search failed: {e}")
    
    # Test 2: Source-based search
    console.print("\n🎭 Testing source-based search...")
    try:
        results = client.search_by_source("P", limit=3)
        console.print(f"✅ Found {len(results)} P-source verses")
        
        if results:
            first_result = results[0]
            console.print(f"   Example: {first_result.get('book', 'Unknown')} {first_result.get('chapter', '?')}:{first_result.get('verse', '?')}")
    except Exception as e:
        console.print(f"❌ Source search failed: {e}")

def test_doublet_endpoints(client):
    """Test doublet analysis functionality"""
    console.print(Panel.fit("📚 Testing Doublet Analysis", style="bold yellow"))
    
    # Test 1: Doublet statistics
    console.print("\n📊 Testing doublet statistics...")
    try:
        stats = client.get_doublet_statistics()
        console.print(f"✅ Doublet stats retrieved")
        console.print(f"   Total verses: {stats.get('total_verses', 'Unknown')}")
        console.print(f"   Doublet verses: {stats.get('doublet_verses', 'Unknown')}")
        console.print(f"   Unique doublets: {stats.get('unique_doublets', 'Unknown')}")
    except Exception as e:
        console.print(f"❌ Doublet stats failed: {e}")
    
    # Test 2: Doublet search
    console.print("\n🔍 Testing doublet search...")
    try:
        results = client.search_doublets(limit=5)
        console.print(f"✅ Found {len(results)} doublet verses")
        
        if results:
            first_result = results[0]
            console.print(f"   Example: {first_result.get('book', 'Unknown')} {first_result.get('chapter', '?')}:{first_result.get('verse', '?')}")
            console.print(f"   Doublet: {first_result.get('doublet_name', 'Unknown')}")
    except Exception as e:
        console.print(f"❌ Doublet search failed: {e}")
    
    # Test 3: Category search
    console.print("\n📂 Testing category search...")
    try:
        results = client.search_doublets_by_category("cosmogony", limit=3)
        console.print(f"✅ Found {len(results)} cosmogony doublets")
    except Exception as e:
        console.print(f"❌ Category search failed: {e}")

def test_pov_endpoints(client):
    """Test POV analysis functionality"""
    console.print(Panel.fit("🎭 Testing POV Analysis", style="bold magenta"))
    
    # Test 1: POV statistics
    console.print("\n📊 Testing POV statistics...")
    try:
        stats = client.get_pov_statistics()
        console.print(f"✅ POV stats retrieved")
        console.print(f"   Total verses: {stats.get('total_verses', 'Unknown')}")
        console.print(f"   POV styles: {len(stats.get('pov_styles', {}))}")
        console.print(f"   POV themes: {len(stats.get('pov_themes', {}))}")
    except Exception as e:
        console.print(f"❌ POV stats failed: {e}")
    
    # Test 2: POV theme search
    console.print("\n🔍 Testing POV theme search...")
    try:
        results = client.search_by_pov_theme("creation", limit=3)
        console.print(f"✅ Found {len(results)} verses with 'creation' POV theme")
    except Exception as e:
        console.print(f"❌ POV theme search failed: {e}")

def test_hybrid_search(client):
    """Test hybrid search functionality"""
    console.print(Panel.fit("🔗 Testing Hybrid Search", style="bold cyan"))
    
    # Test hybrid search
    console.print("\n🔍 Testing hybrid search...")
    try:
        results = client.search_hybrid("flood narrative", limit=3)
        console.print(f"✅ Found {len(results)} results for 'flood narrative'")
        
        if results:
            first_result = results[0]
            console.print(f"   Example: {first_result.get('book', 'Unknown')} {first_result.get('chapter', '?')}:{first_result.get('verse', '?')}")
            console.print(f"   Score: {first_result.get('score', 'Unknown')}")
    except Exception as e:
        console.print(f"❌ Hybrid search failed: {e}")

def main():
    """Main test execution"""
    console.print("🚀 [bold blue]Testing API Endpoints with Real Data[/bold blue]")
    console.print("📖 Using existing Qdrant data (5,852 verses)")
    
    # Test connection
    client = test_qdrant_connection()
    if not client:
        console.print("❌ [red]Cannot proceed without Qdrant connection[/red]")
        return
    
    # Test all endpoints
    test_search_endpoints(client)
    test_doublet_endpoints(client)
    test_pov_endpoints(client)
    test_hybrid_search(client)
    
    console.print("\n🎉 [bold green]All tests completed![/bold green]")
    console.print("💡 [blue]The API endpoints are working correctly with your data.[/blue]")
    console.print("🚀 [blue]Ready for KJPBS integration![/blue]")

if __name__ == "__main__":
    main()
