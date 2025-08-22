# FAQ to Qdrant n8n Workflow Guide

This guide explains how to use the new n8n workflow that automatically ingests FAQ data into Qdrant vector database, with the ability to delete and recreate collections.

## Overview

The FAQ to Qdrant workflow is designed to:

1. **Read FAQ data** from the processed JSONL file
2. **Delete existing collections** if they exist (ensuring fresh data)
3. **Create new collections** with proper vector configuration
4. **Vectorize FAQ content** using OpenAI embeddings
5. **Upload to Qdrant** with metadata and searchable content
6. **Provide webhook endpoints** for easy triggering

## Prerequisites

Before using this workflow, ensure you have:

### 1. Environment Variables

Add these to your `.env` file:

```bash
# Qdrant Cloud Configuration
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# OpenAI Configuration (for embeddings)
OPENAI_API_KEY=your-openai-api-key

# n8n Configuration
N8N_URL=http://localhost:5678
N8N_API_KEY=your-n8n-api-key
```

### 2. Required Software

- **n8n** running locally or in the cloud
- **Python 3.8+** with required packages
- **FAQ data** in `data/processed/premiere_suites_faq_data.jsonl`

### 3. Dependencies

Install required Python packages:

```bash
pip install requests python-dotenv qdrant-client openai
```

## Workflow Components

### 1. Webhook Trigger

- **Endpoint**: `POST /webhook/faq-to-qdrant`
- **Purpose**: Entry point for triggering the workflow
- **Usage**: Send any POST request to trigger FAQ ingestion

### 2. File Reader

- **File**: `data/processed/premiere_suites_faq_data.jsonl`
- **Purpose**: Reads the processed FAQ data
- **Format**: JSONL with metadata, summary, and FAQ entries

### 3. JSONL Parser

- **Purpose**: Parses the JSONL file and extracts FAQ data
- **Output**: Structured data with metadata, summary, and FAQ array

### 4. Collection Management

- **Check Collection**: Verifies if `faq_collection` exists
- **Delete Collection**: Removes existing collection if found
- **Create Collection**: Creates new collection with proper vector configuration

### 5. Vectorization

- **Model**: OpenAI `text-embedding-3-small` (1536 dimensions)
- **Input**: Question + Answer combined text
- **Output**: Vector embeddings for semantic search

### 6. Qdrant Upload

- **Collection**: `faq_collection`
- **Vector Size**: 1536 dimensions
- **Distance**: Cosine similarity
- **Metadata**: Question, answer, category, tags, source URL

## Setup Instructions

### Step 1: Generate the Workflow

```bash
# Run the workflow generator
python src/n8n_integration/faq_to_qdrant_workflow.py
```

This creates:

- `docs/workflows/faq_to_qdrant_workflow.json` - The n8n workflow
- `src/n8n_integration/deploy_faq_workflow.py` - Deployment script
- `src/n8n_integration/test_faq_workflow.py` - Test script

### Step 2: Deploy to n8n

```bash
# Deploy the workflow to n8n
python src/n8n_integration/deploy_faq_workflow.py
```

### Step 3: Test the Workflow

```bash
# Test the workflow execution
python src/n8n_integration/test_faq_workflow.py
```

## Usage

### Manual Trigger

Send a POST request to the webhook endpoint:

```bash
curl -X POST http://localhost:5678/webhook/faq-to-qdrant \
  -H "Content-Type: application/json" \
  -d '{"trigger": "manual", "timestamp": "2025-01-19T10:00:00Z"}'
```

### Programmatic Trigger

Use the Python test script or integrate with your own automation:

```python
import requests

response = requests.post(
    "http://localhost:5678/webhook/faq-to-qdrant",
    json={"trigger": "automated", "source": "scheduled_job"}
)

if response.status_code == 200:
    print("FAQ ingestion completed successfully!")
    print(response.json())
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### Scheduled Execution

Set up cron jobs or use n8n's built-in scheduler:

```bash
# Example cron job (runs daily at 2 AM)
0 2 * * * curl -X POST http://localhost:5678/webhook/faq-to-qdrant
```

## Workflow Execution Flow

1. **Trigger**: Webhook receives POST request
2. **Read**: Loads FAQ data from JSONL file
3. **Parse**: Extracts metadata, summary, and FAQ entries
4. **Check**: Verifies if `faq_collection` exists in Qdrant
5. **Delete**: Removes existing collection (if found)
6. **Create**: Creates new collection with vector configuration
7. **Vectorize**: Generates embeddings for each FAQ
8. **Upload**: Sends vectorized data to Qdrant
9. **Response**: Returns success/error status

## Expected Output

### Success Response

```json
{
  "status": "success",
  "message": "FAQ data ingested successfully",
  "collection": "faq_collection",
  "total_faqs": 30,
  "vector_size": 1536,
  "timestamp": "2025-01-19T10:00:00Z"
}
```

### Error Response

```json
{
  "error": "Failed to create collection",
  "details": "Collection already exists",
  "timestamp": "2025-01-19T10:00:00Z"
}
```

## Qdrant Collection Structure

### Collection Name

- `faq_collection`

### Vector Configuration

- **Size**: 1536 dimensions
- **Distance**: Cosine similarity
- **Model**: OpenAI text-embedding-3-small

### Payload Fields

```json
{
  "question": "Why choose Premiere Suites?",
  "answer": "As Canada's largest and most trusted provider...",
  "category": "About Us",
  "tags": ["furnished", "rent"],
  "source_url": "https://premieresuites.com/faq/",
  "text_chunk": "FAQ 1: Why choose Premiere Suites? | Category: About Us | ...",
  "timestamp": "2025-01-19T10:00:00Z"
}
```

## Troubleshooting

### Common Issues

#### 1. Collection Already Exists

**Error**: `Collection already exists`
**Solution**: The workflow automatically handles this by deleting and recreating the collection.

#### 2. OpenAI API Rate Limits

**Error**: `Rate limit exceeded`
**Solution**: Add delays between embedding requests or upgrade your OpenAI plan.

#### 3. Qdrant Connection Issues

**Error**: `Connection refused`
**Solution**: Verify Qdrant URL and API key in your `.env` file.

#### 4. File Not Found

**Error**: `FAQ data file not found`
**Solution**: Ensure `data/processed/premiere_suites_faq_data.jsonl` exists.

### Debug Mode

Enable debug logging in n8n:

1. Go to n8n settings
2. Enable "Debug mode"
3. Check execution logs for detailed information

### Manual Verification

Test Qdrant collection manually:

```python
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv

load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# Check collection info
collection_info = client.get_collection("faq_collection")
print(f"Collection: {collection_info}")

# Search for FAQs
search_result = client.search(
    collection_name="faq_collection",
    query_vector=[0.1] * 1536,  # Dummy vector
    limit=5
)
print(f"Found {len(search_result)} FAQs")
```

## Integration Examples

### 1. CI/CD Pipeline

Add to your deployment pipeline:

```yaml
# .github/workflows/deploy.yml
- name: Deploy FAQ to Qdrant
  run: |
    curl -X POST ${{ secrets.N8N_URL }}/webhook/faq-to-qdrant \
      -H "Content-Type: application/json" \
      -d '{"deployment": "ci_cd"}'
```

### 2. Monitoring Integration

Monitor workflow execution:

```python
import requests
import time

def monitor_faq_ingestion():
    start_time = time.time()

    response = requests.post(
        "http://localhost:5678/webhook/faq-to-qdrant",
        json={"monitoring": True}
    )

    execution_time = time.time() - start_time

    if response.status_code == 200:
        print(f"✅ FAQ ingestion completed in {execution_time:.2f}s")
    else:
        print(f"❌ FAQ ingestion failed after {execution_time:.2f}s")
```

### 3. Slack Notifications

Add Slack integration to n8n for notifications:

```json
{
  "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
  "message": "FAQ data has been successfully ingested to Qdrant! 📚"
}
```

## Performance Considerations

### Batch Processing

For large FAQ datasets:

- Consider processing in batches
- Add delays between API calls
- Monitor rate limits

### Memory Usage

- FAQ data is loaded entirely into memory
- Consider streaming for very large files
- Monitor n8n memory usage

### Network Latency

- Qdrant Cloud operations may have latency
- OpenAI API calls add network overhead
- Consider timeouts for production use

## Security Best Practices

### API Keys

- Store API keys in environment variables
- Never commit keys to version control
- Rotate keys regularly

### Access Control

- Restrict webhook access to trusted sources
- Use authentication for webhook endpoints
- Monitor webhook usage

### Data Privacy

- FAQ data may contain sensitive information
- Ensure compliance with data protection regulations
- Log access to FAQ data

## Maintenance

### Regular Updates

- Update FAQ data regularly
- Monitor collection performance
- Review and optimize embeddings

### Backup Strategy

- Backup Qdrant collections
- Keep FAQ data backups
- Document workflow changes

### Monitoring

- Monitor workflow execution times
- Track error rates
- Alert on failures

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review n8n execution logs
3. Verify environment configuration
4. Test with the provided test scripts

## Related Documentation

- [Qdrant Setup Guide](../guides/QDRANT_SETUP_GUIDE.md)
- [n8n Integration Guide](../guides/N8N_INTEGRATION_GUIDE.md)
- [FAQ Vectorization Guide](../guides/FAQ_VECTORIZATION_GUIDE.md)
- [Vector Database Guide](../guides/VECTOR_DB_GUIDE.md)


