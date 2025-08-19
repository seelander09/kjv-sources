#!/usr/bin/env python3
"""
Process Deuteronomist Source for Vector Database
===============================================

This script processes the Deuteronomist source from the wikitext files and prepares
it for ingestion into the vector database for LLM analysis and comparison.

The script handles:
1. Parsing the Deuteronomist source with proper color mapping
2. Extracting sub-sources (Dtr1, Dtr2, Song of Moses)
3. Creating structured data for vector database ingestion
4. Generating analysis-ready datasets
"""

import os
import re
import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DeuteronomistVerse:
    """Represents a verse from the Deuteronomist source"""
    reference: str
    text: str
    chapter: int
    verse: int
    sub_source: str  # Dtr1, Dtr2, Song of Moses, Core
    color: str
    full_text: str
    word_count: int
    metadata: Dict[str, Any]

class DeuteronomistProcessor:
    """Processes Deuteronomist source for vector database ingestion"""
    
    def __init__(self, wiki_dir: str = "wiki_markdown", output_dir: str = "output"):
        self.wiki_dir = Path(wiki_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Deuteronomist color mappings
        self.deuteronomist_colors = {
            "#000000": "Core",           # Core Deuteronomic Code
            "#800080": "Dtr1",           # First Deuteronomist version
            "#008800": "Dtr2",           # Second Deuteronomist version
            "#00FF88": "Song_of_Moses",  # Song of Moses
            "#880000": "Late_insertion"  # Late insertions
        }
        
        # Source files to process
        self.source_files = [
            "Deuteronomist_source.wikitext",
            "First_Deuteronomist_Version.wikitext",
            "Deuteronomic_Laws.wikitext",
            "Song_of_Moses.wikitext"
        ]
    
    def parse_deuteronomist_wikitext(self, file_path: Path) -> List[DeuteronomistVerse]:
        """Parse Deuteronomist wikitext file and extract verses"""
        verses = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract verses with color coding
            verse_pattern = r'{{font\|(\d+)\|size=smaller\|color=#0000FF}}{{font\|([^}]+)\|color=([^}]+)}}'
            matches = re.findall(verse_pattern, content, re.DOTALL)
            
            for match in matches:
                verse_num = match[0]
                verse_text = match[1].strip()
                color = match[2]
                
                if not verse_text:
                    continue
                
                # Determine sub-source from color
                sub_source = self.deuteronomist_colors.get(color, "Unknown")
                
                # Create verse object
                verse = DeuteronomistVerse(
                    reference=f"Deuteronomy {verse_num}",
                    text=verse_text,
                    chapter=1,  # Will be updated if chapter info is available
                    verse=int(verse_num),
                    sub_source=sub_source,
                    color=color,
                    full_text=verse_text,
                    word_count=len(verse_text.split()),
                    metadata={
                        "source_file": file_path.name,
                        "color_code": color,
                        "sub_source": sub_source,
                        "parsing_date": datetime.now().isoformat()
                    }
                )
                verses.append(verse)
            
            logger.info(f"Parsed {len(verses)} verses from {file_path.name}")
            return verses
            
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return []
    
    def create_analysis_dataset(self, verses: List[DeuteronomistVerse]) -> List[Dict[str, Any]]:
        """Create analysis dataset for LLM training"""
        dataset = []
        
        for verse in verses:
            # Create instruction-following examples
            instruction_examples = [
                {
                    "instruction": "Analyze the Deuteronomist source characteristics in this verse.",
                    "input": f"Verse: {verse.text}\nReference: {verse.reference}",
                    "output": f"This verse belongs to the {verse.sub_source} sub-source of the Deuteronomist tradition. It contains {verse.word_count} words and shows characteristic Deuteronomic themes.",
                    "metadata": {
                        "book": "Deuteronomy",
                        "verse": verse.verse,
                        "sub_source": verse.sub_source,
                        "word_count": verse.word_count
                    }
                },
                {
                    "instruction": "Compare this Deuteronomist verse with other biblical sources.",
                    "input": f"Deuteronomist verse: {verse.text}",
                    "output": f"This {verse.sub_source} verse demonstrates characteristic Deuteronomic theology, including covenant language and exhortation to obedience.",
                    "metadata": {
                        "source": "D",
                        "sub_source": verse.sub_source,
                        "analysis_type": "comparative"
                    }
                }
            ]
            
            dataset.extend(instruction_examples)
        
        return dataset
    
    def create_vector_db_documents(self, verses: List[DeuteronomistVerse]) -> List[Dict[str, Any]]:
        """Create documents for vector database ingestion"""
        documents = []
        
        for verse in verses:
            # Create document for vector database
            doc = {
                "id": f"deuteronomist_{verse.verse}",
                "text": verse.text,
                "metadata": {
                    "reference": verse.reference,
                    "book": "Deuteronomy",
                    "chapter": verse.chapter,
                    "verse": verse.verse,
                    "sub_source": verse.sub_source,
                    "source": "D",
                    "word_count": verse.word_count,
                    "color_code": verse.color,
                    "document_type": "deuteronomist_verse",
                    "parsing_date": datetime.now().isoformat()
                },
                "embedding_text": f"Deuteronomy {verse.verse}: {verse.text} [Deuteronomist source, {verse.sub_source} sub-source]"
            }
            documents.append(doc)
        
        return documents
    
    def save_csv_output(self, verses: List[DeuteronomistVerse], filename: str) -> None:
        """Save verses to CSV file"""
        csv_path = self.output_dir / filename
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'reference', 'text', 'chapter', 'verse', 'sub_source', 
                'color', 'word_count', 'source_file', 'parsing_date'
            ])
            
            for verse in verses:
                writer.writerow([
                    verse.reference,
                    verse.text,
                    verse.chapter,
                    verse.verse,
                    verse.sub_source,
                    verse.color,
                    verse.word_count,
                    verse.metadata.get('source_file', ''),
                    verse.metadata.get('parsing_date', '')
                ])
        
        logger.info(f"Saved CSV: {csv_path}")
    
    def save_jsonl_output(self, data: List[Dict[str, Any]], filename: str) -> None:
        """Save data to JSONL file"""
        jsonl_path = self.output_dir / filename
        
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved JSONL: {jsonl_path}")
    
    def process_all_sources(self) -> Dict[str, Any]:
        """Process all Deuteronomist source files"""
        logger.info("🚀 Processing Deuteronomist sources...")
        
        all_verses = []
        results = {
            "total_verses": 0,
            "sub_sources": {},
            "files_processed": [],
            "errors": []
        }
        
        # Process each source file
        for filename in self.source_files:
            file_path = self.wiki_dir / filename
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                results["errors"].append(f"File not found: {filename}")
                continue
            
            logger.info(f"📖 Processing: {filename}")
            verses = self.parse_deuteronomist_wikitext(file_path)
            all_verses.extend(verses)
            results["files_processed"].append(filename)
            
            # Count by sub-source
            for verse in verses:
                sub_source = verse.sub_source
                if sub_source not in results["sub_sources"]:
                    results["sub_sources"][sub_source] = 0
                results["sub_sources"][sub_source] += 1
        
        results["total_verses"] = len(all_verses)
        
        if all_verses:
            # Save outputs
            self.save_csv_output(all_verses, "deuteronomist_verses.csv")
            
            # Create analysis dataset
            analysis_dataset = self.create_analysis_dataset(all_verses)
            self.save_jsonl_output(analysis_dataset, "deuteronomist_analysis.jsonl")
            
            # Create vector database documents
            vector_docs = self.create_vector_db_documents(all_verses)
            self.save_jsonl_output(vector_docs, "deuteronomist_vector_docs.jsonl")
            
            # Create summary metadata
            summary = {
                "processing_date": datetime.now().isoformat(),
                "total_verses": len(all_verses),
                "sub_sources": results["sub_sources"],
                "files_processed": results["files_processed"],
                "output_files": [
                    "deuteronomist_verses.csv",
                    "deuteronomist_analysis.jsonl", 
                    "deuteronomist_vector_docs.jsonl"
                ]
            }
            
            summary_path = self.output_dir / "deuteronomist_processing_summary.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📄 Summary saved: {summary_path}")
        
        return results

def main():
    """Main function"""
    processor = DeuteronomistProcessor()
    results = processor.process_all_sources()
    
    print(f"\n📊 Processing Summary:")
    print(f"Total verses: {results['total_verses']}")
    print(f"Files processed: {len(results['files_processed'])}")
    print(f"Sub-sources found: {list(results['sub_sources'].keys())}")
    
    if results["errors"]:
        print(f"Errors: {len(results['errors'])}")
        for error in results["errors"]:
            print(f"  - {error}")

if __name__ == "__main__":
    main()
