#!/usr/bin/env python3
"""
Simple test script for LangChain Qdrant integration
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_langchain_property_integration():
    """Test the property LangChain integration."""
    print("🔗 Testing LangChain Property Integration")
    print("=" * 50)
    
    try:
        from vector_db.langchain_qdrant_integration import LangChainQdrantIntegration
        
        # Initialize with explicit embedding model
        integration = LangChainQdrantIntegration(
            collection_name="test_properties",
            embedding_model="all-MiniLM-L6-v2"
        )
        
        print("✅ LangChain Property Integration initialized successfully")
        
        # Create collection
        integration.create_collection(recreate=True)
        print("✅ Collection created successfully")
        
        # Test with sample data
        sample_texts = [
            "Luxury apartment with pool and gym in downtown Toronto",
            "Pet-friendly studio apartment with modern amenities",
            "High-rise condo with ocean view in Vancouver"
        ]
        
        sample_metadata = [
            {"city": "Toronto", "rating": 4.5, "pet_friendly": True},
            {"city": "Vancouver", "rating": 4.2, "pet_friendly": True},
            {"city": "Vancouver", "rating": 4.8, "pet_friendly": False}
        ]
        
        # Add data
        integration.add_texts(sample_texts, metadatas=sample_metadata)
        print("✅ Sample data added successfully")
        
        # Test search
        results = integration.similarity_search("luxury apartment", k=2)
        print(f"✅ Search completed, found {len(results)} results")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in property integration: {e}")
        return False

def test_langchain_faq_integration():
    """Test the FAQ LangChain integration."""
    print("\n🔗 Testing LangChain FAQ Integration")
    print("=" * 50)
    
    try:
        from vector_db.langchain_faq_integration import LangChainFAQIntegration
        
        # Initialize with explicit embedding model
        integration = LangChainFAQIntegration(
            collection_name="test_faqs",
            embedding_model="all-MiniLM-L6-v2"
        )
        
        print("✅ LangChain FAQ Integration initialized successfully")
        
        # Create collection
        integration.create_collection(recreate=True)
        print("✅ Collection created successfully")
        
        # Test with sample FAQ data
        questions = [
            "How do I book a reservation?",
            "What are the check-in times?",
            "Do you allow pets?"
        ]
        
        answers = [
            "You can book through our website or by calling our reservation line.",
            "Check-in is at 3:00 PM and check-out is at 11:00 AM.",
            "Yes, we are pet-friendly with a $200 pet fee."
        ]
        
        metadata = [
            {"category": "booking", "tags": ["reservation", "online"]},
            {"category": "check-in", "tags": ["times", "schedule"]},
            {"category": "pets", "tags": ["pet-friendly", "fee"]}
        ]
        
        # Add data
        integration.add_faq_texts(questions, answers, metadatas=metadata)
        print("✅ Sample FAQ data added successfully")
        
        # Test search
        results = integration.search_faqs("How do I book?", k=2)
        print(f"✅ FAQ search completed, found {len(results)} results")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in FAQ integration: {e}")
        return False

def main():
    """Main test function."""
    print("🏠 LangChain Qdrant Integration Test")
    print("=" * 60)
    
    # Test property integration
    property_success = test_langchain_property_integration()
    
    # Test FAQ integration
    faq_success = test_langchain_faq_integration()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    print(f"Property Integration: {'✅ PASS' if property_success else '❌ FAIL'}")
    print(f"FAQ Integration: {'✅ PASS' if faq_success else '❌ FAIL'}")
    
    if property_success and faq_success:
        print("\n🎉 All tests passed! LangChain integration is working correctly.")
        print("\n💡 You can now use:")
        print("  • LangChainQdrantIntegration for property data")
        print("  • LangChainFAQIntegration for FAQ data")
        print("  • Both support local Qdrant and Qdrant Cloud")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
        return 1

if __name__ == "__main__":
    exit(main())


