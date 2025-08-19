#!/usr/bin/env python3
"""
Qdrant Cloud Setup for Premiere Suites Property Data

This script helps you set up Qdrant Cloud for your property data.
"""

import os
import sys
from pathlib import Path

def check_environment_variables():
    """Check if Qdrant Cloud environment variables are set."""
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    if not qdrant_url:
        print("❌ QDRANT_URL environment variable is not set")
        return False
    
    if not qdrant_api_key:
        print("❌ QDRANT_API_KEY environment variable is not set")
        return False
    
    print("✅ Qdrant Cloud environment variables are configured")
    return True

def check_data_file():
    """Check if the data file exists."""
    data_file = Path("premiere_suites_data.jsonl")
    if data_file.exists():
        print("✅ Data file found")
        return True
    else:
        print("❌ Data file 'premiere_suites_data.jsonl' not found")
        return False

def setup_environment():
    """Guide user through environment setup."""
    print("\n🔧 Qdrant Cloud Setup Guide")
    print("=" * 50)
    
    print("\nTo use Qdrant Cloud, you need to:")
    print("1. Sign up at https://cloud.qdrant.io/")
    print("2. Create a new cluster")
    print("3. Get your cluster URL and API key")
    print("4. Set environment variables")
    
    print("\nSet your environment variables:")
    print("export QDRANT_URL='https://your-cluster.qdrant.io'")
    print("export QDRANT_API_KEY='your-api-key-here'")
    
    print("\nOr create a .env file with:")
    print("QDRANT_URL=https://your-cluster.qdrant.io")
    print("QDRANT_API_KEY=your-api-key-here")
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("\n✅ .env file found")
        return True
    else:
        print("\n📝 Creating .env file template...")
        with open(".env", "w") as f:
            f.write("# Qdrant Cloud Configuration\n")
            f.write("QDRANT_URL=https://your-cluster.qdrant.io\n")
            f.write("QDRANT_API_KEY=your-api-key-here\n")
        print("✅ .env file created. Please update it with your actual credentials.")
        return False

def install_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing Python dependencies...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def setup_vector_db():
    """Set up the vector database."""
    print("\n🔧 Setting up vector database...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'qdrant_setup.py'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Vector database setup completed successfully")
            return True
        else:
            print(f"❌ Failed to setup vector database: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error setting up vector database: {e}")
        return False

def test_connection():
    """Test connection to Qdrant Cloud."""
    print("\n🔍 Testing connection to Qdrant Cloud...")
    try:
        from qdrant_setup import PremiereSuitesVectorDB
        import os
        
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        vdb = PremiereSuitesVectorDB(
            qdrant_url=qdrant_url,
            qdrant_api_key=qdrant_api_key,
            use_cloud=True
        )
        
        # Try to get collections to test connection
        collections = vdb.client.get_collections()
        print("✅ Successfully connected to Qdrant Cloud")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("☁️  Qdrant Cloud Setup for Premiere Suites")
    print("=" * 60)
    
    # Check data file
    if not check_data_file():
        print("\nPlease ensure 'premiere_suites_data.jsonl' exists in the current directory")
        return False
    
    # Setup environment
    env_configured = setup_environment()
    
    if not env_configured:
        print("\nPlease configure your Qdrant Cloud credentials and run this script again.")
        print("You can either:")
        print("1. Set environment variables: export QDRANT_URL=... && export QDRANT_API_KEY=...")
        print("2. Update the .env file with your credentials")
        return False
    
    # Check environment variables
    if not check_environment_variables():
        print("\nPlease set your Qdrant Cloud environment variables and run this script again.")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\nFailed to install dependencies. Please check your Python environment.")
        return False
    
    # Test connection
    if not test_connection():
        print("\nFailed to connect to Qdrant Cloud. Please check your credentials.")
        return False
    
    # Setup vector database
    if not setup_vector_db():
        print("\nFailed to setup vector database. Check the error messages above.")
        return False
    
    # Success!
    print("\n🎉 Qdrant Cloud setup completed successfully!")
    print("\nNext steps:")
    print("1. Run the interactive search: python search_properties.py")
    print("2. Or use the vector database programmatically")
    print("3. Check the documentation: QDANT_SETUP_GUIDE.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
