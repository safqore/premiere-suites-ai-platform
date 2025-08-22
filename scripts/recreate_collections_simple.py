#!/usr/bin/env python3
"""
Simple Qdrant Collections Recreation Script

This script deletes and recreates both property and FAQ collections.
It can work with both local Qdrant (via Docker) and Qdrant Cloud.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_qdrant_connection():
    """Check if Qdrant is accessible (local or cloud)."""
    try:
        from qdrant_client import QdrantClient
        
        # Check for cloud credentials
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        if qdrant_url and qdrant_api_key:
            print("☁️  Using Qdrant Cloud")
            client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
            client.get_collections()
            return client, True
        else:
            print("🏠 Attempting to connect to local Qdrant...")
            client = QdrantClient(host="localhost", port=6333)
            client.get_collections()
            return client, False
    except Exception as e:
        print(f"❌ Cannot connect to Qdrant: {e}")
        print("\n💡 To fix this:")
        print("   1. For local Qdrant: Start Docker and run 'docker-compose -f config/docker-compose.yml up -d'")
        print("   2. For Qdrant Cloud: Set QDRANT_URL and QDRANT_API_KEY environment variables")
        return None, None

def load_jsonl_data(file_path: str) -> List[Dict[str, Any]]:
    """Load data from JSONL file."""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        return data
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        return []

def filter_data_by_type(data: List[Dict[str, Any]], data_type: str) -> List[Dict[str, Any]]:
    """Filter data by type (faq or property)."""
    return [item for item in data if item.get("type") == data_type]

def delete_collection(client, collection_name: str):
    """Delete a collection if it exists."""
    try:
        collections = client.get_collections()
        collection_exists = any(col.name == collection_name for col in collections.collections)
        
        if collection_exists:
            client.delete_collection(collection_name)
            print(f"✅ Deleted collection: {collection_name}")
        else:
            print(f"ℹ️  Collection {collection_name} does not exist")
    except Exception as e:
        print(f"⚠️  Warning: Could not delete collection {collection_name}: {e}")

def create_collection(client, collection_name: str, vector_size: int = 384):
    """Create a new collection."""
    try:
        from qdrant_client.models import Distance, VectorParams
        
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
        print(f"✅ Created collection: {collection_name}")
    except Exception as e:
        print(f"❌ Error creating collection {collection_name}: {e}")
        raise

def upload_faq_data(client, collection_name: str, faq_data: List[Dict[str, Any]]):
    """Upload FAQ data to collection."""
    try:
        from qdrant_client.models import PointStruct
        from sentence_transformers import SentenceTransformer
        import numpy as np
        
        # Load embedding model
        print("🔤 Loading embedding model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Prepare points
        points = []
        for i, faq in enumerate(faq_data):
            # Create text for embedding
            text = f"Q: {faq.get('question', '')} A: {faq.get('answer', '')}"
            
            # Generate embedding
            embedding = model.encode(text)
            
            # Create point
            point = PointStruct(
                id=i + 1,
                vector=embedding.tolist(),
                payload={
                    "id": faq.get("id", f"faq_{i+1}"),
                    "question": faq.get("question", ""),
                    "answer": faq.get("answer", ""),
                    "category": faq.get("category", ""),
                    "tags": faq.get("tags", []),
                    "source_url": faq.get("source_url", ""),
                    "pageContent": faq.get("pageContent", text)
                }
            )
            points.append(point)
        
        # Upload in batches
        batch_size = 50
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            client.upsert(collection_name=collection_name, points=batch)
            print(f"📤 Uploaded batch {i//batch_size + 1}/{(len(points) + batch_size - 1)//batch_size}")
        
        print(f"✅ Uploaded {len(points)} FAQ entries to {collection_name}")
        
    except Exception as e:
        print(f"❌ Error uploading FAQ data: {e}")
        raise

def upload_property_data(client, collection_name: str, property_data: List[Dict[str, Any]]):
    """Upload property data to collection."""
    try:
        from qdrant_client.models import PointStruct
        from sentence_transformers import SentenceTransformer
        import numpy as np
        
        # Load embedding model
        print("🔤 Loading embedding model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Prepare points
        points = []
        for i, prop in enumerate(property_data):
            # Create text for embedding
            text_parts = []
            if prop.get("property_name"):
                text_parts.append(f"Property: {prop['property_name']}")
            if prop.get("description"):
                text_parts.append(f"Description: {prop['description']}")
            if prop.get("amenities"):
                text_parts.append(f"Amenities: {', '.join(prop['amenities'])}")
            if prop.get("city"):
                text_parts.append(f"Location: {prop['city']}")
            
            text = " | ".join(text_parts) if text_parts else f"Property {prop.get('id', 'Unknown')}"
            
            # Generate embedding
            embedding = model.encode(text)
            
            # Create point
            point = PointStruct(
                id=i + 1,
                vector=embedding.tolist(),
                payload={
                    "id": prop.get("id", f"prop_{i+1}"),
                    "property_name": prop.get("property_name", ""),
                    "city": prop.get("city", ""),
                    "rating": prop.get("rating", 0.0),
                    "room_type": prop.get("room_type", ""),
                    "amenities": prop.get("amenities", []),
                    "description": prop.get("description", ""),
                    "pet_friendly": prop.get("pet_friendly", False),
                    "bedrooms": prop.get("bedrooms", 0),
                    "building_type": prop.get("building_type", ""),
                    "suite_features": prop.get("suite_features", []),
                    "source_url": prop.get("source_url", ""),
                    "image_url": prop.get("image_url", ""),
                    "pageContent": prop.get("pageContent", text)
                }
            )
            points.append(point)
        
        # Upload in batches
        batch_size = 50
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            client.upsert(collection_name=collection_name, points=batch)
            print(f"📤 Uploaded batch {i//batch_size + 1}/{(len(points) + batch_size - 1)//batch_size}")
        
        print(f"✅ Uploaded {len(points)} property entries to {collection_name}")
        
    except Exception as e:
        print(f"❌ Error uploading property data: {e}")
        raise

def get_collection_info(client, collection_name: str):
    """Get collection information."""
    try:
        info = client.get_collection(collection_name)
        print(f"\n📊 Collection: {collection_name}")
        print(f"   Vectors count: {info.vectors_count}")
        print(f"   Vector size: {info.config.params.vectors.size}")
        print(f"   Distance: {info.config.params.vectors.distance}")
    except Exception as e:
        print(f"❌ Error getting collection info: {e}")

def main():
    """Main function."""
    print("🔄 Qdrant Collections Recreation")
    print("=" * 50)
    
    # Check Qdrant connection
    client, is_cloud = check_qdrant_connection()
    if not client:
        return 1
    
    # Check data files
    faq_file = "data/processed/premiere_suites_faq_data.jsonl"
    property_file = "data/processed/premiere_suites_data.jsonl"
    
    if not Path(faq_file).exists():
        print(f"❌ FAQ data file not found: {faq_file}")
        return 1
    
    if not Path(property_file).exists():
        print(f"❌ Property data file not found: {property_file}")
        return 1
    
    print(f"✅ Found FAQ data: {faq_file}")
    print(f"✅ Found property data: {property_file}")
    
    # Load data
    print("\n📄 Loading data files...")
    faq_data = load_jsonl_data(faq_file)
    property_data = load_jsonl_data(property_file)
    
    # Filter data by type
    faqs = filter_data_by_type(faq_data, "faq")
    properties = filter_data_by_type(property_data, "property")
    
    print(f"📊 Loaded {len(faqs)} FAQ entries")
    print(f"📊 Loaded {len(properties)} property entries")
    
    if not faqs:
        print("❌ No FAQ data found")
        return 1
    
    if not properties:
        print("❌ No property data found")
        return 1
    
    # Collection names
    faq_collection = "premiere_suites_faqs"
    property_collection = "premiere_suites_properties"
    
    try:
        # Delete existing collections
        print(f"\n🗑️  Deleting existing collections...")
        delete_collection(client, faq_collection)
        delete_collection(client, property_collection)
        
        # Create new collections
        print(f"\n📦 Creating new collections...")
        create_collection(client, faq_collection)
        create_collection(client, property_collection)
        
        # Upload FAQ data
        print(f"\n📤 Uploading FAQ data...")
        upload_faq_data(client, faq_collection, faqs)
        
        # Upload property data
        print(f"\n📤 Uploading property data...")
        upload_property_data(client, property_collection, properties)
        
        # Get collection info
        print(f"\n📊 Collection Information:")
        get_collection_info(client, faq_collection)
        get_collection_info(client, property_collection)
        
        print(f"\n🎉 Collections recreated successfully!")
        print(f"   FAQ Collection: {faq_collection}")
        print(f"   Property Collection: {property_collection}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during recreation: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
