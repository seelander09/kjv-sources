#!/usr/bin/env python3
"""
Ingest Additional Sources into Vector Database
=============================================

This script ingests additional Wikiversity source pages into the LightRAG vector
database for LLM analysis and comparison. It processes individual source pages,
sub-sources, and specialized analysis pages.

The script handles:
1. Loading additional source markdown files
2. Creating structured documents for vector database
3. Ingesting into LightRAG with proper metadata
4. Creating analysis-ready datasets
"""

import os
import re
import json
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SourceDocument:
    """Represents a source document for vector database ingestion"""
    id: str
    title: str
    content: str
    source_type: str  # individual_source, sub_source, specialized, comparative
    category: str
    metadata: Dict[str, Any]
    embedding_text: str

class AdditionalSourcesIngestion:
    """Ingests additional source pages into the vector database"""
    
    def __init__(self, wiki_dir: str = "wiki_markdown", lightrag_dir: str = "lightrag_data"):
        self.wiki_dir = Path(wiki_dir)
        self.lightrag_dir = Path(lightrag_dir)
        self.lightrag_dir.mkdir(exist_ok=True)
        
        # Source categories and their descriptions
        self.source_categories = {
            "individual_source": "Complete individual source in isolation",
            "sub_source": "Sub-component of a larger source",
            "specialized": "Specialized analysis or thematic content",
            "comparative": "Content for comparative analysis"
        }
        
        # Try to import LightRAG
        try:
            from lightrag import LightRAG
            from lightrag.ingest import Document, Chunk
            self.LIGHTRAG_AVAILABLE = True
            self.LightRAG = LightRAG
            self.Document = Document
            self.Chunk = Chunk
        except ImportError:
            self.LIGHTRAG_AVAILABLE = False
            logger.warning("LightRAG not available. Running in simulation mode.")
    
    def load_markdown_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load and parse a markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title from first heading
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else file_path.stem
            
            # Clean content (remove markdown formatting)
            clean_content = re.sub(r'#{1,6}\s+', '', content)  # Remove headers
            clean_content = re.sub(r'\*\*(.+?)\*\*', r'\1', clean_content)  # Remove bold
            clean_content = re.sub(r'\*(.+?)\*', r'\1', clean_content)  # Remove italic
            clean_content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean_content)  # Remove links
            
            return {
                "title": title,
                "content": clean_content.strip(),
                "raw_content": content,
                "file_path": str(file_path),
                "file_size": len(content)
            }
            
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return None
    
    def categorize_source(self, filename: str, content: str) -> str:
        """Categorize source based on filename and content"""
        filename_lower = filename.lower()
        
        if "isolated" in filename_lower:
            return "individual_source"
        elif any(sub in filename_lower for sub in ["dtr", "version", "laws", "song"]):
            return "sub_source"
        elif any(spec in filename_lower for spec in ["holiness", "levitical", "ritual"]):
            return "specialized"
        elif any(comp in filename_lower for comp in ["covenant", "narrative", "comparative"]):
            return "comparative"
        else:
            return "specialized"
    
    def create_source_documents(self) -> List[SourceDocument]:
        """Create source documents from markdown files"""
        documents = []
        
        # Find all markdown files (excluding existing book files)
        md_files = list(self.wiki_dir.glob("*.md"))
        
        # Filter out existing book files
        existing_books = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]
        additional_files = [f for f in md_files if not any(book in f.name for book in existing_books)]
        
        logger.info(f"Found {len(additional_files)} additional source files")
        
        for file_path in additional_files:
            file_data = self.load_markdown_file(file_path)
            if not file_data:
                continue
            
            # Categorize the source
            category = self.categorize_source(file_path.name, file_data["content"])
            
            # Create document ID
            doc_id = f"additional_source_{file_path.stem}"
            
            # Create embedding text
            embedding_text = f"{file_data['title']}: {file_data['content'][:500]}..."
            
            # Create source document
            doc = SourceDocument(
                id=doc_id,
                title=file_data["title"],
                content=file_data["content"],
                source_type=category,
                category=category,
                metadata={
                    "filename": file_path.name,
                    "file_path": str(file_path),
                    "file_size": file_data["file_size"],
                    "ingestion_date": datetime.now().isoformat(),
                    "source_category": category,
                    "document_type": "additional_source"
                },
                embedding_text=embedding_text
            )
            
            documents.append(doc)
        
        return documents
    
    def create_analysis_datasets(self, documents: List[SourceDocument]) -> Dict[str, List[Dict[str, Any]]]:
        """Create analysis datasets for LLM training"""
        datasets = {
            "source_analysis": [],
            "comparative_analysis": [],
            "thematic_analysis": []
        }
        
        for doc in documents:
            # Source analysis examples
            source_analysis = {
                "instruction": f"Analyze the characteristics of this {doc.source_type} source.",
                "input": f"Source: {doc.title}\nContent: {doc.content[:300]}...",
                "output": f"This {doc.source_type} source titled '{doc.title}' demonstrates characteristic themes and language patterns typical of its category.",
                "metadata": {
                    "source_id": doc.id,
                    "source_type": doc.source_type,
                    "category": doc.category,
                    "analysis_type": "source_characteristics"
                }
            }
            datasets["source_analysis"].append(source_analysis)
            
            # Comparative analysis examples
            if doc.source_type in ["individual_source", "sub_source"]:
                comparative = {
                    "instruction": "Compare this source with other biblical sources.",
                    "input": f"Source: {doc.title}\nContent: {doc.content[:200]}...",
                    "output": f"This {doc.source_type} source can be compared with other sources to identify unique characteristics and shared themes.",
                    "metadata": {
                        "source_id": doc.id,
                        "source_type": doc.source_type,
                        "analysis_type": "comparative"
                    }
                }
                datasets["comparative_analysis"].append(comparative)
            
            # Thematic analysis examples
            if doc.source_type == "specialized":
                thematic = {
                    "instruction": "Identify key themes in this specialized source.",
                    "input": f"Specialized source: {doc.title}\nContent: {doc.content[:250]}...",
                    "output": f"This specialized source focuses on specific themes and provides detailed analysis of particular aspects.",
                    "metadata": {
                        "source_id": doc.id,
                        "source_type": doc.source_type,
                        "analysis_type": "thematic"
                    }
                }
                datasets["thematic_analysis"].append(thematic)
        
        return datasets
    
    def ingest_to_lightrag(self, documents: List[SourceDocument]) -> bool:
        """Ingest documents into LightRAG vector database"""
        if not self.LIGHTRAG_AVAILABLE:
            logger.warning("LightRAG not available. Skipping ingestion.")
            return False
        
        try:
            # Initialize LightRAG
            lightrag = self.LightRAG(
                collection_name="kjv_additional_sources",
                persist_directory=str(self.lightrag_dir)
            )
            
            # Convert documents to LightRAG format
            lightrag_docs = []
            for doc in documents:
                lightrag_doc = self.Document(
                    id=doc.id,
                    text=doc.embedding_text,
                    metadata=doc.metadata
                )
                lightrag_docs.append(lightrag_doc)
            
            # Ingest documents
            lightrag.ingest(lightrag_docs)
            
            logger.info(f"✅ Ingested {len(documents)} documents into LightRAG")
            return True
            
        except Exception as e:
            logger.error(f"Error ingesting to LightRAG: {e}")
            return False
    
    def save_jsonl_datasets(self, datasets: Dict[str, List[Dict[str, Any]]]) -> None:
        """Save analysis datasets to JSONL files"""
        for dataset_name, data in datasets.items():
            if data:
                filename = f"additional_sources_{dataset_name}.jsonl"
                file_path = self.lightrag_dir / filename
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    for item in data:
                        f.write(json.dumps(item, ensure_ascii=False) + '\n')
                
                logger.info(f"Saved {dataset_name} dataset: {file_path}")
    
    def create_ingestion_summary(self, documents: List[SourceDocument], datasets: Dict[str, List[Dict[str, Any]]]) -> None:
        """Create ingestion summary"""
        summary = {
            "ingestion_date": datetime.now().isoformat(),
            "total_documents": len(documents),
            "source_types": {},
            "categories": {},
            "datasets": {},
            "files_processed": []
        }
        
        # Count by source type and category
        for doc in documents:
            if doc.source_type not in summary["source_types"]:
                summary["source_types"][doc.source_type] = 0
            summary["source_types"][doc.source_type] += 1
            
            if doc.category not in summary["categories"]:
                summary["categories"][doc.category] = 0
            summary["categories"][doc.category] += 1
            
            summary["files_processed"].append(doc.metadata["filename"])
        
        # Count dataset sizes
        for dataset_name, data in datasets.items():
            summary["datasets"][dataset_name] = len(data)
        
        # Save summary
        summary_path = self.lightrag_dir / "additional_sources_ingestion_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Ingestion summary saved: {summary_path}")
    
    def process_all_sources(self) -> Dict[str, Any]:
        """Process all additional sources"""
        logger.info("🚀 Processing additional sources for vector database ingestion...")
        
        # Create source documents
        documents = self.create_source_documents()
        
        if not documents:
            logger.warning("No additional source documents found")
            return {"error": "No documents found"}
        
        # Create analysis datasets
        datasets = self.create_analysis_datasets(documents)
        
        # Save datasets
        self.save_jsonl_datasets(datasets)
        
        # Ingest to LightRAG
        ingestion_success = self.ingest_to_lightrag(documents)
        
        # Create summary
        self.create_ingestion_summary(documents, datasets)
        
        results = {
            "total_documents": len(documents),
            "source_types": {},
            "categories": {},
            "datasets_created": list(datasets.keys()),
            "ingestion_success": ingestion_success
        }
        
        # Count by type and category
        for doc in documents:
            if doc.source_type not in results["source_types"]:
                results["source_types"][doc.source_type] = 0
            results["source_types"][doc.source_type] += 1
            
            if doc.category not in results["categories"]:
                results["categories"][doc.category] = 0
            results["categories"][doc.category] += 1
        
        return results

def main():
    """Main function"""
    ingestion = AdditionalSourcesIngestion()
    results = ingestion.process_all_sources()
    
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return
    
    print(f"\n📊 Ingestion Summary:")
    print(f"Total documents: {results['total_documents']}")
    print(f"Source types: {results['source_types']}")
    print(f"Categories: {results['categories']}")
    print(f"Datasets created: {results['datasets_created']}")
    print(f"Ingestion success: {results['ingestion_success']}")

if __name__ == "__main__":
    main()
