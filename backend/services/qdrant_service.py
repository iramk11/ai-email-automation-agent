"""
Qdrant vector database service for semantic search.
"""
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import logging

logger = logging.getLogger(__name__)


class QdrantService:
    """Service for interacting with Qdrant vector database."""
    
    def __init__(self, data_path: str, collection_name: str):
        """
        Initialize Qdrant client.
        
        Args:
            data_path: Path to Qdrant data directory
            collection_name: Name of the collection to use
        """
        self.collection_name = collection_name
        try:
            self.client = QdrantClient(path=data_path)
            logger.info(f"Connected to Qdrant at {data_path}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise
    
    def search(self, query_vector: List[float], limit: int = 6) -> List[Dict[str, Any]]:
        """
        Perform semantic search in the vector database.
        
        Args:
            query_vector: Embedded query vector
            limit: Maximum number of results to return
            
        Returns:
            List of search results with scores and payloads
        """
        try:
            # Try newer API first
            if hasattr(self.client, 'query_points'):
                results = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    limit=limit
                )
                points = results.points
            else:
                # Fallback to older API
                points = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=limit
                )
            
            hits = []
            for point in points:
                hits.append({
                    "score": point.score,
                    "payload": point.payload
                })
            
            logger.info(f"Found {len(hits)} results from Qdrant")
            return hits
            
        except Exception as e:
            logger.error(f"Qdrant search failed: {e}")
            return []
    
    def separate_hits(self, hits: List[Dict[str, Any]]) -> tuple:
        """
        Separate search results into FAQ and graph node hits.
        
        Args:
            hits: List of search results
            
        Returns:
            Tuple of (faq_hits, graph_hits)
        """
        faq_hits = []
        graph_hits = []
        
        for hit in hits:
            payload = hit["payload"]
            score = hit["score"]
            
            if payload.get("type") == "faq":
                faq_hits.append({
                    "score": score,
                    "question": payload.get("question", ""),
                    "answer": payload.get("answer", ""),
                    "faq_id": payload.get("faq_id", 0)
                })
            elif payload.get("type") == "graph_node":
                graph_hits.append({
                    "score": score,
                    "node_name": payload.get("node_name", ""),
                    "node_type": payload.get("node_type", "unknown"),
                    "neighbors": payload.get("neighbors", [])
                })
        
        return faq_hits, graph_hits
    
    def health_check(self) -> bool:
        """
        Check if Qdrant service is healthy.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            collections = self.client.get_collections()
            return self.collection_name in [c.name for c in collections.collections]
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False

