# KJV Sources Enhanced Data Pipeline

A comprehensive data pipeline for downloading, parsing, and analyzing KJV sources data from Wikiversity with enhanced CLI tools and LLM training preparation.

## 🚀 Quick Start

### Windows Users
Simply double-click `run_pipeline.bat` to run the complete pipeline!

### All Platforms
```bash
# Run the complete pipeline
python kjv_pipeline.py

# Or use the CLI directly
python kjv_cli.py view genesis
```

## 📋 What This Pipeline Does

1. **Downloads** KJV sources data from Wikiversity (first 5 books of the Bible)
2. **Parses** the color-coded wikitext files to extract source information
3. **Creates** multiple data formats:
   - Enhanced CSV files with source analysis
   - LLM training datasets (JSONL format)
   - HTML previews with color coding
   - Simple and LLM-optimized CSV exports
4. **Provides** a rich CLI for viewing and analyzing the data

## 📚 Available Books

- **Genesis** - Creation and early history
- **Exodus** - Israel's deliverance and law
- **Leviticus** - Priestly laws and rituals  
- **Numbers** - Wilderness journey and census
- **Deuteronomy** - Moses' final speeches

## 🎨 Documentary Hypothesis Sources

| Source | Color | Description |
|--------|-------|-------------|
| **J** (Jahwist) | Blue | Early narrative source with anthropomorphic God |
| **E** (Elohist) | Cyan | Northern narrative source with prophetic emphasis |
| **P** (Priestly) | Yellow | Priestly/liturgical source with systematic organization |
| **R** (Redactor) | Red | Editorial additions and harmonizing elements |

## 🔧 CLI Commands

### View Data
```bash
# View verses with rich formatting
python kjv_cli.py view genesis

# View specific chapter
python kjv_cli.py view genesis --chapter 1

# View only multi-source verses
python kjv_cli.py view genesis --show-multi

# Filter by source
python kjv_cli.py view genesis --source P

# Compact view
python kjv_cli.py view genesis --format compact

# JSON output
python kjv_cli.py view genesis --format json
```

### Export CSV
```bash
# Export simple CSV
python kjv_cli.py export-csv genesis --format simple

# Export LLM-optimized CSV
python kjv_cli.py export-csv genesis --format llm

# Export with custom filename
python kjv_cli.py export-csv genesis --output my_genesis.csv
```

### Statistics
```bash
# Show comprehensive statistics
python kjv_cli.py stats genesis

# List all available books
python kjv_cli.py list-books
```

### Search
```bash
# Search by text
python kjv_cli.py search genesis --text "God"

# Search specific chapter
python kjv_cli.py search genesis --chapter 1

# Search specific verse
python kjv_cli.py search genesis --verse 1
```

### Training Data Preview
```bash
# Preview instruction fine-tuning data
python kjv_cli.py preview-training genesis --format training

# Preview source classification data
python kjv_cli.py preview-training genesis --format classification

# Preview sequence labeling data
python kjv_cli.py preview-training genesis --format sequence

# Preview analysis data
python kjv_cli.py preview-training genesis --format analysis
```

### Combine Data
```bash
# Combine all books
python kjv_cli.py combine

# Combine specific books
python kjv_cli.py combine --books genesis exodus

# Custom output file
python kjv_cli.py combine --output my_combined_data.csv
```

## 📊 Output Files

### CSV Formats

#### Simple CSV
- `Reference` - Biblical reference (e.g., "Genesis 1:1")
- `Text` - Full verse text
- `Sources` - Source codes (e.g., "P;J;R")
- `Primary Source` - Dominant source
- `Word Count` - Number of words

#### LLM-Optimized CSV
- All simple columns plus:
- `Source Count` - Number of sources
- `Source Sequence` - Order of sources (e.g., "P->J->R")
- `Source Percentages` - Quantitative contribution
- `Redaction Indicators` - Editorial complexity flags
- `J Text`, `E Text`, `P Text`, `R Text` - Individual source texts

### Training Datasets (JSONL)

#### Instruction Fine-tuning
```json
{
  "instruction": "Analyze the source composition of this biblical verse.",
  "input": "Verse: In the beginning God created the heaven and the earth.\nReference: Genesis 1:1",
  "output": "This verse contains 1 source(s): P. Primary source: P."
}
```

#### Source Classification
```json
{
  "text": "In the beginning God created the heaven and the earth.",
  "label": 0,
  "source": "P"
}
```

#### Sequence Labeling
```json
{
  "text": "These are the generations of the heavens and of the earth...",
  "labels": ["P", "J", "R", "J"]
}
```

## 🎯 LLM Training Use Cases

### 1. Source Classification
Train models to identify which source (J, E, P, R) a verse belongs to.

### 2. Multi-source Detection
Train models to detect verses with multiple sources.

### 3. Redaction Analysis
Train models to identify editorial additions and harmonizations.

### 4. Text Generation
Train models to generate text in the style of specific sources.

### 5. Biblical Studies
Train models for theological and historical analysis.

## 📁 File Structure

```
kjv-sources/
├── output/
│   ├── Genesis/
│   │   ├── Genesis.csv              # Enhanced CSV
│   │   ├── Genesis_training.jsonl   # Training data
│   │   ├── Genesis_classification.jsonl
│   │   ├── Genesis_sequence.jsonl
│   │   ├── Genesis_analysis.jsonl
│   │   └── Genesis.html             # HTML preview
│   ├── Exodus/
│   │   └── ... (same structure)
│   └── ... (other books)
├── wiki_markdown/                   # Downloaded source files
├── kjv_cli.py                      # Enhanced CLI
├── kjv_pipeline.py                 # Complete pipeline
├── run_pipeline.bat                # Windows launcher
└── *.csv                          # Exported CSV files
```

## 🔍 Example Usage

### View Genesis Chapter 1
```bash
python kjv_cli.py view genesis --chapter 1 --limit 5
```

### Export LLM Training Data
```bash
python kjv_cli.py export-csv genesis --format llm --output genesis_llm.csv
```

### Search for Multi-source Verses
```bash
python kjv_cli.py view genesis --show-multi --limit 10
```

### Get Statistics
```bash
python kjv_cli.py stats genesis
```

## 🛠️ Requirements

- Python 3.8+
- Required packages (auto-installed):
  - requests
  - beautifulsoup4
  - lxml
  - pandas
  - click
  - rich

## 🚨 Troubleshooting

### Python Not Found
If you get "Python not found" errors:
1. Install Python 3.8+ from python.org
2. Ensure Python is added to your PATH
3. Try using `python3` or `py` instead of `python`

### Missing Dependencies
The pipeline will automatically install required packages. If manual installation is needed:
```bash
pip install requests beautifulsoup4 lxml pandas click rich
```

### No Data Found
If you get "No data found" errors:
1. Run the complete pipeline first: `python kjv_pipeline.py`
2. Check that the `output/` directory exists
3. Verify that CSV files are present in book subdirectories

## 📈 Data Quality

The pipeline provides:
- **High confidence** source identification
- **Multi-source** verse detection
- **Redaction** complexity analysis
- **Quantitative** source percentages
- **LLM-optimized** data structures

## 🤝 Contributing

This pipeline is designed for:
- **Biblical scholars** and researchers
- **LLM developers** working on religious text models
- **Digital humanities** projects
- **Theological education** and training

## 📄 License

[Add your license information here]

---

For questions or issues, please refer to the main project documentation or create an issue in the repository. 