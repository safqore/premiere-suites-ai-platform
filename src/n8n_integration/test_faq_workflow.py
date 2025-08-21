#!/usr/bin/env python3
"""
Test FAQ to Qdrant Workflow

This script tests the FAQ to Qdrant workflow by sending a test request.
"""

import requests
import json
import os
from pathlib import Path

def test_workflow():
    """Test the FAQ to Qdrant workflow."""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    n8n_url = os.getenv("N8N_URL", "http://localhost:5678")
    
    # Test webhook endpoint
    webhook_url = f"{n8n_url}/webhook/faq-to-qdrant"
    
    print(f"🔗 Testing webhook: {webhook_url}")
    
    try:
        response = requests.post(
            webhook_url,
            json={"test": True, "timestamp": "2025-01-19T10:00:00Z"},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Workflow executed successfully!")
            try:
                result = response.json()
                print(f"📋 Result: {json.dumps(result, indent=2)}")
            except:
                print(f"📋 Result: {response.text}")
        else:
            print(f"❌ Workflow failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing workflow: {e}")

def test_qdrant_collection():
    """Test if the FAQ collection was created successfully."""
    
    from dotenv import load_dotenv
    load_dotenv()
    
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    if not qdrant_url or not qdrant_api_key:
        print("❌ Qdrant credentials not found")
        return
    
    headers = {"api-key": qdrant_api_key}
    
    try:
        # Check collection info
        response = requests.get(
            f"{qdrant_url}/collections/faq_collection",
            headers=headers
        )
        
        if response.status_code == 200:
            collection_info = response.json()
            print("✅ FAQ collection exists!")
            print(f"📊 Collection info: {json.dumps(collection_info, indent=2)}")
            
            # Get collection stats
            stats_response = requests.get(
                f"{qdrant_url}/collections/faq_collection",
                headers=headers
            )
            
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"📈 Collection stats: {json.dumps(stats, indent=2)}")
        else:
            print(f"❌ FAQ collection not found: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing Qdrant collection: {e}")

if __name__ == "__main__":
    print("🧪 Testing FAQ to Qdrant workflow...")
    test_workflow()
    print("\n🔍 Testing Qdrant collection...")
    test_qdrant_collection()
