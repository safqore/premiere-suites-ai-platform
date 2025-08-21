# Vectorization Properties Guide

This guide explains how the FAQ vectorization process ensures that the required properties are properly set when storing data in Qdrant.

## Required Properties

When vectorizing FAQ data into Qdrant, the system now ensures these properties are always present:

### 1. `pageContent`

- **Purpose**: The main text content for embedding and retrieval
- **Format**: String containing the FAQ question and answer
- **Fallback**: If empty, uses `"Q: {question}\nA: {answer}"` format
- **Example**: `"Q: How do I book a reservation?\nA: You can book online through our website or call us directly."`

### 2. `metadata`

- **Purpose**: Structured data about the FAQ entry
- **Format**: Object containing all FAQ properties
- **Content**: Always includes `faq_id`, `question`, `answer`, `category`, `tags`, `source_url`, `text_chunk`, and `ingested_at`
- **Example**:

```json
{
  "faq_id": 15,
  "question": "How do I book a reservation?",
  "answer": "You can book online through our website or call us directly.",
  "category": "Booking",
  "tags": ["reservation", "booking"],
  "source_url": "https://example.com/booking",
  "text_chunk": "Q: How do I book a reservation?\nA: You can book online through our website or call us directly.",
  "ingested_at": "2024-01-15T10:30:00"
}
```

### 3. `id`

- **Purpose**: Unique identifier for the FAQ entry
- **Format**: Integer or string
- **Source**: Uses the FAQ's original ID if available, otherwise generates a fallback ID
- **Example**: `15`

## Implementation Details

### LangChain Integration

The `LangChainFAQIntegration` class ensures properties are set correctly:

```python
# In load_faq_documents_from_jsonl method
faq_id = data.get("id")
if faq_id is None:
    faq_id = line_num  # Fallback to line number

# Ensure pageContent is not empty
if not content.strip():
    content = f"FAQ ID: {faq_id}"

# Create metadata object
metadata = {
    "faq_id": faq_id,
    "question": data.get("question", ""),
    "answer": data.get("answer", ""),
    # ... other fields
}

doc = Document(
    page_content=content,
    metadata=metadata
)
```

### Direct Qdrant Vectorization

The `prepare_faq_points` function ensures properties are set correctly:

```python
# Ensure we have a proper ID
faq_id = faq.get("id")
if faq_id is None:
    faq_id = i + 1

# Ensure we have content for pageContent
page_content = faq.get("text_chunk", "")
if not page_content.strip():
    page_content = f"Q: {faq.get('question', '')}\nA: {faq.get('answer', '')}"

# Create metadata object
metadata = {
    "faq_id": faq_id,
    "question": faq.get("question", ""),
    # ... other fields
}

point = PointStruct(
    id=faq_id,
    vector=embeddings[i].tolist(),
    payload={
        "pageContent": page_content,
        "metadata": metadata,
        "id": faq_id,
        # ... other fields for backward compatibility
    }
)
```

## Testing

Run the test script to verify properties are correctly set:

```bash
python test_vectorization_properties.py
```

This test script:

1. Creates test FAQ data with various scenarios (missing IDs, empty content)
2. Tests both LangChain and direct Qdrant vectorization
3. Verifies that all required properties are present
4. Ensures no empty values are stored

## Usage Examples

### Using LangChain Integration

```python
from src.vector_db.langchain_faq_integration import LangChainFAQIntegration

# Initialize integration
integration = LangChainFAQIntegration(
    collection_name="premiere_suites_faqs",
    use_cloud=False
)

# Load and vectorize FAQ data
documents = integration.load_faq_documents_from_jsonl("premiere_suites_faq_data.jsonl")
integration.add_faq_documents(documents)
```

### Using Direct Qdrant Vectorization

```python
from src.vector_db.vectorize_faq_data import vectorize_faq_data

# Vectorize FAQ data
vectorize_faq_data(
    collection_name="premiere_suites_faqs",
    recreate_collection=True
)
```

## Verification

To verify that properties are correctly set in your Qdrant collection:

```python
from qdrant_client import QdrantClient

client = QdrantClient("localhost", port=6333)
points = client.scroll(
    collection_name="premiere_suites_faqs",
    limit=5,
    with_payload=True
)[0]

for point in points:
    print(f"ID: {point.id}")
    print(f"pageContent: {point.payload.get('pageContent', 'NOT FOUND')}")
    print(f"metadata: {point.payload.get('metadata', 'NOT FOUND')}")
    print(f"payload_id: {point.payload.get('id', 'NOT FOUND')}")
    print("---")
```

## Benefits

1. **Consistency**: All FAQ entries have the same structure
2. **Reliability**: No empty or missing properties
3. **Compatibility**: Works with both LangChain and direct Qdrant operations
4. **Fallbacks**: Handles edge cases gracefully
5. **Backward Compatibility**: Maintains existing field structure

## Troubleshooting

If you encounter issues with missing properties:

1. **Check your FAQ data**: Ensure your JSONL file has the required fields
2. **Run the test script**: Verify the vectorization process works correctly
3. **Check Qdrant logs**: Look for any errors during insertion
4. **Verify collection**: Use the verification code above to check stored data

## Migration

If you have existing collections without these properties:

1. Delete the existing collection
2. Re-run the vectorization process
3. The new data will have all required properties

```bash
# Recreate collection with proper properties
python vectorize_faq_data.py --recreate
```
