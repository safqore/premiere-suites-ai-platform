#!/usr/bin/env python3
"""
Test script to debug n8n integration with FAQ search
"""

import os
import json
from dotenv import load_dotenv
from qdrant_setup import PremiereSuitesVectorDB

# Load environment variables
load_dotenv()

def test_faq_search():
    """Test FAQ search functionality"""
    print("🔍 Testing FAQ Search for n8n Integration")
    print("=" * 60)
    
    try:
        # Initialize vector database
        print("1. Initializing vector database...")
        
        # Get Qdrant credentials from environment
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        if not qdrant_url or not qdrant_api_key:
            print("❌ Missing Qdrant credentials in environment variables")
            print("   Please set QDRANT_URL and QDRANT_API_KEY")
            return False
        
        vdb = PremiereSuitesVectorDB(
            qdrant_url=qdrant_url,
            qdrant_api_key=qdrant_api_key,
            collection_name="premiere_suites_faqs",
            embedding_model="text-embedding-3-small",
            use_cloud=True
        )
        
        # Test collection connection
        print("2. Testing collection connection...")
        try:
            info = vdb.get_collection_info()
            print(f"   ✅ Connected to collection: {info['name']}")
            print(f"   📊 Total vectors: {info['vectors_count']}")
        except Exception as e:
            print(f"   ❌ Collection error: {e}")
            return False
        
        # Test search functionality
        print("3. Testing search functionality...")
        test_queries = [
            "What is Premiere Suites Alliance?",
            "How do I book a reservation?",
            "Do you allow pets?",
            "What are check-in times?",
            "What payment methods do you accept?"
        ]
        
        for query in test_queries:
            print(f"\n   🔍 Testing query: '{query}'")
            try:
                results = vdb.client.search(
                    collection_name=vdb.collection_name,
                    query_vector=vdb.generate_query_embedding(query),
                    limit=3,
                    score_threshold=0.5
                )
                
                if results:
                    print(f"   ✅ Found {len(results)} results")
                    for i, result in enumerate(results, 1):
                        print(f"      {i}. Score: {result.score:.3f} - {result.payload.get('question', 'N/A')}")
                else:
                    print(f"   ⚠️  No results found (score threshold too high?)")
                    
            except Exception as e:
                print(f"   ❌ Search error: {e}")
        
        # Test different score thresholds
        print("\n4. Testing different score thresholds...")
        query = "What is Premiere Suites Alliance?"
        
        for threshold in [0.3, 0.5, 0.7, 0.8]:
            try:
                results = vdb.client.search(
                    collection_name=vdb.collection_name,
                    query_vector=vdb.generate_query_embedding(query),
                    limit=3,
                    score_threshold=threshold
                )
                print(f"   Threshold {threshold}: {len(results)} results")
            except Exception as e:
                print(f"   Threshold {threshold}: Error - {e}")
        
        print("\n✅ All tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def generate_n8n_test_data():
    """Generate test data for n8n workflow"""
    print("\n📋 n8n Test Data")
    print("=" * 60)
    
    test_cases = [
        {
            "text": "What is Premiere Suites Alliance?",
            "expected_score": "0.7+",
            "description": "Direct FAQ question"
        },
        {
            "text": "Tell me about the Alliance program",
            "expected_score": "0.6+",
            "description": "Semantic variation"
        },
        {
            "text": "How do I book a reservation?",
            "expected_score": "0.7+",
            "description": "Booking question"
        },
        {
            "text": "Do you allow pets?",
            "expected_score": "0.7+",
            "description": "Pet policy question"
        }
    ]
    
    print("Test these inputs in your n8n workflow:")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Input: '{test_case['text']}'")
        print(f"   Expected: Score {test_case['expected_score']}")
        print(f"   Description: {test_case['description']}")
    
    print("\n🔧 n8n Configuration Tips:")
    print("1. Set scoreThreshold to 0.5 in 'Answer questions with a vector store' node")
    print("2. Use description: '{{ $json.text || $json.message || $json.chat_message }}'")
    print("3. Set topK to 3-5 for best results")
    print("4. Check execution logs for detailed error messages")

def main():
    """Main function"""
    print("🚀 n8n FAQ Integration Test Suite")
    print("=" * 60)
    
    # Run tests
    success = test_faq_search()
    
    if success:
        generate_n8n_test_data()
        
        print("\n🎯 Next Steps:")
        print("1. Import the fixed workflow (n8n_workflow_fixed.json)")
        print("2. Test with the provided test cases")
        print("3. Check execution logs for any errors")
        print("4. Adjust scoreThreshold if needed (0.5 is recommended)")
    else:
        print("\n❌ Tests failed. Please check your configuration.")

if __name__ == "__main__":
    main()
