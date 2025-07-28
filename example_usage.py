#!/usr/bin/env python3
"""
Example Usage of KJV Sources Enhanced CLI
Demonstrates how to use the CLI functionality programmatically
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from kjv_sources.enhanced_cli import cli, console, BOOKS
    import pandas as pd
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please run the pipeline first: python kjv_pipeline.py")
    sys.exit(1)

def example_view_data():
    """Example: View data for Genesis"""
    print("\n" + "="*50)
    print("EXAMPLE: Viewing Genesis Data")
    print("="*50)
    
    # Simulate CLI view command
    book = "genesis"
    book_name = BOOKS.get(book.lower())
    
    if not book_name:
        console.print(f"[red]Error: Unknown book '{book}'[/red]")
        return
    
    csv_path = os.path.join("output", book_name, f"{book_name}.csv")
    if not os.path.exists(csv_path):
        console.print(f"[red]Error: No data found for {book_name}. Run the pipeline first.[/red]")
        return
    
    # Load data
    df = pd.read_csv(csv_path)
    
    # Show first 5 verses
    console.print(f"[bold blue]📖 {book_name} - First 5 Verses[/bold blue]")
    
    for i, row in df.head().iterrows():
        sources = row['sources'].split(';')
        source_str = " + ".join([f"[{get_source_color(s)}]{s}[/{get_source_color(s)}]" for s in sources])
        
        panel_text = (
            f"[bold]{row['canonical_reference']}[/bold]\n"
            f"[italic]{row['full_text']}[/italic]\n"
            f"Sources: {source_str} | Words: {row['word_count']}"
        )
        
        console.print(f"\n{panel_text}")

def example_statistics():
    """Example: Show statistics for all books"""
    print("\n" + "="*50)
    print("EXAMPLE: Statistics for All Books")
    print("="*50)
    
    for book_key, book_name in BOOKS.items():
        csv_path = os.path.join("output", book_name, f"{book_name}.csv")
        
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            
            total_verses = len(df)
            total_words = df['word_count'].sum()
            multi_source = len(df[df['source_count'] > 1])
            
            console.print(f"[bold]{book_name}:[/bold] {total_verses} verses, {total_words} words, {multi_source} multi-source verses")
        else:
            console.print(f"[red]{book_name}:[/red] No data found")

def example_search():
    """Example: Search for specific text"""
    print("\n" + "="*50)
    print("EXAMPLE: Searching for 'God' in Genesis")
    print("="*50)
    
    book_name = "Genesis"
    csv_path = os.path.join("output", book_name, f"{book_name}.csv")
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        
        # Search for verses containing "God"
        god_verses = df[df['full_text'].str.contains('God', case=False, na=False)]
        
        console.print(f"[bold blue]Found {len(god_verses)} verses containing 'God' in {book_name}[/bold blue]")
        
        for i, row in god_verses.head(3).iterrows():
            console.print(f"\n[bold]{row['canonical_reference']}:[/bold] {row['full_text'][:100]}...")

def example_export():
    """Example: Export data to different formats"""
    print("\n" + "="*50)
    print("EXAMPLE: Exporting Data")
    print("="*50)
    
    book_name = "Genesis"
    csv_path = os.path.join("output", book_name, f"{book_name}.csv")
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        
        # Export simple format
        simple_df = df[['canonical_reference', 'full_text', 'sources', 'primary_source', 'word_count']]
        simple_df.columns = ['Reference', 'Text', 'Sources', 'Primary Source', 'Word Count']
        simple_df.to_csv('example_genesis_simple.csv', index=False)
        
        console.print(f"[green]✅ Exported simple CSV: example_genesis_simple.csv ({len(simple_df)} verses)[/green]")
        
        # Export LLM format
        llm_df = df[['canonical_reference', 'full_text', 'sources', 'source_count', 
                    'primary_source', 'source_sequence', 'source_percentages', 
                    'redaction_indicators', 'text_J', 'text_E', 'text_P', 'text_R']]
        llm_df.columns = ['Reference', 'Text', 'Sources', 'Source Count', 'Primary Source',
                         'Source Sequence', 'Source Percentages', 'Redaction Indicators',
                         'J Text', 'E Text', 'P Text', 'R Text']
        llm_df.to_csv('example_genesis_llm.csv', index=False)
        
        console.print(f"[green]✅ Exported LLM CSV: example_genesis_llm.csv ({len(llm_df)} verses)[/green]")

def get_source_color(source):
    """Get color for source display"""
    colors = {
        "J": "blue",
        "E": "cyan", 
        "P": "yellow",
        "R": "red",
        "UNKNOWN": "grey"
    }
    return colors.get(source, "white")

def main():
    """Run all examples"""
    console.print("[bold green]🚀 KJV Sources Enhanced CLI - Example Usage[/bold green]")
    
    # Check if data exists
    if not os.path.exists("output"):
        console.print("[red]❌ No output directory found. Please run the pipeline first:[/red]")
        console.print("   python kjv_pipeline.py")
        return
    
    # Run examples
    example_view_data()
    example_statistics()
    example_search()
    example_export()
    
    console.print("\n[bold green]✅ All examples completed![/bold green]")
    console.print("\n[bold]Generated files:[/bold]")
    console.print("  - example_genesis_simple.csv")
    console.print("  - example_genesis_llm.csv")
    
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  - python kjv_cli.py view genesis")
    console.print("  - python kjv_cli.py stats genesis")
    console.print("  - python kjv_cli.py search genesis --text 'God'")

if __name__ == "__main__":
    main() 