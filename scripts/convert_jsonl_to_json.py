#!/usr/bin/env python3
"""
Convert JSONL FAQ data to structured JSON format
"""

import json
import os
from datetime import datetime

def convert_jsonl_to_json(jsonl_file_path, json_file_path):
    """
    Convert JSONL file to structured JSON format
    
    Args:
        jsonl_file_path (str): Path to input JSONL file
        json_file_path (str): Path to output JSON file
    """
    
    # Initialize the structure
    data = {
        "metadata": {},
        "summary": {},
        "faqs": []
    }
    
    # Read and parse JSONL file
    with open(jsonl_file_path, 'r', encoding='utf-8') as file:
        for line_num, line in enumerate(file, 1):
            line = line.strip()
            if not line:
                continue
                
            try:
                entry = json.loads(line)
                entry_type = entry.get("type")
                
                if entry_type == "metadata":
                    data["metadata"] = entry
                elif entry_type == "summary":
                    data["summary"] = entry
                elif entry_type == "faq":
                    data["faqs"].append(entry)
                else:
                    print(f"Warning: Unknown entry type '{entry_type}' on line {line_num}")
                    
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON on line {line_num}: {e}")
                continue
    
    # Add conversion metadata
    data["conversion_info"] = {
        "converted_at": datetime.now().isoformat(),
        "source_format": "jsonl",
        "target_format": "json",
        "total_entries": len(data["faqs"]) + 2  # +2 for metadata and summary
    }
    
    # Write to JSON file
    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    
    print(f"Successfully converted {jsonl_file_path} to {json_file_path}")
    print(f"Total FAQs: {len(data['faqs'])}")
    print(f"Categories: {data['summary'].get('categories', [])}")

if __name__ == "__main__":
    # Define file paths
    jsonl_file = "data/processed/premiere_suites_faq_data.jsonl"
    json_file = "data/processed/premiere_suites_faq_data.json"
    
    # Check if input file exists
    if not os.path.exists(jsonl_file):
        print(f"Error: Input file {jsonl_file} not found")
        exit(1)
    
    # Convert the file
    convert_jsonl_to_json(jsonl_file, json_file)
