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
    soup = BeautifulSoup(response.content, "lxml")
    links = soup.select("div.chapter a")
    return [BASE_URL + link.get("href") for link in links]

def scrape_chapter(url):
    """Scrape verses from a chapter URL."""
    response = requests.get(url)
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
            "chapter_url": url,
            "verse_num": verse_num,
            "verse_text": verse_text
        })
    return data

def scrape_book(book):
    """Scrape all chapters of a book."""
    print(f"Scraping {book}...")
    chapter_urls = get_chapter_urls(book)
    all_verses = []
    for url in chapter_urls:
        verses = scrape_chapter(url)
        for v in verses:
            v["book"] = book
            v["chapter"] = url.split("/")[-2]
        all_verses.extend(verses)
        time.sleep(1)  # Be polite to the server
    return all_verses

def main():
    all_data = []
    for book in BOOKS:
        book_data = scrape_book(book)
        all_data.extend(book_data)
    
    df = pd.DataFrame(all_data)
    df.to_csv("raw_data.csv", index=False)
    print("✅ Scraping complete. Saved to raw_data.csv")

if __name__ == "__main__":
    main()