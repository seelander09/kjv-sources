#!/usr/bin/env python3
"""
LightRAG Query Interface for KJV Sources Project
Provides structured queries and entity-relation reasoning capabilities
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

# LightRAG imports
try:
    from lightrag import LightRAG
    from lightrag.retrievers import HybridRetriever
    from lightrag.retrievers import DenseRetriever, SparseRetriever
    from lightrag.retrievers import Reranker
    LIGHTRAG_AVAILABLE = True
except ImportError:
    LIGHTRAG_AVAILABLE = False
    print("LightRAG not available. Install with: pip install lightrag")

# Rich terminal interface
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.prompt import Prompt
    from rich.syntax import Syntax
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QueryResult:
    """Represents a query result with metadata"""
    content: str
    metadata: Dict[str, Any]
    score: float
    doc_id: str

class KJVLightRAGQuery:
    """LightRAG query interface for KJV sources data"""
    
    def __init__(self, lightrag_dir: str = "lightrag_data"):
        self.lightrag_dir = Path(lightrag_dir)
        self.console = Console() if RICH_AVAILABLE else None
        
        # Load entity relations
        self.entity_relations = self.load_entity_relations()
        
        # Initialize LightRAG
        if LIGHTRAG_AVAILABLE:
            self.setup_lightrag()
        else:
            logger.warning("LightRAG not available. Running in simulation mode.")
    
    def load_entity_relations(self) -> Dict[str, Any]:
        """Load entity-relation mappings"""
        relations_path = self.lightrag_dir / "entity_relations.json"
        
        if relations_path.exists():
            with open(relations_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Default entity relations
            return {
                "source_entities": {
                    "J": {"name": "Jahwist", "description": "Yahwist source", "color": "blue"},
                    "E": {"name": "Elohist", "description": "Elohist source", "color": "cyan"},
                    "P": {"name": "Priestly", "description": "Priestly source", "color": "yellow"},
                    "R": {"name": "Redactor", "description": "Redactor source", "color": "red"}
                },
                "book_entities": {
                    "Genesis": {"name": "Genesis", "chapters": 50, "type": "narrative"},
                    "Exodus": {"name": "Exodus", "chapters": 40, "type": "narrative"},
                    "Leviticus": {"name": "Leviticus", "chapters": 27, "type": "legal"},
                    "Numbers": {"name": "Numbers", "chapters": 36, "type": "narrative"},
                    "Deuteronomy": {"name": "Deuteronomy", "chapters": 34, "type": "legal"}
                }
            }
    
    def setup_lightrag(self):
        """Initialize LightRAG for querying"""
        try:
            # Configure hybrid retriever
            self.dense_retriever = DenseRetriever(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                device="cpu"
            )
            
            self.sparse_retriever = SparseRetriever(
                model_name="microsoft/DialoGPT-medium"
            )
            
            self.reranker = Reranker(
                model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
            )
            
            self.hybrid_retriever = HybridRetriever(
                dense_retriever=self.dense_retriever,
                sparse_retriever=self.sparse_retriever,
                reranker=self.reranker,
                weights=[0.5, 0.5]
            )
            
            # Load existing LightRAG collection
            self.lightrag = LightRAG(
                retriever=self.hybrid_retriever,
                collection_name="kjv_sources",
                persist_directory=str(self.lightrag_dir)
            )
            
            logger.info("LightRAG query interface initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LightRAG: {e}")
            LIGHTRAG_AVAILABLE = False
    
    def semantic_search(self, query: str, limit: int = 10, 
                       filters: Optional[Dict[str, Any]] = None) -> List[QueryResult]:
        """Perform semantic search with optional filters"""
        if not LIGHTRAG_AVAILABLE:
            return self.simulate_search(query, limit, filters)
        
        try:
            # Perform search with filters
            results = self.lightrag.search(
                query=query,
                k=limit,
                filter=filters
            )
            
            # Convert to QueryResult objects
            query_results = []
            for result in results:
                query_result = QueryResult(
                    content=result.content,
                    metadata=result.metadata,
                    score=result.score,
                    doc_id=result.doc_id
                )
                query_results.append(query_result)
            
            return query_results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def simulate_search(self, query: str, limit: int = 10, 
                       filters: Optional[Dict[str, Any]] = None) -> List[QueryResult]:
        """Simulate search when LightRAG is not available"""
        logger.info(f"Simulating search for: {query}")
        
        # Create mock results
        mock_results = []
        for i in range(min(limit, 5)):
            mock_result = QueryResult(
                content=f"Mock result {i+1} for query: {query}",
                metadata={
                    "type": "verse",
                    "book": "Genesis",
                    "chapter": i + 1,
                    "verse": i + 1,
                    "sources": ["P"],
                    "primary_source": "P"
                },
                score=0.9 - (i * 0.1),
                doc_id=f"mock_{i}"
            )
            mock_results.append(mock_result)
        
        return mock_results
    
    def query_by_source(self, source: str, limit: int = 20) -> List[QueryResult]:
        """Query verses by specific source (J, E, P, R)"""
        filters = {
            "primary_source": source
        }
        
        query = f"verses with {self.entity_relations['source_entities'][source]['name']} source"
        return self.semantic_search(query, limit, filters)
    
    def query_by_book(self, book: str, limit: int = 20) -> List[QueryResult]:
        """Query verses by specific book"""
        filters = {
            "book": book
        }
        
        query = f"verses from {book}"
        return self.semantic_search(query, limit, filters)
    
    def query_multi_source_verses(self, limit: int = 20) -> List[QueryResult]:
        """Query verses with multiple sources"""
        filters = {
            "is_multi_source": True
        }
        
        query = "verses with multiple sources"
        return self.semantic_search(query, limit, filters)
    
    def query_by_chapter(self, book: str, chapter: int, limit: int = 50) -> List[QueryResult]:
        """Query verses by specific chapter"""
        filters = {
            "book": book,
            "chapter": chapter
        }
        
        query = f"verses from {book} chapter {chapter}"
        return self.semantic_search(query, limit, filters)
    
    def query_redaction_indicators(self, limit: int = 20) -> List[QueryResult]:
        """Query verses with redaction indicators"""
        query = "verses with redaction indicators or editorial additions"
        return self.semantic_search(query, limit)
    
    def query_source_sequence(self, sequence: str, limit: int = 20) -> List[QueryResult]:
        """Query verses by source sequence pattern"""
        query = f"verses with source sequence pattern: {sequence}"
        return self.semantic_search(query, limit)
    
    def entity_relation_query(self, entity_type: str, entity_value: str, 
                            relation: str, limit: int = 20) -> List[QueryResult]:
        """Perform entity-relation queries"""
        
        if entity_type == "source":
            if entity_value in self.entity_relations["source_entities"]:
                return self.query_by_source(entity_value, limit)
        
        elif entity_type == "book":
            if entity_value in self.entity_relations["book_entities"]:
                return self.query_by_book(entity_value, limit)
        
        # Fallback to semantic search
        query = f"{relation} {entity_type}: {entity_value}"
        return self.semantic_search(query, limit)
    
    def display_results(self, results: List[QueryResult], title: str = "Search Results"):
        """Display query results in a rich format"""
        if not RICH_AVAILABLE:
            self.display_results_simple(results, title)
            return
        
        if not results:
            self.console.print(f"[yellow]No results found for: {title}[/yellow]")
            return
        
        # Create results table
        table = Table(title=title)
        table.add_column("Score", style="bold", justify="right")
        table.add_column("Reference", style="bold")
        table.add_column("Text", style="italic", width=60)
        table.add_column("Sources", style="bold")
        table.add_column("Type", style="dim")
        
        for result in results:
            # Extract reference from metadata
            ref = result.metadata.get('reference', result.doc_id)
            
            # Color-code sources
            sources = result.metadata.get('sources', [])
            sources_text = Text()
            for source in sources:
                color = self.entity_relations["source_entities"].get(source, {}).get("color", "white")
                sources_text.append(f"{source} ", style=color)
            
            # Truncate text for display
            text = result.content[:80] + "..." if len(result.content) > 80 else result.content
            
            table.add_row(
                f"{result.score:.3f}",
                ref,
                text,
                sources_text,
                result.metadata.get('type', 'unknown')
            )
        
        self.console.print(table)
    
    def display_results_simple(self, results: List[QueryResult], title: str = "Search Results"):
        """Display results in simple text format"""
        print(f"\n{title}")
        print("-" * 50)
        
        if not results:
            print("No results found.")
            return
        
        for i, result in enumerate(results, 1):
            ref = result.metadata.get('reference', result.doc_id)
            sources = result.metadata.get('sources', [])
            sources_str = ";".join(sources)
            
            print(f"{i}. [{result.score:.3f}] {ref} ({sources_str})")
            print(f"   {result.content[:100]}...")
            print()
    
    def interactive_query(self):
        """Interactive query interface"""
        if RICH_AVAILABLE:
            self.interactive_query_rich()
        else:
            self.interactive_query_simple()
    
    def interactive_query_rich(self):
        """Rich interactive query interface"""
        self.console.print("[bold blue]🔍 KJV Sources LightRAG Query Interface[/bold blue]")
        self.console.print("[dim]Type 'help' for available commands, 'quit' to exit[/dim]\n")
        
        while True:
            try:
                command = Prompt.ask("[bold green]Query[/bold green]")
                
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                elif command.lower() == 'help':
                    self.show_help()
                elif command.lower().startswith('source:'):
                    source = command.split(':', 1)[1].strip().upper()
                    if source in ['J', 'E', 'P', 'R']:
                        results = self.query_by_source(source)
                        self.display_results(results, f"Verses with {source} Source")
                    else:
                        self.console.print(f"[red]Invalid source: {source}. Use J, E, P, or R[/red]")
                elif command.lower().startswith('book:'):
                    book = command.split(':', 1)[1].strip()
                    results = self.query_by_book(book)
                    self.display_results(results, f"Verses from {book}")
                elif command.lower().startswith('chapter:'):
                    parts = command.split(':', 1)[1].strip().split()
                    if len(parts) >= 2:
                        book, chapter = parts[0], int(parts[1])
                        results = self.query_by_chapter(book, chapter)
                        self.display_results(results, f"Verses from {book} Chapter {chapter}")
                    else:
                        self.console.print("[red]Format: chapter: <book> <chapter_number>[/red]")
                elif command.lower() == 'multi':
                    results = self.query_multi_source_verses()
                    self.display_results(results, "Multi-Source Verses")
                elif command.lower() == 'redaction':
                    results = self.query_redaction_indicators()
                    self.display_results(results, "Verses with Redaction Indicators")
                else:
                    # General semantic search
                    results = self.semantic_search(command)
                    self.display_results(results, f"Search: {command}")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
        
        self.console.print("[green]Goodbye![/green]")
    
    def interactive_query_simple(self):
        """Simple interactive query interface"""
        print("🔍 KJV Sources LightRAG Query Interface")
        print("Type 'help' for available commands, 'quit' to exit\n")
        
        while True:
            try:
                command = input("Query: ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                elif command.lower() == 'help':
                    self.show_help()
                elif command.lower().startswith('source:'):
                    source = command.split(':', 1)[1].strip().upper()
                    if source in ['J', 'E', 'P', 'R']:
                        results = self.query_by_source(source)
                        self.display_results(results, f"Verses with {source} Source")
                    else:
                        print(f"Invalid source: {source}. Use J, E, P, or R")
                elif command.lower().startswith('book:'):
                    book = command.split(':', 1)[1].strip()
                    results = self.query_by_book(book)
                    self.display_results(results, f"Verses from {book}")
                elif command.lower().startswith('chapter:'):
                    parts = command.split(':', 1)[1].strip().split()
                    if len(parts) >= 2:
                        book, chapter = parts[0], int(parts[1])
                        results = self.query_by_chapter(book, chapter)
                        self.display_results(results, f"Verses from {book} Chapter {chapter}")
                    else:
                        print("Format: chapter: <book> <chapter_number>")
                elif command.lower() == 'multi':
                    results = self.query_multi_source_verses()
                    self.display_results(results, "Multi-Source Verses")
                elif command.lower() == 'redaction':
                    results = self.query_redaction_indicators()
                    self.display_results(results, "Verses with Redaction Indicators")
                else:
                    # General semantic search
                    results = self.semantic_search(command)
                    self.display_results(results, f"Search: {command}")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("Goodbye!")
    
    def show_help(self):
        """Show help information"""
        help_text = """
Available Commands:
- source:J/E/P/R - Query verses by source
- book:<book_name> - Query verses by book
- chapter:<book> <number> - Query verses by chapter
- multi - Query multi-source verses
- redaction - Query verses with redaction indicators
- <any text> - General semantic search
- help - Show this help
- quit - Exit
        """
        
        if RICH_AVAILABLE:
            self.console.print(Panel(help_text, title="Help", border_style="blue"))
        else:
            print(help_text)

def main():
    """Main function to run the LightRAG query interface"""
    print("🚀 KJV Sources LightRAG Query Interface")
    print("=" * 50)
    
    # Initialize query interface
    query_interface = KJVLightRAGQuery()
    
    # Start interactive mode
    query_interface.interactive_query()

if __name__ == "__main__":
    main() 