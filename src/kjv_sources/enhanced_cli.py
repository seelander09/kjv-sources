#!/usr/bin/env python3
"""
Enhanced CLI for KJV Sources Data Pipeline
Provides rich terminal interface for viewing and analyzing KJV sources data
"""

import os
import csv
import json
import glob
import click
import sys
import pandas as pd
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.layout import Layout
from rich.live import Live
from rich.prompt import Prompt
from rich.align import Align
from datetime import datetime

# Add the parent directory to sys.path to import parse_wikitext
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import Qdrant client
try:
    from .qdrant_client import create_qdrant_client, KJVQdrantClient
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

DEFAULT_OUTPUT_DIR = os.path.join(os.getcwd(), "output")

# Source color mapping for terminal display
SOURCE_COLORS = {
    "J": "blue",      # Jahwist source - navy blue
    "E": "cyan",      # Elohist source - teal
    "P": "yellow",    # Priestly source - olive yellow
    "R": "red",       # Redactor - maroon red
    "UNKNOWN": "grey" # Unknown source - grey
}

# Book mapping for CLI
BOOKS = {
    "genesis": "Genesis",
    "exodus": "Exodus", 
    "leviticus": "Leviticus",
    "numbers": "Numbers",
    "deuteronomy": "Deuteronomy"
}

console = Console()

@click.group()
def cli():
    """Enhanced KJV Sources CLI - View and analyze biblical source data."""
    pass

@cli.command()
@click.argument("book")
@click.option("--limit", default=10, help="Number of verses to show")
@click.option("--chapter", type=int, help="Filter by chapter number")
@click.option("--source", help="Filter by specific source (J, E, P, R)")
@click.option("--show-multi", is_flag=True, help="Show multi-source verses only")
@click.option("--format", type=click.Choice(["table", "json", "compact"]), default="table")
def view(book, limit, chapter, source, show_multi, format):
    """View KJV sources data for a specific book with rich formatting."""
    
    book_name = BOOKS.get(book.lower())
    if not book_name:
        console.print(f"[red]Error: Unknown book '{book}'. Available: {list(BOOKS.keys())}[/red]")
        return
    
    csv_path = os.path.join(DEFAULT_OUTPUT_DIR, book_name, f"{book_name}.csv")
    if not os.path.exists(csv_path):
        console.print(f"[red]Error: No data found for {book_name}. Run the parser first.[/red]")
        return
    
    # Load and filter data
    df = pd.read_csv(csv_path)
    
    if chapter:
        df = df[df['chapter'] == chapter]
    
    if source:
        df = df[df['sources'].str.contains(source, na=False)]
    
    if show_multi:
        df = df[df['source_count'] > 1]
    
    df = df.head(limit)
    
    if df.empty:
        console.print(f"[yellow]No verses found matching criteria for {book_name}[/yellow]")
        return
    
    if format == "json":
        console.print_json(data=df.to_dict('records'))
        return
    
    if format == "compact":
        show_compact_view(df, book_name)
        return
    
    show_rich_table(df, book_name)

def show_rich_table(df, book_name):
    """Display data in a rich table format."""
    
    table = Table(title=f"📖 {book_name} - KJV Sources Analysis")
    table.add_column("Reference", style="bold")
    table.add_column("Text", style="italic", width=60)
    table.add_column("Sources", style="bold")
    table.add_column("Primary", style="bold")
    table.add_column("Word Count", justify="right")
    table.add_column("Complexity", justify="right")
    
    for _, row in df.iterrows():
        # Color-code the sources
        sources_text = Text()
        for s in row['sources'].split(';'):
            color = SOURCE_COLORS.get(s, "white")
            sources_text.append(f"{s} ", style=color)
        
        # Determine complexity
        complexity = "🔴" if row['source_count'] > 2 else "🟡" if row['source_count'] > 1 else "🟢"
        
        table.add_row(
            row['canonical_reference'],
            row['full_text'][:80] + "..." if len(row['full_text']) > 80 else row['full_text'],
            sources_text,
            row['primary_source'],
            str(row['word_count']),
            complexity
        )
    
    console.print(table)

def show_compact_view(df, book_name):
    """Display data in a compact format."""
    
    for _, row in df.iterrows():
        # Create colored source indicator
        sources = row['sources'].split(';')
        source_indicators = []
        for s in sources:
            color = SOURCE_COLORS.get(s, "white")
            source_indicators.append(f"[{color}]{s}[/{color}]")
        
        source_str = " + ".join(source_indicators)
        
        panel = Panel(
            f"[bold]{row['canonical_reference']}[/bold]\n"
            f"[italic]{row['full_text']}[/italic]\n"
            f"Sources: {source_str} | Words: {row['word_count']} | "
            f"Primary: [{SOURCE_COLORS.get(row['primary_source'], 'white')}]{row['primary_source']}[/{SOURCE_COLORS.get(row['primary_source'], 'white')}]",
            title=f"Verse {row['verse']}",
            border_style="blue"
        )
        console.print(panel)

@cli.command()
@click.argument("book")
@click.option("--output", default=None, help="Output CSV file path")
@click.option("--format", type=click.Choice(["full", "simple", "llm"]), default="full")
def export_csv(book, output, format):
    """Export KJV sources data to CSV format."""
    
    book_name = BOOKS.get(book.lower())
    if not book_name:
        console.print(f"[red]Error: Unknown book '{book}'. Available: {list(BOOKS.keys())}[/red]")
        return
    
    csv_path = os.path.join(DEFAULT_OUTPUT_DIR, book_name, f"{book_name}.csv")
    if not os.path.exists(csv_path):
        console.print(f"[red]Error: No data found for {book_name}. Run the parser first.[/red]")
        return
    
    df = pd.read_csv(csv_path)
    
    if format == "simple":
        # Simple format with basic columns
        simple_df = df[['canonical_reference', 'full_text', 'sources', 'primary_source', 'word_count']]
        output_cols = ['Reference', 'Text', 'Sources', 'Primary Source', 'Word Count']
        simple_df.columns = output_cols
    
    elif format == "llm":
        # LLM-optimized format
        llm_df = df[['canonical_reference', 'full_text', 'sources', 'source_count', 
                    'primary_source', 'source_sequence', 'source_percentages', 
                    'redaction_indicators', 'text_J', 'text_E', 'text_P', 'text_R']]
        output_cols = ['Reference', 'Text', 'Sources', 'Source Count', 'Primary Source',
                      'Source Sequence', 'Source Percentages', 'Redaction Indicators',
                      'J Text', 'E Text', 'P Text', 'R Text']
        llm_df.columns = output_cols
    
    else:
        # Full format (default)
        output_cols = df.columns
    
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"{book_name}_{format}_{timestamp}.csv"
    
    df.to_csv(output, index=False)
    console.print(f"[green]✅ Exported {len(df)} verses to {output}[/green]")
    console.print(f"[blue]📊 Format: {format} | Columns: {len(output_cols)}[/blue]")

@cli.command()
@click.argument("book")
@click.option("--limit", default=5, help="Number of examples to show")
@click.option("--format", type=click.Choice(["training", "classification", "sequence", "analysis"]), default="training")
def preview_training(book, limit, format):
    """Preview LLM training datasets."""
    
    book_name = BOOKS.get(book.lower())
    if not book_name:
        console.print(f"[red]Error: Unknown book '{book}'. Available: {list(BOOKS.keys())}[/red]")
        return
    
    jsonl_path = os.path.join(DEFAULT_OUTPUT_DIR, book_name, f"{book_name}_{format}.jsonl")
    if not os.path.exists(jsonl_path):
        console.print(f"[red]Error: No {format} data found for {book_name}. Run the parser first.[/red]")
        return
    
    console.print(f"[bold blue]📚 {book_name} - {format.title()} Training Data Preview[/bold blue]")
    console.print(f"[dim]Showing {limit} examples from {jsonl_path}[/dim]\n")
    
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= limit:
                break
            
            data = json.loads(line.strip())
            
            if format == "training":
                panel = Panel(
                    f"[bold]Instruction:[/bold] {data['instruction']}\n\n"
                    f"[bold]Input:[/bold] {data['input']}\n\n"
                    f"[bold]Output:[/bold] {data['output']}",
                    title=f"Example {i+1}",
                    border_style="green"
                )
            
            elif format == "classification":
                panel = Panel(
                    f"[bold]Text:[/bold] {data['text']}\n\n"
                    f"[bold]Label:[/bold] {data['label']} ({data['source']})",
                    title=f"Example {i+1}",
                    border_style="blue"
                )
            
            elif format == "sequence":
                panel = Panel(
                    f"[bold]Text:[/bold] {data['text']}\n\n"
                    f"[bold]Labels:[/bold] {' -> '.join(data['labels'])}",
                    title=f"Example {i+1}",
                    border_style="yellow"
                )
            
            else:  # analysis
                panel = Panel(
                    f"[bold]Task:[/bold] {data['task']}\n\n"
                    f"[bold]Prompt:[/bold] {data['prompt']}\n\n"
                    f"[bold]Answer:[/bold] {data['answer']}",
                    title=f"Example {i+1}",
                    border_style="red"
                )
            
            console.print(panel)

@cli.command()
@click.argument("book")
def stats(book):
    """Show comprehensive statistics for a book."""
    
    book_name = BOOKS.get(book.lower())
    if not book_name:
        console.print(f"[red]Error: Unknown book '{book}'. Available: {list(BOOKS.keys())}[/red]")
        return
    
    csv_path = os.path.join(DEFAULT_OUTPUT_DIR, book_name, f"{book_name}.csv")
    if not os.path.exists(csv_path):
        console.print(f"[red]Error: No data found for {book_name}. Run the parser first.[/red]")
        return
    
    df = pd.read_csv(csv_path)
    
    # Calculate statistics
    total_verses = len(df)
    total_chapters = df['chapter'].nunique()
    total_words = df['word_count'].sum()
    
    # Source analysis
    source_counts = {}
    for sources in df['sources']:
        for source in sources.split(';'):
            source_counts[source] = source_counts.get(source, 0) + 1
    
    multi_source_verses = len(df[df['source_count'] > 1])
    single_source_verses = len(df[df['source_count'] == 1])
    
    # Create statistics table
    stats_table = Table(title=f"📊 {book_name} - Comprehensive Statistics")
    stats_table.add_column("Metric", style="bold")
    stats_table.add_column("Value", style="green")
    stats_table.add_column("Percentage", style="blue")
    
    stats_table.add_row("Total Verses", str(total_verses), "100%")
    stats_table.add_row("Total Chapters", str(total_chapters), f"{total_chapters/total_verses*100:.1f}%")
    stats_table.add_row("Total Words", str(total_words), f"{total_words/total_verses:.1f} avg/verse")
    stats_table.add_row("Single Source Verses", str(single_source_verses), f"{single_source_verses/total_verses*100:.1f}%")
    stats_table.add_row("Multi Source Verses", str(multi_source_verses), f"{multi_source_verses/total_verses*100:.1f}%")
    
    console.print(stats_table)
    
    # Source distribution
    source_table = Table(title="🎨 Source Distribution")
    source_table.add_column("Source", style="bold")
    source_table.add_column("Count", style="green")
    source_table.add_column("Percentage", style="blue")
    
    for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = count / total_verses * 100
        source_table.add_row(
            f"[{SOURCE_COLORS.get(source, 'white')}]{source}[/{SOURCE_COLORS.get(source, 'white')}]",
            str(count),
            f"{percentage:.1f}%"
        )
    
    console.print(source_table)

@cli.command()
@click.option("--books", multiple=True, help="Specific books to process")
@click.option("--output", default="combined_kjv_sources.csv", help="Output file name")
def combine(books, output):
    """Combine multiple books into a single CSV file."""
    
    if not books:
        books = list(BOOKS.keys())
    
    all_data = []
    
    with Progress() as progress:
        task = progress.add_task("Combining books...", total=len(books))
        
        for book in books:
            book_name = BOOKS.get(book.lower())
            if not book_name:
                console.print(f"[yellow]Warning: Unknown book '{book}', skipping...[/yellow]")
                continue
            
            csv_path = os.path.join(DEFAULT_OUTPUT_DIR, book_name, f"{book_name}.csv")
            if not os.path.exists(csv_path):
                console.print(f"[yellow]Warning: No data found for {book_name}, skipping...[/yellow]")
                continue
            
            df = pd.read_csv(csv_path)
            all_data.append(df)
            progress.update(task, advance=1)
    
    if not all_data:
        console.print("[red]Error: No valid data found to combine.[/red]")
        return
    
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df.to_csv(output, index=False)
    
    console.print(f"[green]✅ Combined {len(combined_df)} verses from {len(all_data)} books into {output}[/green]")
    console.print(f"[blue]📊 Books: {', '.join([BOOKS[b.lower()] for b in books if b.lower() in BOOKS])}[/blue]")

@cli.command()
def list_books():
    """List all available books and their status."""
    
    table = Table(title="📚 Available Books Status")
    table.add_column("Book", style="bold")
    table.add_column("Status", style="bold")
    table.add_column("Verses", justify="right")
    table.add_column("Last Updated", style="dim")
    
    for book_key, book_name in BOOKS.items():
        csv_path = os.path.join(DEFAULT_OUTPUT_DIR, book_name, f"{book_name}.csv")
        
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            verse_count = len(df)
            mtime = os.path.getmtime(csv_path)
            last_updated = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            
            table.add_row(
                book_name,
                "[green]✅ Available[/green]",
                str(verse_count),
                last_updated
            )
        else:
            table.add_row(
                book_name,
                "[red]❌ Not Found[/red]",
                "0",
                "Never"
            )
    
    console.print(table)

@cli.command()
@click.argument("book")
@click.option("--chapter", type=int, help="Specific chapter to search")
@click.option("--verse", type=int, help="Specific verse to search")
@click.option("--text", help="Search for text in verses")
def search(book, chapter, verse, text):
    """Search for specific verses or text in a book."""
    
    book_name = BOOKS.get(book.lower())
    if not book_name:
        console.print(f"[red]Error: Unknown book '{book}'. Available: {list(BOOKS.keys())}[/red]")
        return
    
    csv_path = os.path.join(DEFAULT_OUTPUT_DIR, book_name, f"{book_name}.csv")
    if not os.path.exists(csv_path):
        console.print(f"[red]Error: No data found for {book_name}. Run the parser first.[/red]")
        return
    
    df = pd.read_csv(csv_path)
    
    # Apply filters
    if chapter:
        df = df[df['chapter'] == chapter]
    
    if verse:
        df = df[df['verse'] == verse]
    
    if text:
        df = df[df['full_text'].str.contains(text, case=False, na=False)]
    
    if df.empty:
        console.print(f"[yellow]No verses found matching criteria for {book_name}[/yellow]")
        return
    
    console.print(f"[bold blue]🔍 Search Results for {book_name}[/bold blue]")
    console.print(f"[dim]Found {len(df)} verses[/dim]\n")
    
    show_rich_table(df, book_name)

# Qdrant Vector Database Commands

@cli.group()
def qdrant():
    """Qdrant vector database operations for KJV sources data."""
    if not QDRANT_AVAILABLE:
        console.print("[red]❌ Qdrant functionality not available. Install qdrant-client and sentence-transformers.[/red]")
        return

@qdrant.command()
@click.option("--force", is_flag=True, help="Force recreate collection if it exists")
def setup(force):
    """Set up Qdrant collection for KJV sources data."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        success = client.create_collection(force_recreate=force)
        
        if success:
            # Show collection stats
            stats = client.get_collection_stats()
            if stats:
                table = Table(title="📊 Qdrant Collection Statistics")
                table.add_column("Property", style="bold")
                table.add_column("Value", style="green")
                
                for key, value in stats.items():
                    table.add_row(key.replace("_", " ").title(), str(value))
                
                console.print(table)
        else:
            console.print("[red]❌ Failed to set up Qdrant collection[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Error setting up Qdrant: {e}[/red]")

@qdrant.command()
@click.argument("book")
def upload(book):
    """Upload a book's data to Qdrant vector database."""
    if not QDRANT_AVAILABLE:
        return
    
    book_name = BOOKS.get(book.lower())
    if not book_name:
        console.print(f"[red]Error: Unknown book '{book}'. Available: {list(BOOKS.keys())}[/red]")
        return
    
    csv_path = os.path.join(DEFAULT_OUTPUT_DIR, book_name, f"{book_name}.csv")
    if not os.path.exists(csv_path):
        console.print(f"[red]Error: No data found for {book_name}. Run the parser first.[/red]")
        return
    
    try:
        client = create_qdrant_client()
        success = client.upload_book_data(book_name, csv_path)
        
        if success:
            console.print(f"[green]✅ Successfully uploaded {book_name} to Qdrant[/green]")
        else:
            console.print(f"[red]❌ Failed to upload {book_name} to Qdrant[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Error uploading to Qdrant: {e}[/red]")

@qdrant.command()
@click.option("--books", multiple=True, help="Specific books to upload")
def upload_all(books):
    """Upload all books or specific books to Qdrant."""
    if not QDRANT_AVAILABLE:
        return
    
    if not books:
        books = list(BOOKS.keys())
    
    try:
        client = create_qdrant_client()
        
        for book in books:
            book_name = BOOKS.get(book.lower())
            if not book_name:
                console.print(f"[yellow]Warning: Unknown book '{book}', skipping...[/yellow]")
                continue
            
            csv_path = os.path.join(DEFAULT_OUTPUT_DIR, book_name, f"{book_name}.csv")
            if not os.path.exists(csv_path):
                console.print(f"[yellow]Warning: No data found for {book_name}, skipping...[/yellow]")
                continue
            
            console.print(f"[blue]📤 Uploading {book_name}...[/blue]")
            success = client.upload_book_data(book_name, csv_path)
            
            if success:
                console.print(f"[green]✅ {book_name} uploaded successfully[/green]")
            else:
                console.print(f"[red]❌ Failed to upload {book_name}[/red]")
        
        # Show final stats
        stats = client.get_collection_stats()
        if stats:
            console.print(f"\n[bold green]📊 Final Collection Stats:[/bold green]")
            console.print(f"Total verses: {stats.get('total_points', 0)}")
            console.print(f"Vector size: {stats.get('vector_size', 0)}")
            console.print(f"Status: {stats.get('status', 'Unknown')}")
            
    except Exception as e:
        console.print(f"[red]❌ Error uploading to Qdrant: {e}[/red]")

@qdrant.command()
@click.argument("query")
@click.option("--limit", default=10, help="Number of results to return")
@click.option("--book", help="Filter by specific book")
def search_semantic(query, limit, book):
    """Search verses using semantic similarity in Qdrant."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        results = client.search_verses(query, limit=limit, book_filter=book)
        
        if not results:
            console.print("[yellow]No results found for your query.[/yellow]")
            return
        
        console.print(f"[bold blue]🔍 Semantic Search Results for: '{query}'[/bold blue]")
        console.print(f"[dim]Found {len(results)} results[/dim]\n")
        
        table = Table(title="Search Results")
        table.add_column("Score", style="bold", justify="right")
        table.add_column("Reference", style="bold")
        table.add_column("Text", style="italic", width=60)
        table.add_column("Sources", style="bold")
        table.add_column("Book", style="dim")
        
        for result in results:
            # Color-code the sources
            sources_text = Text()
            for s in result['sources'].split(';'):
                color = SOURCE_COLORS.get(s, "white")
                sources_text.append(f"{s} ", style=color)
            
            table.add_row(
                f"{result['score']:.3f}",
                result['reference'],
                result['text'][:80] + "..." if len(result['text']) > 80 else result['text'],
                sources_text,
                result['book']
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]❌ Error searching Qdrant: {e}[/red]")

@qdrant.command()
@click.argument("source")
@click.option("--limit", default=20, help="Number of results to return")
def search_by_source(source, limit):
    """Search verses by specific source (J, E, P, R) in Qdrant."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        results = client.search_by_source(source, limit=limit)
        
        if not results:
            console.print(f"[yellow]No verses found with source '{source}'.[/yellow]")
            return
        
        console.print(f"[bold blue]🔍 Verses with Source '{source}'[/bold blue]")
        console.print(f"[dim]Found {len(results)} results[/dim]\n")
        
        table = Table(title=f"Source {source} Results")
        table.add_column("Reference", style="bold")
        table.add_column("Text", style="italic", width=60)
        table.add_column("Sources", style="bold")
        table.add_column("Book", style="dim")
        
        for result in results:
            # Color-code the sources
            sources_text = Text()
            for s in result['sources'].split(';'):
                color = SOURCE_COLORS.get(s, "white")
                sources_text.append(f"{s} ", style=color)
            
            table.add_row(
                result['reference'],
                result['text'][:80] + "..." if len(result['text']) > 80 else result['text'],
                sources_text,
                result['book']
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]❌ Error searching by source: {e}[/red]")

@qdrant.command()
def stats():
    """Show Qdrant collection statistics."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        stats = client.get_collection_stats()
        
        if stats:
            table = Table(title="📊 Qdrant Collection Statistics")
            table.add_column("Property", style="bold")
            table.add_column("Value", style="green")
            
            for key, value in stats.items():
                table.add_row(key.replace("_", " ").title(), str(value))
            
            console.print(table)
        else:
            console.print("[red]❌ Could not retrieve collection statistics[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Error getting Qdrant stats: {e}[/red]")

@qdrant.command()
@click.option("--force", is_flag=True, help="Confirm deletion")
def delete(force):
    """Delete the Qdrant collection."""
    if not QDRANT_AVAILABLE:
        return
    
    if not force:
        console.print("[yellow]⚠️ Use --force to confirm deletion[/yellow]")
        return
    
    try:
        client = create_qdrant_client()
        success = client.delete_collection()
        
        if success:
            console.print("[green]✅ Collection deleted successfully[/green]")
        else:
            console.print("[red]❌ Failed to delete collection[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Error deleting collection: {e}[/red]")

# Enhanced Qdrant Commands

@qdrant.command()
@click.option("--limit", default=20, help="Number of results to return")
@click.option("--min-sources", default=2, help="Minimum number of sources")
def search_multi_source(limit, min_sources):
    """Search for verses with multiple sources (complex redaction)."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        results = client.search_multi_source_verses(limit=limit, min_sources=min_sources)
        
        if results:
            table = Table(title=f"🔗 Multi-Source Verses (≥{min_sources} sources)")
            table.add_column("Reference", style="bold")
            table.add_column("Text", style="italic", width=60)
            table.add_column("Sources", style="bold")
            table.add_column("Source Count", justify="right")
            table.add_column("Redaction", style="dim")
            
            for result in results:
                # Color-code the sources
                sources_text = Text()
                for s in result["sources"].split(";"):
                    color = SOURCE_COLORS.get(s, "white")
                    sources_text.append(f"{s} ", style=color)
                
                table.add_row(
                    result["reference"],
                    result["text"][:80] + "..." if len(result["text"]) > 80 else result["text"],
                    sources_text,
                    str(result["source_count"]),
                    result["redaction_indicators"]
                )
            
            console.print(table)
        else:
            console.print("[yellow]No multi-source verses found[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error searching multi-source verses: {e}[/red]")

@qdrant.command()
@click.argument("pattern_type", type=click.Choice(["complex", "simple", "interwoven", "harmonized"]))
@click.option("--limit", default=20, help="Number of results to return")
def search_redaction_patterns(pattern_type, limit):
    """Search for verses with specific redaction patterns."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        results = client.search_redaction_patterns(pattern_type=pattern_type, limit=limit)
        
        if results:
            table = Table(title=f"🔍 Redaction Pattern: {pattern_type.title()}")
            table.add_column("Reference", style="bold")
            table.add_column("Text", style="italic", width=60)
            table.add_column("Sources", style="bold")
            table.add_column("Pattern", style="dim")
            
            for result in results:
                # Color-code the sources
                sources_text = Text()
                for s in result["sources"].split(";"):
                    color = SOURCE_COLORS.get(s, "white")
                    sources_text.append(f"{s} ", style=color)
                
                table.add_row(
                    result["reference"],
                    result["text"][:80] + "..." if len(result["text"]) > 80 else result["text"],
                    sources_text,
                    result["redaction_indicators"]
                )
            
            console.print(table)
        else:
            console.print(f"[yellow]No verses found with {pattern_type} redaction pattern[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error searching redaction patterns: {e}[/red]")

@qdrant.command()
@click.argument("sources", nargs=-1, required=True)
@click.option("--combination-type", type=click.Choice(["all", "any"]), default="all", help="How to combine sources")
@click.option("--limit", default=20, help="Number of results to return")
def search_source_combinations(sources, combination_type, limit):
    """Search for verses with specific source combinations."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        results = client.search_source_combinations(
            sources=list(sources), 
            combination_type=combination_type, 
            limit=limit
        )
        
        if results:
            table = Table(title=f"🔗 Source Combination: {' + '.join(sources)} ({combination_type})")
            table.add_column("Reference", style="bold")
            table.add_column("Text", style="italic", width=60)
            table.add_column("Sources", style="bold")
            table.add_column("Primary", style="dim")
            
            for result in results:
                # Color-code the sources
                sources_text = Text()
                for s in result["sources"].split(";"):
                    color = SOURCE_COLORS.get(s, "white")
                    sources_text.append(f"{s} ", style=color)
                
                table.add_row(
                    result["reference"],
                    result["text"][:80] + "..." if len(result["text"]) > 80 else result["text"],
                    sources_text,
                    result["primary_source"]
                )
            
            console.print(table)
        else:
            console.print(f"[yellow]No verses found with {combination_type} combination of {', '.join(sources)}[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error searching source combinations: {e}[/red]")

@qdrant.command()
@click.argument("book")
@click.argument("chapter", type=int)
@click.option("--limit", default=50, help="Number of results to return")
def search_by_chapter(book, chapter, limit):
    """Search for verses in a specific chapter."""
    if not QDRANT_AVAILABLE:
        return
    
    book_name = BOOKS.get(book.lower())
    if not book_name:
        console.print(f"[red]Error: Unknown book '{book}'. Available: {list(BOOKS.keys())}[/red]")
        return
    
    try:
        client = create_qdrant_client()
        results = client.search_by_chapter(book=book_name, chapter=chapter, limit=limit)
        
        if results:
            table = Table(title=f"📖 {book_name} Chapter {chapter}")
            table.add_column("Verse", style="bold")
            table.add_column("Text", style="italic", width=60)
            table.add_column("Sources", style="bold")
            table.add_column("Primary", style="dim")
            
            for result in results:
                # Color-code the sources
                sources_text = Text()
                for s in result["sources"].split(";"):
                    color = SOURCE_COLORS.get(s, "white")
                    sources_text.append(f"{s} ", style=color)
                
                table.add_row(
                    result["reference"],
                    result["text"][:80] + "..." if len(result["text"]) > 80 else result["text"],
                    sources_text,
                    result["primary_source"]
                )
            
            console.print(table)
        else:
            console.print(f"[yellow]No verses found in {book_name} Chapter {chapter}[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error searching by chapter: {e}[/red]")

@qdrant.command()
@click.argument("analysis_type", type=click.Choice(["j_dominant", "p_ritual", "redaction_heavy", "narrative_flow"]))
@click.option("--limit", default=20, help="Number of results to return")
def search_source_analysis(analysis_type, limit):
    """Search for verses based on source analysis patterns."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        results = client.search_source_analysis(analysis_type=analysis_type, limit=limit)
        
        if results:
            analysis_names = {
                "j_dominant": "J-Dominant Verses",
                "p_ritual": "P-Ritual Content",
                "redaction_heavy": "Complex Redaction",
                "narrative_flow": "Narrative Sources (J/E)"
            }
            
            table = Table(title=f"🔍 {analysis_names.get(analysis_type, analysis_type)}")
            table.add_column("Reference", style="bold")
            table.add_column("Text", style="italic", width=60)
            table.add_column("Sources", style="bold")
            table.add_column("Primary", style="dim")
            
            for result in results:
                # Color-code the sources
                sources_text = Text()
                for s in result["sources"].split(";"):
                    color = SOURCE_COLORS.get(s, "white")
                    sources_text.append(f"{s} ", style=color)
                
                table.add_row(
                    result["reference"],
                    result["text"][:80] + "..." if len(result["text"]) > 80 else result["text"],
                    sources_text,
                    result["primary_source"]
                )
            
            console.print(table)
        else:
            console.print(f"[yellow]No verses found for {analysis_type} analysis[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error in source analysis search: {e}[/red]")

@qdrant.command()
@click.argument("query")
@click.option("--limit", default=20, help="Number of results to return")
@click.option("--book", help="Filter by specific book")
@click.option("--source", help="Filter by specific source")
@click.option("--min-sources", type=int, help="Minimum number of sources")
@click.option("--chapter", type=int, help="Filter by specific chapter")
def search_hybrid(query, limit, book, source, min_sources, chapter):
    """Hybrid search combining semantic similarity with structured filtering."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        
        # Build filters
        filters = {}
        if book:
            book_name = BOOKS.get(book.lower())
            if book_name:
                filters["book"] = book_name
        if source:
            filters["source"] = source
        if min_sources:
            filters["min_sources"] = min_sources
        if chapter:
            filters["chapter"] = chapter
        
        results = client.search_hybrid(query=query, filters=filters, limit=limit)
        
        if results:
            filter_text = " + ".join([f"{k}={v}" for k, v in filters.items()])
            title = f"🔍 Hybrid Search: '{query}'"
            if filter_text:
                title += f" [{filter_text}]"
            
            table = Table(title=title)
            table.add_column("Score", justify="right", style="dim")
            table.add_column("Reference", style="bold")
            table.add_column("Text", style="italic", width=60)
            table.add_column("Sources", style="bold")
            
            for result in results:
                # Color-code the sources
                sources_text = Text()
                for s in result["sources"].split(";"):
                    color = SOURCE_COLORS.get(s, "white")
                    sources_text.append(f"{s} ", style=color)
                
                table.add_row(
                    f"{result['score']:.3f}",
                    result["reference"],
                    result["text"][:80] + "..." if len(result["text"]) > 80 else result["text"],
                    sources_text
                )
            
            console.print(table)
        else:
            console.print(f"[yellow]No results found for hybrid search: '{query}'[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error in hybrid search: {e}[/red]")

@qdrant.command()
def source_statistics():
    """Get comprehensive source statistics."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        stats = client.get_source_statistics()
        
        if stats:
            # Create statistics tables
            console.print(Panel.fit("📊 KJV Sources Statistics", style="bold blue"))
            
            # Overall stats
            overall_table = Table(title="Overall Statistics")
            overall_table.add_column("Metric", style="bold")
            overall_table.add_column("Value", style="green")
            
            overall_table.add_row("Total Verses", str(stats["total_verses"]))
            overall_table.add_row("Multi-Source Verses", str(stats["multi_source_verses"]))
            overall_table.add_row("Multi-Source %", f"{(stats['multi_source_verses']/stats['total_verses']*100):.1f}%")
            
            console.print(overall_table)
            
            # Source distribution
            source_table = Table(title="Source Distribution")
            source_table.add_column("Source", style="bold")
            source_table.add_column("Count", justify="right", style="green")
            source_table.add_column("Percentage", justify="right", style="blue")
            
            for source, count in stats["source_counts"].items():
                percentage = (count / stats["total_verses"] * 100) if stats["total_verses"] > 0 else 0
                source_table.add_row(
                    f"{source} ({client.entity_relations['source_entities'].get(source, {}).get('name', source)})",
                    str(count),
                    f"{percentage:.1f}%"
                )
            
            console.print(source_table)
            
            # Book distribution
            book_table = Table(title="Book Distribution")
            book_table.add_column("Book", style="bold")
            book_table.add_column("Count", justify="right", style="green")
            book_table.add_column("Type", style="dim")
            
            for book, count in stats["books"].items():
                book_info = client.entity_relations["book_entities"].get(book, {})
                book_type = book_info.get("type", "unknown")
                book_table.add_row(book, str(count), book_type)
            
            console.print(book_table)
            
            # Redaction patterns
            if stats["redaction_patterns"]:
                redaction_table = Table(title="Redaction Patterns")
                redaction_table.add_column("Pattern", style="bold")
                redaction_table.add_column("Count", justify="right", style="green")
                
                for pattern, count in stats["redaction_patterns"].items():
                    redaction_table.add_row(pattern, str(count))
                
                console.print(redaction_table)
        else:
            console.print("[yellow]No statistics available[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error getting source statistics: {e}[/red]")

# POV Analysis Commands

@qdrant.command()
@click.argument("style", type=click.Choice(["narrative_anthropomorphic", "prophetic_didactic", "systematic_ritual", "editorial_harmonizing"]))
@click.option("--limit", default=20, help="Number of results to return")
def search_pov_style(style, limit):
    """Search for verses with specific POV styles."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        results = client.search_by_pov_style(style=style, limit=limit)
        
        if results:
            style_names = {
                "narrative_anthropomorphic": "Narrative Anthropomorphic (J)",
                "prophetic_didactic": "Prophetic Didactic (E)",
                "systematic_ritual": "Systematic Ritual (P)",
                "editorial_harmonizing": "Editorial Harmonizing (R)"
            }
            
            table = Table(title=f"🎭 POV Style: {style_names.get(style, style)}")
            table.add_column("Reference", style="bold")
            table.add_column("Text", style="italic", width=60)
            table.add_column("Sources", style="bold")
            table.add_column("POV", style="dim")
            
            for result in results:
                # Color-code the sources
                sources_text = Text()
                for s in result["sources"].split(";"):
                    color = SOURCE_COLORS.get(s, "white")
                    sources_text.append(f"{s} ", style=color)
                
                # Get POV info
                pov_primary = result.get("pov_primary", "")
                pov_style = result.get("pov_style", "")
                
                table.add_row(
                    result["reference"],
                    result["text"][:80] + "..." if len(result["text"]) > 80 else result["text"],
                    sources_text,
                    f"{pov_primary} ({pov_style})"
                )
            
            console.print(table)
        else:
            console.print(f"[yellow]No verses found with {style} POV style[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error searching POV style: {e}[/red]")

@qdrant.command()
@click.argument("perspective", type=click.Choice(["intimate_personal", "prophetic_vision", "institutional_priestly", "editorial_omniscient"]))
@click.option("--limit", default=20, help="Number of results to return")
def search_pov_perspective(perspective, limit):
    """Search for verses with specific POV perspectives."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        results = client.search_by_pov_perspective(perspective=perspective, limit=limit)
        
        if results:
            perspective_names = {
                "intimate_personal": "Intimate Personal (J)",
                "prophetic_vision": "Prophetic Vision (E)",
                "institutional_priestly": "Institutional Priestly (P)",
                "editorial_omniscient": "Editorial Omniscient (R)"
            }
            
            table = Table(title=f"👁️ POV Perspective: {perspective_names.get(perspective, perspective)}")
            table.add_column("Reference", style="bold")
            table.add_column("Text", style="italic", width=60)
            table.add_column("Sources", style="bold")
            table.add_column("POV", style="dim")
            
            for result in results:
                # Color-code the sources
                sources_text = Text()
                for s in result["sources"].split(";"):
                    color = SOURCE_COLORS.get(s, "white")
                    sources_text.append(f"{s} ", style=color)
                
                # Get POV info
                pov_primary = result.get("pov_primary", "")
                pov_perspective = result.get("pov_perspective", "")
                
                table.add_row(
                    result["reference"],
                    result["text"][:80] + "..." if len(result["text"]) > 80 else result["text"],
                    sources_text,
                    f"{pov_primary} ({pov_perspective})"
                )
            
            console.print(table)
        else:
            console.print(f"[yellow]No verses found with {perspective} POV perspective[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error searching POV perspective: {e}[/red]")

@qdrant.command()
@click.argument("purpose", type=click.Choice(["storytelling_identity", "moral_instruction", "ritual_instruction", "harmonization_integration"]))
@click.option("--limit", default=20, help="Number of results to return")
def search_pov_purpose(purpose, limit):
    """Search for verses with specific POV purposes."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        results = client.search_by_pov_purpose(purpose=purpose, limit=limit)
        
        if results:
            purpose_names = {
                "storytelling_identity": "Storytelling & Identity (J)",
                "moral_instruction": "Moral Instruction (E)",
                "ritual_instruction": "Ritual Instruction (P)",
                "harmonization_integration": "Harmonization & Integration (R)"
            }
            
            table = Table(title=f"🎯 POV Purpose: {purpose_names.get(purpose, purpose)}")
            table.add_column("Reference", style="bold")
            table.add_column("Text", style="italic", width=60)
            table.add_column("Sources", style="bold")
            table.add_column("POV", style="dim")
            
            for result in results:
                # Color-code the sources
                sources_text = Text()
                for s in result["sources"].split(";"):
                    color = SOURCE_COLORS.get(s, "white")
                    sources_text.append(f"{s} ", style=color)
                
                # Get POV info
                pov_primary = result.get("pov_primary", "")
                pov_purpose = result.get("pov_purpose", "")
                
                table.add_row(
                    result["reference"],
                    result["text"][:80] + "..." if len(result["text"]) > 80 else result["text"],
                    sources_text,
                    f"{pov_primary} ({pov_purpose})"
                )
            
            console.print(table)
        else:
            console.print(f"[yellow]No verses found with {purpose} POV purpose[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error searching POV purpose: {e}[/red]")

@qdrant.command()
@click.argument("theme", type=click.Choice(["creation", "covenant", "family", "journey", "ritual", "holiness", "prophecy", "justice", "worship", "law"]))
@click.option("--limit", default=20, help="Number of results to return")
def search_pov_theme(theme, limit):
    """Search for verses with specific POV themes."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        results = client.search_by_pov_theme(theme=theme, limit=limit)
        
        if results:
            theme_names = {
                "creation": "Creation",
                "covenant": "Covenant",
                "family": "Family",
                "journey": "Journey",
                "ritual": "Ritual",
                "holiness": "Holiness",
                "prophecy": "Prophecy",
                "justice": "Justice",
                "worship": "Worship",
                "law": "Law"
            }
            
            table = Table(title=f"🎨 POV Theme: {theme_names.get(theme, theme)}")
            table.add_column("Reference", style="bold")
            table.add_column("Text", style="italic", width=60)
            table.add_column("Sources", style="bold")
            table.add_column("Themes", style="dim")
            
            for result in results:
                # Color-code the sources
                sources_text = Text()
                for s in result["sources"].split(";"):
                    color = SOURCE_COLORS.get(s, "white")
                    sources_text.append(f"{s} ", style=color)
                
                # Get themes
                themes = result.get("pov_themes", [])
                themes_text = ", ".join(themes[:3])  # Show first 3 themes
                
                table.add_row(
                    result["reference"],
                    result["text"][:80] + "..." if len(result["text"]) > 80 else result["text"],
                    sources_text,
                    themes_text
                )
            
            console.print(table)
        else:
            console.print(f"[yellow]No verses found with {theme} POV theme[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error searching POV theme: {e}[/red]")

@qdrant.command()
@click.argument("source1", type=click.Choice(["J", "E", "P", "R"]))
@click.argument("source2", type=click.Choice(["J", "E", "P", "R"]))
@click.option("--limit", default=20, help="Number of results to return")
def search_pov_comparison(source1, source2, limit):
    """Search for verses that compare POV between two sources."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        results = client.search_pov_comparison(source1=source1, source2=source2, limit=limit)
        
        if results:
            source_names = {"J": "Jahwist", "E": "Elohist", "P": "Priestly", "R": "Redactor"}
            
            table = Table(title=f"🔄 POV Comparison: {source_names.get(source1, source1)} vs {source_names.get(source2, source2)}")
            table.add_column("Reference", style="bold")
            table.add_column("Text", style="italic", width=60)
            table.add_column("Sources", style="bold")
            table.add_column("Primary POV", style="dim")
            table.add_column("Secondary POV", style="dim")
            
            for result in results:
                # Color-code the sources
                sources_text = Text()
                for s in result["sources"].split(";"):
                    color = SOURCE_COLORS.get(s, "white")
                    sources_text.append(f"{s} ", style=color)
                
                # Get POV info
                pov_primary = result.get("pov_primary", "")
                pov_secondary = result.get("pov_secondary", "")
                
                table.add_row(
                    result["reference"],
                    result["text"][:80] + "..." if len(result["text"]) > 80 else result["text"],
                    sources_text,
                    pov_primary,
                    pov_secondary
                )
            
            console.print(table)
        else:
            console.print(f"[yellow]No verses found comparing {source1} and {source2} POV[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error searching POV comparison: {e}[/red]")

@qdrant.command()
@click.argument("complexity", type=click.Choice(["simple", "moderate", "complex", "very_complex"]))
@click.option("--limit", default=20, help="Number of results to return")
def search_pov_complexity(complexity, limit):
    """Search for verses with specific POV complexity levels."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        results = client.search_pov_complexity(complexity=complexity, limit=limit)
        
        if results:
            complexity_names = {
                "simple": "Simple (1 source)",
                "moderate": "Moderate (2 sources)",
                "complex": "Complex (3 sources)",
                "very_complex": "Very Complex (4+ sources)"
            }
            
            table = Table(title=f"🧩 POV Complexity: {complexity_names.get(complexity, complexity)}")
            table.add_column("Reference", style="bold")
            table.add_column("Text", style="italic", width=60)
            table.add_column("Sources", style="bold")
            table.add_column("Source Count", justify="right")
            table.add_column("POV", style="dim")
            
            for result in results:
                # Color-code the sources
                sources_text = Text()
                for s in result["sources"].split(";"):
                    color = SOURCE_COLORS.get(s, "white")
                    sources_text.append(f"{s} ", style=color)
                
                # Get POV info
                pov_primary = result.get("pov_primary", "")
                pov_complexity = result.get("pov_complexity", "")
                
                table.add_row(
                    result["reference"],
                    result["text"][:80] + "..." if len(result["text"]) > 80 else result["text"],
                    sources_text,
                    str(result["source_count"]),
                    f"{pov_primary} ({pov_complexity})"
                )
            
            console.print(table)
        else:
            console.print(f"[yellow]No verses found with {complexity} POV complexity[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error searching POV complexity: {e}[/red]")

@qdrant.command()
@click.argument("query")
@click.option("--limit", default=20, help="Number of results to return")
@click.option("--style", help="Filter by POV style")
@click.option("--perspective", help="Filter by POV perspective")
@click.option("--purpose", help="Filter by POV purpose")
@click.option("--theme", help="Filter by POV theme")
@click.option("--complexity", type=click.Choice(["simple", "moderate", "complex", "very_complex"]), help="Filter by POV complexity")
@click.option("--source", type=click.Choice(["J", "E", "P", "R"]), help="Filter by source")
def search_hybrid_pov(query, limit, style, perspective, purpose, theme, complexity, source):
    """Hybrid search combining semantic similarity with POV filtering."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        
        # Build POV filters
        pov_filters = {}
        if style:
            pov_filters["style"] = style
        if perspective:
            pov_filters["perspective"] = perspective
        if purpose:
            pov_filters["purpose"] = purpose
        if theme:
            pov_filters["theme"] = theme
        if complexity:
            pov_filters["complexity"] = complexity
        if source:
            pov_filters["source"] = source
        
        results = client.search_hybrid_pov(query=query, pov_filters=pov_filters, limit=limit)
        
        if results:
            filter_text = " + ".join([f"{k}={v}" for k, v in pov_filters.items()])
            title = f"🔍 Hybrid POV Search: '{query}'"
            if filter_text:
                title += f" [{filter_text}]"
            
            table = Table(title=title)
            table.add_column("Score", justify="right", style="dim")
            table.add_column("Reference", style="bold")
            table.add_column("Text", style="italic", width=60)
            table.add_column("Sources", style="bold")
            table.add_column("POV", style="dim")
            
            for result in results:
                # Color-code the sources
                sources_text = Text()
                for s in result["sources"].split(";"):
                    color = SOURCE_COLORS.get(s, "white")
                    sources_text.append(f"{s} ", style=color)
                
                # Get POV info
                pov_primary = result.get("pov_primary", "")
                pov_style = result.get("pov_style", "")
                
                table.add_row(
                    f"{result['score']:.3f}",
                    result["reference"],
                    result["text"][:80] + "..." if len(result["text"]) > 80 else result["text"],
                    sources_text,
                    f"{pov_primary} ({pov_style})"
                )
            
            console.print(table)
        else:
            console.print(f"[yellow]No results found for hybrid POV search: '{query}'[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error in hybrid POV search: {e}[/red]")

@qdrant.command()
def pov_statistics():
    """Get comprehensive POV statistics."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        stats = client.get_pov_statistics()
        
        if stats:
            # Create statistics tables
            console.print(Panel.fit("🎭 POV Analysis Statistics", style="bold blue"))
            
            # Overall stats
            overall_table = Table(title="Overall Statistics")
            overall_table.add_column("Metric", style="bold")
            overall_table.add_column("Value", style="green")
            
            overall_table.add_row("Total Verses", str(stats["total_verses"]))
            
            console.print(overall_table)
            
            # POV Styles distribution
            if stats["pov_styles"]:
                style_table = Table(title="POV Styles Distribution")
                style_table.add_column("Style", style="bold")
                style_table.add_column("Count", justify="right", style="green")
                style_table.add_column("Percentage", justify="right", style="blue")
                
                for style, count in stats["pov_styles"].items():
                    percentage = (count / stats["total_verses"] * 100) if stats["total_verses"] > 0 else 0
                    style_table.add_row(style, str(count), f"{percentage:.1f}%")
                
                console.print(style_table)
            
            # POV Perspectives distribution
            if stats["pov_perspectives"]:
                perspective_table = Table(title="POV Perspectives Distribution")
                perspective_table.add_column("Perspective", style="bold")
                perspective_table.add_column("Count", justify="right", style="green")
                
                for perspective, count in stats["pov_perspectives"].items():
                    perspective_table.add_row(perspective, str(count))
                
                console.print(perspective_table)
            
            # POV Purposes distribution
            if stats["pov_purposes"]:
                purpose_table = Table(title="POV Purposes Distribution")
                purpose_table.add_column("Purpose", style="bold")
                purpose_table.add_column("Count", justify="right", style="green")
                
                for purpose, count in stats["pov_purposes"].items():
                    purpose_table.add_row(purpose, str(count))
                
                console.print(purpose_table)
            
            # POV Themes distribution
            if stats["pov_themes"]:
                theme_table = Table(title="POV Themes Distribution")
                theme_table.add_column("Theme", style="bold")
                theme_table.add_column("Count", justify="right", style="green")
                
                # Sort themes by count
                sorted_themes = sorted(stats["pov_themes"].items(), key=lambda x: x[1], reverse=True)
                for theme, count in sorted_themes[:10]:  # Show top 10
                    theme_table.add_row(theme, str(count))
                
                console.print(theme_table)
            
            # POV Complexity distribution
            if stats["pov_complexities"]:
                complexity_table = Table(title="POV Complexity Distribution")
                complexity_table.add_column("Complexity", style="bold")
                complexity_table.add_column("Count", justify="right", style="green")
                complexity_table.add_column("Percentage", justify="right", style="blue")
                
                for complexity, count in stats["pov_complexities"].items():
                    percentage = (count / stats["total_verses"] * 100) if stats["total_verses"] > 0 else 0
                    complexity_table.add_row(complexity, str(count), f"{percentage:.1f}%")
                
                console.print(complexity_table)
        else:
            console.print("[yellow]No POV statistics available[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error getting POV statistics: {e}[/red]")

# ====== DOUBLET ANALYSIS COMMANDS ======

@qdrant.command()
@click.option("--limit", default=50, help="Number of results to return")
def search_doublets(limit):
    """Search for all verses that are part of doublets."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        results = client.search_doublets(limit=limit)
        
        if results:
            table = Table(title=f"📚 Doublet Verses (Top {len(results)})")
            table.add_column("Reference", style="bold blue")
            table.add_column("Text", style="white", max_width=50)
            table.add_column("Sources", style="yellow")
            table.add_column("Doublet Names", style="green")
            table.add_column("Categories", style="cyan")
            table.add_column("Score", justify="right", style="magenta")
            
            for result in results:
                doublet_names = ", ".join(result.get("doublet_names", [])[:2])  # Show first 2
                categories = ", ".join(result.get("doublet_categories", []))
                
                table.add_row(
                    result["canonical_reference"],
                    result["full_text"][:60] + "..." if len(result["full_text"]) > 60 else result["full_text"],
                    result["sources"],
                    doublet_names,
                    categories,
                    f"{result['score']:.3f}"
                )
            
            console.print(table)
            console.print(f"\n[green]✅ Found {len(results)} doublet verses[/green]")
        else:
            console.print("[yellow]No doublet verses found[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error searching doublets: {e}[/red]")

@qdrant.command()
@click.argument("category", type=click.Choice(["cosmogony", "genealogy", "catastrophe", "deception", "covenant", "family_conflict", "prophetic_calling", "law", "wilderness_miracle", "wilderness_provision"]))
@click.option("--limit", default=20, help="Number of results to return")
def search_doublets_by_category(category, limit):
    """Search for doublets by category."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        results = client.search_doublets_by_category(category, limit=limit)
        
        if results:
            table = Table(title=f"📚 Doublets in '{category}' Category")
            table.add_column("Reference", style="bold blue")
            table.add_column("Text", style="white", max_width=50)
            table.add_column("Sources", style="yellow")
            table.add_column("Doublet Name", style="green")
            table.add_column("Themes", style="cyan")
            
            for result in results:
                doublet_name = result.get("doublet_names", [""])[0] if result.get("doublet_names") else ""
                themes = ", ".join(result.get("doublet_themes", [])[:3])  # Show first 3
                
                table.add_row(
                    result["canonical_reference"],
                    result["full_text"][:60] + "..." if len(result["full_text"]) > 60 else result["full_text"],
                    result["sources"],
                    doublet_name,
                    themes
                )
            
            console.print(table)
            console.print(f"\n[green]✅ Found {len(results)} verses in '{category}' doublets[/green]")
        else:
            console.print(f"[yellow]No doublets found in '{category}' category[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error searching doublets by category: {e}[/red]")

@qdrant.command()
@click.argument("doublet_name")
@click.option("--limit", default=20, help="Number of results to return")
def search_doublets_by_name(doublet_name, limit):
    """Search for verses from a specific doublet by name."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        results = client.search_doublets_by_name(doublet_name, limit=limit)
        
        if results:
            table = Table(title=f"📚 Verses from '{doublet_name}' Doublet")
            table.add_column("Reference", style="bold blue")
            table.add_column("Text", style="white", max_width=60)
            table.add_column("Sources", style="yellow")
            table.add_column("Parallels", style="green", max_width=30)
            
            for result in results:
                parallels = ", ".join(result.get("parallel_passages", [])[:2])  # Show first 2
                
                table.add_row(
                    result["canonical_reference"],
                    result["full_text"][:80] + "..." if len(result["full_text"]) > 80 else result["full_text"],
                    result["sources"],
                    parallels
                )
            
            console.print(table)
            console.print(f"\n[green]✅ Found {len(results)} verses from '{doublet_name}' doublet[/green]")
        else:
            console.print(f"[yellow]No verses found for doublet '{doublet_name}'[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error searching doublets by name: {e}[/red]")

@qdrant.command()
@click.argument("book")
@click.argument("chapter", type=int)
@click.argument("verse", type=int)
def search_doublet_parallels(book, chapter, verse):
    """Find parallel passages for a specific verse if it's part of a doublet."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        results = client.search_doublet_parallels(book, chapter, verse)
        
        if results:
            console.print(f"[blue]📖 Parallel passages for {book} {chapter}:{verse}[/blue]\n")
            
            table = Table(title="Parallel Passages")
            table.add_column("Reference", style="bold blue")
            table.add_column("Text", style="white", max_width=60)
            table.add_column("Sources", style="yellow")
            table.add_column("Doublet", style="green")
            table.add_column("Differences", style="cyan", max_width=30)
            
            for result in results:
                doublet_name = result.get("doublet_names", [""])[0] if result.get("doublet_names") else ""
                differences = ", ".join(result.get("theological_differences", [])[:2])
                
                table.add_row(
                    result["canonical_reference"],
                    result["full_text"][:80] + "..." if len(result["full_text"]) > 80 else result["full_text"],
                    result["sources"],
                    doublet_name,
                    differences
                )
            
            console.print(table)
            console.print(f"\n[green]✅ Found {len(results)} parallel passages[/green]")
        else:
            console.print(f"[yellow]No parallel passages found for {book} {chapter}:{verse}. This verse may not be part of a doublet.[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error searching doublet parallels: {e}[/red]")

@qdrant.command()
@click.argument("query")
@click.option("--category", help="Filter by doublet category")
@click.option("--limit", default=20, help="Number of results to return")
def search_hybrid_doublet(query, category, limit):
    """Hybrid search combining semantic similarity with doublet filtering."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        results = client.search_hybrid_doublet(query, category=category, limit=limit)
        
        if results:
            table = Table(title=f"🔍 Hybrid Doublet Search: '{query}'" + (f" (Category: {category})" if category else ""))
            table.add_column("Reference", style="bold blue")
            table.add_column("Text", style="white", max_width=50)
            table.add_column("Sources", style="yellow")
            table.add_column("Doublet", style="green")
            table.add_column("Category", style="cyan")
            table.add_column("Score", justify="right", style="magenta")
            
            for result in results:
                doublet_name = result.get("doublet_names", [""])[0] if result.get("doublet_names") else ""
                category_display = result.get("doublet_categories", [""])[0] if result.get("doublet_categories") else ""
                
                table.add_row(
                    result["canonical_reference"],
                    result["full_text"][:60] + "..." if len(result["full_text"]) > 60 else result["full_text"],
                    result["sources"],
                    doublet_name,
                    category_display,
                    f"{result['score']:.3f}"
                )
            
            console.print(table)
            console.print(f"\n[green]✅ Found {len(results)} relevant doublet verses[/green]")
        else:
            console.print(f"[yellow]No doublet verses found for '{query}'[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error in hybrid doublet search: {e}[/red]")

@qdrant.command()
def doublet_statistics():
    """Get comprehensive doublet statistics."""
    if not QDRANT_AVAILABLE:
        return
    
    try:
        client = create_qdrant_client()
        stats = client.get_doublet_statistics()
        
        if stats:
            # Create statistics tables
            console.print(Panel.fit("📚 Doublet Analysis Statistics", style="bold blue"))
            
            # Overall stats
            overall_table = Table(title="Overall Doublet Statistics")
            overall_table.add_column("Metric", style="bold")
            overall_table.add_column("Value", style="green")
            overall_table.add_column("Percentage", style="blue")
            
            total = stats["total_verses"]
            doublet_verses = stats["doublet_verses"]
            non_doublet = stats["non_doublet_verses"]
            
            overall_table.add_row("Total Verses", str(total), "100.0%")
            overall_table.add_row("Doublet Verses", str(doublet_verses), f"{(doublet_verses/total*100):.1f}%" if total > 0 else "0%")
            overall_table.add_row("Non-Doublet Verses", str(non_doublet), f"{(non_doublet/total*100):.1f}%" if total > 0 else "0%")
            overall_table.add_row("Unique Doublets", str(stats["unique_doublet_count"]), "")
            
            console.print(overall_table)
            
            # Doublet categories
            if stats["doublet_categories"]:
                category_table = Table(title="Doublet Categories")
                category_table.add_column("Category", style="bold")
                category_table.add_column("Verse Count", justify="right", style="green")
                
                sorted_categories = sorted(stats["doublet_categories"].items(), key=lambda x: x[1], reverse=True)
                for category, count in sorted_categories:
                    category_table.add_row(category, str(count))
                
                console.print(category_table)
            
            # Doublets by book
            if stats["doublets_by_book"]:
                book_table = Table(title="Doublets by Book")
                book_table.add_column("Book", style="bold")
                book_table.add_column("Doublet Verses", justify="right", style="green")
                
                sorted_books = sorted(stats["doublets_by_book"].items(), key=lambda x: x[1], reverse=True)
                for book, count in sorted_books:
                    book_table.add_row(book, str(count))
                
                console.print(book_table)
            
            # Source distribution in doublets
            if stats["source_doublet_distribution"]:
                source_table = Table(title="Source Distribution in Doublets")
                source_table.add_column("Source", style="bold")
                source_table.add_column("Doublet Occurrences", justify="right", style="green")
                
                for source, count in stats["source_doublet_distribution"].items():
                    if count > 0:
                        source_table.add_row(source, str(count))
                
                console.print(source_table)
            
            # Top doublet names
            if stats["doublet_names"]:
                name_table = Table(title="Most Common Doublets")
                name_table.add_column("Doublet Name", style="bold")
                name_table.add_column("Verse Count", justify="right", style="green")
                
                sorted_names = sorted(stats["doublet_names"].items(), key=lambda x: x[1], reverse=True)
                for name, count in sorted_names[:10]:  # Top 10
                    name_table.add_row(name, str(count))
                
                console.print(name_table)
            
        else:
            console.print("[yellow]No doublet statistics available[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error getting doublet statistics: {e}[/red]")

if __name__ == "__main__":
    cli() 