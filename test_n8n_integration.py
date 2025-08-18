#!/usr/bin/env python3
"""
Test n8n Integration with Qdrant Cloud

This script tests the n8n integration components to ensure everything works correctly.
"""

import os
import json
import requests
import time
from pathlib import Path

def load_environment():
    """Load environment variables from .env file."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

def test_qdrant_connection():
    """Test connection to Qdrant Cloud."""
    print("🔍 Testing Qdrant Cloud connection...")
    
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    if not qdrant_url or not qdrant_api_key:
        print("❌ Qdrant Cloud credentials not found")
        return False
    
    try:
        # Test health endpoint
        response = requests.get(f"{qdrant_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Qdrant Cloud is accessible")
            return True
        else:
            print(f"❌ Qdrant Cloud health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to Qdrant Cloud: {e}")
        return False

def test_embedding_service():
    """Test the embedding service."""
    print("\n🧠 Testing embedding service...")
    
    try:
        # Test if embedding service is running
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Embedding service is running")
            
            # Test embedding generation
            test_text = "luxury apartment with pool"
            response = requests.post(
                "http://localhost:5000/generate-embedding",
                json={"text": test_text},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "embedding" in data and len(data["embedding"]) == 384:
                    print("✅ Embedding generation works correctly")
                    return True
                else:
                    print("❌ Invalid embedding format")
                    return False
            else:
                print(f"❌ Embedding generation failed: {response.status_code}")
                return False
        else:
            print(f"❌ Embedding service health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Embedding service is not running")
        print("   Start it with: docker-compose -f docker-compose.n8n.yml up embedding-service")
        return False
    except Exception as e:
        print(f"❌ Embedding service test failed: {e}")
        return False

def test_n8n_webhook():
    """Test n8n webhook endpoints."""
    print("\n🔗 Testing n8n webhook endpoints...")
    
    try:
        # Test if n8n is running
        response = requests.get("http://localhost:5678/healthz", timeout=5)
        if response.status_code == 200:
            print("✅ n8n is running")
            
            # Test property search webhook
            test_data = {
                "query": "luxury apartment with pool",
                "limit": 3,
                "city": "Toronto"
            }
            
            response = requests.post(
                "http://localhost:5678/webhook/property-search",
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "results" in data:
                    print("✅ Property search webhook works")
                    print(f"   Found {len(data['results'])} properties")
                    return True
                else:
                    print("❌ Invalid webhook response format")
                    return False
            else:
                print(f"❌ Webhook test failed: {response.status_code}")
                return False
        else:
            print(f"❌ n8n health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ n8n is not running")
        print("   Start it with: docker-compose -f docker-compose.n8n.yml up n8n")
        return False
    except Exception as e:
        print(f"❌ n8n webhook test failed: {e}")
        return False

def test_property_search():
    """Test direct property search functionality."""
    print("\n🏠 Testing property search functionality...")
    
    try:
        from qdrant_setup import PremiereSuitesVectorDB
        
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        vdb = PremiereSuitesVectorDB(
            qdrant_url=qdrant_url,
            qdrant_api_key=qdrant_api_key,
            use_cloud=True
        )
        
        # Test basic search
        results = vdb.search_properties(
            query="luxury apartment with pool",
            limit=3
        )
        
        if results:
            print("✅ Property search works correctly")
            print(f"   Found {len(results)} properties")
            
            # Test filtered search
            filtered_results = vdb.search_properties(
                query="apartment",
                city="Toronto",
                min_rating=4.0,
                limit=2
            )
            
            if filtered_results:
                print("✅ Filtered search works correctly")
                print(f"   Found {len(filtered_results)} filtered properties")
                return True
            else:
                print("❌ Filtered search failed")
                return False
        else:
            print("❌ No search results returned")
            return False
            
    except Exception as e:
        print(f"❌ Property search test failed: {e}")
        return False

def test_workflow_files():
    """Test that workflow files exist and are valid JSON."""
    print("\n📋 Testing workflow files...")
    
    workflow_files = [
        "n8n_property_search_workflow.json",
        "n8n_property_filter_workflow.json"
    ]
    
    for filename in workflow_files:
        if Path(filename).exists():
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                if "name" in data and "nodes" in data:
                    print(f"✅ {filename} is valid")
                else:
                    print(f"❌ {filename} has invalid structure")
                    return False
            except json.JSONDecodeError:
                print(f"❌ {filename} is not valid JSON")
                return False
        else:
            print(f"❌ {filename} not found")
            return False
    
    return True

def test_docker_files():
    """Test that Docker files exist."""
    print("\n🐳 Testing Docker files...")
    
    docker_files = [
        "docker-compose.n8n.yml",
        "Dockerfile.embedding"
    ]
    
    for filename in docker_files:
        if Path(filename).exists():
            print(f"✅ {filename} exists")
        else:
            print(f"❌ {filename} not found")
            return False
    
    return True

def main():
    """Main test function."""
    print("🧪 n8n Integration Test Suite")
    print("=" * 50)
    
    load_environment()
    
    tests = [
        ("Qdrant Cloud Connection", test_qdrant_connection),
        ("Property Search", test_property_search),
        ("Workflow Files", test_workflow_files),
        ("Docker Files", test_docker_files),
        ("Embedding Service", test_embedding_service),
        ("n8n Webhooks", test_n8n_webhook)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your n8n integration is ready to use.")
        print("\nNext steps:")
        print("1. Start n8n: docker-compose -f docker-compose.n8n.yml up -d")
        print("2. Access n8n at: http://localhost:5678")
        print("3. Import the workflow files")
        print("4. Test your integrations")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the issues above.")
        print("\nTroubleshooting:")
        print("1. Ensure Qdrant Cloud is set up correctly")
        print("2. Check that all environment variables are set")
        print("3. Verify Docker services are running")
        print("4. Review the error messages above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
