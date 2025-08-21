#!/usr/bin/env python3
"""
Check and fix content in Qdrant FAQ collection
"""

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# Load environment variables
load_dotenv()

def check_content():
    """Check the current content in the FAQ collection."""
    client = QdrantClient(url=os.getenv('QDRANT_URL'), api_key=os.getenv('QDRANT_API_KEY'))
    
    # Get all points
    points = client.scroll(collection_name='premiere_suites_faqs', limit=100, with_payload=True)[0]
    print(f"Total points found: {len(points)}")
    
    # Check content for each point
    empty_content_count = 0
    for i, point in enumerate(points[:5]):  # Check first 5 points
        print(f"\nPoint {i+1}:")
        print(f"  ID: {point.id}")
        
        content = point.payload.get('content', 'NOT FOUND')
        print(f"  content: {content}")
        
        if not content or content == 'NOT FOUND':
            empty_content_count += 1
            print(f"  ❌ content is empty or missing")
        else:
            print(f"  ✅ content has content: {content[:100]}...")
        
        # Check other fields
        metadata = point.payload.get('metadata', {})
        print(f"  metadata keys: {list(metadata.keys()) if metadata else 'NOT FOUND'}")
        
        # Check if we have the original FAQ data
        question = point.payload.get('question', 'NOT FOUND')
        answer = point.payload.get('answer', 'NOT FOUND')
        print(f"  question: {question[:50] if question != 'NOT FOUND' else 'NOT FOUND'}...")
        print(f"  answer: {answer[:50] if answer != 'NOT FOUND' else 'NOT FOUND'}...")
    
    print(f"\nSummary: {empty_content_count} out of {min(5, len(points))} points have empty content")
    return empty_content_count > 0

def fix_content():
    """Fix empty content by updating the points with proper content."""
    client = QdrantClient(url=os.getenv('QDRANT_URL'), api_key=os.getenv('QDRANT_API_KEY'))
    
    # Get all points
    points = client.scroll(collection_name='premiere_suites_faqs', limit=100, with_payload=True)[0]
    print(f"Fixing content for {len(points)} points...")
    
    # Prepare updates
    updates = []
    for point in points:
        # Get the question and answer from the payload
        question = point.payload.get('question', '')
        answer = point.payload.get('answer', '')
        
        # Create proper content
        if question and answer:
            content = f"Q: {question}\nA: {answer}"
        elif question:
            content = f"Q: {question}"
        elif answer:
            content = f"A: {answer}"
        else:
            content = f"FAQ ID: {point.id}"
        
        # Create updated payload
        updated_payload = point.payload.copy()
        updated_payload['content'] = content
        
        # Add to updates
        updates.append({
            'id': point.id,
            'payload': updated_payload
        })
    
    # Update points in batches
    batch_size = 10
    for i in range(0, len(updates), batch_size):
        batch = updates[i:i + batch_size]
        client.set_payload(
            collection_name='premiere_suites_faqs',
            payload=batch,
            wait=True
        )
        print(f"Updated batch {i//batch_size + 1}/{(len(updates) + batch_size - 1)//batch_size}")
    
    print("✅ content fixed for all points!")

def main():
    """Main function."""
    print("🔍 Checking content in FAQ collection...")
    
    has_empty_content = check_content()
    
    if has_empty_content:
        print("\n🔧 Fixing empty content...")
        fix_content()
        
        print("\n🔍 Verifying fix...")
        check_content()
    else:
        print("\n✅ All content fields are properly set!")

if __name__ == "__main__":
    main()
