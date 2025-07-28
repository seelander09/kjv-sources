#!/usr/bin/env python3

import os
import re
import csv
import json
import time
import sys
import shutil
from collections import Counter, defaultdict

# Color to source mapping from the wikitext files
COLOR_TO_SOURCE = {
    "#888800": "P",  # Priestly source - olive yellow
    "#000088": "J",  # Jahwist source - navy blue  
    "#008888": "E",  # Elohist source - teal blueish grey
    "#880000": "R",  # Redactor - maroon red
    "#000000": "UNKNOWN",  # Black text (unknown source)
    "#888888": "UNKNOWN",  # Grey text (unknown source)
    "#008800": "UNKNOWN",  # Green text (unknown source)
}

def parse_wikitext_file(file_path):
    """Parse a wikitext file to extract verses with their sources"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    verses = []
    current_chapter = None
    
    # Split into lines and process
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Check for chapter headers
        chapter_match = re.match(r'^==\s*Chapter\s+(\d+)\s*==$', line)
        if chapter_match:
            current_chapter = chapter_match.group(1)
            continue
        
        # Check for verse lines with multiple sources
        # Handle both formats:
        # 1. {{font|size=smaller|color=#0000FF|verse_num}} (Genesis, Deuteronomy)
        # 2. <small>{{font|color=#0000FF|verse_num}}</small> (Exodus, Leviticus, Numbers)
        verse_patterns = [
            r'{{font\|size=smaller\|color=#0000FF\|(\d+)}}(.*?)(?={{font\|size=smaller\|color=#0000FF\|\d+}}|$)',
            r'<small>{{font\|color=#0000FF\|(\d+)}}</small>(.*?)(?=<small>{{font\|color=#0000FF\|\d+}}</small>|$)'
        ]
        
        for pattern in verse_patterns:
            matches = re.findall(pattern, line, re.DOTALL)
            
            for match in matches:
                verse_num = match[0]
                verse_content = match[1].strip()
                
                if not current_chapter or not verse_num or not verse_content:
                    continue
                
                # Extract all color-coded segments from the verse
                color_segments = re.findall(r'{{font\|color=([^|]+)\|([^}]+)}}', verse_content)
                
                if not color_segments:
                    continue
                
                # Process each segment and combine into a single verse
                full_text = ""
                sources = []
                colors = []
                
                for color, text in color_segments:
                    text = text.strip()
                    if text:
                        source = COLOR_TO_SOURCE.get(color, "UNKNOWN")
                        sources.append(source)
                        colors.append(color)
                        full_text += text + " "
                
                if full_text.strip():
                    verses.append({
                        'chapter': current_chapter,
                        'verse': verse_num,
                        'source': sources,  # Now a list of sources
                        'text': full_text.strip(),
                        'color': colors,  # Now a list of colors
                        'segments': len(sources)  # Number of source segments
                    })
    
    return verses

def write_csv_output(verses, book_name, output_dir):
    """Write verses to CSV file"""
    
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, f"{book_name}.csv")
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['chapter', 'verse', 'sources', 'text', 'colors', 'segments'])
        
        for verse in verses:
            # Convert lists to strings for CSV
            sources_str = ';'.join(verse['source']) if isinstance(verse['source'], list) else verse['source']
            colors_str = ';'.join(verse['color']) if isinstance(verse['color'], list) else verse['color']
            
            writer.writerow([
                verse['chapter'],
                verse['verse'],
                sources_str,
                verse['text'],
                colors_str,
                verse.get('segments', 1)
            ])
    
    print(f"[✅] CSV written: {csv_path} ({len(verses)} verses)")
    return csv_path

def write_html_preview(verses, book_name, output_dir):
    """Write HTML preview with color-coded sources"""
    
    os.makedirs(output_dir, exist_ok=True)
    html_path = os.path.join(output_dir, f"{book_name}.html")
    
    # Source color mapping for HTML display
    source_colors = {
        "J": "#000088",  # Navy blue
        "E": "#008888",  # Teal
        "P": "#888800",  # Olive yellow
        "R": "#880000",  # Maroon red
        "UNKNOWN": "#666666",  # Grey for unknown
    }
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{book_name} Source Analysis</title>
    <style>
        body {{
            font-family: 'Georgia', serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: white;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .color-box {{
            width: 20px;
            height: 20px;
            border-radius: 3px;
            border: 1px solid #ccc;
        }}
        .chapter {{
            margin-bottom: 40px;
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .chapter-title {{
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .verse {{
            margin-bottom: 15px;
            padding: 10px;
            border-left: 4px solid #ddd;
            background: #fafafa;
        }}
        .verse-header {{
            font-weight: bold;
            margin-bottom: 5px;
            color: #555;
        }}
        .source-tag {{
            display: inline-block;
            padding: 2px 8px;
            margin-left: 10px;
            border-radius: 3px;
            color: white;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .multi-source {{
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            color: white;
        }}
        .text {{
            margin-top: 8px;
            line-height: 1.7;
        }}
        .stats {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stats h3 {{
            margin-top: 0;
            color: #333;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .stat-item {{
            text-align: center;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
        }}
        .stat-number {{
            font-size: 1.5em;
            font-weight: bold;
            color: #007bff;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{book_name} Source Analysis</h1>
        <p>Documentary Hypothesis Source Analysis - Generated from Wikitext on {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
    
    <div class="legend">
        <div class="legend-item">
            <div class="color-box" style="background-color: {source_colors.get('J', '#000088')}"></div>
            <span><strong>J</strong> - Jahwist Source</span>
        </div>
        <div class="legend-item">
            <div class="color-box" style="background-color: {source_colors.get('E', '#008888')}"></div>
            <span><strong>E</strong> - Elohist Source</span>
        </div>
        <div class="legend-item">
            <div class="color-box" style="background-color: {source_colors.get('P', '#888800')}"></div>
            <span><strong>P</strong> - Priestly Source</span>
        </div>
        <div class="legend-item">
            <div class="color-box" style="background-color: {source_colors.get('R', '#880000')}"></div>
            <span><strong>R</strong> - Redactor</span>
        </div>
        <div class="legend-item">
            <div class="color-box" style="background: linear-gradient(45deg, #ff6b6b, #4ecdc4)"></div>
            <span><strong>Multi</strong> - Multiple Sources</span>
        </div>
    </div>
"""
    
    # Add statistics
    source_counts = Counter()
    multi_source_count = 0
    for verse in verses:
        if isinstance(verse['source'], list):
            if len(verse['source']) > 1:
                multi_source_count += 1
            for source in verse['source']:
                source_counts[source] += 1
        else:
            source_counts[verse['source']] += 1
    
    html_content += f"""
    <div class="stats">
        <h3>Statistics</h3>
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-number">{len(verses)}</div>
                <div class="stat-label">Total Verses</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len(set(v['chapter'] for v in verses))}</div>
                <div class="stat-label">Chapters</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{multi_source_count}</div>
                <div class="stat-label">Multi-Source Verses</div>
            </div>
"""
    
    for source, count in source_counts.most_common():
        html_content += f"""
            <div class="stat-item">
                <div class="stat-number">{count}</div>
                <div class="stat-label">{source} Source</div>
            </div>
"""
    
    html_content += """
        </div>
    </div>
"""
    
    # Add verses by chapter
    current_chapter = None
    for verse in verses:
        if verse['chapter'] != current_chapter:
            if current_chapter is not None:
                html_content += "</div>\n"  # Close previous chapter
            html_content += f'<div class="chapter">\n'
            html_content += f'<h2 class="chapter-title">Chapter {verse["chapter"]}</h2>\n'
            current_chapter = verse['chapter']
        
        # Create source tags
        if isinstance(verse['source'], list):
            if len(verse['source']) > 1:
                # Multi-source verse
                source_tags = []
                for i, source in enumerate(verse['source']):
                    color = source_colors.get(source, "#666666")
                    source_tags.append(f'<span class="source-tag" style="background-color: {color}">{source}</span>')
                source_tag_html = ' '.join(source_tags)
                source_tag_html = f'<span class="source-tag multi-source">Multi-Source</span> {source_tag_html}'
            else:
                # Single source in list format
                color = source_colors.get(verse['source'][0], "#666666")
                source_tag_html = f'<span class="source-tag" style="background-color: {color}">{verse["source"][0]}</span>'
        else:
            # Single source (backward compatibility)
            color = source_colors.get(verse['source'], "#666666")
            source_tag_html = f'<span class="source-tag" style="background-color: {color}">{verse["source"]}</span>'
        
        html_content += f"""
        <div class="verse">
            <div class="verse-header">
                Verse {verse['verse']} {source_tag_html}
            </div>
            <div class="text">{verse['text']}</div>
        </div>
"""
    
    if current_chapter is not None:
        html_content += "</div>\n"  # Close last chapter
    
    html_content += """
</body>
</html>
"""
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"[✅] HTML preview written: {html_path}")
    print(f"[💡] Open {html_path} in your web browser to view the full analysis")

def create_latest_files(book_name, output_dir):
    """Create 'latest' symlinks/copies for easy access"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    # Create timestamped files
    csv_source = os.path.join(output_dir, f"{book_name}.csv")
    html_source = os.path.join(output_dir, f"{book_name}.html")
    
    csv_timestamped = os.path.join(output_dir, f"{book_name}_{timestamp}.csv")
    html_timestamped = os.path.join(output_dir, f"{book_name}_{timestamp}.html")
    
    # Copy files with timestamps
    if os.path.exists(csv_source):
        shutil.copy2(csv_source, csv_timestamped)
        print(f"[✅] Timestamped CSV: {csv_timestamped}")
    
    if os.path.exists(html_source):
        shutil.copy2(html_source, html_timestamped)
        print(f"[✅] Timestamped HTML: {html_timestamped}")
    
    # Create 'latest' files (overwrite existing)
    latest_csv = os.path.join(output_dir, f"{book_name}_latest.csv")
    latest_html = os.path.join(output_dir, f"{book_name}_latest.html")
    
    if os.path.exists(csv_source):
        shutil.copy2(csv_source, latest_csv)
        print(f"[✅] Latest CSV: {latest_csv}")
    
    if os.path.exists(html_source):
        shutil.copy2(html_source, latest_html)
        print(f"[✅] Latest HTML: {latest_html}")

def process_single_book(book_name):
    """Process a single book and show preview"""
    print(f"[INFO] Processing single book: {book_name}")
    
    # Define the books mapping
    books = {
        "genesis": "wiki_markdown/Genesis.wikitext",
        "exodus": "wiki_markdown/Exodus.wikitext", 
        "leviticus": "wiki_markdown/Leviticus.wikitext",
        "numbers": "wiki_markdown/Numbers.wikitext",
        "deuteronomy": "wiki_markdown/Deuteronomy.wikitext"
    }
    
    # Normalize book name
    book_key = book_name.lower()
    if book_key not in books:
        print(f"[ERROR] Unknown book: {book_name}")
        print(f"[INFO] Available books: {', '.join(books.keys())}")
        return
    
    file_path = books[book_key]
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return
    
    print(f"\n📖 Processing {book_name.title()}...")
    
    # Parse the wikitext file
    verses = parse_wikitext_file(file_path)
    
    if not verses:
        print(f"[WARN] No verses found in {book_name}")
        return
    
    print(f"[DEBUG] {book_name.title()}: found {len(verses)} verses")
    
    # Count sources and multi-source verses
    source_counts = Counter()
    multi_source_count = 0
    for verse in verses:
        if isinstance(verse['source'], list):
            if len(verse['source']) > 1:
                multi_source_count += 1
            for source in verse['source']:
                source_counts[source] += 1
        else:
            source_counts[verse['source']] += 1
    
    print(f"[DEBUG] {book_name.title()} source counts: {dict(source_counts)}")
    print(f"[DEBUG] {book_name.title()} multi-source verses: {multi_source_count}")
    
    # Show preview of first few verses
    print(f"\n[PREVIEW] First 5 verses:")
    for i, verse in enumerate(verses[:5]):
        sources_str = ';'.join(verse['source']) if isinstance(verse['source'], list) else verse['source']
        print(f"  Chapter {verse['chapter']}, Verse {verse['verse']} ({sources_str}): {verse['text'][:80]}...")
    
    # Show multi-source verses if any
    if multi_source_count > 0:
        print(f"\n[PREVIEW] Multi-source verses (first 3):")
        multi_verses = [v for v in verses if isinstance(v['source'], list) and len(v['source']) > 1]
        for i, verse in enumerate(multi_verses[:3]):
            sources_str = ';'.join(verse['source'])
            print(f"  Chapter {verse['chapter']}, Verse {verse['verse']} ({sources_str}): {verse['text'][:80]}...")
    
    # Ask if user wants to generate files
    response = input(f"\n[QUESTION] Generate CSV and HTML files for {book_name.title()}? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        # Create book-specific output directory
        book_output_dir = os.path.join("output", book_name.title())
        os.makedirs(book_output_dir, exist_ok=True)
        
        # Generate files
        csv_path = write_csv_output(verses, book_name.title(), book_output_dir)
        write_html_preview(verses, book_name.title(), book_output_dir)
        
        # Create latest files
        create_latest_files(book_name.title(), book_output_dir)
        
        print(f"\n[✅] Files generated in {book_output_dir}/ directory")
        print(f"[📁] Book folder: {book_output_dir}")
        print(f"[📄] Latest files: {book_name.title()}_latest.csv and {book_name.title()}_latest.html")
    else:
        print("[INFO] Files not generated")

def process_all_books():
    """Process all books in pipeline mode"""
    print("[INFO] Starting pipeline processing for all books...")
    
    # Define the books to process
    books = {
        "Genesis": "wiki_markdown/Genesis.wikitext",
        "Exodus": "wiki_markdown/Exodus.wikitext", 
        "Leviticus": "wiki_markdown/Leviticus.wikitext",
        "Numbers": "wiki_markdown/Numbers.wikitext",
        "Deuteronomy": "wiki_markdown/Deuteronomy.wikitext"
    }
    
    pipeline_manifest = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pipeline_version": "1.0",
        "books": {}
    }
    
    for book_name, file_path in books.items():
        if not os.path.exists(file_path):
            print(f"[WARN] File not found: {file_path}")
            continue
            
        print(f"\n📖 Processing {book_name}...")
        
        # Parse the wikitext file
        verses = parse_wikitext_file(file_path)
        
        if not verses:
            print(f"[WARN] No verses found in {book_name}")
            continue
        
        print(f"[DEBUG] {book_name}: found {len(verses)} verses")
        
        # Count sources and multi-source verses
        source_counts = Counter()
        multi_source_count = 0
        for verse in verses:
            if isinstance(verse['source'], list):
                if len(verse['source']) > 1:
                    multi_source_count += 1
                for source in verse['source']:
                    source_counts[source] += 1
            else:
                source_counts[verse['source']] += 1
        
        print(f"[DEBUG] {book_name} source counts: {dict(source_counts)}")
        print(f"[DEBUG] {book_name} multi-source verses: {multi_source_count}")
        
        # Create book-specific output directory
        book_output_dir = os.path.join("output", book_name)
        os.makedirs(book_output_dir, exist_ok=True)
        
        # Write CSV output
        csv_path = write_csv_output(verses, book_name, book_output_dir)
        
        # Write HTML preview
        write_html_preview(verses, book_name, book_output_dir)
        
        # Create latest files
        create_latest_files(book_name, book_output_dir)
        
        # Update pipeline manifest
        pipeline_manifest["books"][book_name] = {
            "verses": len(verses),
            "chapters": len(set(v['chapter'] for v in verses)),
            "sources": dict(source_counts),
            "multi_source_verses": multi_source_count,
            "output_dir": book_output_dir,
            "files": {
                "csv": f"{book_name}.csv",
                "html": f"{book_name}.html",
                "latest_csv": f"{book_name}_latest.csv",
                "latest_html": f"{book_name}_latest.html"
            }
        }
    
    # Write pipeline manifest
    pipeline_manifest_path = os.path.join("output", "pipeline_manifest.json")
    with open(pipeline_manifest_path, "w", encoding="utf-8") as f:
        json.dump(pipeline_manifest, f, indent=2)
    print(f"\n[✅] Pipeline manifest written: {pipeline_manifest_path}")
    
    # Create overall latest manifest
    latest_manifest_path = os.path.join("output", "latest_manifest.json")
    with open(latest_manifest_path, "w", encoding="utf-8") as f:
        json.dump(pipeline_manifest, f, indent=2)
    print(f"[✅] Latest manifest written: {latest_manifest_path}")

def main():
    print("[INFO] Starting wikitext parser...")
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == "pipeline":
            process_all_books()
            return
        else:
            book_name = sys.argv[1]
            process_single_book(book_name)
            return
    
    print("[INFO] Usage:")
    print("  python parse_wikitext.py <book_name>  - Process single book")
    print("  python parse_wikitext.py pipeline     - Process all books")
    print("  Available books: genesis, exodus, leviticus, numbers, deuteronomy")

if __name__ == "__main__":
    main()