"""
Embedding service for converting text to vectors.
"""
from sentence_transformers import SentenceTransformer
from typing import List
import logging
from backend.services.cache_service import cached_embedding

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for text embedding using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding service.
        
        Args:
            model_name: Name of the sentence-transformer model
        """
        self.model_name = model_name
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Loaded embedding model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    @cached_embedding
    def encode(self, text: str) -> List[float]:
        """
        Encode a single text into a vector.
        Uses caching to avoid recomputing embeddings for the same text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            embedding = self.model.encode([text], show_progress_bar=False)[0]
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Encoding failed: {e}")
            raise
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Encode multiple texts into vectors.
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.model.encode(texts, show_progress_bar=False)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Batch encoding failed: {e}")
            raise
    
    def get_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            Dimension size
        """
        return self.model.get_sentence_embedding_dimension()

