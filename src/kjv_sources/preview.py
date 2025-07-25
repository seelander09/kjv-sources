from pathlib import Path
import sys

import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()

SOURCE_STYLES = {
    "J": "bold yellow",
    "E": "bold blue",
    "P": "bold green",
    "D": "bold red",
    "R": "bold magenta",
    "—": "dim"
}

def format_source_tag(tag: str) -> str:
    """
    Format a source tag like 'J+E' with individual colors.
    """
    if not tag or tag.strip() == "":
        return "[dim]—[/]"
    parts = tag.split("+")
    styled_parts = []
    for part in parts:
        style = SOURCE_STYLES.get(part.strip(), "dim")
        styled_parts.append(f"[{style}]{part.strip()}[/]")
    return " + ".join(styled_parts)

def preview_verses(csv_path: Path, count: int = 5):
    """
    Preview a few verses from the annotated CSV file.
    """
    if not csv_path.exists():
        console.print(f"[red]File not found:[/] {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    required = {"book", "chapter", "verse", "text", "source"}
    if not required.issubset(df.columns):
        console.print(
            "[red]CSV missing one of the required columns:[/]"
            f" {', '.join(required)}"
        )
        sys.exit(1)

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Book", style="dim", width=12)
    table.add_column("Chapter", justify="right", width=8)
    table.add_column("Verse", justify="right", width=8)
    table.add_column("Text", style="white", width=60)
    table.add_column("Source", style="white", width=20)

    for _, row in df.head(count).iterrows():
        source_tag = format_source_tag(row["source"])
        table.add_row(
            str(row["book"]),
            str(row["chapter"]),
            str(row["verse"]),
            str(row["text"]),
            source_tag
        )

    console.print(table)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print(
            "[yellow]Usage:[/] python preview.py [path_to_csv] [optional:count]"
        )
        sys.exit(1)

    path_arg = Path(sys.argv[1])
    num = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    preview_verses(path_arg, num)