#!/usr/bin/env python3
"""
Test script to verify the Premier Suites Concierge FAQ functionality
"""

import requests
import json
import time

def test_concierge_faq(webhook_url: str):
    """Test the concierge's ability to answer FAQ questions"""
    
    # Test questions that should use the knowledge base
    faq_questions = [
        "What is Premiere Suites Alliance?",
        "Tell me about Premier Suites services",
        "What locations does Premier Suites have?",
        "What are the check-in and check-out times?",
        "Do you offer long-term stays?",
        "What amenities are included?",
        "How do I contact Premier Suites?",
        "What is your cancellation policy?",
        "Do you have pet-friendly accommodations?",
        "What types of rooms do you offer?"
    ]
    
    print("🧪 Testing FAQ Functionality")
    print("=" * 50)
    
    for i, question in enumerate(faq_questions, 1):
        print(f"\n📝 FAQ Question {i}: {question}")
        
        try:
            response = requests.post(
                webhook_url,
                json={"text": question},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('text', 'No response text')
                print(f"🤖 Response: {response_text[:200]}...")
                
                # Check if response indicates knowledge base usage
                if "don't know" in response_text.lower() or "i don't" in response_text.lower():
                    print("⚠️  WARNING: Response suggests knowledge base not being used properly")
                else:
                    print("✅ Response appears to use knowledge base")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error sending question: {e}")
        
        time.sleep(1)  # Small delay between questions

def test_lead_qualification(webhook_url: str):
    """Test the lead qualification flow"""
    
    print("\n\n🧪 Testing Lead Qualification Flow")
    print("=" * 50)
    
    qualification_messages = [
        "Hi, I want to book accommodation",
        "My name is John Smith",
        "john.smith@email.com",
        "I want to stay in New York",
        "Check-in March 1st, check-out April 1st",
        "2 bedrooms for 4 guests",
        "My budget is $2,500 per month"
    ]
    
    for i, message in enumerate(qualification_messages, 1):
        print(f"\n📝 Message {i}: {message}")
        
        try:
            response = requests.post(
                webhook_url,
                json={"text": message},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('text', 'No response text')
                print(f"🤖 Response: {response_text[:200]}...")
                
                # Check if response follows qualification flow
                if any(keyword in response_text.lower() for keyword in ['email', 'city', 'dates', 'guests', 'budget']):
                    print("✅ Response follows qualification flow")
                else:
                    print("⚠️  Response may not be following qualification flow")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error sending message: {e}")
        
        time.sleep(1)

def main():
    print("🚀 Premier Suites Concierge - FAQ & Qualification Test")
    print("=" * 60)
    
    # Get webhook URL from user
    webhook_url = input("Enter your n8n webhook URL: ").strip()
    
    if not webhook_url:
        print("❌ No webhook URL provided. Exiting.")
        return
    
    # Test FAQ functionality
    test_concierge_faq(webhook_url)
    
    # Test lead qualification
    test_lead_qualification(webhook_url)
    
    print("\n✅ Testing complete!")
    print("\n📋 Summary:")
    print("- FAQ questions should use the knowledge base and provide informative answers")
    print("- Lead qualification should follow the structured flow")
    print("- The concierge should be able to handle both types of interactions")

if __name__ == "__main__":
    main()
