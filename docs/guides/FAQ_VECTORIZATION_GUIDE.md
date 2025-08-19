# FAQ Data Vectorization Guide

This guide will walk you through vectorizing your Premiere Suites FAQ data and setting up semantic search.

## 🎯 **Quick Start (3 Steps)**

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Vectorize FAQ Data

```bash
python vectorize_faq_data.py
```

### Step 3: Search FAQ Data

```bash
python search_faqs.py
```

## 📋 **Detailed Steps**

### Prerequisites

1. **Python 3.8+** installed
2. **Qdrant** vector database (local or cloud)
3. **FAQ data file** (`premiere_suites_faq_data.jsonl`)

### Option A: Local Qdrant Setup

1. **Install Qdrant locally** (using Docker):

```bash
docker run -p 6333:6333 qdrant/qdrant
```

2. **Vectorize the data**:

```bash
python vectorize_faq_data.py
```

3. **Search the data**:

```bash
python search_faqs.py
```

### Option B: Qdrant Cloud Setup (Recommended)

1. **Sign up for Qdrant Cloud**:

   - Go to https://cloud.qdrant.io/
   - Create a free account
   - Create a new cluster
   - Get your cluster URL and API key

2. **Create .env file**:

```bash
# Copy the example file
cp env.example .env

# Edit .env with your credentials
nano .env
```

3. **Vectorize with cloud** (automatically detected):

```bash
python vectorize_faq_data.py
```

4. **Search with cloud** (automatically detected):

```bash
python search_faqs.py
```

## 🔧 **Advanced Usage**

### Environment Variables (.env file)

The scripts automatically detect Qdrant Cloud credentials from a `.env` file:

1. **Copy the example file**:

```bash
cp env.example .env
```

2. **Edit .env with your credentials**:

```bash
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key-here
```

3. **Run scripts normally** (they'll auto-detect cloud vs local):

```bash
python vectorize_faq_data.py
python search_faqs.py
```

### Command Line Overrides

You can still override .env settings with command line arguments:

```bash
# Force local usage (ignores .env)
python vectorize_faq_data.py --local

# Force cloud usage with custom credentials
python vectorize_faq_data.py --cloud --url "custom-url" --api-key "custom-key"
```

### Vectorization Options

```bash
# Recreate collection (overwrite existing)
python vectorize_faq_data.py --recreate

# Custom collection name
python vectorize_faq_data.py --collection "my_faqs"

# Cloud with custom collection (using .env file)
python vectorize_faq_data.py --collection "my_faqs" --recreate
```

### Search Options

```bash
# Interactive search
python search_faqs.py

# Single query search
python search_faqs.py --query "How do I book a reservation?"

# Example searches (demonstration)
python search_faqs.py --examples

# Custom number of results
python search_faqs.py --query "pet policy" --limit 10

# Cloud search (using .env file)
python search_faqs.py --query "check-in times"
```

## 📊 **What Gets Vectorized**

The script will vectorize:

- **30 FAQ entries** from your data
- **Text chunks** containing question, answer, category, and tags
- **Metadata** for filtering and display
- **384-dimensional vectors** using the `all-MiniLM-L6-v2` model

## 🔍 **Search Capabilities**

### Semantic Search

- Find relevant FAQs based on meaning, not just keywords
- Understands synonyms and related concepts
- Returns similarity scores

### Filtering

- Filter by category (Guest Services, Reservations, etc.)
- Filter by tags (amenities, booking, payment, etc.)
- Adjust similarity thresholds

### Example Queries

- "How do I book a reservation?"
- "What are the check-in times?"
- "Do you allow pets?"
- "What payment methods do you accept?"
- "Is smoking allowed?"
- "Do you offer housekeeping?"

## 🚀 **Integration with Other Tools**

### n8n Workflow Integration

```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:6333/collections/premiere_suites_faqs/points/search",
        "method": "POST",
        "json": {
          "vector": "{{$json.embedding}}",
          "limit": 5,
          "with_payload": true
        }
      }
    }
  ]
}
```

### API Integration

```python
import requests

# Search FAQs via API
response = requests.post(
    "http://localhost:6333/collections/premiere_suites_faqs/points/search",
    json={
        "vector": embedding_vector,
        "limit": 5,
        "with_payload": True
    }
)
```

## 🛠️ **Troubleshooting**

### Common Issues

1. **"Collection not found"**:

   - Run `vectorize_faq_data.py` first
   - Check if Qdrant is running

2. **"Connection refused"**:

   - Start Qdrant: `docker run -p 6333:6333 qdrant/qdrant`
   - Check if port 6333 is available

3. **"API key invalid"**:

   - Verify your Qdrant Cloud credentials
   - Check environment variables

4. **"No FAQ data found"**:
   - Ensure `premiere_suites_faq_data.jsonl` exists
   - Check file format and content

### Debug Mode

```bash
# Enable debug logging
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from vectorize_faq_data import vectorize_faq_data
vectorize_faq_data()
"
```

## 📈 **Performance**

- **Vectorization**: ~30 seconds for 30 FAQs
- **Search**: <100ms per query
- **Storage**: ~50KB for all vectors
- **Memory**: ~150MB during processing

## 🔄 **Updating Data**

To update FAQ data:

1. **Regenerate FAQ data** (if source changed)
2. **Recreate collection**:

```bash
python vectorize_faq_data.py --recreate
```

## 📞 **Support**

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all dependencies are installed
3. Ensure Qdrant is running and accessible
4. Check FAQ data file format and content

---

**🎉 You're now ready to vectorize and search your FAQ data!**
