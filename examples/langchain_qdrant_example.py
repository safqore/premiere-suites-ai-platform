#!/usr/bin/env python3
"""
LangChain Qdrant Integration Example

This example demonstrates how to use LangChain with Qdrant for the Premiere Suites project.
It shows both the direct Qdrant approach and the LangChain abstraction.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from vector_db.langchain_qdrant_integration import LangChainQdrantIntegration
from vector_db.qdrant_setup import PremiereSuitesVectorDB

def compare_approaches():
    """Compare direct Qdrant vs LangChain approaches."""
    print("🔍 Comparing Direct Qdrant vs LangChain Approaches")
    print("=" * 60)
    
    # Initialize both approaches
    print("\n1️⃣ Initializing Direct Qdrant Setup...")
    direct_vdb = PremiereSuitesVectorDB(
        collection_name="premiere_suites_direct"
    )
    
    print("\n2️⃣ Initializing LangChain Integration...")
    langchain_vdb = LangChainQdrantIntegration(
        collection_name="premiere_suites_langchain"
    )
    
    # Create collections
    print("\n📦 Creating Collections...")
    direct_vdb.create_collection(recreate=True)
    langchain_vdb.create_collection(recreate=True)
    
    # Load sample data
    print("\n📄 Loading Sample Data...")
    sample_texts = [
        "Luxury apartment with pool and gym in downtown Toronto",
        "Pet-friendly studio apartment with modern amenities",
        "High-rise condo with ocean view in Vancouver",
        "Family-friendly apartment with playground and parking",
        "Executive suite with business center and conference rooms"
    ]
    
    sample_metadata = [
        {"city": "Toronto", "rating": 4.5, "pet_friendly": True, "bedrooms": 2},
        {"city": "Vancouver", "rating": 4.2, "pet_friendly": True, "bedrooms": 1},
        {"city": "Vancouver", "rating": 4.8, "pet_friendly": False, "bedrooms": 3},
        {"city": "Toronto", "rating": 4.0, "pet_friendly": True, "bedrooms": 2},
        {"city": "Montreal", "rating": 4.6, "pet_friendly": False, "bedrooms": 1}
    ]
    
    # Add data using direct approach
    print("\n3️⃣ Adding Data with Direct Qdrant...")
    points = []
    for i, (text, metadata) in enumerate(zip(sample_texts, sample_metadata)):
        embedding = direct_vdb.generate_query_embedding(text)
        from qdrant_client.models import PointStruct
        point = PointStruct(
            id=i,
            vector=embedding,
            payload={
                "text": text,
                **metadata
            }
        )
        points.append(point)
    
    direct_vdb.insert_data(points)
    
    # Add data using LangChain
    print("\n4️⃣ Adding Data with LangChain...")
    langchain_vdb.add_texts(sample_texts, metadatas=sample_metadata)
    
    # Test searches
    print("\n🔍 Testing Searches...")
    test_queries = [
        "luxury apartment with amenities",
        "pet friendly apartment",
        "apartment with ocean view"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 40)
        
        # Direct Qdrant search
        print("Direct Qdrant Results:")
        direct_results = direct_vdb.search_properties(query, limit=3)
        for i, result in enumerate(direct_results, 1):
            print(f"  {i}. Score: {result['score']:.3f} - {result.get('text', 'N/A')}")
        
        # LangChain search
        print("\nLangChain Results:")
        langchain_results = langchain_vdb.similarity_search_with_score(query, k=3)
        for i, (doc, score) in enumerate(langchain_results, 1):
            print(f"  {i}. Score: {score:.3f} - {doc.page_content}")
    
    print("\n✅ Comparison completed!")

def langchain_advanced_features():
    """Demonstrate advanced LangChain features."""
    print("\n🚀 LangChain Advanced Features")
    print("=" * 50)
    
    # Initialize LangChain integration
    langchain_vdb = LangChainQdrantIntegration(
        collection_name="premiere_suites_advanced"
    )
    
    # Create collection
    langchain_vdb.create_collection(recreate=True)
    
    # Create sample documents with rich metadata
    from langchain.schema import Document
    
    documents = [
        Document(
            page_content="Luxury penthouse with panoramic city views, private terrace, and 24/7 concierge service. Features include a gourmet kitchen, home theater, and private elevator access.",
            metadata={
                "property_type": "penthouse",
                "city": "Toronto",
                "rating": 4.9,
                "price_range": "high",
                "amenities": ["concierge", "terrace", "kitchen", "theater"],
                "bedrooms": 3,
                "pet_friendly": False
            }
        ),
        Document(
            page_content="Cozy studio apartment perfect for students or young professionals. Located near universities with easy access to public transportation and shopping centers.",
            metadata={
                "property_type": "studio",
                "city": "Vancouver",
                "rating": 4.1,
                "price_range": "budget",
                "amenities": ["transit", "shopping", "university"],
                "bedrooms": 1,
                "pet_friendly": True
            }
        ),
        Document(
            page_content="Family-friendly apartment complex with playground, swimming pool, and community garden. Perfect for families with children, featuring spacious layouts and modern appliances.",
            metadata={
                "property_type": "apartment",
                "city": "Montreal",
                "rating": 4.3,
                "price_range": "mid",
                "amenities": ["playground", "pool", "garden", "appliances"],
                "bedrooms": 2,
                "pet_friendly": True
            }
        )
    ]
    
    # Add documents
    print("📄 Adding documents with rich metadata...")
    langchain_vdb.add_documents(documents)
    
    # Test advanced filtering
    print("\n🔍 Testing Advanced Filtering...")
    
    # Search with filters
    results = langchain_vdb.similarity_search(
        query="family friendly apartment with amenities",
        k=3,
        filter={
            "pet_friendly": True,
            "bedrooms": {"$gte": 2}
        }
    )
    
    print("Filtered Results (pet-friendly, 2+ bedrooms):")
    for i, doc in enumerate(results, 1):
        print(f"  {i}. {doc.page_content[:100]}...")
        print(f"     Metadata: {doc.metadata}")
    
    # Test similarity search with scores
    print("\n📊 Similarity Search with Scores:")
    scored_results = langchain_vdb.similarity_search_with_score(
        query="luxury apartment with city views",
        k=3
    )
    
    for i, (doc, score) in enumerate(scored_results, 1):
        print(f"  {i}. Score: {score:.3f}")
        print(f"     Content: {doc.page_content[:80]}...")
        print(f"     Type: {doc.metadata.get('property_type')}")

def main():
    """Main function to run the examples."""
    print("🏠 Premiere Suites - LangChain Qdrant Integration Examples")
    print("=" * 70)
    
    try:
        # Check if we have sample data
        data_file = Path("premiere_suites_data.jsonl")
        if data_file.exists():
            print("✅ Found existing data file")
            
            # Run with real data
            print("\n📊 Running with Real Data...")
            langchain_vdb = LangChainQdrantIntegration(
                collection_name="premiere_suites_real"
            )
            
            # Load and add documents
            documents = langchain_vdb.load_documents_from_jsonl(str(data_file))
            if documents:
                langchain_vdb.create_collection(recreate=True)
                langchain_vdb.add_documents(documents)
                
                # Test search
                print("\n🔍 Testing with Real Data...")
                results = langchain_vdb.search_properties_langchain(
                    query="luxury apartment with pool and gym",
                    limit=5,
                    min_rating=4.0
                )
                
                print("Search Results:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['property_name']} ({result['city']}) - Rating: {result['rating']} - Score: {result['score']:.3f}")
        else:
            print("📝 No existing data found, running with sample data...")
        
        # Run comparison
        compare_approaches()
        
        # Run advanced features
        langchain_advanced_features()
        
        print("\n🎉 All examples completed successfully!")
        print("\n💡 Key Benefits of LangChain Integration:")
        print("  • Higher-level abstractions for easier development")
        print("  • Built-in document processing and text splitting")
        print("  • Easy integration with other LangChain components")
        print("  • Consistent API across different vector stores")
        print("  • Advanced filtering and search capabilities")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())


