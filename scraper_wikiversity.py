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
from collections import Counter

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

HARD_CODED_LEGEND = {
    "#888800": "E", "#880": "E",
    "#880000": "J", "#800": "J",
    "#008888": "P", "#088": "P",
    "#ff0000": "R", "#f00": "R",
    "#00ff00": "D", "#0f0": "D",
    "#000088": "E",
    "#888888": "P",
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
        for chap, verse, color, source, text in rows:
            if chap != last_chap:
                f.write(f"\n## Chapter {chap}\n")
                last_chap = chap
            swatch = (
                f"`{source}` "
                f"![{color}](https://via.placeholder.com/12/{color[1:]}/000000?text=+) "
            )
            f.write(f"- {chap}:{verse} {swatch} {text}\n")
    print(f"[✅] Markdown preview written: {md_path}")

def print_terminal_preview(book: str, rows: list, limit: int = 20):
    print(f"\n📘 Terminal Preview for {book} (first {limit} rows):\n")
    print(f"{'Chap':<6} {'Verse':<6} {'Source':<6} {'Color':<10} Text")
    print("-" * 80)
    for chap, verse, color, source, text in rows[:limit]:
        try:
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            ansi = f"\033[38;2;{r};{g};{b}m"
        except:
            ansi = ""
        reset = "\033[0m"
        short_text = (text[:60] + "…") if len(text) > 60 else text
        print(f"{chap:<6} {verse:<6} {ansi}{source:<6}{reset} {color:<10} {short_text}")
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

    spans = soup.find_all("span", style=lambda s: s and "#" in s)
    print(f"[DEBUG] {book}: found {len(spans)} total styled spans")

    skips = Counter()
    rows = []
    seen = set()
    source_counts = Counter()

    for span in spans:
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
        sup = span.find_previous(
            lambda t: t.name == "sup" or (t.name == "a" and t.find("sup"))
        )
        if not sup:
            skips["no_sup"] += 1
            continue
        verse = sup.get_text(strip=True).strip("[]")
        chap_tag = span.find_previous(
            lambda t: t.name in ("h2", "h3", "h4") and "Chapter" in t.get_text()
        )
        if not chap_tag:
            skips["no_chap"] += 1
            continue
        cm = re.search(r"Chapter\s+(\d+)", chap_tag.get_text())
        chap = cm.group(1) if cm else ""
        if not chap:
            skips["no_chap"] += 1
            continue
        key = (chap, verse, source, text)
        if key in seen:
            skips["duplicate"] += 1
            continue
        seen.add(key)
        rows.append([chap, verse, hex_code, source, text])
        source_counts[source] += 1

    print(f"[DEBUG] skips: {dict(skips)}")
    print(f"[DEBUG] source counts: {dict(source_counts)}")
    print(f"[DEBUG] kept rows: {len(rows)} / {len(spans)} spans")

    out_dir = os.path.join("output", book)
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, f"{book}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["chapter", "verse", "color", "source", "text"])
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

    return {"spans": len(spans), "rows": len(rows), "sources": dict(source_counts)}

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