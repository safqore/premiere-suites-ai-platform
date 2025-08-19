#!/usr/bin/env python3
"""
Test script to demonstrate search filters functionality
"""

import os
import json
from dotenv import load_dotenv
from qdrant_setup import PremiereSuitesVectorDB

# Load environment variables
load_dotenv()

def test_search_filters():
    """Test different search queries with filters"""
    print("🔍 Testing Search Filters")
    print("=" * 60)
    
    # Test queries with different filters
    test_queries = [
        {
            "query": "What is Premiere Suites Alliance?",
            "expected_category": "About Us",
            "expected_tags": ["furnished", "corporate"],
            "description": "Alliance question (About Us category)"
        },
        {
            "query": "How do I book a reservation?",
            "expected_category": "Reservations",
            "expected_tags": ["booking", "reservation"],
            "description": "Booking question (Reservations category)"
        },
        {
            "query": "Do you allow pets?",
            "expected_category": "Rules and Regulations",
            "expected_tags": ["pet-friendly"],
            "description": "Pet policy (Rules category)"
        },
        {
            "query": "What payment methods do you accept?",
            "expected_category": "Payment",
            "expected_tags": ["payment"],
            "description": "Payment question (Payment category)"
        },
        {
            "query": "What amenities are included?",
            "expected_category": "Guest Services",
            "expected_tags": ["amenities"],
            "description": "Amenities question (Guest Services category)"
        },
        {
            "query": "Do you have parking available?",
            "expected_category": "Guest Services",
            "expected_tags": ["parking"],
            "description": "Parking question (with parking tag)"
        }
    ]
    
    try:
        # Initialize vector database
        print("Initializing vector database...")
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        vdb = PremiereSuitesVectorDB(
            qdrant_url=qdrant_url,
            qdrant_api_key=qdrant_api_key,
            collection_name="premiere_suites_faqs",
            embedding_model="text-embedding-3-small",
            use_cloud=True
        )
        
        # Test each query
        for i, test_case in enumerate(test_queries, 1):
            print(f"\n{i}. {test_case['description']}")
            print(f"   Query: '{test_case['query']}'")
            print(f"   Expected Category: {test_case['expected_category']}")
            print(f"   Expected Tags: {test_case['expected_tags']}")
            
            # Test without filters
            print("   Testing without filters:")
            results = vdb.client.search(
                collection_name=vdb.collection_name,
                query_vector=vdb.generate_query_embedding(test_case['query']),
                limit=3,
                score_threshold=0.3
            )
            
            if results:
                for j, result in enumerate(results, 1):
                    category = result.payload.get('category', 'N/A')
                    tags = result.payload.get('tags', [])
                    print(f"     {j}. Score: {result.score:.3f} - {result.payload.get('question', 'N/A')}")
                    print(f"        Category: {category}, Tags: {tags}")
            else:
                print("     No results found")
            
            # Test with category filter
            print("   Testing with category filter:")
            try:
                from qdrant_client.models import FieldCondition, MatchValue, Filter
                
                filter_condition = Filter(
                    must=[
                        FieldCondition(
                            key="category",
                            match=MatchValue(value=test_case['expected_category'])
                        )
                    ]
                )
                
                filtered_results = vdb.client.search(
                    collection_name=vdb.collection_name,
                    query_vector=vdb.generate_query_embedding(test_case['query']),
                    limit=3,
                    score_threshold=0.2,
                    query_filter=filter_condition
                )
                
                if filtered_results:
                    for j, result in enumerate(filtered_results, 1):
                        print(f"     {j}. Score: {result.score:.3f} - {result.payload.get('question', 'N/A')}")
                        print(f"        Category: {result.payload.get('category', 'N/A')}")
                else:
                    print("     No filtered results found")
                    
            except Exception as e:
                print(f"     Error with filter: {e}")
            
            print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def show_filter_keywords():
    """Show all available filter keywords"""
    print("\n🔑 Available Filter Keywords")
    print("=" * 60)
    
    print("📂 Categories:")
    categories = {
        'booking': 'Reservations',
        'reservation': 'Reservations', 
        'book': 'Reservations',
        'payment': 'Payment',
        'pay': 'Payment',
        'deposit': 'Payment',
        'guest': 'Guest Services',
        'amenities': 'Guest Services',
        'housekeeping': 'Guest Services',
        'rules': 'Rules and Regulations',
        'pet': 'Rules and Regulations',
        'smoking': 'Rules and Regulations',
        'about': 'About Us',
        'alliance': 'About Us',
        'company': 'About Us'
    }
    
    for keyword, category in categories.items():
        print(f"   '{keyword}' → {category}")
    
    print("\n🏷️ Tags:")
    tags = {
        'furnished': 'furnished',
        'pet': 'pet-friendly',
        'pets': 'pet-friendly',
        'parking': 'parking',
        'wifi': 'internet',
        'internet': 'internet',
        'gym': 'amenities',
        'pool': 'pool',
        'laundry': 'laundry',
        'kitchen': 'kitchen',
        'corporate': 'corporate',
        'rent': 'rent',
        'lease': 'lease',
        'short-term': 'short-term',
        'long-term': 'long-term'
    }
    
    for keyword, tag in tags.items():
        print(f"   '{keyword}' → {tag}")
    
    print("\n💡 Example Queries:")
    print("   - 'How do I book a reservation?' (Reservations category)")
    print("   - 'Do you allow pets?' (Rules category + pet-friendly tag)")
    print("   - 'What payment methods do you accept?' (Payment category)")
    print("   - 'Do you have parking available?' (parking tag)")
    print("   - 'What is included in furnished apartments?' (furnished tag)")

def main():
    """Main function"""
    print("🚀 Search Filters Test Suite")
    print("=" * 60)
    
    # Run tests
    success = test_search_filters()
    
    if success:
        show_filter_keywords()
        
        print("\n🎯 **How Filters Work in n8n:**")
        print("1. The 'Fix Chat Input with Filters' node analyzes the message")
        print("2. It extracts category and tag filters based on keywords")
        print("3. The vector store search uses these filters for better results")
        print("4. Score threshold is automatically adjusted based on filters")
        
        print("\n📋 **Benefits:**")
        print("✅ More relevant search results")
        print("✅ Faster response times")
        print("✅ Better user experience")
        print("✅ Automatic category detection")
    else:
        print("\n❌ Tests failed. Check your configuration.")

if __name__ == "__main__":
    main()
