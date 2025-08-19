#!/usr/bin/env python3
"""
Main entry point for the Premiere Suites Scraper
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scrapers import PremiereSuitesScraper
from utils import QuickStart

def main():
    """Main function to run the scraper"""
    print("Premiere Suites Scraper")
    print("=" * 30)
    
    # Initialize scraper
    scraper = PremiereSuitesScraper(headless=True)
    
    # Scrape data
    print("Starting data extraction...")
    properties = scraper.scrape_all()
    
    # Generate outputs
    print(f"Found {len(properties)} properties")
    print("Generating output files...")
    
    # Save to data/processed directory
    output_dir = "data/processed"
    os.makedirs(output_dir, exist_ok=True)
    
    scraper.generate_pdf(properties, f"{output_dir}/premiere_suites_data.pdf")
    scraper.save_to_json(properties, f"{output_dir}/premiere_suites_data.json")
    scraper.save_to_csv(properties, f"{output_dir}/premiere_suites_data.csv")
    scraper.generate_markdown(properties, f"{output_dir}/premiere_suites_data.md")
    
    print("Scraping completed successfully!")
    print(f"Output files saved to: {output_dir}")

if __name__ == "__main__":
    main()
