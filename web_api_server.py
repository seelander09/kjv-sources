#!/usr/bin/env python3
"""
Web API Server for KJV Sources with Mathematical Analysis
========================================================

This module provides a FastAPI web server that exposes mathematical pattern analysis
features for the KJV Bible, including search, pattern analysis, and source attribution.

Author: KJV Sources Project
License: MIT
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Import our mathematical analysis components
from word_level_parser import WordLevelParser, WordData
from mathematical_pattern_engine import MathematicalPatternEngine, WordPattern, GlobalAnalysis
from csv_data_loader import CSVDataLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="KJV Sources Mathematical Analysis API",
    description="API for mathematical pattern analysis of the King James Version Bible",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
try:
    app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
except Exception as e:
    logger.warning(f"Could not mount frontend directory: {e}")

# Global instances
word_parser = None
pattern_engine = None
word_data = []

# Pydantic models for API responses
class WordResponse(BaseModel):
    word: str
    position_global: int
    position_in_verse: int
    position_in_chapter: int
    position_in_book: int
    book: str
    chapter: int
    verse: int
    verse_id: str
    canonical_reference: str
    word_length: int
    is_capitalized: bool
    is_number: bool
    is_proper_name: bool
    source_attribution: List[str]
    mathematical_properties: Dict[str, Any]

class PatternResponse(BaseModel):
    word: str
    total_count: int
    first_occurrence: int
    last_occurrence: int
    is_sevened: bool
    is_777: bool
    is_70x7: bool
    is_77: bool
    is_343: bool
    is_490: bool
    is_980: bool
    position_patterns: List[int]
    pattern_analysis: Dict[str, Any]

class SearchResponse(BaseModel):
    query: str
    results: List[WordResponse]
    total_results: int
    patterns_found: List[PatternResponse]
    search_time_ms: float

class GlobalAnalysisResponse(BaseModel):
    total_words: int
    is_7_power: bool
    is_823543: bool
    word_count_analysis: Dict[str, bool]
    book_analysis: Dict[str, Any]
    chapter_analysis: Dict[str, Any]
    verse_analysis: Dict[str, Any]

class VerseResponse(BaseModel):
    verse_id: str
    canonical_reference: str
    text_full: str
    word_count: int
    sources: List[str]
    source_count: int
    primary_source: str
    source_sequence: str
    source_percentages: Dict[str, float]
    redaction_indicators: List[str]
    text_J: str
    text_E: str
    text_P: str
    text_R: str
    mathematical_properties: Dict[str, Any]

@app.on_event("startup")
async def startup_event():
    """Initialize the API on startup"""
    global word_parser, pattern_engine, word_data
    
    logger.info("Starting KJV Sources Mathematical Analysis API...")
    
    # Initialize word parser
    word_parser = WordLevelParser()
    
    # Load sample data or initialize empty
    word_data = []
    
    logger.info("API initialized successfully")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>KJV Sources Mathematical Analysis API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .container { max-width: 800px; margin: 0 auto; background: rgba(255, 255, 255, 0.95); padding: 40px; border-radius: 15px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1); }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { font-weight: bold; color: #0066cc; }
            .url { font-family: monospace; background: #e0e0e0; padding: 2px 5px; }
            .btn { display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 5px; transition: transform 0.2s; }
            .btn:hover { transform: translateY(-2px); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔢 KJV Sources Mathematical Analysis API</h1>
            <p>Welcome to the mathematical pattern analysis API for the King James Version Bible.</p>
            
            <h2>🚀 Quick Start</h2>
            <a href="/frontend/bible_reader.html" class="btn">📖 Open Bible Reader</a>
            <a href="/docs" class="btn">📚 API Documentation</a>
            
            <h2>📚 Available Endpoints</h2>
            
            <div class="endpoint">
                <div class="method">GET</div>
                <div class="url">/frontend/bible_reader.html</div>
                <p>Complete Bible reader interface with mathematical analysis</p>
            </div>
            
            <div class="endpoint">
                <div class="method">GET</div>
                <div class="url">/docs</div>
                <p>Interactive API documentation (Swagger UI)</p>
            </div>
            
            <div class="endpoint">
                <div class="method">GET</div>
                <div class="url">/api/health</div>
                <p>API health check</p>
            </div>
            
            <div class="endpoint">
                <div class="method">GET</div>
                <div class="url">/api/search</div>
                <p>Search for words in the Bible with mathematical pattern analysis</p>
            </div>
            
            <div class="endpoint">
                <div class="method">GET</div>
                <div class="url">/api/patterns/{word}</div>
                <p>Get mathematical patterns for a specific word</p>
            </div>
            
            <div class="endpoint">
                <div class="method">GET</div>
                <div class="url">/api/chapter/{book}/{chapter}</div>
                <p>Get complete chapter data with word-level analysis</p>
            </div>
            
            <div class="endpoint">
                <div class="method">GET</div>
                <div class="url">/api/global-analysis</div>
                <p>Get global mathematical analysis of the Bible</p>
            </div>
            
            <h2>🔗 Quick Links</h2>
            <ul>
                <li><a href="/frontend/bible_reader.html">📖 Bible Reader Interface</a></li>
                <li><a href="/docs">📚 API Documentation</a></li>
                <li><a href="/api/search?q=God">🔍 Search for "God"</a></li>
                <li><a href="/api/patterns/God">🔢 Patterns for "God"</a></li>
                <li><a href="/api/chapter/Genesis/1">📖 Genesis Chapter 1</a></li>
            </ul>
        </div>
    </body>
    </html>
    """

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "components": {
            "word_parser": word_parser is not None,
            "pattern_engine": pattern_engine is not None,
            "word_data_loaded": len(word_data) > 0
        }
    }

@app.get("/api/search", response_model=SearchResponse)
async def search_bible(
    q: str = Query(..., description="Search query"),
    limit: int = Query(50, description="Maximum number of results"),
    include_patterns: bool = Query(True, description="Include mathematical patterns")
):
    """Search for words in the Bible with mathematical pattern analysis"""
    import time
    start_time = time.time()
    
    if not word_data:
        raise HTTPException(status_code=503, detail="No Bible data loaded")
    
    # Simple search implementation
    query_lower = q.lower()
    results = []
    
    for word in word_data:
        if query_lower in word.word.lower():
            results.append(WordResponse(
                word=word.word,
                position_global=word.position_global,
                position_in_verse=word.position_in_verse,
                position_in_chapter=word.position_in_chapter,
                position_in_book=word.position_in_book,
                book=word.book,
                chapter=word.chapter,
                verse=word.verse,
                verse_id=word.verse_id,
                canonical_reference=word.canonical_reference,
                word_length=word.word_length,
                is_capitalized=word.is_capitalized,
                is_number=word.is_number,
                is_proper_name=word.is_proper_name,
                source_attribution=word.source_attribution,
                mathematical_properties=word.mathematical_properties
            ))
            
            if len(results) >= limit:
                break
    
    # Get patterns if requested
    patterns_found = []
    if include_patterns and pattern_engine:
        try:
            all_patterns = pattern_engine.analyze_all_patterns()
            if query_lower in all_patterns:
                pattern = all_patterns[query_lower]
                patterns_found.append(PatternResponse(
                    word=pattern.word,
                    total_count=pattern.total_count,
                    first_occurrence=pattern.first_occurrence,
                    last_occurrence=pattern.last_occurrence,
                    is_sevened=pattern.is_sevened,
                    is_777=pattern.is_777,
                    is_70x7=pattern.is_70x7,
                    is_77=pattern.is_77,
                    is_343=pattern.is_343,
                    is_490=pattern.is_490,
                    is_980=pattern.is_980,
                    position_patterns=pattern.position_patterns,
                    pattern_analysis=pattern.pattern_analysis
                ))
        except Exception as e:
            logger.warning(f"Failed to get patterns: {e}")
    
    search_time = (time.time() - start_time) * 1000
    
    return SearchResponse(
        query=q,
        results=results,
        total_results=len(results),
        patterns_found=patterns_found,
        search_time_ms=search_time
    )

@app.get("/api/patterns/{word}", response_model=PatternResponse)
async def get_word_patterns(word: str):
    """Get mathematical patterns for a specific word"""
    if not pattern_engine:
        raise HTTPException(status_code=503, detail="Pattern engine not available")
    
    try:
        all_patterns = pattern_engine.analyze_all_patterns()
        if word.lower() not in all_patterns:
            raise HTTPException(status_code=404, detail=f"No patterns found for word: {word}")
        
        pattern = all_patterns[word.lower()]
        return PatternResponse(
            word=pattern.word,
            total_count=pattern.total_count,
            first_occurrence=pattern.first_occurrence,
            last_occurrence=pattern.last_occurrence,
            is_sevened=pattern.is_sevened,
            is_777=pattern.is_777,
            is_70x7=pattern.is_70x7,
            is_77=pattern.is_77,
            is_343=pattern.is_343,
            is_490=pattern.is_490,
            is_980=pattern.is_980,
            position_patterns=pattern.position_patterns,
            pattern_analysis=pattern.pattern_analysis
        )
    except Exception as e:
        logger.error(f"Error getting patterns for {word}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving patterns: {str(e)}")

@app.get("/api/chapter/{book}/{chapter}")
async def get_chapter(book: str, chapter: int):
    """Get complete chapter data with word-level analysis"""
    if not word_data:
        raise HTTPException(status_code=503, detail="No Bible data loaded")
    
    try:
        # Filter words for the specified book and chapter
        chapter_words = [
            word for word in word_data 
            if word.book.lower() == book.lower() and word.chapter == chapter
        ]
        
        if not chapter_words:
            raise HTTPException(status_code=404, detail=f"No data found for {book} Chapter {chapter}")
        
        # Group words by verse
        verses = {}
        for word in chapter_words:
            verse_key = word.verse
            if verse_key not in verses:
                verses[verse_key] = []
            verses[verse_key].append(word)
        
        # Sort verses and words within verses
        sorted_verses = {}
        for verse_num in sorted(verses.keys()):
            sorted_verses[verse_num] = sorted(verses[verse_num], key=lambda w: w.position_in_verse)
        
        # Create response data
        chapter_data = {
            "book": book,
            "chapter": chapter,
            "total_verses": len(sorted_verses),
            "total_words": len(chapter_words),
            "verses": []
        }
        
        for verse_num, words in sorted_verses.items():
            if words:
                first_word = words[0]
                verse_text = " ".join(word.word for word in words)
                
                verse_data = {
                    "verse_number": verse_num,
                    "verse_id": first_word.verse_id,
                    "canonical_reference": first_word.canonical_reference,
                    "text": verse_text,
                    "word_count": len(words),
                    "words": [
                        {
                            "word": word.word,
                            "position_global": word.position_global,
                            "position_in_verse": word.position_in_verse,
                            "word_length": word.word_length,
                            "is_capitalized": word.is_capitalized,
                            "is_number": word.is_number,
                            "is_proper_name": word.is_proper_name,
                            "source_attribution": word.source_attribution,
                            "mathematical_properties": word.mathematical_properties
                        }
                        for word in words
                    ]
                }
                chapter_data["verses"].append(verse_data)
        
        return chapter_data
        
    except Exception as e:
        logger.error(f"Error getting chapter {book} {chapter}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving chapter: {str(e)}")

@app.get("/api/verse/{reference}", response_model=VerseResponse)
async def get_verse(reference: str):
    """Get verse data with source attribution"""
    # This would integrate with your existing CSV data
    # For now, return a sample response
    return VerseResponse(
        verse_id="Gen.1.1",
        canonical_reference="Genesis 1:1",
        text_full="In the beginning God created the heaven and the earth.",
        word_count=10,
        sources=["J", "P"],
        source_count=2,
        primary_source="J",
        source_sequence="J-P",
        source_percentages={"J": 0.6, "P": 0.4},
        redaction_indicators=["editorial"],
        text_J="In the beginning God created",
        text_E="",
        text_P="the heaven and the earth.",
        text_R="",
        mathematical_properties={
            "word_count": 10,
            "is_sevened": False,
            "position_in_bible": 1
        }
    )

@app.get("/api/global-analysis", response_model=GlobalAnalysisResponse)
async def get_global_analysis():
    """Get global mathematical analysis of the Bible"""
    if not pattern_engine:
        raise HTTPException(status_code=503, detail="Pattern engine not available")
    
    try:
        analysis = pattern_engine.get_global_analysis()
        return GlobalAnalysisResponse(
            total_words=analysis.total_words,
            is_7_power=analysis.is_7_power,
            is_823543=analysis.is_823543,
            word_count_analysis=analysis.word_count_analysis,
            book_analysis=analysis.book_analysis,
            chapter_analysis=analysis.chapter_analysis,
            verse_analysis=analysis.verse_analysis
        )
    except Exception as e:
        logger.error(f"Error getting global analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving global analysis: {str(e)}")

@app.get("/api/load-data")
async def load_bible_data():
    """Load Bible data from CSV files (admin endpoint)"""
    global word_data, pattern_engine
    
    try:
        # Load data from CSV files
        loader = CSVDataLoader()
        word_data = loader.load_all_books()
        
        if word_data:
            # Initialize pattern engine
            pattern_engine = MathematicalPatternEngine(word_data)
            
            # Get statistics
            stats = loader.get_statistics()
            
            return {
                "status": "success",
                "words_loaded": len(word_data),
                "pattern_engine_initialized": pattern_engine is not None,
                "statistics": {
                    "total_words": stats.get('total_words', 0),
                    "total_verses": stats.get('total_verses', 0),
                    "total_chapters": stats.get('total_chapters', 0),
                    "total_books": stats.get('total_books', 0),
                    "books": stats.get('books', []),
                    "source_distribution": stats.get('source_distribution', {})
                }
            }
        else:
            raise HTTPException(status_code=404, detail="No CSV data found in output directory")
            
    except Exception as e:
        logger.error(f"Error loading Bible data: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "web_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
