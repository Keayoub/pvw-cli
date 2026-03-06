"""
Read-Query Caching System
Optional in-memory cache with TTL for read-only operations (search, list, read).
Reduces API calls for repeated queries in a single session.
"""

import time
from typing import Dict, Any, Optional, Callable, Tuple
from threading import Lock
from hashlib import md5
import json


class CacheEntry:
    """Individual cache entry with TTL expiry"""
    
    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.ttl_seconds = ttl_seconds
        self.created_at = time.time()
    
    def is_expired(self) -> bool:
        """Check if this cache entry has expired"""
        if self.ttl_seconds <= 0:
            return False  # No TTL = never expires
        return (time.time() - self.created_at) > self.ttl_seconds


class ReadQueryCache:
    """
    In-memory cache for read-only queries with optional TTL.
    
    Thread-safe caching for search, list, and read operations.
    Cache key includes method name and normalized parameters.
    Excludes mutations (writes, deletes, updates).
    """
    
    def __init__(self, default_ttl_seconds: int = 60):
        """
        Initialize cache with default TTL.
        
        Args:
            default_ttl_seconds: Default time-to-live for cache entries (0 = no expiry)
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self.default_ttl_seconds = default_ttl_seconds
        self._hits = 0
        self._misses = 0
    
    def _make_cache_key(self, method_name: str, params: Dict[str, Any]) -> str:
        """
        Generate cache key from method name and parameters.
        
        Includes filter parameters but excludes auth/internal fields.
        """
        # Normalize params: exclude auth fields, sort keys
        normalized = {}
        exclude_keys = {"--token", "--profile", "--debug", "--endpoint", "--account-name"}
        for k, v in params.items():
            if k not in exclude_keys:
                normalized[k] = v
        
        # Create deterministic hash
        key_str = f"{method_name}:{json.dumps(normalized, sort_keys=True, default=str)}"
        return md5(key_str.encode()).hexdigest()
    
    def get(
        self,
        method_name: str,
        params: Dict[str, Any],
        fetch_fn: Optional[Callable] = None,
    ) -> Optional[Any]:
        """
        Get cached result or fetch fresh data.
        
        Args:
            method_name: Name of the method being cached (e.g., "glossaryReadTerms")
            params: Parameters passed to the method
            fetch_fn: Optional function to call if cache miss. 
                      Should match method signature: fetch_fn(params) -> result
        
        Returns:
            Cached result or newly fetched result, or None
        """
        cache_key = self._make_cache_key(method_name, params)
        
        with self._lock:
            if cache_key in self._cache:
                entry = self._cache[cache_key]
                if not entry.is_expired():
                    self._hits += 1
                    return entry.value
                else:
                    del self._cache[cache_key]
        
        # Cache miss
        self._misses += 1
        if fetch_fn:
            result = fetch_fn(params)
            self.put(method_name, params, result)
            return result
        
        return None
    
    def put(
        self,
        method_name: str,
        params: Dict[str, Any],
        value: Any,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """
        Store a result in cache.
        
        Args:
            method_name: Name of the method being cached
            params: Parameters for this result
            value: Result to cache
            ttl_seconds: Time-to-live for this entry (None = use default)
        """
        cache_key = self._make_cache_key(method_name, params)
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds
        
        with self._lock:
            self._cache[cache_key] = CacheEntry(value, ttl)
    
    def invalidate(self, method_name: Optional[str] = None) -> None:
        """
        Invalidate cache on mutations.
        
        Args:
            method_name: Specific method to invalidate (None = invalidate all)
        """
        with self._lock:
            if method_name is None:
                self._cache.clear()
            else:
                # Clear entries matching method prefix
                keys_to_delete = [k for k in self._cache.keys() if method_name in k]
                for key in keys_to_delete:
                    del self._cache[key]
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics for diagnostics"""
        with self._lock:
            total_entries = len(self._cache)
            active_entries = sum(1 for e in self._cache.values() if not e.is_expired())
            hit_rate = (
                self._hits / (self._hits + self._misses)
                if (self._hits + self._misses) > 0
                else 0
            )
            return {
                "total_entries": total_entries,
                "active_entries": active_entries,
                "expired_entries": total_entries - active_entries,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": f"{hit_rate:.1%}",
            }
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0


# Global cache instance
_global_query_cache = ReadQueryCache(default_ttl_seconds=60)


def get_read_query_cache() -> ReadQueryCache:
    """Get the global read-query cache instance"""
    return _global_query_cache
