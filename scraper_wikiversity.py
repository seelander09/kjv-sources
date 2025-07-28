#!/usr/bin/env python3

import os
import sys
import shutil
import re
import json
import time
import requests
from bs4 import BeautifulSoup
import csv
import argparse
from collections import Counter, defaultdict

BOOK_URLS = {
    "Genesis":     "https://en.wikiversity.org/wiki/Bible/King_James/Documentary_Hypothesis/Genesis",
    "Exodus":      "https://en.wikiversity.org/wiki/Bible/King_James/Documentary_Hypothesis/Exodus",
    "Leviticus":   "https://en.wikiversity.org/wiki/Bible/King_James/Documentary_Hypothesis/Leviticus",
    "Numbers":     "https://en.wikiversity.org/wiki/Bible/King_James/Documentary_Hypothesis/Numbers",
    "Deuteronomy": "https://en.wikiversity.org/wiki/Bible/King_James/Documentary_Hypothesis/Deuteronomy",
}

HEX_RE = re.compile(r"#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})")

def normalize_hex(h: str) -> str:
    h = h.strip().lower()
    if len(h) == 4:
        return "#" + "".join(ch*2 for ch in h[1:])
    return h

# Updated color map based on the actual HTML legend
HARD_CODED_LEGEND = {
    # Priestly source (P) - olive yellow
    "#888800": "P", "#880": "P",
    
    # Jahwist source (J) - navy blue  
    "#000088": "J", "#008": "J",
    
    # Elohist source (E) - teal blueish grey
    "#008888": "E", "#088": "E",
    
    # Redactor (R) - maroon red
    "#880000": "R", "#800": "R",
    
    # Common variations and additional colors
    "#0000ff": "J", "#00f": "J",  # Blue variations for J
    "#ff0000": "R", "#f00": "R",  # Red variations for R
    "#00ff00": "D", "#0f0": "D",  # Green for Deuteronomist
    "#006400": "D", "#064": "D",  # Dark green for Deuteronomist
}

def parse_legend(soup: BeautifulSoup) -> dict:
    for tbl in soup.find_all("table"):
        headers = [th.get_text(strip=True).lower() for th in tbl.find_all("th")]
        if any("color" in h for h in headers):
            legend = {}
            for tr in tbl.find_all("tr")[1:]:
                tds = tr.find_all("td")
                if len(tds) < 2:
                    continue
                m = HEX_RE.search(tds[0].get("style", ""))
                hex_code = normalize_hex(m.group(0)) if m else None
                src = tds[1].get_text(strip=True)
                if hex_code and src:
                    legend[hex_code] = src
            return legend
    return {}

def write_markdown_preview(book: str, rows: list):
    out_dir = os.path.join("output", book)
    md_path = os.path.join(out_dir, f"{book}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# {book} Source Preview\n\n")
        last_chap = None
        for chap, verse, sources, text in rows:
            if chap != last_chap:
                f.write(f"\n## Chapter {chap}\n")
                last_chap = chap
            f.write(f"- {chap}:{verse} **{sources}** {text}\n")
    print(f"[✅] Markdown preview written: {md_path}")

def print_terminal_preview(book: str, rows: list, limit: int = 20):
    print(f"\n📘 Terminal Preview for {book} (first {limit} rows):\n")
    print(f"{'Chap':<6} {'Verse':<6} {'Sources':<12} Text")
    print("-" * 80)
    for chap, verse, sources, text in rows[:limit]:
        short_text = (text[:60] + "…") if len(text) > 60 else text
        print(f"{chap:<6} {verse:<6} {sources:<12} {short_text}")
    print("-" * 80)

def scrape_full_book_page_structured(book: str, args) -> dict:
    url = BOOK_URLS[book]
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    legend = parse_legend(soup)
    if not legend:
        print("[WARN] Legend parse failed; using hard-coded map")
        legend = HARD_CODED_LEGEND.copy()
    print(f"[DEBUG] {book} legend: {legend}")

    # Find all paragraphs that contain verse numbers
    paragraphs = soup.find_all("p")
    print(f"[DEBUG] {book}: found {len(paragraphs)} total paragraphs")

    skips = Counter()
    verse_data = defaultdict(lambda: {"sources": set(), "text_parts": []})
    source_counts = Counter()

    # Pre-process to find chapter boundaries - simpler approach
    chapter_boundaries = {}
    chapter_headings = soup.find_all(lambda t: t.name in ("h2", "h3", "h4") and "Chapter" in t.get_text())
    
    # Create a list of all elements in document order
    all_elements = list(soup.find_all())
    
    for i, heading in enumerate(chapter_headings):
        cm = re.search(r"Chapter\s+(\d+)", heading.get_text())
        if cm:
            chapter_num = cm.group(1)
            
            # Find the index of this heading in all_elements
            heading_index = all_elements.index(heading)
            
            # Find the next chapter heading index
            next_heading_index = len(all_elements)
            if i + 1 < len(chapter_headings):
                next_heading = chapter_headings[i + 1]
                next_heading_index = all_elements.index(next_heading)
            
            # Find all paragraphs between this heading and the next
            paragraphs_in_chapter = []
            for j in range(heading_index + 1, next_heading_index):
                elem = all_elements[j]
                if elem.name == "p":
                    paragraphs_in_chapter.append(elem)
            
            chapter_boundaries[chapter_num] = paragraphs_in_chapter
            print(f"[DEBUG] Chapter {chapter_num}: {len(paragraphs_in_chapter)} paragraphs")

    # Process each paragraph with improved chapter detection
    for p in paragraphs:
        # Enhanced verse detection - try multiple methods
        verse = None
        
        # Method 1: Look for small tag with blue span
        small_tag = p.find("small")
        if small_tag:
            verse_span = small_tag.find("span", style=lambda s: s and "#0000ff" in s.lower())
            if verse_span:
                verse = verse_span.get_text(strip=True)
        
        # Method 2: Look for any blue span in the paragraph
        if not verse:
            blue_spans = p.find_all("span", style=lambda s: s and "#0000ff" in s.lower())
            for span in blue_spans:
                span_text = span.get_text(strip=True)
                if span_text.isdigit():
                    verse = span_text
                    break
        
        # Method 3: Look for verse number in paragraph text
        if not verse:
            p_text = p.get_text()
            verse_match = re.search(r'^(\d+)[\.:]?\s', p_text)
            if verse_match:
                verse = verse_match.group(1)
        
        # Method 4: Look for any number at the start of the paragraph
        if not verse:
            p_text = p.get_text(strip=True)
            if p_text and p_text[0].isdigit():
                verse_match = re.match(r'^(\d+)', p_text)
                if verse_match:
                    verse = verse_match.group(1)
        
        if not verse or not verse.isdigit():
            skips["no_verse"] += 1
            continue
        
        # Look for colored text spans in this paragraph
        colored_spans = p.find_all("span", style=lambda s: s and "#" in s and "#0000ff" not in s.lower())
        
        if not colored_spans:
            skips["no_colored_spans"] += 1
            continue
        
        # Find which chapter this paragraph belongs to using the pre-processed boundaries
        chap = None
        for chapter_num, chapter_paragraphs in chapter_boundaries.items():
            if p in chapter_paragraphs:
                chap = chapter_num
                break
        
        if not chap:
            # Fallback: try to find the most recent chapter heading
            chap_tag = p.find_previous(
                lambda t: t.name in ("h2", "h3", "h4") and "Chapter" in t.get_text()
            )
            if chap_tag:
                cm = re.search(r"Chapter\s+(\d+)", chap_tag.get_text())
                chap = cm.group(1) if cm else ""
        
        if not chap:
            skips["no_chap"] += 1
            continue
        
        # Debug: Check Chapter 3, verse 1 specifically
        if book == "Exodus" and chap == "3" and verse == "1":
            print(f"\n🔍 DEBUG: Processing Chapter 3, verse 1")
            print(f"Found {len(colored_spans)} colored spans:")
            for i, span in enumerate(colored_spans):
                style = span.get("style", "")
                text = span.get_text(strip=True)
                m = HEX_RE.search(style)
                if m:
                    hex_code = normalize_hex(m.group(0))
                    source = legend.get(hex_code, "UNKNOWN")
                    print(f"  Span {i+1}: {hex_code} ({source}) - {text[:50]}...")
                else:
                    print(f"  Span {i+1}: No hex code found - {text[:50]}...")
        
        # Process each colored span in this paragraph
        verse_key = (chap, verse)
        for span in colored_spans:
            style = span.get("style", "")
            m = HEX_RE.search(style)
            if not m:
                skips["no_hex"] += 1
                continue
            
            hex_code = normalize_hex(m.group(0))
            if hex_code in ("#0000ff", "#ffffff", "#transparent", "#000000"):
                skips["blue_or_white"] += 1
                continue
            
            if hex_code not in legend:
                skips["not_legend"] += 1
                continue
            
            source = legend[hex_code]
            if args.exclude_source and source == args.exclude_source:
                skips["excluded"] += 1
                continue
            if args.only_source and source != args.only_source:
                skips["filtered"] += 1
                continue
            
            text = span.get_text(strip=True)
            if not text:
                skips["empty_text"] += 1
                continue
            
            # Add source and text to verse data
            verse_data[verse_key]["sources"].add(source)
            verse_data[verse_key]["text_parts"].append((source, text))
            source_counts[source] += 1

    # Convert verse data to rows with combined sources
    rows = []
    for (chap, verse), data in sorted(verse_data.items(), key=lambda x: (int(x[0][0]), int(x[0][1]))):
        # Sort sources alphabetically and join with " + "
        sources = " + ".join(sorted(data["sources"]))
        # Join all text pieces in order they appear
        full_text = " ".join([text for _, text in data["text_parts"]])
        rows.append([chap, verse, sources, full_text])

    print(f"[DEBUG] skips: {dict(skips)}")
    print(f"[DEBUG] source counts: {dict(source_counts)}")
    print(f"[DEBUG] kept rows: {len(rows)} / {len(paragraphs)} paragraphs")

    # Debug: Show Chapter 3 verses specifically
    if book == "Exodus":
        print(f"\n🔍 DEBUG: Chapter 3 verses found:")
        chapter_3_verses = [(chap, verse, sources, text) for chap, verse, sources, text in rows if chap == "3"]
        if chapter_3_verses:
            print(f"Found {len(chapter_3_verses)} verses in Chapter 3:")
            for chap, verse, sources, text in chapter_3_verses[:10]:  # Show first 10
                short_text = (text[:50] + "…") if len(text) > 50 else text
                print(f"  {chap}:{verse} {sources} - {short_text}")
        else:
            print("❌ No Chapter 3 verses found!")

    out_dir = os.path.join("output", book)
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, f"{book}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["chapter", "verse", "sources", "text"])
        writer.writerows(rows)
    print(f"[✅] CSV written: {csv_path} ({len(rows)} rows)")

    link = os.path.join(out_dir, f"latest-{book}.csv")
    if os.path.exists(link):
        os.remove(link)
    try:
        if sys.platform.startswith("win"):
            shutil.copy(csv_path, link)
        else:
            os.symlink(os.path.abspath(csv_path), link)
        print(f"[✅] latest pointer updated: {link}")
    except Exception as e:
        print(f"[WARN] Could not update latest pointer: {e}")

    write_markdown_preview(book, rows)
    print_terminal_preview(book, rows)

    return {"paragraphs": len(paragraphs), "rows": len(rows), "sources": dict(source_counts)}

def main():
    print("[INFO] Starting scraper...")
    parser = argparse.ArgumentParser(
        description="Scrape Documentary-Hypothesis source-tagged text for Pentateuch books."
    )
    parser.add_argument(
        "book",
        choices=list(BOOK_URLS.keys()) + ["All"],
        help="Which book to scrape (or All for every Pentateuch book)"
    )
    parser.add_argument(
        "--exclude-source",
        help="Skip spans with this source label (e.g. U)"
    )
    parser.add_argument(
        "--only-source",
        help="Include only spans with this source label (e.g. P)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print debug HTML structure information"
    )
    args = parser.parse_args()

    books = BOOK_URLS.keys() if args.book == "All" else [args.book]

    manifest = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "books": {}
    }

    for b in books:
        manifest["books"][b] = scrape_full_book_page_structured(b, args)

    man_path = os.path.join("output", "manifest.json")
    with open(man_path, "w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2)
    print(f"[✅] Manifest written: {man_path}")

if __name__ == "__main__":
    main()