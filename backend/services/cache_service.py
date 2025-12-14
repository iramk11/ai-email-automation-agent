"""
Caching service for performance optimization.
"""
from functools import wraps
from cachetools import TTLCache
from typing import Callable, Any
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """Service for caching frequently accessed data."""
    
    def __init__(self, maxsize: int = 1000, ttl: int = 3600):
        """
        Initialize cache service.
        
        Args:
            maxsize: Maximum number of items in cache
            ttl: Time-to-live in seconds (default: 1 hour)
        """
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        logger.info(f"Initialized cache with maxsize={maxsize}, ttl={ttl}s")
    
    def get(self, key: str) -> Any:
        """Get value from cache."""
        return self.cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        self.cache[key] = value
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def stats(self) -> dict:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "maxsize": self.cache.maxsize,
            "ttl": self.cache.ttl
        }


# Global cache instance
_embedding_cache = CacheService(maxsize=500, ttl=7200)  # 2 hours for embeddings
_faq_cache = CacheService(maxsize=200, ttl=1800)  # 30 minutes for FAQs


def cached_embedding(func: Callable) -> Callable:
    """Decorator for caching embedding results."""
    @wraps(func)
    def wrapper(self, text: str, *args, **kwargs):
        # Create cache key from text
        cache_key = hashlib.md5(text.encode()).hexdigest()
        
        # Check cache
        cached_result = _embedding_cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache hit for embedding: {text[:50]}...")
            return cached_result
        
        # Compute and cache
        result = func(self, text, *args, **kwargs)
        _embedding_cache.set(cache_key, result)
        logger.debug(f"Cached embedding: {text[:50]}...")
        return result
    
    return wrapper


def cached_search(func: Callable) -> Callable:
    """Decorator for caching search results."""
    @wraps(func)
    def wrapper(self, query_vector, *args, **kwargs):
        # Create cache key from query vector (first 10 values as hash)
        vector_str = json.dumps(query_vector[:10] if len(query_vector) >= 10 else query_vector)
        cache_key = hashlib.md5(vector_str.encode()).hexdigest()
        
        # Check cache
        cached_result = _faq_cache.get(cache_key)
        if cached_result is not None:
            logger.debug("Cache hit for search query")
            return cached_result
        
        # Compute and cache
        result = func(self, query_vector, *args, **kwargs)
        _faq_cache.set(cache_key, result)
        logger.debug("Cached search result")
        return result
    
    return wrapper

