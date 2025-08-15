#!/usr/bin/env python3
"""
Mathematical Pattern Engine for KJV Bible Analysis
=================================================

This module provides mathematical pattern analysis capabilities for the KJV Bible,
similar to the approach used by KJV Code (https://kjvcode.com).

Author: KJV Sources Project
License: MIT
"""

import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
import logging

from word_level_parser import WordData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WordPattern:
    """Represents a mathematical pattern for a specific word"""
    word: str
    total_count: int
    first_occurrence: int
    last_occurrence: int
    is_sevened: bool
    is_777: bool
    is_70x7: bool
    is_77: bool
    is_343: bool  # 7x7x7
    is_490: bool  # 70x7
    is_980: bool  # 70x7 + 70x7
    position_patterns: List[int]
    occurrences: List[Dict[str, Any]]
    pattern_analysis: Dict[str, Any]

@dataclass
class GlobalAnalysis:
    """Represents global mathematical analysis of the Bible"""
    total_words: int
    is_7_power: bool
    is_823543: bool  # 7^7
    word_count_analysis: Dict[str, bool]
    book_analysis: Dict[str, Any]
    chapter_analysis: Dict[str, Any]
    verse_analysis: Dict[str, Any]

class MathematicalPatternEngine:
    """Engine for mathematical pattern analysis of KJV Bible"""
    
    def __init__(self, word_data: List[WordData]):
        self.words = word_data
        self.patterns: Dict[str, WordPattern] = {}
        self.global_analysis: Optional[GlobalAnalysis] = None
        
        # Significant numbers in biblical numerology
        self.significant_numbers = {
            7, 77, 777, 343, 490, 980, 823543,  # 7^7
            666, 153, 40, 12, 70, 1000, 144000
        }
        
        # Common biblical words for pattern analysis
        self.biblical_words = {
            'God', 'Lord', 'Jesus', 'Christ', 'Father', 'Son', 'Holy', 'Ghost',
            'Spirit', 'Heaven', 'Earth', 'Man', 'Woman', 'Child', 'Children',
            'King', 'Queen', 'Prophet', 'Priest', 'Angel', 'Devil', 'Satan',
            'Sin', 'Grace', 'Faith', 'Love', 'Hope', 'Charity', 'Truth',
            'Life', 'Death', 'Light', 'Darkness', 'Good', 'Evil', 'Right',
            'Wrong', 'Law', 'Commandment', 'Covenant', 'Promise', 'Blessing',
            'Curse', 'Prayer', 'Worship', 'Sacrifice', 'Temple', 'Altar',
            'Blood', 'Flesh', 'Bone', 'Soul', 'Heart', 'Mind', 'Eye', 'Hand',
            'Foot', 'Voice', 'Word', 'Name', 'Seed', 'Fruit', 'Tree', 'Water',
            'Fire', 'Wind', 'Stone', 'Gold', 'Silver', 'Iron', 'Wood', 'Cloth'
        }
    
    def analyze_all_patterns(self) -> Dict[str, WordPattern]:
        """Analyze mathematical patterns for all words"""
        logger.info("Starting comprehensive pattern analysis...")
        
        # Get all unique words
        word_counts = Counter(word_data.word.lower() for word_data in self.words)
        
        # Analyze patterns for each word
        for word, count in word_counts.items():
            if count >= 7:  # Only analyze words that appear 7+ times
                pattern = self.find_word_patterns(word)
                if pattern:
                    self.patterns[word] = pattern
        
        logger.info(f"Analyzed patterns for {len(self.patterns)} words")
        return self.patterns
    
    def find_word_patterns(self, target_word: str) -> Optional[WordPattern]:
        """Find mathematical patterns for a specific word"""
        occurrences = []
        
        for i, word_data in enumerate(self.words):
            if word_data.word.lower() == target_word.lower():
                occurrences.append({
                    'position': word_data.position_global,
                    'global_position': i,
                    'book': word_data.book,
                    'chapter': word_data.chapter,
                    'verse': word_data.verse,
                    'verse_id': word_data.verse_id,
                    'canonical_reference': word_data.canonical_reference,
                    'context': self._get_context(i, 5)  # 5 words before/after
                })
        
        if not occurrences:
            return None
        
        positions = [occ['position'] for occ in occurrences]
        total_count = len(occurrences)
        
        # Calculate mathematical properties
        is_sevened = total_count % 7 == 0
        is_777 = total_count == 777
        is_70x7 = total_count == 490
        is_77 = total_count == 77
        is_343 = total_count == 343
        is_490 = total_count == 490
        is_980 = total_count == 980
        
        # Analyze position patterns
        position_patterns = self._analyze_position_patterns(positions)
        
        # Create pattern analysis
        pattern_analysis = {
            'first_occurrence': min(positions),
            'last_occurrence': max(positions),
            'span': max(positions) - min(positions),
            'position_differences': [positions[i+1] - positions[i] for i in range(len(positions)-1)],
            'average_spacing': sum(positions[i+1] - positions[i] for i in range(len(positions)-1)) / (len(positions)-1) if len(positions) > 1 else 0,
            'is_significant_number': total_count in self.significant_numbers,
            'is_biblical_word': target_word.lower() in {word.lower() for word in self.biblical_words},
            'position_mod_7': [pos % 7 for pos in positions],
            'position_mod_77': [pos % 77 for pos in positions],
            'position_mod_777': [pos % 777 for pos in positions]
        }
        
        return WordPattern(
            word=target_word,
            total_count=total_count,
            first_occurrence=min(positions),
            last_occurrence=max(positions),
            is_sevened=is_sevened,
            is_777=is_777,
            is_70x7=is_70x7,
            is_77=is_77,
            is_343=is_343,
            is_490=is_490,
            is_980=is_980,
            position_patterns=position_patterns,
            occurrences=occurrences,
            pattern_analysis=pattern_analysis
        )
    
    def _get_context(self, word_index: int, context_size: int) -> Dict[str, str]:
        """Get context around a word"""
        start = max(0, word_index - context_size)
        end = min(len(self.words), word_index + context_size + 1)
        
        before_words = [self.words[i].word for i in range(start, word_index)]
        after_words = [self.words[i].word for i in range(word_index + 1, end)]
        
        return {
            'before': ' '.join(before_words),
            'after': ' '.join(after_words),
            'full_context': ' '.join([self.words[i].word for i in range(start, end)])
        }
    
    def _analyze_position_patterns(self, positions: List[int]) -> List[int]:
        """Analyze patterns in word positions"""
        patterns = []
        
        # Check for arithmetic sequences
        if len(positions) >= 3:
            diffs = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
            if len(set(diffs)) == 1:  # All differences are the same
                patterns.append(diffs[0])
        
        # Check for geometric sequences
        if len(positions) >= 3:
            ratios = [positions[i+1] / positions[i] for i in range(len(positions)-1)]
            if len(set(ratios)) == 1:  # All ratios are the same
                patterns.append(int(ratios[0]))
        
        # Check for Fibonacci-like patterns
        for i in range(len(positions) - 2):
            if positions[i] + positions[i+1] == positions[i+2]:
                patterns.append(0)  # Fibonacci pattern found
        
        return patterns
    
    def find_numerical_relationships(self) -> GlobalAnalysis:
        """Find global mathematical relationships in the Bible"""
        total_words = len(self.words)
        
        # Check if total words is a power of 7
        is_7_power = self._is_power_of_seven(total_words)
        is_823543 = total_words == 823543  # 7^7
        
        # Word count analysis
        word_count_analysis = {
            'divisible_by_7': total_words % 7 == 0,
            'divisible_by_77': total_words % 77 == 0,
            'divisible_by_777': total_words % 777 == 0,
            'divisible_by_343': total_words % 343 == 0,
            'divisible_by_490': total_words % 490 == 0,
            'is_823543': is_823543,
            'is_7_power': is_7_power
        }
        
        # Book analysis
        book_analysis = self._analyze_books()
        
        # Chapter analysis
        chapter_analysis = self._analyze_chapters()
        
        # Verse analysis
        verse_analysis = self._analyze_verses()
        
        self.global_analysis = GlobalAnalysis(
            total_words=total_words,
            is_7_power=is_7_power,
            is_823543=is_823543,
            word_count_analysis=word_count_analysis,
            book_analysis=book_analysis,
            chapter_analysis=chapter_analysis,
            verse_analysis=verse_analysis
        )
        
        return self.global_analysis
    
    def _is_power_of_seven(self, n: int) -> bool:
        """Check if number is a power of 7"""
        if n <= 0:
            return False
        while n % 7 == 0:
            n //= 7
        return n == 1
    
    def _analyze_books(self) -> Dict[str, Any]:
        """Analyze mathematical patterns by book"""
        book_counts = Counter(word_data.book for word_data in self.words)
        
        analysis = {}
        for book, count in book_counts.items():
            analysis[book] = {
                'word_count': count,
                'is_sevened': count % 7 == 0,
                'is_777': count == 777,
                'is_70x7': count == 490,
                'is_77': count == 77,
                'is_343': count == 343,
                'is_980': count == 980
            }
        
        return analysis
    
    def _analyze_chapters(self) -> Dict[str, Any]:
        """Analyze mathematical patterns by chapter"""
        chapter_counts = Counter(
            f"{word_data.book}_{word_data.chapter}" 
            for word_data in self.words
        )
        
        analysis = {}
        for chapter, count in chapter_counts.items():
            analysis[chapter] = {
                'word_count': count,
                'is_sevened': count % 7 == 0,
                'is_777': count == 777,
                'is_70x7': count == 490
            }
        
        return analysis
    
    def _analyze_verses(self) -> Dict[str, Any]:
        """Analyze mathematical patterns by verse"""
        verse_counts = Counter(
            f"{word_data.book}_{word_data.chapter}_{word_data.verse}" 
            for word_data in self.words
        )
        
        analysis = {}
        for verse, count in verse_counts.items():
            analysis[verse] = {
                'word_count': count,
                'is_sevened': count % 7 == 0,
                'is_777': count == 777,
                'is_70x7': count == 490
            }
        
        return analysis
    
    def find_sevened_words(self) -> List[WordPattern]:
        """Find all words that appear 7, 77, 777, etc. times"""
        sevened_patterns = []
        
        for word, pattern in self.patterns.items():
            if pattern.is_sevened or pattern.is_77 or pattern.is_777 or pattern.is_343:
                sevened_patterns.append(pattern)
        
        return sorted(sevened_patterns, key=lambda x: x.total_count, reverse=True)
    
    def find_significant_patterns(self) -> List[WordPattern]:
        """Find patterns that match significant biblical numbers"""
        significant_patterns = []
        
        for word, pattern in self.patterns.items():
            if pattern.total_count in self.significant_numbers:
                significant_patterns.append(pattern)
        
        return sorted(significant_patterns, key=lambda x: x.total_count, reverse=True)
    
    def search_patterns(self, 
                       category: Optional[str] = None,
                       number: Optional[int] = None,
                       person: Optional[str] = None) -> List[WordPattern]:
        """Search for patterns by category, number, or person"""
        results = []
        
        for word, pattern in self.patterns.items():
            # Filter by number
            if number and pattern.total_count != number:
                continue
            
            # Filter by person (proper names)
            if person and person.lower() not in word.lower():
                continue
            
            # Filter by category
            if category:
                if category == 'sevened' and not pattern.is_sevened:
                    continue
                elif category == '777' and not pattern.is_777:
                    continue
                elif category == '70x7' and not pattern.is_70x7:
                    continue
                elif category == 'biblical' and not pattern.pattern_analysis['is_biblical_word']:
                    continue
            
            results.append(pattern)
        
        return sorted(results, key=lambda x: x.total_count, reverse=True)
    
    def save_patterns(self, output_file: str = "mathematical_patterns.json"):
        """Save all patterns to JSON file"""
        patterns_dict = {}
        
        for word, pattern in self.patterns.items():
            patterns_dict[word] = {
                'word': pattern.word,
                'total_count': pattern.total_count,
                'first_occurrence': pattern.first_occurrence,
                'last_occurrence': pattern.last_occurrence,
                'is_sevened': pattern.is_sevened,
                'is_777': pattern.is_777,
                'is_70x7': pattern.is_70x7,
                'is_77': pattern.is_77,
                'is_343': pattern.is_343,
                'is_490': pattern.is_490,
                'is_980': pattern.is_980,
                'position_patterns': pattern.position_patterns,
                'pattern_analysis': pattern.pattern_analysis
            }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(patterns_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(patterns_dict)} patterns to {output_file}")
    
    def save_global_analysis(self, output_file: str = "global_analysis.json"):
        """Save global analysis to JSON file"""
        if not self.global_analysis:
            self.find_numerical_relationships()
        
        analysis_dict = {
            'total_words': self.global_analysis.total_words,
            'is_7_power': self.global_analysis.is_7_power,
            'is_823543': self.global_analysis.is_823543,
            'word_count_analysis': self.global_analysis.word_count_analysis,
            'book_analysis': self.global_analysis.book_analysis,
            'chapter_analysis': self.global_analysis.chapter_analysis,
            'verse_analysis': self.global_analysis.verse_analysis
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved global analysis to {output_file}")
