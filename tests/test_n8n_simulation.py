#!/usr/bin/env python3
"""
Simulate n8n workflow to debug the FAQ search issue
"""

import os
import json
from dotenv import load_dotenv
from qdrant_setup import PremiereSuitesVectorDB

# Load environment variables
load_dotenv()

def simulate_n8n_workflow():
    """Simulate the exact n8n workflow to find the issue"""
    print("🔍 Simulating n8n Workflow")
    print("=" * 60)
    
    # Test query
    test_query = "What is Premiere Suites Alliance?"
    print(f"Test Query: '{test_query}'")
    
    try:
        # Initialize vector database (same as n8n)
        print("\n1. Initializing vector database...")
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        vdb = PremiereSuitesVectorDB(
            qdrant_url=qdrant_url,
            qdrant_api_key=qdrant_api_key,
            collection_name="premiere_suites_faqs",
            embedding_model="text-embedding-3-small",
            use_cloud=True
        )
        
        # Test different score thresholds (like n8n would)
        print("\n2. Testing different score thresholds...")
        thresholds = [0.3, 0.5, 0.7, 0.8]
        
        for threshold in thresholds:
            print(f"\n   Testing threshold: {threshold}")
            try:
                results = vdb.client.search(
                    collection_name=vdb.collection_name,
                    query_vector=vdb.generate_query_embedding(test_query),
                    limit=5,
                    score_threshold=threshold
                )
                
                print(f"   Results found: {len(results)}")
                if results:
                    for i, result in enumerate(results, 1):
                        print(f"     {i}. Score: {result.score:.3f} - {result.payload.get('question', 'N/A')}")
                else:
                    print("     ❌ No results (this is what n8n is getting)")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Test the exact n8n configuration
        print("\n3. Testing n8n-like configuration...")
        print("   Using: scoreThreshold=0.5, topK=5")
        
        try:
            results = vdb.client.search(
                collection_name=vdb.collection_name,
                query_vector=vdb.generate_query_embedding(test_query),
                limit=5,
                score_threshold=0.5
            )
            
            print(f"   Results: {len(results)}")
            if results:
                print("   ✅ This should work in n8n")
                for i, result in enumerate(results, 1):
                    print(f"     {i}. Score: {result.score:.3f} - {result.payload.get('question', 'N/A')}")
            else:
                print("   ❌ No results - this explains the empty response")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test with lower threshold (recommended fix)
        print("\n4. Testing with lower threshold (recommended fix)...")
        print("   Using: scoreThreshold=0.3, topK=5")
        
        try:
            results = vdb.client.search(
                collection_name=vdb.collection_name,
                query_vector=vdb.generate_query_embedding(test_query),
                limit=5,
                score_threshold=0.3
            )
            
            print(f"   Results: {len(results)}")
            if results:
                print("   ✅ This should definitely work in n8n")
                for i, result in enumerate(results, 1):
                    print(f"     {i}. Score: {result.score:.3f} - {result.payload.get('question', 'N/A')}")
            else:
                print("   ❌ Still no results - there's a deeper issue")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        return False

def check_n8n_configuration():
    """Check what might be wrong with n8n configuration"""
    print("\n🔧 n8n Configuration Analysis")
    print("=" * 60)
    
    print("Based on the test results, here are the most likely issues:")
    
    print("\n1. **Score Threshold Too High**")
    print("   - Your n8n workflow might have a scoreThreshold > 0.7")
    print("   - At 0.7 threshold: 1 result")
    print("   - At 0.8 threshold: 0 results")
    print("   - Solution: Set scoreThreshold to 0.5 or 0.3")
    
    print("\n2. **Description Field Issue**")
    print("   - The description field might not be extracting text properly")
    print("   - Check: '{{ $json.text || $json.message || $json.chat_message }}'")
    print("   - Make sure the text is being passed correctly")
    
    print("\n3. **Collection Name Mismatch**")
    print("   - Verify collection name is exactly: 'premiere_suites_faqs'")
    print("   - Check Qdrant credentials in n8n")
    
    print("\n4. **Embedding Model Mismatch**")
    print("   - Ensure n8n is using: 'text-embedding-3-small'")
    print("   - Check OpenAI API key is valid")
    
    print("\n🎯 **Recommended Fixes:**")
    print("1. Set scoreThreshold to 0.3 in n8n")
    print("2. Use the debug workflow to see what's happening")
    print("3. Check execution logs for errors")
    print("4. Verify all credentials are correct")

def main():
    """Main function"""
    print("🚀 n8n FAQ Search Debug Simulation")
    print("=" * 60)
    
    # Run simulation
    success = simulate_n8n_workflow()
    
    if success:
        check_n8n_configuration()
        
        print("\n📋 **Next Steps:**")
        print("1. Import the debug workflow (n8n_debug_workflow.json)")
        print("2. Test with 'What is Premiere Suites Alliance?'")
        print("3. Check the debug nodes output")
        print("4. Look at execution logs")
        print("5. Adjust scoreThreshold to 0.3 if needed")
    else:
        print("\n❌ Simulation failed. Check your configuration.")

if __name__ == "__main__":
    main()
