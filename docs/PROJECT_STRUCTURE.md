# Project Structure Documentation

## Overview

The Premiere Suites Scraper has been reorganized into a clean, maintainable structure following Python best practices. This document outlines the new organization and provides guidance for developers.

## Directory Structure

```
premiere_suites_scraper/
├── src/                          # Source code
│   ├── __init__.py              # Package initialization
│   ├── scrapers/                # Web scraping modules
│   │   ├── __init__.py         # Scrapers package
│   │   ├── premiere_scraper.py # Main property scraper
│   │   └── faq_scraper.py      # FAQ scraper
│   ├── vector_db/              # Vector database operations
│   │   ├── __init__.py         # Vector DB package
│   │   ├── qdrant_setup.py     # Qdrant database setup
│   │   ├── langchain_qdrant_integration.py # LangChain integration
│   │   ├── langchain_faq_integration.py # FAQ LangChain integration
│   │   ├── search_faqs.py      # FAQ search functionality
│   │   ├── search_properties.py # Property search
│   │   ├── setup_faq_vectorization.py # FAQ setup
│   │   └── cloud_setup.py      # Cloud deployment
│   ├── n8n_integration/        # n8n workflow management
│   │   ├── __init__.py         # n8n package
│   │   ├── n8n_setup.py        # n8n setup and configuration
│   │   ├── deploy_concierge_workflow.py # Workflow deployment
│   │   ├── deploy_faq_workflow.py # FAQ workflow deployment
│   │   ├── faq_to_qdrant_workflow.py # FAQ to Qdrant workflow
│   │   ├── debug_n8n_issue.py  # Debugging tools
│   │   ├── test_faq_workflow.py # FAQ workflow testing
│   │   └── example_cloud_usage.py # Usage examples
│   └── utils/                  # Utility functions
│       ├── __init__.py         # Utils package
│       ├── map_faq_sections.py # FAQ section mapping
│       └── quick_start.py      # Quick start utilities
├── tests/                      # Test files
│   ├── __init__.py            # Tests package
│   ├── test_scraper.py        # Scraper tests
│   ├── test_concierge_faq.py  # FAQ tests
│   ├── test_n8n_integration.py # n8n integration tests
│   ├── test_n8n_simulation.py # n8n simulation tests
│   ├── test_search_filters.py # Search filter tests
│   ├── test_vectorization_properties.py # Vectorization tests
│   └── test_langchain_integration.py # LangChain integration tests
├── data/                       # Data storage
│   ├── raw/                   # Raw scraped data
│   │   ├── .gitkeep          # Preserve directory
│   │   ├── premiere_suites_data.pdf
│   │   ├── premiere_suites_data.csv
│   │   ├── premiere_suites_data.txt
│   │   └── premiere_suites_data.md
│   ├── processed/             # Processed data files
│   │   ├── .gitkeep          # Preserve directory
│   │   ├── premiere_suites_data.json
│   │   ├── premiere_suites_data.jsonl
│   │   ├── premiere_suites_faq_data.jsonl
│   │   ├── premiere_suites_faq_data.json
│   │   └── premiere_suites_chunks.txt
│   └── exports/               # Export files
│       └── .gitkeep          # Preserve directory
├── docs/                       # Documentation
│   ├── guides/                # User guides
│   │   ├── README.md         # Main documentation
│   │   ├── CONCIERGE_WORKFLOW_GUIDE.md
│   │   ├── FAQ_VECTORIZATION_GUIDE.md
│   │   ├── FAQ_TO_QDRANT_WORKFLOW_GUIDE.md
│   │   ├── IMPORT_WORKFLOW_TO_N8N.md
│   │   ├── LANGCHAIN_QDRANT_GUIDE.md
│   │   ├── MANUAL_WORKFLOW_CREATION.md
│   │   ├── N8N_INTEGRATION_GUIDE.md
│   │   ├── QDANT_SETUP_GUIDE.md
│   │   ├── QDRANT_CLOUD_GUIDE.md
│   │   ├── SUMMARY.md
│   │   └── VECTOR_DB_GUIDE.md
│   ├── workflows/             # n8n workflow files
│   ├── FAQ_DATA_COMPLETION_SUMMARY.md
│   ├── PROPERTY_DATA_COMPLETION_SUMMARY.md
│   ├── PAGECONTENT_STANDARDIZATION_SUMMARY.md
│   ├── FAQ_WORKFLOW_SUMMARY.md
│   ├── VECTORIZATION_PROPERTIES_GUIDE.md
│   ├── FAQ_VECTORIZATION_GUIDE.md
│   └── qdrant_web_interface_guide.md
├── scripts/                    # Setup and utility scripts
│   ├── setup.py               # Automated setup script
│   ├── convert_jsonl_to_json.py # JSONL to JSON converter
│   ├── check_and_fix_pagecontent.py # Page content checker
│   ├── vectorize_faq_data.py  # FAQ vectorization script
│   ├── recreate_collections_with_properties.py # Collection recreation
│   ├── recreate_collections_langchain.py # LangChain collection recreation
│   └── start_qdrant_local.py  # Local Qdrant startup
├── examples/                   # Example usage
│   ├── faq_workflow_example.py
│   ├── langchain_faq_example.py
│   └── langchain_qdrant_example.py
├── config/                     # Configuration files
│   ├── docker-compose.yml     # Docker configuration
│   └── env.example            # Environment template
├── web/                        # Web interface files
│   ├── premiere_suites_demo.html # Demo interface
│   ├── test_webhook.html      # Webhook testing interface
│   └── simple_webhook_test.html # Simple webhook test
├── logs/                       # Application logs
├── __init__.py                # Root package initialization
├── main.py                    # Main application entry point
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Project configuration
├── Makefile                  # Build and deployment commands
└── README.md                 # Project documentation
├── logs/                       # Log files
│   └── .gitkeep              # Preserve directory
├── main.py                     # Main entry point
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Modern Python project config
├── Makefile                   # Development tasks
├── README.md                  # Project overview
├── .gitignore                 # Git ignore rules
└── PROJECT_STRUCTURE.md       # This file
```

## Module Organization

### 1. Scrapers (`src/scrapers/`)

Contains all web scraping functionality:

- **`premiere_scraper.py`**: Main scraper for Premiere Suites properties
- **`faq_scraper.py`**: Scraper for FAQ data

**Usage:**

```python
from src.scrapers import PremiereSuitesScraper, FAQScraper

scraper = PremiereSuitesScraper(headless=True)
properties = scraper.scrape_all()
```

### 2. Vector Database (`src/vector_db/`)

Handles all vector database operations:

- **`qdrant_setup.py`**: Qdrant database setup and configuration
- **`vectorize_faq_data.py`**: FAQ data vectorization
- **`search_faqs.py`**: FAQ search functionality
- **`search_properties.py`**: Property search functionality
- **`setup_faq_vectorization.py`**: FAQ vectorization setup
- **`cloud_setup.py`**: Cloud deployment configuration

**Usage:**

```python
from src.vector_db import QdrantSetup, FAQVectorizer, FAQSearcher

qdrant = QdrantSetup()
qdrant.setup_collection("properties")
```

### 3. n8n Integration (`src/n8n_integration/`)

Manages n8n workflow operations:

- **`n8n_setup.py`**: n8n setup and configuration
- **`deploy_concierge_workflow.py`**: Workflow deployment
- **`debug_n8n_issue.py`**: Debugging tools
- **`example_cloud_usage.py`**: Usage examples

**Usage:**

```python
from src.n8n_integration import N8NSetup, ConciergeWorkflowDeployer

n8n = N8NSetup()
n8n.deploy_workflow("concierge")
```

### 4. Utils (`src/utils/`)

Contains utility functions:

- **`map_faq_sections.py`**: FAQ section mapping utilities
- **`quick_start.py`**: Quick start utilities

**Usage:**

```python
from src.utils import FAQSectionMapper, QuickStart

mapper = FAQSectionMapper()
sections = mapper.map_sections(faq_data)
```

## Data Organization

### Data Directory Structure

- **`data/raw/`**: Raw scraped data (not tracked in git)
- **`data/processed/`**: Processed data files (tracked in git)
- **`data/exports/`**: Export files for external use

### Data Files

The scraper generates several output formats:

1. **JSON** (`premiere_suites_data.json`): Raw structured data
2. **CSV** (`premiere_suites_data.csv`): Tabular format
3. **PDF** (`premiere_suites_data.pdf`): Vector database optimized
4. **Markdown** (`premiere_suites_data.md`): Human-readable format
5. **JSONL** (`premiere_suites_data.jsonl`): Line-delimited JSON
6. **Text** (`premiere_suites_data.txt`): Plain text format

## Documentation Organization

### Guides (`docs/guides/`)

- **`README.md`**: Main project documentation
- **`CONCIERGE_WORKFLOW_GUIDE.md`**: Concierge workflow setup
- **`FAQ_VECTORIZATION_GUIDE.md`**: FAQ processing guide
- **`N8N_INTEGRATION_GUIDE.md`**: n8n integration guide
- **`QDANT_SETUP_GUIDE.md`**: Qdrant setup guide
- **`QDRANT_CLOUD_GUIDE.md`**: Cloud deployment guide
- **`VECTOR_DB_GUIDE.md`**: Vector database guide
- **`SUMMARY.md`**: Project summary

### Workflows (`docs/workflows/`)

Contains all n8n workflow JSON files for automation.

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Scraper settings
HEADLESS_MODE=true
REQUEST_TIMEOUT=30
SCROLL_PAUSE=2

# Vector database settings
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=your_api_key

# n8n settings
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your_api_key
```

### Configuration Files

- **`config/docker-compose.yml`**: Docker configuration
- **`config/env.example`**: Environment template

## Development Workflow

### Setup

```bash
# Automated setup
make setup

# Manual setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Common Tasks

```bash
make help      # Show available commands
make setup     # Set up the project
make install   # Install dependencies
make test      # Run tests
make run       # Run the scraper
make clean     # Clean up generated files
make lint      # Run linting
make format    # Format code
```

### Testing

```bash
# Run all tests
make test

# Run specific test
python -m pytest tests/test_scraper.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## Import Structure

### Before (Old Structure)

```python
from premiere_scraper import PremiereSuitesScraper
from qdrant_setup import QdrantSetup
```

### After (New Structure)

```python
from src.scrapers import PremiereSuitesScraper
from src.vector_db import QdrantSetup
```

## Migration Notes

### For Existing Code

1. **Update imports**: Change from direct imports to package imports
2. **Update file paths**: Data files are now in `data/processed/`
3. **Update configuration**: Use the new config structure

### For New Development

1. **Use package imports**: Import from `src.*` modules
2. **Follow the structure**: Place new code in appropriate directories
3. **Add tests**: Place tests in the `tests/` directory
4. **Update documentation**: Add guides to `docs/guides/`

## Benefits of New Structure

1. **Modularity**: Clear separation of concerns
2. **Maintainability**: Easy to find and modify code
3. **Scalability**: Easy to add new features
4. **Testing**: Organized test structure
5. **Documentation**: Clear documentation organization
6. **Configuration**: Centralized configuration management
7. **Development**: Standard development tools and workflows

## Next Steps

1. **Update existing scripts**: Modify any scripts that reference old file locations
2. **Add type hints**: Consider adding type hints to improve code quality
3. **Add more tests**: Expand test coverage
4. **Documentation**: Keep documentation up to date
5. **CI/CD**: Consider adding continuous integration
