#!/usr/bin/env python3
"""
Script to update file references to the new organized project structure.

This script helps developers update any hardcoded file paths that might
reference the old structure where files were in the root directory.
"""

import os
import re
from pathlib import Path

# File mapping from old locations to new locations
FILE_MAPPING = {
    # Data files
    'premiere_suites_data.pdf': 'data/raw/premiere_suites_data.pdf',
    'premiere_suites_data.csv': 'data/raw/premiere_suites_data.csv',
    'premiere_suites_data.txt': 'data/raw/premiere_suites_data.txt',
    'premiere_suites_data.md': 'data/raw/premiere_suites_data.md',
    'premiere_suites_data.json': 'data/processed/premiere_suites_data.json',
    'premiere_suites_data.jsonl': 'data/processed/premiere_suites_data.jsonl',
    'premiere_suites_faq_data.jsonl': 'data/processed/premiere_suites_faq_data.jsonl',
    'premiere_suites_chunks.txt': 'data/processed/premiere_suites_chunks.txt',
    
    # Documentation files
    'FAQ_DATA_COMPLETION_SUMMARY.md': 'docs/FAQ_DATA_COMPLETION_SUMMARY.md',
    'PROPERTY_DATA_COMPLETION_SUMMARY.md': 'docs/PROPERTY_DATA_COMPLETION_SUMMARY.md',
    'PAGECONTENT_STANDARDIZATION_SUMMARY.md': 'docs/PAGECONTENT_STANDARDIZATION_SUMMARY.md',
    'FAQ_WORKFLOW_SUMMARY.md': 'docs/FAQ_WORKFLOW_SUMMARY.md',
    'VECTORIZATION_PROPERTIES_GUIDE.md': 'docs/VECTORIZATION_PROPERTIES_GUIDE.md',
    'FAQ_VECTORIZATION_GUIDE.md': 'docs/FAQ_VECTORIZATION_GUIDE.md',
    'qdrant_web_interface_guide.md': 'docs/qdrant_web_interface_guide.md',
    
    # Script files
    'convert_jsonl_to_json.py': 'scripts/convert_jsonl_to_json.py',
    'check_and_fix_pagecontent.py': 'scripts/check_and_fix_pagecontent.py',
    'vectorize_faq_data.py': 'scripts/vectorize_faq_data.py',
    'recreate_collections_with_properties.py': 'scripts/recreate_collections_with_properties.py',
    'recreate_collections_langchain.py': 'scripts/recreate_collections_langchain.py',
    'start_qdrant_local.py': 'scripts/start_qdrant_local.py',
    
    # Test files
    'test_vectorization_properties.py': 'tests/test_vectorization_properties.py',
    'test_langchain_integration.py': 'tests/test_langchain_integration.py',
}

def find_python_files(directory='.'):
    """Find all Python files in the directory tree."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip virtual environment and git directories
        dirs[:] = [d for d in dirs if d not in ['.venv', '.git', '__pycache__']]
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def update_file_references(file_path):
    """Update file references in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        updated = False
        
        # Update file references
        for old_path, new_path in FILE_MAPPING.items():
            # Look for various patterns of file references
            patterns = [
                f"'{old_path}'",
                f'"{old_path}"',
                f"'{old_path}'",
                f'"{old_path}"',
                f"open('{old_path}'",
                f'open("{old_path}"',
                f"Path('{old_path}'",
                f'Path("{old_path}"',
                f"'{old_path}'",
                f'"{old_path}"',
            ]
            
            for pattern in patterns:
                if pattern in content:
                    new_pattern = pattern.replace(old_path, new_path)
                    content = content.replace(pattern, new_pattern)
                    updated = True
        
        # Write back if changes were made
        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated: {file_path}")
            return True
        else:
            print(f"⏭️  No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to update file references."""
    print("🔄 Updating file references to new organized structure...")
    print("=" * 60)
    
    # Find all Python files
    python_files = find_python_files()
    
    if not python_files:
        print("No Python files found.")
        return
    
    print(f"Found {len(python_files)} Python files to check.")
    print()
    
    updated_count = 0
    
    for file_path in python_files:
        if update_file_references(file_path):
            updated_count += 1
    
    print()
    print("=" * 60)
    print(f"✅ Update complete! Updated {updated_count} files.")
    print()
    print("📋 Summary of file location changes:")
    print()
    
    for old_path, new_path in FILE_MAPPING.items():
        print(f"  {old_path} → {new_path}")
    
    print()
    print("💡 Remember to:")
    print("  - Update any import statements that reference moved modules")
    print("  - Check for any hardcoded paths in configuration files")
    print("  - Update documentation that references old file locations")
    print("  - Test your code to ensure all file references work correctly")

if __name__ == "__main__":
    main()
