#!/usr/bin/env python3
"""
CSV Data Loader for KJV Sources
==============================

This module loads data from the existing CSV files and converts them into
word-level data for mathematical analysis.

Author: KJV Sources Project
License: MIT
"""

import os
import csv
import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from word_level_parser import WordData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSVDataLoader:
    """Loader for converting CSV data to word-level data"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.word_data: List[WordData] = []
        self.global_position = 0
        
        # Common proper names in the Bible
        self.proper_names = {
            'God', 'Lord', 'Jesus', 'Christ', 'Moses', 'David', 'Abraham', 'Isaac', 'Jacob',
            'Joseph', 'Noah', 'Adam', 'Eve', 'Cain', 'Abel', 'Seth', 'Enoch', 'Lamech',
            'Shem', 'Ham', 'Japheth', 'Sarah', 'Rebekah', 'Rachel', 'Leah', 'Benjamin',
            'Judah', 'Reuben', 'Simeon', 'Levi', 'Dan', 'Naphtali', 'Gad', 'Asher',
            'Issachar', 'Zebulun', 'Manasseh', 'Ephraim', 'Joshua', 'Caleb', 'Aaron',
            'Miriam', 'Samuel', 'Saul', 'Solomon', 'Elijah', 'Elisha', 'Isaiah',
            'Jeremiah', 'Ezekiel', 'Daniel', 'Hosea', 'Joel', 'Amos', 'Obadiah',
            'Jonah', 'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai', 'Zechariah',
            'Malachi', 'Matthew', 'Mark', 'Luke', 'John', 'Peter', 'Paul', 'James',
            'Jude', 'Timothy', 'Titus', 'Philemon', 'Barnabas', 'Stephen', 'Philip',
            'Thomas', 'Andrew', 'Simon', 'Judas', 'Mary', 'Elizabeth', 'Anna',
            'Zacharias', 'John', 'Herod', 'Pilate', 'Caiaphas', 'Annas', 'Gamaliel'
        }
    
    def load_all_books(self) -> List[WordData]:
        """Load data from all available CSV files"""
        logger.info("Loading data from all available CSV files...")
        
        # Get all book directories
        book_dirs = [d for d in os.listdir(self.output_dir) 
                    if os.path.isdir(os.path.join(self.output_dir, d))]
        
        for book_dir in sorted(book_dirs):
            book_path = os.path.join(self.output_dir, book_dir)
            csv_files = [f for f in os.listdir(book_path) if f.endswith('.csv')]
            
            if csv_files:
                # Use the latest CSV file
                latest_csv = sorted(csv_files)[-1]
                csv_path = os.path.join(book_path, latest_csv)
                logger.info(f"Loading {book_dir} from {latest_csv}")
                
                self.load_book_csv(csv_path, book_dir)
        
        logger.info(f"Loaded {len(self.word_data)} words total")
        return self.word_data
    
    def load_book_csv(self, csv_path: str, book_name: str) -> List[WordData]:
        """Load data from a single book CSV file"""
        logger.info(f"Loading {book_name} from {csv_path}")
        
        if not os.path.exists(csv_path):
            logger.error(f"CSV file not found: {csv_path}")
            return []
        
        book_words = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                verse_words = self.process_verse(row, book_name)
                book_words.extend(verse_words)
        
        self.word_data.extend(book_words)
        logger.info(f"Loaded {len(book_words)} words from {book_name}")
        return book_words
    
    def process_verse(self, row: Dict[str, str], book_name: str) -> List[WordData]:
        """Process a single verse row into word-level data"""
        verse_words = []
        
        # Extract verse information
        chapter = int(row['chapter'])
        verse = int(row['verse'])
        verse_id = row['verse_id']
        canonical_ref = row['canonical_reference']
        full_text = row['full_text']
        text_clean = row['text_clean']
        
        # Parse sources
        sources = row['sources'].split(';') if row['sources'] else []
        source_percentages = self.parse_source_percentages(row['source_percentages'])
        
        # Get source-specific texts
        text_j = row.get('text_J', '')
        text_e = row.get('text_E', '')
        text_p = row.get('text_P', '')
        text_r = row.get('text_R', '')
        
        # Split text into words
        words = text_clean.split()
        
        for word_pos, word in enumerate(words):
            # Clean the word
            clean_word = re.sub(r'[^\w\s]', '', word)
            if not clean_word:
                continue
            
            # Determine source attribution for this word
            word_sources = self.determine_word_sources(
                word, word_pos, words, sources, text_j, text_e, text_p, text_r
            )
            
            # Create WordData object
            word_data = WordData(
                word=clean_word,
                position_global=self.global_position + 1,
                position_in_verse=word_pos + 1,
                position_in_chapter=len(verse_words) + 1,  # Approximate
                position_in_book=len(self.word_data) + 1,  # Approximate
                book=book_name,
                chapter=chapter,
                verse=verse,
                verse_id=verse_id,
                canonical_reference=canonical_ref,
                word_length=len(clean_word),
                is_capitalized=clean_word[0].isupper() if clean_word else False,
                is_number=clean_word.isdigit(),
                is_proper_name=clean_word in self.proper_names,
                source_attribution=word_sources,
                mathematical_properties={
                    'source_percentages': source_percentages,
                    'verse_word_count': len(words),
                    'is_first_word': word_pos == 0,
                    'is_last_word': word_pos == len(words) - 1
                }
            )
            
            verse_words.append(word_data)
            self.global_position += 1
        
        return verse_words
    
    def determine_word_sources(self, word: str, word_pos: int, all_words: List[str], 
                             sources: List[str], text_j: str, text_e: str, 
                             text_p: str, text_r: str) -> List[str]:
        """Determine which sources contributed to a specific word"""
        word_sources = []
        
        # Simple heuristic: check if word appears in source-specific texts
        if text_j and word.lower() in text_j.lower():
            word_sources.append('J')
        if text_e and word.lower() in text_e.lower():
            word_sources.append('E')
        if text_p and word.lower() in text_p.lower():
            word_sources.append('P')
        if text_r and word.lower() in text_r.lower():
            word_sources.append('R')
        
        # If no specific sources found, use the general sources
        if not word_sources and sources:
            word_sources = sources
        
        return word_sources
    
    def parse_source_percentages(self, percentages_str: str) -> Dict[str, float]:
        """Parse source percentages string into dictionary"""
        if not percentages_str:
            return {}
        
        percentages = {}
        try:
            # Format: "J:39.4;E:0.0;P:57.0;R:2.1;UNKNOWN:0.0"
            for part in percentages_str.split(';'):
                if ':' in part:
                    source, percentage = part.split(':')
                    percentages[source] = float(percentage)
        except Exception as e:
            logger.warning(f"Failed to parse percentages: {percentages_str}, error: {e}")
        
        return percentages
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the loaded data"""
        if not self.word_data:
            return {}
        
        stats = {
            'total_words': len(self.word_data),
            'total_verses': len(set(word.verse_id for word in self.word_data)),
            'total_chapters': len(set(f"{word.book}_{word.chapter}" for word in self.word_data)),
            'total_books': len(set(word.book for word in self.word_data)),
            'books': list(set(word.book for word in self.word_data)),
            'word_length_distribution': {},
            'source_distribution': {},
            'proper_names': [],
            'capitalized_words': [],
            'numeric_words': []
        }
        
        # Analyze word properties
        for word in self.word_data:
            # Word length distribution
            length = word.word_length
            stats['word_length_distribution'][length] = stats['word_length_distribution'].get(length, 0) + 1
            
            # Source distribution
            for source in word.source_attribution:
                stats['source_distribution'][source] = stats['source_distribution'].get(source, 0) + 1
            
            # Collect special words
            if word.is_proper_name:
                stats['proper_names'].append(word.word)
            if word.is_capitalized:
                stats['capitalized_words'].append(word.word)
            if word.is_number:
                stats['numeric_words'].append(word.word)
        
        # Remove duplicates
        stats['proper_names'] = list(set(stats['proper_names']))
        stats['capitalized_words'] = list(set(stats['capitalized_words']))
        stats['numeric_words'] = list(set(stats['numeric_words']))
        
        return stats
    
    def save_word_data(self, output_file: str = "word_data.json"):
        """Save word data to JSON file"""
        logger.info(f"Saving word data to {output_file}")
        
        data = {
            'metadata': {
                'total_words': len(self.word_data),
                'books_loaded': list(set(word.book for word in self.word_data)),
                'version': '1.0.0'
            },
            'words': [
                {
                    'word': word.word,
                    'position_global': word.position_global,
                    'position_in_verse': word.position_in_verse,
                    'position_in_chapter': word.position_in_chapter,
                    'position_in_book': word.position_in_book,
                    'book': word.book,
                    'chapter': word.chapter,
                    'verse': word.verse,
                    'verse_id': word.verse_id,
                    'canonical_reference': word.canonical_reference,
                    'word_length': word.word_length,
                    'is_capitalized': word.is_capitalized,
                    'is_number': word.is_number,
                    'is_proper_name': word.is_proper_name,
                    'source_attribution': word.source_attribution,
                    'mathematical_properties': word.mathematical_properties
                }
                for word in self.word_data
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(self.word_data)} words to {output_file}")

def main():
    """Main function to load CSV data"""
    loader = CSVDataLoader()
    
    # Load all books
    word_data = loader.load_all_books()
    
    if word_data:
        # Get statistics
        stats = loader.get_statistics()
        logger.info("Data loading statistics:")
        logger.info(f"  Total words: {stats['total_words']}")
        logger.info(f"  Total verses: {stats['total_verses']}")
        logger.info(f"  Total chapters: {stats['total_chapters']}")
        logger.info(f"  Total books: {stats['total_books']}")
        logger.info(f"  Books: {', '.join(stats['books'])}")
        logger.info(f"  Source distribution: {stats['source_distribution']}")
        
        # Save to JSON
        loader.save_word_data()
        
        return word_data
    else:
        logger.error("No data loaded")
        return []

if __name__ == "__main__":
    main()
