#!/usr/bin/env python3
"""
Deploy FAQ to Qdrant Workflow

This script deploys the FAQ to Qdrant workflow to n8n.
"""

import json
import requests
import os
from pathlib import Path

def deploy_workflow():
    """Deploy the workflow to n8n."""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    n8n_url = os.getenv("N8N_URL", "http://localhost:5678")
    n8n_api_key = os.getenv("N8N_API_KEY")
    
    if not n8n_api_key:
        print("❌ N8N_API_KEY environment variable is required")
        return False
    
    # Load workflow
    workflow_file = Path("docs/workflows/faq_to_qdrant_workflow.json")
    if not workflow_file.exists():
        print(f"❌ Workflow file not found: {workflow_file}")
        return False
    
    with open(workflow_file, "r") as f:
        workflow = json.load(f)
    
    # Deploy to n8n
    headers = {
        "X-N8N-API-KEY": n8n_api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{n8n_url}/api/v1/workflows",
            json=workflow,
            headers=headers
        )
        
        if response.status_code == 201:
            print("✅ Workflow deployed successfully!")
            print(f"   Workflow ID: {response.json().get('id')}")
            print(f"   Webhook URL: {n8n_url}/webhook/faq-to-qdrant")
            return True
        else:
            print(f"❌ Failed to deploy workflow: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error deploying workflow: {e}")
        return False

if __name__ == "__main__":
    deploy_workflow()
