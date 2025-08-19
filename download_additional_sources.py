#!/usr/bin/env python3
"""
Download Additional Wikiversity Source Pages
============================================

This script downloads additional Wikiversity pages for individual source analysis
and prepares them for ingestion into the vector database for LLM analysis.

The script focuses on:
1. Individual source pages (J, E, P, D, R in isolation)
2. Sub-source pages (Dtr1, Dtr2, etc.)
3. Specialized analysis pages
4. Comparative analysis pages
"""

import os
import re
import json
import requests
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SourcePage:
    """Represents a source page to download"""
    name: str
    url: str
    category: str
    description: str
    priority: int = 1

class AdditionalSourcesDownloader:
    """Downloads and processes additional Wikiversity source pages"""
    
    def __init__(self, output_dir: str = "wiki_markdown", base_url: str = "https://en.wikiversity.org"):
        self.output_dir = Path(output_dir)
        self.base_url = base_url
        self.output_dir.mkdir(exist_ok=True)
        
        # Define additional source pages to download
        self.source_pages = [
            # Individual source pages
            SourcePage(
                name="Jahwist_source_isolated",
                url="/wiki/Bible/King_James/Documentary_Hypothesis/Jahwist_source",
                category="individual_source",
                description="Jahwist source in isolation",
                priority=1
            ),
            SourcePage(
                name="Elohist_source_isolated", 
                url="/wiki/Bible/King_James/Documentary_Hypothesis/Elohist_source",
                category="individual_source",
                description="Elohist source in isolation",
                priority=1
            ),
            SourcePage(
                name="Priestly_source_isolated",
                url="/wiki/Bible/King_James/Documentary_Hypothesis/Priestly_source", 
                category="individual_source",
                description="Priestly source in isolation",
                priority=1
            ),
            SourcePage(
                name="Deuteronomist_source_isolated",
                url="/wiki/Bible/King_James/Documentary_Hypothesis/Deuteronomist_source",
                category="individual_source", 
                description="Deuteronomist source in isolation",
                priority=1
            ),
            
            # Deuteronomist sub-sources
            SourcePage(
                name="First_Deuteronomist_Version",
                url="/wiki/Bible/King_James/Documentary_Hypothesis/Deuteronomist_source/First_Deuteronomist_Version",
                category="sub_source",
                description="First Deuteronomist version (Dtr1)",
                priority=2
            ),
            SourcePage(
                name="Deuteronomic_Laws",
                url="/wiki/Bible/King_James/Documentary_Hypothesis/Deuteronomist_source/First_Deuteronomist_Version/Deuteronomic_Laws",
                category="sub_source",
                description="Deuteronomic law code",
                priority=2
            ),
            SourcePage(
                name="Song_of_Moses",
                url="/wiki/Bible/King_James/Documentary_Hypothesis/Deuteronomist_source/Secondary_Deuteronomist_Additions/Song_of_Moses",
                category="sub_source",
                description="Song of Moses from Deuteronomist source",
                priority=2
            ),
            
            # Specialized analysis pages
            SourcePage(
                name="Holiness_code",
                url="/wiki/Bible/King_James/Documentary_Hypothesis/Priestly_source/Holiness_code",
                category="specialized",
                description="Holiness code from Priestly source",
                priority=3
            ),
            SourcePage(
                name="Levitical_Laws",
                url="/wiki/Bible/King_James/Documentary_Hypothesis/Priestly_source/Levitical_Laws",
                category="specialized",
                description="Levitical laws from Priestly source",
                priority=3
            ),
            SourcePage(
                name="Levitical_ritual",
                url="/wiki/Bible/King_James/Documentary_Hypothesis/Priestly_source/Levitical_ritual",
                category="specialized",
                description="Levitical ritual texts",
                priority=3
            ),
            
            # Comparative analysis pages
            SourcePage(
                name="Covenant_Code",
                url="/wiki/Bible/King_James/Documentary_Hypothesis/Elohist_source/Covenant_Code",
                category="comparative",
                description="Covenant code for comparison",
                priority=4
            ),
            SourcePage(
                name="Narrative",
                url="/wiki/Bible/King_James/Documentary_Hypothesis/Deuteronomist_source/First_Deuteronomist_Version/Narrative",
                category="comparative",
                description="Narrative elements for comparison",
                priority=4
            ),
        ]
    
    def fetch_raw_wikitext(self, page_url: str) -> str:
        """Fetch raw wikitext for a page"""
        try:
            full_url = self.base_url + page_url + "?action=raw"
            response = requests.get(full_url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {page_url}: {e}")
            return ""
    
    def save_and_convert(self, page: SourcePage, raw_text: str) -> bool:
        """Save raw wikitext and convert to markdown"""
        if not raw_text.strip():
            logger.warning(f"No content for {page.name}")
            return False
        
        try:
            # Save raw wikitext
            wikitext_path = self.output_dir / f"{page.name}.wikitext"
            with open(wikitext_path, "w", encoding="utf-8") as f:
                f.write(raw_text)
            
            # Convert to markdown using pandoc
            md_path = self.output_dir / f"{page.name}.md"
            result = subprocess.run([
                "pandoc",
                "--from", "mediawiki",
                "--to", "gfm",
                str(wikitext_path),
                "-o", str(md_path)
            ], capture_output=True, text=True, check=True)
            
            logger.info(f"✅ Downloaded and converted: {page.name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Pandoc conversion failed for {page.name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to save {page.name}: {e}")
            return False
    
    def create_metadata_file(self, pages: List[SourcePage]) -> None:
        """Create metadata file for downloaded pages"""
        metadata = {
            "download_date": datetime.now().isoformat(),
            "total_pages": len(pages),
            "categories": {},
            "pages": []
        }
        
        for page in pages:
            # Add to category stats
            if page.category not in metadata["categories"]:
                metadata["categories"][page.category] = 0
            metadata["categories"][page.category] += 1
            
            # Add page info
            metadata["pages"].append({
                "name": page.name,
                "url": page.url,
                "category": page.category,
                "description": page.description,
                "priority": page.priority,
                "files": [
                    f"{page.name}.wikitext",
                    f"{page.name}.md"
                ]
            })
        
        # Save metadata
        metadata_path = self.output_dir / "additional_sources_metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Metadata saved to: {metadata_path}")
    
    def download_all(self, priority_filter: Optional[int] = None) -> Dict[str, Any]:
        """Download all source pages"""
        logger.info("🚀 Starting download of additional source pages...")
        
        results = {
            "successful": [],
            "failed": [],
            "skipped": []
        }
        
        # Filter by priority if specified
        pages_to_download = self.source_pages
        if priority_filter is not None:
            pages_to_download = [p for p in self.source_pages if p.priority <= priority_filter]
            logger.info(f"📋 Filtering to priority {priority_filter} and below: {len(pages_to_download)} pages")
        
        for page in pages_to_download:
            logger.info(f"📥 Downloading: {page.name} ({page.category})")
            
            raw_text = self.fetch_raw_wikitext(page.url)
            if raw_text:
                if self.save_and_convert(page, raw_text):
                    results["successful"].append(page.name)
                else:
                    results["failed"].append(page.name)
            else:
                results["skipped"].append(page.name)
        
        # Create metadata file
        self.create_metadata_file(pages_to_download)
        
        # Print summary
        logger.info(f"\n📊 Download Summary:")
        logger.info(f"✅ Successful: {len(results['successful'])}")
        logger.info(f"❌ Failed: {len(results['failed'])}")
        logger.info(f"⏭️  Skipped: {len(results['skipped'])}")
        
        return results

def main():
    """Main function"""
    downloader = AdditionalSourcesDownloader()
    
    # Download all pages (you can specify priority: 1=essential, 2=important, 3=useful, 4=optional)
    results = downloader.download_all(priority_filter=4)
    
    print(f"\n🎉 Download complete!")
    print(f"Files saved in: {downloader.output_dir}")
    print(f"Check additional_sources_metadata.json for details")

if __name__ == "__main__":
    main()
