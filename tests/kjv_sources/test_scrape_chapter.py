import requests_mock
from kjv_sources.scraper import scrape_chapter

SAMPLE_HTML = """
<div class="scripture">
  <span><b>1</b>In the beginning God created the heaven and the earth.</span>
  <span><b>2</b>And the earth was without form...</span>
</div>
"""

def test_scrape_chapter_parses_verses():
    url = "https://example.com/Genesis/1/"
    with requests_mock.Mocker() as m:
        m.get(url, text=SAMPLE_HTML)
        data = scrape_chapter(url)
    
    assert isinstance(data, list)
    assert data[0]["verse_num"] == "1"
    assert "created the heaven" in data[0]["verse_text"]
    assert data[1]["verse_num"] == "2"