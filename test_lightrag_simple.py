#!/usr/bin/env python3
"""
Simple LightRAG test script
"""

def test_lightrag():
    """Test LightRAG installation"""
    print("🧪 Testing LightRAG Installation")
    print("=" * 40)
    
    try:
        import lightrag
        print(f"✅ LightRAG imported successfully")
        print(f"   Version: {lightrag.__version__}")
    except ImportError as e:
        print(f"❌ LightRAG import failed: {e}")
        return False
    
    try:
        from lightrag import LightRAG
        print("✅ LightRAG class imported")
    except ImportError as e:
        print(f"❌ LightRAG class import failed: {e}")
        return False
    
    try:
        from lightrag.retrievers import HybridRetriever, DenseRetriever, SparseRetriever
        print("✅ Retriever classes imported")
    except ImportError as e:
        print(f"❌ Retriever imports failed: {e}")
        return False
    
    try:
        from lightrag.retrievers import Reranker
        print("✅ Reranker imported")
    except ImportError as e:
        print(f"❌ Reranker import failed: {e}")
        return False
    
    try:
        from lightrag.ingest import Document
        print("✅ Document class imported")
    except ImportError as e:
        print(f"❌ Document import failed: {e}")
        return False
    
    print("\n🎉 All LightRAG imports successful!")
    return True

if __name__ == "__main__":
    test_lightrag() 