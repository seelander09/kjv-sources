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

if __name__ == "__main__":
    cli() 