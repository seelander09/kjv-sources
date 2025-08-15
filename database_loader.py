#!/usr/bin/env python3
"""
Database Loader for KJV Sources with Mathematical Analysis
=========================================================

This module handles loading word-level data and mathematical patterns into PostgreSQL.

Author: KJV Sources Project
License: MIT
"""

import os
import json
import csv
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from typing import List, Dict, Any, Optional
import logging

from word_level_parser import WordLevelParser, WordData
from mathematical_pattern_engine import MathematicalPatternEngine, WordPattern, GlobalAnalysis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BibleDatabaseLoader:
    """Database loader for KJV Bible with mathematical analysis"""
    
    def __init__(self, db_url: str, output_dir: str = "output"):
        self.db_url = db_url
        self.output_dir = output_dir
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.db_url)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            logger.info("Connected to database successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Database connection closed")
    
    def create_tables(self):
        """Create all necessary tables"""
        schema_file = "database_schema.sql"
        
        if not os.path.exists(schema_file):
            logger.error(f"Schema file not found: {schema_file}")
            return
        
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        try:
            self.cursor.execute(schema_sql)
            self.conn.commit()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            self.conn.rollback()
            raise
    
    def load_word_data(self, word_data: List[WordData]):
        """Load word-level data into database"""
        logger.info(f"Loading {len(word_data)} words into database...")
        
        # Prepare data for bulk insert
        words_data = []
        for word in word_data:
            words_data.append((
                word.verse_id,
                word.word,
                word.position_global,
                word.position_in_verse,
                word.position_in_chapter,
                word.position_in_book,
                word.word_length,
                word.is_capitalized,
                word.is_number,
                word.is_proper_name,
                word.source_attribution,
                json.dumps(word.mathematical_properties)
            ))
        
        # Bulk insert words
        insert_query = """
            INSERT INTO words (
                verse_id, word, position_global, position_in_verse, 
                position_in_chapter, position_in_book, word_length, 
                is_capitalized, is_number, is_proper_name, 
                source_attribution, mathematical_properties
            ) VALUES %s
        """
        
        try:
            execute_values(self.cursor, insert_query, words_data)
            self.conn.commit()
            logger.info(f"Successfully loaded {len(words_data)} words")
        except Exception as e:
            logger.error(f"Failed to load words: {e}")
            self.conn.rollback()
            raise
    
    def load_word_patterns(self, patterns: Dict[str, WordPattern]):
        """Load word patterns into database"""
        logger.info(f"Loading {len(patterns)} word patterns into database...")
        
        # Prepare data for bulk insert
        patterns_data = []
        for word, pattern in patterns.items():
            patterns_data.append((
                pattern.word,
                pattern.total_count,
                pattern.first_occurrence,
                pattern.last_occurrence,
                pattern.is_sevened,
                pattern.is_777,
                pattern.is_70x7,
                pattern.is_77,
                pattern.is_343,
                pattern.is_490,
                pattern.is_980,
                json.dumps(pattern.position_patterns),
                json.dumps(pattern.pattern_analysis)
            ))
        
        # Bulk insert patterns
        insert_query = """
            INSERT INTO word_patterns (
                word, total_count, first_occurrence, last_occurrence,
                is_sevened, is_777, is_70x7, is_77, is_343, is_490, is_980,
                position_patterns, pattern_analysis
            ) VALUES %s
        """
        
        try:
            execute_values(self.cursor, insert_query, patterns_data)
            self.conn.commit()
            logger.info(f"Successfully loaded {len(patterns_data)} patterns")
        except Exception as e:
            logger.error(f"Failed to load patterns: {e}")
            self.conn.rollback()
            raise
    
    def load_global_analysis(self, analysis: GlobalAnalysis):
        """Load global analysis into database"""
        logger.info("Loading global analysis into database...")
        
        insert_query = """
            INSERT INTO global_analysis (
                total_words, is_7_power, is_823543, word_count_analysis,
                book_analysis, chapter_analysis, verse_analysis
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            self.cursor.execute(insert_query, (
                analysis.total_words,
                analysis.is_7_power,
                analysis.is_823543,
                json.dumps(analysis.word_count_analysis),
                json.dumps(analysis.book_analysis),
                json.dumps(analysis.chapter_analysis),
                json.dumps(analysis.verse_analysis)
            ))
            self.conn.commit()
            logger.info("Successfully loaded global analysis")
        except Exception as e:
            logger.error(f"Failed to load global analysis: {e}")
            self.conn.rollback()
            raise
    
    def load_csv_to_verses(self, csv_path: str):
        """Load enhanced CSV data into verses table"""
        logger.info(f"Loading CSV data from {csv_path}")
        
        if not os.path.exists(csv_path):
            logger.error(f"CSV file not found: {csv_path}")
            return
        
        # First, ensure books and chapters exist
        self._ensure_books_and_chapters(csv_path)
        
        # Load verses
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Get book and chapter IDs
                book_id = self._get_book_id(row['book'])
                chapter_id = self._get_chapter_id(book_id, int(row['chapter']))
                
                # Insert verse
                insert_query = """
                    INSERT INTO verses (
                        chapter_id, verse, osis_ref, canonical_reference,
                        text_full, word_count, sources, source_count,
                        primary_source, source_sequence, source_percentages,
                        redaction_indicators, text_J, text_E, text_P, text_R,
                        metadata, mathematical_properties
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                try:
                    self.cursor.execute(insert_query, (
                        chapter_id,
                        int(row['verse']),
                        row['verse_id'],
                        row['canonical_reference'],
                        row['full_text'],
                        int(row['word_count']),
                        row['sources'].split(';') if row['sources'] else [],
                        int(row['source_count']),
                        row['primary_source'],
                        row['source_sequence'],
                        json.dumps(self._parse_percentages(row['source_percentages'])),
                        row['redaction_indicators'].split(';') if row['redaction_indicators'] and row['redaction_indicators'] != 'none' else [],
                        row['text_J'],
                        row['text_E'],
                        row['text_P'],
                        row['text_R'],
                        row['metadata'],
                        json.dumps({})  # Placeholder for mathematical properties
                    ))
                except Exception as e:
                    logger.error(f"Failed to insert verse {row['verse_id']}: {e}")
                    continue
        
        self.conn.commit()
        logger.info("Successfully loaded verses from CSV")
    
    def _ensure_books_and_chapters(self, csv_path: str):
        """Ensure books and chapters exist in database"""
