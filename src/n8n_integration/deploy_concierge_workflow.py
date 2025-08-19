#!/usr/bin/env python3
"""
Deploy and test the Premier Suites Booking Concierge workflow
"""

import json
import requests
import time
from typing import Dict, Any

class N8NConciergeDeployer:
    def __init__(self, n8n_base_url: str = "http://localhost:5678"):
        self.n8n_base_url = n8n_base_url.rstrip('/')
        self.api_url = f"{self.n8n_base_url}/api/v1"
        
    def deploy_workflow(self, workflow_file: str) -> Dict[str, Any]:
        """Deploy a workflow to n8n"""
        try:
            with open(workflow_file, 'r') as f:
                workflow_data = json.load(f)
            
            # Create the workflow
            response = requests.post(
                f"{self.api_url}/workflows",
                json=workflow_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                workflow = response.json()
                print(f"✅ Workflow deployed successfully: {workflow['name']}")
                print(f"   ID: {workflow['id']}")
                return workflow
            else:
                print(f"❌ Failed to deploy workflow: {response.status_code}")
                print(f"   Response: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Error deploying workflow: {e}")
            return {}
    
    def activate_workflow(self, workflow_id: str) -> bool:
        """Activate a workflow"""
        try:
            response = requests.post(f"{self.api_url}/workflows/{workflow_id}/activate")
            
            if response.status_code == 200:
                print(f"✅ Workflow activated: {workflow_id}")
                return True
            else:
                print(f"❌ Failed to activate workflow: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error activating workflow: {e}")
            return False
    
    def get_webhook_url(self, workflow_id: str) -> str:
        """Get the webhook URL for a workflow"""
        try:
            response = requests.get(f"{self.api_url}/workflows/{workflow_id}")
            
            if response.status_code == 200:
                workflow = response.json()
                webhook_id = None
                
                # Find the webhook trigger node
                for node in workflow.get('nodes', []):
                    if node.get('type') == '@n8n/n8n-nodes-langchain.chatTrigger':
                        webhook_id = node.get('parameters', {}).get('webhookId')
                        break
                
                if webhook_id:
                    webhook_url = f"{self.n8n_base_url}/webhook/{webhook_id}"
                    print(f"🌐 Webhook URL: {webhook_url}")
                    return webhook_url
                else:
                    print("❌ No webhook found in workflow")
                    return ""
            else:
                print(f"❌ Failed to get workflow: {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"❌ Error getting webhook URL: {e}")
            return ""
    
    def test_conversation(self, webhook_url: str) -> None:
        """Test the conversation flow"""
        if not webhook_url:
            print("❌ No webhook URL provided")
            return
        
        test_messages = [
            "Hi, I'm John Smith",
            "john.smith@email.com",
            "I'm looking to stay in New York",
            "Check-in on March 1st, check-out on April 1st",
            "I need 2 bedrooms for 4 guests",
            "My budget is $2,500 per month"
        ]
        
        print("\n🧪 Testing conversation flow...")
        print("=" * 50)
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n📝 Message {i}: {message}")
            
            try:
                response = requests.post(
                    webhook_url,
                    json={"text": message},
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"🤖 Response: {result.get('text', 'No response text')}")
                else:
                    print(f"❌ Error: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error sending message: {e}")
            
            time.sleep(1)  # Small delay between messages
    
    def test_disqualification(self, webhook_url: str) -> None:
        """Test the disqualification flow (low budget)"""
        if not webhook_url:
            print("❌ No webhook URL provided")
            return
        
        test_messages = [
            "Hi, I'm Jane Doe",
            "jane.doe@email.com", 
            "I want to stay in Miami",
            "Check-in March 1st, check-out March 5th",
            "Just 1 bedroom for 2 people",
            "My budget is $800 per month"
        ]
        
        print("\n🧪 Testing disqualification flow (low budget)...")
        print("=" * 50)
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n📝 Message {i}: {message}")
            
            try:
                response = requests.post(
                    webhook_url,
                    json={"text": message},
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"🤖 Response: {result.get('text', 'No response text')}")
                else:
                    print(f"❌ Error: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error sending message: {e}")
            
            time.sleep(1)

def main():
    print("🚀 Premier Suites Booking Concierge - Deployment Script")
    print("=" * 60)
    
    # Initialize deployer
    deployer = N8NConciergeDeployer()
    
    # Deploy the simple concierge workflow
    print("\n📦 Deploying Simple Concierge Workflow...")
    workflow = deployer.deploy_workflow("n8n_simple_concierge_workflow.json")
    
    if not workflow:
        print("❌ Deployment failed. Exiting.")
        return
    
    # Activate the workflow
    print("\n🔌 Activating workflow...")
    if not deployer.activate_workflow(workflow['id']):
        print("❌ Activation failed. Exiting.")
        return
    
    # Get webhook URL
    print("\n🔗 Getting webhook URL...")
    webhook_url = deployer.get_webhook_url(workflow['id'])
    
    if not webhook_url:
        print("❌ Could not get webhook URL. Exiting.")
        return
    
    # Test the conversation flow
    print("\n" + "=" * 60)
    deployer.test_conversation(webhook_url)
    
    # Test disqualification flow
    print("\n" + "=" * 60)
    deployer.test_disqualification(webhook_url)
    
    print("\n✅ Deployment and testing complete!")
    print(f"🌐 Your concierge is available at: {webhook_url}")

if __name__ == "__main__":
    main()
