# Premiere Suites Web Scraper

A comprehensive web scraper for extracting property data from [Premiere Suites](https://premieresuites.com/find-your-match/) and generating structured documents for vector database ingestion.

## 🏗️ Project Structure

The project follows a clean, organized structure with proper separation of concerns:

```
premiere_suites_scraper/
├── src/                          # Source code
│   ├── scrapers/                # Web scraping modules
│   │   ├── premiere_scraper.py # Main property scraper
│   │   └── faq_scraper.py      # FAQ scraper
│   ├── vector_db/              # Vector database operations
│   │   ├── qdrant_setup.py     # Qdrant database setup
│   │   ├── langchain_qdrant_integration.py # LangChain integration
│   │   ├── langchain_faq_integration.py # FAQ LangChain integration
│   │   ├── search_faqs.py      # FAQ search functionality
│   │   └── search_properties.py # Property search
│   ├── n8n_integration/        # n8n workflow management
│   │   ├── n8n_setup.py        # n8n setup and configuration
│   │   ├── deploy_concierge_workflow.py # Workflow deployment
│   │   ├── deploy_faq_workflow.py # FAQ workflow deployment
│   │   └── faq_to_qdrant_workflow.py # FAQ to Qdrant workflow
│   └── utils/                  # Utility functions
│       ├── map_faq_sections.py # FAQ section mapping
│       └── quick_start.py      # Quick start utilities
├── tests/                      # Test files
├── data/                       # Data storage
│   ├── raw/                   # Raw scraped data (PDF, CSV, TXT, MD)
│   ├── processed/             # Processed data files (JSON, JSONL)
│   └── exports/               # Export files
├── docs/                       # Documentation
│   ├── guides/                # User guides and tutorials
│   ├── workflows/             # n8n workflow files
│   └── *.md                   # Project documentation summaries
├── scripts/                    # Utility scripts
│   ├── convert_jsonl_to_json.py # Data format conversion
│   ├── check_and_fix_pagecontent.py # Content validation
│   ├── vectorize_faq_data.py  # FAQ vectorization
│   └── start_qdrant_local.py  # Local Qdrant startup
├── examples/                   # Example usage and tutorials
├── config/                     # Configuration files
├── web/                        # Web interface files
│   ├── premiere_suites_demo.html # Demo interface
│   ├── test_webhook.html      # Webhook testing interface
│   └── simple_webhook_test.html # Simple webhook test
├── logs/                       # Log files
├── __init__.py                # Root package initialization
├── main.py                    # Main entry point
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Modern Python project config
├── Makefile                  # Development tasks
└── README.md                 # Project overview
```

## 📁 File Organization

The project follows a clean, organized structure to maintain code quality and ease of development:

### **Source Code (`src/`)**

- **`scrapers/`**: Web scraping modules for properties and FAQs
- **`vector_db/`**: Vector database operations and integrations
- **`n8n_integration/`**: n8n workflow management and deployment
- **`utils/`**: Utility functions and helper modules

### **Data Management (`data/`)**

- **`raw/`**: Original scraped data (PDF, CSV, TXT, MD files)
- **`processed/`**: Processed and structured data (JSON, JSONL files)
- **`exports/`**: Files ready for external use or distribution

### **Documentation (`docs/`)**

- **`guides/`**: User guides, tutorials, and setup instructions
- **`workflows/`**: n8n workflow JSON files
- **`PROJECT_STRUCTURE.md`**: Detailed project structure documentation
- **`PROJECT_REORGANIZATION_SUMMARY.md`**: Summary of project reorganization
- **`PROJECT_LAYOUT_FIXES.md`**: Documentation of layout improvements
- **`*.md`**: Project documentation summaries and completion reports

### **Scripts (`scripts/`)**

- Data conversion and processing utilities
- Content validation and fixing tools
- Vectorization and database setup scripts
- Local development environment setup
- **`update_file_references.py`**: Migration script to update file paths to new structure
- **`convert_text_chunks_to_pagecontent.py`**: Converts `text_chunk` fields to `pageContent` for consistency

### **Tests (`tests/`)**

- Unit tests for all modules
- Integration tests for workflows
- Vectorization and search functionality tests

### **Examples (`examples/`)**

- Usage examples and tutorials
- LangChain integration examples
- FAQ workflow examples

## 🚀 Quick Start

### Migration from Old Structure

If you're updating from the previous structure where files were in the root directory, run the migration script:

```bash
# Update file references to new organized structure
python scripts/update_file_references.py
```

This script will automatically update any hardcoded file paths in your Python files to reference the new organized structure.

### Option 1: Automated Setup

```bash
# Clone the repository
git clone <repository-url>
cd premiere_suites_scraper

# Run automated setup
make setup

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run the scraper
make run
```

### Option 2: Manual Setup

```bash
# Clone the repository
git clone <repository-url>
cd premiere_suites_scraper

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the scraper
python main.py
```

## 📋 Features

- **Multi-format Output**: Generates JSON, CSV, PDF, and Markdown files
- **Comprehensive Data Extraction**: Extracts property names, cities, ratings, amenities, descriptions, and more
- **PDF Generation**: Creates structured PDF documents optimized for vector database ingestion
- **Dual Scraping Methods**: Uses both requests and Selenium for maximum data extraction
- **Error Handling**: Robust error handling and logging
- **Deduplication**: Automatically removes duplicate properties
- **Vector Database Integration**: Ready-to-use vector database setup and search functionality
- **n8n Workflow Support**: Pre-built workflows for automation

## 🛠️ Development

### Available Commands

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

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
python -m pytest tests/test_scraper.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint
```

## 📊 Output Files

The scraper generates the following files organized by type:

### **Raw Data (`data/raw/`)**

- **`premiere_suites_data.pdf`**: Original PDF document
- **`premiere_suites_data.csv`**: Raw CSV data
- **`premiere_suites_data.txt`**: Plain text format
- **`premiere_suites_data.md`**: Markdown format

### **Processed Data (`data/processed/`)**

- **`premiere_suites_data.json`**: Structured JSON data with complete property information
- **`premiere_suites_data.jsonl`**: Line-delimited JSON format for streaming (with `pageContent` field)
- **`premiere_suites_faq_data.jsonl`**: FAQ data in JSONL format (with `pageContent` field)
- **`premiere_suites_faq_data.json`**: FAQ data in JSON format (with `pageContent` field)
- **`premiere_suites_chunks.txt`**: Text chunks for vectorization

### **Key Files**

1. **`data/raw/premiere_suites_data.pdf`** - Primary file for vector database ingestion

   - Structured PDF document with property information
   - Optimized for text extraction and vector embedding
   - Includes summary statistics and detailed property listings
   - Suitable for n8n automation workflows

2. **`data/processed/premiere_suites_data.json`** - Raw structured data in JSON format

   - Complete property information with all extracted fields
   - Useful for data analysis and processing

3. **`data/raw/premiere_suites_data.csv`** - Tabular data format

   - Compatible with spreadsheet applications
   - Easy to import into databases

4. **`data/raw/premiere_suites_data.md`** - Markdown format for easy reading
   - Alternative format for vector database ingestion
   - Human-readable structure

## 🔧 Configuration

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

### Programmatic Usage

```python
from src.scrapers import PremiereSuitesScraper
from src.vector_db import QdrantSetup

# Initialize scraper
scraper = PremiereSuitesScraper(headless=True)

# Scrape data
properties = scraper.scrape_all()

# Generate PDF for vector database
scraper.generate_pdf(properties, "data/processed/premiere_suites_data.pdf")

# Set up vector database
qdrant = QdrantSetup()
qdrant.setup_collection("properties")
```

## 📚 Documentation

- **[Vector Database Guide](docs/guides/VECTOR_DB_GUIDE.md)** - Setting up and using vector databases
- **[n8n Integration Guide](docs/guides/N8N_INTEGRATION_GUIDE.md)** - Automating workflows with n8n
- **[FAQ Vectorization Guide](docs/guides/FAQ_VECTORIZATION_GUIDE.md)** - Processing FAQ data
- **[Qdrant Setup Guide](docs/guides/QDANT_SETUP_GUIDE.md)** - Qdrant database configuration
- **[Qdrant Cloud Guide](docs/guides/QDRANT_CLOUD_GUIDE.md)** - Cloud deployment options

## 🔍 Vector Database Integration

### For n8n Workflows

1. **Upload the PDF**: Use the generated `premiere_suites_data.pdf` file
2. **Text Extraction**: Extract text from the PDF using n8n's PDF nodes
3. **Chunking**: Split the text into appropriate chunks for embedding
4. **Vector Embedding**: Generate embeddings using your preferred model
5. **Database Storage**: Store in your vector database (Pinecone, Weaviate, etc.)

### Example n8n Workflow

```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.readPdf",
      "parameters": {
        "operation": "fromFile",
        "filePath": "data/processed/premiere_suites_data.pdf"
      }
    },
    {
      "type": "n8n-nodes-base.splitInBatches",
      "parameters": {
        "batchSize": 1000
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "your-embedding-api-endpoint",
        "method": "POST"
      }
    }
  ]
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Chrome/Chromium not found**:

   - Install Chrome or Chromium browser
   - Ensure it's in your system PATH

2. **No properties found**:

   - Check internet connection
   - Website structure may have changed
   - Try running with `headless=False` for debugging

3. **PDF generation errors**:

   - Ensure ReportLab is installed: `pip install reportlab`
   - Check write permissions in output directory

4. **Import errors**:
   - Make sure you're running from the project root
   - Ensure virtual environment is activated
   - Check that all dependencies are installed

### Debug Mode

Run with visible browser for debugging:

```python
scraper = PremiereSuitesScraper(headless=False)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Add tests if applicable
5. Run tests: `make test`
6. Submit a pull request

## 📄 License

This project is for educational and research purposes. Please ensure compliance with applicable laws and website terms of service.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section
2. Review the logs for error messages
3. Open an issue with detailed information about the problem

## 📈 Changelog

### v2.0.0

- Reorganized project structure for better maintainability
- Added proper Python package structure
- Improved documentation and guides
- Added development tools (Makefile, setup scripts)
- Enhanced vector database integration

### v1.0.0

- Initial release
- PDF generation for vector database ingestion
- Multi-format output support
- Comprehensive property data extraction
