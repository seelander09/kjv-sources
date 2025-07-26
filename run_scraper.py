import argparse
from scraper_wikiversity import (
    scrape_genesis_wikiversity,
    scrape_exodus_wikiversity,
    scrape_leviticus_wikiversity,
    scrape_numbers_wikiversity,
    scrape_deuteronomy_wikiversity,
)

parser = argparse.ArgumentParser()
parser.add_argument("--book", required=True, choices=["genesis", "exodus", "leviticus", "numbers", "deuteronomy"])
parser.add_argument("--csv", help="Path to output CSV file", default="output.csv")
parser.add_argument("--dry-run", action="store_true")
parser.add_argument("--no-open", action="store_true")
args = parser.parse_args()

print(f"📘 Running scraper for {args.book}...")

scraper_map = {
    "genesis": scrape_genesis_wikiversity,
    "exodus": scrape_exodus_wikiversity,
    "leviticus": scrape_leviticus_wikiversity,
    "numbers": scrape_numbers_wikiversity,
    "deuteronomy": scrape_deuteronomy_wikiversity,
}

scraper_fn = scraper_map[args.book]
scraper_fn(csv_path=args.csv, dry_run=args.dry_run, no_open=args.no_open)