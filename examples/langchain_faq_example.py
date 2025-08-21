#!/usr/bin/env python3
"""
LangChain FAQ Integration Example

This example demonstrates how to use LangChain with Qdrant for FAQ data
in the Premiere Suites project.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from vector_db.langchain_faq_integration import LangChainFAQIntegration
from vector_db.qdrant_setup import PremiereSuitesVectorDB

def create_sample_faq_data():
    """Create sample FAQ data for testing."""
    sample_faqs = [
        {
            "type": "faq",
            "id": "faq_001",
            "question": "How do I book a reservation at Premiere Suites?",
            "answer": "You can book a reservation through our website, by calling our reservation line, or by visiting any of our properties directly. Online booking is available 24/7 and offers the best rates.",
            "category": "booking",
            "tags": ["reservation", "booking", "online", "phone"],
            "source_url": "https://premieresuites.com/booking"
        },
        {
            "type": "faq",
            "id": "faq_002",
            "question": "What are the check-in and check-out times?",
            "answer": "Check-in time is 3:00 PM and check-out time is 11:00 AM. Early check-in and late check-out may be available upon request, subject to availability.",
            "category": "check-in",
            "tags": ["check-in", "check-out", "times", "early", "late"],
            "source_url": "https://premieresuites.com/check-in"
        },
        {
            "type": "faq",
            "id": "faq_003",
            "question": "Do you allow pets in your properties?",
            "answer": "Yes, we are pet-friendly! We allow up to 2 pets per unit with a non-refundable pet fee of $200 per pet. Please notify us in advance if you plan to bring pets.",
            "category": "pets",
            "tags": ["pets", "pet-friendly", "animals", "fee"],
            "source_url": "https://premieresuites.com/pets"
        },
        {
            "type": "faq",
            "id": "faq_004",
            "question": "What payment methods do you accept?",
            "answer": "We accept all major credit cards (Visa, MasterCard, American Express), debit cards, and bank transfers. Payment is required at the time of booking.",
            "category": "payment",
            "tags": ["payment", "credit card", "debit", "bank transfer"],
            "source_url": "https://premieresuites.com/payment"
        },
        {
            "type": "faq",
            "id": "faq_005",
            "question": "Is smoking allowed in the properties?",
            "answer": "No, all our properties are non-smoking. Smoking is strictly prohibited inside all units and common areas. Violation may result in additional cleaning fees.",
            "category": "policies",
            "tags": ["smoking", "non-smoking", "policy", "fees"],
            "source_url": "https://premieresuites.com/policies"
        },
        {
            "type": "faq",
            "id": "faq_006",
            "question": "Do you offer housekeeping services?",
            "answer": "Yes, we offer weekly housekeeping services for stays of 7 days or longer. Additional cleaning services can be arranged for an extra fee. Daily housekeeping is available upon request.",
            "category": "services",
            "tags": ["housekeeping", "cleaning", "weekly", "daily"],
            "source_url": "https://premieresuites.com/services"
        },
        {
            "type": "faq",
            "id": "faq_007",
            "question": "What amenities are included in my stay?",
            "answer": "All stays include free Wi-Fi, parking, access to fitness centers and pools, 24/7 front desk service, and basic kitchen appliances. Premium amenities vary by property.",
            "category": "amenities",
            "tags": ["amenities", "wifi", "parking", "fitness", "pool"],
            "source_url": "https://premieresuites.com/amenities"
        },
        {
            "type": "faq",
            "id": "faq_008",
            "question": "Can I extend my stay after check-in?",
            "answer": "Yes, you can extend your stay subject to availability. Please contact the front desk at least 24 hours before your scheduled check-out to request an extension.",
            "category": "extensions",
            "tags": ["extend", "stay", "availability", "front desk"],
            "source_url": "https://premieresuites.com/extensions"
        },
        {
            "type": "faq",
            "id": "faq_009",
            "question": "What is your cancellation policy?",
            "answer": "Cancellations made 48 hours or more before check-in receive a full refund. Cancellations within 48 hours are subject to a one-night charge. No-shows are charged the full stay.",
            "category": "cancellation",
            "tags": ["cancellation", "refund", "policy", "no-show"],
            "source_url": "https://premieresuites.com/cancellation"
        },
        {
            "type": "faq",
            "id": "faq_010",
            "question": "Do you have parking available?",
            "answer": "Yes, free parking is available at all our properties. Some locations offer covered parking for an additional fee. Please inquire about parking options when booking.",
            "category": "parking",
            "tags": ["parking", "free", "covered", "fee"],
            "source_url": "https://premieresuites.com/parking"
        }
    ]
    
    # Save to JSONL file
    import json
    with open("sample_faq_data.jsonl", "w") as f:
        for faq in sample_faqs:
            f.write(json.dumps(faq) + "\n")
    
    print(f"✅ Created sample FAQ data with {len(sample_faqs)} entries")
    return "sample_faq_data.jsonl"

def compare_faq_approaches():
    """Compare direct Qdrant vs LangChain approaches for FAQ data."""
    print("🔍 Comparing Direct Qdrant vs LangChain FAQ Approaches")
    print("=" * 60)
    
    # Initialize both approaches
    print("\n1️⃣ Initializing Direct Qdrant Setup...")
    direct_vdb = PremiereSuitesVectorDB(
        collection_name="premiere_suites_faqs_direct"
    )
    
    print("\n2️⃣ Initializing LangChain FAQ Integration...")
    langchain_vdb = LangChainFAQIntegration(
        collection_name="premiere_suites_faqs_langchain"
    )
    
    # Create collections
    print("\n📦 Creating Collections...")
    direct_vdb.create_collection(recreate=True)
    langchain_vdb.create_collection(recreate=True)
    
    # Load sample data
    print("\n📄 Loading Sample FAQ Data...")
    faq_file = create_sample_faq_data()
    
    # Add data using direct approach
    print("\n3️⃣ Adding Data with Direct Qdrant...")
    faqs = direct_vdb.load_data_from_jsonl(faq_file)
    points = direct_vdb.prepare_points(faqs)
    direct_vdb.insert_data(points)
    
    # Add data using LangChain
    print("\n4️⃣ Adding Data with LangChain...")
    documents = langchain_vdb.load_faq_documents_from_jsonl(faq_file)
    langchain_vdb.add_faq_documents(documents)
    
    # Test searches
    print("\n🔍 Testing FAQ Searches...")
    test_queries = [
        "How do I book a room?",
        "Can I bring my dog?",
        "What time can I check in?",
        "Do you have parking?"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 40)
        
        # Direct Qdrant search
        print("Direct Qdrant Results:")
        direct_results = direct_vdb.search_properties(query, limit=3)
        for i, result in enumerate(direct_results, 1):
            print(f"  {i}. Score: {result['score']:.3f} - {result.get('text_chunk', 'N/A')[:50]}...")
        
        # LangChain search
        print("\nLangChain Results:")
        langchain_results = langchain_vdb.search_faqs_with_score(query, k=3)
        for i, (doc, score) in enumerate(langchain_results, 1):
            print(f"  {i}. Score: {score:.3f} - {doc.page_content[:50]}...")
    
    print("\n✅ FAQ comparison completed!")

def langchain_faq_advanced_features():
    """Demonstrate advanced LangChain FAQ features."""
    print("\n🚀 LangChain FAQ Advanced Features")
    print("=" * 50)
    
    # Initialize LangChain integration
    langchain_vdb = LangChainFAQIntegration(
        collection_name="premiere_suites_faqs_advanced"
    )
    
    # Create collection
    langchain_vdb.create_collection(recreate=True)
    
    # Load sample data
    faq_file = create_sample_faq_data()
    documents = langchain_vdb.load_faq_documents_from_jsonl(faq_file)
    langchain_vdb.add_faq_documents(documents)
    
    # Get categories and tags
    print("\n📂 FAQ Categories and Tags:")
    categories = langchain_vdb.get_faq_categories()
    tags = langchain_vdb.get_faq_tags()
    
    print(f"Categories: {', '.join(categories)}")
    print(f"Tags: {', '.join(tags)}")
    
    # Test category filtering
    print("\n🔍 Testing Category Filtering:")
    for category in categories[:3]:  # Test first 3 categories
        print(f"\nCategory: {category}")
        results = langchain_vdb.search_faqs(
            query="booking and reservation",
            k=3,
            category=category
        )
        for i, doc in enumerate(results, 1):
            print(f"  {i}. {doc.metadata.get('question', 'N/A')}")
    
    # Test advanced search with scores
    print("\n📊 Advanced Search with Scores:")
    scored_results = langchain_vdb.search_faqs_with_score(
        query="pet policy and fees",
        k=5,
        min_score=0.3
    )
    
    for i, (doc, score) in enumerate(scored_results, 1):
        print(f"  {i}. Score: {score:.3f}")
        print(f"     Q: {doc.metadata.get('question', 'N/A')}")
        print(f"     A: {doc.metadata.get('answer', 'N/A')[:100]}...")
        print()

def interactive_faq_search():
    """Interactive FAQ search interface."""
    print("\n🔍 Interactive FAQ Search")
    print("=" * 40)
    
    # Initialize integration
    langchain_vdb = LangChainFAQIntegration(
        collection_name="premiere_suites_faqs_interactive"
    )
    
    # Create collection and load data
    langchain_vdb.create_collection(recreate=True)
    faq_file = create_sample_faq_data()
    documents = langchain_vdb.load_faq_documents_from_jsonl(faq_file)
    langchain_vdb.add_faq_documents(documents)
    
    print("Type 'quit' to exit, 'help' for commands")
    
    while True:
        try:
            query = input("\n❓ Enter your FAQ search query: ").strip()
            
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
            results = langchain_vdb.search_faqs_langchain(
                query=query, 
                limit=limit, 
                category=category
            )
            
            # Display results
            if not results:
                print("❌ No results found.")
            else:
                print(f"\n🔍 Found {len(results)} results:")
                print("=" * 80)
                
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result['question']}")
                    print(f"   📊 Similarity Score: {result['score']:.3f}")
                    print(f"   📂 Category: {result['category']}")
                    print(f"   🏷️  Tags: {', '.join(result['tags']) if result['tags'] else 'None'}")
                    print(f"   💬 Answer: {result['answer'][:200]}{'...' if len(result['answer']) > 200 else ''}")
                    print("-" * 80)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function to run the FAQ examples."""
    print("🏠 Premiere Suites - LangChain FAQ Integration Examples")
    print("=" * 70)
    
    try:
        # Check if we have FAQ data
        faq_file = Path("premiere_suites_faq_data.jsonl")
        if faq_file.exists():
            print("✅ Found existing FAQ data file")
            
            # Run with real data
            print("\n📊 Running with Real FAQ Data...")
            langchain_vdb = LangChainFAQIntegration(
                collection_name="premiere_suites_faqs_real"
            )
            
            # Load and add documents
            documents = langchain_vdb.load_faq_documents_from_jsonl(str(faq_file))
            if documents:
                langchain_vdb.create_collection(recreate=True)
                langchain_vdb.add_faq_documents(documents)
                
                # Test search
                print("\n🔍 Testing with Real FAQ Data...")
                results = langchain_vdb.search_faqs_langchain(
                    query="How do I book a reservation?",
                    limit=5
                )
                
                print("Search Results:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['question']} - Score: {result['score']:.3f}")
        else:
            print("📝 No existing FAQ data found, running with sample data...")
        
        # Run comparison
        compare_faq_approaches()
        
        # Run advanced features
        langchain_faq_advanced_features()
        
        # Run interactive search
        interactive_faq_search()
        
        print("\n🎉 All FAQ examples completed successfully!")
        print("\n💡 Key Benefits of LangChain FAQ Integration:")
        print("  • Specialized FAQ search and retrieval")
        print("  • Category and tag-based filtering")
        print("  • Question-answer pair optimization")
        print("  • Easy integration with other LangChain components")
        print("  • Advanced filtering and search capabilities")
        
    except Exception as e:
        print(f"❌ Error running FAQ examples: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())


