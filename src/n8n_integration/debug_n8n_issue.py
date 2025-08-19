#!/usr/bin/env python3
"""
Comprehensive debugging script for n8n FAQ search issue
"""

import os
import json
from dotenv import load_dotenv
from qdrant_setup import PremiereSuitesVectorDB

# Load environment variables
load_dotenv()

def test_exact_n8n_configuration():
    """Test the exact configuration that n8n should be using"""
    print("🔍 Testing Exact n8n Configuration")
    print("=" * 60)
    
    test_query = "What is Premiere Suites Alliance?"
    print(f"Test Query: '{test_query}'")
    
    try:
        # Initialize vector database (same as n8n)
        print("\n1. Initializing vector database...")
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        if not qdrant_url or not qdrant_api_key:
            print("❌ Missing Qdrant credentials!")
            print(f"   QDRANT_URL: {'Set' if qdrant_url else 'Missing'}")
            print(f"   QDRANT_API_KEY: {'Set' if qdrant_api_key else 'Missing'}")
            return False
        
        vdb = PremiereSuitesVectorDB(
            qdrant_url=qdrant_url,
            qdrant_api_key=qdrant_api_key,
            collection_name="premiere_suites_faqs",
            embedding_model="text-embedding-3-small",
            use_cloud=True
        )
        
        # Test collection info
        print("\n2. Testing collection connection...")
        try:
            info = vdb.get_collection_info()
            print(f"   ✅ Collection: {info['name']}")
            print(f"   📊 Vectors: {info['vectors_count']}")
        except Exception as e:
            print(f"   ❌ Collection error: {e}")
            return False
        
        # Test different configurations that n8n might be using
        print("\n3. Testing different n8n configurations...")
        
        configurations = [
            {"score_threshold": 0.3, "top_k": 5, "description": "Recommended (0.3 threshold)"},
            {"score_threshold": 0.5, "top_k": 5, "description": "Default (0.5 threshold)"},
            {"score_threshold": 0.7, "top_k": 5, "description": "High threshold (0.7)"},
            {"score_threshold": 0.8, "top_k": 5, "description": "Very high threshold (0.8)"},
            {"score_threshold": None, "top_k": 5, "description": "No threshold"},
        ]
        
        for config in configurations:
            print(f"\n   Testing: {config['description']}")
            try:
                results = vdb.client.search(
                    collection_name=vdb.collection_name,
                    query_vector=vdb.generate_query_embedding(test_query),
                    limit=config["top_k"],
                    score_threshold=config["score_threshold"]
                )
                
                print(f"   Results: {len(results)}")
                if results:
                    for i, result in enumerate(results, 1):
                        print(f"     {i}. Score: {result.score:.3f} - {result.payload.get('question', 'N/A')}")
                else:
                    print("     ❌ No results (this might be your n8n issue)")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Test with empty query
        print("\n4. Testing with empty query...")
        try:
            results = vdb.client.search(
                collection_name=vdb.collection_name,
                query_vector=vdb.generate_query_embedding(""),
                limit=5,
                score_threshold=0.3
            )
            print(f"   Empty query results: {len(results)}")
        except Exception as e:
            print(f"   Empty query error: {e}")
        
        # Test with very short query
        print("\n5. Testing with short query...")
        try:
            results = vdb.client.search(
                collection_name=vdb.collection_name,
                query_vector=vdb.generate_query_embedding("Alliance"),
                limit=5,
                score_threshold=0.3
            )
            print(f"   Short query results: {len(results)}")
            if results:
                for i, result in enumerate(results, 1):
                    print(f"     {i}. Score: {result.score:.3f} - {result.payload.get('question', 'N/A')}")
        except Exception as e:
            print(f"   Short query error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def check_n8n_credentials():
    """Check if n8n credentials match"""
    print("\n🔑 Checking n8n Credentials")
    print("=" * 60)
    
    # Check environment variables
    env_vars = {
        "QDRANT_URL": os.getenv("QDRANT_URL"),
        "QDRANT_API_KEY": os.getenv("QDRANT_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    }
    
    print("Environment Variables:")
    for var, value in env_vars.items():
        if value:
            # Mask the API key for security
            if "API_KEY" in var:
                masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"   ✅ {var}: {masked_value}")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: Missing")
    
    # Check if these match your n8n credentials
    print("\n📋 n8n Credential Check:")
    print("1. In n8n, verify your Qdrant credentials match:")
    print(f"   - URL: {env_vars['QDRANT_URL']}")
    print(f"   - API Key: {env_vars['QDRANT_API_KEY'][:8]}...{env_vars['QDRANT_API_KEY'][-4:] if env_vars['QDRANT_API_KEY'] else 'Missing'}")
    print("2. Verify your OpenAI API key is valid")
    print("3. Check that collection name is exactly: 'premiere_suites_faqs'")

def generate_n8n_troubleshooting_steps():
    """Generate troubleshooting steps for n8n"""
    print("\n🔧 n8n Troubleshooting Steps")
    print("=" * 60)
    
    print("1. **Check Execution Logs**")
    print("   - Go to n8n execution history")
    print("   - Look for any error messages")
    print("   - Check if the vector store tool is being called")
    
    print("\n2. **Verify Node Configuration**")
    print("   - 'Answer questions with a vector store' node:")
    print("     * Description: '{{ $json.chatInput }}'")
    print("     * Score Threshold: 0.3")
    print("     * Top K: 5")
    
    print("\n3. **Check Data Flow**")
    print("   - Ensure 'Fix Chat Input' node is setting chatInput field")
    print("   - Verify the field is being passed to the vector store tool")
    
    print("\n4. **Test Step by Step**")
    print("   - Test the 'Fix Chat Input' node output")
    print("   - Test the vector store tool with a simple query")
    print("   - Check if the agent receives the tool results")
    
    print("\n5. **Common Issues**")
    print("   - Score threshold too high (> 0.7)")
    print("   - Missing chatInput field")
    print("   - Wrong collection name")
    print("   - Invalid credentials")
    print("   - Network connectivity issues")

def main():
    """Main function"""
    print("🚀 n8n FAQ Search Comprehensive Debug")
    print("=" * 60)
    
    # Run tests
    success = test_exact_n8n_configuration()
    
    if success:
        check_n8n_credentials()
        generate_n8n_troubleshooting_steps()
        
        print("\n🎯 **Most Likely Issues:**")
        print("1. Score threshold in n8n is > 0.7")
        print("2. chatInput field is not being passed correctly")
        print("3. Collection name mismatch")
        print("4. Credential mismatch between environment and n8n")
        
        print("\n📋 **Immediate Actions:**")
        print("1. Check n8n execution logs for errors")
        print("2. Verify scoreThreshold is set to 0.3 in n8n")
        print("3. Ensure chatInput field is being set in 'Fix Chat Input' node")
        print("4. Test with the debug workflow to see exact data flow")
    else:
        print("\n❌ Basic tests failed. Check your configuration.")

if __name__ == "__main__":
    main()
