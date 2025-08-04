#!/usr/bin/env python3
"""
LightRAG Ingestion Script for KJV Sources Project
Handles Markdown and JSONL files for entity-relation reasoning and structured queries
Supports hybrid mode for optimal retrieval performance
"""

import os
import json
import re
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

# LightRAG imports (will be installed separately)
try:
    from lightrag import LightRAG
    from lightrag.retrievers import HybridRetriever
    from lightrag.retrievers import DenseRetriever, SparseRetriever
    from lightrag.retrievers import Reranker
    from lightrag.ingest import IngestPipeline
    from lightrag.ingest import Document, Chunk
    LIGHTRAG_AVAILABLE = True
except ImportError:
    LIGHTRAG_AVAILABLE = False
    print("LightRAG not available. Install with: pip install lightrag")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VerseEntity:
    """Represents a biblical verse with source analysis"""
    reference: str
    text: str
    book: str
    chapter: int
    verse: int
    sources: List[str]
    primary_source: str
    source_count: int
    word_count: int
    source_sequence: str
    source_percentages: str
    redaction_indicators: str
    text_J: str
    text_E: str
    text_P: str
    text_R: str

@dataclass
class SourceAnalysis:
    """Represents source analysis data"""
    instruction: str
    input_text: str
    output: str
    metadata: Dict[str, Any]

class KJVLightRAGIngestion:
    """LightRAG ingestion pipeline for KJV sources data"""
    
    def __init__(self, output_dir: str = "output", lightrag_dir: str = "lightrag_data"):
        self.output_dir = Path(output_dir)
        self.lightrag_dir = Path(lightrag_dir)
        self.lightrag_dir.mkdir(exist_ok=True)
        
        # Initialize LightRAG components
        if LIGHTRAG_AVAILABLE:
            self.setup_lightrag()
        else:
            logger.warning("LightRAG not available. Running in simulation mode.")
    
    def setup_lightrag(self):
        """Initialize LightRAG with hybrid retriever configuration"""
        try:
            # Configure hybrid retriever for optimal performance
            self.dense_retriever = DenseRetriever(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                device="cpu"  # Change to "cuda" if GPU available
            )
            
            self.sparse_retriever = SparseRetriever(
                model_name="microsoft/DialoGPT-medium"
            )
            
            self.reranker = Reranker(
                model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
            )
            
            # Create hybrid retriever
            self.hybrid_retriever = HybridRetriever(
                dense_retriever=self.dense_retriever,
                sparse_retriever=self.sparse_retriever,
                reranker=self.reranker,
                weights=[0.5, 0.5]  # Equal weights for dense and sparse
            )
            
            # Initialize LightRAG
            self.lightrag = LightRAG(
                retriever=self.hybrid_retriever,
                collection_name="kjv_sources",
                persist_directory=str(self.lightrag_dir)
            )
            
            logger.info("LightRAG initialized successfully with hybrid retriever")
            
        except Exception as e:
            logger.error(f"Failed to initialize LightRAG: {e}")
            LIGHTRAG_AVAILABLE = False
    
    def parse_verse_reference(self, reference: str) -> Tuple[str, int, int]:
        """Parse verse reference into book, chapter, verse"""
        # Handle various reference formats
        patterns = [
            r"(\w+)\s+(\d+):(\d+)",  # Genesis 1:1
            r"(\w+)\s+(\d+)\s+(\d+)",  # Genesis 1 1
        ]
        
        for pattern in patterns:
            match = re.match(pattern, reference)
            if match:
                book, chapter, verse = match.groups()
                return book, int(chapter), int(verse)
        
        return reference, 0, 0
    
    def load_csv_data(self, book_name: str) -> List[VerseEntity]:
        """Load verse data from CSV files"""
        csv_path = self.output_dir / book_name / f"{book_name}.csv"
        
        if not csv_path.exists():
            logger.warning(f"CSV file not found: {csv_path}")
            return []
        
        verses = []
        try:
            import pandas as pd
            df = pd.read_csv(csv_path)
            
            for _, row in df.iterrows():
                book, chapter, verse = self.parse_verse_reference(row['canonical_reference'])
                
                verse_entity = VerseEntity(
                    reference=row['canonical_reference'],
                    text=row['full_text'],
                    book=book,
                    chapter=chapter,
                    verse=verse,
                    sources=row['sources'].split(';') if pd.notna(row['sources']) else [],
                    primary_source=row['primary_source'],
                    source_count=row['source_count'],
                    word_count=row['word_count'],
                    source_sequence=row.get('source_sequence', ''),
                    source_percentages=row.get('source_percentages', ''),
                    redaction_indicators=row.get('redaction_indicators', ''),
                    text_J=row.get('text_J', ''),
                    text_E=row.get('text_E', ''),
                    text_P=row.get('text_P', ''),
                    text_R=row.get('text_R', '')
                )
                verses.append(verse_entity)
            
            logger.info(f"Loaded {len(verses)} verses from {book_name}")
            return verses
            
        except Exception as e:
            logger.error(f"Error loading CSV data for {book_name}: {e}")
            return []
    
    def load_jsonl_data(self, book_name: str, data_type: str) -> List[SourceAnalysis]:
        """Load JSONL training/analysis data"""
        jsonl_path = self.output_dir / book_name / f"{book_name}_{data_type}.jsonl"
        
        if not jsonl_path.exists():
            logger.warning(f"JSONL file not found: {jsonl_path}")
            return []
        
        analyses = []
        try:
            with open(jsonl_path, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line.strip())
                    
                    analysis = SourceAnalysis(
                        instruction=data.get('instruction', ''),
                        input_text=data.get('input', ''),
                        output=data.get('output', ''),
                        metadata=data.get('metadata', {})
                    )
                    analyses.append(analysis)
            
            logger.info(f"Loaded {len(analyses)} {data_type} records from {book_name}")
            return analyses
            
        except Exception as e:
            logger.error(f"Error loading JSONL data for {book_name} {data_type}: {e}")
            return []
    
    def load_markdown_data(self, book_name: str) -> str:
        """Load Markdown source preview data"""
        md_path = self.output_dir / book_name / f"{book_name}.md"
        
        if not md_path.exists():
            logger.warning(f"Markdown file not found: {md_path}")
            return ""
        
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Loaded Markdown content from {book_name}")
            return content
            
        except Exception as e:
            logger.error(f"Error loading Markdown data for {book_name}: {e}")
            return ""
    
    def create_verse_documents(self, verses: List[VerseEntity]) -> List[Document]:
        """Convert verse entities to LightRAG documents"""
        documents = []
        
        for verse in verses:
            # Create rich metadata for entity-relation reasoning
            metadata = {
                "type": "verse",
                "book": verse.book,
                "chapter": verse.chapter,
                "verse": verse.verse,
                "reference": verse.reference,
                "sources": verse.sources,
                "primary_source": verse.primary_source,
                "source_count": verse.source_count,
                "word_count": verse.word_count,
                "source_sequence": verse.source_sequence,
                "source_percentages": verse.source_percentages,
                "redaction_indicators": verse.redaction_indicators,
                "has_j_source": "J" in verse.sources,
                "has_e_source": "E" in verse.sources,
                "has_p_source": "P" in verse.sources,
                "has_r_source": "R" in verse.sources,
                "is_multi_source": verse.source_count > 1,
                "text_j": verse.text_J,
                "text_e": verse.text_E,
                "text_p": verse.text_P,
                "text_r": verse.text_R
            }
            
            # Create document with verse text and metadata
            doc = Document(
                content=verse.text,
                metadata=metadata,
                doc_id=f"{verse.book}_{verse.chapter}_{verse.verse}"
            )
            documents.append(doc)
        
        return documents
    
    def create_analysis_documents(self, analyses: List[SourceAnalysis], data_type: str) -> List[Document]:
        """Convert source analysis data to LightRAG documents"""
        documents = []
        
        for i, analysis in enumerate(analyses):
            # Create metadata for analysis documents
            metadata = {
                "type": f"analysis_{data_type}",
                "instruction": analysis.instruction,
                "output": analysis.output,
                "book": analysis.metadata.get('book', ''),
                "chapter": analysis.metadata.get('chapter', ''),
                "verse": analysis.metadata.get('verse', ''),
                "sources": analysis.metadata.get('sources', []),
                "is_multi_source": analysis.metadata.get('is_multi_source', False)
            }
            
            # Create document with input text and metadata
            doc = Document(
                content=analysis.input_text,
                metadata=metadata,
                doc_id=f"{data_type}_{i}"
            )
            documents.append(doc)
        
        return documents
    
    def create_markdown_documents(self, content: str, book_name: str) -> List[Document]:
        """Convert Markdown content to LightRAG documents"""
        documents = []
        
        # Split content into chapters
        chapters = re.split(r'## Chapter (\d+)', content)
        
        for i in range(1, len(chapters), 2):
            if i + 1 < len(chapters):
                chapter_num = chapters[i]
                chapter_content = chapters[i + 1]
                
                # Create metadata for chapter documents
                metadata = {
                    "type": "markdown_chapter",
                    "book": book_name,
                    "chapter": int(chapter_num),
                    "content_type": "source_preview"
                }
                
                # Create document with chapter content
                doc = Document(
                    content=chapter_content,
                    metadata=metadata,
                    doc_id=f"{book_name}_chapter_{chapter_num}"
                )
                documents.append(doc)
        
        return documents
    
    def ingest_book(self, book_name: str) -> bool:
        """Ingest all data for a specific book"""
        logger.info(f"Starting ingestion for {book_name}")
        
        if not LIGHTRAG_AVAILABLE:
            logger.warning("LightRAG not available. Running in simulation mode.")
            return self.simulate_ingestion(book_name)
        
        try:
            all_documents = []
            
            # 1. Load and process verse data
            verses = self.load_csv_data(book_name)
            if verses:
                verse_docs = self.create_verse_documents(verses)
                all_documents.extend(verse_docs)
                logger.info(f"Created {len(verse_docs)} verse documents")
            
            # 2. Load and process training data
            training_data = self.load_jsonl_data(book_name, "training")
            if training_data:
                training_docs = self.create_analysis_documents(training_data, "training")
                all_documents.extend(training_docs)
                logger.info(f"Created {len(training_docs)} training documents")
            
            # 3. Load and process classification data
            classification_data = self.load_jsonl_data(book_name, "classification")
            if classification_data:
                classification_docs = self.create_analysis_documents(classification_data, "classification")
                all_documents.extend(classification_docs)
                logger.info(f"Created {len(classification_docs)} classification documents")
            
            # 4. Load and process sequence data
            sequence_data = self.load_jsonl_data(book_name, "sequence")
            if sequence_data:
                sequence_docs = self.create_analysis_documents(sequence_data, "sequence")
                all_documents.extend(sequence_docs)
                logger.info(f"Created {len(sequence_docs)} sequence documents")
            
            # 5. Load and process analysis data
            analysis_data = self.load_jsonl_data(book_name, "analysis")
            if analysis_data:
                analysis_docs = self.create_analysis_documents(analysis_data, "analysis")
                all_documents.extend(analysis_docs)
                logger.info(f"Created {len(analysis_docs)} analysis documents")
            
            # 6. Load and process Markdown data
            markdown_content = self.load_markdown_data(book_name)
            if markdown_content:
                markdown_docs = self.create_markdown_documents(markdown_content, book_name)
                all_documents.extend(markdown_docs)
                logger.info(f"Created {len(markdown_docs)} markdown documents")
            
            # 7. Ingest all documents into LightRAG
            if all_documents:
                self.lightrag.add_documents(all_documents)
                logger.info(f"Successfully ingested {len(all_documents)} documents for {book_name}")
                return True
            else:
                logger.warning(f"No documents created for {book_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error ingesting {book_name}: {e}")
            return False
    
    def simulate_ingestion(self, book_name: str) -> bool:
        """Simulate ingestion when LightRAG is not available"""
        logger.info(f"Simulating ingestion for {book_name}")
        
        # Load data to verify it exists
        verses = self.load_csv_data(book_name)
        training_data = self.load_jsonl_data(book_name, "training")
        markdown_content = self.load_markdown_data(book_name)
        
        total_items = len(verses) + len(training_data) + (1 if markdown_content else 0)
        
        logger.info(f"Simulation complete for {book_name}: {total_items} items would be ingested")
        return total_items > 0
    
    def ingest_all_books(self) -> Dict[str, bool]:
        """Ingest data for all available books"""
        books = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]
        results = {}
        
        logger.info("Starting ingestion for all books")
        
        for book in books:
            success = self.ingest_book(book)
            results[book] = success
        
        # Log summary
        successful = sum(results.values())
        total = len(results)
        logger.info(f"Ingestion complete: {successful}/{total} books successful")
        
        return results
    
    def create_entity_relations(self) -> Dict[str, Any]:
        """Create entity-relation mappings for structured queries"""
        relations = {
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
            },
            "relation_types": {
                "contains_source": "verse -> source",
                "belongs_to_book": "verse -> book",
                "has_chapter": "verse -> chapter",
                "multi_source": "verse -> multiple_sources",
                "redaction": "verse -> redaction_indicators"
            }
        }
        
        return relations
    
    def save_entity_relations(self):
        """Save entity-relation mappings to file"""
        relations = self.create_entity_relations()
        relations_path = self.lightrag_dir / "entity_relations.json"
        
        with open(relations_path, 'w', encoding='utf-8') as f:
            json.dump(relations, f, indent=2)
        
        logger.info(f"Entity relations saved to {relations_path}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the ingested collection"""
        if not LIGHTRAG_AVAILABLE:
            return {"status": "LightRAG not available"}
        
        try:
            stats = self.lightrag.get_collection_stats()
            return stats
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}

def main():
    """Main function to run the LightRAG ingestion pipeline"""
    print("🚀 KJV Sources LightRAG Ingestion Pipeline")
    print("=" * 50)
    
    # Initialize ingestion pipeline
    ingestion = KJVLightRAGIngestion()
    
    # Create entity relations
    ingestion.save_entity_relations()
    
    # Ingest all books
    results = ingestion.ingest_all_books()
    
    # Print results
    print("\n📊 Ingestion Results:")
    print("-" * 30)
    for book, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"{book}: {status}")
    
    # Get collection stats
    if LIGHTRAG_AVAILABLE:
        stats = ingestion.get_collection_stats()
        print(f"\n📈 Collection Statistics:")
        print("-" * 30)
        for key, value in stats.items():
            print(f"{key}: {value}")
    
    print(f"\n🎯 Entity-Relation Reasoning Ready!")
    print(f"📁 Data stored in: {ingestion.lightrag_dir}")
    print(f"🔗 Entity relations: {ingestion.lightrag_dir}/entity_relations.json")

if __name__ == "__main__":
    main() 