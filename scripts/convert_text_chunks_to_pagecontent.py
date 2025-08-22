#!/usr/bin/env python3
"""
Script to convert 'text_chunk' fields to 'content' in JSON and JSONL files.

This script processes all JSON and JSONL files in the data/processed/ directory
and converts any 'text_chunk' fields to 'content' to maintain consistency
with standard document formats.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List

def convert_text_chunk_to_content(obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert 'text_chunk' field to 'content' in a dictionary object.
    
    Args:
        obj: Dictionary object that may contain 'text_chunk' field
        
    Returns:
        Dictionary with 'text_chunk' converted to 'content'
    """
    if isinstance(obj, dict):
        # Create a new dictionary to avoid modifying the original
        new_obj = {}
        
        for key, value in obj.items():
            if key == 'text_chunk':
                # Convert text_chunk to content
                new_obj['content'] = value
            else:
                # Recursively process nested dictionaries and lists
                if isinstance(value, dict):
                    new_obj[key] = convert_text_chunk_to_content(value)
                elif isinstance(value, list):
                    new_obj[key] = [convert_text_chunk_to_content(item) if isinstance(item, dict) else item for item in value]
                else:
                    new_obj[key] = value
        
        return new_obj
    
    return obj

def process_jsonl_file(file_path: Path) -> bool:
    """
    Process a JSONL file and convert text_chunk to content.
    
    Args:
        file_path: Path to the JSONL file
        
    Returns:
        True if changes were made, False otherwise
    """
    print(f"Processing JSONL file: {file_path}")
    
    try:
        # Read all lines from the file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            print(f"  ⏭️  File is empty: {file_path}")
            return False
        
        updated_lines = []
        changes_made = False
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            try:
                # Parse JSON object from line
                obj = json.loads(line)
                
                # Check if this object has text_chunk field
                if isinstance(obj, dict) and 'text_chunk' in obj:
                    # Convert text_chunk to content
                    updated_obj = convert_text_chunk_to_content(obj)
                    updated_lines.append(json.dumps(updated_obj, ensure_ascii=False))
                    changes_made = True
                    print(f"  ✅ Line {line_num}: Converted 'text_chunk' to 'content'")
                else:
                    # No text_chunk field, keep as is
                    updated_lines.append(line)
                    
            except json.JSONDecodeError as e:
                print(f"  ⚠️  Line {line_num}: JSON decode error - {e}")
                updated_lines.append(line)
        
        # Write back to file if changes were made
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                for line in updated_lines:
                    f.write(line + '\n')
            print(f"  ✅ Updated file: {file_path}")
            return True
        else:
            print(f"  ⏭️  No 'text_chunk' fields found in: {file_path}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False

def process_json_file(file_path: Path) -> bool:
    """
    Process a JSON file and convert text_chunk to content.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        True if changes were made, False otherwise
    """
    print(f"Processing JSON file: {file_path}")
    
    try:
        # Read JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert text_chunk to content
        updated_data = convert_text_chunk_to_content(data)
        
        # Check if any changes were made
        if has_text_chunk_field(data):
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, indent=2, ensure_ascii=False)
            print(f"  ✅ Updated file: {file_path}")
            return True
        else:
            print(f"  ⏭️  No 'text_chunk' fields found in: {file_path}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False

def has_text_chunk_field(obj: Any) -> bool:
    """
    Recursively check if an object contains any 'text_chunk' fields.
    
    Args:
        obj: Object to check (dict, list, or primitive)
        
    Returns:
        True if text_chunk field is found, False otherwise
    """
    if isinstance(obj, dict):
        if 'text_chunk' in obj:
            return True
        for value in obj.values():
            if has_text_chunk_field(value):
                return True
    elif isinstance(obj, list):
        for item in obj:
            if has_text_chunk_field(item):
                return True
    return False

def main():
    """Main function to process all JSON and JSONL files."""
    print("🔄 Converting 'text_chunk' to 'content' in processed data files...")
    print("=" * 70)
    
    # Get the data/processed directory
    processed_dir = Path("data/processed")
    
    if not processed_dir.exists():
        print(f"❌ Directory not found: {processed_dir}")
        return
    
    # Find all JSON and JSONL files
    json_files = list(processed_dir.glob("*.json"))
    jsonl_files = list(processed_dir.glob("*.jsonl"))
    
    all_files = json_files + jsonl_files
    
    if not all_files:
        print("No JSON or JSONL files found in data/processed/")
        return
    
    print(f"Found {len(all_files)} files to process:")
    for file_path in all_files:
        print(f"  - {file_path.name}")
    print()
    
    total_changes = 0
    
    # Process JSONL files
    for file_path in jsonl_files:
        if process_jsonl_file(file_path):
            total_changes += 1
        print()
    
    # Process JSON files
    for file_path in json_files:
        if process_json_file(file_path):
            total_changes += 1
        print()
    
    print("=" * 70)
    print(f"✅ Conversion complete! Updated {total_changes} files.")
    print()
    print("📋 Summary:")
    print(f"  - Total files processed: {len(all_files)}")
    print(f"  - Files updated: {total_changes}")
    print(f"  - Files unchanged: {len(all_files) - total_changes}")
    print()
    print("💡 All 'text_chunk' fields have been converted to 'content'")
    print("   for consistency with standard document formats.")

if __name__ == "__main__":
    main()
