#!/usr/bin/env python3
"""
Minimal Biblical Doublets Heat Map Test
======================================

Creates a simple visualization using only pandas and basic Python libraries.
This version tests the core functionality without external graphics dependencies.

Author: KJV Sources Project
License: MIT
"""

import json
import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict

class MinimalHeatMapTest:
    """Minimal heat map test using available libraries"""
    
    def __init__(self, doublets_file: str = "doublets_data.json"):
        self.doublets_file = Path(doublets_file)
        self.doublets_data = self.load_doublets_data()
        self.torah_books = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]
    
    def load_doublets_data(self) -> Dict[str, Any]:
        """Load doublets data from JSON file"""
        if not self.doublets_file.exists():
            raise FileNotFoundError(f"Doublets file not found: {self.doublets_file}")
        
        with open(self.doublets_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def parse_biblical_reference(self, reference: str) -> Tuple[str, int, int, int, int]:
        """Parse biblical reference into components"""
        # Handle complex references like "Genesis 6:5-8; 7:1-5,7,10,12,16b-20,22-23; 8:2b-3a,6,8-12,13b,20-22"
        # For testing, just extract the first book and chapter
        simple_pattern = r'([A-Za-z0-9\s]+)\s+(\d+):(\d+)'
        match = re.search(simple_pattern, reference.strip())
        
        if match:
            book = match.group(1).strip()
            chapter = int(match.group(2))
            verse = int(match.group(3))
            return book, chapter, verse, chapter, verse
        else:
            print(f"Warning: Could not parse reference: {reference}")
            return "Unknown", 1, 1, 1, 1
    
    def create_doublets_dataframe(self) -> pd.DataFrame:
        """Create a pandas DataFrame of doublets for analysis"""
        doublet_data = []
        
        for doublet in self.doublets_data.get("doublets", []):
            doublet_id = doublet["id"]
            category = doublet["category"]
            name = doublet["name"]
            
            for i, passage in enumerate(doublet["passages"]):
                reference = passage["reference"]
                source = passage.get("source", "Unknown")
                book = passage.get("book", "Unknown")
                
                # Parse the reference
                parsed_book, start_ch, start_v, end_ch, end_v = self.parse_biblical_reference(reference)
                
                doublet_data.append({
                    "doublet_id": doublet_id,
                    "doublet_name": name,
                    "category": category,
                    "source": source,
                    "book": parsed_book,
                    "reference": reference,
                    "chapter": start_ch,
                    "verse": start_v,
                    "passage_index": i
                })
        
        return pd.DataFrame(doublet_data)
    
    def test_data_processing(self):
        """Test the data processing functionality"""
        print("="*60)
        print("MINIMAL HEAT MAP TEST - DATA PROCESSING")
        print("="*60)
        
        # Create DataFrame
        df = self.create_doublets_dataframe()
        print(f"📊 Created DataFrame with {len(df)} rows")
        print(f"📊 Columns: {list(df.columns)}")
        
        # Display first few rows
        print(f"\n📋 First 5 rows:")
        print(df.head().to_string())
        
        # Book distribution
        print(f"\n📈 Distribution by Book:")
        book_counts = df['book'].value_counts()
        for book, count in book_counts.items():
            print(f"   {book}: {count} passages")
        
        # Category distribution
        print(f"\n📈 Distribution by Category:")
        category_counts = df['category'].value_counts()
        for category, count in category_counts.items():
            category_name = self.doublets_data.get("categories", {}).get(category, category)
            print(f"   {category}: {count} passages")
        
        # Source distribution
        print(f"\n📈 Distribution by Source:")
        source_counts = df['source'].value_counts()
        for source, count in source_counts.items():
            print(f"   {source}: {count} passages")
        
        return df
    
    def create_text_heatmap(self, df: pd.DataFrame):
        """Create a text-based heat map representation"""
        print(f"\n📊 TEXT-BASED HEAT MAP")
        print("="*60)
        
        # Create a simple text grid
        max_chapter = df['chapter'].max()
        
        for book in self.torah_books:
            book_data = df[df['book'] == book]
            if not book_data.empty:
                print(f"\n📖 {book.upper()}")
                print("-" * 50)
                
                # Create a simple visualization using characters
                chapters = sorted(book_data['chapter'].unique())
                print("Chapters with doublets: ", end="")
                
                for ch in range(1, max(chapters) + 1):
                    if ch in chapters:
                        # Count doublets in this chapter
                        count = len(book_data[book_data['chapter'] == ch])
                        if count == 1:
                            print("●", end="")  # Single doublet
                        elif count == 2:
                            print("◆", end="")  # Two doublets
                        else:
                            print("█", end="")  # Multiple doublets
                    else:
                        print("·", end="")  # No doublets
                    
                    if ch % 10 == 0:
                        print(f" ({ch})", end="")
                
                print()  # New line
                
                # Show legend for this book
                for _, row in book_data.iterrows():
                    print(f"   Ch.{row['chapter']:2d}: {row['doublet_name']} ({row['category']}, {row['source']})")
    
    def generate_csv_export(self, df: pd.DataFrame, output_file: str = "doublets_heatmap_data.csv"):
        """Export data to CSV for external analysis"""
        df.to_csv(output_file, index=False)
        print(f"\n💾 Data exported to: {output_file}")
        print("   This CSV can be imported into Excel, Tableau, or other visualization tools")
        return output_file

def main():
    """Main function to run the minimal heat map test"""
    print("Minimal Biblical Doublets Heat Map Test")
    print("======================================")
    
    try:
        # Initialize the test
        test = MinimalHeatMapTest()
        
        # Test data processing
        df = test.test_data_processing()
        
        # Create text-based heat map
        test.create_text_heatmap(df)
        
        # Export to CSV
        csv_file = test.generate_csv_export(df)
        
        print(f"\n✅ Minimal heat map test completed!")
        print(f"📊 Data processed successfully")
        print(f"📈 Text visualization created") 
        print(f"💾 CSV export: {csv_file}")
        print(f"\nNext steps:")
        print(f"1. Install matplotlib/seaborn for full graphics: pip install matplotlib seaborn")
        print(f"2. Open {csv_file} in Excel or Google Sheets for visualization")
        print(f"3. Use the doublets_overview.html for web-based visualization")
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        raise

if __name__ == "__main__":
    main()
