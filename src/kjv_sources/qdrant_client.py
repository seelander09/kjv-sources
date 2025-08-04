#!/usr/bin/env python3
"""
Qdrant Client for KJV Sources Data
Handles vector database operations for storing and querying biblical source data
"""

import os
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np
import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, 
    Filter, FieldCondition, MatchValue,
    CreateCollection, UpdateCollection
)
from sentence_transformers import SentenceTransformer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

console = Console()

class KJVQdrantClient:
    """Client for managing KJV sources data in Qdrant vector database."""
    
    def __init__(self, api_key: str, cluster_id: str, endpoint: str):
        """Initialize Qdrant client with cluster details."""
        self.api_key = api_key
        self.cluster_id = cluster_id
        self.endpoint = endpoint
        self.collection_name = "kjv_sources"
        
        # Initialize Qdrant client
        self.client = QdrantClient(
            url=endpoint,
            api_key=api_key
        )
        
        # Initialize sentence transformer for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        
        console.print(f"[green]✅ Connected to Qdrant cluster: {cluster_id}[/green]")
    
    def create_collection(self, force_recreate: bool = False) -> bool:
        """Create the KJV sources collection in Qdrant."""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_exists = any(c.name == self.collection_name for c in collections.collections)
            
            if collection_exists and force_recreate:
                console.print(f"[yellow]🗑️ Deleting existing collection: {self.collection_name}[/yellow]")
                self.client.delete_collection(self.collection_name)
                collection_exists = False
            
            if not collection_exists:
                console.print(f"[blue]📚 Creating collection: {self.collection_name}[/blue]")
                
                # Create collection with vector parameters
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                
                console.print(f"[green]✅ Collection '{self.collection_name}' created successfully[/green]")
                return True
            else:
                console.print(f"[blue]📚 Collection '{self.collection_name}' already exists[/blue]")
                return True
                
        except Exception as e:
            console.print(f"[red]❌ Error creating collection: {e}[/red]")
            return False
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for given text."""
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            console.print(f"[red]❌ Error generating embedding: {e}[/red]")
            return []
    
    def prepare_verse_data(self, row: pd.Series) -> Dict[str, Any]:
        """Prepare verse data for Qdrant storage."""
        # Create a rich text representation for embedding
        text_for_embedding = f"{row['canonical_reference']}: {row['full_text']}"
        
        # Generate embedding
        embedding = self.get_embedding(text_for_embedding)
        
        if not embedding:
            return None
        
        # Prepare metadata
        metadata = {
            "book": row.get('book', ''),
            "chapter": int(row.get('chapter', 0)),
            "verse": int(row.get('verse', 0)),
            "canonical_reference": row.get('canonical_reference', ''),
            "full_text": row.get('full_text', ''),
            "sources": row.get('sources', ''),
            "source_count": int(row.get('source_count', 0)),
            "primary_source": row.get('primary_source', ''),
            "word_count": int(row.get('word_count', 0)),
            "source_sequence": row.get('source_sequence', ''),
            "source_percentages": row.get('source_percentages', ''),
            "redaction_indicators": row.get('redaction_indicators', ''),
            "text_J": row.get('text_J', ''),
            "text_E": row.get('text_E', ''),
            "text_P": row.get('text_P', ''),
            "text_R": row.get('text_R', ''),
            "source_confidence": row.get('source_confidence', ''),
            "is_multi_source": row.get('source_count', 0) > 1,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "id": str(uuid.uuid4()),
            "vector": embedding,
            "metadata": metadata
        }
    
    def upload_book_data(self, book_name: str, csv_path: str) -> bool:
        """Upload a book's data to Qdrant."""
        try:
            console.print(f"[blue]📖 Loading data for {book_name}...[/blue]")
            df = pd.read_csv(csv_path)
            
            if df.empty:
                console.print(f"[yellow]⚠️ No data found for {book_name}[/yellow]")
                return False
            
            # Prepare points for upload
            points = []
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"Processing {book_name} verses...", total=len(df))
                
                for _, row in df.iterrows():
                    verse_data = self.prepare_verse_data(row)
                    if verse_data:
                        points.append(PointStruct(
                            id=verse_data["id"],
                            vector=verse_data["vector"],
                            payload=verse_data["metadata"]
                        ))
                    progress.update(task, advance=1)
            
            if not points:
                console.print(f"[red]❌ No valid points prepared for {book_name}[/red]")
                return False
            
            # Upload to Qdrant
            console.print(f"[blue]📤 Uploading {len(points)} verses to Qdrant...[/blue]")
            
            # Upload in batches to avoid memory issues
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                console.print(f"[green]✅ Uploaded batch {i//batch_size + 1}/{(len(points) + batch_size - 1)//batch_size}[/green]")
            
            console.print(f"[green]✅ Successfully uploaded {len(points)} verses for {book_name}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Error uploading {book_name}: {e}[/red]")
            return False
    
    def search_verses(self, query: str, limit: int = 10, book_filter: Optional[str] = None) -> List[Dict]:
        """Search verses using semantic similarity."""
        try:
            # Generate embedding for query
            query_embedding = self.get_embedding(query)
            if not query_embedding:
                return []
            
            # Prepare filter
            search_filter = None
            if book_filter:
                search_filter = Filter(
                    must=[
                        FieldCondition(
                            key="book",
                            match=MatchValue(value=book_filter)
                        )
                    ]
                )
            
            # Search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter=search_filter,
                with_payload=True
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "score": result.score,
                    "reference": result.payload.get("canonical_reference", ""),
                    "text": result.payload.get("full_text", ""),
                    "sources": result.payload.get("sources", ""),
                    "primary_source": result.payload.get("primary_source", ""),
                    "book": result.payload.get("book", ""),
                    "chapter": result.payload.get("chapter", 0),
                    "verse": result.payload.get("verse", 0)
                })
            
            return results
            
        except Exception as e:
            console.print(f"[red]❌ Error searching verses: {e}[/red]")
            return []
    
    def search_by_source(self, source: str, limit: int = 20) -> List[Dict]:
        """Search verses by specific source (J, E, P, R)."""
        try:
            # Search for verses containing the specified source
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=[0.0] * self.embedding_dim,  # Dummy vector for filtering only
                limit=limit,
                query_filter=Filter(
                    must=[
                        FieldCondition(
                            key="sources",
                            match=MatchValue(value=source)
                        )
                    ]
                ),
                with_payload=True
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "reference": result.payload.get("canonical_reference", ""),
                    "text": result.payload.get("full_text", ""),
                    "sources": result.payload.get("sources", ""),
                    "primary_source": result.payload.get("primary_source", ""),
                    "book": result.payload.get("book", ""),
                    "chapter": result.payload.get("chapter", 0),
                    "verse": result.payload.get("verse", 0)
                })
            
            return results
            
        except Exception as e:
            console.print(f"[red]❌ Error searching by source: {e}[/red]")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            collection_count = self.client.count(self.collection_name)
            
            return {
                "collection_name": self.collection_name,
                "total_points": collection_count.count,
                "vector_size": collection_info.config.params.vectors.size,
                "distance": collection_info.config.params.vectors.distance,
                "status": collection_info.status
            }
            
        except Exception as e:
            console.print(f"[red]❌ Error getting collection stats: {e}[/red]")
            return {}
    
    def delete_collection(self) -> bool:
        """Delete the collection."""
        try:
            self.client.delete_collection(self.collection_name)
            console.print(f"[green]✅ Collection '{self.collection_name}' deleted[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Error deleting collection: {e}[/red]")
            return False

def create_qdrant_client() -> KJVQdrantClient:
    """Create and return a configured Qdrant client."""
    # Qdrant cluster configuration
    API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.4r0SK3yIac0KN8iw8RcO2pfTYqXLsv_m01WV5SFaio4"
    CLUSTER_ID = "6ee24530-ebe8-4553-b5db-f554e567969c"
    ENDPOINT = "https://6ee24530-ebe8-4553-b5db-f554e567969c.us-east4-0.gcp.cloud.qdrant.io"
    
    return KJVQdrantClient(API_KEY, CLUSTER_ID, ENDPOINT) 