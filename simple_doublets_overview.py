#!/usr/bin/env python3
"""
Simple Biblical Doublets Overview
=================================

Creates text-based and HTML bird's eye view of biblical doublets distribution.
This version requires no external graphics libraries and focuses on showing
the conceptual approach for doublet visualization.

Author: KJV Sources Project
License: MIT
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict

class SimpleDoubletsOverview:
    """Creates simple text and HTML overview of biblical doublets"""
    
    def __init__(self, doublets_file: str = "doublets_data.json"):
        self.doublets_file = Path(doublets_file)
        self.doublets_data = self.load_doublets_data()
        self.torah_books = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]
        
        # Colors for HTML visualization
        self.category_colors = {
            "cosmogony": "#e74c3c",
            "genealogy": "#f39c12", 
            "catastrophe": "#8e44ad",
            "deception": "#e67e22",
            "covenant": "#2980b9",
            "family_conflict": "#27ae60",
            "prophetic_calling": "#34495e",
            "law": "#16a085",
            "wilderness_miracle": "#d35400",
            "wilderness_provision": "#c0392b"
        }
        
        self.source_colors = {
            "J": "#000088", "E": "#008888", "P": "#888800", 
            "D": "#000000", "R": "#880000"
        }
    
    def load_doublets_data(self) -> Dict[str, Any]:
        """Load doublets data from JSON file"""
        if not self.doublets_file.exists():
            raise FileNotFoundError(f"Doublets file not found: {self.doublets_file}")
        
        with open(self.doublets_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def parse_biblical_reference(self, reference: str) -> Tuple[str, int, int]:
        """Parse biblical reference into book, chapter, verse"""
        pattern = r'([A-Za-z0-9\s]+)\s+(\d+):(\d+)'
        match = re.search(pattern, reference.strip())
        
        if match:
            book = match.group(1).strip()
            chapter = int(match.group(2))
            verse = int(match.group(3))
            return book, chapter, verse
        else:
            print(f"Warning: Could not parse reference: {reference}")
            return "Unknown", 1, 1
    
    def calculate_position(self, book: str, chapter: int) -> int:
        """Calculate relative position for visualization"""
        book_positions = {
            "Genesis": 0, "Exodus": 50, "Leviticus": 90,
            "Numbers": 120, "Deuteronomy": 156
        }
        return book_positions.get(book, 0) + chapter
    
    def generate_text_overview(self):
        """Generate text-based overview of doublets"""
        print("\n" + "="*80)
        print("BIBLICAL DOUBLETS - BIRD'S EYE VIEW")
        print("="*80)
        print("Distribution of repeated passages across the Torah")
        print("="*80)
        
        # Organize doublets by book
        book_doublets = defaultdict(list)
        
        for doublet in self.doublets_data.get("doublets", []):
            for passage in doublet["passages"]:
                book, chapter, verse = self.parse_biblical_reference(passage["reference"])
                if book in self.torah_books:
                    book_doublets[book].append({
                        "name": doublet["name"],
                        "category": doublet["category"], 
                        "source": passage.get("source", "Unknown"),
                        "reference": passage["reference"],
                        "chapter": chapter
                    })
        
        # Display by book
        for book in self.torah_books:
            doublets = book_doublets[book]
            if doublets:
                print(f"\n📖 {book.upper()}")
                print("-" * 40)
                
                # Sort by chapter
                doublets.sort(key=lambda x: x["chapter"])
                
                for doublet in doublets:
                    category_name = self.doublets_data.get("categories", {}).get(
                        doublet["category"], doublet["category"]
                    )
                    print(f"  📍 {doublet['reference']:<20} | {doublet['name']:<25} | {category_name}")
                    print(f"     Source: {doublet['source']:<2} | Category: {doublet['category']}")
                    print()
        
        # Generate summary statistics
        self.generate_text_statistics()
    
    def generate_text_statistics(self):
        """Generate text-based statistics"""
        print("\n" + "="*60)
        print("DOUBLETS STATISTICS")
        print("="*60)
        
        total_doublets = len(self.doublets_data.get("doublets", []))
        total_passages = sum(len(d["passages"]) for d in self.doublets_data.get("doublets", []))
        
        print(f"📊 Total Doublets: {total_doublets}")
        print(f"📊 Total Passages: {total_passages}")
        print(f"📊 Average Passages per Doublet: {total_passages / total_doublets:.1f}")
        
        # Category distribution
        print(f"\n📈 Distribution by Category:")
        category_counts = defaultdict(int)
        for doublet in self.doublets_data.get("doublets", []):
            category_counts[doublet["category"]] += len(doublet["passages"])
        
        for category, count in sorted(category_counts.items()):
            category_name = self.doublets_data.get("categories", {}).get(category, category)
            print(f"   {category_name:<30}: {count} passages")
        
        # Source distribution
        print(f"\n📈 Distribution by Source:")
        source_counts = defaultdict(int)
        for doublet in self.doublets_data.get("doublets", []):
            for passage in doublet["passages"]:
                source = passage.get("source", "Unknown")
                source_counts[source] += 1
        
        for source, count in sorted(source_counts.items()):
            print(f"   Source {source}: {count} passages")
    
    def generate_html_overview(self, output_file: str = "doublets_overview.html"):
        """Generate HTML visualization of doublets"""
        # Create HTML content
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Biblical Doublets - Bird's Eye View</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        h1 {{
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
            font-size: 2.5em;
        }}
        
        .overview {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        
        .book-section {{
            border: 2px solid #34495e;
            border-radius: 10px;
            padding: 20px;
            background: #f8f9fa;
        }}
        
        .book-title {{
            font-size: 1.8em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 5px;
        }}
        
        .doublet-bar {{
            display: flex;
            align-items: center;
            margin: 10px 0;
            padding: 10px;
            border-radius: 8px;
            border-left: 6px solid #95a5a6;
            background: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        .doublet-info {{
            flex: 1;
        }}
        
        .doublet-name {{
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 5px;
        }}
        
        .doublet-details {{
            font-size: 0.9em;
            color: #666;
        }}
        
        .legend {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 30px;
            padding: 20px;
            background: #ecf0f1;
            border-radius: 10px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 3px;
        }}
        
        .statistics {{
            margin-top: 30px;
            padding: 20px;
            background: #e8f4f8;
            border-radius: 10px;
            border-left: 5px solid #3498db;
        }}
        
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #2980b9;
        }}
        
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        
        .visual-timeline {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            overflow-x: auto;
        }}
        
        .timeline {{
            display: flex;
            min-width: 800px;
            height: 200px;
            position: relative;
            background: white;
            border-radius: 8px;
            padding: 20px;
        }}
        
        .book-column {{
            flex: 1;
            border-right: 1px solid #ddd;
            padding: 0 10px;
            position: relative;
        }}
        
        .book-label {{
            text-align: center;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
            transform: rotate(-45deg);
            font-size: 0.8em;
        }}
        
        .doublet-marker {{
            width: 100%;
            height: 15px;
            margin: 2px 0;
            border-radius: 3px;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📖 Biblical Doublets - Bird's Eye View</h1>
        <p style="text-align: center; color: #666; font-size: 1.1em; margin-bottom: 30px;">
            Distribution of repeated passages across the Torah showing patterns in the Documentary Hypothesis
        </p>
        
        <div class="visual-timeline">
            <h3>Visual Timeline Overview</h3>
            <div class="timeline">
"""
        
        # Add timeline visualization
        book_doublets = defaultdict(list)
        for doublet in self.doublets_data.get("doublets", []):
            for passage in doublet["passages"]:
                book, chapter, verse = self.parse_biblical_reference(passage["reference"])
                if book in self.torah_books:
                    book_doublets[book].append({
                        "name": doublet["name"],
                        "category": doublet["category"], 
                        "source": passage.get("source", "Unknown")
                    })
        
        for book in self.torah_books:
            html_content += f"""
                <div class="book-column">
                    <div class="book-label">{book}</div>
"""
            doublets = book_doublets[book]
            for doublet in doublets:
                color = self.category_colors.get(doublet["category"], "#95a5a6")
                html_content += f"""
                    <div class="doublet-marker" style="background-color: {color};" 
                         title="{doublet['name']} ({doublet['category']})"></div>
"""
            html_content += "</div>"
        
        html_content += """
            </div>
        </div>
        
        <div class="overview">
"""
        
        # Add detailed book sections
        for book in self.torah_books:
            doublets = book_doublets[book]
            if doublets:
                html_content += f"""
            <div class="book-section">
                <div class="book-title">📖 {book}</div>
"""
                for doublet in doublets:
                    color = self.category_colors.get(doublet["category"], "#95a5a6")
                    category_name = self.doublets_data.get("categories", {}).get(
                        doublet["category"], doublet["category"]
                    )
                    html_content += f"""
                <div class="doublet-bar" style="border-left-color: {color};">
                    <div class="doublet-info">
                        <div class="doublet-name">{doublet['name']}</div>
                        <div class="doublet-details">
                            Category: {category_name} | Source: {doublet['source']}
                        </div>
                    </div>
                </div>
"""
                html_content += "</div>"
        
        # Add statistics
        total_doublets = len(self.doublets_data.get("doublets", []))
        total_passages = sum(len(d["passages"]) for d in self.doublets_data.get("doublets", []))
        
        html_content += f"""
        </div>
        
        <div class="statistics">
            <h3>📊 Statistics Overview</h3>
            <div class="stat-grid">
                <div class="stat-item">
                    <div class="stat-number">{total_doublets}</div>
                    <div class="stat-label">Total Doublets</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{total_passages}</div>
                    <div class="stat-label">Total Passages</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{total_passages / total_doublets:.1f}</div>
                    <div class="stat-label">Avg Passages/Doublet</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{len(self.torah_books)}</div>
                    <div class="stat-label">Books Analyzed</div>
                </div>
            </div>
        </div>
        
        <div class="legend">
            <h3 style="grid-column: 1 / -1;">🎨 Category Legend</h3>
"""
        
        # Add legend
        for category, color in self.category_colors.items():
            category_name = self.doublets_data.get("categories", {}).get(category, category)
            html_content += f"""
            <div class="legend-item">
                <div class="legend-color" style="background-color: {color};"></div>
                <span>{category_name}</span>
            </div>
"""
        
        html_content += """
        </div>
    </div>
</body>
</html>
"""
        
        # Save HTML file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML overview saved to: {output_file}")
        return output_file

def main():
    """Main function to generate simple doublets overview"""
    print("Simple Biblical Doublets Overview Generator")
    print("===========================================")
    
    try:
        # Initialize the overview generator
        overview = SimpleDoubletsOverview()
        
        # Generate text overview
        overview.generate_text_overview()
        
        # Generate HTML overview
        print("\nGenerating HTML visualization...")
        html_file = overview.generate_html_overview()
        
        print(f"\n✅ Doublets overview completed!")
        print(f"🌐 HTML visualization: {html_file}")
        print(f"\nThis provides a bird's eye view of doublet distribution")
        print(f"across the Torah, showing patterns and clusters of")
        print(f"repeated passages according to the Documentary Hypothesis.")
        
    except Exception as e:
        print(f"❌ Error generating overview: {e}")
        raise

if __name__ == "__main__":
    main()
