#!/usr/bin/env python3
"""
FAQ Search Interface

This script provides an interactive interface to search through vectorized FAQ data.
"""

import logging
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from qdrant_setup import PremiereSuitesVectorDB

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def search_faqs(vdb: PremiereSuitesVectorDB, 
                query: str, 
                limit: int = 5,
                category: Optional[str] = None,
                min_score: float = 0.5) -> List[Dict[str, Any]]:
    """
    Search for FAQs using semantic similarity.
    
    Args:
        vdb: Vector database instance
        query: Search query
        limit: Maximum number of results
        category: Filter by category
        min_score: Minimum similarity score
        
    Returns:
        List of search results
    """
    try:
        # Build filter if category is specified
        filter_condition = None
        if category:
            from qdrant_client.models import FieldCondition, MatchValue, Filter
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="category",
                        match=MatchValue(value=category)
                    )
                ]
            )
        
        # Perform search
        results = vdb.client.search(
            collection_name=vdb.collection_name,
            query_vector=vdb.model.encode([query])[0].tolist(),
            limit=limit,
            query_filter=filter_condition,
            score_threshold=min_score
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "score": result.score,
                "faq_id": result.payload.get("faq_id"),
                "question": result.payload.get("question"),
                "answer": result.payload.get("answer"),
                "category": result.payload.get("category"),
                "tags": result.payload.get("tags", [])
            })
        
        return formatted_results
        
    except Exception as e:
        logger.error(f"Error searching FAQs: {e}")
        return []

def display_results(results: List[Dict[str, Any]]) -> None:
    """Display search results in a formatted way."""
    if not results:
        print("❌ No results found.")
        return
    
    print(f"\n🔍 Found {len(results)} results:")
    print("=" * 80)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['question']}")
        print(f"   📊 Similarity Score: {result['score']:.3f}")
        print(f"   📂 Category: {result['category']}")
        print(f"   🏷️  Tags: {', '.join(result['tags']) if result['tags'] else 'None'}")
        print(f"   💬 Answer: {result['answer'][:200]}{'...' if len(result['answer']) > 200 else ''}")
        print("-" * 80)

def interactive_search(vdb: PremiereSuitesVectorDB) -> None:
    """Interactive search interface."""
    print("\n🔍 FAQ Search Interface")
    print("=" * 50)
    print("Type 'quit' to exit, 'help' for commands")
    
    while True:
        try:
            query = input("\n❓ Enter your search query: ").strip()
            
            if query.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif query.lower() == 'help':
                print("\n📖 Available commands:")
                print("  - Type any question to search")
                print("  - 'quit' to exit")
                print("  - 'help' to show this help")
                print("\n💡 Example queries:")
                print("  - 'How do I book a reservation?'")
                print("  - 'What are the check-in times?'")
                print("  - 'Do you allow pets?'")
                print("  - 'What payment methods do you accept?'")
                continue
            elif not query:
                continue
            
            # Get search parameters
            try:
                limit = int(input("📊 Number of results (default 5): ") or "5")
            except ValueError:
                limit = 5
            
            category = input("📂 Filter by category (optional): ").strip() or None
            
            # Perform search
            print(f"\n🔍 Searching for: '{query}'")
            results = search_faqs(vdb, query, limit=limit, category=category)
            
            # Display results
            display_results(results)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def example_searches(vdb: PremiereSuitesVectorDB) -> None:
    """Run example searches to demonstrate functionality."""
    example_queries = [
        "How do I book a reservation?",
        "What are the check-in and check-out times?",
        "Do you allow pets?",
        "What payment methods do you accept?",
        "Is smoking allowed?",
        "Do you offer housekeeping?",
        "What amenities are included?",
        "Can I extend my stay?",
        "What is the cancellation policy?",
        "Do you have parking available?"
    ]
    
    print("\n🧪 Running Example Searches")
    print("=" * 50)
    
    for query in example_queries:
        print(f"\n🔍 Query: '{query}'")
        results = search_faqs(vdb, query, limit=3)
        display_results(results)
        input("\nPress Enter to continue to next query...")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Search Premiere Suites FAQ data")
    parser.add_argument("--collection", default="premiere_suites_faqs",
                       help="Collection name (default: premiere_suites_faqs)")
    parser.add_argument("--cloud", action="store_true",
                       help="Force use of Qdrant Cloud (auto-detected if QDRANT_URL and QDRANT_API_KEY are set)")
    parser.add_argument("--local", action="store_true",
                       help="Force use of local Qdrant instance (ignores environment variables)")
    parser.add_argument("--url", help="Qdrant Cloud URL (overrides QDRANT_URL environment variable)")
    parser.add_argument("--api-key", help="Qdrant Cloud API key (overrides QDRANT_API_KEY environment variable)")
    parser.add_argument("--examples", action="store_true",
                       help="Run example searches instead of interactive mode")
    parser.add_argument("--query", help="Run a single search query")
    parser.add_argument("--limit", type=int, default=5, help="Number of results (default: 5)")
    
    args = parser.parse_args()
    
    print("🏠 Premiere Suites FAQ Search")
    print("=" * 50)
    
    try:
        # Initialize vector database
        print("Initializing vector database...")
        
        # Auto-detect cloud vs local based on environment variables
        env_qdrant_url = os.getenv("QDRANT_URL")
        env_qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        # Determine if we should use cloud
        use_cloud = args.cloud
        if not use_cloud and not args.local:
            use_cloud = bool(env_qdrant_url and env_qdrant_api_key)
        
        if use_cloud:
            # Use provided credentials or fall back to environment variables
            qdrant_url = args.url or env_qdrant_url
            qdrant_api_key = args.api_key or env_qdrant_api_key
            
            if not qdrant_url or not qdrant_api_key:
                print("❌ Qdrant Cloud requires both QDRANT_URL and QDRANT_API_KEY environment variables or --url and --api-key arguments")
                return 1
            
            print(f"✅ Using Qdrant Cloud: {qdrant_url}")
            vdb = PremiereSuitesVectorDB(
                qdrant_url=qdrant_url,
                qdrant_api_key=qdrant_api_key,
                collection_name=args.collection,
                use_cloud=True
            )
        else:
            print("✅ Using local Qdrant instance")
            vdb = PremiereSuitesVectorDB(collection_name=args.collection)
        
        # Check if collection exists
        try:
            info = vdb.get_collection_info()
            print(f"✅ Connected to collection: {info['name']}")
            print(f"📊 Total vectors: {info['vectors_count']}")
        except Exception as e:
            print(f"❌ Collection not found or error: {e}")
            print("💡 Make sure to run vectorize_faq_data.py first!")
            return 1
        
        # Run search based on arguments
        if args.query:
            print(f"\n🔍 Searching for: '{args.query}'")
            results = search_faqs(vdb, args.query, limit=args.limit)
            display_results(results)
        elif args.examples:
            example_searches(vdb)
        else:
            interactive_search(vdb)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
