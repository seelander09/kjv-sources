#!/usr/bin/env python3
import re
import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import shutil
import platform
import subprocess
import argparse

COLOR_SOURCE_MAP = {
    "#0000ff": "J",
    "#000088": "J",
    "#008080": "E",
    "#008888": "E",
    "#888800": "P",
    "#800000": "R",
    "#006400": "D",
}

def open_file(path: str):
    """Cross-platform file opener."""
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", path], check=False)
        else:  # Linux
            subprocess.run(["xdg-open", path], check=False)
    except Exception as e:
        print(f"⚠️ Could not auto-open {path}: {e}")

def scrape_genesis_wikiversity(output_dir: str,
                               no_open: bool,
                               dry_run: bool):
    url = (
        "https://en.wikiversity.org/wiki/"
        "Bible/King_James/Documentary_Hypothesis/Genesis"
    )
    resp = requests.get(url)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    content = soup.find("div", id="mw-content-text")
    if not content:
        print("❌ Could not find main content div (#mw-content-text).")
        return

    rows = []
    unknown_colors = {}
    chapter = ""

    # Walk through chapter headings (h2/h3/h4) and paragraphs in order
    for tag in content.find_all(["h2", "h3", "h4", "p"]):
        # Capture chapter number from any header
        if tag.name in ("h2", "h3", "h4"):
            heading = tag.get_text(strip=True)
            # Try several patterns
            m = re.search(r"Genesis\s+(\d+)", heading)
            if not m:
                m = re.search(r"Chapter\s+(\d+)", heading)
            if m:
                chapter = m.group(1)
            continue

        # Paragraph → look for verse spans
        spans = tag.find_all("span", style=True)
        if len(spans) < 2:
            continue

        verse_label = spans[0].get_text(strip=True)
        if not re.match(r"^\d+$", verse_label):
            continue

        for seg in spans[1:]:
            text = seg.get_text(" ", strip=True)
            if not text:
                continue

            m = re.search(r"color\s*:\s*(#[0-9A-Fa-f]{6})", seg["style"])
            if not m:
                continue
            hex_color = m.group(1).lower()

            source = COLOR_SOURCE_MAP.get(hex_color)
            if not source:
                unknown_colors[hex_color] = unknown_colors.get(hex_color, 0) + 1
                continue

            rows.append({
                "book":    "Genesis",
                "chapter": chapter,
                "verse":   verse_label,
                "text":    text,
                "source":  source
            })

    print(f"🔍 Parsed {len(rows)} segments with chapter tracking.")
    print("\n🧪 Sample:")
    for row in rows[:5]:
        print(f"  {row['chapter']}:{row['verse']} [{row['source']}] → {row['text'][:60]}...")

    # Prepare filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(output_dir, exist_ok=True)
    output_csv = os.path.join(
        output_dir, f"genesis_hypothesis_{timestamp}.csv"
    )
    latest_link = os.path.join(
        output_dir, "genesis_hypothesis_latest.csv"
    )
    manifest_log = os.path.join(
        output_dir, "genesis_manifest.log"
    )

    if dry_run:
        print("\n--- DRY RUN ---")
        print(f"Would write CSV:        {output_csv}")
        print(f"Would update latest:    {latest_link}")
        print(f"Would append manifest:  {manifest_log}")
        return

    # Write the CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=[
            "book", "chapter", "verse", "text", "source"
        ])
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n✅ Wrote {len(rows)} segments to {output_csv}")

    # Create/update symlink (or fallback copy on Windows)
    try:
        if os.path.islink(latest_link) or os.path.exists(latest_link):
            os.remove(latest_link)
        os.symlink(output_csv, latest_link)
        print(f"🔗 Symlinked latest → {latest_link}")
    except OSError:
        shutil.copy2(output_csv, latest_link)
        print(f"📎 Copied latest file → {latest_link}")

    # Append to manifest
    with open(manifest_log, "a", encoding="utf-8") as log:
        log.write(f"\n[{timestamp}]\n")
        log.write(f"  File: {os.path.basename(output_csv)}\n")
        log.write(f"  Segments: {len(rows)}\n")
        if unknown_colors:
            log.write("  Unmapped colors:\n")
            for c, cnt in unknown_colors.items():
                log.write(f"    {c} → {cnt}\n")
        else:
            log.write("  Unmapped colors: None\n")
    print(f"🗂️ Logged version info → {manifest_log}")

    # Auto-open unless suppressed
    if not no_open:
        open_file(output_csv)
        open_file(manifest_log)

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Scrape Genesis KJV Documentary-Hypothesis with chapter tracking, "
            "versioning, manifest & optional auto-open."
        )
    )
    parser.add_argument(
        "--output-dir",
        default="data",
        help="Directory for CSVs, symlink & manifest"
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Suppress auto-opening of output files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without writing or opening files"
    )
    args = parser.parse_args()

    scrape_genesis_wikiversity(
        output_dir=args.output_dir,
        no_open=args.no_open,
        dry_run=args.dry_run
    )

if __name__ == "__main__":
    main()