#!/usr/bin/env python3
"""
Script to convert FAQ data from 'text_chunk' or 'pageContent' to 'content' field.

This script processes FAQ data files and converts any 'text_chunk' or 'pageContent' 
fields to 'content' to maintain consistency across the FAQ system.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List

def convert_faq_field_to_content(obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert 'text_chunk' or 'pageContent' field to 'content' in a dictionary object.
    
    Args:
        obj: Dictionary object to process
        
    Returns:
        Dictionary with 'text_chunk' or 'pageContent' converted to 'content'
    """
    if not isinstance(obj, dict):
        return obj
    
    new_obj = {}
    
    for key, value in obj.items():
        if key in ['text_chunk', 'pageContent']:
            # Convert text_chunk or pageContent to content
            new_obj['content'] = value
        elif isinstance(value, dict):
            new_obj[key] = convert_faq_field_to_content(value)
        elif isinstance(value, list):
            new_obj[key] = [convert_faq_field_to_content(item) if isinstance(item, dict) else item for item in value]
        else:
            new_obj[key] = value
    
    return new_obj

def process_jsonl_file(file_path: str) -> None:
    """
    Process a JSONL file and convert text_chunk/pageContent to content.
    
    Args:
        file_path: Path to the JSONL file
    """
    print(f"📄 Processing JSONL file: {file_path}")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Process each line
    updated_lines = []
    line_num = 0
    
    for line in lines:
        line_num += 1
        line = line.strip()
        
        if not line:
            continue
            
        try:
            obj = json.loads(line)
            
            # Convert text_chunk/pageContent to content
            updated_obj = convert_faq_field_to_content(obj)
            
            # Write updated line
            updated_lines.append(json.dumps(updated_obj, ensure_ascii=False))
            
            # Check if conversion happened
            if 'text_chunk' in obj or 'pageContent' in obj:
                print(f"  ✅ Line {line_num}: Converted to 'content'")
            
        except json.JSONDecodeError as e:
            print(f"  ❌ Line {line_num}: JSON decode error - {e}")
            updated_lines.append(line)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        for line in updated_lines:
            f.write(line + '\n')
    
    print(f"  ✅ Updated {len(updated_lines)} lines in {file_path}")

def process_json_file(file_path: str) -> None:
    """
    Process a JSON file and convert text_chunk/pageContent to content.
    
    Args:
        file_path: Path to the JSON file
    """
    print(f"📄 Processing JSON file: {file_path}")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert text_chunk/pageContent to content
    updated_data = convert_faq_field_to_content(data)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Updated {file_path}")

def main():
    """Main function to convert FAQ data files."""
    print("🔄 Converting FAQ data from 'text_chunk'/'pageContent' to 'content'...")
    
    # Define FAQ data files to process
    data_dir = Path("data/processed")
    faq_files = [
        "premiere_suites_faq_data.json",
        "premiere_suites_faq_data.jsonl",
        "premiere_suites_faq_data.csv"  # Note: CSV might need special handling
    ]
    
    # Process each file
    for filename in faq_files:
        file_path = data_dir / filename
        
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
        
        if filename.endswith('.jsonl'):
            process_jsonl_file(str(file_path))
        elif filename.endswith('.json'):
            process_json_file(str(file_path))
        elif filename.endswith('.csv'):
            print(f"⚠️  CSV file conversion not implemented yet: {file_path}")
        else:
            print(f"⚠️  Unsupported file type: {file_path}")
    
    print("\n✅ FAQ data conversion completed!")
    print("💡 All 'text_chunk' and 'pageContent' fields have been converted to 'content'")

if __name__ == "__main__":
    main()
