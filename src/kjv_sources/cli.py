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

# Source color mapping to match the actual colors from wikitext files
SOURCE_COLORS = {
    "J": "#000088",      # Jahwist source - navy blue (matches wikitext)
    "E": "#008888",      # Elohist source - teal blueish grey (matches wikitext)
    "P": "#888800",      # Priestly source - olive yellow (matches wikitext)
    "R": "#880000",      # Redactor - maroon red (matches wikitext)
    "UNKNOWN": "#666666"  # Unknown source - grey
}

# Rich color mapping for terminal display (using hex colors)
RICH_COLORS = {
    "J": "rgb(0,0,136)",      # navy blue
    "E": "rgb(0,136,136)",    # teal
    "P": "rgb(136,136,0)",    # olive yellow
    "R": "rgb(136,0,0)",      # maroon red
    "UNKNOWN": "rgb(102,102,102)"  # grey
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
@click.option("--show-source-texts", is_flag=True, help="Show individual source text columns")
def rich_preview(book, limit, chapter, show_multi, source, show_source_texts):
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
        color = RICH_COLORS.get(source, "white")
        stats_text.append(f"[{color}]{source}[/{color}]: {count}")
    
    if multi_source_count > 0:
        stats_text.append(f"[magenta]Multi-source[/magenta]: {multi_source_count}")
    
    console.print(Panel(
        " ".join(stats_text),
        title="[bold]Source Distribution[/bold]",
        border_style="blue"
    ))
    
    # Create table
    if show_source_texts:
        # Extended table with source text columns
        table = Table(
            title=f"{book.title()} - Verses Preview (with Source Texts)",
            show_header=True,
            header_style="bold magenta",
            border_style="blue"
        )
        
        # Add columns
        table.add_column("Ch", style="cyan", width=4, justify="center")
        table.add_column("V", style="cyan", width=4, justify="center")
        table.add_column("Sources", style="green", width=12, justify="center")
        table.add_column("Text", style="white", width=40, overflow="fold")
        table.add_column("J Text", style=RICH_COLORS["J"], width=30, overflow="fold")
        table.add_column("E Text", style=RICH_COLORS["E"], width=30, overflow="fold")
        table.add_column("P Text", style=RICH_COLORS["P"], width=30, overflow="fold")
        table.add_column("R Text", style=RICH_COLORS["R"], width=30, overflow="fold")
        
        # Add rows
        for verse in verses:
            # Format sources
            sources = verse['source'] if isinstance(verse['source'], list) else [verse['source']]
            source_tags = []
            
            for source in sources:
                color = RICH_COLORS.get(source, "white")
                source_tags.append(f"[{color}]{source}[/{color}]")
            
            source_str = ";".join(source_tags)
            is_multi = len(sources) > 1
            
            # Format text (truncate if too long)
            text = verse['text']
            if len(text) > 37:
                text = text[:34] + "..."
            
            # Get source texts
            text_j = verse.get('text_J', '')
            text_e = verse.get('text_E', '')
            text_p = verse.get('text_P', '')
            text_r = verse.get('text_R', '')
            
            # Truncate source texts
            for source_text in [text_j, text_e, text_p, text_r]:
                if len(source_text) > 27:
                    source_text = source_text[:24] + "..."
            
            # Add row with conditional styling
            row_style = "bold magenta" if is_multi else None
            
            table.add_row(
                verse['chapter'],
                verse['verse'],
                source_str,
                text,
                text_j,
                text_e,
                text_p,
                text_r,
                style=row_style
            )
    else:
        # Standard table
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
                color = RICH_COLORS.get(source, "white")
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
    
    # Show legend with actual colors
    console.print()
    legend_table = Table(
        title="[bold]Source Legend (matching wikitext colors)[/bold]",
        show_header=False,
        border_style="dim",
        width=60
    )
    legend_table.add_column("Source", style="bold")
    legend_table.add_column("Description", style="dim")
    legend_table.add_column("Color", style="dim")
    
    legend_table.add_row(
        f"[{RICH_COLORS['J']}]J[/{RICH_COLORS['J']}]", 
        "Jahwist Source", 
        f"[{RICH_COLORS['J']}]{SOURCE_COLORS['J']}[/{RICH_COLORS['J']}]"
    )
    legend_table.add_row(
        f"[{RICH_COLORS['E']}]E[/{RICH_COLORS['E']}]", 
        "Elohist Source", 
        f"[{RICH_COLORS['E']}]{SOURCE_COLORS['E']}[/{RICH_COLORS['E']}]"
    )
    legend_table.add_row(
        f"[{RICH_COLORS['P']}]P[/{RICH_COLORS['P']}]", 
        "Priestly Source", 
        f"[{RICH_COLORS['P']}]{SOURCE_COLORS['P']}[/{RICH_COLORS['P']}]"
    )
    legend_table.add_row(
        f"[{RICH_COLORS['R']}]R[/{RICH_COLORS['R']}]", 
        "Redactor", 
        f"[{RICH_COLORS['R']}]{SOURCE_COLORS['R']}[/{RICH_COLORS['R']}]"
    )
    legend_table.add_row(
        "[magenta]Multi[/magenta]", 
        "Multiple Sources", 
        "[magenta]Mixed[/magenta]"
    )
    
    console.print(legend_table)

@cli.command()
@click.argument("book")
@click.option("--limit", default=5, help="Number of examples to show")
@click.option("--format", type=click.Choice(["training", "classification", "sequence", "analysis"]), default="training")
def preview_training(book, limit, format):
    """Preview LLM training datasets."""
    console = Console()
    
    # Define the books mapping
    books = {
        "genesis": "output/Genesis",
        "exodus": "output/Exodus", 
        "leviticus": "output/Leviticus",
        "numbers": "output/Numbers",
        "deuteronomy": "output/Deuteronomy"
    }
    
    # Normalize book name
    book_key = book.lower()
    if book_key not in books:
        console.print(f"[red]Unknown book: {book}[/red]")
        console.print(f"Available books: {', '.join(books.keys())}")
        return
    
    book_dir = books[book_key]
    if not os.path.exists(book_dir):
        console.print(f"[red]Book directory not found: {book_dir}[/red]")
        console.print(f"[yellow]Run 'python parse_wikitext.py {book}' first to generate training data[/yellow]")
        return
    
    # Determine file path based on format
    format_files = {
        "training": f"{book.title()}_training.jsonl",
        "classification": f"{book.title()}_classification.jsonl", 
        "sequence": f"{book.title()}_sequence.jsonl",
        "analysis": f"{book.title()}_analysis.jsonl"
    }
    
    file_path = os.path.join(book_dir, format_files[format])
    if not os.path.exists(file_path):
        console.print(f"[red]Training file not found: {file_path}[/red]")
        return
    
    console.print()
    console.print(Panel(
        f"[bold green]{book.title()}[/bold green] - {format.title()} Training Data Preview",
        subtitle=f"[dim]Showing first {limit} examples[/dim]"
    ))
    
    # Read and display examples
    examples = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= limit:
                break
            examples.append(json.loads(line.strip()))
    
    if not examples:
        console.print(f"[yellow]No examples found in {file_path}[/yellow]")
        return
    
    # Display examples based on format
    if format == "training":
        table = Table(
            title=f"{book.title()} - Instruction Fine-tuning Examples",
            show_header=True,
            header_style="bold green",
            border_style="green"
        )
        table.add_column("Instruction", style="cyan", width=40, overflow="fold")
        table.add_column("Input", style="white", width=50, overflow="fold")
        table.add_column("Output", style="yellow", width=50, overflow="fold")
        
        for example in examples:
            table.add_row(
                example.get('instruction', ''),
                example.get('input', '')[:47] + "..." if len(example.get('input', '')) > 50 else example.get('input', ''),
                example.get('output', '')[:47] + "..." if len(example.get('output', '')) > 50 else example.get('output', '')
            )
    
    elif format == "classification":
        table = Table(
            title=f"{book.title()} - Source Classification Examples",
            show_header=True,
            header_style="bold blue",
            border_style="blue"
        )
        table.add_column("Text", style="white", width=60, overflow="fold")
        table.add_column("Source", style="cyan", width=8, justify="center")
        table.add_column("Label", style="green", width=8, justify="center")
        
        for example in examples:
            label_color = "green" if example.get('label') == 1 else "red"
            label_text = "YES" if example.get('label') == 1 else "NO"
            table.add_row(
                example.get('text', '')[:57] + "..." if len(example.get('text', '')) > 60 else example.get('text', ''),
                example.get('source', ''),
                f"[{label_color}]{label_text}[/{label_color}]"
            )
    
    elif format == "sequence":
        table = Table(
            title=f"{book.title()} - Sequence Labeling Examples",
            show_header=True,
            header_style="bold magenta",
            border_style="magenta"
        )
        table.add_column("Text", style="white", width=70, overflow="fold")
        table.add_column("Labels", style="cyan", width=20, overflow="fold")
        
        for example in examples:
            table.add_row(
                example.get('text', '')[:67] + "..." if len(example.get('text', '')) > 70 else example.get('text', ''),
                '->'.join(example.get('labels', []))
            )
    
    elif format == "analysis":
        table = Table(
            title=f"{book.title()} - Complex Analysis Examples",
            show_header=True,
            header_style="bold red",
            border_style="red"
        )
        table.add_column("Task", style="cyan", width=20, overflow="fold")
        table.add_column("Prompt", style="white", width=50, overflow="fold")
        table.add_column("Answer", style="yellow", width=50, overflow="fold")
        
        for example in examples:
            table.add_row(
                example.get('task', ''),
                example.get('prompt', '')[:47] + "..." if len(example.get('prompt', '')) > 50 else example.get('prompt', ''),
                example.get('answer', '')[:47] + "..." if len(example.get('answer', '')) > 50 else example.get('answer', '')
            )
    
    console.print(table)
    
    # Show file info
    console.print()
    info_panel = Panel(
        f"[bold]File:[/bold] {file_path}\n"
        f"[bold]Format:[/bold] {format.title()}\n"
        f"[bold]Examples shown:[/bold] {len(examples)} of {limit}",
        title="[bold]Dataset Information[/bold]",
        border_style="dim"
    )
    console.print(info_panel)

@cli.command()
@click.argument("book")
@click.option("--limit", default=5, help="Number of verses to show")
def preview_enhanced_csv(book, limit):
    """Preview the enhanced CSV structure with LLM-optimized columns."""
    console = Console()
    
    # Define the books mapping
    books = {
        "genesis": "output/Genesis/Genesis.csv",
        "exodus": "output/Exodus/Exodus.csv", 
        "leviticus": "output/Leviticus/Leviticus.csv",
        "numbers": "output/Numbers/Numbers.csv",
        "deuteronomy": "output/Deuteronomy/Deuteronomy.csv"
    }
    
    # Normalize book name
    book_key = book.lower()
    if book_key not in books:
        console.print(f"[red]Unknown book: {book}[/red]")
        console.print(f"Available books: {', '.join(books.keys())}")
        return
    
    csv_path = books[book_key]
    if not os.path.exists(csv_path):
        console.print(f"[red]Enhanced CSV not found: {csv_path}[/red]")
        console.print(f"[yellow]Run 'python parse_wikitext.py {book}' first to generate enhanced CSV[/yellow]")
        return
    
    console.print()
    console.print(Panel(
        f"[bold green]{book.title()}[/bold green] - Enhanced CSV Preview",
        subtitle=f"[dim]Showing first {limit} rows with LLM-optimized columns[/dim]"
    ))
    
    # Read CSV and display
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            rows.append(row)
    
    if not rows:
        console.print(f"[yellow]No rows found in {csv_path}[/yellow]")
        return
    
    # Create table with key enhanced columns
    table = Table(
        title=f"{book.title()} - Enhanced CSV Structure",
        show_header=True,
        header_style="bold green",
        border_style="green"
    )
    
    # Add key columns for LLM training
    key_columns = [
        ('verse_id', 'Verse ID', 'cyan', 15),
        ('canonical_reference', 'Reference', 'cyan', 12),
        ('word_count', 'Words', 'green', 6),
        ('sources', 'Sources', 'yellow', 12),
        ('source_count', 'Count', 'green', 6),
        ('primary_source', 'Primary', 'blue', 8),
        ('source_sequence', 'Sequence', 'magenta', 15),
        ('source_percentages', 'Percentages', 'white', 20),
        ('redaction_indicators', 'Redaction', 'red', 15),
        ('full_text', 'Text', 'white', 40)
    ]
    
    for col_key, col_name, style, width in key_columns:
        table.add_column(col_name, style=style, width=width, overflow="fold")
    
    # Add rows
    for row in rows:
        # Truncate long text
        text = row.get('full_text', '')
        if len(text) > 37:
            text = text[:34] + "..."
        
        # Format percentages
        percentages = row.get('source_percentages', '')
        if len(percentages) > 17:
            percentages = percentages[:14] + "..."
        
        table.add_row(
            row.get('verse_id', ''),
            row.get('canonical_reference', ''),
            row.get('word_count', ''),
            row.get('sources', ''),
            row.get('source_count', ''),
            row.get('primary_source', ''),
            row.get('source_sequence', ''),
            percentages,
            row.get('redaction_indicators', ''),
            text
        )
    
    console.print(table)
    
    # Show column information
    console.print()
    columns_info = Panel(
        f"[bold]Enhanced CSV Columns for LLM Training:[/bold]\n\n"
        f"[cyan]• verse_id[/cyan] - Unique identifier for each verse\n"
        f"[cyan]• canonical_reference[/cyan] - Standard biblical reference\n"
        f"[cyan]• word_count[/cyan] - Number of words in verse\n"
        f"[cyan]• sources[/cyan] - All sources present (semicolon-separated)\n"
        f"[cyan]• source_count[/cyan] - Number of sources in verse\n"
        f"[cyan]• primary_source[/cyan] - First/dominant source\n"
        f"[cyan]• source_sequence[/cyan] - Order of sources (J->R->J)\n"
        f"[cyan]• source_percentages[/cyan] - Quantitative source contribution\n"
        f"[cyan]• redaction_indicators[/cyan] - Redaction complexity flags\n"
        f"[cyan]• text_J/E/P/R[/cyan] - Individual source texts\n"
        f"[cyan]• metadata[/cyan] - JSON with additional analysis data",
        title="[bold]LLM Training Features[/bold]",
        border_style="blue"
    )
    console.print(columns_info)

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