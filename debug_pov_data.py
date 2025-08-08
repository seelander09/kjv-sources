#!/usr/bin/env python3
"""
Debug script to check POV data in Qdrant
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from kjv_sources.qdrant_client import create_qdrant_client

def debug_pov_data():
    """Debug POV data in Qdrant"""
    print("🔍 Debugging POV data in Qdrant...")
    
    try:
        client = create_qdrant_client()
        
        # Get a few sample points to see what's actually stored
        print("\n📊 Checking sample data...")
        
        # Scroll through a few points to see the actual data structure
        scroll_result = client.client.scroll(
            collection_name=client.collection_name,
            limit=5,
            with_payload=True
        )
        
        for i, point in enumerate(scroll_result[0]):
            print(f"\n--- Point {i+1} ---")
            payload = point.payload
            
            # Check what POV fields exist
            pov_fields = [k for k in payload.keys() if k.startswith('pov_')]
            print(f"POV fields found: {pov_fields}")
            
            # Show some key POV values
            for field in ['pov_style', 'pov_perspective', 'pov_purpose', 'pov_complexity']:
                if field in payload:
                    print(f"  {field}: {payload[field]}")
                else:
                    print(f"  {field}: NOT FOUND")
            
            # Show sources field
            if 'sources' in payload:
                print(f"  sources: {payload['sources']}")
            else:
                print(f"  sources: NOT FOUND")
        
        # Try a simple search without filters to see if basic search works
        print("\n🧪 Testing basic search...")
        try:
            basic_results = client.client.search(
                collection_name=client.collection_name,
                query_vector=client.get_embedding("creation"),
                limit=3
            )
            print(f"✅ Basic search works: {len(basic_results)} results")
        except Exception as e:
            print(f"❌ Basic search failed: {e}")
        
        # Check collection info
        print("\n📋 Collection info...")
        try:
            collection_info = client.client.get_collection(client.collection_name)
            print(f"Collection: {collection_info.name}")
            print(f"Status: {collection_info.status}")
            print(f"Points count: {collection_info.points_count}")
        except Exception as e:
            print(f"❌ Could not get collection info: {e}")
        
    except Exception as e:
        print(f"❌ Error debugging: {e}")

if __name__ == "__main__":
    debug_pov_data()
