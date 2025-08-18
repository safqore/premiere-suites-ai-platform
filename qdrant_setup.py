#!/usr/bin/env python3
"""
Qdrant Vector Database Setup for Premiere Suites Property Data

This script sets up a Qdrant vector database to store and search through
property listings with semantic search capabilities.
Supports both Qdrant Cloud and local Qdrant instances.
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import numpy as np
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, 
    FieldCondition, MatchValue, Filter,
    CreateCollection, OptimizersConfigDiff
)
from qdrant_client.http import models

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PremiereSuitesVectorDB:
    """Vector database manager for Premiere Suites property data."""
    
    def __init__(self, 
                 qdrant_url: Optional[str] = None,
                 qdrant_api_key: Optional[str] = None,
                 qdrant_host: str = "localhost", 
                 qdrant_port: int = 6333,
                 collection_name: str = "premiere_suites_properties",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 use_cloud: bool = False):
        """
        Initialize the vector database manager.
        
        Args:
            qdrant_url: Qdrant Cloud URL (e.g., "https://your-cluster.qdrant.io")
            qdrant_api_key: Qdrant Cloud API key
            qdrant_host: Qdrant server host (for local instances)
            qdrant_port: Qdrant server port (for local instances)
            collection_name: Name of the collection to store properties
            embedding_model: Sentence transformer model to use for embeddings
            use_cloud: Whether to use Qdrant Cloud (if True, qdrant_url and qdrant_api_key are required)
        """
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Initialize Qdrant client
        if use_cloud:
            if not qdrant_url or not qdrant_api_key:
                raise ValueError("Qdrant Cloud requires both qdrant_url and qdrant_api_key")
            logger.info(f"Connecting to Qdrant Cloud: {qdrant_url}")
            self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        else:
            logger.info(f"Connecting to local Qdrant: {qdrant_host}:{qdrant_port}")
            self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        
        # Initialize sentence transformer
        logger.info(f"Loading embedding model: {embedding_model}")
        self.model = SentenceTransformer(embedding_model)
        self.vector_size = self.model.get_sentence_embedding_dimension()
        
        logger.info(f"Vector dimension: {self.vector_size}")
    
    def create_collection(self, recreate: bool = False) -> None:
        """
        Create the collection for storing property data.
        
        Args:
            recreate: Whether to recreate the collection if it exists
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_exists = any(col.name == self.collection_name for col in collections.collections)
            
            if collection_exists and recreate:
                logger.info(f"Recreating collection: {self.collection_name}")
                self.client.delete_collection(self.collection_name)
                collection_exists = False
            
            if not collection_exists:
                logger.info(f"Creating collection: {self.collection_name}")
                
                # Create collection with optimized settings
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE,
                        on_disk=True  # Store vectors on disk for large datasets
                    ),
                    optimizers_config=OptimizersConfigDiff(
                        memmap_threshold=10000,  # Use memory mapping for collections > 10k points
                        default_segment_number=2
                    )
                )
                
                # Create payload indexes for efficient filtering
                self._create_indexes()
                logger.info(f"Collection '{self.collection_name}' created successfully")
            else:
                logger.info(f"Collection '{self.collection_name}' already exists")
                
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    def _create_indexes(self) -> None:
        """Create payload indexes for efficient filtering."""
        try:
            # Index for city filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="city",
                field_schema=models.PayloadFieldSchema.KEYWORD
            )
            
            # Index for rating filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="rating",
                field_schema=models.PayloadFieldSchema.FLOAT
            )
            
            # Index for pet_friendly filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="pet_friendly",
                field_schema=models.PayloadFieldSchema.BOOL
            )
            
            # Index for bedrooms filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="bedrooms",
                field_schema=models.PayloadFieldSchema.INTEGER
            )
            
            # Index for room_type filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="room_type",
                field_schema=models.PayloadFieldSchema.KEYWORD
            )
            
            logger.info("Payload indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Error creating indexes (some may already exist): {e}")
    
    def load_data_from_jsonl(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load property data from JSONL file.
        
        Args:
            file_path: Path to the JSONL file
            
        Returns:
            List of property dictionaries
        """
        properties = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        if data.get("type") == "property":
                            properties.append(data)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parsing line {line_num}: {e}")
                        continue
            
            logger.info(f"Loaded {len(properties)} properties from {file_path}")
            return properties
            
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            Numpy array of embeddings
        """
        logger.info(f"Generating embeddings for {len(texts)} texts")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings
    
    def prepare_points(self, properties: List[Dict[str, Any]]) -> List[PointStruct]:
        """
        Prepare property data for insertion into Qdrant.
        
        Args:
            properties: List of property dictionaries
            
        Returns:
            List of PointStruct objects
        """
        # Extract text chunks for embedding
        texts = [prop.get("text_chunk", "") for prop in properties]
        
        # Generate embeddings
        embeddings = self.generate_embeddings(texts)
        
        # Create points
        points = []
        for i, prop in enumerate(properties):
            point = PointStruct(
                id=i,  # Using index as ID, you might want to use a unique identifier
                vector=embeddings[i].tolist(),
                payload={
                    "property_id": prop.get("id"),
                    "property_name": prop.get("property_name"),
                    "city": prop.get("city"),
                    "rating": prop.get("rating"),
                    "room_type": prop.get("room_type"),
                    "amenities": prop.get("amenities", []),
                    "description": prop.get("description"),
                    "pet_friendly": prop.get("pet_friendly"),
                    "bedrooms": prop.get("bedrooms"),
                    "building_type": prop.get("building_type"),
                    "suite_features": prop.get("suite_features", []),
                    "source_url": prop.get("source_url"),
                    "image_url": prop.get("image_url"),
                    "text_chunk": prop.get("text_chunk"),
                    "price_range": prop.get("price_range"),
                    "location_details": prop.get("location_details"),
                    "ingested_at": datetime.now().isoformat()
                }
            )
            points.append(point)
        
        logger.info(f"Prepared {len(points)} points for insertion")
        return points
    
    def insert_data(self, points: List[PointStruct], batch_size: int = 100) -> None:
        """
        Insert data into the collection in batches.
        
        Args:
            points: List of PointStruct objects
            batch_size: Number of points to insert per batch
        """
        try:
            total_points = len(points)
            logger.info(f"Inserting {total_points} points in batches of {batch_size}")
            
            for i in range(0, total_points, batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                logger.info(f"Inserted batch {i//batch_size + 1}/{(total_points + batch_size - 1)//batch_size}")
            
            logger.info("Data insertion completed successfully")
            
        except Exception as e:
            logger.error(f"Error inserting data: {e}")
            raise
    
    def search_properties(self, 
                         query: str, 
                         limit: int = 10, 
                         city: Optional[str] = None,
                         min_rating: Optional[float] = None,
                         pet_friendly: Optional[bool] = None,
                         bedrooms: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for properties using semantic similarity and filters.
        
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
            # Generate query embedding
            query_embedding = self.model.encode([query])[0].tolist()
            
            # Build filter
            filter_conditions = []
            
            if city:
                filter_conditions.append(FieldCondition(key="city", match=MatchValue(value=city)))
            
            if min_rating is not None:
                filter_conditions.append(FieldCondition(key="rating", range=models.Range(gte=min_rating)))
            
            if pet_friendly is not None:
                filter_conditions.append(FieldCondition(key="pet_friendly", match=MatchValue(value=pet_friendly)))
            
            if bedrooms is not None:
                filter_conditions.append(FieldCondition(key="bedrooms", match=MatchValue(value=bedrooms)))
            
            search_filter = Filter(must=filter_conditions) if filter_conditions else None
            
            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter=search_filter,
                with_payload=True
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "score": result.score,
                    "property_id": result.payload.get("property_id"),
                    "property_name": result.payload.get("property_name"),
                    "city": result.payload.get("city"),
                    "rating": result.payload.get("rating"),
                    "description": result.payload.get("description"),
                    "amenities": result.payload.get("amenities", []),
                    "pet_friendly": result.payload.get("pet_friendly"),
                    "bedrooms": result.payload.get("bedrooms"),
                    "source_url": result.payload.get("source_url"),
                    "image_url": result.payload.get("image_url")
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching properties: {e}")
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.
        
        Returns:
            Dictionary with collection information
        """
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": info.name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "segments_count": info.segments_count,
                "config": {
                    "vector_size": info.config.params.vectors.size,
                    "distance": info.config.params.vectors.distance,
                    "on_disk": info.config.params.vectors.on_disk
                }
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            raise

def main():
    """Main function to set up the vector database."""
    # Load environment variables from .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # python-dotenv not installed, continue without it
    
    # Check for environment variables for Qdrant Cloud
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    use_cloud = bool(qdrant_url and qdrant_api_key)
    
    if use_cloud:
        logger.info("Using Qdrant Cloud configuration")
        vdb = PremiereSuitesVectorDB(
            qdrant_url=qdrant_url,
            qdrant_api_key=qdrant_api_key,
            use_cloud=True
        )
    else:
        logger.info("Using local Qdrant configuration")
        vdb = PremiereSuitesVectorDB()
    
    try:
        # Create collection
        vdb.create_collection(recreate=True)
        
        # Load data
        properties = vdb.load_data_from_jsonl("premiere_suites_data.jsonl")
        
        if not properties:
            logger.error("No properties found in the data file")
            return
        
        # Prepare points
        points = vdb.prepare_points(properties)
        
        # Insert data
        vdb.insert_data(points)
        
        # Get collection info
        info = vdb.get_collection_info()
        logger.info(f"Collection info: {info}")
        
        # Test search
        logger.info("Testing search functionality...")
        results = vdb.search_properties(
            query="luxury apartment with pool and gym",
            limit=5,
            min_rating=4.0
        )
        
        logger.info("Search results:")
        for i, result in enumerate(results, 1):
            logger.info(f"{i}. {result['property_name']} ({result['city']}) - Rating: {result['rating']} - Score: {result['score']:.4f}")
        
        logger.info("Vector database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()
