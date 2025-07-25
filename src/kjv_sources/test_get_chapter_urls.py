import requests_mock
from kjv_sources.scraper import get_chapter_urls, BASE_URL

def test_get_chapter_urls_returns_full_links(tmp_path):
    html = """
    <div class="chapter">
      <a href="/Genesis/1/">Chapter 1</a>
      <a href="/Genesis/2/">Chapter 2</a>
    </div>
    """
    with requests_mock.Mocker() as m:
        m.get(f"{BASE_URL}/Genesis/", text=html)
        urls = get_chapter_urls("Genesis")
    
    assert urls == [
        f"{BASE_URL}/Genesis/1/",
        f"{BASE_URL}/Genesis/2/"
    ]