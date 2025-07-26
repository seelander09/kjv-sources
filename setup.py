from setuptools import setup, find_packages

setup(
    name="kjv-sources",
    version="0.1.0",
    description="Scripture scraping and parsing tools",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # Add dependencies here if needed
        "click>=8.0",
        "rich>=13.0"
    ],
    entry_points={
        "console_scripts": [
            "kjv-scrape = scraper:main",
            "kjv-sources = kjv_sources.cli:cli",
        ],
    },
)