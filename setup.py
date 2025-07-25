from setuptools import setup, find_packages

setup(
    name="kjv-sources",
    version="0.1.0",
    description="Scripture scraping and parsing tools",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # e.g. "requests>=2.25.1", "beautifulsoup4"
    ],
    entry_points={
        "console_scripts": [
            "kjv-scrape = scraper:main",
        ],
    },
)