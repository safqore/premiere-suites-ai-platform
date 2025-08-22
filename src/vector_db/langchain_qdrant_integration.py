#!/usr/bin/env python3
"""
LangChain Integration with Qdrant Vector Database

This module provides LangChain integration for the Premiere Suites Qdrant setup,
allowing you to use both direct Qdrant operations and LangChain's higher-level abstractions.
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

class LangChainQdrantIntegration:
    """
    LangChain integration with Qdrant for Premiere Suites data.
    
    This class provides both direct Qdrant operations and LangChain abstractions,
    allowing you to use the best of both worlds.
    """
    
    def __init__(self, 
                 collection_name: str = "premiere_suites_properties",
                 embedding_model: Optional[str] = None,
                 use_cloud: bool = False,
                 qdrant_url: Optional[str] = None,
                 qdrant_api_key: Optional[str] = None):
        """
        Initialize LangChain integration with Qdrant.
        
        Args:
            collection_name: Name of the Qdrant collection
            embedding_model: Embedding model to use
            use_cloud: Whether to use Qdrant Cloud
            qdrant_url: Qdrant Cloud URL
            qdrant_api_key: Qdrant Cloud API key
        """
        self.collection_name = collection_name
        self.use_cloud = use_cloud
        
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
        
        logger.info(f"LangChain integration initialized with {embedding_model}")
    
    def create_collection(self, recreate: bool = False) -> None:
        """Create the Qdrant collection."""
        self.vdb.create_collection(recreate=recreate)
    
    def add_documents(self, documents: List[Document], batch_size: int = 100) -> None:
        """
        Add documents to the vector store using LangChain.
        
        Args:
            documents: List of LangChain Document objects
            batch_size: Number of documents to process per batch
        """
        try:
            logger.info(f"Adding {len(documents)} documents using LangChain")
            
            # Add documents in batches
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                self.langchain_store.add_documents(batch)
                logger.info(f"Added batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")
            
            logger.info("Document addition completed successfully")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Add texts to the vector store using LangChain.
        
        Args:
            texts: List of text strings
            metadatas: Optional list of metadata dictionaries
        """
        try:
            logger.info(f"Adding {len(texts)} texts using LangChain")
            self.langchain_store.add_texts(texts, metadatas=metadatas)
            logger.info("Text addition completed successfully")
            
        except Exception as e:
            logger.error(f"Error adding texts: {e}")
            raise
    
    def similarity_search(self, 
                         query: str, 
                         k: int = 10,
                         filter: Optional[Dict[str, Any]] = None,
                         **kwargs) -> List[Document]:
        """
        Perform similarity search using LangChain.
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Optional filter dictionary
            **kwargs: Additional search parameters
            
        Returns:
            List of LangChain Document objects
        """
        try:
            logger.info(f"Performing similarity search for: '{query}'")
            
            # Convert filter to Qdrant format if needed
            qdrant_filter = self._convert_filter_to_qdrant(filter) if filter else None
            
            results = self.langchain_store.similarity_search(
                query=query,
                k=k,
                filter=qdrant_filter,
                **kwargs
            )
            
            logger.info(f"Found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            raise
    
    def similarity_search_with_score(self, 
                                   query: str, 
                                   k: int = 10,
                                   filter: Optional[Dict[str, Any]] = None,
                                   **kwargs) -> List[tuple[Document, float]]:
        """
        Perform similarity search with scores using LangChain.
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Optional filter dictionary
            **kwargs: Additional search parameters
            
        Returns:
            List of tuples containing (Document, score)
        """
        try:
            logger.info(f"Performing similarity search with scores for: '{query}'")
            
            # Convert filter to Qdrant format if needed
            qdrant_filter = self._convert_filter_to_qdrant(filter) if filter else None
            
            results = self.langchain_store.similarity_search_with_score(
                query=query,
                k=k,
                filter=qdrant_filter,
                **kwargs
            )
            
            logger.info(f"Found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search with scores: {e}")
            raise
    
    def _convert_filter_to_qdrant(self, filter_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert LangChain filter format to Qdrant format.
        
        Args:
            filter_dict: LangChain filter dictionary
            
        Returns:
            Qdrant filter dictionary
        """
        # This is a simple conversion - you might need to extend this
        # based on your specific filter requirements
        return filter_dict
    
    def load_documents_from_jsonl(self, file_path: str) -> List[Document]:
        """
        Load documents from JSONL file and convert to LangChain Document format.
        
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
                        
                        if data.get("type") == "property":
                            # Create LangChain Document
                            doc = Document(
                                page_content=data.get("text_chunk", ""),
                                metadata={
                                    "property_id": data.get("id"),
                                    "property_name": data.get("property_name"),
                                    "city": data.get("city"),
                                    "rating": data.get("rating"),
                                    "room_type": data.get("room_type"),
                                    "amenities": data.get("amenities", []),
                                    "description": data.get("description"),
                                    "pet_friendly": data.get("pet_friendly"),
                                    "bedrooms": data.get("bedrooms"),
                                    "building_type": data.get("building_type"),
                                    "suite_features": data.get("suite_features", []),
                                    "source_url": data.get("source_url"),
                                    "image_url": data.get("image_url"),
                                    "price_range": data.get("price_range"),
                                    "location_details": data.get("location_details")
                                }
                            )
                            documents.append(doc)
                            
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parsing line {line_num}: {e}")
                        continue
            
            logger.info(f"Loaded {len(documents)} documents from {file_path}")
            return documents
            
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            raise
    
    def search_properties_langchain(self, 
                                  query: str, 
                                  limit: int = 10,
                                  city: Optional[str] = None,
                                  min_rating: Optional[float] = None,
                                  pet_friendly: Optional[bool] = None,
                                  bedrooms: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search properties using LangChain with the same interface as the original search.
        
        Args:
            query: Search query text
            limit: Maximum number of results to return
            city: Filter by city
            min_rating: Minimum rating filter
            pet_friendly: Pet friendly filter
            bedrooms: Number of bedrooms filter
            
        Returns:
            List of search results with scores
        """
        try:
            # Build filter
            filter_dict = {}
            if city:
                filter_dict["city"] = city
            if min_rating is not None:
                filter_dict["rating"] = {"$gte": min_rating}
            if pet_friendly is not None:
                filter_dict["pet_friendly"] = pet_friendly
            if bedrooms is not None:
                filter_dict["bedrooms"] = bedrooms
            
            # Perform search
            results = self.similarity_search_with_score(
                query=query,
                k=limit,
                filter=filter_dict if filter_dict else None
            )
            
            # Format results to match original interface
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "score": score,
                    "property_id": doc.metadata.get("property_id"),
                    "property_name": doc.metadata.get("property_name"),
                    "city": doc.metadata.get("city"),
                    "rating": doc.metadata.get("rating"),
                    "description": doc.metadata.get("description"),
                    "amenities": doc.metadata.get("amenities", []),
                    "pet_friendly": doc.metadata.get("pet_friendly"),
                    "bedrooms": doc.metadata.get("bedrooms"),
                    "source_url": doc.metadata.get("source_url"),
                    "image_url": doc.metadata.get("image_url")
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching properties with LangChain: {e}")
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        return self.vdb.get_collection_info()
    
    def delete_collection(self) -> None:
        """Delete the collection."""
        self.vdb.client.delete_collection(self.collection_name)
        logger.info(f"Collection '{self.collection_name}' deleted")

def main():
    """Example usage of LangChain integration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="LangChain Qdrant Integration Example")
    parser.add_argument("--collection", default="premiere_suites_properties",
                       help="Collection name")
    parser.add_argument("--data-file", default="premiere_suites_data.jsonl",
                       help="Path to JSONL data file")
    parser.add_argument("--cloud", action="store_true",
                       help="Use Qdrant Cloud")
    parser.add_argument("--recreate", action="store_true",
                       help="Recreate collection")
    
    args = parser.parse_args()
    
    print("🔗 LangChain Qdrant Integration")
    print("=" * 50)
    
    try:
        # Initialize integration
        integration = LangChainQdrantIntegration(
            collection_name=args.collection,
            use_cloud=args.cloud
        )
        
        # Create collection
        integration.create_collection(recreate=args.recreate)
        
        # Load documents
        documents = integration.load_documents_from_jsonl(args.data_file)
        
        if not documents:
            print("❌ No documents found to process")
            return
        
        # Add documents using LangChain
        integration.add_documents(documents)
        
        # Test search
        print("\n🔍 Testing LangChain search...")
        results = integration.search_properties_langchain(
            query="luxury apartment with pool and gym",
            limit=5,
            min_rating=4.0
        )
        
        print("\n📊 Search Results:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['property_name']} ({result['city']}) - Rating: {result['rating']} - Score: {result['score']:.4f}")
        
        print("\n✅ LangChain integration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
