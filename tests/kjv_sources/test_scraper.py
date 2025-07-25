from kjv_sources import scraper

def test_scraper_module_exists():
    assert hasattr(scraper, "__file__")

def test_scraper_has_main():
    assert callable(getattr(scraper, "main", None))