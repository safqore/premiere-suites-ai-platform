# Premiere Suites Web Scraper

A comprehensive web scraper for extracting property data from [Premiere Suites](https://premieresuites.com/find-your-match/) and generating structured documents for vector database ingestion.

## Features

- **Multi-format Output**: Generates JSON, CSV, PDF, and Markdown files
- **Comprehensive Data Extraction**: Extracts property names, cities, ratings, amenities, descriptions, and more
- **PDF Generation**: Creates structured PDF documents optimized for vector database ingestion
- **Dual Scraping Methods**: Uses both requests and Selenium for maximum data extraction
- **Error Handling**: Robust error handling and logging
- **Deduplication**: Automatically removes duplicate properties

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd premiere_suites_scraper
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Chrome/Chromium** (for Selenium):
   - macOS: `brew install --cask google-chrome`
   - Ubuntu: `sudo apt-get install chromium-browser`
   - Windows: Download from [Chrome website](https://www.google.com/chrome/)

## Usage

### Basic Usage

Run the main scraper:
```bash
python premiere_scraper.py
```

This will:
- Scrape the Premiere Suites website
- Generate multiple output files
- Display summary statistics

### Test the Scraper

Run the test script to verify functionality:
```bash
python test_scraper.py
```

### Programmatic Usage

```python
from premiere_scraper import PremiereSuitesScraper

# Initialize scraper
scraper = PremiereSuitesScraper(headless=True)

# Scrape data
properties = scraper.scrape_all()

# Generate PDF for vector database
scraper.generate_pdf(properties, "premiere_suites_data.pdf")

# Generate other formats
scraper.save_to_json(properties, "data.json")
scraper.save_to_csv(properties, "data.csv")
scraper.generate_markdown(properties, "data.md")
```

## Output Files

The scraper generates the following files:

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

## Data Structure

Each property contains the following information:

```python
@dataclass
class PropertyData:
    property_name: str          # Building/property name
    city: str                   # City location
    rating: Optional[float]     # Rating (0.0-5.0)
    room_type: str              # Type of room/suite
    amenities: List[str]        # Available amenities
    description: str            # Property description
    url: str                    # Source URL
    image_url: Optional[str]    # Property image URL
    price_range: Optional[str]  # Price information
    pet_friendly: bool          # Pet policy
    bedrooms: Optional[int]     # Number of bedrooms
    location_details: Optional[str]  # Additional location info
    property_id: Optional[str]  # Unique property identifier
    building_type: Optional[str] # Type of building
    suite_features: List[str]   # Suite-specific features
```

## Vector Database Integration

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
        "filePath": "premiere_suites_data.pdf"
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

## Configuration

### Scraper Options

```python
# Initialize with visible browser (for debugging)
scraper = PremiereSuitesScraper(headless=False)

# Custom file names
scraper.generate_pdf(properties, "custom_filename.pdf")
```

### Environment Variables

Create a `.env` file for custom configurations:
```env
HEADLESS_MODE=true
REQUEST_TIMEOUT=30
SCROLL_PAUSE=2
```

## Troubleshooting

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

### Debug Mode

Run with visible browser for debugging:
```python
scraper = PremiereSuitesScraper(headless=False)
```

## Legal and Ethical Considerations

- **Respect robots.txt**: Check the website's robots.txt file
- **Rate limiting**: The scraper includes delays to avoid overwhelming the server
- **Terms of Service**: Ensure compliance with Premiere Suites' terms of service
- **Data usage**: Use extracted data responsibly and in accordance with applicable laws

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational and research purposes. Please ensure compliance with applicable laws and website terms of service.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Open an issue with detailed information about the problem

## Changelog

### v1.0.0
- Initial release
- PDF generation for vector database ingestion
- Multi-format output support
- Comprehensive property data extraction
