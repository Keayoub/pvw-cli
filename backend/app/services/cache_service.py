# Enhanced Purview CLI v2.0 - Redis Cache Service
# Provides caching functionality for improved performance

import json
import redis
import asyncio
from typing import Optional, Any, Dict, List
from datetime import datetime, timedelta
import pickle
import logging
from functools import wraps

from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisCache:
    """Redis cache service for caching frequently accessed data"""
    
    def __init__(self):
        self.redis_client = None
        self.is_connected = False
        
    async def connect(self):
        """Connect to Redis server"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                health_check_interval=30
            )
            
            # Test connection
            await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.ping
            )
            
            self.is_connected = True
            logger.info("Connected to Redis cache")
            
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            self.is_connected = False
            
    async def disconnect(self):
        """Disconnect from Redis server"""
        if self.redis_client:
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.close
                )
                logger.info("Disconnected from Redis cache")
            except Exception as e:
                logger.error(f"Error disconnecting from Redis: {e}")
                
        self.is_connected = False
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.is_connected:
            return None
            
        try:
            value = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.get, key
            )
            
            if value:
                # Try to deserialize JSON first, then pickle
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    try:
                        return pickle.loads(value.encode('latin-1'))
                    except Exception:
                        return value
                        
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            
        return None
        
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with optional TTL"""
        if not self.is_connected:
            return False
            
        try:
            ttl = ttl or settings.REDIS_CACHE_TTL
            
            # Try to serialize as JSON first, then pickle
            try:
                serialized_value = json.dumps(value, default=str)
            except (TypeError, ValueError):
                serialized_value = pickle.dumps(value).decode('latin-1')
                
            await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.setex, key, ttl, serialized_value
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
            
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.is_connected:
            return False
            
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.delete, key
            )
            return True
            
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
            
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.is_connected:
            return False
            
        try:
            exists = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.exists, key
            )
            return bool(exists)
            
        except Exception as e:
            logger.error(f"Error checking cache key existence {key}: {e}")
            return False
            
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.is_connected:
            return 0
            
        try:
            keys = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.keys, pattern
            )
            
            if keys:
                await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.delete, *keys
                )
                
            return len(keys)
            
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
            return 0
            
    async def increment(self, key: str, amount: int = 1, ttl: int = None) -> Optional[int]:
        """Increment counter in cache"""
        if not self.is_connected:
            return None
            
        try:
            # Use pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            pipe.incr(key, amount)
            
            if ttl:
                pipe.expire(key, ttl)
                
            result = await asyncio.get_event_loop().run_in_executor(
                None, pipe.execute
            )
            
            return result[0]
            
        except Exception as e:
            logger.error(f"Error incrementing cache key {key}: {e}")
            return None
            
    async def get_hash(self, key: str, field: str = None) -> Optional[Any]:
        """Get hash field value or entire hash"""
        if not self.is_connected:
            return None
            
        try:
            if field:
                value = await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.hget, key, field
                )
                return value
            else:
                hash_data = await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.hgetall, key
                )
                return hash_data if hash_data else None
                
        except Exception as e:
            logger.error(f"Error getting hash {key}: {e}")
            return None
            
    async def set_hash(self, key: str, hash_data: Dict[str, Any], ttl: int = None) -> bool:
        """Set hash data with optional TTL"""
        if not self.is_connected:
            return False
            
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.hset, key, mapping=hash_data
            )
            
            if ttl:
                await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.expire, key, ttl
                )
                
            return True
            
        except Exception as e:
            logger.error(f"Error setting hash {key}: {e}")
            return False


class CacheService:
    """Main cache service interface that provides high-level caching operations"""
    
    def __init__(self):
        self.cache = RedisCache()
        
    async def initialize(self):
        """Initialize the cache service"""
        await self.cache.connect()
        
    async def shutdown(self):
        """Shutdown the cache service"""
        await self.cache.disconnect()
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        return await self.cache.get(key)
        
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with optional TTL"""
        return await self.cache.set(key, value, ttl)
        
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        return await self.cache.delete(key)
        
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        return await self.cache.exists(key)
        
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        return await self.cache.clear_pattern(pattern)
        
    async def get_hash(self, key: str, field: str = None) -> Optional[Any]:
        """Get hash field value or entire hash"""
        return await self.cache.get_hash(key, field)
        
    async def set_hash(self, key: str, hash_data: Dict[str, Any], ttl: int = None) -> bool:
        """Set hash data with optional TTL"""
        return await self.cache.set_hash(key, hash_data, ttl)
        
    @property
    def is_connected(self) -> bool:
        """Check if cache is connected"""
        return self.cache.is_connected


# Create global cache instance
cache = RedisCache()

# Cache decorators
def cache_result(key_prefix: str, ttl: int = None):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{key_prefix}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
                
            # Execute function and cache result
            logger.debug(f"Cache miss for {cache_key}")
            result = await func(*args, **kwargs)
            
            if result is not None:
                await cache.set(cache_key, result, ttl or settings.REDIS_CACHE_TTL)
                
            return result
            
        return wrapper
    return decorator

def invalidate_cache_pattern(pattern: str):
    """Decorator to invalidate cache patterns after function execution"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            await cache.clear_pattern(pattern)
            return result
        return wrapper
    return decorator

# Cache key generators
class CacheKeys:
    """Cache key generators for different data types"""
    
    @staticmethod
    def user_profile(user_id: str) -> str:
        return f"user:profile:{user_id}"
        
    @staticmethod
    def entity_details(entity_id: str) -> str:
        return f"entity:details:{entity_id}"
        
    @staticmethod
    def scan_results(scan_id: str) -> str:
        return f"scan:results:{scan_id}"
        
    @staticmethod
    def lineage_graph(entity_id: str) -> str:
        return f"lineage:graph:{entity_id}"
        
    @staticmethod
    def analytics_metrics(metric_type: str, timeframe: str) -> str:
        return f"analytics:metrics:{metric_type}:{timeframe}"
        
    @staticmethod
    def governance_policies(organization_id: str) -> str:
        return f"governance:policies:{organization_id}"
        
    @staticmethod
    def search_results(query: str, filters: str) -> str:
        query_hash = hash(f"{query}:{filters}")
        return f"search:results:{query_hash}"
        
    @staticmethod
    def classification_definitions() -> str:
        return "classification:definitions"
        
    @staticmethod
    def data_source_config(source_id: str) -> str:
        return f"datasource:config:{source_id}"

# Cache warming functions
class CacheWarmer:
    """Functions to pre-populate cache with frequently accessed data"""
    
    @staticmethod
    async def warm_classification_definitions():
        """Pre-cache classification definitions"""
        try:
            # This would typically fetch from database
            # For now, using mock data
            definitions = [
                {"name": "PII", "description": "Personally Identifiable Information"},
                {"name": "Financial", "description": "Financial data"},
                {"name": "Confidential", "description": "Confidential business data"}
            ]
            
            await cache.set(
                CacheKeys.classification_definitions(),
                definitions,
                ttl=3600  # 1 hour
            )
            
            logger.info("Warmed classification definitions cache")
            
        except Exception as e:
            logger.error(f"Error warming classification definitions cache: {e}")
            
    @staticmethod
    async def warm_user_sessions():
        """Pre-cache active user sessions"""
        try:
            # This would typically fetch from database or session store
            # For now, using mock data
            sessions = {
                "active_users": 150,
                "last_updated": datetime.now().isoformat()
            }
            
            await cache.set(
                "user:sessions:stats",
                sessions,
                ttl=300  # 5 minutes
            )
            
            logger.info("Warmed user sessions cache")
            
        except Exception as e:
            logger.error(f"Error warming user sessions cache: {e}")

# Initialize cache warmer
cache_warmer = CacheWarmer()

async def initialize_cache():
    """Initialize cache service and warm frequently accessed data"""
    await cache.connect()
    
    if cache.is_connected:
        # Warm frequently accessed data
        await cache_warmer.warm_classification_definitions()
        logger.info("Cache service initialized successfully")
    else:
        logger.warning("Cache service failed to initialize")

async def cleanup_cache():
    """Cleanup cache service"""
    await cache.disconnect()
    logger.info("Cache service cleanup completed")
