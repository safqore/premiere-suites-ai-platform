#!/usr/bin/env python3
"""
FAQ Vectorization Setup Script

This script helps you set up the FAQ vectorization environment.
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    # Define package names and their import names
    required_packages = {
        'qdrant_client': 'qdrant_client',
        'sentence_transformers': 'sentence_transformers',
        'python-dotenv': 'dotenv'  # The import name is 'dotenv', not 'python_dotenv'
    }
    
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} (missing)")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n📦 Install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def check_env_file():
    """Check if .env file exists and is configured."""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("\n📝 .env file not found. Creating template...")
        
        # Copy from example if it exists
        example_file = Path("env.example")
        if example_file.exists():
            with open(example_file, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("✅ Created .env file from template")
            print("📝 Please edit .env with your Qdrant Cloud credentials")
            return False
        else:
            # Create basic template
            with open(env_file, 'w') as f:
                f.write("# Qdrant Cloud Configuration\n")
                f.write("QDRANT_URL=https://your-cluster.qdrant.io\n")
                f.write("QDRANT_API_KEY=your-api-key-here\n")
            
            print("✅ Created basic .env file")
            print("📝 Please edit .env with your Qdrant Cloud credentials")
            return False
    
    # Check if .env has actual credentials
    with open(env_file, 'r') as f:
        content = f.read()
    
    if "your-cluster.qdrant.io" in content or "your-api-key-here" in content:
        print("\n⚠️  .env file exists but contains placeholder values")
        print("📝 Please edit .env with your actual Qdrant Cloud credentials")
        return False
    
    print("✅ .env file is configured")
    return True

def test_qdrant_connection():
    """Test connection to Qdrant (local or cloud)."""
    print("\n🔗 Testing Qdrant connection...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        if qdrant_url and qdrant_api_key:
            print("🌐 Testing Qdrant Cloud connection...")
            from qdrant_client import QdrantClient
            
            client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
            collections = client.get_collections()
            print(f"✅ Connected to Qdrant Cloud: {qdrant_url}")
            print(f"📊 Found {len(collections.collections)} collections")
            return True
        else:
            print("🏠 Testing local Qdrant connection...")
            from qdrant_client import QdrantClient
            
            try:
                client = QdrantClient(host="localhost", port=6333)
                collections = client.get_collections()
                print("✅ Connected to local Qdrant instance")
                print(f"📊 Found {len(collections.collections)} collections")
                return True
            except Exception as e:
                print("❌ Local Qdrant not accessible")
                print("💡 Start Qdrant with: docker run -p 6333:6333 qdrant/qdrant")
                return False
                
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def check_faq_data():
    """Check if FAQ data file exists."""
    print("\n📄 Checking FAQ data...")
    
    faq_file = Path("premiere_suites_faq_data.jsonl")
    
    if not faq_file.exists():
        print("❌ FAQ data file not found: premiere_suites_faq_data.jsonl")
        print("💡 Make sure you have the FAQ data file in the current directory")
        return False
    
    # Count FAQ entries
    faq_count = 0
    with open(faq_file, 'r') as f:
        for line in f:
            if line.strip() and '"type": "faq"' in line:
                faq_count += 1
    
    print(f"✅ FAQ data file found with {faq_count} entries")
    return True

def setup_instructions():
    """Show setup instructions."""
    print("\n📋 Setup Instructions")
    print("=" * 50)
    
    print("\n1. 🌐 Get Qdrant Cloud credentials:")
    print("   - Go to https://cloud.qdrant.io/")
    print("   - Create a free account")
    print("   - Create a new cluster")
    print("   - Copy your cluster URL and API key")
    
    print("\n2. 📝 Configure .env file:")
    print("   - Edit .env file with your credentials")
    print("   - Replace placeholder values with actual values")
    
    print("\n3. 🚀 Vectorize FAQ data:")
    print("   python vectorize_faq_data.py")
    
    print("\n4. 🔍 Search FAQ data:")
    print("   python search_faqs.py")
    
    print("\n💡 Alternative: Use local Qdrant")
    print("   docker run -p 6333:6333 qdrant/qdrant")

def main():
    """Main setup function."""
    print("🏠 Premiere Suites FAQ Vectorization Setup")
    print("=" * 50)
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check FAQ data
    data_ok = check_faq_data()
    
    # Check .env configuration
    env_ok = check_env_file()
    
    # Test connection
    connection_ok = test_qdrant_connection()
    
    # Summary
    print("\n📊 Setup Summary")
    print("=" * 50)
    print(f"Dependencies: {'✅' if deps_ok else '❌'}")
    print(f"FAQ Data: {'✅' if data_ok else '❌'}")
    print(f"Environment: {'✅' if env_ok else '❌'}")
    print(f"Connection: {'✅' if connection_ok else '❌'}")
    
    if deps_ok and data_ok and env_ok and connection_ok:
        print("\n🎉 Setup is complete! You can now:")
        print("   python vectorize_faq_data.py")
        print("   python search_faqs.py")
    else:
        print("\n⚠️  Setup incomplete. Please fix the issues above.")
        setup_instructions()
    
    return 0

if __name__ == "__main__":
    exit(main())
