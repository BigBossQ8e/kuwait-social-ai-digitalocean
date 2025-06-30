"""
Enhanced caching service for Kuwait Social AI
Implements granular caching for frequently accessed data
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import redis
from functools import wraps
import logging
from flask import current_app
import pickle
import zlib

logger = logging.getLogger(__name__)


class CacheService:
    """Enhanced caching service with multiple storage backends"""
    
    def __init__(self, redis_url: str = None):
        """Initialize cache service"""
        self.redis_url = redis_url or current_app.config.get('REDIS_URL', 'redis://localhost:6379')
        self._redis_client = None
        self._memory_cache = {}  # Fallback in-memory cache
        self.default_ttl = 3600  # 1 hour default
        
        # Cache prefixes for different data types
        self.prefixes = {
            'hashtags': 'ht:',
            'holidays': 'hd:',
            'prayer_times': 'pt:',
            'trending': 'tr:',
            'analytics': 'an:',
            'content': 'ct:',
            'translations': 'tl:',
            'user_data': 'ud:'
        }
    
    @property
    def redis_client(self):
        """Lazy loading of Redis client"""
        if self._redis_client is None:
            try:
                self._redis_client = redis.from_url(
                    self.redis_url,
                    decode_responses=False,  # We'll handle encoding ourselves
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                # Test connection
                self._redis_client.ping()
                logger.info("Redis cache connected successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Falling back to memory cache.")
                self._redis_client = None
        
        return self._redis_client
    
    def _generate_key(self, prefix: str, key: str, **kwargs) -> str:
        """Generate cache key with prefix and optional parameters"""
        if kwargs:
            # Sort kwargs for consistent key generation
            params = "&".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
            key = f"{key}?{params}"
        
        # Hash long keys to avoid Redis key length limits
        if len(key) > 100:
            key_hash = hashlib.md5(key.encode()).hexdigest()
            key = f"{key[:50]}_{key_hash}"
        
        return f"{prefix}{key}"
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serialize data for storage"""
        try:
            # Use pickle for Python objects, compress for efficiency
            serialized = pickle.dumps(data)
            compressed = zlib.compress(serialized)
            return compressed
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            raise
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize data from storage"""
        try:
            decompressed = zlib.decompress(data)
            return pickle.loads(decompressed)
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            raise
    
    def set(self, category: str, key: str, value: Any, ttl: int = None, **kwargs) -> bool:
        """Set cache value"""
        cache_key = self._generate_key(self.prefixes.get(category, 'misc:'), key, **kwargs)
        ttl = ttl or self.default_ttl
        
        try:
            serialized_value = self._serialize_data(value)
            
            if self.redis_client:
                # Store in Redis
                result = self.redis_client.setex(cache_key, ttl, serialized_value)
                return bool(result)
            else:
                # Fallback to memory cache
                expiry = datetime.utcnow() + timedelta(seconds=ttl)
                self._memory_cache[cache_key] = {
                    'value': value,  # Store original value in memory cache
                    'expiry': expiry
                }
                return True
                
        except Exception as e:
            logger.error(f"Cache set error for key {cache_key}: {e}")
            return False
    
    def get(self, category: str, key: str, **kwargs) -> Optional[Any]:
        """Get cache value"""
        cache_key = self._generate_key(self.prefixes.get(category, 'misc:'), key, **kwargs)
        
        try:
            if self.redis_client:
                # Get from Redis
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    return self._deserialize_data(cached_data)
            else:
                # Get from memory cache
                cached_item = self._memory_cache.get(cache_key)
                if cached_item:
                    if datetime.utcnow() < cached_item['expiry']:
                        return cached_item['value']
                    else:
                        # Remove expired item
                        del self._memory_cache[cache_key]
            
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {cache_key}: {e}")
            return None
    
    def delete(self, category: str, key: str, **kwargs) -> bool:
        """Delete cache value"""
        cache_key = self._generate_key(self.prefixes.get(category, 'misc:'), key, **kwargs)
        
        try:
            if self.redis_client:
                result = self.redis_client.delete(cache_key)
                return bool(result)
            else:
                if cache_key in self._memory_cache:
                    del self._memory_cache[cache_key]
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Cache delete error for key {cache_key}: {e}")
            return False
    
    def clear_category(self, category: str) -> int:
        """Clear all cache entries for a category"""
        prefix = self.prefixes.get(category, 'misc:')
        
        try:
            if self.redis_client:
                # Use SCAN to find and delete keys with prefix
                keys = []
                for key in self.redis_client.scan_iter(match=f"{prefix}*"):
                    keys.append(key)
                
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            else:
                # Clear from memory cache
                keys_to_delete = [k for k in self._memory_cache.keys() if k.startswith(prefix)]
                for key in keys_to_delete:
                    del self._memory_cache[key]
                return len(keys_to_delete)
                
        except Exception as e:
            logger.error(f"Cache clear category error for {category}: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            'backend': 'redis' if self.redis_client else 'memory',
            'categories': {}
        }
        
        try:
            if self.redis_client:
                # Redis stats
                info = self.redis_client.info()
                stats.update({
                    'redis_connected': True,
                    'redis_memory_used': info.get('used_memory_human'),
                    'redis_total_keys': info.get('db0', {}).get('keys', 0)
                })
                
                # Count keys by category
                for category, prefix in self.prefixes.items():
                    key_count = len(list(self.redis_client.scan_iter(match=f"{prefix}*")))
                    stats['categories'][category] = key_count
            else:
                # Memory cache stats
                stats.update({
                    'redis_connected': False,
                    'memory_cache_size': len(self._memory_cache)
                })
                
                # Count by category
                for category, prefix in self.prefixes.items():
                    key_count = len([k for k in self._memory_cache.keys() if k.startswith(prefix)])
                    stats['categories'][category] = key_count
        
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            stats['error'] = str(e)
        
        return stats


# Global cache instance
cache_service = CacheService()


def cached(category: str, key_func=None, ttl: int = None, **cache_kwargs):
    """
    Decorator for caching function results
    
    Args:
        category: Cache category (e.g., 'hashtags', 'holidays')
        key_func: Function to generate cache key from function args
        ttl: Time to live in seconds
        **cache_kwargs: Additional cache key parameters
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation from function name and args
                arg_str = "_".join(str(arg) for arg in args[:3])  # Limit arg length
                kwarg_str = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items())[:3])
                cache_key = f"{func.__name__}_{arg_str}_{kwarg_str}"
            
            # Try to get from cache
            cached_result = cache_service.get(category, cache_key, **cache_kwargs)
            if cached_result is not None:
                logger.debug(f"Cache hit for {category}:{cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_service.set(category, cache_key, result, ttl, **cache_kwargs)
            logger.debug(f"Cache miss for {category}:{cache_key}, result cached")
            
            return result
        
        return wrapper
    return decorator


# Specific cache functions for Kuwait Social AI data
class KuwaitDataCache:
    """Kuwait-specific data caching"""
    
    @staticmethod
    @cached('hashtags', ttl=1800)  # 30 minutes
    def get_trending_hashtags(location: str = 'kuwait', platform: str = 'instagram'):
        """Cache trending hashtags"""
        # This would normally fetch from external API
        # Placeholder implementation
        return [
            '#Kuwait', '#الكويت', '#Q8', '#KuwaitNationalDay',
            '#RamadanKuwait', '#KuwaitBusiness', '#KuwaitFood'
        ]
    
    @staticmethod
    @cached('holidays', ttl=86400)  # 24 hours
    def get_kuwait_holidays(year: int):
        """Cache Kuwait holidays for the year"""
        # This would normally fetch from a holidays API
        holidays = [
            {'date': f'{year}-01-01', 'name': 'New Year', 'type': 'public'},
            {'date': f'{year}-02-25', 'name': 'National Day', 'type': 'national'},
            {'date': f'{year}-02-26', 'name': 'Liberation Day', 'type': 'national'},
            # Add more holidays based on Islamic calendar
        ]
        return holidays
    
    @staticmethod
    @cached('prayer_times', ttl=3600)  # 1 hour
    def get_prayer_times(date: str, city: str = 'kuwait'):
        """Cache prayer times for specific date and city"""
        # This would normally fetch from prayer times API
        # Placeholder implementation
        return {
            'fajr': '04:30',
            'dhuhr': '12:00',
            'asr': '15:30',
            'maghrib': '18:00',
            'isha': '19:30'
        }
    
    @staticmethod
    @cached('translations', ttl=604800)  # 7 days (translations don't change)
    def get_translation(text: str, source_lang: str = 'en', target_lang: str = 'ar'):
        """Cache translations"""
        # This would normally call translation service
        # Cache key includes both text hash and language pair
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        cache_key = f"{text_hash}_{source_lang}_{target_lang}"
        return None  # Placeholder - actual translation would be cached
    
    @staticmethod
    @cached('content', ttl=1800)  # 30 minutes
    def get_content_suggestions(industry: str, tone: str = 'professional'):
        """Cache content suggestions by industry"""
        # This would normally generate or fetch content suggestions
        return {
            'topics': ['Product Launch', 'Customer Story', 'Behind the Scenes'],
            'templates': ['announcement', 'testimonial', 'educational']
        }


# Cache warming functions
def warm_cache():
    """Warm up cache with frequently accessed data"""
    logger.info("Starting cache warming...")
    
    try:
        # Warm trending hashtags
        KuwaitDataCache.get_trending_hashtags()
        KuwaitDataCache.get_trending_hashtags(platform='snapchat')
        
        # Warm current year holidays
        current_year = datetime.utcnow().year
        KuwaitDataCache.get_kuwait_holidays(current_year)
        
        # Warm today's prayer times
        today = datetime.utcnow().strftime('%Y-%m-%d')
        KuwaitDataCache.get_prayer_times(today)
        
        # Warm content suggestions for common industries
        industries = ['restaurant', 'retail', 'services', 'healthcare']
        for industry in industries:
            KuwaitDataCache.get_content_suggestions(industry)
        
        logger.info("Cache warming completed successfully")
        
    except Exception as e:
        logger.error(f"Cache warming failed: {e}")


# Cache management utilities
def clear_expired_cache():
    """Clear expired entries from memory cache"""
    if not cache_service.redis_client:
        # Only needed for memory cache
        now = datetime.utcnow()
        expired_keys = [
            key for key, item in cache_service._memory_cache.items()
            if item['expiry'] < now
        ]
        
        for key in expired_keys:
            del cache_service._memory_cache[key]
        
        logger.info(f"Cleared {len(expired_keys)} expired cache entries")


def get_cache_health() -> Dict[str, Any]:
    """Get cache health status"""
    health = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'issues': []
    }
    
    try:
        stats = cache_service.get_stats()
        health['stats'] = stats
        
        if not stats.get('redis_connected', False):
            health['status'] = 'degraded'
            health['issues'].append('Redis not connected, using memory fallback')
        
        # Check if cache is being used
        total_keys = sum(stats.get('categories', {}).values())
        if total_keys == 0:
            health['issues'].append('No cached data found - cache may need warming')
        
    except Exception as e:
        health['status'] = 'unhealthy'
        health['issues'].append(f'Cache health check failed: {str(e)}')
    
    return health