# Vector Database Integration Guide

## 🎯 **RECOMMENDED FORMATS FOR VECTOR DATABASES**

### 1. **JSON Lines (.jsonl) - BEST CHOICE** ⭐⭐⭐

**Why it's optimal:**

- Each line is a separate JSON object (perfect for chunking)
- Maintains structured data while being easy to process
- Most vector databases have native JSON support
- Easy to filter and query specific fields
- Better than PDF for text extraction

**Example structure:**

```json
{"type": "metadata", "generated_on": "2024-01-15T10:30:00", "total_properties": 50}
{"type": "summary", "cities_covered": 25, "average_rating": 4.2}
{"type": "property", "id": "WETMORE", "property_name": "The Wetmore House", "city": "Fredericton", "text_chunk": "Property 1: The Wetmore House | Location: Fredericton | Rating: 4.6/5.0 | Room Type: Living Room | Pet Friendly: Yes | Amenities: Gym, Laundry, Parking"}
```

### 2. **Chunked Text (.txt) - EXCELLENT** ⭐⭐

**Why it's great:**

- Pre-chunked for optimal embedding
- No formatting overhead
- Easy to process line-by-line
- Smaller file sizes
- Perfect for semantic search

**Example structure:**

```
--- CHUNK 1 ---
Property 1: The Wetmore House | Location: Fredericton | Rating: 4.6/5.0 | Room Type: Living Room | Pet Friendly: Yes | Amenities: Gym, Laundry, Parking

Property 2: The Lofts on Bannatyne | Location: Winnipeg | Rating: 5.0/5.0 | Room Type: Living Room | Pet Friendly: No | Amenities: Pool, WiFi, Furnished

--- CHUNK 2 ---
Property 3: Circa II | Location: Markham | Rating: 3.9/5.0 | Room Type: Living Room | Pet Friendly: Yes | Amenities: Gym, Parking
```

### 3. **Plain Text (.txt) - GOOD** ⭐

**Why it works well:**

- Simple text processing
- Easy to chunk and embed
- No complex formatting
- Works with any text processing pipeline

## 🚀 **n8n Integration Workflows**

### Workflow 1: JSON Lines Processing (Recommended)

```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.readTextFile",
      "parameters": {
        "filePath": "premiere_suites_data.jsonl"
      }
    },
    {
      "type": "n8n-nodes-base.splitInBatches",
      "parameters": {
        "batchSize": 1
      }
    },
    {
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "// Parse JSON line\nconst data = JSON.parse($input.first().json);\n\n// Only process property entries\nif (data.type === 'property') {\n  return {\n    json: {\n      id: data.id,\n      text: data.text_chunk,\n      metadata: {\n        property_name: data.property_name,\n        city: data.city,\n        rating: data.rating,\n        amenities: data.amenities,\n        pet_friendly: data.pet_friendly\n      }\n    }\n  };\n}\nreturn null;"
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "your-embedding-api-endpoint",
        "method": "POST",
        "json": "{\n  \"text\": \"{{$json.text}}\",\n  \"metadata\": \"{{$json.metadata}}\"\n}"
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "your-vector-db-endpoint",
        "method": "POST",
        "json": "{\n  \"vector\": \"{{$json.embedding}}\",\n  \"metadata\": \"{{$json.metadata}}\",\n  \"id\": \"{{$json.id}}\"\n}"
      }
    }
  ]
}
```

### Workflow 2: Chunked Text Processing

```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.readTextFile",
      "parameters": {
        "filePath": "premiere_suites_chunks.txt"
      }
    },
    {
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "// Split by chunks\nconst text = $input.first().json;\nconst chunks = text.split('--- CHUNK').filter(chunk => chunk.trim());\n\nreturn chunks.map((chunk, index) => {\n  const lines = chunk.split('\\n').filter(line => line.trim());\n  const chunkNumber = lines[0].replace(/[^0-9]/g, '');\n  const content = lines.slice(1).join(' ').trim();\n  \n  return {\n    json: {\n      id: `chunk_${chunkNumber}`,\n      text: content,\n      chunk_number: parseInt(chunkNumber)\n    }\n  };\n});"
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "your-embedding-api-endpoint",
        "method": "POST",
        "json": "{\n  \"text\": \"{{$json.text}}\"\n}"
      }
    }
  ]
}
```

### Workflow 3: PDF Processing (Alternative)

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
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "// Clean and process text\nconst text = $input.first().json.text;\nconst cleanedText = text.replace(/\\s+/g, ' ').trim();\n\nreturn {\n  json: {\n    text: cleanedText,\n    length: cleanedText.length\n  }\n};"
      }
    }
  ]
}
```

## 🔧 **Vector Database Setup Examples**

### Pinecone Integration

```python
import pinecone
from openai import OpenAI

# Initialize Pinecone
pinecone.init(api_key="your-api-key", environment="your-environment")
index = pinecone.Index("premiere-suites")

# Process JSON Lines
with open("premiere_suites_data.jsonl", "r") as f:
    for line in f:
        data = json.loads(line)
        if data["type"] == "property":
            # Generate embedding
            client = OpenAI(api_key="your-openai-key")
            response = client.embeddings.create(
                input=data["text_chunk"],
                model="text-embedding-ada-002"
            )

            # Upsert to Pinecone
            index.upsert(
                vectors=[{
                    "id": data["id"],
                    "values": response.data[0].embedding,
                    "metadata": {
                        "property_name": data["property_name"],
                        "city": data["city"],
                        "rating": data["rating"]
                    }
                }]
            )
```

### Weaviate Integration

```python
import weaviate
from weaviate.classes.init import Auth

# Initialize Weaviate
client = weaviate.connect_to_wcs(
    cluster_url="your-cluster-url",
    auth_credentials=Auth.api_key("your-api-key")
)

# Create schema
client.collections.create(
    name="PremiereSuites",
    properties=[
        {"name": "property_name", "dataType": ["text"]},
        {"name": "city", "dataType": ["text"]},
        {"name": "rating", "dataType": ["number"]},
        {"name": "amenities", "dataType": ["text[]"]}
    ],
    vectorizer_config=weaviate.classes.config.Configure.Vectorizer.text2vec_openai()
)

# Process data
collection = client.collections.get("PremiereSuites")
with open("premiere_suites_data.jsonl", "r") as f:
    for line in f:
        data = json.loads(line)
        if data["type"] == "property":
            collection.data.insert({
                "property_name": data["property_name"],
                "city": data["city"],
                "rating": data["rating"],
                "amenities": data["amenities"]
            })
```

## 📊 **Performance Comparison**

| Format       | Processing Speed | Storage Efficiency | Query Performance | Ease of Use |
| ------------ | ---------------- | ------------------ | ----------------- | ----------- |
| JSON Lines   | ⭐⭐⭐⭐⭐       | ⭐⭐⭐⭐           | ⭐⭐⭐⭐⭐        | ⭐⭐⭐⭐⭐  |
| Chunked Text | ⭐⭐⭐⭐         | ⭐⭐⭐⭐⭐         | ⭐⭐⭐⭐          | ⭐⭐⭐⭐    |
| Plain Text   | ⭐⭐⭐⭐         | ⭐⭐⭐⭐⭐         | ⭐⭐⭐            | ⭐⭐⭐⭐⭐  |
| PDF          | ⭐⭐             | ⭐⭐               | ⭐⭐              | ⭐⭐        |

## 🎯 **Recommendations**

### For n8n Workflows:

1. **Use JSON Lines (.jsonl)** - Best structured data with easy processing
2. **Use Chunked Text (.txt)** - Pre-optimized for embedding
3. **Avoid PDF** - More complex processing, potential text extraction issues

### For Direct API Integration:

1. **JSON Lines** - Native support in most vector databases
2. **Structured JSON** - Easy to filter and query
3. **Plain Text** - Simple and reliable

### For Maximum Performance:

1. **Pre-chunked data** - Reduces processing overhead
2. **Structured metadata** - Enables advanced filtering
3. **Optimized text chunks** - Better embedding quality

## 🔄 **Automation Tips**

1. **Schedule regular updates** - Run scraper weekly/monthly
2. **Incremental updates** - Only process new properties
3. **Version control** - Keep track of data changes
4. **Backup strategies** - Store multiple format versions
5. **Monitoring** - Track embedding quality and performance

This guide provides the optimal approach for integrating Premiere Suites data into your vector database workflow!
