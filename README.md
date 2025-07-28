# KJV Sources - Documentary Hypothesis Analysis

A comprehensive tool for analyzing the Documentary Hypothesis in the King James Version of the Bible, with enhanced data structures optimized for LLM training and scholarly research.

## 🎯 Overview

This project parses wikitext files containing color-coded biblical verses according to the Documentary Hypothesis (J, E, P, R sources) and generates multiple data formats for analysis, visualization, and machine learning applications.

### Key Features

- **Multi-source verse parsing** with individual source text extraction
- **LLM-optimized data structures** for training and fine-tuning
- **Rich CLI interface** with color-coded previews
- **Multiple output formats** (CSV, JSONL, HTML, training datasets)
- **Source analysis** with percentages, confidence metrics, and redaction indicators
- **Pipeline processing** for batch operations across all books

## 📚 Documentary Hypothesis Sources

The tool identifies and analyzes four main sources:

| Source | Color | Description | Characteristics |
|--------|-------|-------------|-----------------|
| **J** (Jahwist) | `#000088` (Navy Blue) | Early narrative source | Anthropomorphic God, vivid storytelling |
| **E** (Elohist) | `#008888` (Teal) | Northern narrative source | Prophetic emphasis, divine messengers |
| **P** (Priestly) | `#888800` (Olive Yellow) | Priestly/liturgical source | Systematic organization, ritual focus |
| **R** (Redactor) | `#880000` (Maroon Red) | Editorial additions | Harmonizing elements, transitions |

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+ required
python --version

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Process a single book
python parse_wikitext.py genesis

# Process all books in pipeline mode
python parse_wikitext.py pipeline

# Preview data with CLI
python -m src.kjv_sources.cli rich-preview genesis
```

## 📖 Detailed Usage Guide

### 1. Data Processing

#### Single Book Processing
```bash
# Process Genesis with enhanced output
python parse_wikitext.py genesis

# Process with specific options
python parse_wikitext.py exodus
python parse_wikitext.py leviticus
python parse_wikitext.py numbers
python parse_wikitext.py deuteronomy
```

#### Pipeline Processing
```bash
# Process all books at once
python parse_wikitext.py pipeline
```

This generates:
- Enhanced CSV files with LLM-optimized columns
- HTML previews with color-coded sources
- Training datasets for machine learning
- Timestamped and latest file versions

### 2. CLI Interface

The CLI provides rich, interactive previews and analysis tools.

#### Rich Preview Command
```bash
# Basic preview
python -m src.kjv_sources.cli rich-preview genesis

# Preview with source text columns
python -m src.kjv_sources.cli rich-preview genesis --show-source-texts

# Filter by chapter
python -m src.kjv_sources.cli rich-preview genesis --chapter 1

# Show only multi-source verses
python -m src.kjv_sources.cli rich-preview genesis --show-multi

# Filter by specific source
python -m src.kjv_sources.cli rich-preview genesis --source J

# Combine filters
python -m src.kjv_sources.cli rich-preview genesis --chapter 2 --source P --limit 5
```

#### Training Data Preview
```bash
# Preview instruction fine-tuning data
python -m src.kjv_sources.cli preview-training genesis --format training

# Preview source classification data
python -m src.kjv_sources.cli preview-training genesis --format classification

# Preview sequence labeling data
python -m src.kjv_sources.cli preview-training genesis --format sequence

# Preview complex analysis data
python -m src.kjv_sources.cli preview-training genesis --format analysis

# Show more examples
python -m src.kjv_sources.cli preview-training genesis --format training --limit 10
```

#### Enhanced CSV Preview
```bash
# Preview LLM-optimized CSV structure
python -m src.kjv_sources.cli preview-enhanced-csv genesis

# Show more rows
python -m src.kjv_sources.cli preview-enhanced-csv genesis --limit 10
```

#### Standard CSV Preview
```bash
# Preview basic CSV data
python -m src.kjv_sources.cli preview genesis

# Preview with JSON format
python -m src.kjv_sources.cli preview genesis --format json

# Filter by chapter
python -m src.kjv_sources.cli preview genesis --chapter 1
```

### 3. Output Files

#### Generated File Structure
```
output/
├── Genesis/
│   ├── Genesis.csv                    # Enhanced CSV with LLM features
│   ├── Genesis.html                   # Color-coded HTML preview
│   ├── Genesis_training.jsonl         # Instruction fine-tuning data
│   ├── Genesis_classification.jsonl   # Source classification data
│   ├── Genesis_sequence.jsonl         # Sequence labeling data
│   ├── Genesis_analysis.jsonl         # Complex analysis tasks
│   ├── Genesis_latest.csv             # Latest CSV version
│   └── Genesis_latest.html            # Latest HTML version
├── Exodus/
│   └── ... (same structure)
├── pipeline_manifest.json             # Pipeline processing summary
└── latest_manifest.json               # Latest processing summary
```

### Research Applications
- **Textual criticism** and source analysis
- **Computational linguistics** for biblical studies
- **Machine learning** in religious studies
- **Digital humanities** research
- **Theological education** and training

## 🤝 License

[Add your license information here]

## 🤝 Acknowledgments

- **Wikitext sources** from [source attribution]
- **Documentary Hypothesis** scholarship
- **Rich library** for CLI formatting
- **Click library** for command-line interface

---

For questions, issues, or contributions, please refer to the project documentation or create an issue in the repository.

#### Enhanced CSV Columns

| Column | Description | LLM Training Use |
|--------|-------------|------------------|
| `verse_id` | Unique identifier | Data linking, references |
| `canonical_reference` | Standard biblical reference | Context, citations |
| `word_count` | Number of words | Text analysis, complexity |
| `sources` | All sources (semicolon-separated) | Multi-label classification |
| `source_count` | Number of sources | Complexity assessment |
| `primary_source` | Dominant source | Primary classification |
| `source_sequence` | Order of sources (J->R->J) | Sequence analysis |
| `source_percentages` | Quantitative contribution | Source dominance analysis |
| `redaction_indicators` | Redaction complexity flags | Editorial analysis |
| `text_J/E/P/R` | Individual source texts | Source-specific analysis |
| `metadata` | JSON with additional data | Extended analysis |

## 🤖 LLM Training Datasets

### 1. Instruction Fine-tuning (`*_training.jsonl`)
```json
{
  "instruction": "Analyze the source composition of this biblical verse.",
  "input": "Verse: In the beginning God created the heaven and the earth.\nReference: Genesis 1:1",
  "output": "This verse contains 1 source(s): P. Primary source: P.",
  "metadata": {
    "book": "Genesis",
    "chapter": "1",
    "verse": "1",
    "sources": ["P"],
    "is_multi_source": false
  }
}
```

### 2. Source Classification (`*_classification.jsonl`)
```json
{
  "text": "In the beginning God created the heaven and the earth.",
  "label": 0,
  "source": "J",
  "metadata": {
    "book": "Genesis",
    "chapter": "1",
    "verse": "1",
    "all_sources": ["P"]
  }
}
```

### 3. Sequence Labeling (`*_sequence.jsonl`)
```json
{
  "text": "These are the generations of the heavens and of the earth when they were created, in the day that the LORD God made the earth and the heavens,",
  "labels": ["P", "J", "R", "J"],
  "metadata": {
    "book": "Genesis",
    "chapter": "2",
    "verse": "4",
    "source_sequence": "P->J->R->J"
  }
}
```

### 4. Complex Analysis (`*_analysis.jsonl`)
```json
{
  "task": "redaction_analysis",
  "prompt": "Analyze the redaction process in: These are the generations...",
  "answer": "Redaction indicators: Complex redaction",
  "metadata": {
    "verse_id": "Genesis_2_4"
  }
}
```

## 🔧 Advanced Usage

### Custom Data Processing
```python
from parse_wikitext import parse_wikitext_file, write_csv_output

# Parse custom wikitext file
verses = parse_wikitext_file("path/to/custom.wikitext")

# Generate enhanced CSV
write_csv_output(verses, "CustomBook", "output/")
```

### CLI Customization
```bash
# Use custom output directory
python -m src.kjv_sources.cli rich-preview genesis --data-dir /custom/path

# Combine multiple books
python -m src.kjv_sources.cli combine --books Genesis Exodus --output combined.jsonl
```

### Batch Processing Script
```bash
#!/bin/bash
# Process all books and generate training data
for book in genesis exodus leviticus numbers deuteronomy; do
    echo "Processing $book..."
    python parse_wikitext.py $book
    python -m src.kjv_sources.cli preview-training $book --format training --limit 3
done
```

## 📊 Data Analysis Examples

### Source Distribution Analysis
```python
import pandas as pd

# Load enhanced CSV
df = pd.read_csv("output/Genesis/Genesis.csv")

# Analyze source distribution
source_counts = df['sources'].str.split(';').explode().value_counts()
print("Source distribution:", source_counts)

# Find multi-source verses
multi_source = df[df['source_count'] > 1]
print(f"Multi-source verses: {len(multi_source)}")
```

### LLM Training Preparation
```python
import json

# Load training data
with open("output/Genesis/Genesis_training.jsonl", "r") as f:
    training_data = [json.loads(line) for line in f]

# Prepare for fine-tuning
instructions = [ex["instruction"] for ex in training_data]
inputs = [ex["input"] for ex in training_data]
outputs = [ex["output"] for ex in training_data]
```