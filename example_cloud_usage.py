#!/usr/bin/env python3
"""
Example Usage of Qdrant Cloud for Premiere Suites Property Search

This script demonstrates various search scenarios using the Qdrant Cloud setup.
"""

import os
from qdrant_setup import PremiereSuitesVectorDB

def load_environment():
    """Load environment variables from .env file."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

def initialize_vdb():
    """Initialize the vector database with cloud credentials."""
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    if not qdrant_url or not qdrant_api_key:
        raise ValueError("Please set QDRANT_URL and QDRANT_API_KEY environment variables")
    
    return PremiereSuitesVectorDB(
        qdrant_url=qdrant_url,
        qdrant_api_key=qdrant_api_key,
        use_cloud=True
    )

def print_results(results, title):
    """Print search results in a formatted way."""
    print(f"\n{title}")
    print("=" * 60)
    
    if not results:
        print("No results found.")
        return
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['property_name']}")
        print(f"   Location: {result['city']}")
        print(f"   Rating: {result['rating']}/5.0")
        print(f"   Pet Friendly: {'Yes' if result['pet_friendly'] else 'No'}")
        print(f"   Amenities: {', '.join(result['amenities'][:3])}{'...' if len(result['amenities']) > 3 else ''}")
        print(f"   Similarity Score: {result['score']:.4f}")
        print("-" * 40)

def example_searches():
    """Run various example searches."""
    print("🏠 Premiere Suites Property Search Examples")
    print("=" * 60)
    
    try:
        # Initialize vector database
        vdb = initialize_vdb()
        
        # Get collection info
        info = vdb.get_collection_info()
        print(f"Connected to collection with {info['points_count']} properties")
        
        # Example 1: Luxury properties
        print("\n🔍 Example 1: Luxury Properties")
        results = vdb.search_properties(
            query="luxury apartment with pool and gym",
            limit=5,
            min_rating=4.0
        )
        print_results(results, "Luxury Properties with Pool and Gym")
        
        # Example 2: Pet-friendly properties in specific cities
        print("\n🔍 Example 2: Pet-Friendly Properties")
        cities = ["Toronto", "Vancouver", "Calgary"]
        for city in cities:
            results = vdb.search_properties(
                query="pet friendly apartment",
                limit=3,
                city=city,
                pet_friendly=True
            )
            print_results(results, f"Pet-Friendly Properties in {city}")
        
        # Example 3: High-rated properties with specific amenities
        print("\n🔍 Example 3: High-Rated Properties")
        results = vdb.search_properties(
            query="apartment with terrace and in-suite laundry",
            limit=5,
            min_rating=4.5
        )
        print_results(results, "High-Rated Properties with Terrace and In-Suite Laundry")
        
        # Example 4: Properties by location and rating
        print("\n🔍 Example 4: Location-Based Search")
        results = vdb.search_properties(
            query="modern apartment building",
            limit=5,
            city="Vancouver",
            min_rating=4.0
        )
        print_results(results, "Modern Apartments in Vancouver (4+ Rating)")
        
        # Example 5: Specific amenity search
        print("\n🔍 Example 5: Specific Amenity Search")
        results = vdb.search_properties(
            query="apartment with garden and parking",
            limit=5
        )
        print_results(results, "Properties with Garden and Parking")
        
        # Example 6: Budget-friendly options
        print("\n🔍 Example 6: Budget-Friendly Options")
        results = vdb.search_properties(
            query="affordable apartment with basic amenities",
            limit=5,
            min_rating=3.5
        )
        print_results(results, "Affordable Properties (3.5+ Rating)")
        
        print("\n✅ All example searches completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please ensure:")
        print("1. Qdrant Cloud credentials are set correctly")
        print("2. The vector database is populated with data")
        print("3. Your cluster is active and accessible")

def advanced_search_examples():
    """Demonstrate advanced search features."""
    print("\n🔬 Advanced Search Examples")
    print("=" * 60)
    
    try:
        vdb = initialize_vdb()
        
        # Example: Complex filtering
        print("\n🔍 Complex Filter Example")
        results = vdb.search_properties(
            query="luxury apartment with premium amenities",
            limit=10,
            min_rating=4.0,
            pet_friendly=True,
            bedrooms=1
        )
        print_results(results, "Luxury 1-Bedroom Pet-Friendly Properties (4+ Rating)")
        
        # Example: City comparison
        print("\n🔍 City Comparison")
        cities = ["Toronto", "Vancouver", "Calgary", "Edmonton"]
        for city in cities:
            results = vdb.search_properties(
                query="high quality apartment",
                limit=2,
                city=city,
                min_rating=4.0
            )
            if results:
                print(f"\nTop properties in {city}:")
                for result in results:
                    print(f"  • {result['property_name']} (Rating: {result['rating']})")
        
        print("\n✅ Advanced search examples completed!")
        
    except Exception as e:
        print(f"❌ Error in advanced searches: {e}")

def main():
    """Main function."""
    load_environment()
    
    # Run basic examples
    example_searches()
    
    # Run advanced examples
    advanced_search_examples()
    
    print("\n🎉 All examples completed!")
    print("\nTo run interactive search: python search_properties.py")
    print("To set up your own searches, use the PremiereSuitesVectorDB class")

if __name__ == "__main__":
    main()
