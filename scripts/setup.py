#!/usr/bin/env python3
"""
Setup script for Premiere Suites Scraper
"""

import os
import sys
import subprocess
import shutil

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def setup_virtual_environment():
    """Set up virtual environment"""
    if os.path.exists(".venv"):
        print("✓ Virtual environment already exists")
        return True
    
    return run_command("python3 -m venv .venv", "Creating virtual environment")

def install_dependencies():
    """Install Python dependencies"""
    # Determine the correct pip command
    if os.name == 'nt':  # Windows
        pip_cmd = ".venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        pip_cmd = ".venv/bin/pip"
    
    return run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies")

def create_directories():
    """Create necessary directories"""
    directories = [
        "data/raw",
        "data/processed", 
        "data/exports",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    return True

def copy_config_files():
    """Copy configuration files"""
    if not os.path.exists(".env"):
        if os.path.exists("config/env.example"):
            shutil.copy("config/env.example", ".env")
            print("✓ Created .env file from template")
        else:
            print("⚠ No env.example found, you'll need to create .env manually")
    
    return True

def main():
    """Main setup function"""
    print("Premiere Suites Scraper Setup")
    print("=" * 30)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Set up virtual environment
    if not setup_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Copy config files
    if not copy_config_files():
        sys.exit(1)
    
    print("\n" + "=" * 30)
    print("Setup completed successfully!")
    print("\nNext steps:")
    print("1. Activate virtual environment:")
    if os.name == 'nt':  # Windows
        print("   .venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("   source .venv/bin/activate")
    print("2. Configure your .env file with necessary settings")
    print("3. Run the scraper: python main.py")
    print("4. Run tests: python -m pytest tests/")

if __name__ == "__main__":
    main()
