"""
Optimized API Utilities and Middleware

Features:
1. Response caching
2. Compression (gzip/brotli)
3. Rate limiting
4. Performance monitoring
5. Database connection pooling
"""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZIPMiddleware
from functools import wraps
import time
import logging
import gzip
import json
from typing import Callable, Any, Dict, Optional
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


# ==================== RESPONSE CACHING ====================

class ResponseCache:
    """
    In-memory response caching with TTL.
    For production, use Redis instead.
    """
    
    def __init__(self, ttl: int = 300):
        """
        Initialize response cache.
        
        Args:
            ttl: Time to live in seconds (default: 5 minutes)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached response if not expired."""
        if key in self.cache:
            cached_data = self.cache[key]
            if time.time() - cached_data['timestamp'] < self.ttl:
                logger.debug(f"✅ Cache HIT: {key}")
                return cached_data['data']
            else:
                # Expired, remove from cache
                del self.cache[key]
                logger.debug(f"⏱️  Cache EXPIRED: {key}")
        
        logger.debug(f"❌ Cache MISS: {key}")
        return None
    
    def set(self, key: str, data: Any):
        """Set cached response with current timestamp."""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
        logger.debug(f"💾 Cache SET: {key}")
    
    def invalidate(self, pattern: Optional[str] = None):
        """
        Invalidate cache entries.
        
        Args:
            pattern: If provided, only invalidate keys containing this pattern.
                     If None, clear entire cache.
        """
        if pattern is None:
            self.cache.clear()
            logger.info("🔄 Cache cleared (all)")
        else:
            keys_to_delete = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self.cache[key]
            logger.info(f"🔄 Cache cleared ({len(keys_to_delete)} entries matching '{pattern}')")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self.cache)
        total_size_bytes = sum(
            len(json.dumps(v['data']).encode('utf-8')) 
            for v in self.cache.values()
        )
        
        return {
            'total_entries': total_entries,
            'total_size_mb': round(total_size_bytes / 1024 / 1024, 2),
            'ttl_seconds': self.ttl
        }


# Global cache instance
response_cache = ResponseCache(ttl=300)  # 5 minutes default


def cached_response(ttl: int = 300, cache_key_func: Optional[Callable] = None):
    """
    Decorator to cache endpoint responses.
    
    Args:
        ttl: Time to live in seconds
        cache_key_func: Optional function to generate custom cache key
    
    Example:
        @app.get("/api/signals")
        @cached_response(ttl=60)
        async def get_signals():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                # Default: use function name + args
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            cached = response_cache.get(cache_key)
            if cached is not None:
                return cached
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            response_cache.set(cache_key, result)
            
            return result
        
        return wrapper
    return decorator


# ==================== RATE LIMITING ====================

class RateLimiter:
    """
    Simple in-memory rate limiter.
    For production, use Redis-based rate limiting.
    """
    
    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests allowed per minute
        """
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """
        Check if request is allowed for client.
        
        Args:
            client_id: Client identifier (e.g., IP address)
        
        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        minute_ago = now - 60
        
        # Clean up old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.requests_per_minute:
            logger.warning(f"⚠️  Rate limit exceeded for {client_id}")
            return False
        
        # Add current request
        self.requests[client_id].append(now)
        return True
    
    def get_stats(self, client_id: str) -> Dict[str, Any]:
        """Get rate limit stats for client."""
        now = time.time()
        minute_ago = now - 60
        
        recent_requests = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        return {
            'requests_last_minute': len(recent_requests),
            'limit': self.requests_per_minute,
            'remaining': max(0, self.requests_per_minute - len(recent_requests))
        }


# Global rate limiter
rate_limiter = RateLimiter(requests_per_minute=60)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce rate limiting."""
    
    async def dispatch(self, request: Request, call_next):
        # Extract client identifier (IP address)
        client_ip = request.client.host
        
        # Check rate limit
        if not rate_limiter.is_allowed(client_ip):
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "limit": rate_limiter.requests_per_minute
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        stats = rate_limiter.get_stats(client_ip)
        response.headers["X-RateLimit-Limit"] = str(stats['limit'])
        response.headers["X-RateLimit-Remaining"] = str(stats['remaining'])
        
        return response


# ==================== PERFORMANCE MONITORING ====================

class PerformanceMonitor:
    """Track API performance metrics."""
    
    def __init__(self):
        self.metrics: Dict[str, list] = defaultdict(list)
        self.max_history = 1000  # Keep last 1000 requests per endpoint
    
    def record(self, endpoint: str, duration: float, status_code: int):
        """
        Record request metrics.
        
        Args:
            endpoint: API endpoint path
            duration: Request duration in seconds
            status_code: HTTP status code
        """
        self.metrics[endpoint].append({
            'duration': duration,
            'status_code': status_code,
            'timestamp': time.time()
        })
        
        # Keep only recent history
        if len(self.metrics[endpoint]) > self.max_history:
            self.metrics[endpoint] = self.metrics[endpoint][-self.max_history:]
    
    def get_stats(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance statistics.
        
        Args:
            endpoint: Specific endpoint or None for all endpoints
        
        Returns:
            Performance statistics
        """
        if endpoint:
            metrics = self.metrics.get(endpoint, [])
            if not metrics:
                return {}
            
            durations = [m['duration'] for m in metrics]
            return {
                'endpoint': endpoint,
                'total_requests': len(metrics),
                'avg_duration_ms': round(sum(durations) / len(durations) * 1000, 2),
                'min_duration_ms': round(min(durations) * 1000, 2),
                'max_duration_ms': round(max(durations) * 1000, 2),
                'p95_duration_ms': round(sorted(durations)[int(len(durations) * 0.95)] * 1000, 2) if len(durations) > 20 else 0
            }
        else:
            # Stats for all endpoints
            all_stats = {}
            for ep in self.metrics.keys():
                all_stats[ep] = self.get_stats(ep)
            return all_stats


# Global performance monitor
performance_monitor = PerformanceMonitor()


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to track API performance."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Record metrics
        performance_monitor.record(
            endpoint=request.url.path,
            duration=duration,
            status_code=response.status_code
        )
        
        # Add performance header
        response.headers["X-Response-Time"] = f"{duration*1000:.2f}ms"
        
        # Log slow requests (> 1 second)
        if duration > 1.0:
            logger.warning(
                f"⚠️  Slow request: {request.method} {request.url.path} "
                f"took {duration*1000:.0f}ms"
            )
        
        return response


# ==================== RESPONSE COMPRESSION ====================

def compress_json_response(data: Any, compression: str = "gzip") -> bytes:
    """
    Compress JSON response for faster transmission.
    
    Args:
        data: Data to compress (will be JSON-serialized)
        compression: Compression algorithm ('gzip' or 'brotli')
    
    Returns:
        Compressed bytes
    """
    json_str = json.dumps(data)
    json_bytes = json_str.encode('utf-8')
    
    if compression == "gzip":
        return gzip.compress(json_bytes, compresslevel=6)
    elif compression == "brotli":
        try:
            import brotli
            return brotli.compress(json_bytes, quality=6)
        except ImportError:
            logger.warning("Brotli not installed, falling back to gzip")
            return gzip.compress(json_bytes, compresslevel=6)
    else:
        return json_bytes


# ==================== DATABASE CONNECTION POOLING ====================

def get_db_config(database_url: str) -> Dict[str, Any]:
    """
    Get optimized database configuration based on database type.
    
    Args:
        database_url: Database connection URL
    
    Returns:
        Dictionary of engine configuration parameters
    """
    if 'postgresql' in database_url:
        return {
            'pool_size': 20,              # Number of persistent connections
            'max_overflow': 10,           # Additional connections when pool is full
            'pool_recycle': 3600,         # Recycle connections after 1 hour
            'pool_pre_ping': True,        # Test connections before using
            'pool_timeout': 30,           # Timeout waiting for connection
            'echo': False,                # Don't log all SQL (performance)
            'echo_pool': False,           # Don't log pool checkouts
            'connect_args': {
                'connect_timeout': 10,
                'application_name': 'AlphaForge'
            }
        }
    else:  # SQLite
        return {
            'connect_args': {
                'check_same_thread': False,
                'timeout': 30
            },
            'pool_size': 5,
            'max_overflow': 10,
            'pool_recycle': 3600
        }


# ==================== UTILITY FUNCTIONS ====================

def create_optimized_response(
    data: Any,
    compress: bool = True,
    cache_key: Optional[str] = None
) -> JSONResponse:
    """
    Create optimized JSON response with optional compression and caching.
    
    Args:
        data: Data to return
        compress: Whether to compress response
        cache_key: Optional cache key to store response
    
    Returns:
        JSONResponse with optimizations applied
    """
    # Cache if key provided
    if cache_key:
        response_cache.set(cache_key, data)
    
    # Create response
    if compress and isinstance(data, (dict, list)):
        # Add metadata
        response_data = {
            'success': True,
            'data': data,
            'timestamp': datetime.utcnow().isoformat(),
            'compressed': True
        }
        return JSONResponse(
            content=response_data,
            headers={
                'Content-Encoding': 'gzip',
                'X-Compressed': 'true'
            }
        )
    else:
        return JSONResponse(content=data)


def paginate_results(
    items: list,
    page: int = 1,
    page_size: int = 50,
    max_page_size: int = 100
) -> Dict[str, Any]:
    """
    Paginate results with metadata.
    
    Args:
        items: List of items to paginate
        page: Page number (1-indexed)
        page_size: Items per page
        max_page_size: Maximum allowed page size
    
    Returns:
        Paginated response with metadata
    """
    # Enforce limits
    page = max(1, page)
    page_size = min(page_size, max_page_size)
    
    # Calculate pagination
    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    # Slice items
    paginated_items = items[start_idx:end_idx]
    
    return {
        'items': paginated_items,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total_items': total_items,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }


# ==================== MONITORING ENDPOINTS ====================

def get_system_metrics() -> Dict[str, Any]:
    """Get comprehensive system metrics."""
    try:
        import psutil
        
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # Cache stats
        cache_stats = response_cache.get_stats()
        
        # Performance stats
        perf_stats = performance_monitor.get_stats()
        
        return {
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_mb': round(memory.available / 1024 / 1024, 2)
            },
            'cache': cache_stats,
            'performance': perf_stats,
            'timestamp': datetime.utcnow().isoformat()
        }
    except ImportError:
        logger.warning("psutil not installed, system metrics unavailable")
        return {
            'cache': response_cache.get_stats(),
            'performance': performance_monitor.get_stats(),
            'timestamp': datetime.utcnow().isoformat()
        }
