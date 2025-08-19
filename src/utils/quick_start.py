#!/usr/bin/env python3
"""
Quick Start Script for Premiere Suites Vector Database

This script automates the entire setup process for the Qdrant vector database.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_docker():
    """Check if Docker is running."""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is installed")
            return True
        else:
            print("❌ Docker is not installed or not running")
            return False
    except FileNotFoundError:
        print("❌ Docker is not installed")
        return False

def check_docker_compose():
    """Check if Docker Compose is available."""
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker Compose is available")
            return True
        else:
            print("❌ Docker Compose is not available")
            return False
    except FileNotFoundError:
        print("❌ Docker Compose is not installed")
        return False

def start_qdrant():
    """Start Qdrant using Docker Compose."""
    print("\n🚀 Starting Qdrant...")
    try:
        result = subprocess.run(['docker-compose', 'up', '-d'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Qdrant started successfully")
            return True
        else:
            print(f"❌ Failed to start Qdrant: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error starting Qdrant: {e}")
        return False

def wait_for_qdrant():
    """Wait for Qdrant to be ready."""
    print("⏳ Waiting for Qdrant to be ready...")
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get('http://localhost:6333/health', timeout=5)
            if response.status_code == 200:
                print("✅ Qdrant is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(2)
        print(f"   Attempt {attempt + 1}/{max_attempts}...")
    
    print("❌ Qdrant failed to start within expected time")
    return False

def check_data_file():
    """Check if the data file exists."""
    data_file = Path("premiere_suites_data.jsonl")
    if data_file.exists():
        print("✅ Data file found")
        return True
    else:
        print("❌ Data file 'premiere_suites_data.jsonl' not found")
        return False

def install_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing Python dependencies...")
    try:
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

def test_search():
    """Test the search functionality."""
    print("\n🔍 Testing search functionality...")
    try:
        from qdrant_setup import PremiereSuitesVectorDB
        
        vdb = PremiereSuitesVectorDB()
        results = vdb.search_properties("luxury apartment", limit=3)
        
        if results:
            print("✅ Search test successful")
            print("   Sample results:")
            for i, result in enumerate(results[:2], 1):
                print(f"   {i}. {result['property_name']} ({result['city']})")
            return True
        else:
            print("❌ No search results returned")
            return False
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🏠 Premiere Suites Vector Database - Quick Start")
    print("=" * 60)
    
    # Check prerequisites
    print("\n📋 Checking prerequisites...")
    
    if not check_docker():
        print("\nPlease install Docker first: https://docs.docker.com/get-docker/")
        return False
    
    if not check_docker_compose():
        print("\nPlease install Docker Compose first: https://docs.docker.com/compose/install/")
        return False
    
    if not check_data_file():
        print("\nPlease ensure 'premiere_suites_data.jsonl' exists in the current directory")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\nFailed to install dependencies. Please check your Python environment.")
        return False
    
    # Start Qdrant
    if not start_qdrant():
        print("\nFailed to start Qdrant. Please check Docker and try again.")
        return False
    
    # Wait for Qdrant to be ready
    if not wait_for_qdrant():
        print("\nQdrant failed to start properly. Check the logs with: docker-compose logs qdrant")
        return False
    
    # Setup vector database
    if not setup_vector_db():
        print("\nFailed to setup vector database. Check the error messages above.")
        return False
    
    # Test search
    if not test_search():
        print("\nSearch test failed. The setup may not be working correctly.")
        return False
    
    # Success!
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run the interactive search: python search_properties.py")
    print("2. Or use the vector database programmatically")
    print("3. Check the documentation: QDANT_SETUP_GUIDE.md")
    print("\nTo stop Qdrant: docker-compose down")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
