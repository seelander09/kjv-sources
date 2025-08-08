# Enhanced Qdrant Vector Database Integration for KJV Sources

This guide explains how to use the enhanced Qdrant vector database to store and search your KJV sources data with advanced entity-relation reasoning capabilities.

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install qdrant-client sentence-transformers numpy
```

### 2. Set Up Qdrant Collection
```bash
python kjv_cli.py qdrant setup
```

### 3. Upload Your Data
```bash
# Upload all books
python kjv_cli.py qdrant upload-all

# Or upload specific books
python kjv_cli.py qdrant upload genesis
python kjv_cli.py qdrant upload exodus
```

### 4. Test the Enhanced Features
```bash
# Test semantic search
python kjv_cli.py qdrant search-semantic "God created the world"

# Test entity-relation search
python kjv_cli.py qdrant search-multi-source
python kjv_cli.py qdrant search-source-combinations J P
```

## 📊 What Enhanced Qdrant Provides

### Vector Embeddings
- **Semantic Search**: Find verses by meaning, not just exact text
- **Similarity Matching**: Discover related verses across books
- **Context Understanding**: Search for concepts and themes

### Advanced Entity-Relation Filtering
- **Source Filtering**: Find verses by J, E, P, R sources
- **Book Filtering**: Search within specific books
- **Multi-source Detection**: Find verses with multiple sources
- **Redaction Pattern Analysis**: Identify complex editorial work
- **Source Combination Queries**: Find verses with specific source combinations

### Rich Metadata
- **Complete Verse Data**: All source information preserved
- **Source Analysis**: Primary sources, percentages, sequences
- **Redaction Indicators**: Editorial complexity flags
- **Entity-Relation Mappings**: Structured relationships between entities

## 🔧 Enhanced Qdrant Commands

### Setup and Management

#### Create Collection
```bash
# Create new collection
python kjv_cli.py qdrant setup

# Recreate existing collection
python kjv_cli.py qdrant setup --force
```

#### Upload Data
```bash
# Upload all books
python kjv_cli.py qdrant upload-all

# Upload specific books
python kjv_cli.py qdrant upload genesis
python kjv_cli.py qdrant upload exodus leviticus

# Upload with progress tracking
python kjv_cli.py qdrant upload-all --books genesis exodus
```

#### Collection Statistics
```bash
# View collection stats
python kjv_cli.py qdrant stats

# Get comprehensive source statistics
python kjv_cli.py qdrant source-statistics
```

#### Delete Collection
```bash
# Delete collection (use with caution)
python kjv_cli.py qdrant delete --force
```

### Basic Search Commands

#### Semantic Search
```bash
# Basic semantic search
python kjv_cli.py qdrant search-semantic "God created"

# Search with limit
python kjv_cli.py qdrant search-semantic "creation story" --limit 20
```

#### Source Search
```bash
# Search by specific source
python kjv_cli.py qdrant search-by-source P

# Search with limit
python kjv_cli.py qdrant search-by-source J --limit 15
```

### Advanced Entity-Relation Commands

#### Multi-Source Verse Search
```bash
# Find verses with multiple sources (complex redaction)
python kjv_cli.py qdrant search-multi-source

# Find verses with 3+ sources
python kjv_cli.py qdrant search-multi-source --min-sources 3 --limit 10
```

#### Redaction Pattern Analysis
```bash
# Find verses with complex redaction
python kjv_cli.py qdrant search-redaction-patterns complex

# Find verses with simple redaction
python kjv_cli.py qdrant search-redaction-patterns simple

# Find interwoven sources
python kjv_cli.py qdrant search-redaction-patterns interwoven

# Find harmonized text
python kjv_cli.py qdrant search-redaction-patterns harmonized
```

#### Source Combination Queries
```bash
# Find verses with BOTH J and P sources
python kjv_cli.py qdrant search-source-combinations J P --combination-type all

# Find verses with EITHER J or P sources
python kjv_cli.py qdrant search-source-combinations J P --combination-type any

# Find verses with J, P, and R sources
python kjv_cli.py qdrant search-source-combinations J P R --limit 15
```

#### Chapter-Specific Search
```bash
# Search Genesis Chapter 1
python kjv_cli.py qdrant search-by-chapter genesis 1

# Search Exodus Chapter 20 (Ten Commandments)
python kjv_cli.py qdrant search-by-chapter exodus 20

# Search with custom limit
python kjv_cli.py qdrant search-by-chapter deuteronomy 5 --limit 30
```

#### Source Analysis Patterns
```bash
# Find J-dominant verses
python kjv_cli.py qdrant search-source-analysis j_dominant

# Find P-ritual content
python kjv_cli.py qdrant search-source-analysis p_ritual

# Find verses with complex redaction
python kjv_cli.py qdrant search-source-analysis redaction_heavy

# Find narrative flow (J/E sources)
python kjv_cli.py qdrant search-source-analysis narrative_flow
```

#### Hybrid Search (Semantic + Structured)
```bash
# Semantic search with book filter
python kjv_cli.py qdrant search-hybrid "covenant" --book genesis

# Semantic search with source filter
python kjv_cli.py qdrant search-hybrid "creation" --source P

# Semantic search with multiple filters
python kjv_cli.py qdrant search-hybrid "law" --book exodus --source P --chapter 20

# Find complex verses about specific topics
python kjv_cli.py qdrant search-hybrid "sacrifice" --min-sources 2 --limit 15
```

## 📈 Advanced Usage Examples

### Research Workflows

#### 1. Source Analysis Research
```bash
# Get overall statistics
python kjv_cli.py qdrant source-statistics

# Find complex redaction patterns
python kjv_cli.py qdrant search-redaction-patterns complex --limit 30

# Compare J and P creation accounts
python kjv_cli.py qdrant search-source-combinations J P --combination-type all
python kjv_cli.py qdrant search-source-analysis j_dominant
python kjv_cli.py qdrant search-source-analysis p_ritual
```

#### 2. Narrative Flow Analysis
```bash
# Find narrative sources across books
python kjv_cli.py qdrant search-source-analysis narrative_flow --limit 50

# Analyze Genesis narrative structure
python kjv_cli.py qdrant search-hybrid "story" --book genesis --source J

# Find covenant narratives
python kjv_cli.py qdrant search-hybrid "covenant" --source J --limit 20
```

#### 3. Redaction Complexity Study
```bash
# Find most complex redaction
python kjv_cli.py qdrant search-multi-source --min-sources 3 --limit 10

# Analyze redaction patterns by book
python kjv_cli.py qdrant search-hybrid "redaction" --book genesis
python kjv_cli.py qdrant search-hybrid "redaction" --book exodus

# Find harmonized text
python kjv_cli.py qdrant search-redaction-patterns harmonized
```

#### 4. Chapter-by-Chapter Analysis
```bash
# Analyze Genesis creation account
python kjv_cli.py qdrant search-by-chapter genesis 1

# Analyze Exodus law
python kjv_cli.py qdrant search-by-chapter exodus 20

# Analyze Deuteronomy covenant renewal
python kjv_cli.py qdrant search-by-chapter deuteronomy 5
```

## 🔍 Entity-Relation Structure

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

## 📊 Statistics and Analytics

### Source Distribution Analysis
```bash
# Get comprehensive statistics
python kjv_cli.py qdrant source-statistics
```

This provides:
- **Overall Statistics**: Total verses, multi-source count, percentages
- **Source Distribution**: Count and percentage for each source (J, E, P, R)
- **Book Distribution**: Verse count by book with type classification
- **Redaction Patterns**: Frequency of different redaction types

### Custom Analysis Scripts
```python
from src.kjv_sources.qdrant_client import create_qdrant_client

# Create client
client = create_qdrant_client()

# Get statistics
stats = client.get_source_statistics()

# Analyze specific patterns
j_verses = client.search_by_source("J", limit=1000)
p_verses = client.search_by_source("P", limit=1000)

# Compare source characteristics
complex_verses = client.search_multi_source_verses(limit=100)
```

## 🚀 Performance Optimization

### Query Optimization
- **Use filters**: Combine semantic search with structured filters for better results
- **Limit results**: Use appropriate limits to avoid overwhelming output
- **Batch processing**: For large datasets, process in batches

### Memory Management
- **Scroll API**: Use scroll for large result sets
- **Pagination**: Process results in pages
- **Filter early**: Apply filters before semantic search

## 🔧 Troubleshooting

### Common Issues

#### Connection Problems
```bash
# Check Qdrant connection
python kjv_cli.py qdrant stats

# Verify API key and endpoint
# Check network connectivity
```

#### Data Issues
```bash
# Recreate collection if needed
python kjv_cli.py qdrant setup --force

# Re-upload data
python kjv_cli.py qdrant upload-all
```

#### Search Issues
```bash
# Test basic search first
python kjv_cli.py qdrant search-semantic "test"

# Check collection has data
python kjv_cli.py qdrant source-statistics
```

## 📚 Integration Examples

### Programmatic Usage
```python
from src.kjv_sources.qdrant_client import create_qdrant_client

# Initialize client
client = create_qdrant_client()

# Entity-relation search
results = client.search_entity_relation("source", "J", limit=20)

# Hybrid search
results = client.search_hybrid(
    query="covenant with Abraham",
    filters={"book": "Genesis", "source": "J"},
    limit=15
)

# Source analysis
results = client.search_source_analysis("j_dominant", limit=30)

# Get statistics
stats = client.get_source_statistics()
print(f"Total verses: {stats['total_verses']}")
```

### Research Applications
- **Textual criticism** and source analysis
- **Computational linguistics** for biblical studies
- **Machine learning** in religious studies
- **Digital humanities** research
- **Theological education** and training

## 🎯 Advanced Features

### Custom Entity-Relation Queries
The enhanced Qdrant client supports custom entity-relation queries:

```python
# Find verses where J and P sources are combined
results = client.search_source_combinations(["J", "P"], "all")

# Find verses with complex redaction
results = client.search_redaction_patterns("complex")

# Find narrative flow
results = client.search_source_analysis("narrative_flow")
```

### Hybrid Retrieval
Combine semantic similarity with structured filtering:

```python
# Semantic search with source filter
results = client.search_hybrid(
    query="creation narrative",
    filters={"source": "P", "book": "Genesis"}
)
```

### Statistical Analysis
Get comprehensive statistics for research:

```python
# Get source distribution
stats = client.get_source_statistics()
print(f"J source verses: {stats['source_counts']['J']}")
print(f"Multi-source verses: {stats['multi_source_verses']}")
```

---

**Note**: The enhanced Qdrant integration provides powerful entity-relation reasoning capabilities while maintaining the simplicity and performance of a single system. This approach gives you most of the benefits of LightRAG without the complexity of managing multiple systems. 