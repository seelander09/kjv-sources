#!/usr/bin/env python3
"""
Word-Level Parser for KJV Bible Mathematical Analysis
====================================================

This module provides word-level parsing capabilities for mathematical pattern analysis
of the King James Version Bible, similar to the approach used by KJV Code.

Author: KJV Sources Project
License: MIT
"""

import os
import re
import json
import csv
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WordData:
    """Represents a single word with full metadata"""
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
    source_attribution: List[str]  # J, E, P, R if applicable
    mathematical_properties: Dict[str, Any]

class WordLevelParser:
    """Parser for word-level analysis of KJV Bible text"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.words: List[WordData] = []
        self.word_positions: Dict[str, List[int]] = defaultdict(list)
        self.book_positions: Dict[str, List[int]] = defaultdict(list)
        self.verse_positions: Dict[str, List[int]] = defaultdict(list)
        
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
        
        # Book names mapping
        self.book_names = {
            'genesis': 'Genesis', 'exodus': 'Exodus', 'leviticus': 'Leviticus',
            'numbers': 'Numbers', 'deuteronomy': 'Deuteronomy', 'joshua': 'Joshua',
            'judges': 'Judges', 'ruth': 'Ruth', 'samuel': 'Samuel', 'kings': 'Kings',
            'chronicles': 'Chronicles', 'ezra': 'Ezra', 'nehemiah': 'Nehemiah',
            'esther': 'Esther', 'job': 'Job', 'psalms': 'Psalms', 'psalm': 'Psalm',
            'proverbs': 'Proverbs', 'ecclesiastes': 'Ecclesiastes', 'song': 'Song of Solomon',
            'isaiah': 'Isaiah', 'jeremiah': 'Jeremiah', 'lamentations': 'Lamentations',
            'ezekiel': 'Ezekiel', 'daniel': 'Daniel', 'hosea': 'Hosea', 'joel': 'Joel',
            'amos': 'Amos', 'obadiah': 'Obadiah', 'jonah': 'Jonah', 'micah': 'Micah',
            'nahum': 'Nahum', 'habakkuk': 'Habakkuk', 'zephaniah': 'Zephaniah',
            'haggai': 'Haggai', 'zechariah': 'Zechariah', 'malachi': 'Malachi',
            'matthew': 'Matthew', 'mark': 'Mark', 'luke': 'Luke', 'john': 'John',
            'acts': 'Acts', 'romans': 'Romans', 'corinthians': 'Corinthians',
            'galatians': 'Galatians', 'ephesians': 'Ephesians', 'philippians': 'Philippians',
            'colossians': 'Colossians', 'thessalonians': 'Thessalonians',
            'timothy': 'Timothy', 'titus': 'Titus', 'philemon': 'Philemon',
            'hebrews': 'Hebrews', 'james': 'James', 'peter': 'Peter', 'john': 'John',
            'jude': 'Jude', 'revelation': 'Revelation'
        }
    
    def parse_word_level_file(self, file_path: str) -> List[WordData]:
        """Parse a word-per-line KJV file into structured word data"""
        logger.info(f"Parsing word-level file: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return []
        
        words = []
        current_position = 0
        current_book = None
        current_chapter = 0
        current_verse = 0
        current_verse_id = ""
        current_canonical_ref = ""
        word_in_verse = 0
        word_in_chapter = 0
        word_in_book = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                # Check for book headers
                if self._is_book_header(line):
                    current_book = self._extract_book_name(line)
                    current_chapter = 0
                    current_verse = 0
                    word_in_book = 0
                    logger.info(f"Processing book: {current_book}")
                    continue
                
                # Check for chapter headers
                if self._is_chapter_header(line):
                    current_chapter = self._extract_chapter_number(line)
                    current_verse = 0
                    word_in_chapter = 0
                    continue
                
                # Check for verse headers
                if self._is_verse_header(line):
                    current_verse = self._extract_verse_number(line)
                    current_verse_id = f"{current_book}_{current_chapter}_{current_verse}"
                    current_canonical_ref = f"{current_book} {current_chapter}:{current_verse}"
                    word_in_verse = 0
                    continue
                
                # Process regular word
                if current_book and current_chapter and current_verse:
                    word_data = WordData(
                        word=line,
                        position_global=current_position,
                        position_in_verse=word_in_verse,
                        position_in_chapter=word_in_chapter,
                        position_in_book=word_in_book,
                        book=current_book,
                        chapter=current_chapter,
                        verse=current_verse,
                        verse_id=current_verse_id,
                        canonical_reference=current_canonical_ref,
                        word_length=len(line),
                        is_capitalized=line[0].isupper() if line else False,
                        is_number=line.isdigit(),
                        is_proper_name=self._is_proper_name(line),
                        source_attribution=[],  # Will be populated later
                        mathematical_properties=self._calculate_mathematical_properties(line, current_position)
                    )
                    
                    words.append(word_data)
                    
                    # Update position tracking
                    self.word_positions[line.lower()].append(current_position)
                    self.book_positions[current_book].append(current_position)
                    self.verse_positions[current_verse_id].append(current_position)
                    
                    current_position += 1
                    word_in_verse += 1
                    word_in_chapter += 1
                    word_in_book += 1
        
        self.words = words
        logger.info(f"Parsed {len(words)} words from {file_path}")
        return words
    
    def _is_book_header(self, line: str) -> bool:
        """Check if line is a book header"""
        return re.match(r'^[A-Z\s]+$', line.strip()) and len(line.strip()) > 3
    
    def _is_chapter_header(self, line: str) -> bool:
        """Check if line is a chapter header"""
        return re.match(r'^Chapter\s+\d+$', line.strip(), re.IGNORECASE)
    
    def _is_verse_header(self, line: str) -> bool:
        """Check if line is a verse header"""
        return re.match(r'^\d+$', line.strip())
    
    def _extract_book_name(self, line: str) -> str:
        """Extract book name from header line"""
        book_name = line.strip()
        return self.book_names.get(book_name.lower(), book_name)
    
    def _extract_chapter_number(self, line: str) -> int:
        """Extract chapter number from header line"""
        match = re.search(r'\d+', line)
        return int(match.group()) if match else 0
    
    def _extract_verse_number(self, line: str) -> int:
        """Extract verse number from header line"""
        return int(line.strip())
    
    def _is_proper_name(self, word: str) -> bool:
        """Check if word is likely a proper name"""
        # Remove punctuation and check
        clean_word = re.sub(r'[^\w]', '', word)
        
        # Check against known proper names
        if clean_word.lower() in {name.lower() for name in self.proper_names}:
            return True
        
        # Check capitalization pattern
        if word and word[0].isupper() and len(word) > 2:
            return True
        
        return False
    
    def _calculate_mathematical_properties(self, word: str, position: int) -> Dict[str, Any]:
        """Calculate mathematical properties for a word"""
        return {
            'position': position,
            'word_length': len(word),
            'is_sevened': len(word) % 7 == 0,
            'is_77': len(word) == 77,
            'is_777': len(word) == 777,
            'is_70x7': len(word) == 490,
            'position_mod_7': position % 7,
            'position_mod_77': position % 77,
            'position_mod_777': position % 777,
            'is_prime_length': self._is_prime(len(word)),
            'is_perfect_square_length': self._is_perfect_square(len(word)),
            'is_fibonacci_length': self._is_fibonacci(len(word))
        }
    
    def _is_prime(self, n: int) -> bool:
        """Check if number is prime"""
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    def _is_perfect_square(self, n: int) -> bool:
        """Check if number is a perfect square"""
        root = int(n ** 0.5)
        return root * root == n
    
    def _is_fibonacci(self, n: int) -> bool:
        """Check if number is in Fibonacci sequence"""
        if n < 0:
            return False
        if n == 0 or n == 1:
            return True
        
        a, b = 0, 1
        while b <= n:
            if b == n:
                return True
            a, b = b, a + b
        return False
    
    def save_word_data(self, output_file: str = None):
        """Save word data to CSV file"""
        if not output_file:
            output_file = os.path.join(self.output_dir, "word_level_analysis.csv")
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'word', 'position_global', 'position_in_verse', 'position_in_chapter',
                'position_in_book', 'book', 'chapter', 'verse', 'verse_id',
                'canonical_reference', 'word_length', 'is_capitalized', 'is_number',
                'is_proper_name', 'source_attribution', 'mathematical_properties'
            ])
            
            for word_data in self.words:
                writer.writerow([
                    word_data.word,
                    word_data.position_global,
                    word_data.position_in_verse,
                    word_data.position_in_chapter,
                    word_data.position_in_book,
                    word_data.book,
                    word_data.chapter,
                    word_data.verse,
                    word_data.verse_id,
                    word_data.canonical_reference,
                    word_data.word_length,
                    word_data.is_capitalized,
                    word_data.is_number,
                    word_data.is_proper_name,
                    ';'.join(word_data.source_attribution),
                    json.dumps(word_data.mathematical_properties)
                ])
        
        logger.info(f"Saved word data to {output_file}")
    
    def get_word_statistics(self) -> Dict[str, Any]:
        """Get comprehensive word statistics"""
        if not self.words:
            return {}
        
        total_words = len(self.words)
        word_counts = Counter(word_data.word.lower() for word_data in self.words)
        
        return {
            'total_words': total_words,
            'unique_words': len(word_counts),
            'most_common_words': word_counts.most_common(20),
            'word_length_distribution': Counter(word_data.word_length for word_data in self.words),
            'proper_names_count': sum(1 for word_data in self.words if word_data.is_proper_name),
            'numbers_count': sum(1 for word_data in self.words if word_data.is_number),
            'capitalized_count': sum(1 for word_data in self.words if word_data.is_capitalized),
            'is_sevened_total': total_words % 7 == 0,
            'is_823543': total_words == 823543,  # 7^7
            'book_word_counts': Counter(word_data.book for word_data in self.words)
        }
