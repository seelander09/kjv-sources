#!/usr/bin/env python3
"""
Test script to verify LightRAG setup with KJV sources data
"""

import os
import json
import pandas as pd
from pathlib import Path

def test_data_structure():
    """Test that the data structure is compatible with LightRAG"""
    print("🔍 Testing KJV Sources Data Structure for LightRAG")
    print("=" * 60)
    
    output_dir = Path("output")
    if not output_dir.exists():
        print("❌ Output directory not found")
        return False
    
    books = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]
    total_verses = 0
    total_training = 0
    total_markdown = 0
    
    for book in books:
        book_dir = output_dir / book
        if not book_dir.exists():
            print(f"⚠️  {book} directory not found")
            continue
        
        print(f"\n📖 {book}:")
        
        # Test CSV data
        csv_path = book_dir / f"{book}.csv"
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                verse_count = len(df)
                total_verses += verse_count
                print(f"  ✅ CSV: {verse_count} verses")
                
                # Check required columns
                required_cols = ['canonical_reference', 'full_text', 'sources', 'primary_source']
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    print(f"  ⚠️  Missing columns: {missing_cols}")
                else:
                    print(f"  ✅ All required columns present")
                    
            except Exception as e:
                print(f"  ❌ CSV error: {e}")
        else:
            print(f"  ❌ CSV file not found")
        
        # Test JSONL files
        jsonl_types = ["training", "classification", "sequence", "analysis"]
        for jsonl_type in jsonl_types:
            jsonl_path = book_dir / f"{book}_{jsonl_type}.jsonl"
            if jsonl_path.exists():
                try:
                    with open(jsonl_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        count = len(lines)
                        total_training += count
                        print(f"  ✅ {jsonl_type}: {count} records")
                        
                        # Test JSON parsing
                        if lines:
                            json.loads(lines[0].strip())
                            print(f"  ✅ {jsonl_type}: Valid JSON format")
                            
                except Exception as e:
                    print(f"  ❌ {jsonl_type} error: {e}")
            else:
                print(f"  ⚠️  {jsonl_type}: File not found")
        
        # Test Markdown
        md_path = book_dir / f"{book}.md"
        if md_path.exists():
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        total_markdown += 1
                        print(f"  ✅ Markdown: {len(content)} characters")
                    else:
                        print(f"  ⚠️  Markdown: Empty file")
            except Exception as e:
                print(f"  ❌ Markdown error: {e}")
        else:
            print(f"  ⚠️  Markdown: File not found")
    
    print(f"\n📊 Summary:")
    print(f"  Total verses: {total_verses}")
    print(f"  Total training records: {total_training}")
    print(f"  Total markdown files: {total_markdown}")
    
    if total_verses > 0:
        print(f"\n✅ Data structure is compatible with LightRAG!")
        print(f"   Ready for ingestion pipeline.")
        return True
    else:
        print(f"\n❌ No compatible data found.")
        return False

def test_entity_relations():
    """Test entity-relation structure"""
    print(f"\n🔗 Testing Entity-Relation Structure")
    print("-" * 40)
    
    # Define expected entities
    source_entities = {
        "J": {"name": "Jahwist", "description": "Yahwist source", "color": "blue"},
        "E": {"name": "Elohist", "description": "Elohist source", "color": "cyan"},
        "P": {"name": "Priestly", "description": "Priestly source", "color": "yellow"},
        "R": {"name": "Redactor", "description": "Redactor source", "color": "red"}
    }
    
    book_entities = {
        "Genesis": {"name": "Genesis", "chapters": 50, "type": "narrative"},
        "Exodus": {"name": "Exodus", "chapters": 40, "type": "narrative"},
        "Leviticus": {"name": "Leviticus", "chapters": 27, "type": "legal"},
        "Numbers": {"name": "Numbers", "chapters": 36, "type": "narrative"},
        "Deuteronomy": {"name": "Deuteronomy", "chapters": 34, "type": "legal"}
    }
    
    relation_types = {
        "contains_source": "verse -> source",
        "belongs_to_book": "verse -> book",
        "has_chapter": "verse -> chapter",
        "multi_source": "verse -> multiple_sources",
        "redaction": "verse -> redaction_indicators"
    }
    
    relations = {
        "source_entities": source_entities,
        "book_entities": book_entities,
        "relation_types": relation_types
    }
    
    # Test entity structure
    print(f"✅ Source entities: {len(source_entities)}")
    for source, info in source_entities.items():
        print(f"   {source}: {info['name']} ({info['description']})")
    
    print(f"\n✅ Book entities: {len(book_entities)}")
    for book, info in book_entities.items():
        print(f"   {book}: {info['chapters']} chapters ({info['type']})")
    
    print(f"\n✅ Relation types: {len(relation_types)}")
    for rel_type, description in relation_types.items():
        print(f"   {rel_type}: {description}")
    
    # Save test entity relations
    lightrag_dir = Path("lightrag_data")
    lightrag_dir.mkdir(exist_ok=True)
    
    relations_path = lightrag_dir / "entity_relations.json"
    with open(relations_path, 'w', encoding='utf-8') as f:
        json.dump(relations, f, indent=2)
    
    print(f"\n✅ Entity relations saved to: {relations_path}")
    return True

def test_lightrag_imports():
    """Test LightRAG imports"""
    print(f"\n🧪 Testing LightRAG Imports")
    print("-" * 30)
    
    try:
        from lightrag import LightRAG
        print("✅ LightRAG import successful")
    except ImportError:
        print("❌ LightRAG not available")
        print("   Install with: pip install lightrag")
        return False
    
    try:
        from lightrag.retrievers import HybridRetriever, DenseRetriever, SparseRetriever
        print("✅ Retriever imports successful")
    except ImportError:
        print("❌ Retriever imports failed")
        return False
    
    try:
        from lightrag.retrievers import Reranker
        print("✅ Reranker import successful")
    except ImportError:
        print("❌ Reranker import failed")
        return False
    
    try:
        from lightrag.ingest import Document
        print("✅ Document import successful")
    except ImportError:
        print("❌ Document import failed")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 KJV Sources LightRAG Setup Test")
    print("=" * 60)
    
    # Test data structure
    data_ok = test_data_structure()
    
    # Test entity relations
    entities_ok = test_entity_relations()
    
    # Test LightRAG imports
    lightrag_ok = test_lightrag_imports()
    
    print(f"\n🎯 Test Results:")
    print(f"   Data Structure: {'✅' if data_ok else '❌'}")
    print(f"   Entity Relations: {'✅' if entities_ok else '❌'}")
    print(f"   LightRAG Imports: {'✅' if lightrag_ok else '❌'}")
    
    if data_ok and entities_ok:
        print(f"\n✅ Ready for LightRAG ingestion!")
        print(f"   Run: python lightrag_ingestion.py")
        
        if lightrag_ok:
            print(f"   Then: python lightrag_query.py")
        else:
            print(f"   Install LightRAG first: pip install lightrag")
    else:
        print(f"\n❌ Setup issues detected. Check the output above.")
    
    print(f"\n📁 Files created:")
    print(f"   lightrag_data/entity_relations.json")

if __name__ == "__main__":
    main() 