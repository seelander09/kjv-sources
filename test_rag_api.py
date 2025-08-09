#!/usr/bin/env python3
"""
Test Script for RAG API Server
==============================

Comprehensive testing suite for the FastAPI backend that will integrate
with the KJPBS Qt application.

Usage:
    python test_rag_api.py

Make sure the API server is running:
    python rag_api_server.py
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

console = Console()

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"
TEST_TIMEOUT = 30

class APITester:
    """Test suite for the RAG API"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
        self.test_results = []
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_test(self, test_name: str, success: bool, response_time: float, details: str = ""):
        """Log test results"""
        self.test_results.append({
            "test": test_name,
            "success": success,
            "response_time": response_time,
            "details": details
        })
        
        status = "✅" if success else "❌"
        time_str = f"{response_time:.2f}s"
        console.print(f"{status} {test_name} ({time_str}) - {details}")
    
    async def test_endpoint(self, method: str, endpoint: str, data: Dict = None, expected_status: int = 200):
        """Generic endpoint tester"""
        start_time = time.time()
        test_name = f"{method.upper()} {endpoint}"
        
        try:
            if method.upper() == "GET":
                response = await self.client.get(f"{self.base_url}{endpoint}")
            elif method.upper() == "POST":
                response = await self.client.post(f"{self.base_url}{endpoint}", json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = time.time() - start_time
            success = response.status_code == expected_status
            
            details = f"Status: {response.status_code}"
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    if isinstance(json_data, dict):
                        if 'data' in json_data:
                            data_info = json_data['data']
                            if isinstance(data_info, dict) and 'count' in data_info:
                                details += f", Results: {data_info['count']}"
                            elif isinstance(data_info, list):
                                details += f", Results: {len(data_info)}"
                except:
                    pass
            
            self.log_test(test_name, success, response_time, details)
            return response
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test(test_name, False, response_time, f"Error: {str(e)}")
            return None

    async def run_all_tests(self):
        """Run comprehensive test suite"""
        console.print(Panel.fit("🧪 RAG API Test Suite", style="bold blue"))
        
        # Test 1: Health and basic endpoints
        console.print("\n📋 [bold]Basic Endpoints[/bold]")
        await self.test_endpoint("GET", "/")
        await self.test_endpoint("GET", "/health")
        await self.test_endpoint("GET", "/docs", expected_status=200)
        
        # Test 2: Utility endpoints
        console.print("\n🔧 [bold]Utility Endpoints[/bold]")
        await self.test_endpoint("GET", "/api/books")
        await self.test_endpoint("GET", "/api/sources")
        
        # Test 3: Search endpoints
        console.print("\n🔍 [bold]Search Endpoints[/bold]")
        search_data = {
            "query": "creation of man",
            "limit": 5
        }
        await self.test_endpoint("POST", "/api/search", search_data)
        
        # Test with filters
        filtered_search = {
            "query": "God created",
            "book": "Genesis",
            "source": "P",
            "limit": 3
        }
        await self.test_endpoint("POST", "/api/search", filtered_search)
        
        # Test 4: Chat endpoint
        console.print("\n💬 [bold]Chat AI Assistant[/bold]")
        chat_data = {
            "query": "Tell me about the creation stories in Genesis",
            "max_results": 5,
            "include_sources": True
        }
        await self.test_endpoint("POST", "/api/chat", chat_data)
        
        # Test chat with context
        chat_with_context = {
            "query": "What are the differences between these accounts?",
            "context": {"previous_topic": "creation", "focus": "doublets"},
            "max_results": 3
        }
        await self.test_endpoint("POST", "/api/chat", chat_with_context)
        
        # Test 5: Doublet analysis
        console.print("\n📚 [bold]Doublet Analysis[/bold]")
        await self.test_endpoint("GET", "/api/doublets/statistics")
        await self.test_endpoint("GET", "/api/doublets/categories")
        
        # Search doublets by query
        doublet_search = {
            "query": "flood narrative",
            "limit": 5
        }
        await self.test_endpoint("POST", "/api/doublets/search", doublet_search)
        
        # Search doublets by category
        category_search = {
            "category": "cosmogony",
            "limit": 5
        }
        await self.test_endpoint("POST", "/api/doublets/search", category_search)
        
        # Search doublets by name
        name_search = {
            "doublet_name": "Creation Stories",
            "limit": 5
        }
        await self.test_endpoint("POST", "/api/doublets/search", name_search)
        
        # Test parallel passages
        await self.test_endpoint("GET", "/api/doublets/parallels/Genesis/1/1")
        
        # Test 6: POV analysis
        console.print("\n🎭 [bold]POV Analysis[/bold]")
        await self.test_endpoint("GET", "/api/pov/statistics")
        
        # POV search by style
        pov_style = {
            "style": "narrative_anthropomorphic",
            "limit": 5
        }
        await self.test_endpoint("POST", "/api/pov/search", pov_style)
        
        # POV search by theme
        pov_theme = {
            "theme": "creation",
            "limit": 3
        }
        await self.test_endpoint("POST", "/api/pov/search", pov_theme)
        
        # Test 7: Error handling
        console.print("\n⚠️ [bold]Error Handling[/bold]")
        
        # Invalid book
        invalid_search = {
            "query": "test",
            "book": "InvalidBook",
            "limit": 5
        }
        await self.test_endpoint("POST", "/api/search", invalid_search)
        
        # Invalid parallel reference
        await self.test_endpoint("GET", "/api/doublets/parallels/InvalidBook/999/999", expected_status=500)
        
        # Invalid POV search (no filters)
        await self.test_endpoint("POST", "/api/pov/search", {"limit": 5}, expected_status=400)

    def print_summary(self):
        """Print test results summary"""
        console.print("\n" + "="*60)
        console.print(Panel.fit("📊 Test Results Summary", style="bold cyan"))
        
        # Create summary table
        table = Table(title="Test Results")
        table.add_column("Test", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Time", style="yellow")
        table.add_column("Details", style="white")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            time_str = f"{result['response_time']:.2f}s"
            table.add_row(
                result["test"],
                status,
                time_str,
                result["details"]
            )
        
        console.print(table)
        
        # Overall statistics
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        avg_response_time = sum(r["response_time"] for r in self.test_results) / total_tests if total_tests > 0 else 0
        
        stats_table = Table(title="Statistics")
        stats_table.add_column("Metric", style="bold blue")
        stats_table.add_column("Value", style="bold green")
        
        stats_table.add_row("Total Tests", str(total_tests))
        stats_table.add_row("Passed", str(passed_tests))
        stats_table.add_row("Failed", str(total_tests - passed_tests))
        stats_table.add_row("Success Rate", f"{success_rate:.1f}%")
        stats_table.add_row("Avg Response Time", f"{avg_response_time:.2f}s")
        
        console.print(stats_table)
        
        # Status message
        if success_rate >= 90:
            console.print("🎉 [bold green]API is working excellently![/bold green]")
        elif success_rate >= 70:
            console.print("✅ [bold yellow]API is mostly functional with some issues[/bold yellow]")
        else:
            console.print("⚠️ [bold red]API has significant issues that need attention[/bold red]")

async def main():
    """Main test execution"""
    console.print("🚀 [bold blue]Starting RAG API Test Suite[/bold blue]")
    console.print(f"📡 Testing API at: {API_BASE_URL}")
    console.print("⏱️ Make sure the API server is running: python rag_api_server.py\n")
    
    try:
        async with APITester() as tester:
            await tester.run_all_tests()
            tester.print_summary()
            
    except Exception as e:
        console.print(f"❌ [bold red]Test suite failed: {e}[/bold red]")
        console.print("💡 Make sure the API server is running and accessible")

if __name__ == "__main__":
    # Check if we can reach the server first
    console.print("🔍 Checking if API server is running...")
    try:
        import requests
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            console.print("✅ API server is responding")
        else:
            console.print(f"⚠️ API server returned status {response.status_code}")
    except Exception:
        console.print("❌ Cannot reach API server")
        console.print("💡 Start the server with: python rag_api_server.py")
        console.print("📡 Server should be running at http://127.0.0.1:8000")
        exit(1)
    
    # Run async tests
    asyncio.run(main())
