"""
Unit tests for CacheService.
"""
import pytest
import time
from backend.services.cache_service import CacheService, _embedding_cache, _faq_cache


class TestCacheService:
    """Test cases for CacheService."""
    
    def test_init(self):
        """Test cache initialization."""
        cache = CacheService(maxsize=100, ttl=60)
        assert cache.cache.maxsize == 100
        assert cache.cache.ttl == 60
    
    def test_set_and_get(self):
        """Test setting and getting values."""
        cache = CacheService(maxsize=10, ttl=60)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
    
    def test_cache_expiration(self):
        """Test cache expiration."""
        cache = CacheService(maxsize=10, ttl=1)  # 1 second TTL
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        time.sleep(2)  # Wait for expiration
        assert cache.get("key1") is None
    
    def test_cache_clear(self):
        """Test clearing cache."""
        cache = CacheService(maxsize=10, ttl=60)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        assert len(cache.cache) == 2
        
        cache.clear()
        assert len(cache.cache) == 0
    
    def test_cache_stats(self):
        """Test cache statistics."""
        cache = CacheService(maxsize=100, ttl=60)
        cache.set("key1", "value1")
        stats = cache.stats()
        
        assert "size" in stats
        assert "maxsize" in stats
        assert "ttl" in stats
        assert stats["size"] == 1
        assert stats["maxsize"] == 100
    
    def test_cache_maxsize(self):
        """Test cache respects maxsize."""
        cache = CacheService(maxsize=2, ttl=60)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict oldest
        
        # Cache should only have 2 items
        assert len(cache.cache) <= 2

