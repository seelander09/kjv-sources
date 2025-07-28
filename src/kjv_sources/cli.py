import os
import csv
import json
import glob
import click
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax

# Add the parent directory to sys.path to import parse_wikitext
sys.path.append(str(Path(__file__).parent.parent.parent))
from parse_wikitext import parse_wikitext_file, COLOR_TO_SOURCE

DEFAULT_OUTPUT_DIR = os.path.join(os.getcwd(), "output")

# Source color mapping for terminal display
SOURCE_COLORS = {
    "J": "blue",      # Jahwist source
    "E": "cyan",      # Elohist source  
    "P": "yellow",    # Priestly source
    "R": "red",       # Redactor
    "UNKNOWN": "white"  # Unknown source
}

@click.group()
def cli():
    """kjv-sources CLI: preview and combine scripture data."""
    pass

@cli.command()
@click.argument("book", required=False)
@click.option("--data-dir", default=DEFAULT_OUTPUT_DIR,
    help="Directory where output/<Book>/*.csv files live")
@click.option("--limit", default=10, help="Max rows to show per book")
@click.option("--chapter", type=int, help="Filter by chapter number")
@click.option("--format", type=click.Choice(["table", "json"]), default="table")
def preview(book, data_dir, limit, chapter, format):
    """Preview CSV rows for one book or all books."""
    console = Console()
    pattern = (
        f"{data_dir}/{book}/*.csv"
        if book else f"{data_dir}/*/*.csv"
    )
    files = sorted(glob.glob(pattern))
    if not files:
        raise click.ClickException(f"No CSVs found with pattern {pattern}")

    for path in files:
        name = os.path.basename(os.path.dirname(path))
        rows = []
        with open(path, encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                if chapter and int(row["chapter"]) != chapter:
                    continue
                rows.append(row)
                if len(rows) >= limit:
                    break

        if not rows:
            console.print(f"[yellow]No matching rows in {name}[/yellow]")
            continue

        if format == "json":
            click.echo(json.dumps({name: rows}, ensure_ascii=False, indent=2))
        else:
            table = Table(title=f"{name} — {os.path.basename(path)} ({len(rows)}/{limit})")
            for col in rows[0].keys():
                table.add_column(col, overflow="fold")
            for r in rows:
                table.add_row(*(r[c] for c in r))
            console.print(table)

@cli.command()
@click.argument("book")
@click.option("--limit", default=10, help="Number of verses to preview")
@click.option("--chapter", type=int, help="Filter by chapter number")
@click.option("--show-multi", is_flag=True, help="Show multi-source verses only")
@click.option("--source", help="Filter by specific source (J, E, P, R)")
def rich_preview(book, limit, chapter, show_multi, source):
    """Show a rich preview of verses with color-coded sources in a table format."""
    console = Console()
    
    # Define the books mapping
    books = {
        "genesis": "wiki_markdown/Genesis.wikitext",
        "exodus": "wiki_markdown/Exodus.wikitext", 
        "leviticus": "wiki_markdown/Leviticus.wikitext",
        "numbers": "wiki_markdown/Numbers.wikitext",
        "deuteronomy": "wiki_markdown/Deuteronomy.wikitext"
    }
    
    # Normalize book name
    book_key = book.lower()
    if book_key not in books:
        console.print(f"[red]Unknown book: {book}[/red]")
        console.print(f"Available books: {', '.join(books.keys())}")
        return
    
    file_path = books[book_key]
    if not os.path.exists(file_path):
        console.print(f"[red]File not found: {file_path}[/red]")
        return
    
    # Show loading message
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Parsing {book.title()}...", total=None)
        
        # Parse the wikitext file
        verses = parse_wikitext_file(file_path)
        
        if not verses:
            console.print(f"[yellow]No verses found in {book.title()}[/yellow]")
            return
        
        # Filter verses if needed
        if chapter:
            verses = [v for v in verses if int(v['chapter']) == chapter]
        
        if show_multi:
            verses = [v for v in verses if isinstance(v['source'], list) and len(v['source']) > 1]
        
        if source:
            source = source.upper()
            verses = [v for v in verses if source in (v['source'] if isinstance(v['source'], list) else [v['source']])]
        
        # Limit verses
        verses = verses[:limit]
        
        progress.update(task, description=f"Found {len(verses)} verses")
    
    # Display header
    console.print()
    console.print(Panel(
        f"[bold blue]{book.title()}[/bold blue] - Rich Preview",
        subtitle=f"[dim]{len(verses)} verses shown[/dim]"
    ))
    
    # Show statistics
    source_counts = {}
    multi_source_count = 0
    for verse in verses:
        if isinstance(verse['source'], list):
            if len(verse['source']) > 1:
                multi_source_count += 1
            for source in verse['source']:
                source_counts[source] = source_counts.get(source, 0) + 1
        else:
            source_counts[verse['source']] = source_counts.get(verse['source'], 0) + 1
    
    # Create statistics panel
    stats_text = []
    for source, count in sorted(source_counts.items()):
        color = SOURCE_COLORS.get(source, "white")
        stats_text.append(f"[{color}]{source}[/{color}]: {count}")
    
    if multi_source_count > 0:
        stats_text.append(f"[magenta]Multi-source[/magenta]: {multi_source_count}")
    
    console.print(Panel(
        " ".join(stats_text),
        title="[bold]Source Distribution[/bold]",
        border_style="blue"
    ))
    
    # Create table
    table = Table(
        title=f"{book.title()} - Verses Preview",
        show_header=True,
        header_style="bold magenta",
        border_style="blue"
    )
    
    # Add columns
    table.add_column("Chapter", style="cyan", width=8, justify="center")
    table.add_column("Verse", style="cyan", width=6, justify="center")
    table.add_column("Sources", style="green", width=15, justify="center")
    table.add_column("Text", style="white", width=80, overflow="fold")
    table.add_column("Segments", style="dim", width=10, justify="center")
    
    # Add rows
    for verse in verses:
        # Format sources
        sources = verse['source'] if isinstance(verse['source'], list) else [verse['source']]
        source_tags = []
        
        for source in sources:
            color = SOURCE_COLORS.get(source, "white")
            source_tags.append(f"[{color}]{source}[/{color}]")
        
        source_str = ";".join(source_tags)
        is_multi = len(sources) > 1
        
        # Format text (truncate if too long)
        text = verse['text']
        if len(text) > 75:
            text = text[:72] + "..."
        
        # Add row with conditional styling
        row_style = "bold magenta" if is_multi else None
        segments = len(sources)
        
        table.add_row(
            verse['chapter'],
            verse['verse'],
            source_str,
            text,
            str(segments),
            style=row_style
        )
    
    console.print(table)
    
    # Show legend
    console.print()
    legend_table = Table(
        title="[bold]Source Legend[/bold]",
        show_header=False,
        border_style="dim",
        width=50
    )
    legend_table.add_column("Source", style="bold")
    legend_table.add_column("Description", style="dim")
    
    legend_table.add_row("[blue]J[/blue]", "Jahwist Source")
    legend_table.add_row("[cyan]E[/cyan]", "Elohist Source")
    legend_table.add_row("[yellow]P[/yellow]", "Priestly Source")
    legend_table.add_row("[red]R[/red]", "Redactor")
    legend_table.add_row("[magenta]Multi[/magenta]", "Multiple Sources")
    
    console.print(legend_table)

@cli.command()
@click.option("--data-dir", default=DEFAULT_OUTPUT_DIR,
    help="Directory where output/<Book>/*.csv files live")
@click.option("--format", type=click.Choice(["json", "jsonl"]), default="jsonl")
@click.option("--books", multiple=True,
    help="Subset of books to combine (e.g., --books Genesis Exodus)")
@click.option("--output", default="combined.jsonl",
    help="Path to write the combined file")
def combine(data_dir, format, books, output):
    """Merge all book CSVs into one flat JSON/JSONL."""
    patterns = (
        [f"{data_dir}/{b}/*.csv" for b in books]
        if books else [f"{data_dir}/*/*.csv"]
    )
    files = sorted(sum((glob.glob(p) for p in patterns), []))
    total = 0
    records = []

    with open(output, "w", encoding="utf-8") as out_fp:
        for path in files:
            book = os.path.basename(os.path.dirname(path))
            with open(path, encoding="utf-8") as fp:
                for row in csv.DictReader(fp):
                    rec = {
                        "book": book,
                        "chapter": int(row["chapter"]),
                        "verse": int(row["verse"]),
                        "text": row["text"],
                        "sources": json.loads(row.get("sources", "[]")),
                        "color": row.get("color_code"),
                    }
                    total += 1
                    if format == "jsonl":
                        out_fp.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    else:
                        records.append(rec)

        if format == "json":
            json.dump(records, out_fp, ensure_ascii=False, indent=2)

    click.echo(f"Wrote {total} records to {output}")

if __name__ == "__main__":
    cli()