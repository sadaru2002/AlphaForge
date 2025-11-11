"""
In-Memory Cache Manager for FastAPI
Implements intelligent caching for frequently accessed data
"""
from typing import Any, Optional, Dict, Callable
from datetime import datetime, timedelta
from functools import wraps
import asyncio
import hashlib
import json


class CacheEntry:
    """Represents a single cache entry with TTL"""
    
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.created_at = datetime.now()
        self.ttl = ttl  # Time to live in seconds
        self.hits = 0
        
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        if self.ttl is None:
            return False
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl)
    
    def get_age(self) -> int:
        """Get age of cache entry in seconds"""
        return int((datetime.now() - self.created_at).total_seconds())


class CacheManager:
    """
    In-memory cache manager with TTL and LRU eviction
    Thread-safe for async operations
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self._cache: Dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'sets': 0,
        }
    
    def _generate_key(self, key: str, **kwargs) -> str:
        """Generate cache key from string and kwargs"""
        if not kwargs:
            return key
        
        # Sort kwargs for consistent key generation
        sorted_kwargs = json.dumps(kwargs, sort_keys=True)
        hash_obj = hashlib.md5(sorted_kwargs.encode())
        return f"{key}:{hash_obj.hexdigest()}"
    
    async def get(self, key: str, **kwargs) -> Optional[Any]:
        """Get value from cache"""
        cache_key = self._generate_key(key, **kwargs)
        
        async with self._lock:
            entry = self._cache.get(cache_key)
            
            if entry is None:
                self._stats['misses'] += 1
                return None
            
            if entry.is_expired():
                del self._cache[cache_key]
                self._stats['misses'] += 1
                return None
            
            entry.hits += 1
            self._stats['hits'] += 1
            return entry.value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, **kwargs):
        """Set value in cache with optional TTL"""
        cache_key = self._generate_key(key, **kwargs)
        ttl = ttl if ttl is not None else self._default_ttl
        
        async with self._lock:
            # Check if we need to evict entries
            if len(self._cache) >= self._max_size and cache_key not in self._cache:
                await self._evict_lru()
            
            self._cache[cache_key] = CacheEntry(value, ttl)
            self._stats['sets'] += 1
    
    async def delete(self, key: str, **kwargs):
        """Delete value from cache"""
        cache_key = self._generate_key(key, **kwargs)
        
        async with self._lock:
            if cache_key in self._cache:
                del self._cache[cache_key]
    
    async def clear(self):
        """Clear all cache entries"""
        async with self._lock:
            self._cache.clear()
    
    async def _evict_lru(self):
        """Evict least recently used entry"""
        if not self._cache:
            return
        
        # Find entry with lowest hits and oldest age
        lru_key = min(
            self._cache.items(),
            key=lambda x: (x[1].hits, -x[1].get_age())
        )[0]
        
        del self._cache[lru_key]
        self._stats['evictions'] += 1
    
    async def cleanup_expired(self):
        """Remove all expired entries"""
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = (
            self._stats['hits'] / (self._stats['hits'] + self._stats['misses'])
            if (self._stats['hits'] + self._stats['misses']) > 0
            else 0
        )
        
        return {
            **self._stats,
            'size': len(self._cache),
            'max_size': self._max_size,
            'hit_rate': f"{hit_rate * 100:.2f}%",
        }
    
    def cache_result(self, ttl: Optional[int] = None, key_prefix: str = ""):
        """
        Decorator for caching function results
        
        Usage:
            @cache_manager.cache_result(ttl=60, key_prefix="signals")
            async def get_signals():
                # expensive operation
                return data
        """
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                func_name = f"{key_prefix}:{func.__name__}" if key_prefix else func.__name__
                
                # Try to get from cache
                cached = await self.get(func_name, args=str(args), kwargs=str(kwargs))
                if cached is not None:
                    return cached
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                await self.set(func_name, result, ttl, args=str(args), kwargs=str(kwargs))
                
                return result
            
            return wrapper
        return decorator


# Global cache instance
cache_manager = CacheManager(max_size=1000, default_ttl=300)  # 5 minutes default


# Background task to cleanup expired entries
async def cache_cleanup_task():
    """Background task to periodically clean up expired cache entries"""
    while True:
        await asyncio.sleep(60)  # Run every minute
        await cache_manager.cleanup_expired()
