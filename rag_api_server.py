#!/usr/bin/env python3
"""
RAG API Server for KJPBS Integration
====================================

FastAPI backend wrapper for the KJV Sources RAG system, designed to provide
RESTful endpoints for the King James Pure Bible Search (KJPBS) Qt application.

This server exposes the doublet analysis, POV analysis, and semantic search
capabilities of the existing Qdrant-based system through HTTP endpoints.

Author: KJV Sources Project
License: MIT
"""

import os
import sys
import json
import asyncio
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pathlib import Path

# FastAPI and HTTP dependencies
from fastapi import FastAPI, HTTPException, Query, Path as FastAPIPath, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, field_validator

# Rich for beautiful console output
from rich.console import Console
from rich.table import Table
from rich import print as rprint

# Import our existing RAG system
sys.path.append(str(Path(__file__).parent / "src"))
try:
    from kjv_sources.qdrant_client import create_qdrant_client, KJVQdrantClient
except ImportError as e:
    print(f"❌ Error importing KJV Sources modules: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

# Initialize console for rich output
console = Console()

# =============================================================================
# Pydantic Models for API Request/Response Schemas
# =============================================================================

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    query: str = Field(..., min_length=1, max_length=1000, description="User's question or query")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context (verse references, search results, etc.)")
    include_sources: bool = Field(default=True, description="Whether to include source citations")
    max_results: int = Field(default=10, ge=1, le=50, description="Maximum number of results to return")

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(..., description="AI-generated response")
    sources: List[Dict[str, Any]] = Field(default=[], description="Source verses and citations")
    doublets_found: List[Dict[str, Any]] = Field(default=[], description="Any doublets identified")
    analysis_type: str = Field(..., description="Type of analysis performed")
    timestamp: datetime = Field(default_factory=datetime.now)

class SearchRequest(BaseModel):
    """Request model for semantic search"""
    query: str = Field(..., min_length=1, max_length=500)
    book: Optional[str] = Field(default=None, description="Filter by specific book")
    source: Optional[str] = Field(default=None, description="Filter by documentary source (J, E, P, D, R)")
    limit: int = Field(default=10, ge=1, le=100)
    
    @field_validator('source')
    @classmethod
    def validate_source(cls, v):
        if v and v not in ['J', 'E', 'P', 'D', 'R']:
            raise ValueError('Source must be one of: J, E, P, D, R')
        return v

class DoubletSearchRequest(BaseModel):
    """Request model for doublet-specific searches"""
    query: Optional[str] = Field(default=None, description="Semantic query for doublets")
    category: Optional[str] = Field(default=None, description="Doublet category filter")
    doublet_name: Optional[str] = Field(default=None, description="Specific doublet name")
    book: Optional[str] = Field(default=None)
    chapter: Optional[int] = Field(default=None, ge=1)
    verse: Optional[int] = Field(default=None, ge=1)
    limit: int = Field(default=20, ge=1, le=100)

class POVSearchRequest(BaseModel):
    """Request model for POV analysis searches"""
    style: Optional[str] = Field(default=None, description="POV style filter")
    perspective: Optional[str] = Field(default=None, description="POV perspective filter")
    purpose: Optional[str] = Field(default=None, description="POV purpose filter")
    theme: Optional[str] = Field(default=None, description="POV theme filter")
    complexity: Optional[str] = Field(default=None, description="POV complexity filter")
    limit: int = Field(default=15, ge=1, le=50)

class VerseReference(BaseModel):
    """Model for verse reference"""
    book: str
    chapter: int = Field(ge=1)
    verse: int = Field(ge=1)

class ApiResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool
    data: Any
    message: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)

# =============================================================================
# FastAPI Application Setup
# =============================================================================

# Create FastAPI app instance
app = FastAPI(
    title="KJV Sources RAG API",
    description="RESTful API for biblical text analysis using Documentary Hypothesis and doublet detection",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for cross-origin requests (needed for Qt frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme (optional - for future authentication)
security = HTTPBearer(auto_error=False)

# Global variables for RAG system
qdrant_client: Optional[KJVQdrantClient] = None
entity_relations: Optional[Dict] = None

# =============================================================================
# Application Startup and Dependencies
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system on startup"""
    global qdrant_client, entity_relations
    
    console.print("🚀 [bold blue]Starting KJV Sources RAG API Server[/bold blue]")
    
    try:
        # Initialize Qdrant client
        console.print("📊 [yellow]Connecting to Qdrant cluster...[/yellow]")
        qdrant_client = create_qdrant_client()
        
        # Load entity relations
        console.print("📚 [yellow]Loading entity relations...[/yellow]")
        entity_relations_path = Path(__file__).parent / "lightrag_data" / "entity_relations.json"
        if entity_relations_path.exists():
            with open(entity_relations_path, 'r', encoding='utf-8') as f:
                entity_relations = json.load(f)
        else:
            entity_relations = {"source_entities": {}, "book_entities": {}, "relation_types": {}}
        
        # Test connection
        stats = qdrant_client.get_collection_stats()
        console.print(f"✅ [green]Connected to Qdrant - {stats.get('points_count', 0)} verses available[/green]")
        
    except Exception as e:
        console.print(f"❌ [red]Failed to initialize RAG system: {e}[/red]")
        raise e

def get_qdrant_client() -> KJVQdrantClient:
    """Dependency to get the Qdrant client"""
    if qdrant_client is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    return qdrant_client

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Optional authentication dependency for future use"""
    # For now, allow all requests
    # In production, implement proper JWT token validation
    return {"user": "anonymous"}

# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "KJV Sources RAG API",
        "version": "2.1.0",
        "description": "Biblical text analysis with Documentary Hypothesis and doublet detection",
        "endpoints": {
            "chat": "/api/chat - AI-powered biblical Q&A",
            "semantic_search": "/api/search - Semantic verse search",
            "doublets": "/api/doublets - Doublet analysis endpoints",
            "pov": "/api/pov - Point of view analysis",
            "health": "/health - Health check"
        },
        "features": [
            "30+ identified biblical doublets",
            "Documentary Hypothesis source analysis (J, E, P, D, R)",
            "Point of view and authorial perspective analysis",
            "Vector-based semantic search",
            "Cross-reference and parallel passage detection"
        ]
    }

@app.get("/health")
async def health_check(client: KJVQdrantClient = Depends(get_qdrant_client)):
    """Health check endpoint"""
    try:
        stats = client.get_collection_stats()
        return {
            "status": "healthy",
            "qdrant_connection": "active",
            "verses_available": stats.get('points_count', 0),
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

# =============================================================================
# Chat and AI Assistant Endpoints
# =============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_bible(
    request: ChatRequest,
    client: KJVQdrantClient = Depends(get_qdrant_client),
    current_user: Dict = Depends(get_current_user)
):
    """
    Main chat endpoint for AI biblical assistant
    
    This endpoint provides intelligent responses to biblical questions by:
    1. Performing semantic search on the query
    2. Identifying relevant doublets
    3. Analyzing documentary sources
    4. Generating contextual responses with citations
    """
    try:
        console.print(f"💬 [blue]Chat query received: {request.query[:50]}...[/blue]")
        
        # Perform semantic search
        search_results = client.search_verses(
            query=request.query,
            limit=request.max_results
        )
        
        # Check for doublets in the results
        doublet_results = []
        if any('doublet' in request.query.lower() or 'parallel' in request.query.lower() for _ in [None]):
            try:
                doublet_results = client.search_hybrid_doublet(
                    query=request.query,
                    limit=5
                )
            except Exception as e:
                console.print(f"⚠️ [yellow]Doublet search failed: {e}[/yellow]")
        
        # Generate AI response (placeholder for now - integrate with your preferred LLM)
        ai_response = generate_biblical_response(
            query=request.query,
            search_results=search_results,
            doublet_results=doublet_results,
            context=request.context
        )
        
        return ChatResponse(
            response=ai_response,
            sources=search_results[:request.max_results] if request.include_sources else [],
            doublets_found=doublet_results,
            analysis_type="semantic_search_with_doublets"
        )
        
    except Exception as e:
        console.print(f"❌ [red]Chat endpoint error: {e}[/red]")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

def generate_biblical_response(
    query: str,
    search_results: List[Dict],
    doublet_results: List[Dict],
    context: Optional[Dict] = None
) -> str:
    """
    Generate AI response based on search results
    
    This is a placeholder function. In production, you would integrate with:
    - OpenAI GPT-4
    - Anthropic Claude
    - Local LLM (Ollama, etc.)
    """
    
    # Extract key information
    num_results = len(search_results)
    has_doublets = len(doublet_results) > 0
    
    # Get sources represented
    sources = set()
    books = set()
    for result in search_results:
        if 'sources' in result:
            sources.update(result['sources'].split(';') if isinstance(result['sources'], str) else [result['sources']])
        if 'book' in result:
            books.add(result['book'])
    
    # Build response
    response_parts = []
    
    # Opening
    if has_doublets:
        response_parts.append(f"I found {len(doublet_results)} doublet passages related to your query about '{query}'.")
    else:
        response_parts.append(f"Based on my analysis of {num_results} biblical passages related to '{query}':")
    
    # Source analysis
    if sources:
        source_names = {
            'J': 'Yahwist',
            'E': 'Elohist', 
            'P': 'Priestly',
            'D': 'Deuteronomist',
            'R': 'Redactor'
        }
        source_list = [f"{s} ({source_names.get(s, s)})" for s in sorted(sources) if s in source_names]
        if source_list:
            response_parts.append(f"The passages span multiple documentary sources: {', '.join(source_list)}.")
    
    # Doublet information
    if has_doublets:
        doublet_categories = set()
        for doublet in doublet_results:
            if 'doublet_categories' in doublet:
                cats = doublet['doublet_categories']
                if isinstance(cats, list):
                    doublet_categories.update(cats)
                elif isinstance(cats, str):
                    doublet_categories.add(cats)
        
        if doublet_categories:
            response_parts.append(f"These doublets fall into categories: {', '.join(sorted(doublet_categories))}.")
    
    # Key passages
    if search_results:
        top_result = search_results[0]
        book = top_result.get('book', 'Unknown')
        chapter = top_result.get('chapter', '?')
        verse = top_result.get('verse', '?')
        text = top_result.get('text', '')[:200] + ('...' if len(top_result.get('text', '')) > 200 else '')
        
        response_parts.append(f"Key passage: {book} {chapter}:{verse} - \"{text}\"")
    
    # Scholarly insight
    if 'creation' in query.lower() and has_doublets:
        response_parts.append("The creation accounts represent different theological perspectives: P's cosmic, ordered creation versus J's anthropocentric garden narrative.")
    elif 'flood' in query.lower() and has_doublets:
        response_parts.append("The flood narrative combines J's anthropomorphic deity with P's cosmic covenant theology.")
    elif sources and len(sources) > 1:
        response_parts.append("The multiple sources reflect different theological emphases and historical contexts in ancient Israel.")
    
    return " ".join(response_parts)

# =============================================================================
# Search Endpoints
# =============================================================================

@app.post("/api/search", response_model=ApiResponse)
async def semantic_search(
    request: SearchRequest,
    client: KJVQdrantClient = Depends(get_qdrant_client)
):
    """Semantic search endpoint for biblical verses"""
    try:
        # Build search filters
        search_kwargs = {'limit': request.limit}
        if request.book:
            search_kwargs['book_filter'] = request.book.title()
        if request.source:
            search_kwargs['source_filter'] = request.source

        results = client.search_verses(request.query, **search_kwargs)
        
        return ApiResponse(
            success=True,
            data={
                "results": results,
                "query": request.query,
                "count": len(results),
                "filters_applied": {k: v for k, v in search_kwargs.items() if k != 'limit'}
            },
            message=f"Found {len(results)} verses matching '{request.query}'"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# =============================================================================
# Doublet Analysis Endpoints
# =============================================================================

@app.post("/api/doublets/search", response_model=ApiResponse)
async def search_doublets(
    request: DoubletSearchRequest,
    client: KJVQdrantClient = Depends(get_qdrant_client)
):
    """Search for doublets with various filters"""
    try:
        results = []
        
        if request.query:
            # Semantic doublet search
            results = client.search_hybrid_doublet(request.query, limit=request.limit)
        elif request.category:
            # Category-based search
            results = client.search_doublets_by_category(request.category, limit=request.limit)
        elif request.doublet_name:
            # Name-based search
            results = client.search_doublets_by_name(request.doublet_name, limit=request.limit)
        else:
            # General doublet search
            results = client.search_doublets(limit=request.limit)
        
        return ApiResponse(
            success=True,
            data={
                "doublets": results,
                "count": len(results),
                "search_type": "semantic" if request.query else "filtered"
            },
            message=f"Found {len(results)} doublet verses"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Doublet search failed: {str(e)}")

@app.get("/api/doublets/parallels/{book}/{chapter}/{verse}", response_model=ApiResponse)
async def get_parallel_passages(
    book: str = FastAPIPath(..., description="Book name"),
    chapter: int = FastAPIPath(..., ge=1, description="Chapter number"),
    verse: int = FastAPIPath(..., ge=1, description="Verse number"),
    client: KJVQdrantClient = Depends(get_qdrant_client)
):
    """Get parallel passages for a specific verse"""
    try:
        results = client.search_doublet_parallels(book.title(), chapter, verse)
        
        return ApiResponse(
            success=True,
            data={
                "reference": f"{book.title()} {chapter}:{verse}",
                "parallels": results,
                "count": len(results)
            },
            message=f"Found {len(results)} parallel passages for {book.title()} {chapter}:{verse}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parallel search failed: {str(e)}")

@app.get("/api/doublets/statistics", response_model=ApiResponse)
async def get_doublet_statistics(client: KJVQdrantClient = Depends(get_qdrant_client)):
    """Get comprehensive doublet statistics"""
    try:
        stats = client.get_doublet_statistics()
        return ApiResponse(
            success=True,
            data=stats,
            message="Doublet statistics retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics retrieval failed: {str(e)}")

@app.get("/api/doublets/categories", response_model=ApiResponse)
async def get_doublet_categories(client: KJVQdrantClient = Depends(get_qdrant_client)):
    """Get list of available doublet categories"""
    try:
        # This could be enhanced to pull from database
        categories = [
            "cosmogony", "genealogy", "catastrophe", "deception", "covenant",
            "family_conflict", "prophetic_calling", "law", "wilderness_miracle",
            "wilderness_provision"
        ]
        
        return ApiResponse(
            success=True,
            data={"categories": categories},
            message=f"Retrieved {len(categories)} doublet categories"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Category retrieval failed: {str(e)}")

# =============================================================================
# POV Analysis Endpoints
# =============================================================================

@app.post("/api/pov/search", response_model=ApiResponse)
async def search_pov(
    request: POVSearchRequest,
    client: KJVQdrantClient = Depends(get_qdrant_client)
):
    """Search verses by point of view characteristics"""
    try:
        results = []
        
        if request.style:
            results = client.search_by_pov_style(request.style, limit=request.limit)
        elif request.perspective:
            results = client.search_by_pov_perspective(request.perspective, limit=request.limit)
        elif request.purpose:
            results = client.search_by_pov_purpose(request.purpose, limit=request.limit)
        elif request.theme:
            results = client.search_by_pov_theme(request.theme, limit=request.limit)
        elif request.complexity:
            results = client.search_pov_complexity(request.complexity, limit=request.limit)
        else:
            raise HTTPException(status_code=400, detail="At least one POV filter must be specified")
        
        return ApiResponse(
            success=True,
            data={
                "results": results,
                "count": len(results),
                "pov_filter": {k: v for k, v in request.dict().items() if v is not None and k != 'limit'}
            },
            message=f"Found {len(results)} verses matching POV criteria"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"POV search failed: {str(e)}")

@app.get("/api/pov/statistics", response_model=ApiResponse)
async def get_pov_statistics(client: KJVQdrantClient = Depends(get_qdrant_client)):
    """Get POV analysis statistics"""
    try:
        stats = client.get_pov_statistics()
        return ApiResponse(
            success=True,
            data=stats,
            message="POV statistics retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"POV statistics failed: {str(e)}")

# =============================================================================
# Utility Endpoints
# =============================================================================

@app.get("/api/books", response_model=ApiResponse)
async def get_available_books(client: KJVQdrantClient = Depends(get_qdrant_client)):
    """Get list of available books in the database"""
    try:
        # This should be enhanced to query actual data
        books = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]
        
        return ApiResponse(
            success=True,
            data={"books": books},
            message=f"Retrieved {len(books)} available books"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Book list retrieval failed: {str(e)}")

@app.get("/api/sources", response_model=ApiResponse)
async def get_documentary_sources():
    """Get information about documentary sources"""
    sources = {
        "J": {
            "name": "Yahwist",
            "description": "Uses YAHWEH name for God, anthropomorphic descriptions, southern perspective",
            "characteristics": ["anthropomorphic deity", "vivid narratives", "Judah-favoring"]
        },
        "E": {
            "name": "Elohist", 
            "description": "Uses Elohim for God until Exodus 3, northern perspective, dream revelations",
            "characteristics": ["northern tribes favored", "God speaks through dreams", "morally sensitive"]
        },
        "P": {
            "name": "Priestly",
            "description": "Ritual and theological focus, temple worship, genealogies",
            "characteristics": ["ritual purity", "temple architecture", "divine transcendence"]
        },
        "D": {
            "name": "Deuteronomist",
            "description": "Deuteronomy and historical books, centralized worship",
            "characteristics": ["worship centralization", "covenant theology", "historical perspective"]
        },
        "R": {
            "name": "Redactor",
            "description": "Editorial additions to harmonize sources",
            "characteristics": ["editorial comments", "source harmonization", "structural organization"]
        }
    }
    
    return ApiResponse(
        success=True,
        data={"sources": sources},
        message="Documentary Hypothesis sources retrieved"
    )

# =============================================================================
# Main Application Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    console.print("🌟 [bold cyan]KJV Sources RAG API Server[/bold cyan]")
    console.print("📖 Biblical analysis with Documentary Hypothesis and doublet detection")
    console.print("🔗 KJPBS Integration Ready")
    
    # Run the server
    uvicorn.run(
        "rag_api_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
