#!/usr/bin/env python3
"""
n8n Integration Setup for Premiere Suites Qdrant Cloud

This script helps set up n8n workflows to interact with the Qdrant Cloud
vector database for property searches and automation.
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, Any, List

def load_environment():
    """Load environment variables from .env file."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

def check_n8n_installation():
    """Check if n8n is installed and running."""
    print("🔍 Checking n8n installation...")
    
    # Check if n8n is installed globally
    try:
        import subprocess
        result = subprocess.run(['n8n', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ n8n is installed (version: {result.stdout.strip()})")
            return True
        else:
            print("❌ n8n is not installed globally")
            return False
    except FileNotFoundError:
        print("❌ n8n is not installed")
        return False

def create_n8n_credentials():
    """Create n8n credentials for Qdrant Cloud."""
    print("\n🔐 Creating n8n credentials for Qdrant Cloud...")
    
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    if not qdrant_url or not qdrant_api_key:
        print("❌ Qdrant Cloud credentials not found in environment variables")
        return False
    
    credentials = {
        "name": "Qdrant Cloud",
        "type": "httpHeaderAuth",
        "data": {
            "name": "Qdrant Cloud API",
            "httpHeaderAuth": {
                "name": "api-key",
                "value": qdrant_api_key
            },
            "httpBasicAuth": {},
            "httpDigestAuth": {},
            "httpQueryAuth": {},
            "oAuth2": {},
            "httpHeaderAuth": {
                "name": "api-key",
                "value": qdrant_api_key
            }
        }
    }
    
    # Save credentials to file
    with open("n8n_qdrant_credentials.json", "w") as f:
        json.dump(credentials, f, indent=2)
    
    print("✅ n8n credentials saved to n8n_qdrant_credentials.json")
    print(f"   Qdrant URL: {qdrant_url}")
    print("   API Key: [HIDDEN]")
    
    return True

def create_n8n_workflows():
    """Create example n8n workflows for property search."""
    print("\n📋 Creating n8n workflows...")
    
    workflows = {
        "property_search_workflow": {
            "name": "Property Search Workflow",
            "nodes": [
                {
                    "id": "webhook",
                    "type": "n8n-nodes-base.webhook",
                    "position": [240, 300],
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "property-search",
                        "responseMode": "responseNode",
                        "options": {}
                    }
                },
                {
                    "id": "qdrant_search",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [460, 300],
                    "parameters": {
                        "url": "={{ $env.QDRANT_URL }}/collections/premiere_suites_properties/points/search",
                        "authentication": "httpHeaderAuth",
                        "httpHeaderAuth": {
                            "name": "api-key",
                            "value": "={{ $env.QDRANT_API_KEY }}"
                        },
                        "method": "POST",
                        "sendHeaders": True,
                        "headerParameters": {
                            "parameters": [
                                {
                                    "name": "Content-Type",
                                    "value": "application/json"
                                }
                            ]
                        },
                        "sendBody": True,
                        "bodyParameters": {
                            "parameters": [
                                {
                                    "name": "vector",
                                    "value": "={{ $json.query_vector }}"
                                },
                                {
                                    "name": "limit",
                                    "value": "={{ $json.limit || 10 }}"
                                },
                                {
                                    "name": "with_payload",
                                    "value": "true"
                                }
                            ]
                        }
                    }
                },
                {
                    "id": "format_results",
                    "type": "n8n-nodes-base.set",
                    "position": [680, 300],
                    "parameters": {
                        "values": {
                            "string": [
                                {
                                    "name": "results",
                                    "value": "={{ $json.result }}"
                                },
                                {
                                    "name": "total_found",
                                    "value": "={{ $json.result.length }}"
                                },
                                {
                                    "name": "query",
                                    "value": "={{ $('Webhook').item.json.query }}"
                                }
                            ]
                        },
                        "options": {}
                    }
                },
                {
                    "id": "webhook_response",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "position": [900, 300],
                    "parameters": {
                        "respondWith": "json",
                        "responseBody": "={{ $json }}",
                        "options": {}
                    }
                }
            ],
            "connections": {
                "Webhook": {
                    "main": [
                        [
                            {
                                "node": "Qdrant Search",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "Qdrant Search": {
                    "main": [
                        [
                            {
                                "node": "Format Results",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "Format Results": {
                    "main": [
                        [
                            {
                                "node": "Webhook Response",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            }
        },
        "property_filter_workflow": {
            "name": "Property Filter Workflow",
            "nodes": [
                {
                    "id": "webhook",
                    "type": "n8n-nodes-base.webhook",
                    "position": [240, 300],
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "property-filter",
                        "responseMode": "responseNode",
                        "options": {}
                    }
                },
                {
                    "id": "build_filter",
                    "type": "n8n-nodes-base.set",
                    "position": [460, 300],
                    "parameters": {
                        "values": {
                            "string": [
                                {
                                    "name": "filter",
                                    "value": "={{ $json.city ? { must: [{ key: 'city', match: { value: $json.city } }] } : {} }}"
                                }
                            ]
                        },
                        "options": {}
                    }
                },
                {
                    "id": "qdrant_search",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [680, 300],
                    "parameters": {
                        "url": "={{ $env.QDRANT_URL }}/collections/premiere_suites_properties/points/search",
                        "authentication": "httpHeaderAuth",
                        "httpHeaderAuth": {
                            "name": "api-key",
                            "value": "={{ $env.QDRANT_API_KEY }}"
                        },
                        "method": "POST",
                        "sendHeaders": True,
                        "headerParameters": {
                            "parameters": [
                                {
                                    "name": "Content-Type",
                                    "value": "application/json"
                                }
                            ]
                        },
                        "sendBody": True,
                        "bodyParameters": {
                            "parameters": [
                                {
                                    "name": "vector",
                                    "value": "={{ $json.query_vector }}"
                                },
                                {
                                    "name": "limit",
                                    "value": "={{ $json.limit || 10 }}"
                                },
                                {
                                    "name": "filter",
                                    "value": "={{ $json.filter }}"
                                },
                                {
                                    "name": "with_payload",
                                    "value": "true"
                                }
                            ]
                        }
                    }
                },
                {
                    "id": "webhook_response",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "position": [900, 300],
                    "parameters": {
                        "respondWith": "json",
                        "responseBody": "={{ $json }}",
                        "options": {}
                    }
                }
            ],
            "connections": {
                "Webhook": {
                    "main": [
                        [
                            {
                                "node": "Build Filter",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "Build Filter": {
                    "main": [
                        [
                            {
                                "node": "Qdrant Search",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "Qdrant Search": {
                    "main": [
                        [
                            {
                                "node": "Webhook Response",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            }
        }
    }
    
    # Save workflows to files
    for workflow_name, workflow_data in workflows.items():
        filename = f"n8n_{workflow_name}.json"
        with open(filename, "w") as f:
            json.dump(workflow_data, f, indent=2)
        print(f"✅ Created workflow: {filename}")
    
    return True

def create_embedding_service():
    """Create a simple embedding service for n8n."""
    print("\n🧠 Creating embedding service...")
    
    embedding_service = {
        "name": "embedding_service.py",
        "content": '''#!/usr/bin/env python3
"""
Embedding Service for n8n Property Search

This service generates embeddings for search queries to be used with Qdrant Cloud.
"""

from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import os

app = Flask(__name__)

# Load the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

@app.route('/generate-embedding', methods=['POST'])
def generate_embedding():
    """Generate embedding for a text query."""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Generate embedding
        embedding = model.encode([text])[0].tolist()
        
        return jsonify({
            'embedding': embedding,
            'text': text,
            'dimension': len(embedding)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'model': 'all-MiniLM-L6-v2'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
'''
    }
    
    with open("embedding_service.py", "w") as f:
        f.write(embedding_service["content"])
    
    print("✅ Created embedding service: embedding_service.py")
    return True

def create_n8n_environment_file():
    """Create n8n environment configuration."""
    print("\n⚙️ Creating n8n environment configuration...")
    
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    if not qdrant_url or not qdrant_api_key:
        print("❌ Qdrant Cloud credentials not found")
        return False
    
    env_content = f"""# n8n Environment Variables for Qdrant Cloud Integration

# Qdrant Cloud Configuration
QDRANT_URL={qdrant_url}
QDRANT_API_KEY={qdrant_api_key}

# n8n Configuration
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your-secure-password

# Optional: Database configuration
N8N_DATABASE_TYPE=sqlite
N8N_DATABASE_SQLITE_DATABASE=./n8n-database.db

# Optional: Webhook configuration
N8N_WEBHOOK_URL=http://localhost:5678/
"""
    
    with open("n8n.env", "w") as f:
        f.write(env_content)
    
    print("✅ Created n8n environment file: n8n.env")
    print("   Please update the password in n8n.env")
    
    return True

def create_docker_compose_n8n():
    """Create Docker Compose file for n8n with embedding service."""
    print("\n🐳 Creating Docker Compose for n8n...")
    
    docker_compose = '''version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: premiere_suites_n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=your-secure-password
      - N8N_DATABASE_TYPE=sqlite
      - N8N_DATABASE_SQLITE_DATABASE=/home/node/.n8n/database.db
      - QDRANT_URL=${QDRANT_URL}
      - QDRANT_API_KEY=${QDRANT_API_KEY}
    volumes:
      - n8n_data:/home/node/.n8n
      - ./n8n_workflows:/home/node/.n8n/workflows
    restart: unless-stopped
    depends_on:
      - embedding-service

  embedding-service:
    build:
      context: .
      dockerfile: Dockerfile.embedding
    container_name: premiere_suites_embedding
    ports:
      - "5000:5000"
    environment:
      - PORT=5000
    restart: unless-stopped

volumes:
  n8n_data:
    driver: local
'''
    
    with open("docker-compose.n8n.yml", "w") as f:
        f.write(docker_compose)
    
    print("✅ Created Docker Compose file: docker-compose.n8n.yml")
    return True

def create_embedding_dockerfile():
    """Create Dockerfile for embedding service."""
    print("\n🐳 Creating Dockerfile for embedding service...")
    
    dockerfile = '''FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the embedding service
COPY embedding_service.py .

# Expose port
EXPOSE 5000

# Run the service
CMD ["python", "embedding_service.py"]
'''
    
    with open("Dockerfile.embedding", "w") as f:
        f.write(dockerfile)
    
    print("✅ Created Dockerfile: Dockerfile.embedding")
    return True

def create_n8n_usage_examples():
    """Create examples of how to use n8n with the property search."""
    print("\n📚 Creating n8n usage examples...")
    
    examples = {
        "webhook_examples.md": """# n8n Webhook Examples

## Property Search Webhook

### Endpoint
```
POST http://localhost:5678/webhook/property-search
```

### Request Body
```json
{
  "query": "luxury apartment with pool",
  "limit": 5,
  "city": "Toronto",
  "min_rating": 4.0,
  "pet_friendly": true
}
```

### Response
```json
{
  "results": [
    {
      "property_name": "300 Front",
      "city": "Toronto",
      "rating": 5.0,
      "score": 0.85,
      "amenities": ["Pool", "Gym", "Pet Friendly"],
      "source_url": "https://premieresuites.com/..."
    }
  ],
  "total_found": 5,
  "query": "luxury apartment with pool"
}
```

## Property Filter Webhook

### Endpoint
```
POST http://localhost:5678/webhook/property-filter
```

### Request Body
```json
{
  "query": "apartment with terrace",
  "city": "Vancouver",
  "min_rating": 4.5,
  "limit": 10
}
```

## Slack Integration Example

### Workflow Trigger
- Slack message containing "find apartment in Toronto"
- Extract city and requirements
- Call property search webhook
- Format results for Slack
- Send response back to Slack

## Email Integration Example

### Workflow Trigger
- Email received with property requirements
- Parse email content for search criteria
- Call property search webhook
- Generate HTML email with results
- Send email response

## CRM Integration Example

### Workflow Trigger
- New lead created in CRM
- Extract property requirements from lead data
- Search for matching properties
- Update lead with property recommendations
- Send automated follow-up email
""",
        
        "n8n_workflow_import.md": """# Importing n8n Workflows

## Method 1: Manual Import

1. Open n8n at http://localhost:5678
2. Click "Import from file"
3. Select the workflow JSON file
4. Click "Import"

## Method 2: API Import

```bash
curl -X POST http://localhost:5678/rest/workflows \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Basic YWRtaW46eW91ci1zZWN1cmUtcGFzc3dvcmQ=" \\
  -d @n8n_property_search_workflow.json
```

## Method 3: Docker Volume Mount

The workflows are automatically available in the container at:
```
/home/node/.n8n/workflows/
```

## Available Workflows

1. **property_search_workflow.json** - Basic property search
2. **property_filter_workflow.json** - Advanced filtering
3. **slack_integration_workflow.json** - Slack bot integration
4. **email_integration_workflow.json** - Email automation
5. **crm_integration_workflow.json** - CRM integration
"""
    }
    
    for filename, content in examples.items():
        with open(filename, "w") as f:
            f.write(content)
        print(f"✅ Created example: {filename}")
    
    return True

def main():
    """Main setup function."""
    print("🔧 n8n Integration Setup for Premiere Suites")
    print("=" * 60)
    
    load_environment()
    
    # Check n8n installation
    n8n_installed = check_n8n_installation()
    
    # Create n8n credentials
    if not create_n8n_credentials():
        print("\n❌ Failed to create n8n credentials")
        return False
    
    # Create n8n workflows
    if not create_n8n_workflows():
        print("\n❌ Failed to create n8n workflows")
        return False
    
    # Create embedding service
    if not create_embedding_service():
        print("\n❌ Failed to create embedding service")
        return False
    
    # Create n8n environment file
    if not create_n8n_environment_file():
        print("\n❌ Failed to create n8n environment file")
        return False
    
    # Create Docker Compose for n8n
    if not create_docker_compose_n8n():
        print("\n❌ Failed to create Docker Compose file")
        return False
    
    # Create embedding Dockerfile
    if not create_embedding_dockerfile():
        print("\n❌ Failed to create embedding Dockerfile")
        return False
    
    # Create usage examples
    if not create_n8n_usage_examples():
        print("\n❌ Failed to create usage examples")
        return False
    
    # Success!
    print("\n🎉 n8n integration setup completed successfully!")
    print("\nNext steps:")
    print("1. Start n8n with Docker: docker-compose -f docker-compose.n8n.yml up -d")
    print("2. Access n8n at: http://localhost:5678")
    print("3. Import the workflow JSON files")
    print("4. Configure your webhooks and integrations")
    print("5. Test the property search workflows")
    
    if not n8n_installed:
        print("\nNote: n8n is not installed globally. Using Docker is recommended.")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
