# LangChain Qdrant Integration Guide

This guide explains how to use LangChain with Qdrant for the Premiere Suites project, providing both direct Qdrant operations and LangChain's higher-level abstractions.

## Overview

The LangChain integration provides:
- **Direct Qdrant Access**: Full control over Qdrant operations
- **LangChain Abstractions**: Higher-level APIs for easier development
- **Document Processing**: Built-in text splitting and document handling
- **Advanced Filtering**: Rich filtering capabilities
- **Consistent API**: Same interface across different vector stores

## Quick Start

### 1. Basic Setup

```python
from src.vector_db.langchain_qdrant_integration import LangChainQdrantIntegration

# Initialize with local Qdrant
integration = LangChainQdrantIntegration(
    collection_name="premiere_suites_properties"
)

# Or with Qdrant Cloud
integration = LangChainQdrantIntegration(
    collection_name="premiere_suites_properties",
    use_cloud=True,
    qdrant_url="https://your-cluster.qdrant.io",
    qdrant_api_key="your-api-key"
)
```

### 2. Create Collection

```python
# Create new collection
integration.create_collection()

# Recreate existing collection
integration.create_collection(recreate=True)
```

### 3. Add Data

```python
# Add texts with metadata
texts = [
    "Luxury apartment with pool and gym",
    "Pet-friendly studio apartment",
    "Family apartment with playground"
]

metadata = [
    {"city": "Toronto", "rating": 4.5, "pet_friendly": True},
    {"city": "Vancouver", "rating": 4.2, "pet_friendly": True},
    {"city": "Montreal", "rating": 4.0, "pet_friendly": True}
]

integration.add_texts(texts, metadatas=metadata)
```

### 4. Search

```python
# Basic similarity search
results = integration.similarity_search(
    query="luxury apartment with amenities",
    k=5
)

# Search with scores
results_with_scores = integration.similarity_search_with_score(
    query="pet friendly apartment",
    k=3
)

# Search with filters
filtered_results = integration.similarity_search(
    query="apartment in Toronto",
    k=5,
    filter={
        "city": "Toronto",
        "rating": {"$gte": 4.0},
        "pet_friendly": True
    }
)
```

## Advanced Usage

### Document Processing

```python
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Create documents
documents = [
    Document(
        page_content="Luxury penthouse with panoramic city views...",
        metadata={
            "property_type": "penthouse",
            "city": "Toronto",
            "rating": 4.9,
            "amenities": ["concierge", "terrace", "kitchen"]
        }
    )
]

# Add documents
integration.add_documents(documents)

# Text splitting for large documents
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

split_docs = text_splitter.split_documents(documents)
integration.add_documents(split_docs)
```

### Loading from JSONL

```python
# Load existing data from JSONL file
documents = integration.load_documents_from_jsonl("premiere_suites_data.jsonl")
integration.add_documents(documents)
```

### Advanced Filtering

```python
# Complex filters
results = integration.similarity_search(
    query="family apartment",
    k=10,
    filter={
        "city": "Toronto",
        "rating": {"$gte": 4.0},
        "pet_friendly": True,
        "bedrooms": {"$gte": 2},
        "amenities": {"$contains": "playground"}
    }
)
```

### Property-Specific Search

```python
# Use the property-specific search interface
results = integration.search_properties_langchain(
    query="luxury apartment with pool",
    limit=5,
    city="Toronto",
    min_rating=4.5,
    pet_friendly=True,
    bedrooms=2
)

for result in results:
    print(f"{result['property_name']} - {result['city']} - Rating: {result['rating']}")
```

## Comparison: Direct Qdrant vs LangChain

### Direct Qdrant Approach

```python
from src.vector_db.qdrant_setup import PremiereSuitesVectorDB

# Initialize
vdb = PremiereSuitesVectorDB()

# Create collection
vdb.create_collection()

# Add data
properties = vdb.load_data_from_jsonl("data.jsonl")
points = vdb.prepare_points(properties)
vdb.insert_data(points)

# Search
results = vdb.search_properties(
    query="luxury apartment",
    limit=10,
    city="Toronto",
    min_rating=4.0
)
```

### LangChain Approach

```python
from src.vector_db.langchain_qdrant_integration import LangChainQdrantIntegration

# Initialize
integration = LangChainQdrantIntegration()

# Create collection
integration.create_collection()

# Add data
documents = integration.load_documents_from_jsonl("data.jsonl")
integration.add_documents(documents)

# Search
results = integration.similarity_search(
    query="luxury apartment",
    k=10,
    filter={"city": "Toronto", "rating": {"$gte": 4.0}}
)
```

## Benefits of LangChain Integration

### 1. **Higher-Level Abstractions**

```python
# LangChain provides Document objects
from langchain.schema import Document

doc = Document(
    page_content="Property description...",
    metadata={"city": "Toronto", "rating": 4.5}
)

# Easy document processing
integration.add_documents([doc])
```

### 2. **Built-in Text Splitting**

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

# Automatically split large documents
split_docs = splitter.split_documents(documents)
integration.add_documents(split_docs)
```

### 3. **Consistent API**

```python
# Same interface across different vector stores
from langchain.vectorstores import Qdrant, Pinecone, Weaviate

# Easy to switch between vector stores
qdrant_store = Qdrant(...)
pinecone_store = Pinecone(...)

# Same methods
qdrant_store.similarity_search(query, k=5)
pinecone_store.similarity_search(query, k=5)
```

### 4. **Advanced Filtering**

```python
# Rich filtering capabilities
filter_dict = {
    "city": "Toronto",
    "rating": {"$gte": 4.0, "$lte": 5.0},
    "pet_friendly": True,
    "amenities": {"$contains": "pool"},
    "bedrooms": {"$gte": 2}
}

results = integration.similarity_search(
    query="luxury apartment",
    k=10,
    filter=filter_dict
)
```

## Environment Configuration

### Local Development

```bash
# Set environment variables
export QDRANT_HOST=localhost
export QDRANT_PORT=6333
export EMBEDDING_MODEL=all-MiniLM-L6-v2

# Or use .env file
echo "QDRANT_HOST=localhost" > .env
echo "QDRANT_PORT=6333" >> .env
echo "EMBEDDING_MODEL=all-MiniLM-L6-v2" >> .env
```

### Qdrant Cloud

```bash
# Set cloud credentials
export QDRANT_URL=https://your-cluster.qdrant.io
export QDRANT_API_KEY=your-api-key
export EMBEDDING_MODEL=text-embedding-3-small

# Or use .env file
echo "QDRANT_URL=https://your-cluster.qdrant.io" > .env
echo "QDRANT_API_KEY=your-api-key" >> .env
echo "EMBEDDING_MODEL=text-embedding-3-small" >> .env
```

### OpenAI Embeddings

```bash
# For OpenAI embeddings
export OPENAI_API_KEY=your-openai-key
export EMBEDDING_MODEL=text-embedding-3-small
```

## Example Workflows

### 1. **Property Search Application**

```python
def search_properties(query, filters=None):
    """Search properties with natural language queries."""
    integration = LangChainQdrantIntegration()
    
    # Convert filters to LangChain format
    langchain_filter = convert_filters(filters) if filters else None
    
    # Perform search
    results = integration.similarity_search(
        query=query,
        k=10,
        filter=langchain_filter
    )
    
    return format_results(results)

def convert_filters(filters):
    """Convert application filters to LangChain format."""
    langchain_filter = {}
    
    if filters.get('city'):
        langchain_filter['city'] = filters['city']
    
    if filters.get('min_rating'):
        langchain_filter['rating'] = {'$gte': filters['min_rating']}
    
    if filters.get('pet_friendly') is not None:
        langchain_filter['pet_friendly'] = filters['pet_friendly']
    
    return langchain_filter
```

### 2. **Document Processing Pipeline**

```python
def process_property_documents(documents):
    """Process property documents with text splitting."""
    integration = LangChainQdrantIntegration()
    
    # Create text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    # Split documents
    split_docs = text_splitter.split_documents(documents)
    
    # Add to vector store
    integration.add_documents(split_docs)
    
    return len(split_docs)
```

### 3. **Real-time Search API**

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
integration = LangChainQdrantIntegration()

@app.route('/search', methods=['POST'])
def search_properties():
    data = request.json
    query = data.get('query')
    filters = data.get('filters', {})
    limit = data.get('limit', 10)
    
    try:
        results = integration.search_properties_langchain(
            query=query,
            limit=limit,
            **filters
        )
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
```

## Performance Optimization

### 1. **Batch Processing**

```python
# Process documents in batches
def add_documents_batched(documents, batch_size=100):
    integration = LangChainQdrantIntegration()
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        integration.add_documents(batch)
        print(f"Processed batch {i//batch_size + 1}")
```

### 2. **Indexing Strategy**

```python
# Create optimized collection
integration.create_collection()

# Add payload indexes for filtering
integration.vdb._create_indexes()
```

### 3. **Embedding Caching**

```python
# Cache embeddings for repeated queries
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_embedding(text):
    return integration.embeddings.embed_query(text)
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Install missing dependencies
   pip install langchain langchain-community qdrant-client
   ```

2. **Connection Issues**
   ```python
   # Check Qdrant connection
   try:
       collections = integration.vdb.client.get_collections()
       print("Connected successfully")
   except Exception as e:
       print(f"Connection failed: {e}")
   ```

3. **Filter Format Issues**
   ```python
   # Use correct filter format
   filter_dict = {
       "city": "Toronto",  # Exact match
       "rating": {"$gte": 4.0},  # Range query
       "amenities": {"$contains": "pool"}  # Contains query
   }
   ```

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Initialize with debug info
integration = LangChainQdrantIntegration()
integration.vdb.client.get_collections()  # Test connection
```

## Best Practices

1. **Use Appropriate Chunk Sizes**
   - Small chunks (500-1000 chars) for precise search
   - Larger chunks (1000-2000 chars) for context

2. **Optimize Metadata**
   - Include all searchable fields in metadata
   - Use consistent data types
   - Index frequently filtered fields

3. **Monitor Performance**
   - Track search response times
   - Monitor collection size
   - Check embedding generation speed

4. **Error Handling**
   - Always wrap operations in try-catch blocks
   - Implement retry logic for network operations
   - Log errors for debugging

## Next Steps

1. **Explore LangChain Components**
   - [LangChain Documentation](https://python.langchain.com/)
   - [Vector Store Integrations](https://python.langchain.com/docs/modules/data_connection/vectorstores/)
   - [Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/)

2. **Advanced Features**
   - Implement hybrid search (semantic + keyword)
   - Add document retrieval chains
   - Integrate with LLMs for question answering

3. **Production Deployment**
   - Set up monitoring and alerting
   - Implement caching strategies
   - Optimize for high-traffic scenarios

## Support

- **LangChain Documentation**: [https://python.langchain.com/](https://python.langchain.com/)
- **Qdrant Documentation**: [https://qdrant.tech/documentation/](https://qdrant.tech/documentation/)
- **Project Issues**: Check the project's GitHub repository

For specific issues with the integration, check the logs and ensure all dependencies are properly installed.


