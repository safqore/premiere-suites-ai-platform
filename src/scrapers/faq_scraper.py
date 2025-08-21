#!/usr/bin/env python3
"""
Premiere Suites FAQ Scraper
Extracts FAQ data from https://premieresuites.com/faq/
Generates JSONL document for vector database ingestion
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
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class FAQData:
    """Data structure for FAQ information"""
    question: str
    answer: str
    category: Optional[str]
    tags: List[str]
    source_url: str
    faq_id: str
    raw_html: str

class PremiereSuitesFAQScraper:
    """Main scraper class for Premiere Suites FAQ website"""
    
    def __init__(self, headless: bool = True):
        self.base_url = "https://premieresuites.com/faq/"
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
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Fix common spacing issues
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between camelCase
        text = re.sub(r'([a-z])(\d)', r'\1 \2', text)     # Add space between letter and number
        text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)  # Add space between number and letter
        
        # Fix specific known issues
        text = text.replace('Ourshort-term', 'Our short-term')
        text = text.replace('Explore thebenefits', 'Explore the benefits')
        text = text.replace('Explore oursearch', 'Explore our search')
        text = text.replace('Learn more aboutPremiere', 'Learn more about Premiere')
        text = text.replace('Visit ourContact', 'Visit our Contact')
        text = text.replace('You cansearch', 'You can search')
        text = text.replace('you cancontact', 'you can contact')
        text = text.replace('Pleasecontact', 'Please contact')
        text = text.replace('pleasecontact', 'please contact')
        text = text.replace('pleaseget', 'please get')
        text = text.replace('Click hereto', 'Click here to')
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def extract_faq_data_from_html(self, html_content: str) -> List[FAQData]:
        """Extract FAQ data from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        faqs = []
        
        # Look for FAQ sections with specific structure
        faq_sections = soup.find_all('div', class_='faq__each')
        
        logger.info(f"Found {len(faq_sections)} FAQ sections")
        
        # Process each FAQ section
        for section in faq_sections:
            try:
                faq_data = self.parse_faq_section(section)
                if faq_data:
                    faqs.append(faq_data)
            except Exception as e:
                logger.warning(f"Error parsing FAQ section: {e}")
                continue
        
        # If no FAQs found with specific structure, try alternative approach
        if not faqs:
            faqs = self.extract_faqs_alternative(soup)
        
        return faqs
    
    def parse_faq_section(self, section) -> Optional[FAQData]:
        """Parse individual FAQ section with improved accuracy"""
        try:
            # Find the question (h3 with class sub-title)
            question_elem = section.find('h3', class_='sub-title')
            if not question_elem:
                return None
            
            question = self.clean_text(question_elem.get_text())
            
            # Find the answer panel
            panel_id = section.get('id', '').replace('fq_', 'fq_') + '_panel'
            answer_panel = section.find('div', id=panel_id)
            
            if not answer_panel:
                # Try alternative panel finding
                answer_panel = section.find('div', class_='psf_panel')
            
            if not answer_panel:
                return None
            
            # Extract and clean answer text
            answer = self.clean_text(answer_panel.get_text())
            
            # Skip if question or answer is too short
            if len(question) < 5 or len(answer) < 10:
                return None
            
            # Generate FAQ ID from section ID
            section_id = section.get('id', '')
            faq_id = section_id.upper() if section_id else f"FAQ_{hash(question) % 1000:03d}"
            
            # Determine category based on content
            category = self.determine_category(question + " " + answer)
            
            # Extract tags
            tags = self.extract_tags_from_text(question + " " + answer)
            
            # Create FAQData object
            faq_data = FAQData(
                question=question,
                answer=answer,
                category=category,
                tags=tags,
                source_url=self.base_url,
                faq_id=faq_id,
                raw_html=str(section)
            )
            
            return faq_data
            
        except Exception as e:
            logger.error(f"Error parsing FAQ section: {e}")
            return None
    
    def extract_faqs_alternative(self, soup) -> List[FAQData]:
        """Alternative FAQ extraction method"""
        faqs = []
        
        # Look for accordion structure
        accordions = soup.find_all('div', class_='accordion')
        
        for i, accordion in enumerate(accordions):
            try:
                # Find question in accordion
                question_elem = accordion.find(['h3', 'h4', 'h5'])
                if not question_elem:
                    continue
                
                question = self.clean_text(question_elem.get_text())
                
                # Find corresponding panel
                panel = accordion.find_next_sibling('div', class_='psf_panel')
                if not panel:
                    continue
                
                answer = self.clean_text(panel.get_text())
                
                if len(question) < 5 or len(answer) < 10:
                    continue
                
                faq_data = FAQData(
                    question=question,
                    answer=answer,
                    category=self.determine_category(question + " " + answer),
                    tags=self.extract_tags_from_text(question + " " + answer),
                    source_url=self.base_url,
                    faq_id=f"FAQ_{i+1:03d}",
                    raw_html=str(accordion)
                )
                
                faqs.append(faq_data)
                
            except Exception as e:
                logger.warning(f"Error parsing accordion: {e}")
                continue
        
        return faqs
    
    def extract_tags_from_text(self, text: str) -> List[str]:
        """Extract relevant tags from text"""
        tags = []
        
        # Common FAQ-related keywords
        keywords = [
            'booking', 'reservation', 'check-in', 'check-out', 'payment', 'cancellation',
            'pet', 'pet-friendly', 'amenities', 'furnished', 'utilities', 'internet',
            'parking', 'laundry', 'cleaning', 'maintenance', 'security', 'deposit',
            'rent', 'lease', 'contract', 'corporate', 'short-term', 'long-term',
            'furniture', 'kitchen', 'bedroom', 'bathroom', 'parking', 'gym', 'pool'
        ]
        
        text_lower = text.lower()
        for keyword in keywords:
            if keyword in text_lower:
                tags.append(keyword)
        
        return tags
    
    def determine_category(self, text: str) -> str:
        """Determine FAQ category based on content with improved accuracy"""
        text_lower = text.lower()
        
        # More specific category matching
        if any(word in text_lower for word in ['book', 'reservation', 'check-in', 'check-out', 'cancel']):
            return "Booking & Reservations"
        elif any(word in text_lower for word in ['payment', 'deposit', 'rent', 'cost', 'price', 'rate', 'fee']):
            return "Payment & Pricing"
        elif any(word in text_lower for word in ['pet', 'animal', 'dog', 'cat']):
            return "Pet Policies"
        elif any(word in text_lower for word in ['alliance', 'corporate', 'business', 'company', 'partner']):
            return "Corporate Services"
        elif any(word in text_lower for word in ['amenity', 'furniture', 'kitchen', 'laundry', 'gym', 'pool', 'housekeeping']):
            return "Amenities & Services"
        elif any(word in text_lower for word in ['smoking', 'policy', 'rule', 'regulation']):
            return "Rules & Regulations"
        elif any(word in text_lower for word in ['wifi', 'internet', 'phone', 'tv', 'cable']):
            return "Technology & Services"
        else:
            return "General"
    
    def scrape_with_requests(self) -> List[FAQData]:
        """Scrape using requests library"""
        try:
            logger.info("Starting FAQ scraping with requests...")
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            faqs = self.extract_faq_data_from_html(response.text)
            logger.info(f"Extracted {len(faqs)} FAQs using requests")
            return faqs
            
        except Exception as e:
            logger.error(f"Error scraping with requests: {e}")
            return []
    
    def scrape_with_selenium(self) -> List[FAQData]:
        """Scrape using Selenium for dynamic content"""
        try:
            logger.info("Starting FAQ scraping with Selenium...")
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
            faqs = self.extract_faq_data_from_html(page_source)
            
            logger.info(f"Extracted {len(faqs)} FAQs using Selenium")
            return faqs
            
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
    
    def scrape_all(self) -> List[FAQData]:
        """Scrape using both methods and combine results with improved deduplication"""
        logger.info("Starting comprehensive FAQ scraping...")
        
        # Try requests first
        faqs_requests = self.scrape_with_requests()
        
        # Try Selenium for dynamic content
        faqs_selenium = self.scrape_with_selenium()
        
        # Combine results
        all_faqs = faqs_requests + faqs_selenium
        
        # Improved deduplication based on question content
        seen = set()
        unique_faqs = []
        
        for faq in all_faqs:
            # Create a more robust key for deduplication
            question_key = re.sub(r'[^\w\s]', '', faq.question.lower()).strip()
            question_key = re.sub(r'\s+', ' ', question_key)
            
            if question_key and question_key not in seen:
                seen.add(question_key)
                unique_faqs.append(faq)
        
        # Sort by FAQ ID to maintain order
        unique_faqs.sort(key=lambda x: x.faq_id)
        
        logger.info(f"Total unique FAQs found: {len(unique_faqs)}")
        return unique_faqs
    
    def generate_jsonl(self, faqs: List[FAQData], filename: str = "premiere_suites_faq_data.jsonl"):
        """Generate JSON Lines format - OPTIMAL for vector database ingestion"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Write metadata as first line
                metadata = {
                    "type": "metadata",
                    "generated_on": datetime.now().isoformat(),
                    "total_faqs": len(faqs),
                    "source_url": self.base_url,
                    "purpose": "vector_database_ingestion",
                    "format": "jsonl",
                    "content_type": "faq"
                }
                f.write(json.dumps(metadata, ensure_ascii=False) + '\n')
                
                # Write summary statistics
                categories = set(faq.category for faq in faqs)
                all_tags = []
                for faq in faqs:
                    all_tags.extend(faq.tags)
                unique_tags = list(set(all_tags))
                
                summary = {
                    "type": "summary",
                    "categories_covered": len(categories),
                    "total_tags": len(unique_tags),
                    "categories": sorted(list(categories)),
                    "top_tags": sorted(unique_tags)[:20]  # Top 20 tags
                }
                f.write(json.dumps(summary, ensure_ascii=False) + '\n')
                
                # Write each FAQ as a separate JSON line
                for i, faq in enumerate(faqs, 1):
                    # Create structured FAQ data
                    faq_data = {
                        "type": "faq",
                        "id": faq.faq_id,
                        "question": faq.question,
                        "answer": faq.answer,
                        "category": faq.category,
                        "tags": faq.tags,
                        "source_url": faq.source_url
                    }
                    
                    # Also create a text chunk for embedding
                    text_chunk = self.create_text_chunk(faq, i)
                    faq_data["text_chunk"] = text_chunk
                    
                    f.write(json.dumps(faq_data, ensure_ascii=False) + '\n')
            
            logger.info(f"FAQ JSON Lines file generated successfully: {filename}")
            
        except Exception as e:
            logger.error(f"Error generating FAQ JSON Lines: {e}")
    
    def create_text_chunk(self, faq: FAQData, index: int) -> str:
        """Create optimized text chunk for vector embedding"""
        chunks = []
        
        # FAQ header
        chunks.append(f"FAQ {index}: {faq.question}")
        chunks.append(f"Category: {faq.category}")
        
        # Answer
        chunks.append(f"Answer: {faq.answer}")
        
        # Tags
        if faq.tags:
            chunks.append(f"Tags: {', '.join(faq.tags)}")
        
        return " | ".join(chunks)

    def save_to_json(self, faqs: List[FAQData], filename: str = "premiere_suites_faq_data.json"):
        """Save FAQ data to JSON format"""
        try:
            data = {
                "metadata": {
                    "generated_on": datetime.now().isoformat(),
                    "total_faqs": len(faqs),
                    "source_url": self.base_url,
                    "purpose": "vector_database_ingestion",
                    "format": "json",
                    "content_type": "faq"
                },
                "summary": {
                    "categories_covered": len(set(faq.category for faq in faqs)),
                    "total_tags": len(set(tag for faq in faqs for tag in faq.tags)),
                    "categories": sorted(list(set(faq.category for faq in faqs))),
                    "top_tags": sorted(list(set(tag for faq in faqs for tag in faq.tags)))[:20]
                },
                "faqs": [
                    {
                        "id": faq.faq_id,
                        "question": faq.question,
                        "answer": faq.answer,
                        "category": faq.category,
                        "tags": faq.tags,
                        "source_url": faq.source_url,
                        "text_chunk": self.create_text_chunk(faq, i + 1)
                    }
                    for i, faq in enumerate(faqs)
                ]
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"FAQ JSON file generated successfully: {filename}")
            
        except Exception as e:
            logger.error(f"Error generating FAQ JSON: {e}")

    def save_to_csv(self, faqs: List[FAQData], filename: str = "premiere_suites_faq_data.csv"):
        """Save FAQ data to CSV format"""
        try:
            import csv
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    'ID', 'Question', 'Answer', 'Category', 'Tags', 'Source URL', 'Text Chunk'
                ])
                
                # Write data
                for i, faq in enumerate(faqs, 1):
                    writer.writerow([
                        faq.faq_id,
                        faq.question,
                        faq.answer,
                        faq.category,
                        ', '.join(faq.tags),
                        faq.source_url,
                        self.create_text_chunk(faq, i)
                    ])
            
            logger.info(f"FAQ CSV file generated successfully: {filename}")
            
        except Exception as e:
            logger.error(f"Error generating FAQ CSV: {e}")

    def generate_pdf(self, faqs: List[FAQData], filename: str = "premiere_suites_faq_data.pdf"):
        """Generate PDF document for FAQ data"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            story.append(Paragraph("Premiere Suites FAQ Data", title_style))
            story.append(Spacer(1, 20))
            
            # Metadata
            metadata_style = ParagraphStyle(
                'Metadata',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.grey
            )
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", metadata_style))
            story.append(Paragraph(f"Total FAQs: {len(faqs)}", metadata_style))
            story.append(Paragraph(f"Source: {self.base_url}", metadata_style))
            story.append(Spacer(1, 20))
            
            # Summary
            categories = set(faq.category for faq in faqs)
            all_tags = [tag for faq in faqs for tag in faq.tags]
            unique_tags = list(set(all_tags))
            
            summary_style = ParagraphStyle(
                'Summary',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=20
            )
            story.append(Paragraph("Summary", styles['Heading2']))
            story.append(Paragraph(f"Categories covered: {len(categories)}", summary_style))
            story.append(Paragraph(f"Categories: {', '.join(sorted(categories))}", summary_style))
            story.append(Paragraph(f"Total unique tags: {len(unique_tags)}", summary_style))
            story.append(Paragraph(f"Top tags: {', '.join(sorted(unique_tags)[:10])}", summary_style))
            story.append(Spacer(1, 20))
            
            # FAQs by category
            faqs_by_category = {}
            for faq in faqs:
                if faq.category not in faqs_by_category:
                    faqs_by_category[faq.category] = []
                faqs_by_category[faq.category].append(faq)
            
            for category in sorted(faqs_by_category.keys()):
                story.append(Paragraph(f"Category: {category}", styles['Heading2']))
                story.append(Spacer(1, 10))
                
                for i, faq in enumerate(faqs_by_category[category], 1):
                    # Question
                    question_style = ParagraphStyle(
                        'Question',
                        parent=styles['Normal'],
                        fontSize=12,
                        fontName='Helvetica-Bold',
                        spaceAfter=5
                    )
                    story.append(Paragraph(f"Q{i}: {faq.question}", question_style))
                    
                    # Answer
                    answer_style = ParagraphStyle(
                        'Answer',
                        parent=styles['Normal'],
                        fontSize=11,
                        leftIndent=20,
                        spaceAfter=10
                    )
                    story.append(Paragraph(f"A: {faq.answer}", answer_style))
                    
                    # Tags
                    if faq.tags:
                        tag_style = ParagraphStyle(
                            'Tags',
                            parent=styles['Normal'],
                            fontSize=9,
                            textColor=colors.blue,
                            leftIndent=20,
                            spaceAfter=10
                        )
                        story.append(Paragraph(f"Tags: {', '.join(faq.tags)}", tag_style))
                    
                    story.append(Spacer(1, 10))
                
                story.append(PageBreak())
            
            doc.build(story)
            logger.info(f"FAQ PDF file generated successfully: {filename}")
            
        except Exception as e:
            logger.error(f"Error generating FAQ PDF: {e}")

    def generate_markdown(self, faqs: List[FAQData], filename: str = "premiere_suites_faq_data.md"):
        """Generate Markdown document for FAQ data"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Header
                f.write("# Premiere Suites FAQ Data\n\n")
                f.write(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Total FAQs:** {len(faqs)}\n")
                f.write(f"**Source:** {self.base_url}\n\n")
                
                # Summary
                categories = set(faq.category for faq in faqs)
                all_tags = [tag for faq in faqs for tag in faq.tags]
                unique_tags = list(set(all_tags))
                
                f.write("## Summary\n\n")
                f.write(f"- **Categories covered:** {len(categories)}\n")
                f.write(f"- **Categories:** {', '.join(sorted(categories))}\n")
                f.write(f"- **Total unique tags:** {len(unique_tags)}\n")
                f.write(f"- **Top tags:** {', '.join(sorted(unique_tags)[:10])}\n\n")
                
                # FAQs by category
                faqs_by_category = {}
                for faq in faqs:
                    if faq.category not in faqs_by_category:
                        faqs_by_category[faq.category] = []
                    faqs_by_category[faq.category].append(faq)
                
                for category in sorted(faqs_by_category.keys()):
                    f.write(f"## {category}\n\n")
                    
                    for i, faq in enumerate(faqs_by_category[category], 1):
                        f.write(f"### Q{i}: {faq.question}\n\n")
                        f.write(f"{faq.answer}\n\n")
                        
                        if faq.tags:
                            f.write(f"**Tags:** {', '.join(faq.tags)}\n\n")
                        
                        f.write("---\n\n")
            
            logger.info(f"FAQ Markdown file generated successfully: {filename}")
            
        except Exception as e:
            logger.error(f"Error generating FAQ Markdown: {e}")

    def generate_plain_text(self, faqs: List[FAQData], filename: str = "premiere_suites_faq_data.txt"):
        """Generate plain text document for FAQ data"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Header
                f.write("Premiere Suites FAQ Data\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total FAQs: {len(faqs)}\n")
                f.write(f"Source: {self.base_url}\n\n")
                
                # Summary
                categories = set(faq.category for faq in faqs)
                all_tags = [tag for faq in faqs for tag in faq.tags]
                unique_tags = list(set(all_tags))
                
                f.write("SUMMARY\n")
                f.write("-" * 20 + "\n")
                f.write(f"Categories covered: {len(categories)}\n")
                f.write(f"Categories: {', '.join(sorted(categories))}\n")
                f.write(f"Total unique tags: {len(unique_tags)}\n")
                f.write(f"Top tags: {', '.join(sorted(unique_tags)[:10])}\n\n")
                
                # FAQs by category
                faqs_by_category = {}
                for faq in faqs:
                    if faq.category not in faqs_by_category:
                        faqs_by_category[faq.category] = []
                    faqs_by_category[faq.category].append(faq)
                
                for category in sorted(faqs_by_category.keys()):
                    f.write(f"CATEGORY: {category}\n")
                    f.write("-" * 30 + "\n\n")
                    
                    for i, faq in enumerate(faqs_by_category[category], 1):
                        f.write(f"Q{i}: {faq.question}\n")
                        f.write(f"A: {faq.answer}\n")
                        
                        if faq.tags:
                            f.write(f"Tags: {', '.join(faq.tags)}\n")
                        
                        f.write("\n" + "-" * 50 + "\n\n")
            
            logger.info(f"FAQ plain text file generated successfully: {filename}")
            
        except Exception as e:
            logger.error(f"Error generating FAQ plain text: {e}")

    def generate_chunked_text(self, faqs: List[FAQData], filename: str = "premiere_suites_faq_chunks.txt", chunk_size: int = 1000):
        """Generate chunked text for vector database ingestion"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                current_chunk = []
                current_size = 0
                chunk_number = 1
                
                for i, faq in enumerate(faqs, 1):
                    text_chunk = self.create_text_chunk(faq, i)
                    
                    # Check if adding this FAQ would exceed chunk size
                    if current_size + len(text_chunk) > chunk_size and current_chunk:
                        # Write current chunk
                        f.write(f"--- CHUNK {chunk_number} ---\n")
                        f.write("\n\n".join(current_chunk))
                        f.write("\n\n")
                        
                        # Start new chunk
                        current_chunk = [text_chunk]
                        current_size = len(text_chunk)
                        chunk_number += 1
                    else:
                        # Add to current chunk
                        current_chunk.append(text_chunk)
                        current_size += len(text_chunk)
                
                # Write final chunk
                if current_chunk:
                    f.write(f"--- CHUNK {chunk_number} ---\n")
                    f.write("\n\n".join(current_chunk))
                    f.write("\n\n")
            
            logger.info(f"FAQ chunked text file generated successfully: {filename}")
            
        except Exception as e:
            logger.error(f"Error generating FAQ chunked text: {e}")

def main():
    """Main function to run the FAQ scraper"""
    scraper = PremiereSuitesFAQScraper(headless=True)
    
    try:
        # Scrape all FAQ data
        faqs = scraper.scrape_all()
        
        if faqs:
            # Generate all output formats
            scraper.save_to_json(faqs)
            scraper.save_to_csv(faqs)
            scraper.generate_pdf(faqs)
            scraper.generate_markdown(faqs)
            scraper.generate_plain_text(faqs)
            scraper.generate_chunked_text(faqs)
            scraper.generate_jsonl(faqs)
            
            # Print summary
            print(f"\nFAQ Scraping completed successfully!")
            print(f"Total FAQs found: {len(faqs)}")
            
            # Show categories
            categories = set(faq.category for faq in faqs)
            print(f"Categories covered: {len(categories)}")
            print(f"Categories: {', '.join(sorted(categories))}")
            
            # Show some sample FAQs
            print(f"\nSample FAQs:")
            for i, faq in enumerate(faqs[:3], 1):
                print(f"{i}. Q: {faq.question[:100]}...")
                print(f"   A: {faq.answer[:100]}...")
                print(f"   Category: {faq.category}")
                print()
            
            print(f"Files generated:")
            print(f"- premiere_suites_faq_data.json (structured data)")
            print(f"- premiere_suites_faq_data.csv (tabular format)")
            print(f"- premiere_suites_faq_data.pdf (for vector database)")
            print(f"- premiere_suites_faq_data.md (alternative format)")
            print(f"- premiere_suites_faq_data.txt (plain text)")
            print(f"- premiere_suites_faq_chunks.txt (chunked for embedding)")
            print(f"- premiere_suites_faq_data.jsonl (for vector database)")
            
        else:
            print("No FAQs found. Please check the website structure.")
            
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    finally:
        scraper.close_driver()

if __name__ == "__main__":
    main()
