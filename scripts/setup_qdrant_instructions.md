# Qdrant Setup Instructions

This guide explains how to set up Qdrant for the Premiere Suites scraper project.

## Option 1: Local Qdrant (Recommended for Development)

### Prerequisites

- Docker Desktop installed and running
- Docker Compose available

### Steps

1. **Start Docker Desktop**

   ```bash
   # On macOS, Docker Desktop should be running
   # Check if Docker is running:
   docker ps
   ```

2. **Start Qdrant using Docker Compose**

   ```bash
   cd /Users/muhammadqureshi/premiere_suites_scraper
   docker-compose -f config/docker-compose.yml up -d
   ```

3. **Verify Qdrant is running**

   ```bash
   curl http://localhost:6333/health
   # Should return: {"title":"qdrant","version":"1.x.x","status":"ok"}
   ```

4. **Run the recreation script**
   ```bash
   python scripts/recreate_collections_simple.py
   ```

## Option 2: Qdrant Cloud (Recommended for Production)

### Prerequisites

- Qdrant Cloud account
- API key and cluster URL

### Steps

1. **Sign up for Qdrant Cloud**

   - Visit: https://cloud.qdrant.io/
   - Create an account and cluster

2. **Get your credentials**

   - Copy your cluster URL (e.g., `https://your-cluster.qdrant.io`)
   - Copy your API key

3. **Set environment variables**

   ```bash
   # Create .env file
   cp config/env.example .env

   # Edit .env file with your credentials
   QDRANT_URL=https://your-cluster.qdrant.io
   QDRANT_API_KEY=your-api-key-here
   ```

4. **Run the recreation script**
   ```bash
   python scripts/recreate_collections_simple.py
   ```

## Troubleshooting

### Docker Issues

- **Docker not running**: Start Docker Desktop application
- **Permission issues**: Make sure Docker Desktop is running and you have proper permissions
- **Port conflicts**: Make sure ports 6333 and 6334 are available

### Connection Issues

- **Local connection refused**: Make sure Qdrant container is running
- **Cloud authentication failed**: Check your API key and URL
- **Network issues**: Check your internet connection for cloud setup

### Data Issues

- **Missing data files**: Make sure the JSONL files exist in `data/processed/`
- **Empty collections**: Check that the data files contain valid JSON

## Verification

After successful setup, you can verify the collections:

```bash
# Check collections (local)
curl http://localhost:6333/collections

# Check collections (cloud)
curl -H "api-key: YOUR_API_KEY" https://your-cluster.qdrant.io/collections
```

You should see two collections:

- `premiere_suites_faqs`
- `premiere_suites_properties`

## Next Steps

Once Qdrant is set up and collections are created, you can:

1. **Search FAQs**: Use the FAQ search functionality
2. **Search Properties**: Use the property search functionality
3. **Integrate with LangChain**: Use the LangChain integration scripts
4. **Deploy to production**: Use Qdrant Cloud for production deployments
