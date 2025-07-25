import pytest
from kjv_sources.scraper import scrape_book

class Dummy:
    def __init__(self, urls, verses):
        self.urls = urls
        self.verses = verses

def test_scrape_book_aggregates_all_chapters(monkeypatch):
    dummy_urls = ["u1", "u2"]
    dummy_verses = [{"verse_num":"1","verse_text":"A"}]

    monkeypatch.setattr("kjv_sources.scraper.get_chapter_urls", lambda book: dummy_urls)
    monkeypatch.setattr("kjv_sources.scraper.scrape_chapter", lambda url: dummy_verses)

    result = scrape_book("Genesis")
    # Should have 2 chapters × 1 verse each
    assert len(result) == 2
    assert all(item["book"] == "Genesis" for item in result)