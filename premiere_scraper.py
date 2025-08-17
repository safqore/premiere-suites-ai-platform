#!/usr/bin/env python3
"""
Premiere Suites Web Scraper
Extracts property data from https://premieresuites.com/find-your-match/
Generates PDF document for vector database ingestion
"""

import requests
import json
import time
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import pandas as pd
from tqdm import tqdm
import logging
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import markdown
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PropertyData:
    """Data structure for property information"""
    property_name: str
    city: str
    rating: Optional[float]
    room_type: str
    amenities: List[str]
    description: str
    url: str
    image_url: Optional[str]
    price_range: Optional[str]
    pet_friendly: bool
    bedrooms: Optional[int]
    location_details: Optional[str]
    raw_html: str
    property_id: Optional[str]
    building_type: Optional[str]
    suite_features: List[str]

class PremiereSuitesScraper:
    """Main scraper class for Premiere Suites website"""
    
    def __init__(self, headless: bool = True):
        self.base_url = "https://premieresuites.com/find-your-match/"
        self.session = requests.Session()
        self.ua = UserAgent()
        self.headless = headless
        self.driver = None
        self.setup_session()
        
    def setup_session(self):
        """Setup requests session with headers"""
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def setup_driver(self):
        """Setup Selenium WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--user-agent={self.ua.random}")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def close_driver(self):
        """Close Selenium WebDriver"""
        if self.driver:
            self.driver.quit()
    
    def extract_property_data_from_html(self, html_content: str) -> List[PropertyData]:
        """Extract property data from HTML content using dynamic URL parsing"""
        soup = BeautifulSoup(html_content, 'html.parser')
        properties = []
        
        # Find all property links
        property_links = soup.find_all('a', href=re.compile(r'/furnished-apartments/[^/]+/[^/]+/'))
        
        # Extract unique property URLs
        unique_urls = set()
        for link in property_links:
            href = link.get('href')
            if href:
                unique_urls.add(href)
        
        logger.info(f"Found {len(unique_urls)} unique property URLs")
        
        # First, extract all ratings from the page
        all_ratings = self.extract_all_ratings(soup)
        logger.info(f"Found {len(all_ratings)} ratings on the page")
        
        # Parse each unique property URL
        for i, url in enumerate(unique_urls):
            try:
                property_data = self.parse_property_from_url(url, soup, all_ratings, i)
                if property_data:
                    properties.append(property_data)
            except Exception as e:
                logger.warning(f"Error parsing property from URL {url}: {e}")
                continue
        
        return properties
    
    def extract_all_ratings(self, soup: BeautifulSoup) -> List[float]:
        """Extract all ratings from the page"""
        text = soup.get_text()
        rating_matches = re.findall(r'(\d+\.\d+)', text)
        ratings = []
        
        for match in rating_matches:
            try:
                rating = float(match)
                # Validate rating is reasonable (between 1.0 and 5.0)
                if 1.0 <= rating <= 5.0:
                    ratings.append(rating)
            except ValueError:
                continue
        
        return ratings
    
    def parse_property_from_url(self, url: str, soup: BeautifulSoup, all_ratings: List[float], index: int) -> Optional[PropertyData]:
        """Parse property information from URL and associated HTML content"""
        try:
            # Extract city and property name from URL
            # URL format: /furnished-apartments/city/property-name/
            url_parts = url.strip('/').split('/')
            logger.debug(f"Parsing URL: {url}, parts: {url_parts}")
            
            if len(url_parts) >= 3:
                city = url_parts[-2].replace('-', ' ').title()
                property_slug = url_parts[-1].replace('-', ' ')
                property_name = property_slug.replace('_', ' ').title()
            else:
                logger.warning(f"Invalid URL format: {url}")
                return None
            
            logger.debug(f"Extracted - Property: {property_name}, City: {city}")
            
            # Find the property card/section that contains this URL
            property_section = soup.find('a', href=url)
            if not property_section:
                logger.warning(f"Could not find link with href: {url}")
                return None
            
            # Get the parent container for more information
            # Try multiple levels of parent containers to find the one with rating info
            container = property_section.find_parent(['div', 'article', 'section'])
            if not container:
                container = property_section
            
            # If the immediate parent doesn't have rating info, try to find a larger container
            container_text = container.get_text()
            if not re.search(r'\d+\.\d+', container_text):
                # Look for a larger container that might contain the rating
                larger_container = container.find_parent(['div', 'article', 'section', 'main'])
                if larger_container:
                    container = larger_container
                    container_text = container.get_text()
            
            # Also search the entire page for property-specific information
            # This helps find amenities and other details that might be in different sections
            full_page_text = soup.get_text()
            
            # Extract additional information from the container and full page
            # Use rating from the all_ratings list if available
            rating = None
            if index < len(all_ratings):
                rating = all_ratings[index]
            
            # Extract room type
            room_type = self.extract_room_type(container_text)
            
            # Extract amenities from both container and full page
            container_amenities = self.extract_amenities(container_text)
            page_amenities = self.extract_amenities(full_page_text)
            # Combine and deduplicate amenities
            all_amenities = list(set(container_amenities + page_amenities))
            
            # Extract suite features from both container and full page
            container_suite_features = self.extract_suite_features(container_text)
            page_suite_features = self.extract_suite_features(full_page_text)
            # Combine and deduplicate suite features
            all_suite_features = list(set(container_suite_features + page_suite_features))
            
            # Extract image URL
            image_url = self.extract_image_url(container)
            
            # Extract bedrooms from both container and full page
            container_bedrooms = self.extract_bedrooms(container_text)
            page_bedrooms = self.extract_bedrooms(full_page_text)
            bedrooms = container_bedrooms or page_bedrooms
            
            # Determine pet friendly status from both container and full page
            container_pet_friendly = self.is_pet_friendly(container_text)
            page_pet_friendly = self.is_pet_friendly(full_page_text)
            pet_friendly = container_pet_friendly or page_pet_friendly
            
            # Generate property ID
            property_id = re.sub(r'[^a-zA-Z0-9]', '', property_name)[:10].upper()
            
            # Create description
            description = f"{property_name} {city}"
            if rating:
                description += f" {rating}"
            
            # Create PropertyData object
            property_data = PropertyData(
                property_name=property_name,
                city=city,
                rating=rating,
                room_type=room_type,
                amenities=all_amenities,
                description=description,
                url=f"https://premieresuites.com{url}",
                image_url=image_url,
                price_range=None,
                pet_friendly=pet_friendly,
                bedrooms=bedrooms,
                location_details=None,
                raw_html=str(container),
                property_id=property_id,
                building_type="Apartment Building",
                suite_features=all_suite_features
            )
            
            logger.debug(f"Successfully created property data for: {property_name}")
            return property_data
            
        except Exception as e:
            logger.error(f"Error parsing property from URL {url}: {e}")
            return None
    
    def extract_rating(self, text: str) -> Optional[float]:
        """Extract rating from text content"""
        # Look for rating patterns like "4.5", "5.0", etc.
        rating_patterns = [
            r'(\d+\.\d+)',  # Standard decimal format
            r'(\d+\.\d+)/5',  # With /5 suffix
            r'Rating:\s*(\d+\.\d+)',  # With "Rating:" prefix
            r'(\d+\.\d+)\s*stars?',  # With "stars" suffix
        ]
        
        for pattern in rating_patterns:
            rating_match = re.search(pattern, text, re.IGNORECASE)
            if rating_match:
                try:
                    rating = float(rating_match.group(1))
                    # Validate rating is reasonable (between 1.0 and 5.0)
                    if 1.0 <= rating <= 5.0:
                        return rating
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def extract_room_type(self, text: str) -> str:
        """Extract room type from text content"""
        text_lower = text.lower()
        if 'kitchen' in text_lower:
            return "Kitchen"
        elif 'living room' in text_lower:
            return "Living Room"
        elif 'dining' in text_lower:
            return "Dining Room"
        else:
            return "Suite"
    
    def extract_amenities(self, text: str) -> List[str]:
        """Extract amenities from text content"""
        amenities = []
        amenity_keywords = [
            'Gym', 'Laundry', 'Parking', 'Pool', 'WiFi', 'Furnished', 
            'Pet Friendly', 'Free WiFi', 'Fully Furnished', 'In-suite Laundry',
            'Fitness Center', 'Exercise Room', 'Workout Room', 'Business Center',
            'Concierge', 'Doorman', 'Security', 'Elevator', 'Balcony', 'Terrace',
            'Garden', 'BBQ', 'Outdoor Space', 'Storage', 'Bike Storage'
        ]
        
        text_lower = text.lower()
        for keyword in amenity_keywords:
            if keyword.lower() in text_lower:
                amenities.append(keyword)
        
        return amenities
    
    def extract_bedrooms(self, text: str) -> Optional[int]:
        """Extract number of bedrooms from text content"""
        # Look for various bedroom patterns
        bedroom_patterns = [
            r'(\d+)\s*(?:bedroom|bed)\s*(?:suite|apartment|unit)',  # "2 bedroom suite"
            r'(?:suite|apartment|unit)\s*(?:with\s+)?(\d+)\s*(?:bedroom|bed)',  # "suite with 2 bedroom"
            r'(\d+)\s*(?:BR|BRs)',  # "2BR"
            r'(\d+)\s*(?:bed)',  # "2 bed"
        ]
        
        for pattern in bedroom_patterns:
            bedroom_match = re.search(pattern, text, re.IGNORECASE)
            if bedroom_match:
                try:
                    return int(bedroom_match.group(1))
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def is_pet_friendly(self, text: str) -> bool:
        """Determine if property is pet friendly"""
        text_lower = text.lower()
        pet_indicators = [
            'pet friendly', 'pets allowed', 'pet-friendly', 'pets welcome',
            'pet policy', 'dogs allowed', 'cats allowed'
        ]
        
        for indicator in pet_indicators:
            if indicator in text_lower:
                return True
        
        return False
    
    def extract_image_url(self, container) -> Optional[str]:
        """Extract image URL from container"""
        img_elem = container.find('img')
        if img_elem and img_elem.get('src'):
            return img_elem.get('src')
        return None

    def extract_suite_features(self, text: str) -> List[str]:
        """Extract suite-specific features from text content"""
        suite_features = []
        suite_feature_keywords = [
            'Fully Furnished', 'Furnished', 'Unfurnished', 'Partially Furnished',
            'Kitchen', 'Full Kitchen', 'Kitchenette', 'Kitchen Appliances',
            'Dishwasher', 'Microwave', 'Stove', 'Oven', 'Refrigerator',
            'In-suite Laundry', 'Washer', 'Dryer', 'Laundry Hookups',
            'Balcony', 'Terrace', 'Patio', 'Private Balcony',
            'Walk-in Closet', 'Storage', 'Built-in Storage',
            'Hardwood Floors', 'Carpeted', 'Tile Floors',
            'Air Conditioning', 'Central Air', 'Heating',
            'Walk-in Shower', 'Tub', 'Ensuite Bathroom',
            'Queen Bed', 'King Bed', 'Double Bed', 'Single Bed',
            'Sofa Bed', 'Pull-out Couch', 'Dining Table',
            'Work Desk', 'Office Space', 'Study Area',
            'City View', 'Mountain View', 'Water View', 'Garden View',
            'Corner Unit', 'End Unit', 'Top Floor', 'Penthouse',
            'Newly Renovated', 'Updated', 'Modern', 'Contemporary',
            'Luxury', 'Premium', 'High-end', 'Designer'
        ]
        
        text_lower = text.lower()
        for keyword in suite_feature_keywords:
            if keyword.lower() in text_lower:
                suite_features.append(keyword)
        
        return suite_features


    def scrape_with_requests(self) -> List[PropertyData]:
        """Scrape using requests library"""
        try:
            logger.info("Starting scraping with requests...")
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            properties = self.extract_property_data_from_html(response.text)
            logger.info(f"Extracted {len(properties)} properties using requests")
            return properties
            
        except Exception as e:
            logger.error(f"Error scraping with requests: {e}")
            return []
    
    def scrape_with_selenium(self) -> List[PropertyData]:
        """Scrape using Selenium for dynamic content"""
        try:
            logger.info("Starting scraping with Selenium...")
            self.setup_driver()
            
            self.driver.get(self.base_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Scroll to load more content
            self.scroll_page()
            
            # Get page source
            page_source = self.driver.page_source
            properties = self.extract_property_data_from_html(page_source)
            
            logger.info(f"Extracted {len(properties)} properties using Selenium")
            return properties
            
        except Exception as e:
            logger.error(f"Error scraping with Selenium: {e}")
            return []
        finally:
            self.close_driver()
    
    def scroll_page(self):
        """Scroll page to load dynamic content"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # Wait for new content to load
                time.sleep(2)
                
                # Calculate new scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                if new_height == last_height:
                    break
                    
                last_height = new_height
                
        except Exception as e:
            logger.warning(f"Error during scrolling: {e}")
    
    def scrape_all(self) -> List[PropertyData]:
        """Scrape using both methods and combine results"""
        logger.info("Starting comprehensive scraping...")
        
        # Try requests first
        properties_requests = self.scrape_with_requests()
        
        # Try Selenium for dynamic content
        properties_selenium = self.scrape_with_selenium()
        
        # Combine and deduplicate results
        all_properties = properties_requests + properties_selenium
        
        # Simple deduplication based on property name and city
        seen = set()
        unique_properties = []
        
        for prop in all_properties:
            key = (prop.property_name, prop.city)
            if key not in seen:
                seen.add(key)
                unique_properties.append(prop)
        
        logger.info(f"Total unique properties found: {len(unique_properties)}")
        return unique_properties
    
    def save_to_json(self, properties: List[PropertyData], filename: str = "premiere_suites_data.json"):
        """Save scraped data to JSON file"""
        try:
            data = [asdict(prop) for prop in properties]
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
    
    def save_to_csv(self, properties: List[PropertyData], filename: str = "premiere_suites_data.csv"):
        """Save scraped data to CSV file"""
        try:
            data = [asdict(prop) for prop in properties]
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8')
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
    
    def generate_pdf(self, properties: List[PropertyData], filename: str = "premiere_suites_data.pdf"):
        """Generate PDF document for vector database ingestion"""
        try:
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                spaceBefore=20,
                textColor=colors.darkgreen
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                alignment=TA_JUSTIFY
            )
            
            # Add title
            title = Paragraph("Premiere Suites Property Database", title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Add generation info
            info_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
            info_text += f"Total Properties: {len(properties)}<br/>"
            info_text += f"Source: {self.base_url}<br/>"
            info_text += f"Purpose: Vector Database Ingestion for LLM Training"
            
            info_para = Paragraph(info_text, normal_style)
            story.append(info_para)
            story.append(Spacer(1, 20))
            
            # Add summary statistics
            cities = set(p.city for p in properties)
            avg_rating = sum(p.rating or 0 for p in properties) / len([p for p in properties if p.rating]) if any(p.rating for p in properties) else 0
            pet_friendly_count = sum(1 for p in properties if p.pet_friendly)
            
            summary_text = f"<b>Summary Statistics:</b><br/>"
            summary_text += f"• Cities Covered: {len(cities)}<br/>"
            summary_text += f"• Average Rating: {avg_rating:.2f}<br/>"
            summary_text += f"• Pet Friendly Properties: {pet_friendly_count}<br/>"
            summary_text += f"• Cities: {', '.join(sorted(cities))}"
            
            summary_para = Paragraph(summary_text, normal_style)
            story.append(summary_para)
            story.append(Spacer(1, 30))
            
            # Add property details
            for i, prop in enumerate(properties, 1):
                # Property header
                prop_title = f"{i}. {prop.property_name} - {prop.city}"
                story.append(Paragraph(prop_title, heading_style))
                
                # Property details
                details_text = f"<b>Property ID:</b> {prop.property_id}<br/>"
                details_text += f"<b>Room Type:</b> {prop.room_type}<br/>"
                if prop.rating:
                    details_text += f"<b>Rating:</b> {prop.rating}/5.0<br/>"
                if prop.bedrooms:
                    details_text += f"<b>Bedrooms:</b> {prop.bedrooms}<br/>"
                details_text += f"<b>Pet Friendly:</b> {'Yes' if prop.pet_friendly else 'No'}<br/>"
                
                if prop.amenities:
                    details_text += f"<b>Amenities:</b> {', '.join(prop.amenities)}<br/>"
                
                details_text += f"<b>Description:</b> {prop.description}<br/>"
                details_text += f"<b>Building Type:</b> {prop.building_type}<br/>"
                
                if prop.suite_features:
                    details_text += f"<b>Suite Features:</b> {', '.join(prop.suite_features)}<br/>"
                
                details_para = Paragraph(details_text, normal_style)
                story.append(details_para)
                story.append(Spacer(1, 15))
                
                # Add page break every 5 properties to keep it readable
                if i % 5 == 0 and i < len(properties):
                    story.append(PageBreak())
            
            # Build PDF
            doc.build(story)
            logger.info(f"PDF generated successfully: {filename}")
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
    
    def generate_markdown(self, properties: List[PropertyData], filename: str = "premiere_suites_data.md"):
        """Generate Markdown document for vector database ingestion"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# Premiere Suites Property Database\n\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"Total Properties: {len(properties)}\n\n")
                f.write(f"Source: {self.base_url}\n\n")
                f.write("## Summary Statistics\n\n")
                
                cities = set(p.city for p in properties)
                avg_rating = sum(p.rating or 0 for p in properties) / len([p for p in properties if p.rating]) if any(p.rating for p in properties) else 0
                pet_friendly_count = sum(1 for p in properties if p.pet_friendly)
                
                f.write(f"- **Cities Covered:** {len(cities)}\n")
                f.write(f"- **Average Rating:** {avg_rating:.2f}\n")
                f.write(f"- **Pet Friendly Properties:** {pet_friendly_count}\n")
                f.write(f"- **Cities:** {', '.join(sorted(cities))}\n\n")
                
                f.write("## Property Details\n\n")
                
                for i, prop in enumerate(properties, 1):
                    f.write(f"### {i}. {prop.property_name} - {prop.city}\n\n")
                    f.write(f"**Property ID:** {prop.property_id}\n\n")
                    f.write(f"**Room Type:** {prop.room_type}\n\n")
                    if prop.rating:
                        f.write(f"**Rating:** {prop.rating}/5.0\n\n")
                    if prop.bedrooms:
                        f.write(f"**Bedrooms:** {prop.bedrooms}\n\n")
                    f.write(f"**Pet Friendly:** {'Yes' if prop.pet_friendly else 'No'}\n\n")
                    
                    if prop.amenities:
                        f.write(f"**Amenities:** {', '.join(prop.amenities)}\n\n")
                    
                    f.write(f"**Description:** {prop.description}\n\n")
                    f.write(f"**Building Type:** {prop.building_type}\n\n")
                    
                    if prop.suite_features:
                        f.write(f"**Suite Features:** {', '.join(prop.suite_features)}\n\n")
                    
                    f.write("---\n\n")
            
            logger.info(f"Markdown file generated successfully: {filename}")
            
        except Exception as e:
            logger.error(f"Error generating Markdown: {e}")
    
    def generate_jsonl(self, properties: List[PropertyData], filename: str = "premiere_suites_data.jsonl"):
        """Generate JSON Lines format - OPTIMAL for vector database ingestion"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Write metadata as first line
                metadata = {
                    "type": "metadata",
                    "generated_on": datetime.now().isoformat(),
                    "total_properties": len(properties),
                    "source_url": self.base_url,
                    "purpose": "vector_database_ingestion",
                    "format": "jsonl"
                }
                f.write(json.dumps(metadata, ensure_ascii=False) + '\n')
                
                # Write summary statistics
                cities = set(p.city for p in properties)
                avg_rating = sum(p.rating or 0 for p in properties) / len([p for p in properties if p.rating]) if any(p.rating for p in properties) else 0
                pet_friendly_count = sum(1 for p in properties if p.pet_friendly)
                
                summary = {
                    "type": "summary",
                    "cities_covered": len(cities),
                    "average_rating": round(avg_rating, 2),
                    "pet_friendly_count": pet_friendly_count,
                    "cities": sorted(list(cities))
                }
                f.write(json.dumps(summary, ensure_ascii=False) + '\n')
                
                # Write each property as a separate JSON line
                for i, prop in enumerate(properties, 1):
                    # Create structured property data
                    property_data = {
                        "type": "property",
                        "id": prop.property_id,
                        "property_name": prop.property_name,
                        "city": prop.city,
                        "rating": prop.rating,
                        "room_type": prop.room_type,
                        "amenities": prop.amenities,
                        "description": prop.description,
                        "pet_friendly": prop.pet_friendly,
                        "bedrooms": prop.bedrooms,
                        "building_type": prop.building_type,
                        "suite_features": prop.suite_features,
                        "source_url": prop.url,
                        "image_url": prop.image_url,
                        "price_range": prop.price_range,
                        "location_details": prop.location_details
                    }
                    
                    # Also create a text chunk for embedding
                    text_chunk = self.create_text_chunk(prop, i)
                    property_data["text_chunk"] = text_chunk
                    
                    f.write(json.dumps(property_data, ensure_ascii=False) + '\n')
            
            logger.info(f"JSON Lines file generated successfully: {filename}")
            
        except Exception as e:
            logger.error(f"Error generating JSON Lines: {e}")
    
    def create_text_chunk(self, prop: PropertyData, index: int) -> str:
        """Create optimized text chunk for vector embedding"""
        chunks = []
        
        # Property header
        chunks.append(f"Property {index}: {prop.property_name}")
        chunks.append(f"Location: {prop.city}")
        
        # Key details
        if prop.rating:
            chunks.append(f"Rating: {prop.rating}/5.0")
        if prop.bedrooms:
            chunks.append(f"Bedrooms: {prop.bedrooms}")
        chunks.append(f"Room Type: {prop.room_type}")
        chunks.append(f"Pet Friendly: {'Yes' if prop.pet_friendly else 'No'}")
        
        # Amenities
        if prop.amenities:
            chunks.append(f"Amenities: {', '.join(prop.amenities)}")
        
        # Description
        if prop.description:
            chunks.append(f"Description: {prop.description}")
        
        # Building type
        chunks.append(f"Building Type: {prop.building_type}")
        
        # Suite features
        if prop.suite_features:
            chunks.append(f"Suite Features: {', '.join(prop.suite_features)}")
        
        return " | ".join(chunks)
    
    def generate_plain_text(self, properties: List[PropertyData], filename: str = "premiere_suites_data.txt"):
        """Generate plain text format for vector database ingestion"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Header
                f.write("PREMIERE SUITES PROPERTY DATABASE\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Properties: {len(properties)}\n")
                f.write(f"Source: {self.base_url}\n\n")
                
                # Summary
                cities = set(p.city for p in properties)
                avg_rating = sum(p.rating or 0 for p in properties) / len([p for p in properties if p.rating]) if any(p.rating for p in properties) else 0
                pet_friendly_count = sum(1 for p in properties if p.pet_friendly)
                
                f.write("SUMMARY STATISTICS:\n")
                f.write(f"Cities Covered: {len(cities)}\n")
                f.write(f"Average Rating: {avg_rating:.2f}\n")
                f.write(f"Pet Friendly Properties: {pet_friendly_count}\n")
                f.write(f"Cities: {', '.join(sorted(cities))}\n\n")
                
                f.write("PROPERTY DETAILS:\n")
                f.write("=" * 50 + "\n\n")
                
                # Property details
                for i, prop in enumerate(properties, 1):
                    f.write(f"{i}. {prop.property_name} - {prop.city}\n")
                    f.write(f"   Property ID: {prop.property_id}\n")
                    f.write(f"   Room Type: {prop.room_type}\n")
                    
                    if prop.rating:
                        f.write(f"   Rating: {prop.rating}/5.0\n")
                    if prop.bedrooms:
                        f.write(f"   Bedrooms: {prop.bedrooms}\n")
                    
                    f.write(f"   Pet Friendly: {'Yes' if prop.pet_friendly else 'No'}\n")
                    
                    if prop.amenities:
                        f.write(f"   Amenities: {', '.join(prop.amenities)}\n")
                    
                    f.write(f"   Description: {prop.description}\n")
                    f.write(f"   Building Type: {prop.building_type}\n")
                    
                    if prop.suite_features:
                        f.write(f"   Suite Features: {', '.join(prop.suite_features)}\n")
                    
                    f.write("\n" + "-" * 30 + "\n\n")
            
            logger.info(f"Plain text file generated successfully: {filename}")
            
        except Exception as e:
            logger.error(f"Error generating plain text: {e}")
    
    def generate_chunked_text(self, properties: List[PropertyData], filename: str = "premiere_suites_chunks.txt", chunk_size: int = 1000):
        """Generate chunked text format optimized for vector embedding"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Write header
                f.write(f"# Premiere Suites Property Database - Chunked for Vector Embedding\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n")
                f.write(f"# Total Properties: {len(properties)}\n")
                f.write(f"# Chunk Size: {chunk_size} characters\n\n")
                
                current_chunk = ""
                chunk_number = 1
                
                for i, prop in enumerate(properties, 1):
                    # Create property text
                    prop_text = self.create_text_chunk(prop, i)
                    
                    # Check if adding this property would exceed chunk size
                    if len(current_chunk) + len(prop_text) > chunk_size and current_chunk:
                        # Write current chunk
                        f.write(f"--- CHUNK {chunk_number} ---\n")
                        f.write(current_chunk.strip() + "\n\n")
                        current_chunk = prop_text
                        chunk_number += 1
                    else:
                        # Add to current chunk
                        if current_chunk:
                            current_chunk += "\n\n" + prop_text
                        else:
                            current_chunk = prop_text
                
                # Write final chunk
                if current_chunk:
                    f.write(f"--- CHUNK {chunk_number} ---\n")
                    f.write(current_chunk.strip() + "\n")
            
            logger.info(f"Chunked text file generated successfully: {filename}")
            
        except Exception as e:
            logger.error(f"Error generating chunked text: {e}")

def main():
    """Main function to run the scraper"""
    scraper = PremiereSuitesScraper(headless=True)
    
    try:
        # Scrape all data
        properties = scraper.scrape_all()
        
        if properties:
            # Save data in multiple formats
            scraper.save_to_json(properties)
            scraper.save_to_csv(properties)
            scraper.generate_pdf(properties)
            scraper.generate_markdown(properties)
            scraper.generate_jsonl(properties)
            scraper.generate_plain_text(properties)
            scraper.generate_chunked_text(properties)
            
            # Print summary
            print(f"\nScraping completed successfully!")
            print(f"Total properties found: {len(properties)}")
            print(f"Cities covered: {len(set(p.city for p in properties))}")
            print(f"Average rating: {sum(p.rating or 0 for p in properties) / len([p for p in properties if p.rating]) if any(p.rating for p in properties) else 0:.2f}")
            print(f"\nFiles generated:")
            print(f"- premiere_suites_data.json")
            print(f"- premiere_suites_data.csv")
            print(f"- premiere_suites_data.pdf (for vector database)")
            print(f"- premiere_suites_data.md (alternative format)")
            print(f"- premiere_suites_data.jsonl (for vector database)")
            print(f"- premiere_suites_data.txt (plain text)")
            print(f"- premiere_suites_chunks.txt (chunked for embedding)")
            
        else:
            print("No properties found. Please check the website structure.")
            
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    finally:
        scraper.close_driver()

if __name__ == "__main__":
    main()
