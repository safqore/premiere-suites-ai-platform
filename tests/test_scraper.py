#!/usr/bin/env python3
"""
Test script for Premiere Suites Scraper
"""

import sys
import os
from premiere_scraper import PremiereSuitesScraper

def test_scraper():
    """Test the scraper functionality"""
    print("Testing Premiere Suites Scraper...")
    print("=" * 50)
    
    # Initialize scraper
    scraper = PremiereSuitesScraper(headless=True)
    
    try:
        # Test scraping
        print("Starting scraping process...")
        properties = scraper.scrape_all()
        
        if properties:
            print(f"✅ Successfully scraped {len(properties)} properties")
            
            # Test file generation
            print("\nGenerating output files...")
            
            # JSON
            scraper.save_to_json(properties, "test_premiere_suites_data.json")
            print("✅ JSON file generated")
            
            # CSV
            scraper.save_to_csv(properties, "test_premiere_suites_data.csv")
            print("✅ CSV file generated")
            
            # PDF
            scraper.generate_pdf(properties, "test_premiere_suites_data.pdf")
            print("✅ PDF file generated")
            
            # Markdown
            scraper.generate_markdown(properties, "test_premiere_suites_data.md")
            print("✅ Markdown file generated")
            
            # JSON Lines (OPTIMAL for vector databases)
            scraper.generate_jsonl(properties, "test_premiere_suites_data.jsonl")
            print("✅ JSON Lines file generated (OPTIMAL for vector DB)")
            
            # Plain text
            scraper.generate_plain_text(properties, "test_premiere_suites_data.txt")
            print("✅ Plain text file generated")
            
            # Chunked text
            scraper.generate_chunked_text(properties, "test_premiere_suites_chunks.txt")
            print("✅ Chunked text file generated")
            
            # Print sample data
            print(f"\nSample property data:")
            print(f"Property: {properties[0].property_name}")
            print(f"City: {properties[0].city}")
            print(f"Rating: {properties[0].rating}")
            print(f"Room Type: {properties[0].room_type}")
            print(f"Amenities: {properties[0].amenities}")
            
            print(f"\n📁 Generated files:")
            for filename in ["test_premiere_suites_data.json", "test_premiere_suites_data.csv", 
                           "test_premiere_suites_data.pdf", "test_premiere_suites_data.md",
                           "test_premiere_suites_data.jsonl", "test_premiere_suites_data.txt",
                           "test_premiere_suites_chunks.txt"]:
                if os.path.exists(filename):
                    size = os.path.getsize(filename)
                    print(f"  - {filename} ({size} bytes)")
            
            print(f"\n🎯 RECOMMENDED for Vector Database:")
            print(f"  - test_premiere_suites_data.jsonl (structured, line-by-line)")
            print(f"  - test_premiere_suites_chunks.txt (pre-chunked for embedding)")
            print(f"  - test_premiere_suites_data.txt (simple text processing)")
            
            return True
            
        else:
            print("❌ No properties found")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    finally:
        scraper.close_driver()

if __name__ == "__main__":
    success = test_scraper()
    sys.exit(0 if success else 1)
