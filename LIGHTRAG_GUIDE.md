# LightRAG Integration Guide for KJV Sources Project

## Overview

This guide explains how to set up and use LightRAG (Lightweight Retrieval-Augmented Generation) with your KJV sources project for advanced entity-relation reasoning and structured queries.

## Features

- **Hybrid Retrieval**: Combines dense and sparse retrieval for optimal performance
- **Entity-Relation Reasoning**: Structured queries based on biblical sources (J, E, P, R)
- **Multi-Modal Ingestion**: Handles CSV, JSONL, and Markdown files
- **Rich Query Interface**: Interactive terminal interface with color-coded results
- **Structured Metadata**: Comprehensive metadata for advanced filtering

## Installation

### 1. Install LightRAG Dependencies

```bash
# Install LightRAG and related packages
pip install -r lightrag_requirements.txt

# Or install individually
pip install lightrag sentence-transformers torch transformers rich pandas
```

### 2. Verify Installation

```bash
python -c "import lightrag; print('LightRAG installed successfully')"
```

## Setup Process

### 1. Data Ingestion

Run the LightRAG ingestion pipeline to process your existing data:

```bash
python lightrag_ingestion.py
```

This will:
- Load all CSV, JSONL, and Markdown files from the `output/` directory
- Create structured documents with rich metadata
- Set up entity-relation mappings
- Store everything in the `lightrag_data/` directory

### 2. Verify Ingestion

Check the ingestion results:
- Look for the `lightrag_data/` directory
- Verify `entity_relations.json` was created
- Check collection statistics

## Usage

### Interactive Query Interface

Start the interactive query interface:

```bash
python lightrag_query.py
```

### Available Commands

#### Source-Based Queries
```bash
source:J    # Query verses with Jahwist source
source:E    # Query verses with Elohist source  
source:P    # Query verses with Priestly source
source:R    # Query verses with Redactor source
```

#### Book-Based Queries
```bash
book:Genesis     # Query verses from Genesis
book:Exodus      # Query verses from Exodus
book:Leviticus   # Query verses from Leviticus
book:Numbers     # Query verses from Numbers
book:Deuteronomy # Query verses from Deuteronomy
```

#### Chapter-Based Queries
```bash
chapter:Genesis 1    # Query verses from Genesis Chapter 1
chapter:Exodus 20    # Query verses from Exodus Chapter 20
```

#### Special Queries
```bash
multi        # Query verses with multiple sources
redaction    # Query verses with redaction indicators
```

#### Semantic Search
```bash
creation story           # General semantic search
covenant with Abraham    # Find covenant-related verses
priestly rituals         # Find ritual instructions
```

### Programmatic Usage

You can also use LightRAG programmatically:

```python
from lightrag_query import KJVLightRAGQuery

# Initialize query interface
query_interface = KJVLightRAGQuery()

# Query by source
results = query_interface.query_by_source("J", limit=10)

# Query by book
results = query_interface.query_by_book("Genesis", limit=20)

# Semantic search
results = query_interface.semantic_search("creation narrative", limit=15)

# Display results
query_interface.display_results(results, "My Search Results")
```

## Entity-Relation Structure

### Source Entities
- **J (Jahwist)**: Narrative source with anthropomorphic God
- **E (Elohist)**: Northern source emphasizing divine communication
- **P (Priestly)**: Ritual and genealogical source
- **R (Redactor)**: Editorial additions and connections

### Book Entities
- **Genesis**: Creation and patriarchal narratives
- **Exodus**: Liberation and covenant formation
- **Leviticus**: Ritual and legal codes
- **Numbers**: Wilderness journey and census
- **Deuteronomy**: Covenant renewal and law

### Relation Types
- `contains_source`: verse → source
- `belongs_to_book`: verse → book
- `has_chapter`: verse → chapter
- `multi_source`: verse → multiple sources
- `redaction`: verse → redaction indicators

## Advanced Features

### Hybrid Retrieval

LightRAG uses a hybrid approach combining:

1. **Dense Retrieval**: Semantic similarity using sentence transformers
2. **Sparse Retrieval**: Keyword-based retrieval using BM25
3. **Reranking**: Final ranking using cross-encoder models

### Metadata Filtering

All documents include rich metadata for advanced filtering:

```python
# Example metadata structure
{
    "type": "verse",
    "book": "Genesis",
    "chapter": 1,
    "verse": 1,
    "sources": ["P"],
    "primary_source": "P",
    "source_count": 1,
    "word_count": 10,
    "is_multi_source": False,
    "has_j_source": False,
    "has_e_source": False,
    "has_p_source": True,
    "has_r_source": False
}
```

### Structured Queries

Perform complex entity-relation queries:

```python
# Find verses where J and P sources are combined
results = query_interface.entity_relation_query(
    entity_type="source",
    entity_value="J",
    relation="combined_with",
    limit=20
)
```

## Performance Optimization

### Model Selection

The default configuration uses:
- **Dense Model**: `sentence-transformers/all-MiniLM-L6-v2` (fast, good quality)
- **Sparse Model**: `microsoft/DialoGPT-medium` (keyword matching)
- **Reranker**: `cross-encoder/ms-marco-MiniLM-L-6-v2` (high quality ranking)

### GPU Acceleration

For better performance, enable GPU acceleration:

```python
# In lightrag_ingestion.py, change:
device="cuda"  # Instead of "cpu"
```

### Collection Management

```python
# Get collection statistics
stats = query_interface.get_collection_stats()
print(f"Total documents: {stats['total_documents']}")
print(f"Vector size: {stats['vector_size']}")
```

## Troubleshooting

### Common Issues

1. **LightRAG Import Error**
   ```bash
   pip install lightrag --upgrade
   ```

2. **Model Download Issues**
   ```bash
   # Clear model cache
   rm -rf ~/.cache/huggingface/
   ```

3. **Memory Issues**
   - Reduce batch size in ingestion
   - Use smaller models
   - Enable gradient checkpointing

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with Existing Pipeline

### Workflow Integration

1. **Run your existing pipeline** to generate CSV/JSONL files
2. **Run LightRAG ingestion** to create vector database
3. **Use query interface** for advanced analysis

### Data Flow

```
WikiText → Parser → CSV/JSONL → LightRAG Ingestion → Vector DB → Query Interface
```

## Examples

### Example 1: Source Analysis
```bash
# Find all verses with multiple sources
multi

# Analyze redaction patterns
redaction

# Compare J and P creation accounts
source:J
source:P
```

### Example 2: Narrative Analysis
```bash
# Find covenant narratives
covenant with Abraham

# Find ritual instructions
priestly rituals

# Find genealogical information
genealogy of Adam
```

### Example 3: Chapter Analysis
```bash
# Analyze Genesis creation account
chapter:Genesis 1

# Analyze Exodus covenant
chapter:Exodus 20

# Analyze Deuteronomy law
chapter:Deuteronomy 5
```

## Future Enhancements

- **Multi-language Support**: Hebrew text integration
- **Temporal Analysis**: Chronological source development
- **Geographic Mapping**: Location-based queries
- **Thematic Clustering**: Automatic topic discovery
- **Comparative Analysis**: Cross-book source patterns

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Check LightRAG documentation
4. Create an issue in the repository

---

**Note**: LightRAG provides a powerful foundation for biblical source analysis. The hybrid retrieval approach ensures both semantic understanding and precise keyword matching, making it ideal for complex textual analysis tasks. 