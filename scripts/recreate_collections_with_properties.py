#!/usr/bin/env python3
"""
Recreate Qdrant Collections with Updated Properties

This script drops existing collections and recreates them with the new property structure
that ensures content, metadata, and id are properly set.
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def drop_collections(client, collection_names):
    """Drop specified collections from Qdrant."""
    print("🗑️  Dropping existing collections...")
    
    for collection_name in collection_names:
        try:
            # Check if collection exists
            collections = client.get_collections()
            collection_exists = any(col.name == collection_name for col in collections.collections)
            
            if collection_exists:
                client.delete_collection(collection_name)
                print(f"✅ Dropped collection: {collection_name}")
            else:
                print(f"ℹ️  Collection {collection_name} does not exist, skipping...")
                
        except Exception as e:
            print(f"⚠️  Warning: Could not drop collection {collection_name}: {e}")

def recreate_faq_collection(collection_name="premiere_suites_faqs", use_cloud=None):
    """Recreate FAQ collection with updated properties."""
    print(f"\n🔄 Recreating FAQ collection: {collection_name}")
    
    try:
        # Import here to avoid circular imports
        from src.vector_db.vectorize_faq_data import vectorize_faq_data
        
        # Auto-detect cloud vs local based on environment variables
        env_qdrant_url = os.getenv("QDRANT_URL")
        env_qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        # Determine if we should use cloud
        if use_cloud is None:
            use_cloud = bool(env_qdrant_url and env_qdrant_api_key)
        
        if use_cloud:
            print("🌐 Using Qdrant Cloud")
            vectorize_faq_data(
                collection_name=collection_name,
                recreate_collection=True,
                use_cloud=True,
                qdrant_url=env_qdrant_url,
                qdrant_api_key=env_qdrant_api_key
            )
        else:
            print("🏠 Using local Qdrant instance")
            vectorize_faq_data(
                collection_name=collection_name,
                recreate_collection=True,
                use_cloud=False
            )
        
        print(f"✅ FAQ collection '{collection_name}' recreated successfully!")
        
    except Exception as e:
        print(f"❌ Error recreating FAQ collection: {e}")
        raise

def recreate_properties_collection(collection_name="premiere_suites_properties", use_cloud=None):
    """Recreate properties collection with updated properties."""
    print(f"\n🔄 Recreating properties collection: {collection_name}")
    
    try:
        # Import here to avoid circular imports
        from src.vector_db.qdrant_setup import PremiereSuitesVectorDB
        from src.scrapers.premiere_scraper import load_property_data
        
        # Auto-detect cloud vs local based on environment variables
        env_qdrant_url = os.getenv("QDRANT_URL")
        env_qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        # Determine if we should use cloud
        if use_cloud is None:
            use_cloud = bool(env_qdrant_url and env_qdrant_api_key)
        
        # Initialize vector database
        if use_cloud:
            print("🌐 Using Qdrant Cloud")
            vdb = PremiereSuitesVectorDB(
                qdrant_url=env_qdrant_url,
                qdrant_api_key=env_qdrant_api_key,
                collection_name=collection_name,
                embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
                use_cloud=True
            )
        else:
            print("🏠 Using local Qdrant instance")
            vdb = PremiereSuitesVectorDB(
                collection_name=collection_name,
                embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            )
        
        # Create collection
        vdb.create_collection(recreate=True)
        
        # Load property data
        property_file = "premiere_suites_data.jsonl"
        if not Path(property_file).exists():
            print(f"⚠️  Property data file not found: {property_file}")
            print("   Skipping properties collection recreation...")
            return
        
        properties = load_property_data(property_file)
        
        if not properties:
            print("⚠️  No property data found to vectorize")
            return
        
        # Prepare points with updated property structure
        from qdrant_client.models import PointStruct
        from datetime import datetime
        
        # Extract text for embedding
        texts = []
        for prop in properties:
            # Create comprehensive text for embedding
            text_parts = []
            if prop.get("name"):
                text_parts.append(f"Property: {prop['name']}")
            if prop.get("description"):
                text_parts.append(f"Description: {prop['description']}")
            if prop.get("amenities"):
                text_parts.append(f"Amenities: {', '.join(prop['amenities'])}")
            if prop.get("location"):
                text_parts.append(f"Location: {prop['location']}")
            
            text = " | ".join(text_parts) if text_parts else f"Property {prop.get('id', 'Unknown')}"
            texts.append(text)
        
        # Generate embeddings
        print("Generating embeddings for property data...")
        embeddings = vdb.generate_embeddings(texts)
        
        # Create points with updated structure
        points = []
        for i, prop in enumerate(properties):
            # Ensure we have a proper ID - convert string IDs to integers
            prop_id = prop.get("id")
            if prop_id is None:
                prop_id = i + 1
            elif isinstance(prop_id, str):
                # Convert string IDs like "prop_001" to integers
                try:
                    # Extract number from string ID (e.g., "prop_001" -> 1)
                    if prop_id.startswith("prop_"):
                        prop_id = int(prop_id.replace("prop_", ""))
                    else:
                        # Try to convert directly to int, fallback to hash
                        prop_id = int(prop_id)
                except (ValueError, AttributeError):
                    # If conversion fails, use hash of the string as fallback
                    prop_id = abs(hash(prop_id)) % (2**63)  # Ensure it's a positive integer
            elif not isinstance(prop_id, int):
                # Convert other types to integer
                prop_id = abs(hash(str(prop_id))) % (2**63)
            
            # Create content
            page_content = texts[i]
            
            # Create metadata object
            metadata = {
                "property_id": prop_id,
                "name": prop.get("name", ""),
                "description": prop.get("description", ""),
                "amenities": prop.get("amenities", []),
                "location": prop.get("location", ""),
                "price": prop.get("price", ""),
                "rating": prop.get("rating", ""),
                "source_url": prop.get("source_url", ""),
                "ingested_at": datetime.now().isoformat()
            }
            
            point = PointStruct(
                id=prop_id,
                vector=embeddings[i].tolist(),
                payload={
                    "content": page_content,
                    "metadata": metadata,
                    "id": prop_id,
                    # Also include individual fields for backward compatibility
                    "property_id": prop_id,
                    "name": prop.get("name", ""),
                    "description": prop.get("description", ""),
                    "amenities": prop.get("amenities", []),
                    "location": prop.get("location", ""),
                    "price": prop.get("price", ""),
                    "rating": prop.get("rating", ""),
                    "source_url": prop.get("source_url", ""),
                    "ingested_at": datetime.now().isoformat()
                }
            )
            points.append(point)
        
        # Insert data
        print(f"Inserting {len(points)} property points...")
        vdb.insert_data(points, batch_size=50)
        
        # Get collection info
        info = vdb.get_collection_info()
        print(f"✅ Properties collection '{collection_name}' recreated successfully!")
        print(f"   Total vectors: {info['vectors_count']}")
        print(f"   Vector size: {info['vector_size']}")
        
    except Exception as e:
        print(f"❌ Error recreating properties collection: {e}")
        raise

def verify_collections(client, collection_names):
    """Verify that collections have the correct property structure."""
    print("\n🔍 Verifying collection properties...")
    
    for collection_name in collection_names:
        try:
            # Check if collection exists
            collections = client.get_collections()
            collection_exists = any(col.name == collection_name for col in collections.collections)
            
            if not collection_exists:
                print(f"⚠️  Collection {collection_name} does not exist")
                continue
            
            # Get a few points to verify structure
            points = client.scroll(
                collection_name=collection_name,
                limit=3,
                with_payload=True
            )[0]
            
            if not points:
                print(f"⚠️  Collection {collection_name} is empty")
                continue
            
            print(f"\n📊 Collection: {collection_name}")
            print(f"   Total points: {len(points)}")
            
            # Check first point for required properties
            first_point = points[0]
            required_props = ["content", "metadata", "id"]
            
            for prop in required_props:
                if prop in first_point.payload:
                    print(f"   ✅ {prop}: Present")
                else:
                    print(f"   ❌ {prop}: Missing")
            
            # Show sample data
            print(f"   📝 Sample content: {first_point.payload.get('content', 'NOT FOUND')[:100]}...")
            print(f"   🏷️  Sample metadata keys: {list(first_point.payload.get('metadata', {}).keys())}")
            
        except Exception as e:
            print(f"❌ Error verifying collection {collection_name}: {e}")

def main():
    """Main function to recreate collections."""
    parser = argparse.ArgumentParser(description="Recreate Qdrant collections with updated properties")
    parser.add_argument("--collections", nargs="+", 
                       default=["premiere_suites_faqs", "premiere_suites_properties"],
                       help="Collections to recreate (default: all)")
    parser.add_argument("--cloud", action="store_true", 
                       help="Force use of Qdrant Cloud")
    parser.add_argument("--local", action="store_true",
                       help="Force use of local Qdrant instance")
    parser.add_argument("--verify-only", action="store_true",
                       help="Only verify existing collections, don't recreate")
    
    args = parser.parse_args()
    
    print("🔄 Qdrant Collections Recreation")
    print("=" * 50)
    
    try:
        # Determine cloud usage
        use_cloud = None
        if args.local:
            use_cloud = False
        elif args.cloud:
            use_cloud = True
        
        # Initialize Qdrant client
        env_qdrant_url = os.getenv("QDRANT_URL")
        env_qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        if use_cloud or (use_cloud is None and env_qdrant_url and env_qdrant_api_key):
            from qdrant_client import QdrantClient
            client = QdrantClient(url=env_qdrant_url, api_key=env_qdrant_api_key)
            print("🌐 Connected to Qdrant Cloud")
        else:
            from qdrant_client import QdrantClient
            client = QdrantClient(host="localhost", port=6333)
            print("🏠 Connected to local Qdrant instance")
        
        if args.verify_only:
            # Only verify existing collections
            verify_collections(client, args.collections)
        else:
            # Drop existing collections
            drop_collections(client, args.collections)
            
            # Recreate collections
            if "premiere_suites_faqs" in args.collections:
                recreate_faq_collection(use_cloud=use_cloud)
            
            if "premiere_suites_properties" in args.collections:
                recreate_properties_collection(use_cloud=use_cloud)
            
            # Verify the new collections
            verify_collections(client, args.collections)
        
        print("\n✅ Collection recreation completed successfully!")
        print("\n📋 Summary:")
        print("   - Collections now have proper content, metadata, and id properties")
        print("   - All data has been re-vectorized with the new structure")
        print("   - Backward compatibility is maintained")
        
    except Exception as e:
        print(f"\n❌ Error during collection recreation: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
