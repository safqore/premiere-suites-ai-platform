#!/usr/bin/env python3
"""
Recreate Collections with LangChain Integration

This script deletes and recreates both property and FAQ collections using LangChain.
It will load data from existing JSONL files and create fresh collections with LangChain.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from vector_db.langchain_qdrant_integration import LangChainQdrantIntegration
from vector_db.langchain_faq_integration import LangChainFAQIntegration

def check_data_files():
    """Check if required data files exist."""
    print("📄 Checking data files...")
    
    property_file = Path("data/processed/premiere_suites_data.jsonl")
    faq_file = Path("data/processed/premiere_suites_faq_data.jsonl")
    
    files_exist = {
        "properties": property_file.exists(),
        "faqs": faq_file.exists()
    }
    
    if files_exist["properties"]:
        print(f"✅ Property data found: {property_file}")
    else:
        print(f"❌ Property data missing: {property_file}")
    
    if files_exist["faqs"]:
        print(f"✅ FAQ data found: {faq_file}")
    else:
        print(f"❌ FAQ data missing: {faq_file}")
    
    return files_exist

def count_data_entries(file_path: str) -> int:
    """Count the number of entries in a JSONL file."""
    count = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    count += 1
        return count
    except Exception as e:
        print(f"Error counting entries in {file_path}: {e}")
        return 0

def recreate_property_collection(use_cloud: bool = False):
    """Recreate the property collection using LangChain."""
    print("\n🏠 Recreating Property Collection with LangChain")
    print("=" * 60)
    
    try:
        # Initialize LangChain integration
        print("🔗 Initializing LangChain Property Integration...")
        integration = LangChainQdrantIntegration(
            collection_name="premiere_suites_properties",
            embedding_model="all-MiniLM-L6-v2",
            use_cloud=use_cloud
        )
        
        # Delete existing collection if it exists
        print("🗑️  Deleting existing collection...")
        try:
            integration.delete_collection()
            print("✅ Existing collection deleted")
        except Exception as e:
            print(f"ℹ️  No existing collection to delete: {e}")
        
        # Create new collection
        print("📦 Creating new collection...")
        integration.create_collection()
        print("✅ Collection created successfully")
        
        # Load property data
        property_file = "data/processed/premiere_suites_data.jsonl"
        if not Path(property_file).exists():
            print(f"❌ Property data file not found: {property_file}")
            return False
        
        print(f"📄 Loading property data from {property_file}...")
        documents = integration.load_documents_from_jsonl(property_file)
        
        if not documents:
            print("❌ No property documents found")
            return False
        
        print(f"✅ Loaded {len(documents)} property documents")
        
        # Add documents using LangChain
        print("📤 Adding documents to collection...")
        integration.add_documents(documents, batch_size=50)
        print("✅ Documents added successfully")
        
        # Get collection info
        info = integration.get_collection_info()
        print(f"\n📊 Collection Info:")
        print(f"   Name: {info['name']}")
        print(f"   Total vectors: {info['vectors_count']}")
        print(f"   Vector size: {info['vector_size']}")
        
        # Test search
        print("\n🔍 Testing property search...")
        results = integration.search_properties_langchain(
            query="luxury apartment with pool and gym",
            limit=3,
            min_rating=4.0
        )
        
        print(f"✅ Search test completed, found {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['property_name']} ({result['city']}) - Rating: {result['rating']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error recreating property collection: {e}")
        return False

def recreate_faq_collection(use_cloud: bool = False):
    """Recreate the FAQ collection using LangChain."""
    print("\n❓ Recreating FAQ Collection with LangChain")
    print("=" * 60)
    
    try:
        # Initialize LangChain integration
        print("🔗 Initializing LangChain FAQ Integration...")
        integration = LangChainFAQIntegration(
            collection_name="premiere_suites_faqs",
            embedding_model="all-MiniLM-L6-v2",
            use_cloud=use_cloud
        )
        
        # Delete existing collection if it exists
        print("🗑️  Deleting existing collection...")
        try:
            integration.delete_collection()
            print("✅ Existing collection deleted")
        except Exception as e:
            print(f"ℹ️  No existing collection to delete: {e}")
        
        # Create new collection
        print("📦 Creating new collection...")
        integration.create_collection()
        print("✅ Collection created successfully")
        
        # Load FAQ data
        faq_file = "data/processed/premiere_suites_faq_data.jsonl"
        if not Path(faq_file).exists():
            print(f"❌ FAQ data file not found: {faq_file}")
            return False
        
        print(f"📄 Loading FAQ data from {faq_file}...")
        documents = integration.load_faq_documents_from_jsonl(faq_file)
        
        if not documents:
            print("❌ No FAQ documents found")
            return False
        
        print(f"✅ Loaded {len(documents)} FAQ documents")
        
        # Add documents using LangChain
        print("📤 Adding documents to collection...")
        integration.add_faq_documents(documents, batch_size=50)
        print("✅ Documents added successfully")
        
        # Get collection info
        info = integration.get_collection_info()
        print(f"\n📊 Collection Info:")
        print(f"   Name: {info['name']}")
        print(f"   Total vectors: {info['vectors_count']}")
        print(f"   Vector size: {info['vector_size']}")
        
        # Get categories and tags
        categories = integration.get_faq_categories()
        tags = integration.get_faq_tags()
        print(f"\n📂 Categories: {', '.join(categories)}")
        print(f"🏷️  Tags: {', '.join(tags)}")
        
        # Test search
        print("\n🔍 Testing FAQ search...")
        results = integration.search_faqs_langchain(
            query="How do I book a reservation?",
            limit=3
        )
        
        print(f"✅ Search test completed, found {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['question']} - Category: {result['category']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error recreating FAQ collection: {e}")
        return False

def create_sample_data_if_missing():
    """Create sample data files if they don't exist."""
    print("\n📝 Creating sample data files if missing...")
    
    # Create sample property data
    property_file = Path("data/processed/premiere_suites_data.jsonl")
    if not property_file.exists():
        print("📄 Creating sample property data...")
        sample_properties = [
            {
                "type": "property",
                "id": "prop_001",
                "property_name": "Luxury Downtown Apartment",
                "city": "Toronto",
                "rating": 4.8,
                "room_type": "apartment",
                "amenities": ["pool", "gym", "concierge", "parking"],
                "description": "Luxury apartment with stunning city views, modern amenities, and 24/7 concierge service.",
                "pet_friendly": True,
                "bedrooms": 2,
                "building_type": "high-rise",
                "suite_features": ["balcony", "in-suite laundry", "gourmet kitchen"],
                "source_url": "https://example.com/property1",
                "image_url": "https://example.com/image1.jpg",
                "text_chunk": "Luxury apartment with stunning city views, modern amenities, and 24/7 concierge service. Features include pool, gym, concierge, and parking. Pet-friendly with 2 bedrooms and balcony.",
                "price_range": "$2,500-$3,500",
                "location_details": "Downtown Toronto"
            },
            {
                "type": "property",
                "id": "prop_002",
                "property_name": "Cozy Studio in Vancouver",
                "city": "Vancouver",
                "rating": 4.2,
                "room_type": "studio",
                "amenities": ["wifi", "kitchen", "laundry"],
                "description": "Cozy studio apartment perfect for students or young professionals.",
                "pet_friendly": True,
                "bedrooms": 1,
                "building_type": "apartment",
                "suite_features": ["kitchen", "laundry"],
                "source_url": "https://example.com/property2",
                "image_url": "https://example.com/image2.jpg",
                "text_chunk": "Cozy studio apartment perfect for students or young professionals. Features wifi, kitchen, and laundry facilities. Pet-friendly with 1 bedroom.",
                "price_range": "$1,200-$1,800",
                "location_details": "West End, Vancouver"
            }
        ]
        
        with open(property_file, 'w') as f:
            for prop in sample_properties:
                f.write(json.dumps(prop) + "\n")
        print(f"✅ Created sample property data with {len(sample_properties)} entries")
    
    # Create sample FAQ data
    faq_file = Path("data/processed/premiere_suites_faq_data.jsonl")
    if not faq_file.exists():
        print("📄 Creating sample FAQ data...")
        sample_faqs = [
            {
                "type": "faq",
                "id": "faq_001",
                "question": "How do I book a reservation at Premiere Suites?",
                "answer": "You can book a reservation through our website, by calling our reservation line, or by visiting any of our properties directly. Online booking is available 24/7 and offers the best rates.",
                "category": "booking",
                "tags": ["reservation", "booking", "online", "phone"],
                "source_url": "https://premieresuites.com/booking",
                "text_chunk": "Q: How do I book a reservation at Premiere Suites?\nA: You can book a reservation through our website, by calling our reservation line, or by visiting any of our properties directly. Online booking is available 24/7 and offers the best rates."
            },
            {
                "type": "faq",
                "id": "faq_002",
                "question": "What are the check-in and check-out times?",
                "answer": "Check-in time is 3:00 PM and check-out time is 11:00 AM. Early check-in and late check-out may be available upon request, subject to availability.",
                "category": "check-in",
                "tags": ["check-in", "check-out", "times", "early", "late"],
                "source_url": "https://premieresuites.com/check-in",
                "text_chunk": "Q: What are the check-in and check-out times?\nA: Check-in time is 3:00 PM and check-out time is 11:00 AM. Early check-in and late check-out may be available upon request, subject to availability."
            },
            {
                "type": "faq",
                "id": "faq_003",
                "question": "Do you allow pets in your properties?",
                "answer": "Yes, we are pet-friendly! We allow up to 2 pets per unit with a non-refundable pet fee of $200 per pet. Please notify us in advance if you plan to bring pets.",
                "category": "pets",
                "tags": ["pets", "pet-friendly", "animals", "fee"],
                "source_url": "https://premieresuites.com/pets",
                "text_chunk": "Q: Do you allow pets in your properties?\nA: Yes, we are pet-friendly! We allow up to 2 pets per unit with a non-refundable pet fee of $200 per pet. Please notify us in advance if you plan to bring pets."
            }
        ]
        
        with open(faq_file, 'w') as f:
            for faq in sample_faqs:
                f.write(json.dumps(faq) + "\n")
        print(f"✅ Created sample FAQ data with {len(sample_faqs)} entries")

def main():
    """Main function to recreate collections."""
    print("🏠 Premiere Suites - Recreate Collections with LangChain")
    print("=" * 70)
    
    # Check if we should use cloud
    use_cloud = os.getenv("QDRANT_URL") and os.getenv("QDRANT_API_KEY")
    if use_cloud:
        print("☁️  Using Qdrant Cloud")
    else:
        print("🏠 Using local Qdrant")
    
    # Create sample data if missing
    create_sample_data_if_missing()
    
    # Check data files
    files_exist = check_data_files()
    
    # Recreate collections
    success = True
    
    if files_exist["properties"]:
        property_success = recreate_property_collection(use_cloud)
        success = success and property_success
    else:
        print("⚠️  Skipping property collection (no data file)")
    
    if files_exist["faqs"]:
        faq_success = recreate_faq_collection(use_cloud)
        success = success and faq_success
    else:
        print("⚠️  Skipping FAQ collection (no data file)")
    
    # Summary
    print("\n📊 Recreation Summary")
    print("=" * 30)
    print(f"Property Collection: {'✅ SUCCESS' if files_exist['properties'] and success else '❌ FAILED'}")
    print(f"FAQ Collection: {'✅ SUCCESS' if files_exist['faqs'] and success else '❌ FAILED'}")
    
    if success:
        print("\n🎉 All collections recreated successfully with LangChain!")
        print("\n💡 You can now use:")
        print("  • LangChainQdrantIntegration for property search")
        print("  • LangChainFAQIntegration for FAQ search")
        print("  • Both collections are optimized for LangChain operations")
    else:
        print("\n⚠️  Some collections failed to recreate. Check the error messages above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())


