# Qdrant Vector Database Integration for KJV Sources

This guide explains how to use Qdrant vector database to store and search your KJV sources data with semantic similarity and advanced filtering.

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

### 4. Test the Setup
```bash
# Test semantic search
python kjv_cli.py qdrant search-semantic "God created the world"

# Test source search
python kjv_cli.py qdrant search-by-source P
```

## 📊 What Qdrant Provides

### Vector Embeddings
- **Semantic Search**: Find verses by meaning, not just exact text
- **Similarity Matching**: Discover related verses across books
- **Context Understanding**: Search for concepts and themes

### Advanced Filtering
- **Source Filtering**: Find verses by J, E, P, R sources
- **Book Filtering**: Search within specific books
- **Multi-source Detection**: Find verses with multiple sources

### Rich Metadata
- **Complete Verse Data**: All source information preserved
- **Source Analysis**: Primary sources, percentages, sequences
- **Redaction Indicators**: Editorial complexity flags

## 🔧 Qdrant Commands

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
```

#### Delete Collection
```bash
# Delete collection (use with caution)
python kjv_cli.py qdrant delete --force
```

### Search Commands

#### Semantic Search
```bash
# Basic semantic search
python kjv_cli.py qdrant search-semantic "God created"

# Search with limit
python kjv_cli.py qdrant search-semantic "creation story" --limit 20

# Search within specific book
python kjv_cli.py qdrant search-semantic "God said" --book Genesis
```

#### Source-based Search
```bash
# Find verses by source
python kjv_cli.py qdrant search-by-source P
python kjv_cli.py qdrant search-by-source J --limit 15

# Find multi-source verses
python kjv_cli.py qdrant search-by-source "P;J"
```

## 🎯 Search Examples

### Theological Concepts
```bash
# Creation themes
python kjv_cli.py qdrant search-semantic "beginning of creation"

# Divine commands
python kjv_cli.py qdrant search-semantic "God commanded"

# Covenant themes
python kjv_cli.py qdrant search-semantic "covenant with God"

# Prophetic messages
python kjv_cli.py qdrant search-semantic "prophet spoke"
```

### Source Analysis
```bash
# Priestly source content
python kjv_cli.py qdrant search-by-source P --limit 10

# Jahwist narratives
python kjv_cli.py qdrant search-by-source J --limit 10

# Elohist material
python kjv_cli.py qdrant search-by-source E --limit 10

# Redactor additions
python kjv_cli.py qdrant search-by-source R --limit 10
```

### Cross-book Analysis
```bash
# Creation accounts across books
python kjv_cli.py qdrant search-semantic "creation" --limit 20

# Law and commandments
python kjv_cli.py qdrant search-semantic "commandments law"

# Narrative themes
python kjv_cli.py qdrant search-semantic "story narrative"
```

## 🔍 Advanced Search Strategies

### Combining Semantic and Source Search
```bash
# Find Priestly creation accounts
python kjv_cli.py qdrant search-semantic "creation" --book Genesis
# Then filter results for P source in your analysis
```

### Multi-concept Search
```bash
# Search for multiple related concepts
python kjv_cli.py qdrant search-semantic "God blessing promise"
```

### Contextual Search
```bash
# Search for specific narrative contexts
python kjv_cli.py qdrant search-semantic "garden of Eden"
python kjv_cli.py qdrant search-semantic "wilderness journey"
```

## 📈 Data Structure in Qdrant

### Vector Embeddings
- **Model**: `all-MiniLM-L6-v2`
- **Dimension**: 384
- **Distance**: Cosine similarity
- **Text**: `{reference}: {full_text}`

### Metadata Fields
```json
{
  "book": "Genesis",
  "chapter": 1,
  "verse": 1,
  "canonical_reference": "Genesis 1:1",
  "full_text": "In the beginning God created...",
  "sources": "P",
  "source_count": 1,
  "primary_source": "P",
  "word_count": 10,
  "source_sequence": "P",
  "source_percentages": "J:0.0;E:0.0;P:100.0;R:0.0",
  "redaction_indicators": "none",
  "text_J": "",
  "text_E": "",
  "text_P": "In the beginning God created...",
  "text_R": "",
  "source_confidence": "high",
  "is_multi_source": false,
  "timestamp": "2024-01-01T12:00:00"
}
```

## 🚨 Troubleshooting

### Common Issues

#### Connection Errors
```bash
# Check if Qdrant is accessible
curl https://6ee24530-ebe8-4553-b5db-f554e567969c.us-east4-0.gcp.cloud.qdrant.io/collections
```

#### Missing Dependencies
```bash
# Install required packages
pip install qdrant-client sentence-transformers numpy
```

#### Collection Not Found
```bash
# Recreate collection
python kjv_cli.py qdrant setup --force
```

#### Upload Failures
```bash
# Check if CSV files exist
python kjv_cli.py list-books

# Re-run pipeline if needed
python kjv_pipeline.py
```

### Performance Tips

#### Large Datasets
- Upload books individually for better progress tracking
- Use batch processing for large collections
- Monitor memory usage during embedding generation

#### Search Optimization
- Use specific book filters to narrow search scope
- Limit results to reduce response time
- Combine semantic and source filters for precision

## 🔬 Research Applications

### Biblical Studies
- **Source Criticism**: Analyze J, E, P, R distributions
- **Thematic Analysis**: Find related concepts across books
- **Redaction Analysis**: Study editorial additions

### LLM Training
- **Retrieval-Augmented Generation**: Use Qdrant for context retrieval
- **Fine-tuning Data**: Generate training examples from search results
- **Evaluation**: Test model understanding of biblical concepts

### Digital Humanities
- **Text Mining**: Discover patterns in biblical text
- **Comparative Analysis**: Study differences between sources
- **Historical Research**: Trace development of biblical traditions

## 📊 Monitoring and Analytics

### Collection Health
```bash
# Regular health checks
python kjv_cli.py qdrant stats

# Monitor collection size
python kjv_cli.py qdrant stats | grep "Total Points"
```

### Search Analytics
- Track popular search queries
- Monitor search performance
- Analyze user patterns

## 🔐 Security and Access

### API Key Management
- Store API keys securely
- Rotate keys regularly
- Monitor usage patterns

### Data Privacy
- Qdrant data is encrypted in transit
- Access is controlled via API keys
- No personal data is stored

## 🎯 Best Practices

### Data Management
1. **Regular Backups**: Export data periodically
2. **Version Control**: Track collection changes
3. **Testing**: Validate search results

### Search Optimization
1. **Specific Queries**: Use precise search terms
2. **Filtering**: Combine semantic and metadata filters
3. **Iterative Refinement**: Refine searches based on results

### Performance
1. **Batch Operations**: Upload data in batches
2. **Caching**: Cache frequently used embeddings
3. **Monitoring**: Track response times and errors

## 📚 Additional Resources

### Qdrant Documentation
- [Qdrant Python Client](https://qdrant.tech/documentation/guides/python/)
- [Vector Similarity Search](https://qdrant.tech/documentation/concepts/vector_similarity/)
- [Filtering and Payload](https://qdrant.tech/documentation/concepts/filtering/)

### Sentence Transformers
- [Model Documentation](https://www.sbert.net/)
- [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [Embedding Generation](https://www.sbert.net/examples/applications/computing-embeddings/README.html)

### Biblical Studies
- [Documentary Hypothesis](https://en.wikipedia.org/wiki/Documentary_hypothesis)
- [Source Criticism](https://en.wikipedia.org/wiki/Source_criticism)
- [Biblical Textual Criticism](https://en.wikipedia.org/wiki/Biblical_textual_criticism)

---

Your KJV sources data is now ready for advanced semantic search and analysis in Qdrant! 🎉 