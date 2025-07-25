from pathlib import Path
import argparse
import sys

import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()

# style map for the single-letter tags
SOURCE_STYLES = {
    "J": "bold yellow",
    "E": "bold blue",
    "P": "bold green",
    "D": "bold red",
    "R": "bold magenta",
    "—": "dim"
}

# full-name map (without the word “source”)
SOURCE_FULL_NAMES = {
    "J": "yahwist",
    "E": "elohist",
    "P": "priestly",
    "D": "deuteronomist",
    "R": "redactor",
    "—": "none"
}

def print_legend():
    console.print("\n[bold underline]Source Legend[/]")
    for tag, style in SOURCE_STYLES.items():
        if tag == "—":
            continue
        full = SOURCE_FULL_NAMES[tag]
        console.print(f"[{style}]{tag}[/] = [{style}]{full}[/]")

def preview_verses(csv_path: Path, count: int = 5, filter_sources=None):
    if not csv_path.exists():
        console.print(f"[red]File not found:[/] {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    required = {"book", "chapter", "verse", "text", "source"}
    if not required.issubset(df.columns):
        console.print("[red]CSV missing required columns:[/] " + ", ".join(required))
        sys.exit(1)

    # apply --filter if given
    if filter_sources:
        df = df[df["source"].apply(
            lambda s: any(tag in s.split("+") for tag in filter_sources)
        )]

    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("Book", style="dim", width=12)
    table.add_column("Chapter", justify="right", width=8)
    table.add_column("Verse", justify="right", width=8)
    table.add_column("Text", style="white", width=60)
    table.add_column("Source", style="white", width=30)

    for _, row in df.head(count).iterrows():
        raw = row["source"] or "—"
        parts = [p.strip() for p in raw.split("+")]

        # combine letter+name for each source
        styled_pairs = []
        for p in parts:
            style = SOURCE_STYLES.get(p, "dim")
            full  = SOURCE_FULL_NAMES.get(p, p)
            styled_pairs.append(f"[{style}]{p} {full}[/]")

        cell = ", ".join(styled_pairs)

        table.add_row(
            str(row["book"]),
            str(row["chapter"]),
            str(row["verse"]),
            str(row["text"]),
            cell
        )

    console.print(table)
    print_legend()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preview annotated scripture verses.")
    parser.add_argument("csv_path", type=Path, help="Path to CSV file")
    parser.add_argument("--count", type=int, default=5, help="Number of verses to preview")
    parser.add_argument(
        "--filter",
        dest="filter_sources",
        type=lambda s: s.split(","),
        help="Comma-separated source tags to include (e.g. J,P)"
    )

    args = parser.parse_args()
    preview_verses(args.csv_path, args.count, args.filter_sources)