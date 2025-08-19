#!/usr/bin/env python3
"""
Property Search Interface for Premiere Suites Vector Database

This script provides an interactive interface to search through properties
using semantic similarity and various filters.
"""

import json
from typing import List, Dict, Any, Optional
from qdrant_setup import PremiereSuitesVectorDB

def print_search_results(results: List[Dict[str, Any]]) -> None:
    """Pretty print search results."""
    if not results:
        print("No results found.")
        return
    
    print(f"\nFound {len(results)} properties:")
    print("=" * 80)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['property_name']}")
        print(f"   Location: {result['city']}")
        print(f"   Rating: {result['rating']}/5.0")
        print(f"   Bedrooms: {result['bedrooms']}")
        print(f"   Pet Friendly: {'Yes' if result['pet_friendly'] else 'No'}")
        print(f"   Amenities: {', '.join(result['amenities'][:5])}{'...' if len(result['amenities']) > 5 else ''}")
        print(f"   Similarity Score: {result['score']:.4f}")
        print(f"   URL: {result['source_url']}")
        print("-" * 80)

def interactive_search(vdb: PremiereSuitesVectorDB) -> None:
    """Interactive search interface."""
    print("🏠 Premiere Suites Property Search")
    print("=" * 50)
    
    while True:
        print("\nSearch Options:")
        print("1. Search by description")
        print("2. Search with filters")
        print("3. View collection info")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            query = input("Enter your search query: ").strip()
            if not query:
                print("Please enter a search query.")
                continue
            
            limit = input("Number of results (default 10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            
            try:
                results = vdb.search_properties(query=query, limit=limit)
                print_search_results(results)
            except Exception as e:
                print(f"Error searching: {e}")
        
        elif choice == "2":
            query = input("Enter your search query: ").strip()
            if not query:
                print("Please enter a search query.")
                continue
            
            # Get filters
            city = input("Filter by city (optional): ").strip() or None
            min_rating = input("Minimum rating (optional, e.g., 4.0): ").strip()
            min_rating = float(min_rating) if min_rating and min_rating.replace('.', '').isdigit() else None
            
            pet_friendly = input("Pet friendly only? (y/n, optional): ").strip().lower()
            pet_friendly = True if pet_friendly == 'y' else (False if pet_friendly == 'n' else None)
            
            bedrooms = input("Number of bedrooms (optional): ").strip()
            bedrooms = int(bedrooms) if bedrooms.isdigit() else None
            
            limit = input("Number of results (default 10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            
            try:
                results = vdb.search_properties(
                    query=query,
                    limit=limit,
                    city=city,
                    min_rating=min_rating,
                    pet_friendly=pet_friendly,
                    bedrooms=bedrooms
                )
                print_search_results(results)
            except Exception as e:
                print(f"Error searching: {e}")
        
        elif choice == "3":
            try:
                info = vdb.get_collection_info()
                print("\nCollection Information:")
                print(f"Name: {info['name']}")
                print(f"Total Properties: {info['points_count']}")
                print(f"Vector Size: {info['config']['vector_size']}")
                print(f"Distance Metric: {info['config']['distance']}")
                print(f"Storage: {'On Disk' if info['config']['on_disk'] else 'In Memory'}")
            except Exception as e:
                print(f"Error getting collection info: {e}")
        
        elif choice == "4":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1-4.")

def example_searches(vdb: PremiereSuitesVectorDB) -> None:
    """Run some example searches to demonstrate functionality."""
    print("\n🔍 Example Searches")
    print("=" * 50)
    
    examples = [
        {
            "query": "luxury apartment with pool and gym",
            "description": "Luxury properties with pool and gym"
        },
        {
            "query": "pet friendly apartment in Toronto",
            "description": "Pet friendly properties in Toronto"
        },
        {
            "query": "high rated apartment with terrace",
            "description": "Highly rated properties with terrace"
        },
        {
            "query": "apartment with in-suite laundry",
            "description": "Properties with in-suite laundry"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['description']}")
        print(f"   Query: '{example['query']}'")
        
        try:
            results = vdb.search_properties(query=example['query'], limit=3)
            if results:
                print("   Top results:")
                for j, result in enumerate(results, 1):
                    print(f"     {j}. {result['property_name']} ({result['city']}) - Rating: {result['rating']}")
            else:
                print("   No results found")
        except Exception as e:
            print(f"   Error: {e}")

def main():
    """Main function."""
    try:
        # Initialize vector database
        print("Initializing vector database...")
        
        # Load environment variables from .env file if it exists
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass  # python-dotenv not installed, continue without it
        
        # Check for environment variables for Qdrant Cloud
        import os
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        use_cloud = bool(qdrant_url and qdrant_api_key)
        
        if use_cloud:
            print("Using Qdrant Cloud configuration")
            vdb = PremiereSuitesVectorDB(
                qdrant_url=qdrant_url,
                qdrant_api_key=qdrant_api_key,
                use_cloud=True
            )
        else:
            print("Using local Qdrant configuration")
            vdb = PremiereSuitesVectorDB()
        
        # Check if collection exists and has data
        try:
            info = vdb.get_collection_info()
            if info['points_count'] == 0:
                print("Collection is empty. Please run qdrant_setup.py first to populate the database.")
                return
            print(f"Connected to collection with {info['points_count']} properties")
        except Exception as e:
            print(f"Error connecting to collection: {e}")
            print("Please make sure Qdrant is running and the collection exists.")
            return
        
        # Run example searches
        example_searches(vdb)
        
        # Start interactive search
        interactive_search(vdb)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Please make sure Qdrant is running and accessible.")

if __name__ == "__main__":
    main()
