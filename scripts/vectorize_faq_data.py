#!/usr/bin/env python3
"""
FAQ Data Vectorization Script

This script vectorizes the Premiere Suites FAQ data and stores it in a Qdrant vector database.
"""

import json
import logging
import os
import sys
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.vector_db.qdrant_setup import PremiereSuitesVectorDB

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_faq_data(file_path: str = "data/processed/premiere_suites_faq_data.jsonl") -> List[Dict[str, Any]]:
    """
    Load FAQ data from JSON Lines file.
    
    Args:
        file_path: Path to the JSON Lines file
        
    Returns:
        List of FAQ dictionaries
    """
    faqs = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    data = json.loads(line)
                    if data.get("type") == "faq":
                        faqs.append(data)
                except json.JSONDecodeError as e:
                    logger.warning(f"Error parsing line {line_num}: {e}")
                    continue
                    
        logger.info(f"Loaded {len(faqs)} FAQ entries from {file_path}")
        return faqs
        
    except FileNotFoundError:
        logger.error(f"FAQ data file not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading FAQ data: {e}")
        raise

def prepare_faq_points(faqs: List[Dict[str, Any]], vdb: PremiereSuitesVectorDB) -> List[Any]:
    """
    Prepare FAQ data for insertion into Qdrant.
    
    Args:
        faqs: List of FAQ dictionaries
        vdb: Vector database instance to use for embeddings
        
    Returns:
        List of PointStruct objects
    """
    from qdrant_client.models import PointStruct
    from datetime import datetime
    
    # Extract text chunks for embedding
    texts = []
    for faq in faqs:
        # Use content if available, otherwise fall back to text_chunk or create from Q&A
        page_content = faq.get("content", "")
        if not page_content.strip():
            text_chunk = faq.get("text_chunk", "")
            if not text_chunk.strip():
                page_content = f"Q: {faq.get('question', '')}\nA: {faq.get('answer', '')}"
            else:
                page_content = text_chunk
        texts.append(page_content)
    
    # Generate embeddings using the provided vector database instance
    logger.info("Generating embeddings for FAQ data...")
    embeddings = vdb.generate_embeddings(texts)
    
    # Create points
    points = []
    for i, faq in enumerate(faqs):
        # Ensure we have a proper ID - convert string IDs to integers
        faq_id = faq.get("id")
        if faq_id is None:
            faq_id = i + 1
        elif isinstance(faq_id, str):
            # Convert string IDs like "faq_001" to integers
            try:
                # Extract number from string ID (e.g., "faq_001" -> 1, "FQ_1" -> 1)
                if faq_id.startswith("faq_"):
                    faq_id = int(faq_id.replace("faq_", ""))
                elif faq_id.startswith("FQ_"):
                    faq_id = int(faq_id.replace("FQ_", ""))
                else:
                    # Try to convert directly to int, fallback to hash
                    faq_id = int(faq_id)
            except (ValueError, AttributeError):
                # If conversion fails, use hash of the string as fallback
                faq_id = abs(hash(faq_id)) % (2**63)  # Ensure it's a positive integer
        elif not isinstance(faq_id, int):
            # Convert other types to integer
            faq_id = abs(hash(str(faq_id))) % (2**63)
        
        # Use content if available, otherwise create it
        page_content = faq.get("content", "")
        if not page_content.strip():
            text_chunk = faq.get("text_chunk", "")
            if not text_chunk.strip():
                page_content = f"Q: {faq.get('question', '')}\nA: {faq.get('answer', '')}"
            else:
                page_content = text_chunk
        
        # Create metadata object
        metadata = {
            "faq_id": faq_id,
            "question": faq.get("question", ""),
            "answer": faq.get("answer", ""),
            "category": faq.get("category", ""),
            "tags": faq.get("tags", []),
            "source_url": faq.get("source_url", ""),
            "content": page_content,  # Include content in metadata
            "ingested_at": datetime.now().isoformat()
        }
        
        point = PointStruct(
            id=faq_id,
            vector=embeddings[i].tolist(),
            payload={
                "content": page_content,  # This is the key field for retrieval
                "metadata": metadata,
                "id": faq_id,
                # Also include individual fields for backward compatibility
                "faq_id": faq_id,
                "question": faq.get("question", ""),
                "answer": faq.get("answer", ""),
                "category": faq.get("category", ""),
                "tags": faq.get("tags", []),
                "source_url": faq.get("source_url", ""),
                "content": page_content,  # Include content in payload
                "ingested_at": datetime.now().isoformat()
            }
        )
        points.append(point)
    
    logger.info(f"Prepared {len(points)} FAQ points for insertion")
    return points

def vectorize_faq_data(collection_name: str = "premiere_suites_faqs",
                      recreate_collection: bool = False,
                      use_cloud: bool = None,
                      qdrant_url: str = None,
                      qdrant_api_key: str = None) -> None:
    """
    Vectorize FAQ data and store in Qdrant vector database.
    
    Args:
        collection_name: Name of the collection to store FAQs
        recreate_collection: Whether to recreate the collection if it exists
        use_cloud: Whether to use Qdrant Cloud
        qdrant_url: Qdrant Cloud URL (required if use_cloud=True)
        qdrant_api_key: Qdrant Cloud API key (required if use_cloud=True)
    """
    try:
        # Initialize vector database
        logger.info("Initializing vector database...")
        
        # Auto-detect cloud vs local based on environment variables
        env_qdrant_url = os.getenv("QDRANT_URL")
        env_qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        # Determine if we should use cloud
        if use_cloud is None:
            use_cloud = bool(env_qdrant_url and env_qdrant_api_key)
        
        if use_cloud:
            # Use provided credentials or fall back to environment variables
            qdrant_url = qdrant_url or env_qdrant_url
            qdrant_api_key = qdrant_api_key or env_qdrant_api_key
            
            if not qdrant_url or not qdrant_api_key:
                raise ValueError("Qdrant Cloud requires both QDRANT_URL and QDRANT_API_KEY environment variables or command line arguments")
            
            logger.info(f"Using Qdrant Cloud: {qdrant_url}")
            vdb = PremiereSuitesVectorDB(
                qdrant_url=qdrant_url,
                qdrant_api_key=qdrant_api_key,
                collection_name=collection_name,
                embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
                use_cloud=True
            )
        else:
            logger.info("Using local Qdrant instance")
            vdb = PremiereSuitesVectorDB(
                collection_name=collection_name,
                embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            )
        
        # Create collection
        logger.info(f"Creating collection: {collection_name}")
        vdb.create_collection(recreate=recreate_collection)
        
        # Load FAQ data
        logger.info("Loading FAQ data...")
        faqs = load_faq_data()
        
        if not faqs:
            logger.error("No FAQ data found to vectorize")
            return
        
        # Prepare points for insertion
        logger.info("Preparing FAQ data for vectorization...")
        points = prepare_faq_points(faqs, vdb)
        
        # Insert data into vector database
        logger.info("Inserting FAQ data into vector database...")
        vdb.insert_data(points, batch_size=50)
        
        # Get collection info
        info = vdb.get_collection_info()
        logger.info(f"Vectorization completed successfully!")
        logger.info(f"Collection: {info['name']}")
        logger.info(f"Total vectors: {info['vectors_count']}")
        logger.info(f"Vector size: {info['vector_size']}")
        
    except Exception as e:
        logger.error(f"Error during vectorization: {e}")
        raise

def main():
    """Main function to run FAQ vectorization."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Vectorize Premiere Suites FAQ data")
    parser.add_argument("--collection", default="premiere_suites_faqs", 
                       help="Collection name (default: premiere_suites_faqs)")
    parser.add_argument("--recreate", action="store_true", 
                       help="Recreate collection if it exists")
    parser.add_argument("--cloud", action="store_true", 
                       help="Force use of Qdrant Cloud (auto-detected if QDRANT_URL and QDRANT_API_KEY are set)")
    parser.add_argument("--local", action="store_true",
                       help="Force use of local Qdrant instance (ignores environment variables)")
    parser.add_argument("--url", help="Qdrant Cloud URL (overrides QDRANT_URL environment variable)")
    parser.add_argument("--api-key", help="Qdrant Cloud API key (overrides QDRANT_API_KEY environment variable)")
    
    args = parser.parse_args()
    
    print("🏠 Premiere Suites FAQ Vectorization")
    print("=" * 50)
    
    try:
        # Determine cloud usage based on arguments
        use_cloud = None
        if args.local:
            use_cloud = False
        elif args.cloud:
            use_cloud = True
        
        vectorize_faq_data(
            collection_name=args.collection,
            recreate_collection=args.recreate,
            use_cloud=use_cloud,
            qdrant_url=args.url,
            qdrant_api_key=args.api_key
        )
        
        print("\n✅ FAQ data vectorization completed successfully!")
        print(f"📊 Collection: {args.collection}")
        print("\n🔍 You can now search the FAQ data using semantic similarity!")
        
    except Exception as e:
        print(f"\n❌ Error during vectorization: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
