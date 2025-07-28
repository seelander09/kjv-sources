#!/usr/bin/env python3
import os
import re
import requests
import subprocess
from bs4 import BeautifulSoup

# 1. Configuration
ROOT_URL     = "https://en.wikiversity.org/wiki/Bible/King_James/Documentary_Hypothesis"
BASE_URL     = "https://en.wikiversity.org"
OUTPUT_DIR   = "wiki_markdown"
WIKI_NS_PATH = "/wiki/Bible/King_James/Documentary_Hypothesis/"

# 2. Gather all linked URLs under the root namespace
def gather_links():
    resp = requests.get(ROOT_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    urls = set()
    for a in soup.select("#mw-content-text a[href]"):
        href = a["href"]
        if href.startswith(WIKI_NS_PATH):
            full = BASE_URL + href
            urls.add(full)
    return sorted(urls)

# 3. Fetch raw wiki-text for a page
def fetch_raw_wikitext(page_url):
    raw_url = page_url + "?action=raw"
    resp = requests.get(raw_url)
    resp.raise_for_status()
    return resp.text

# 4. Write raw text and convert to Markdown
def save_and_convert(name, raw_text):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    raw_path = os.path.join(OUTPUT_DIR, f"{name}.wikitext")
    md_path  = os.path.join(OUTPUT_DIR, f"{name}.md")

    # Save raw wiki-text
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(raw_text)

    # Convert to GitHub-flavored Markdown
    subprocess.run([
        "pandoc",
        "--from",    "mediawiki",
        "--to",      "gfm",
        raw_path,
        "-o",        md_path
    ], check=True)

    print(f"[OK] {name}.md")

def main():
    print(f"🔍 Crawling root page for links…")
    pages = gather_links()

    print(f"📥 Found {len(pages)} pages; downloading and converting…")
    for url in pages:
        name = url.rsplit("/", 1)[-1]
        raw  = fetch_raw_wikitext(url)
        save_and_convert(name, raw)

    print("\n✅ All pages saved in the `wiki_markdown/` folder.")

if __name__ == "__main__":
    main()