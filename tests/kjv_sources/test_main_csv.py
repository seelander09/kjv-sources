import pandas as pd
from kjv_sources.scraper import main, scrape_sources
import pytest

def test_main_creates_csv(tmp_path, monkeypatch):
    out = tmp_path / "raw_data.csv"
    dummy_data = [
        {"book":"Gen","chapter":"1","verse_num":"1","verse_text":"Hello","chapter_url":"u"}
    ]

    # Stub scrape_sources to return our dummy data
    monkeypatch.setattr("kjv_sources.scraper.scrape_sources", lambda: dummy_data)

    # Run main with cwd set to tmp_path
    monkeypatch.chdir(tmp_path)
    main()

    # Read CSV and verify contents
    df = pd.read_csv(out)
    assert df.shape == (1, 5)
    assert df.loc[0, "verse_text"] == "Hello"