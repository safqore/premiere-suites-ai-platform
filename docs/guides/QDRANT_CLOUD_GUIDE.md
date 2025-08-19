# Qdrant Cloud Setup Guide

This guide will help you set up Qdrant Cloud to store and search through your Premiere Suites property data with semantic search capabilities.

## Why Qdrant Cloud?

- **No Infrastructure Management**: No need to run Docker or manage servers
- **Scalability**: Automatically scales with your data
- **High Availability**: Managed service with 99.9% uptime
- **Security**: Enterprise-grade security and compliance
- **Easy Setup**: Simple API-based setup

## Prerequisites

- Python 3.8+
- Qdrant Cloud account (free tier available)
- Your scraped property data in `premiere_suites_data.jsonl`

## Step 1: Create Qdrant Cloud Account

1. **Sign up** at [https://cloud.qdrant.io/](https://cloud.qdrant.io/)
2. **Create a new cluster**:
   - Choose a region close to you
   - Select the free tier (1GB storage, sufficient for your 61 properties)
   - Give your cluster a name (e.g., "premiere-suites")
3. **Get your credentials**:
   - Copy the cluster URL (e.g., `https://your-cluster.qdrant.io`)
   - Copy the API key from the cluster settings

## Step 2: Configure Environment Variables

You have two options to set your Qdrant Cloud credentials:

### Option A: Environment Variables

```bash
export QDRANT_URL="https://your-cluster.qdrant.io"
export QDRANT_API_KEY="your-api-key-here"
```

### Option B: .env File (Recommended)

Create a `.env` file in your project directory:

```bash
# Qdrant Cloud Configuration
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key-here
```

**Security Note**: Add `.env` to your `.gitignore` file to keep your API key secure.

## Step 3: Automated Setup

Run the cloud setup script:

```bash
python cloud_setup.py
```

This script will:

- Check if your credentials are configured
- Install all dependencies
- Test the connection to Qdrant Cloud
- Set up the vector database with your data
- Run a test search

## Step 4: Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Vector Database

```bash
python qdrant_setup.py
```

### 3. Test Search

```bash
python search_properties.py
```

## Usage

### Interactive Search Interface

```bash
python search_properties.py
```

### Programmatic Usage

```python
from qdrant_setup import PremiereSuitesVectorDB
import os

# Initialize with cloud credentials
vdb = PremiereSuitesVectorDB(
    qdrant_url=os.getenv("QDRANT_URL"),
    qdrant_api_key=os.getenv("QDRANT_API_KEY"),
    use_cloud=True
)

# Search for properties
results = vdb.search_properties(
    query="luxury apartment with pool",
    limit=10,
    city="Toronto",
    min_rating=4.0,
    pet_friendly=True
)

# Print results
for result in results:
    print(f"{result['property_name']} - {result['city']} - Rating: {result['rating']}")
```

## Features

### Semantic Search

- Search properties using natural language queries
- Find similar properties based on descriptions and amenities
- Uses sentence transformers for high-quality embeddings

### Advanced Filtering

- Filter by city
- Filter by minimum rating
- Filter by pet-friendly status
- Filter by number of bedrooms
- Combine multiple filters

### Cloud Benefits

- **Automatic Scaling**: Handles traffic spikes automatically
- **Global Distribution**: Low latency from anywhere
- **Backup & Recovery**: Automatic backups and disaster recovery
- **Monitoring**: Built-in monitoring and alerting

## Data Structure

Each property in Qdrant Cloud contains:

- **Vector**: 384-dimensional embedding of the property description
- **Payload**:
  - `property_id`: Unique identifier
  - `property_name`: Name of the property
  - `city`: City location
  - `rating`: Property rating (0-5)
  - `room_type`: Type of room/suite
  - `amenities`: List of available amenities
  - `description`: Property description
  - `pet_friendly`: Boolean for pet policy
  - `bedrooms`: Number of bedrooms
  - `building_type`: Type of building
  - `suite_features`: List of suite features
  - `source_url`: Original property URL
  - `image_url`: Property image URL
  - `text_chunk`: Full text description for embedding
  - `ingested_at`: Timestamp of when data was added

## Example Searches

Try these example searches:

1. **Luxury properties**: "luxury apartment with pool and gym"
2. **Pet-friendly options**: "pet friendly apartment in Toronto"
3. **High-rated properties**: "high rated apartment with terrace"
4. **Specific amenities**: "apartment with in-suite laundry"
5. **Location-specific**: "apartment in Vancouver with ocean view"

## Management

### View Collection Info

```python
info = vdb.get_collection_info()
print(f"Total properties: {info['points_count']}")
print(f"Vector size: {info['config']['vector_size']}")
```

### Recreate Collection

```python
vdb.create_collection(recreate=True)
```

### Monitor Usage

- Check your Qdrant Cloud dashboard for usage metrics
- Monitor API calls and storage usage
- Set up alerts for usage limits

## Cost Considerations

### Free Tier

- **Storage**: 1GB (sufficient for ~100,000 properties)
- **API Calls**: 1,000 requests/day
- **Perfect for development and small projects**

### Paid Plans

- **Starter**: $25/month for 10GB storage and 100K requests/day
- **Professional**: $99/month for 100GB storage and 1M requests/day
- **Enterprise**: Custom pricing for large-scale deployments

## Troubleshooting

### Connection Issues

- Verify your cluster URL and API key
- Check if your cluster is active in the Qdrant Cloud dashboard
- Ensure your IP is not blocked (if using IP restrictions)

### Authentication Errors

- Verify your API key is correct
- Check if your API key has the necessary permissions
- Ensure your cluster is not paused

### Rate Limiting

- Monitor your API usage in the dashboard
- Implement request caching if needed
- Consider upgrading your plan for higher limits

### Data Issues

- Verify your data format in `premiere_suites_data.jsonl`
- Check that all required fields are present
- Ensure text encoding is UTF-8

## Security Best Practices

1. **API Key Management**:

   - Store API keys in environment variables or `.env` files
   - Never commit API keys to version control
   - Rotate API keys regularly

2. **Access Control**:

   - Use IP restrictions if needed
   - Monitor API usage for unusual patterns
   - Set up alerts for security events

3. **Data Privacy**:
   - Ensure your data complies with privacy regulations
   - Consider data retention policies
   - Implement data encryption if required

## Next Steps

1. **Scale Up**: Add more properties to your dataset
2. **Customize Embeddings**: Try different sentence transformer models
3. **Add More Filters**: Extend filtering capabilities
4. **Web Interface**: Create a web-based search interface
5. **Real-time Updates**: Set up automatic data updates
6. **Analytics**: Add search analytics and insights

## Support

- **Qdrant Cloud Documentation**: [https://cloud.qdrant.io/docs/](https://cloud.qdrant.io/docs/)
- **Qdrant Community**: [https://discord.gg/qdrant](https://discord.gg/qdrant)
- **GitHub Issues**: [https://github.com/qdrant/qdrant](https://github.com/qdrant/qdrant)

If you encounter issues:

1. Check the Qdrant Cloud dashboard for cluster status
2. Verify your credentials and network connectivity
3. Review the logs in your application
4. Contact Qdrant support if needed
