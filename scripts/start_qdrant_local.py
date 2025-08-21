#!/usr/bin/env python3
"""
Start Qdrant Locally

This script helps you start Qdrant locally for development.
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def check_docker():
    """Check if Docker is available and running."""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is available")
            return True
        else:
            print("❌ Docker is not available")
            return False
    except FileNotFoundError:
        print("❌ Docker is not installed")
        return False

def check_docker_running():
    """Check if Docker daemon is running."""
    try:
        result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker daemon is running")
            return True
        else:
            print("❌ Docker daemon is not running")
            return False
    except Exception as e:
        print(f"❌ Error checking Docker: {e}")
        return False

def check_qdrant_running():
    """Check if Qdrant is already running."""
    try:
        response = requests.get("http://localhost:6333/health", timeout=5)
        if response.status_code == 200:
            print("✅ Qdrant is already running on localhost:6333")
            return True
        else:
            print("❌ Qdrant is not responding properly")
            return False
    except requests.exceptions.RequestException:
        print("ℹ️  Qdrant is not running on localhost:6333")
        return False

def start_qdrant_docker():
    """Start Qdrant using Docker."""
    print("\n🐳 Starting Qdrant with Docker...")
    
    try:
        # Check if Qdrant container is already running
        result = subprocess.run(['docker', 'ps', '--filter', 'name=premiere_suites_qdrant'], 
                              capture_output=True, text=True)
        
        if 'premiere_suites_qdrant' in result.stdout:
            print("✅ Qdrant container is already running")
            return True
        
        # Start Qdrant container
        print("📦 Pulling Qdrant image...")
        subprocess.run(['docker', 'pull', 'qdrant/qdrant:latest'], check=True)
        
        print("🚀 Starting Qdrant container...")
        subprocess.run([
            'docker', 'run', '-d',
            '--name', 'premiere_suites_qdrant',
            '-p', '6333:6333',
            '-p', '6334:6334',
            'qdrant/qdrant:latest'
        ], check=True)
        
        print("⏳ Waiting for Qdrant to start...")
        time.sleep(5)
        
        # Check if Qdrant is responding
        for i in range(10):
            if check_qdrant_running():
                print("✅ Qdrant started successfully!")
                return True
            print(f"⏳ Waiting... ({i+1}/10)")
            time.sleep(2)
        
        print("❌ Qdrant failed to start properly")
        return False
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Qdrant: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_manual_instructions():
    """Show manual instructions for starting Qdrant."""
    print("\n📋 Manual Qdrant Setup Instructions")
    print("=" * 50)
    
    print("\n1. 🐳 Using Docker:")
    print("   docker run -d --name premiere_suites_qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest")
    
    print("\n2. 🏗️  Using Docker Compose:")
    print("   cd config")
    print("   docker-compose up -d")
    
    print("\n3. 📦 Using pip (Python):")
    print("   pip install qdrant-client")
    print("   python -m qdrant.http")
    
    print("\n4. 🍺 Using Homebrew (macOS):")
    print("   brew install qdrant")
    print("   qdrant")
    
    print("\n5. ☁️  Using Qdrant Cloud:")
    print("   - Go to https://cloud.qdrant.io/")
    print("   - Create a free account")
    print("   - Create a new cluster")
    print("   - Set environment variables:")
    print("     export QDRANT_URL=https://your-cluster.qdrant.io")
    print("     export QDRANT_API_KEY=your-api-key")
    
    print("\n💡 After starting Qdrant, run:")
    print("   python recreate_collections_langchain.py")

def main():
    """Main function to start Qdrant."""
    print("🏠 Premiere Suites - Start Qdrant Locally")
    print("=" * 50)
    
    # Check if Qdrant is already running
    if check_qdrant_running():
        print("\n🎉 Qdrant is ready! You can now run:")
        print("   python recreate_collections_langchain.py")
        return 0
    
    # Check Docker availability
    docker_available = check_docker() and check_docker_running()
    
    if docker_available:
        print("\n🐳 Docker is available. Attempting to start Qdrant...")
        if start_qdrant_docker():
            print("\n🎉 Qdrant started successfully!")
            print("💡 You can now run:")
            print("   python recreate_collections_langchain.py")
            return 0
        else:
            print("\n⚠️  Failed to start Qdrant with Docker.")
    else:
        print("\n⚠️  Docker is not available.")
    
    # Show manual instructions
    show_manual_instructions()
    
    return 1

if __name__ == "__main__":
    exit(main())


