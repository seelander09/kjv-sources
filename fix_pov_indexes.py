#!/usr/bin/env python3
"""
Script to manually create missing POV field indexes
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from kjv_sources.qdrant_client import create_qdrant_client

def fix_pov_indexes():
    """Create missing POV field indexes"""
    print("🔧 Fixing POV field indexes...")
    
    try:
        client = create_qdrant_client()
        
        # Fields that need indexes (these are the ones causing errors)
        missing_fields = [
            "pov_style", "pov_perspective", "pov_purpose", "pov_complexity",
            "pov_audience", "pov_emotion", "pov_authority", "pov_temporal",
            "pov_spatial", "pov_social", "pov_theological", "sources"
        ]
        
        for field in missing_fields:
            try:
                print(f"Creating index for {field}...")
                client.client.create_payload_index(
                    collection_name=client.collection_name,
                    field_name=field,
                    field_schema="keyword"
                )
                print(f"✅ Created index for {field}")
            except Exception as e:
                print(f"⚠️ Could not create index for {field}: {e}")
        
        print("🎉 POV index fix completed!")
        
        # Test a few searches
        print("\n🧪 Testing fixed searches...")
        
        try:
            style_results = client.search_by_pov_style("narrative_anthropomorphic", limit=3)
            print(f"✅ POV style search: {len(style_results)} results")
        except Exception as e:
            print(f"❌ POV style search still failing: {e}")
        
        try:
            perspective_results = client.search_by_pov_perspective("intimate_personal", limit=3)
            print(f"✅ POV perspective search: {len(perspective_results)} results")
        except Exception as e:
            print(f"❌ POV perspective search still failing: {e}")
        
        try:
            comparison_results = client.search_pov_comparison("J", "P", limit=3)
            print(f"✅ POV comparison search: {len(comparison_results)} results")
        except Exception as e:
            print(f"❌ POV comparison search still failing: {e}")
        
    except Exception as e:
        print(f"❌ Error fixing indexes: {e}")

if __name__ == "__main__":
    fix_pov_indexes()
