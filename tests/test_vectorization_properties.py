#!/usr/bin/env python3
"""
Test script to verify vectorization properties are correctly set.

This script tests that the FAQ vectorization process ensures:
- content is not empty
- metadata is a proper object (not empty)
- id is properly set
"""

import json
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_faq_data():
    """Create test FAQ data with various scenarios."""
    test_data = [
        {
            "type": "faq",
            "id": 1,
            "question": "How do I book a reservation?",
            "answer": "You can book online through our website or call us directly.",
            "category": "Booking",
            "tags": ["reservation", "booking"],
            "source_url": "https://example.com/booking",
            "text_chunk": "Q: How do I book a reservation?\nA: You can book online through our website or call us directly."
        },
        {
            "type": "faq",
            "id": 2,
            "question": "What are check-in times?",
            "answer": "Check-in is available from 3 PM onwards.",
            "category": "Check-in",
            "tags": ["check-in", "arrival"],
            "source_url": "https://example.com/checkin",
            "text_chunk": ""  # Empty text_chunk to test fallback
        },
        {
            "type": "faq",
            "id": None,  # Missing ID to test fallback
            "question": "Do you allow pets?",
            "answer": "Yes, we are pet-friendly with a small fee.",
            "category": "Pets",
            "tags": ["pets", "animals"],
            "source_url": "https://example.com/pets",
            "text_chunk": "Q: Do you allow pets?\nA: Yes, we are pet-friendly with a small fee."
        }
    ]
    
    # Write test data to JSONL file
    test_file = "test_faq_data.jsonl"
    with open(test_file, 'w', encoding='utf-8') as f:
        for item in test_data:
            f.write(json.dumps(item) + '\n')
    
    logger.info(f"Created test FAQ data file: {test_file}")
    return test_file

def test_langchain_integration():
    """Test LangChain integration with property verification."""
    from src.vector_db.langchain_faq_integration import LangChainFAQIntegration
    
    print("\n🔗 Testing LangChain Integration")
    print("=" * 50)
    
    try:
        # Create test data
        test_file = create_test_faq_data()
        
        # Initialize integration
        integration = LangChainFAQIntegration(
            collection_name="test_faq_properties",
            use_cloud=True,  # Use cloud for testing
            qdrant_url=os.getenv("QDRANT_URL"),
            qdrant_api_key=os.getenv("QDRANT_API_KEY")
        )
        
        # Create collection
        integration.create_collection(recreate=True)
        
        # Load documents
        documents = integration.load_faq_documents_from_jsonl(test_file)
        
        print(f"\n📄 Loaded {len(documents)} documents:")
        for i, doc in enumerate(documents):
            print(f"\nDocument {i + 1}:")
            print(f"  content: {doc.page_content[:100]}...")
            print(f"  metadata: {doc.metadata}")
            print(f"  faq_id: {doc.metadata.get('faq_id')}")
            
            # Verify properties
            assert doc.page_content.strip(), f"Document {i + 1}: content is empty"
            assert doc.metadata, f"Document {i + 1}: metadata is empty"
            assert 'faq_id' in doc.metadata, f"Document {i + 1}: faq_id missing from metadata"
        
        # Add documents
        integration.add_faq_documents(documents)
        
        # Verify in Qdrant
        points = integration.vdb.client.scroll(
            collection_name="test_faq_properties",
            limit=10,
            with_payload=True
        )[0]
        
        print(f"\n📊 Verified {len(points)} points in Qdrant:")
        for i, point in enumerate(points):
            print(f"\nPoint {i + 1}:")
            print(f"  id: {point.id}")
            # Both approaches now use 'content' consistently
            content = point.payload.get('content', 'NOT FOUND')
            print(f"  content: {content[:100]}...")
            print(f"  metadata: {point.payload.get('metadata', 'NOT FOUND')}")
            print(f"  payload_id: {point.payload.get('id', 'NOT FOUND')}")
            
            # Verify properties
            assert content and content != 'NOT FOUND', f"Point {i + 1}: content missing"
            assert point.payload.get('metadata'), f"Point {i + 1}: metadata missing"
            assert point.payload.get('id'), f"Point {i + 1}: id missing"
        
        print("\n✅ LangChain integration test passed!")
        
        # Cleanup
        integration.delete_collection()
        Path(test_file).unlink(missing_ok=True)
        
    except Exception as e:
        print(f"\n❌ LangChain integration test failed: {e}")
        raise

def test_direct_qdrant_vectorization():
    """Test direct Qdrant vectorization with property verification."""
    from src.vector_db.vectorize_faq_data import vectorize_faq_data, load_faq_data, prepare_faq_points
    from src.vector_db.qdrant_setup import PremiereSuitesVectorDB
    
    print("\n🏠 Testing Direct Qdrant Vectorization")
    print("=" * 50)
    
    try:
        # Create test data
        test_file = create_test_faq_data()
        
        # Initialize vector database
        vdb = PremiereSuitesVectorDB(
            collection_name="test_direct_properties",
            embedding_model="all-MiniLM-L6-v2",
            use_cloud=True,
            qdrant_url=os.getenv("QDRANT_URL"),
            qdrant_api_key=os.getenv("QDRANT_API_KEY")
        )
        
        # Create collection
        vdb.create_collection(recreate=True)
        
        # Load FAQ data
        faqs = load_faq_data(test_file)
        
        # Prepare points
        points = prepare_faq_points(faqs, vdb)
        
        print(f"\n📄 Prepared {len(points)} points:")
        for i, point in enumerate(points):
            print(f"\nPoint {i + 1}:")
            print(f"  id: {point.id}")
            print(f"  content: {point.payload.get('content', 'NOT FOUND')[:100]}...")
            print(f"  metadata: {point.payload.get('metadata', 'NOT FOUND')}")
            print(f"  payload_id: {point.payload.get('id', 'NOT FOUND')}")
            
            # Verify properties
            assert point.payload.get('content'), f"Point {i + 1}: content missing"
            assert point.payload.get('metadata'), f"Point {i + 1}: metadata missing"
            assert point.payload.get('id'), f"Point {i + 1}: id missing"
        
        # Insert data
        vdb.insert_data(points)
        
        # Verify in Qdrant
        stored_points = vdb.client.scroll(
            collection_name="test_direct_properties",
            limit=10,
            with_payload=True
        )[0]
        
        print(f"\n📊 Verified {len(stored_points)} points in Qdrant:")
        for i, point in enumerate(stored_points):
            print(f"\nStored Point {i + 1}:")
            print(f"  id: {point.id}")
            print(f"  content: {point.payload.get('content', 'NOT FOUND')[:100]}...")
            print(f"  metadata: {point.payload.get('metadata', 'NOT FOUND')}")
            print(f"  payload_id: {point.payload.get('id', 'NOT FOUND')}")
            
            # Verify properties
            assert point.payload.get('content'), f"Stored Point {i + 1}: content missing"
            assert point.payload.get('metadata'), f"Stored Point {i + 1}: metadata missing"
            assert point.payload.get('id'), f"Stored Point {i + 1}: id missing"
        
        print("\n✅ Direct Qdrant vectorization test passed!")
        
        # Cleanup
        vdb.client.delete_collection("test_direct_properties")
        Path(test_file).unlink(missing_ok=True)
        
    except Exception as e:
        print(f"\n❌ Direct Qdrant vectorization test failed: {e}")
        raise

def main():
    """Run all tests."""
    print("🧪 Testing Vectorization Properties")
    print("=" * 50)
    
    try:
        # Test LangChain integration
        test_langchain_integration()
        
        # Test direct Qdrant vectorization
        test_direct_qdrant_vectorization()
        
        print("\n🎉 All tests passed! Properties are correctly set.")
        print("\n✅ Verified properties:")
        print("   - content: Always has content (never empty)")
        print("   - metadata: Always a proper object (never empty)")
        print("   - id: Always properly set (uses FAQ ID or fallback)")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
