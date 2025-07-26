# kjv-sources

A command-line scraper for the King James Version of Genesis, annotated by Documentary-Hypothesis source (J, E, P, D, R), pulled from Wikiversity.  

Features:

- Parses inline-style color codes → source labels  
- Tracks chapters via `<h2>/<h3>/<h4>` headings  
- Emits one CSV row per text-segment: `book,chapter,verse,text,source`  
- Timestamped CSV filenames (`genesis_hypothesis_YYYYMMDD_HHMMSS.csv`)  
- `genesis_hypothesis_latest.csv` symlink (or copy on Windows) to the newest run  
- Append-only manifest log (`genesis_manifest.log`) recording each version  
- Cross-platform auto-open of CSV + manifest  
- CLI flags: `--output-dir`, `--no-open`, `--dry-run`  

---  

## 📦 Installation

1. Clone your repo (if you haven’t already):  
   ```bash
   git clone https://github.com/seelander09/kjv-sources.git
   cd kjv-sources
   ```

2. Create & activate your Python environment:

   **Conda**  
   ```bash
   conda create -n kjv-sources-env python=3.10
   conda activate kjv-sources-env
   ```

   **venv**  
   ```bash
   python -m venv kjv-sources-env
   .\kjv-sources-env\Scripts\activate   # Windows
   source kjv-sources-env/bin/activate   # macOS/Linux
   ```

3. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

---  

## ⚙️ Usage

All commands assume you’re in the project root and your environment is activated.

### Basic scrape (defaults)

```bash
python scraper_wikiversity.py
```

- Outputs a timestamped CSV in `data/`  
- Updates (or copies) `data/genesis_hypothesis_latest.csv`  
- Appends run info to `data/genesis_manifest.log`  
- Auto-opens both the CSV and the manifest  

### CLI Options

- `--output-dir DIR`  
  Write CSV, symlink/latest copy, and manifest into `DIR` instead of the default `data/`.  
  ```bash
  python scraper_wikiversity.py --output-dir output/genesis
  ```

- `--no-open`  
  Prevents auto-opening of the CSV and manifest after scraping:  
  ```bash
  python scraper_wikiversity.py --no-open
  ```

- `--dry-run`  
  Show what would happen (filenames, counts, steps) without writing any files or opening anything:  
  ```bash
  python scraper_wikiversity.py --dry-run
  ```

### Full Example

```bash
python scraper_wikiversity.py \
  --output-dir my_data \
  --no-open
```

This will:

1. Fetch & parse Genesis from Wikiversity  
2. Save `my_data/genesis_hypothesis_<timestamp>.csv`  
3. Update `my_data/genesis_hypothesis_latest.csv`  
4. Append a block to `my_data/genesis_manifest.log`  
5. Skip auto-opening files  

---  

## 🗂️ File Structure

```
kjv-sources/
├── data/
│   ├── genesis_hypothesis_20250726_001200.csv
│   ├── genesis_hypothesis_latest.csv
│   └── genesis_manifest.log
├── scraper_wikiversity.py      # Main scraper + CLI entry point
├── requirements.txt            # requests, beautifulsoup4
├── .gitignore
└── README.md
```

---  

## 🗺️ Next Steps

- Extend to other books (add `--book`, `--url` flags)  
- Convert CSV → JSONL for AI-ready corpora  
- Dockerize for reproducible runs  
- Add pytest suites for HTML parsing edge cases  
- Publish on PyPI with a console script entry point  

Contributions welcome! Feel free to open an issue or a pull request.
