"""
Premiere Suites AI Platform

A comprehensive AI platform for Premiere Suites with data collection, vectorization, 
and intelligent concierge services. Includes FAQ management, vector database integration, 
and N8N workflow automation.
"""

__version__ = "2.0.0"
__author__ = "Premiere Suites Team"
__description__ = "AI platform for Premiere Suites with data collection, vectorization, and concierge services"

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
