import os
import csv
import json
import glob
import click
from rich.console import Console
from rich.table import Table

DEFAULT_OUTPUT_DIR = os.path.join(os.getcwd(), "output")

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