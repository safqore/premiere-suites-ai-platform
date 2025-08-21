#!/usr/bin/env python3
"""
FAQ to Qdrant n8n Workflow

This script creates an n8n workflow that:
1. Reads FAQ data from JSONL file
2. Deletes existing FAQ collection if it exists
3. Creates a new FAQ collection
4. Vectorizes and uploads FAQ data to Qdrant
5. Provides webhook endpoints for triggering the workflow
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import requests
from datetime import datetime

def load_environment():
    """Load environment variables from .env file."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

def create_faq_workflow():
    """Create the FAQ to Qdrant workflow."""
    
    workflow = {
        "name": "FAQ to Qdrant Workflow",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "faq-to-qdrant",
                    "responseMode": "responseNode",
                    "options": {
                        "responseHeaders": {
                            "parameters": [
                                {
                                    "name": "Content-Type",
                                    "value": "application/json"
                                }
                            ]
                        }
                    }
                },
                "id": "webhook_trigger",
                "name": "Webhook Trigger",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [240, 300],
                "webhookId": "faq-to-qdrant-webhook"
            },
            {
                "parameters": {
                    "filePath": "data/processed/premiere_suites_faq_data.jsonl",
                    "options": {}
                },
                "id": "read_faq_file",
                "name": "Read FAQ File",
                "type": "n8n-nodes-base.readBinaryFile",
                "typeVersion": 1,
                "position": [460, 300]
            },
            {
                "parameters": {
                    "jsCode": """
// Parse JSONL file content
const fileContent = $input.first().json.data;
const lines = fileContent.split('\\n').filter(line => line.trim());

const faqData = [];
let metadata = null;
let summary = null;

for (const line of lines) {
    try {
        const parsed = JSON.parse(line);
        
        if (parsed.type === 'metadata') {
            metadata = parsed;
        } else if (parsed.type === 'summary') {
            summary = parsed;
        } else if (parsed.type === 'faq') {
            faqData.push(parsed);
        }
    } catch (error) {
        console.log('Error parsing line:', line, error);
    }
}

return [
    {
        json: {
            metadata,
            summary,
            faqs: faqData,
            total_faqs: faqData.length
        }
    }
];
"""
                },
                "id": "parse_jsonl",
                "name": "Parse JSONL",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [680, 300]
            },
            {
                "parameters": {
                    "url": "={{ $env.QDRANT_URL }}/collections/faq_collection",
                    "authentication": "httpHeaderAuth",
                    "httpHeaderAuth": {
                        "name": "api-key",
                        "value": "={{ $env.QDRANT_API_KEY }}"
                    },
                    "options": {
                        "timeout": 10000
                    }
                },
                "id": "check_collection_exists",
                "name": "Check Collection Exists",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [900, 200]
            },
            {
                "parameters": {
                    "method": "DELETE",
                    "url": "={{ $env.QDRANT_URL }}/collections/faq_collection",
                    "authentication": "httpHeaderAuth",
                    "httpHeaderAuth": {
                        "name": "api-key",
                        "value": "={{ $env.QDRANT_API_KEY }}"
                    },
                    "options": {
                        "timeout": 10000
                    }
                },
                "id": "delete_collection",
                "name": "Delete Collection",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [1120, 200]
            },
            {
                "parameters": {
                    "method": "PUT",
                    "url": "={{ $env.QDRANT_URL }}/collections/faq_collection",
                    "authentication": "httpHeaderAuth",
                    "httpHeaderAuth": {
                        "name": "api-key",
                        "value": "={{ $env.QDRANT_API_KEY }}"
                    },
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": [
                            {
                                "name": "vectors",
                                "value": "{\"size\": 1536, \"distance\": \"Cosine\"}"
                            }
                        ]
                    },
                    "options": {
                        "timeout": 10000
                    }
                },
                "id": "create_collection",
                "name": "Create Collection",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [1340, 300]
            },
            {
                "parameters": {
                    "jsCode": """
// Vectorize FAQ data using OpenAI embeddings
const faqs = $input.first().json.faqs;
const vectorizedFaqs = [];

for (const faq of faqs) {
    // Create text for embedding (question + answer)
    const textForEmbedding = `Question: ${faq.question}\\nAnswer: ${faq.answer}`;
    
    // Create payload for OpenAI embedding
    const embeddingPayload = {
        input: textForEmbedding,
        model: "text-embedding-3-small"
    };
    
    vectorizedFaqs.push({
        id: faq.id,
        question: faq.question,
        answer: faq.answer,
        category: faq.category,
        tags: faq.tags,
        source_url: faq.source_url,
        text_chunk: faq.text_chunk,
        embedding_payload: embeddingPayload
    });
}

return [
    {
        json: {
            vectorized_faqs: vectorizedFaqs,
            total_count: vectorizedFaqs.length
        }
    }
];
"""
                },
                "id": "vectorize_faqs",
                "name": "Vectorize FAQs",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1560, 300]
            },
            {
                "parameters": {
                    "method": "POST",
                    "url": "https://api.openai.com/v1/embeddings",
                    "authentication": "httpHeaderAuth",
                    "httpHeaderAuth": {
                        "name": "Authorization",
                        "value": "Bearer {{ $env.OPENAI_API_KEY }}"
                    },
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": [
                            {
                                "name": "input",
                                "value": "={{ $json.embedding_payload.input }}"
                            },
                            {
                                "name": "model",
                                "value": "={{ $json.embedding_payload.model }}"
                            }
                        ]
                    },
                    "options": {
                        "timeout": 30000
                    }
                },
                "id": "get_embeddings",
                "name": "Get Embeddings",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [1780, 300]
            },
            {
                "parameters": {
                    "jsCode": """
// Prepare data for Qdrant upload
const faqs = $input.all();
const uploadData = [];

for (const faq of faqs) {
    const faqData = faq.json;
    const embedding = faqData.data[0].embedding;
    
    uploadData.push({
        id: faqData.id,
        vector: embedding,
        payload: {
            question: faqData.question,
            answer: faqData.answer,
            category: faqData.category,
            tags: faqData.tags,
            source_url: faqData.source_url,
            text_chunk: faqData.text_chunk,
            timestamp: new Date().toISOString()
        }
    });
}

return [
    {
        json: {
            points: uploadData,
            total_points: uploadData.length
        }
    }
];
"""
                },
                "id": "prepare_upload_data",
                "name": "Prepare Upload Data",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [2000, 300]
            },
            {
                "parameters": {
                    "method": "PUT",
                    "url": "={{ $env.QDRANT_URL }}/collections/faq_collection/points",
                    "authentication": "httpHeaderAuth",
                    "httpHeaderAuth": {
                        "name": "api-key",
                        "value": "={{ $env.QDRANT_API_KEY }}"
                    },
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": [
                            {
                                "name": "points",
                                "value": "={{ $json.points }}"
                            }
                        ]
                    },
                    "options": {
                        "timeout": 30000
                    }
                },
                "id": "upload_to_qdrant",
                "name": "Upload to Qdrant",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [2220, 300]
            },
            {
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ { status: 'success', message: 'FAQ data ingested successfully', collection: 'faq_collection', total_faqs: $('Parse JSONL').first().json.total_faqs, vector_size: 1536, timestamp: new Date().toISOString() } }}",
                    "options": {}
                },
                "id": "response",
                "name": "Success Response",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [2440, 300]
            }
        ],
        "connections": {
            "webhook_trigger": {
                "main": [
                    [
                        {
                            "node": "read_faq_file",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "read_faq_file": {
                "main": [
                    [
                        {
                            "node": "parse_jsonl",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "parse_jsonl": {
                "main": [
                    [
                        {
                            "node": "check_collection_exists",
                            "type": "main",
                            "index": 0
                        },
                        {
                            "node": "create_collection",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "check_collection_exists": {
                "main": [
                    [
                        {
                            "node": "delete_collection",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "delete_collection": {
                "main": [
                    [
                        {
                            "node": "create_collection",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "create_collection": {
                "main": [
                    [
                        {
                            "node": "vectorize_faqs",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "vectorize_faqs": {
                "main": [
                    [
                        {
                            "node": "get_embeddings",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "get_embeddings": {
                "main": [
                    [
                        {
                            "node": "prepare_upload_data",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "prepare_upload_data": {
                "main": [
                    [
                        {
                            "node": "upload_to_qdrant",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "upload_to_qdrant": {
                "main": [
                    [
                        {
                            "node": "response",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "active": True,
        "settings": {
            "executionOrder": "v1"
        },
        "versionId": "1",
        "meta": {
            "templateCredsSetupCompleted": True
        },
        "id": "faq-to-qdrant-workflow",
        "tags": ["faq", "qdrant", "vector-database"]
    }
    
    return workflow

def create_workflow_file():
    """Create the workflow JSON file."""
    workflow = create_faq_workflow()
    
    # Create workflows directory if it doesn't exist
    workflows_dir = Path("docs/workflows")
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    # Save workflow to file
    workflow_file = workflows_dir / "faq_to_qdrant_workflow.json"
    with open(workflow_file, "w") as f:
        json.dump(workflow, f, indent=2)
    
    print(f"✅ FAQ to Qdrant workflow created: {workflow_file}")
    return workflow_file

def create_deployment_script():
    """Create a deployment script for the workflow."""
    
    script_content = """#!/usr/bin/env python3
\"\"\"
Deploy FAQ to Qdrant Workflow

This script deploys the FAQ to Qdrant workflow to n8n.
\"\"\"

import json
import requests
import os
from pathlib import Path

def deploy_workflow():
    \"\"\"Deploy the workflow to n8n.\"\"\"
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    n8n_url = os.getenv("N8N_URL", "http://localhost:5678")
    n8n_api_key = os.getenv("N8N_API_KEY")
    
    if not n8n_api_key:
        print("❌ N8N_API_KEY environment variable is required")
        return False
    
    # Load workflow
    workflow_file = Path("docs/workflows/faq_to_qdrant_workflow.json")
    if not workflow_file.exists():
        print(f"❌ Workflow file not found: {workflow_file}")
        return False
    
    with open(workflow_file, "r") as f:
        workflow = json.load(f)
    
    # Deploy to n8n
    headers = {
        "X-N8N-API-KEY": n8n_api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{n8n_url}/api/v1/workflows",
            json=workflow,
            headers=headers
        )
        
        if response.status_code == 201:
            print("✅ Workflow deployed successfully!")
            print(f"   Workflow ID: {response.json().get('id')}")
            print(f"   Webhook URL: {n8n_url}/webhook/faq-to-qdrant")
            return True
        else:
            print(f"❌ Failed to deploy workflow: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error deploying workflow: {e}")
        return False

if __name__ == "__main__":
    deploy_workflow()
"""
    
    script_file = Path("src/n8n_integration/deploy_faq_workflow.py")
    with open(script_file, "w") as f:
        f.write(script_content)
    
    # Make it executable
    os.chmod(script_file, 0o755)
    
    print(f"✅ Deployment script created: {script_file}")
    return script_file

def create_test_script():
    """Create a test script for the workflow."""
    
    script_content = """#!/usr/bin/env python3
\"\"\"
Test FAQ to Qdrant Workflow

This script tests the FAQ to Qdrant workflow by sending a test request.
\"\"\"

import requests
import json
import os
from pathlib import Path

def test_workflow():
    \"\"\"Test the FAQ to Qdrant workflow.\"\"\"
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    n8n_url = os.getenv("N8N_URL", "http://localhost:5678")
    
    # Test webhook endpoint
    webhook_url = f"{n8n_url}/webhook/faq-to-qdrant"
    
    print(f"🔗 Testing webhook: {webhook_url}")
    
    try:
        response = requests.post(
            webhook_url,
            json={"test": True, "timestamp": "2025-01-19T10:00:00Z"},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Workflow executed successfully!")
            try:
                result = response.json()
                print(f"📋 Result: {json.dumps(result, indent=2)}")
            except:
                print(f"📋 Result: {response.text}")
        else:
            print(f"❌ Workflow failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing workflow: {e}")

def test_qdrant_collection():
    \"\"\"Test if the FAQ collection was created successfully.\"\"\"
    
    from dotenv import load_dotenv
    load_dotenv()
    
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    if not qdrant_url or not qdrant_api_key:
        print("❌ Qdrant credentials not found")
        return
    
    headers = {"api-key": qdrant_api_key}
    
    try:
        # Check collection info
        response = requests.get(
            f"{qdrant_url}/collections/faq_collection",
            headers=headers
        )
        
        if response.status_code == 200:
            collection_info = response.json()
            print("✅ FAQ collection exists!")
            print(f"📊 Collection info: {json.dumps(collection_info, indent=2)}")
            
            # Get collection stats
            stats_response = requests.get(
                f"{qdrant_url}/collections/faq_collection",
                headers=headers
            )
            
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"📈 Collection stats: {json.dumps(stats, indent=2)}")
        else:
            print(f"❌ FAQ collection not found: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing Qdrant collection: {e}")

if __name__ == "__main__":
    print("🧪 Testing FAQ to Qdrant workflow...")
    test_workflow()
    print("\\n🔍 Testing Qdrant collection...")
    test_qdrant_collection()
"""
    
    script_file = Path("src/n8n_integration/test_faq_workflow.py")
    with open(script_file, "w") as f:
        f.write(script_content)
    
    # Make it executable
    os.chmod(script_file, 0o755)
    
    print(f"✅ Test script created: {script_file}")
    return script_file

def main():
    """Main function to create the FAQ to Qdrant workflow."""
    print("🚀 Creating FAQ to Qdrant n8n workflow...")
    
    # Load environment
    load_environment()
    
    # Create workflow file
    workflow_file = create_workflow_file()
    
    # Create deployment script
    deploy_script = create_deployment_script()
    
    # Create test script
    test_script = create_test_script()
    
    print("\n📋 Summary:")
    print(f"   Workflow: {workflow_file}")
    print(f"   Deploy script: {deploy_script}")
    print(f"   Test script: {test_script}")
    
    print("\n🔧 Next steps:")
    print("   1. Ensure n8n is running")
    print("   2. Set N8N_API_KEY in your .env file")
    print("   3. Run: python src/n8n_integration/deploy_faq_workflow.py")
    print("   4. Test with: python src/n8n_integration/test_faq_workflow.py")
    
    print("\n🌐 Webhook endpoint will be available at:")
    print("   http://localhost:5678/webhook/faq-to-qdrant")
    
    print("\n📝 Environment variables needed:")
    print("   QDRANT_URL=https://your-cluster.qdrant.io")
    print("   QDRANT_API_KEY=your-qdrant-api-key")
    print("   OPENAI_API_KEY=your-openai-api-key")
    print("   N8N_API_KEY=your-n8n-api-key")

if __name__ == "__main__":
    main()
