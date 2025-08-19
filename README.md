# Premiere Suites Web Scraper

A comprehensive web scraper for extracting property data from [Premiere Suites](https://premieresuites.com/find-your-match/) and generating structured documents for vector database ingestion.

## 🏗️ Project Structure

```
premiere_suites_scraper/
├── src/                    # Source code
│   ├── scrapers/          # Web scraping modules
│   │   ├── premiere_scraper.py
│   │   └── faq_scraper.py
│   ├── vector_db/         # Vector database operations
│   │   ├── qdrant_setup.py
│   │   ├── vectorize_faq_data.py
│   │   ├── search_faqs.py
│   │   └── search_properties.py
│   ├── n8n_integration/   # n8n workflow management
│   │   ├── n8n_setup.py
│   │   └── deploy_concierge_workflow.py
│   └── utils/             # Utility functions
│       ├── map_faq_sections.py
│       └── quick_start.py
├── tests/                 # Test files
├── data/                  # Data storage
│   ├── raw/              # Raw scraped data
│   ├── processed/        # Processed data files
│   └── exports/          # Export files
├── docs/                  # Documentation
│   ├── guides/           # User guides
│   └── workflows/        # n8n workflow files
├── config/               # Configuration files
├── scripts/              # Setup and utility scripts
├── main.py               # Main entry point
├── requirements.txt      # Python dependencies
└── Makefile             # Development tasks
```

## 🚀 Quick Start

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

The scraper generates the following files in `data/processed/`:

### 1. `premiere_suites_data.pdf`

**Primary file for vector database ingestion**

- Structured PDF document with property information
- Optimized for text extraction and vector embedding
- Includes summary statistics and detailed property listings
- Suitable for n8n automation workflows

### 2. `premiere_suites_data.json`

- Raw structured data in JSON format
- Complete property information with all extracted fields
- Useful for data analysis and processing

### 3. `premiere_suites_data.csv`

- Tabular data format
- Compatible with spreadsheet applications
- Easy to import into databases

### 4. `premiere_suites_data.md`

- Markdown format for easy reading
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
