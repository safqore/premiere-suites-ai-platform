#!/usr/bin/env python3
"""
FAQ to Qdrant Workflow Example

This example demonstrates how to use the FAQ to Qdrant n8n workflow
programmatically, including triggering the workflow and monitoring its execution.
"""

import requests
import json
import time
import os
from datetime import datetime
from pathlib import Path

def load_environment():
    """Load environment variables."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

def trigger_faq_workflow(webhook_url, payload=None):
    """
    Trigger the FAQ to Qdrant workflow.
    
    Args:
        webhook_url: The n8n webhook URL
        payload: Optional payload to send with the request
    
    Returns:
        dict: Response from the workflow
    """
    if payload is None:
        payload = {
            "trigger": "programmatic",
            "timestamp": datetime.now().isoformat(),
            "source": "example_script"
        }
    
    print(f"🔗 Triggering FAQ workflow at: {webhook_url}")
    print(f"📤 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=300  # 5 minute timeout
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Workflow executed successfully!")
            print(f"📋 Result: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"❌ Workflow failed: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("⏰ Workflow timed out (took longer than 5 minutes)")
        return None
    except Exception as e:
        print(f"❌ Error triggering workflow: {e}")
        return None

def monitor_workflow_execution(webhook_url, max_attempts=3):
    """
    Monitor workflow execution with retries.
    
    Args:
        webhook_url: The n8n webhook URL
        max_attempts: Maximum number of retry attempts
    
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"🔄 Monitoring workflow execution (max {max_attempts} attempts)...")
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n📋 Attempt {attempt}/{max_attempts}")
        
        result = trigger_faq_workflow(webhook_url)
        
        if result:
            return True
        
        if attempt < max_attempts:
            wait_time = 30 * attempt  # Exponential backoff
            print(f"⏳ Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)
    
    print("❌ All attempts failed")
    return False

def verify_qdrant_collection():
    """
    Verify that the FAQ collection was created in Qdrant.
    
    Returns:
        bool: True if collection exists and has data, False otherwise
    """
    try:
        from qdrant_client import QdrantClient
        
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        if not qdrant_url or not qdrant_api_key:
            print("❌ Qdrant credentials not found in environment")
            return False
        
        print("🔍 Verifying Qdrant collection...")
        
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        
        # Check if collection exists
        try:
            collection_info = client.get_collection("faq_collection")
            print("✅ FAQ collection exists!")
            print(f"📊 Collection info: {json.dumps(collection_info.dict(), indent=2)}")
            
            # Get collection stats
            stats = client.get_collection("faq_collection")
            print(f"📈 Collection stats: {json.dumps(stats.dict(), indent=2)}")
            
            # Try a simple search
            search_result = client.search(
                collection_name="faq_collection",
                query_vector=[0.1] * 1536,  # Dummy vector
                limit=1
            )
            
            if search_result:
                print(f"✅ Collection has {len(search_result)} FAQ(s)")
                return True
            else:
                print("⚠️  Collection exists but appears to be empty")
                return False
                
        except Exception as e:
            print(f"❌ Error accessing collection: {e}")
            return False
            
    except ImportError:
        print("❌ qdrant-client not installed. Install with: pip install qdrant-client")
        return False
    except Exception as e:
        print(f"❌ Error verifying collection: {e}")
        return False

def search_faqs(query_text, limit=5):
    """
    Search FAQs using the Qdrant collection.
    
    Args:
        query_text: Text to search for
        limit: Maximum number of results to return
    
    Returns:
        list: Search results
    """
    try:
        from qdrant_client import QdrantClient
        import openai
        
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not all([qdrant_url, qdrant_api_key, openai_api_key]):
            print("❌ Missing required credentials")
            return []
        
        print(f"🔍 Searching FAQs for: '{query_text}'")
        
        # Get embedding for query
        openai.api_key = openai_api_key
        response = openai.Embedding.create(
            input=query_text,
            model="text-embedding-3-small"
        )
        query_vector = response['data'][0]['embedding']
        
        # Search in Qdrant
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        
        search_result = client.search(
            collection_name="faq_collection",
            query_vector=query_vector,
            limit=limit
        )
        
        print(f"✅ Found {len(search_result)} results:")
        
        for i, result in enumerate(search_result, 1):
            print(f"\n{i}. Score: {result.score:.4f}")
            print(f"   Question: {result.payload.get('question', 'N/A')}")
            print(f"   Answer: {result.payload.get('answer', 'N/A')[:100]}...")
            print(f"   Category: {result.payload.get('category', 'N/A')}")
        
        return search_result
        
    except Exception as e:
        print(f"❌ Error searching FAQs: {e}")
        return []

def main():
    """Main example function."""
    print("🚀 FAQ to Qdrant Workflow Example")
    print("=" * 50)
    
    # Load environment
    load_environment()
    
    # Get webhook URL
    n8n_url = os.getenv("N8N_URL", "http://localhost:5678")
    webhook_url = f"{n8n_url}/webhook/faq-to-qdrant"
    
    print(f"🌐 n8n URL: {n8n_url}")
    print(f"🔗 Webhook URL: {webhook_url}")
    
    # Check if required environment variables are set
    required_vars = ["QDRANT_URL", "QDRANT_API_KEY", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        return
    
    print("✅ All required environment variables are set")
    
    # Example 1: Simple workflow trigger
    print("\n" + "=" * 50)
    print("Example 1: Simple Workflow Trigger")
    print("=" * 50)
    
    result = trigger_faq_workflow(webhook_url)
    
    if result:
        print("✅ Example 1 completed successfully!")
    else:
        print("❌ Example 1 failed")
        return
    
    # Example 2: Workflow with custom payload
    print("\n" + "=" * 50)
    print("Example 2: Workflow with Custom Payload")
    print("=" * 50)
    
    custom_payload = {
        "trigger": "custom_example",
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "source": "example_script",
            "version": "1.0",
            "description": "Custom payload example"
        }
    }
    
    result = trigger_faq_workflow(webhook_url, custom_payload)
    
    if result:
        print("✅ Example 2 completed successfully!")
    else:
        print("❌ Example 2 failed")
    
    # Example 3: Monitor workflow with retries
    print("\n" + "=" * 50)
    print("Example 3: Monitor Workflow with Retries")
    print("=" * 50)
    
    success = monitor_workflow_execution(webhook_url, max_attempts=2)
    
    if success:
        print("✅ Example 3 completed successfully!")
    else:
        print("❌ Example 3 failed")
    
    # Example 4: Verify Qdrant collection
    print("\n" + "=" * 50)
    print("Example 4: Verify Qdrant Collection")
    print("=" * 50)
    
    collection_exists = verify_qdrant_collection()
    
    if collection_exists:
        print("✅ Example 4 completed successfully!")
    else:
        print("❌ Example 4 failed")
    
    # Example 5: Search FAQs
    print("\n" + "=" * 50)
    print("Example 5: Search FAQs")
    print("=" * 50)
    
    if collection_exists:
        # Search for different types of questions
        search_queries = [
            "How do I book a reservation?",
            "What is included in the apartment?",
            "Can I bring my pet?",
            "What are the check-in times?",
            "Do you offer parking?"
        ]
        
        for query in search_queries:
            print(f"\n🔍 Searching: '{query}'")
            results = search_faqs(query, limit=3)
            
            if results:
                print(f"✅ Found {len(results)} relevant FAQs")
            else:
                print("❌ No results found")
    else:
        print("⚠️  Skipping search example - collection not available")
    
    print("\n" + "=" * 50)
    print("🎉 Example completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()


