#!/usr/bin/env python3
"""
Quick import test for RAG API Server
===================================

This script tests that all required modules can be imported successfully
before attempting to start the full API server.

Usage:
    python test_api_imports.py
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()

def test_imports():
    """Test all critical imports for the API server"""
    console.print(Panel.fit("🧪 Testing API Server Imports", style="bold blue"))
    
    tests = []
    
    # Test 1: FastAPI dependencies
    try:
        import fastapi
        import uvicorn
        import pydantic
        tests.append(("FastAPI Framework", True, f"FastAPI {fastapi.__version__}"))
    except ImportError as e:
        tests.append(("FastAPI Framework", False, f"Import error: {e}"))
    
    # Test 2: HTTP and networking
    try:
        import httpx
        import aiohttp
        tests.append(("HTTP Clients", True, "httpx and aiohttp available"))
    except ImportError as e:
        tests.append(("HTTP Clients", False, f"Import error: {e}"))
    
    # Test 3: Rich console (for pretty output)
    try:
        from rich.console import Console
        from rich.table import Table
        tests.append(("Rich Console", True, "Rich library available"))
    except ImportError as e:
        tests.append(("Rich Console", False, f"Import error: {e}"))
    
    # Test 4: Existing KJV Sources modules
    try:
        sys.path.append(str(Path(__file__).parent / "src"))
        from kjv_sources.qdrant_client import QdrantClient
        tests.append(("QdrantClient", True, "KJV Sources Qdrant client available"))
    except ImportError as e:
        tests.append(("QdrantClient", False, f"Import error: {e}"))
    
    # Test 5: Entity relations file
    try:
        entity_relations_path = Path(__file__).parent / "lightrag_data" / "entity_relations.json"
        if entity_relations_path.exists():
            tests.append(("Entity Relations", True, "Entity relations file available"))
        else:
            tests.append(("Entity Relations", False, "Entity relations file not found"))
    except Exception as e:
        tests.append(("Entity Relations", False, f"Error: {e}"))
    
    # Test 6: Core Python libraries
    try:
        import json
        import asyncio
        import datetime
        from typing import Dict, List, Any, Optional
        tests.append(("Core Python", True, "Standard library imports successful"))
    except ImportError as e:
        tests.append(("Core Python", False, f"Import error: {e}"))
    
    # Print results
    console.print("\n📋 [bold]Import Test Results:[/bold]")
    all_passed = True
    
    for test_name, success, details in tests:
        status = "✅" if success else "❌"
        color = "green" if success else "red"
        console.print(f"{status} [bold {color}]{test_name}[/bold {color}]: {details}")
        if not success:
            all_passed = False
    
    # Summary
    console.print(f"\n📊 [bold]Summary:[/bold]")
    if all_passed:
        console.print("🎉 [bold green]All imports successful! API server is ready to start.[/bold green]")
        console.print("💡 [blue]Run: python rag_api_server.py[/blue]")
        return True
    else:
        console.print("⚠️ [bold yellow]Some imports failed. Install missing dependencies:[/bold yellow]")
        console.print("💡 [blue]Run: pip install -r api_requirements.txt[/blue]")
        return False

def test_qdrant_connection():
    """Test if we can connect to Qdrant"""
    console.print("\n🔗 [bold]Testing Qdrant Connection:[/bold]")
    
    try:
        sys.path.append(str(Path(__file__).parent / "src"))
        from kjv_sources.qdrant_client import QdrantClient
        
        client = QdrantClient()
        stats = client.get_collection_stats()
        
        verse_count = stats.get('points_count', 0)
        console.print(f"✅ [green]Qdrant connection successful![/green]")
        console.print(f"📊 [blue]Verses available: {verse_count}[/blue]")
        
        if verse_count > 0:
            console.print("🎯 [green]Database has data - API will work fully[/green]")
        else:
            console.print("⚠️ [yellow]Database is empty - upload data first[/yellow]")
            console.print("💡 [blue]Run: python kjv_cli.py qdrant upload genesis[/blue]")
        
        return True
        
    except Exception as e:
        console.print(f"❌ [red]Qdrant connection failed: {e}[/red]")
        console.print("💡 [blue]Make sure Qdrant is running and accessible[/blue]")
        return False

if __name__ == "__main__":
    console.print("🚀 [bold cyan]KJV Sources RAG API - Import Test[/bold cyan]")
    
    # Test imports
    imports_ok = test_imports()
    
    # Test Qdrant connection if imports are OK
    if imports_ok:
        qdrant_ok = test_qdrant_connection()
        
        if imports_ok and qdrant_ok:
            console.print("\n🎉 [bold green]Everything looks good! Ready to start the API server.[/bold green]")
            console.print("📡 [blue]Start with: python rag_api_server.py[/blue]")
            console.print("🧪 [blue]Test with: python test_rag_api.py[/blue]")
        else:
            console.print("\n⚠️ [bold yellow]Some issues detected. Fix them before starting the API.[/bold yellow]")
    
    else:
        console.print("\n❌ [bold red]Import issues detected. Install dependencies first.[/bold red]")
        console.print("📦 [blue]Run: pip install -r api_requirements.txt[/blue]")
