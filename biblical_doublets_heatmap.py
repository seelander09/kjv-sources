#!/usr/bin/env python3
"""
Biblical Doublets Heat Map Visualization
=======================================

Creates a bird's eye view heat map showing the distribution of doublets
across the entire Bible. This visualization helps identify patterns and
clusters of repeated passages in the biblical text.

Author: KJV Sources Project
License: MIT
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any
import re
from collections import defaultdict

class BiblicalDoubletsHeatMap:
    """Creates heat map visualizations of biblical doublets"""
    
    def __init__(self, doublets_file: str = "doublets_data.json"):
        self.doublets_file = Path(doublets_file)
        self.doublets_data = self.load_doublets_data()
        
        # Biblical books in canonical order
        self.biblical_books = [
            "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
            "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel", 
            "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles",
            "Ezra", "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
            "Ecclesiastes", "Song of Songs", "Isaiah", "Jeremiah",
            "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel",
            "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk",
            "Zephaniah", "Haggai", "Zechariah", "Malachi"
        ]
        
        # Focus on Torah (first 5 books) where we have data
        self.torah_books = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]
        
        # Doublet category colors
        self.category_colors = {
            "cosmogony": "#e74c3c",        # Red - Creation stories
            "genealogy": "#f39c12",        # Orange - Family lineages
            "catastrophe": "#8e44ad",      # Purple - Divine judgment
            "deception": "#e67e22",        # Dark orange - Deception stories
            "covenant": "#2980b9",         # Blue - Covenant accounts
            "family_conflict": "#27ae60",  # Green - Family tensions
            "prophetic_calling": "#34495e", # Dark gray - Divine calling
            "law": "#16a085",              # Teal - Legal traditions
            "wilderness_miracle": "#d35400", # Red orange - Wilderness miracles
            "wilderness_provision": "#c0392b" # Dark red - Wilderness provision
        }
        
        # Source colors (matching project standards)
        self.source_colors = {
            "J": "#000088",  # Navy Blue - Jahwist
            "E": "#008888",  # Teal - Elohist  
            "P": "#888800",  # Olive Yellow - Priestly
            "D": "#000000",  # Black - Deuteronomist
            "R": "#880000",  # Maroon Red - Redactor
        }
    
    def load_doublets_data(self) -> Dict[str, Any]:
        """Load doublets data from JSON file"""
        if not self.doublets_file.exists():
            raise FileNotFoundError(f"Doublets file not found: {self.doublets_file}")
        
        with open(self.doublets_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def parse_biblical_reference(self, reference: str) -> Tuple[str, int, int, int, int]:
        """
        Parse biblical reference into components
        Returns: (book, start_chapter, start_verse, end_chapter, end_verse)
        """
        # Handle references like "Genesis 1:1-2:3" or "Genesis 12:10-20"
        pattern = r'([A-Za-z0-9\s]+)\s+(\d+):(\d+)(?:-(\d+):(\d+))?'
        match = re.match(pattern, reference.strip())
        
        if not match:
            # Fallback for simpler references
            simple_pattern = r'([A-Za-z0-9\s]+)\s+(\d+):(\d+)'
            simple_match = re.match(simple_pattern, reference.strip())
            if simple_match:
                book, chapter, verse = simple_match.groups()
                return book.strip(), int(chapter), int(verse), int(chapter), int(verse)
            else:
                print(f"Warning: Could not parse reference: {reference}")
                return "Unknown", 1, 1, 1, 1
        
        book = match.group(1).strip()
        start_chapter = int(match.group(2))
        start_verse = int(match.group(3))
        
        # Handle end chapter and verse
        if match.group(4) and match.group(5):
            end_chapter = int(match.group(4))
            end_verse = int(match.group(5))
        else:
            end_chapter = start_chapter
            end_verse = start_verse
        
        return book, start_chapter, start_verse, end_chapter, end_verse
    
    def calculate_verse_position(self, book: str, chapter: int, verse: int) -> int:
        """
        Calculate relative position of verse within the Torah
        This creates a linear coordinate system across all five books
        """
        # Approximate verse counts for positioning (based on KJV)
        book_verse_counts = {
            "Genesis": 1533,
            "Exodus": 1213, 
            "Leviticus": 859,
            "Numbers": 1288,
            "Deuteronomy": 959
        }
        
        # Calculate cumulative position
        position = 0
        for torah_book in self.torah_books:
            if torah_book == book:
                # Rough estimate: 30 verses per chapter average
                position += (chapter - 1) * 30 + verse
                break
            else:
                position += book_verse_counts.get(torah_book, 1000)
        
        return position
    
    def create_doublets_matrix(self) -> pd.DataFrame:
        """Create a matrix representation of doublets for heat map"""
        # Create data structure for heat map
        doublet_positions = []
        
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
                
                # Calculate position
                start_pos = self.calculate_verse_position(parsed_book, start_ch, start_v)
                end_pos = self.calculate_verse_position(parsed_book, end_ch, end_v)
                
                # Add to positions list
                doublet_positions.append({
                    "doublet_id": doublet_id,
                    "doublet_name": name,
                    "category": category,
                    "source": source,
                    "book": parsed_book,
                    "reference": reference,
                    "start_position": start_pos,
                    "end_position": end_pos,
                    "passage_index": i,
                    "intensity": 1.0  # Can be adjusted based on various factors
                })
        
        return pd.DataFrame(doublet_positions)
    
    def create_overview_heatmap(self, output_file: str = "biblical_doublets_overview.png"):
        """Create a bird's eye view heat map of all doublets"""
        df = self.create_doublets_matrix()
        
        if df.empty:
            print("No doublet data found to visualize")
            return
        
        # Set up the figure
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(20, 12))
        
        # Create position ranges for visualization
        max_position = df['end_position'].max()
        
        # Create heat map background
        background_data = np.zeros((len(self.torah_books), int(max_position // 100) + 1))
        
        # Plot doublets as colored rectangles
        y_positions = {book: i for i, book in enumerate(self.torah_books)}
        
        for _, row in df.iterrows():
            book = row['book']
            if book not in y_positions:
                continue
                
            y_pos = y_positions[book]
            start_x = row['start_position'] / 100  # Scale down for visualization
            width = max(1, (row['end_position'] - row['start_position']) / 100)
            
            # Get color based on category
            color = self.category_colors.get(row['category'], '#95a5a6')
            
            # Add rectangle for this doublet
            rect = patches.Rectangle(
                (start_x, y_pos - 0.4), 
                width, 0.8,
                linewidth=1,
                edgecolor='black',
                facecolor=color,
                alpha=0.7,
                label=row['doublet_name'] if row['passage_index'] == 0 else ""
            )
            ax.add_patch(rect)
        
        # Customize the plot
        ax.set_xlim(0, max_position / 100)
        ax.set_ylim(-0.5, len(self.torah_books) - 0.5)
        ax.set_yticks(range(len(self.torah_books)))
        ax.set_yticklabels(self.torah_books)
        ax.set_xlabel('Position in Torah (Approximate)', fontsize=14)
        ax.set_ylabel('Biblical Books', fontsize=14)
        ax.set_title('Biblical Doublets - Bird\'s Eye View\nDistribution of Repeated Passages in the Torah', 
                    fontsize=16, fontweight='bold', pad=20)
        
        # Add grid for better readability
        ax.grid(True, alpha=0.3, axis='x')
        
        # Create legend for categories
        legend_elements = []
        for category, color in self.category_colors.items():
            category_name = self.doublets_data.get("categories", {}).get(category, category)
            legend_elements.append(patches.Patch(color=color, label=category_name))
        
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
        
        # Adjust layout and save
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Overview heat map saved to: {output_file}")
        return output_file
    
    def create_detailed_heatmap(self, output_file: str = "biblical_doublets_detailed.png"):
        """Create a detailed heat map with source information"""
        df = self.create_doublets_matrix()
        
        if df.empty:
            print("No doublet data found to visualize")
            return
        
        # Create a more detailed visualization
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 16))
        
        # Top plot: Doublets by category
        self._plot_category_heatmap(ax1, df)
        
        # Bottom plot: Doublets by source
        self._plot_source_heatmap(ax2, df)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Detailed heat map saved to: {output_file}")
        return output_file
    
    def _plot_category_heatmap(self, ax, df):
        """Plot heat map colored by doublet category"""
        y_positions = {book: i for i, book in enumerate(self.torah_books)}
        
        for _, row in df.iterrows():
            book = row['book']
            if book not in y_positions:
                continue
                
            y_pos = y_positions[book]
            start_x = row['start_position'] / 100
            width = max(1, (row['end_position'] - row['start_position']) / 100)
            color = self.category_colors.get(row['category'], '#95a5a6')
            
            rect = patches.Rectangle(
                (start_x, y_pos - 0.4), width, 0.8,
                linewidth=1, edgecolor='black', facecolor=color, alpha=0.8
            )
            ax.add_patch(rect)
        
        ax.set_xlim(0, df['end_position'].max() / 100)
        ax.set_ylim(-0.5, len(self.torah_books) - 0.5)
        ax.set_yticks(range(len(self.torah_books)))
        ax.set_yticklabels(self.torah_books)
        ax.set_title('Doublets by Category', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
    
    def _plot_source_heatmap(self, ax, df):
        """Plot heat map colored by documentary source"""
        y_positions = {book: i for i, book in enumerate(self.torah_books)}
        
        for _, row in df.iterrows():
            book = row['book']
            if book not in y_positions:
                continue
                
            y_pos = y_positions[book]
            start_x = row['start_position'] / 100
            width = max(1, (row['end_position'] - row['start_position']) / 100)
            color = self.source_colors.get(row['source'], '#95a5a6')
            
            rect = patches.Rectangle(
                (start_x, y_pos - 0.4), width, 0.8,
                linewidth=1, edgecolor='black', facecolor=color, alpha=0.8
            )
            ax.add_patch(rect)
        
        ax.set_xlim(0, df['end_position'].max() / 100)
        ax.set_ylim(-0.5, len(self.torah_books) - 0.5)
        ax.set_yticks(range(len(self.torah_books)))
        ax.set_yticklabels(self.torah_books)
        ax.set_xlabel('Position in Torah (Approximate)', fontsize=12)
        ax.set_title('Doublets by Documentary Source', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add source legend
        legend_elements = []
        for source, color in self.source_colors.items():
            legend_elements.append(patches.Patch(color=color, label=f"Source {source}"))
        ax.legend(handles=legend_elements, loc='upper right')
    
    def generate_statistics(self):
        """Generate statistics about doublets distribution"""
        df = self.create_doublets_matrix()
        
        if df.empty:
            print("No doublet data available for statistics")
            return
        
        print("\n" + "="*60)
        print("BIBLICAL DOUBLETS STATISTICS")
        print("="*60)
        
        # Overall statistics
        total_doublets = len(df['doublet_id'].unique())
        total_passages = len(df)
        
        print(f"Total Doublets: {total_doublets}")
        print(f"Total Passages: {total_passages}")
        print(f"Average Passages per Doublet: {total_passages / total_doublets:.1f}")
        
        # Distribution by book
        print(f"\nDistribution by Book:")
        book_counts = df['book'].value_counts()
        for book, count in book_counts.items():
            print(f"  {book}: {count} passages")
        
        # Distribution by category
        print(f"\nDistribution by Category:")
        category_counts = df['category'].value_counts()
        for category, count in category_counts.items():
            category_name = self.doublets_data.get("categories", {}).get(category, category)
            print(f"  {category_name}: {count} passages")
        
        # Distribution by source
        print(f"\nDistribution by Source:")
        source_counts = df['source'].value_counts()
        for source, count in source_counts.items():
            print(f"  Source {source}: {count} passages")
        
        print("="*60)

def main():
    """Main function to generate biblical doublets visualizations"""
    print("Biblical Doublets Heat Map Generator")
    print("====================================")
    
    try:
        # Initialize the heat map generator
        heatmap = BiblicalDoubletsHeatMap()
        
        # Generate statistics
        heatmap.generate_statistics()
        
        # Create overview heat map
        print("\nGenerating overview heat map...")
        overview_file = heatmap.create_overview_heatmap()
        
        # Create detailed heat map
        print("\nGenerating detailed heat map...")
        detailed_file = heatmap.create_detailed_heatmap()
        
        print(f"\n✅ Heat map visualizations completed!")
        print(f"📊 Overview: {overview_file}")
        print(f"📊 Detailed: {detailed_file}")
        print(f"\nThese visualizations provide a bird's eye view of doublet")
        print(f"distribution across the Torah, helping identify patterns")
        print(f"and clusters of repeated passages.")
        
    except Exception as e:
        print(f"❌ Error generating heat maps: {e}")
        raise

if __name__ == "__main__":
    main()
