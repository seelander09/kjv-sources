"""
scraper.py — Module for scraping KJV verses with source annotations.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://www.kingjamesbibleonline.org"
BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"
    # Add more books as needed
]

def get_chapter_urls(book):
    """Scrape all chapter URLs for a given book."""
    book_url = f"{BASE_URL}/{book}/"
    response = requests.get(book_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")
    links = soup.select("div.chapter a")
    return [BASE_URL + link.get("href") for link in links]

def scrape_chapter(url):
    """Scrape verses from a chapter URL."""
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")
    verses = soup.select("div.scripture span")
    
    data = []
    for verse in verses:
        num_tag = verse.find("b")
        if not num_tag:
            continue
        verse_num = num_tag.text.strip()
        verse_text = verse.get_text().replace(verse_num, "").strip()
        data.append({
            "book": url.split("/")[-3],
            "chapter": url.split("/")[-2],
            "verse_num": verse_num,
            "verse_text": verse_text,
            "chapter_url": url
        })
    return data

def scrape_book(book):
    """Scrape all chapters of a single book."""
    print(f"Scraping {book}...")
    all_verses = []
    for url in get_chapter_urls(book):
        verses = scrape_chapter(url)
        # Ensure book name is correctly attached
        for v in verses:
            v["book"] = book
        all_verses.extend(verses)
        time.sleep(1)  # politeness delay
    return all_verses

def scrape_sources(books=BOOKS):
    """Scrape verses for all books in BOOKS."""
    all_data = []
    for book in books:
        all_data.extend(scrape_book(book))
    return all_data

def main():
    """Entry point: scrape sources and save to CSV."""
    all_data = scrape_sources()
    df = pd.DataFrame(all_data)
    df.to_csv("raw_data.csv", index=False)
    print("✅ Scraping complete. Saved to raw_data.csv")

if __name__ == "__main__":
    main()