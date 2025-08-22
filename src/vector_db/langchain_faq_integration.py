#!/usr/bin/env python3
"""
LangChain FAQ Integration with Qdrant Vector Database

This module provides LangChain integration for FAQ data in the Premiere Suites project,
allowing you to use both direct Qdrant operations and LangChain's higher-level abstractions
for FAQ search and retrieval.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient

from .qdrant_setup import PremiereSuitesVectorDB

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LangChainFAQIntegration:
    """
    LangChain integration with Qdrant for FAQ data.
    
    This class provides both direct Qdrant operations and LangChain abstractions
    specifically designed for FAQ search and retrieval.
    """
    
    def __init__(self, 
                 collection_name: str = "premiere_suites_faqs",
                 embedding_model: Optional[str] = None,
                 use_cloud: bool = False,
                 qdrant_url: Optional[str] = None,
                 qdrant_api_key: Optional[str] = None):
        """
        Initialize LangChain integration with Qdrant for FAQ data.
        
        Args:
            collection_name: Name of the Qdrant collection
            embedding_model: Embedding model to use
            use_cloud: Whether to use Qdrant Cloud
            qdrant_url: Qdrant Cloud URL
            qdrant_api_key: Qdrant Cloud API key
        """
        self.collection_name = collection_name
        self.use_cloud = use_cloud
        
        # Get embedding model from environment if not provided
        if embedding_model is None:
            embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        
        # Initialize the underlying Qdrant setup
        self.vdb = PremiereSuitesVectorDB(
            qdrant_url=qdrant_url,
            qdrant_api_key=qdrant_api_key,
            collection_name=collection_name,
            embedding_model=embedding_model,
            use_cloud=use_cloud
        )
        
        # Initialize LangChain components
        self._setup_langchain()
    
    def _setup_langchain(self):
        """Set up LangChain components."""
        # Get embedding model from environment or use default
        embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        
        # Ensure embedding_model is not None
        if embedding_model is None:
            embedding_model = "all-MiniLM-L6-v2"
        
        # Initialize embeddings
        if embedding_model.startswith('text-embedding-'):
            # Use OpenAI embeddings
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI embedding models")
            
            self.embeddings = OpenAIEmbeddings(
                model=embedding_model,
                openai_api_key=openai_api_key
            )
        else:
            # Use HuggingFace embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model,
                model_kwargs={'device': 'cpu'}
            )
        
        # Initialize LangChain Qdrant vector store
        self.langchain_store = Qdrant(
            client=self.vdb.client,
            collection_name=self.collection_name,
            embeddings=self.embeddings
        )
        
        logger.info(f"LangChain FAQ integration initialized with {embedding_model}")
    
    def create_collection(self, recreate: bool = False) -> None:
        """Create the Qdrant collection for FAQs."""
        self.vdb.create_collection(recreate=recreate)
    
    def add_faq_documents(self, documents: List[Document], batch_size: int = 50) -> None:
        """
        Add FAQ documents to the vector store using custom content field.
        
        Args:
            documents: List of LangChain Document objects
            batch_size: Number of documents to process per batch
        """
        try:
            logger.info(f"Adding {len(documents)} FAQ documents with custom content field")
            
            # Ensure all documents have proper structure
            for i, doc in enumerate(documents):
                # Ensure content is not empty
                if not doc.page_content.strip():
                    doc.page_content = f"FAQ Document {i + 1}"
                
                # Ensure metadata exists and has required fields
                if not hasattr(doc, 'metadata') or doc.metadata is None:
                    doc.metadata = {}
                
                # Ensure faq_id exists in metadata
                if 'faq_id' not in doc.metadata:
                    doc.metadata['faq_id'] = i + 1
            
            # Add documents manually to use custom field names
            self._add_documents_with_custom_fields(documents, batch_size)
            
            logger.info("FAQ document addition completed successfully")
            
        except Exception as e:
            logger.error(f"Error adding FAQ documents: {e}")
            raise
    
    def _add_documents_with_custom_fields(self, documents: List[Document], batch_size: int = 50) -> None:
        """
        Add documents manually to Qdrant with custom field names (content instead of page_content).
        """
        from qdrant_client.models import PointStruct
        from datetime import datetime
        import uuid
        
        # Generate embeddings for all documents
        texts = [doc.page_content for doc in documents]
        embeddings = self.vdb.generate_embeddings(texts)
        
        # Create points with custom field structure
        points = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            # Generate a unique ID for this point
            point_id = str(uuid.uuid4())
            
            # Create payload with custom field names to match direct Qdrant approach
            payload = {
                "content": doc.page_content,  # Use content instead of page_content
                "metadata": doc.metadata,
                "id": doc.metadata.get('faq_id', i + 1),
                # Also include individual fields for backward compatibility
                "faq_id": doc.metadata.get('faq_id', i + 1),
                "question": doc.metadata.get('question', ''),
                "answer": doc.metadata.get('answer', ''),
                "category": doc.metadata.get('category', ''),
                "tags": doc.metadata.get('tags', []),
                "source_url": doc.metadata.get('source_url', ''),
                "content": doc.metadata.get('content', ''),
                "ingested_at": datetime.now().isoformat()
            }
            
            point = PointStruct(
                id=point_id,
                vector=embedding.tolist(),
                payload=payload
            )
            points.append(point)
        
        # Insert points in batches
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.vdb.client.upsert(
                collection_name=self.collection_name,
                wait=True,
                points=batch
            )
            logger.info(f"Added batch {i//batch_size + 1}/{(len(points) + batch_size - 1)//batch_size}")
        
        logger.info(f"Successfully added {len(points)} documents with custom content field")
    
    def add_faq_texts(self, questions: List[str], answers: List[str], 
                     metadatas: Optional[List[Dict[str, Any]]] = None,
                     ids: Optional[List[Union[str, int]]] = None) -> None:
        """
        Add FAQ texts to the vector store using LangChain.
        
        Args:
            questions: List of FAQ questions
            answers: List of FAQ answers
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of IDs for each FAQ entry
        """
        try:
            # Combine questions and answers for embedding
            texts = [f"Q: {q}\nA: {a}" for q, a in zip(questions, answers)]
            
            # Ensure all texts have content
            for i, text in enumerate(texts):
                if not text.strip():
                    texts[i] = f"FAQ Entry {i + 1}"
            
            # Prepare metadata if not provided
            if metadatas is None:
                metadatas = []
                for i, (q, a) in enumerate(zip(questions, answers)):
                    metadata = {
                        "faq_id": ids[i] if ids and i < len(ids) else i + 1,
                        "question": q,
                        "answer": a,
                        "category": "",
                        "tags": [],
                        "source_url": "",
                        "text_chunk": f"Q: {q}\nA: {a}"
                    }
                    metadatas.append(metadata)
            
            logger.info(f"Adding {len(texts)} FAQ texts using LangChain")
            self.langchain_store.add_texts(texts, metadatas=metadatas, ids=ids)
            logger.info("FAQ text addition completed successfully")
            
        except Exception as e:
            logger.error(f"Error adding FAQ texts: {e}")
            raise
    
    def search_faqs(self, 
                   query: str, 
                   k: int = 5,
                   category: Optional[str] = None,
                   min_score: float = 0.5,
                   **kwargs) -> List[Document]:
        """
        Search FAQs using LangChain.
        
        Args:
            query: Search query
            k: Number of results to return
            category: Filter by category
            min_score: Minimum similarity score
            **kwargs: Additional search parameters
            
        Returns:
            List of LangChain Document objects
        """
        try:
            logger.info(f"Performing FAQ search for: '{query}'")
            
            # Build filter
            filter_dict = {}
            if category:
                filter_dict["category"] = category
            
            # Perform search
            results = self.langchain_store.similarity_search(
                query=query,
                k=k,
                filter=filter_dict if filter_dict else None,
                **kwargs
            )
            
            # Filter by minimum score if needed
            if min_score > 0:
                # Get scores for filtering
                scored_results = self.langchain_store.similarity_search_with_score(
                    query=query,
                    k=k,
                    filter=filter_dict if filter_dict else None,
                    **kwargs
                )
                results = [doc for doc, score in scored_results if score >= min_score]
            
            logger.info(f"Found {len(results)} FAQ results")
            return results
            
        except Exception as e:
            logger.error(f"Error in FAQ search: {e}")
            raise
    
    def search_faqs_with_score(self, 
                             query: str, 
                             k: int = 5,
                             category: Optional[str] = None,
                             min_score: float = 0.5,
                             **kwargs) -> List[tuple[Document, float]]:
        """
        Search FAQs with scores using LangChain.
        
        Args:
            query: Search query
            k: Number of results to return
            category: Filter by category
            min_score: Minimum similarity score
            **kwargs: Additional search parameters
            
        Returns:
            List of tuples containing (Document, score)
        """
        try:
            logger.info(f"Performing FAQ search with scores for: '{query}'")
            
            # Build filter
            filter_dict = {}
            if category:
                filter_dict["category"] = category
            
            # Perform search
            results = self.langchain_store.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter_dict if filter_dict else None,
                **kwargs
            )
            
            # Filter by minimum score
            filtered_results = [(doc, score) for doc, score in results if score >= min_score]
            
            logger.info(f"Found {len(filtered_results)} FAQ results")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error in FAQ search with scores: {e}")
            raise
    
    def load_faq_documents_from_jsonl(self, file_path: str) -> List[Document]:
        """
        Load FAQ documents from JSONL file and convert to LangChain Document format.
        
        Args:
            file_path: Path to the JSONL file
            
        Returns:
            List of LangChain Document objects
        """
        documents = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        import json
                        data = json.loads(line)
                        
                        if data.get("type") == "faq":
                            # Create LangChain Document
                            # Combine question and answer for better search
                            content = f"Q: {data.get('question', '')}\nA: {data.get('answer', '')}"
                            
                            # Ensure we have the required properties
                            faq_id = data.get("id")
                            if faq_id is None:
                                # If no ID exists, use line number as fallback
                                faq_id = line_num
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
                            
                            # Create metadata object - ensure it's not empty
                            metadata = {
                                "faq_id": faq_id,
                                "question": data.get("question", ""),
                                "answer": data.get("answer", ""),
                                "category": data.get("category", ""),
                                "tags": data.get("tags", []),
                                "source_url": data.get("source_url", ""),
                                "text_chunk": data.get("text_chunk", "")
                            }
                            
                            # Ensure pageContent is not empty
                            if not content.strip():
                                content = f"FAQ ID: {faq_id}"
                            
                            doc = Document(
                                page_content=content,
                                metadata=metadata
                            )
                            documents.append(doc)
                            
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parsing line {line_num}: {e}")
                        continue
            
            logger.info(f"Loaded {len(documents)} FAQ documents from {file_path}")
            return documents
            
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading FAQ documents: {e}")
            raise
    
    def search_faqs_langchain(self, 
                            query: str, 
                            limit: int = 5,
                            category: Optional[str] = None,
                            min_score: float = 0.5) -> List[Dict[str, Any]]:
        """
        Search FAQs using LangChain with the same interface as the original search.
        
        Args:
            query: Search query text
            limit: Maximum number of results to return
            category: Filter by category
            min_score: Minimum similarity score
            
        Returns:
            List of search results with scores
        """
        try:
            # Perform search
            results = self.search_faqs_with_score(
                query=query,
                k=limit,
                category=category,
                min_score=min_score
            )
            
            # Format results to match original interface
            formatted_results = []
            for doc, score in results:
                # Extract question and answer from content
                content = doc.page_content
                question = doc.metadata.get("question", "")
                answer = doc.metadata.get("answer", "")
                
                formatted_results.append({
                    "score": score,
                    "faq_id": doc.metadata.get("faq_id"),
                    "question": question,
                    "answer": answer,
                    "category": doc.metadata.get("category"),
                    "tags": doc.metadata.get("tags", [])
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching FAQs with LangChain: {e}")
            raise
    
    def get_faq_categories(self) -> List[str]:
        """
        Get all unique FAQ categories in the collection.
        
        Returns:
            List of category names
        """
        try:
            # Get all points from the collection
            points = self.vdb.client.scroll(
                collection_name=self.collection_name,
                limit=10000,  # Adjust based on your data size
                with_payload=True
            )[0]
            
            # Extract unique categories
            categories = set()
            for point in points:
                category = point.payload.get("category")
                if category:
                    categories.add(category)
            
            return sorted(list(categories))
            
        except Exception as e:
            logger.error(f"Error getting FAQ categories: {e}")
            return []
    
    def get_faq_tags(self) -> List[str]:
        """
        Get all unique FAQ tags in the collection.
        
        Returns:
            List of tag names
        """
        try:
            # Get all points from the collection
            points = self.vdb.client.scroll(
                collection_name=self.collection_name,
                limit=10000,  # Adjust based on your data size
                with_payload=True
            )[0]
            
            # Extract unique tags
            tags = set()
            for point in points:
                point_tags = point.payload.get("tags", [])
                if isinstance(point_tags, list):
                    tags.update(point_tags)
            
            return sorted(list(tags))
            
        except Exception as e:
            logger.error(f"Error getting FAQ tags: {e}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the FAQ collection."""
        return self.vdb.get_collection_info()
    
    def delete_collection(self) -> None:
        """Delete the FAQ collection."""
        self.vdb.client.delete_collection(self.collection_name)
        logger.info(f"FAQ collection '{self.collection_name}' deleted")

def main():
    """Example usage of LangChain FAQ integration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="LangChain FAQ Integration Example")
    parser.add_argument("--collection", default="premiere_suites_faqs",
                       help="Collection name")
    parser.add_argument("--data-file", default="premiere_suites_faq_data.jsonl",
                       help="Path to JSONL FAQ data file")
    parser.add_argument("--cloud", action="store_true",
                       help="Use Qdrant Cloud")
    parser.add_argument("--recreate", action="store_true",
                       help="Recreate collection")
    parser.add_argument("--query", help="Test search query")
    
    args = parser.parse_args()
    
    print("🔗 LangChain FAQ Integration")
    print("=" * 50)
    
    try:
        # Initialize integration
        integration = LangChainFAQIntegration(
            collection_name=args.collection,
            use_cloud=args.cloud
        )
        
        # Create collection
        integration.create_collection(recreate=args.recreate)
        
        # Load FAQ documents
        documents = integration.load_faq_documents_from_jsonl(args.data_file)
        
        if not documents:
            print("❌ No FAQ documents found to process")
            return
        
        # Add documents using LangChain
        integration.add_faq_documents(documents)
        
        # Get collection info
        info = integration.get_collection_info()
        print(f"\n📊 Collection Info:")
        print(f"   Name: {info['name']}")
        print(f"   Total vectors: {info['vectors_count']}")
        print(f"   Vector size: {info['vector_size']}")
        
        # Get categories and tags
        categories = integration.get_faq_categories()
        tags = integration.get_faq_tags()
        print(f"\n📂 Categories: {', '.join(categories)}")
        print(f"🏷️  Tags: {', '.join(tags)}")
        
        # Test search
        if args.query:
            print(f"\n🔍 Testing search: '{args.query}'")
            results = integration.search_faqs_langchain(
                query=args.query,
                limit=5
            )
            
            print(f"\n📊 Search Results:")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['question']}")
                print(f"   Score: {result['score']:.3f}")
                print(f"   Category: {result['category']}")
                print(f"   Answer: {result['answer'][:100]}...")
                print()
        else:
            # Run example searches
            example_queries = [
                "How do I book a reservation?",
                "What are the check-in times?",
                "Do you allow pets?",
                "What payment methods do you accept?"
            ]
            
            print("\n🔍 Example Searches:")
            for query in example_queries:
                print(f"\n📝 Query: '{query}'")
                results = integration.search_faqs_langchain(query, limit=2)
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['question']} (Score: {result['score']:.3f})")
        
        print("\n✅ LangChain FAQ integration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
