"""
Unit tests for EmbeddingService.
"""
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from backend.services.embedding_service import EmbeddingService


class TestEmbeddingService:
    """Test cases for EmbeddingService."""
    
    def test_init(self):
        """Test service initialization."""
        service = EmbeddingService()
        assert service.model is not None
        assert service.model_name == "all-MiniLM-L6-v2"
    
    def test_encode(self):
        """Test text encoding."""
        service = EmbeddingService()
        text = "Hello world"
        embedding = service.encode(text)
        
        # EmbeddingService.encode() returns List[float], not numpy array
        assert isinstance(embedding, list)
        assert len(embedding) == 384
        assert all(isinstance(x, (float, np.floating)) for x in embedding)
    
    def test_encode_batch(self):
        """Test batch encoding."""
        service = EmbeddingService()
        texts = ["Hello", "World", "Test"]
        embeddings = service.encode_batch(texts)
        
        assert len(embeddings) == 3
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) == 384 for emb in embeddings)
    
    def test_encode_empty_string(self):
        """Test encoding empty string."""
        service = EmbeddingService()
        embedding = service.encode("")
        assert isinstance(embedding, list)
        assert len(embedding) == 384
    
    def test_encode_error_handling(self):
        """Test error handling in encode."""
        service = EmbeddingService()
        # Should handle None gracefully or raise appropriate error
        with pytest.raises((TypeError, AttributeError)):
            service.encode(None)

