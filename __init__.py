"""
Premiere Suites Scraper

A comprehensive web scraping and data processing system for Premier Suites properties.
Includes FAQ management, vector database integration, and N8N workflow automation.
"""

__version__ = "1.0.0"
__author__ = "Premiere Suites Team"
__description__ = "Web scraping and data processing system for Premier Suites"

# Import main components for easy access
from .src.scrapers import premiere_scraper, faq_scraper
from .src.vector_db import qdrant_setup, langchain_qdrant_integration
from .src.n8n_integration import n8n_setup, deploy_concierge_workflow

__all__ = [
    "premiere_scraper",
    "faq_scraper", 
    "qdrant_setup",
    "langchain_qdrant_integration",
    "n8n_setup",
    "deploy_concierge_workflow"
]
