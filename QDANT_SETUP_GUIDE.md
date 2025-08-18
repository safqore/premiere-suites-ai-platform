# Qdrant Vector Database Setup Guide

This guide will help you set up a Qdrant vector database to store and search through your Premiere Suites property data with semantic search capabilities.

## Prerequisites

- Python 3.8+
- Docker and Docker Compose (for running Qdrant)
- Your scraped property data in `premiere_suites_data.jsonl`

## Installation

### 1. Install Dependencies

First, install the required Python packages:

```bash
pip install -r requirements.txt
```

### 2. Start Qdrant Database

Use Docker Compose to start Qdrant:

```bash
docker-compose up -d
```

This will start Qdrant on:

- REST API: http://localhost:6333
- gRPC API: localhost:6334

You can verify Qdrant is running by visiting: http://localhost:6333/health

### 3. Set Up the Vector Database

Run the setup script to create the collection and populate it with your data:

```bash
python qdrant_setup.py
```

This script will:

- Create a Qdrant collection optimized for your data
- Generate embeddings for all property descriptions
- Insert all properties into the vector database
- Create indexes for efficient filtering
- Run a test search to verify everything works

## Usage

### Interactive Search Interface

Run the interactive search interface:

```bash
python search_properties.py
```

This provides:

- Semantic search by description
- Filtering by city, rating, pet-friendly status, and bedrooms
- Collection information display
- Example searches to demonstrate functionality

### Programmatic Usage

You can also use the vector database programmatically:

```python
from qdrant_setup import PremiereSuitesVectorDB

# Initialize the database
vdb = PremiereSuitesVectorDB()

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

### Performance Optimizations

- Vectors stored on disk for large datasets
- Memory mapping for collections > 10k points
- Indexed payload fields for fast filtering
- Batch insertion for efficient data loading

## Data Structure

Each property in the vector database contains:

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

Here are some example searches you can try:

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

To recreate the collection (useful for updates):

```python
vdb.create_collection(recreate=True)
```

### Stop Qdrant

```bash
docker-compose down
```

To also remove the data volume:

```bash
docker-compose down -v
```

## Troubleshooting

### Qdrant Connection Issues

- Ensure Docker is running
- Check if ports 6333 and 6334 are available
- Verify Qdrant container is healthy: `docker-compose ps`

### Memory Issues

- The setup uses disk storage for vectors to handle large datasets
- If you have memory constraints, the embeddings are generated in batches

### Search Quality

- The embedding model (`all-MiniLM-L6-v2`) is optimized for semantic similarity
- For better results, try different query formulations
- Use filters to narrow down results

### Data Updates

- To update the database with new data, run `qdrant_setup.py` again
- The script will recreate the collection by default
- For incremental updates, modify the script to use `recreate=False`

## Performance Considerations

- **Embedding Generation**: Takes time for large datasets (61 properties should be fast)
- **Search Speed**: Very fast with indexed filters
- **Storage**: Vectors stored on disk, metadata in memory
- **Scalability**: Can handle millions of properties with proper configuration

## Next Steps

1. **Customize Embeddings**: Try different sentence transformer models
2. **Add More Filters**: Extend filtering capabilities
3. **Web Interface**: Create a web-based search interface
4. **Real-time Updates**: Set up automatic data updates
5. **Analytics**: Add search analytics and insights

## Support

If you encounter issues:

1. Check the logs: `docker-compose logs qdrant`
2. Verify your data format in `premiere_suites_data.jsonl`
3. Ensure all dependencies are installed correctly
4. Check that Qdrant is accessible at http://localhost:6333
