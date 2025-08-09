#!/usr/bin/env python3
"""
Simple RAG API Server for Testing
=================================

A simplified version of the RAG API server that works reliably
for testing with real Qdrant data.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# FastAPI imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Rich for console output
from rich.console import Console
from rich.panel import Panel

# Add src to path and import our client
sys.path.append(str(Path(__file__).parent / "src"))
from kjv_sources.qdrant_client import create_qdrant_client

console = Console()

# Pydantic models
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=10, ge=1, le=100)

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    max_results: int = Field(default=10, ge=1, le=50)

class ApiResponse(BaseModel):
    success: bool
    data: Any
    message: str = ""

# Create FastAPI app
app = FastAPI(
    title="KJV Sources RAG API (Simple)",
    description="Simple API for testing with real Qdrant data",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global client
client = None

@app.on_event("startup")
async def startup_event():
    """Initialize the Qdrant client"""
    global client
    console.print("🚀 [bold blue]Starting Simple RAG API Server[/bold blue]")
    
    try:
        client = create_qdrant_client()
        stats = client.get_collection_stats()
        console.print(f"✅ [green]Connected to Qdrant - {stats['total_points']} verses available[/green]")
    except Exception as e:
        console.print(f"❌ [red]Failed to initialize: {e}[/red]")
        raise e

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "KJV Sources RAG API (Simple)",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/health - Health check",
            "/api/search - Semantic search",
            "/api/chat - AI chat",
            "/api/doublets - Doublet analysis",
            "/api/pov - POV analysis"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if not client:
        raise HTTPException(status_code=503, detail="Client not initialized")
    
    try:
        stats = client.get_collection_stats()
        return {
            "status": "healthy",
            "verses_available": stats['total_points'],
            "collection_name": stats['collection_name']
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@app.post("/api/search", response_model=ApiResponse)
async def search_verses(request: SearchRequest):
    """Semantic search for verses"""
    if not client:
        raise HTTPException(status_code=503, detail="Client not initialized")
    
    try:
        results = client.search_verses(request.query, limit=request.limit)
        return ApiResponse(
            success=True,
            data={
                "results": results,
                "query": request.query,
                "count": len(results)
            },
            message=f"Found {len(results)} verses matching '{request.query}'"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/chat", response_model=ApiResponse)
async def chat_with_bible(request: ChatRequest):
    """AI chat endpoint"""
    if not client:
        raise HTTPException(status_code=503, detail="Client not initialized")
    
    try:
        # Get search results
        search_results = client.search_verses(request.query, limit=request.max_results)
        
        # Get doublet results if relevant
        doublet_results = []
        if any(word in request.query.lower() for word in ['doublet', 'parallel', 'flood', 'creation']):
            try:
                doublet_results = client.search_hybrid_doublet(request.query, limit=3)
            except:
                pass
        
        # Generate simple response
        response_parts = []
        response_parts.append(f"Based on your query about '{request.query}', I found {len(search_results)} relevant verses.")
        
        if search_results:
            first_result = search_results[0]
            book = first_result.get('book', 'Unknown')
            chapter = first_result.get('chapter', '?')
            verse = first_result.get('verse', '?')
            sources = first_result.get('sources', 'Unknown')
            
            response_parts.append(f"Key passage: {book} {chapter}:{verse} (Sources: {sources})")
        
        if doublet_results:
            response_parts.append(f"I also found {len(doublet_results)} doublet passages related to your query.")
        
        return ApiResponse(
            success=True,
            data={
                "response": " ".join(response_parts),
                "sources": search_results[:3],
                "doublets_found": doublet_results
            },
            message="Chat response generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/api/doublets/statistics", response_model=ApiResponse)
async def get_doublet_statistics():
    """Get doublet statistics"""
    if not client:
        raise HTTPException(status_code=503, detail="Client not initialized")
    
    try:
        stats = client.get_doublet_statistics()
        return ApiResponse(
            success=True,
            data=stats,
            message="Doublet statistics retrieved"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics failed: {str(e)}")

@app.post("/api/doublets/search", response_model=ApiResponse)
async def search_doublets(request: SearchRequest):
    """Search for doublets"""
    if not client:
        raise HTTPException(status_code=503, detail="Client not initialized")
    
    try:
        results = client.search_hybrid_doublet(request.query, limit=request.limit)
        return ApiResponse(
            success=True,
            data={
                "doublets": results,
                "count": len(results)
            },
            message=f"Found {len(results)} doublet verses"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Doublet search failed: {str(e)}")

@app.get("/api/pov/statistics", response_model=ApiResponse)
async def get_pov_statistics():
    """Get POV statistics"""
    if not client:
        raise HTTPException(status_code=503, detail="Client not initialized")
    
    try:
        stats = client.get_pov_statistics()
        return ApiResponse(
            success=True,
            data=stats,
            message="POV statistics retrieved"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"POV statistics failed: {str(e)}")

@app.post("/api/pov/search", response_model=ApiResponse)
async def search_pov(request: SearchRequest):
    """Search by POV theme"""
    if not client:
        raise HTTPException(status_code=503, detail="Client not initialized")
    
    try:
        results = client.search_by_pov_theme(request.query, limit=request.limit)
        return ApiResponse(
            success=True,
            data={
                "results": results,
                "count": len(results)
            },
            message=f"Found {len(results)} verses with POV theme '{request.query}'"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"POV search failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    console.print("🌟 [bold cyan]Simple KJV Sources RAG API Server[/bold cyan]")
    console.print("📖 Testing with real Qdrant data")
    console.print("🔗 Ready for KJPBS integration")
    
    uvicorn.run(
        "simple_api_server:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )
