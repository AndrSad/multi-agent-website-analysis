"""
Advanced caching system for production deployment.

This module provides multiple caching backends (memory, Redis, file) with
TTL support, cache invalidation, and performance monitoring.
"""

import time
import json
import pickle
import hashlib
import threading
from typing import Any, Dict, Optional, Union, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import logging
from abc import ABC, abstractmethod


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: datetime = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def touch(self):
        """Update access information."""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()


class CacheBackend(ABC):
    """Abstract base class for cache backends."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass
    
    @abstractmethod
    def size(self) -> int:
        """Get cache size."""
        pass
    
    @abstractmethod
    def keys(self) -> List[str]:
        """Get all cache keys."""
        pass


class MemoryCacheBackend(CacheBackend):
    """In-memory cache backend with LRU eviction."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, CacheEntry] = {}
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            
            # Check if expired
            if entry.is_expired():
                del self.cache[key]
                return None
            
            # Update access info
            entry.touch()
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        try:
            with self.lock:
                # Calculate expiration time
                expires_at = None
                if ttl is not None:
                    expires_at = datetime.utcnow() + timedelta(seconds=ttl)
                
                # Create cache entry
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_at=datetime.utcnow(),
                    expires_at=expires_at
                )
                
                # Evict if necessary
                if len(self.cache) >= self.max_size and key not in self.cache:
                    self._evict_lru()
                
                self.cache[key] = entry
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to set cache entry {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            return True
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        with self.lock:
            if key not in self.cache:
                return False
            
            entry = self.cache[key]
            if entry.is_expired():
                del self.cache[key]
                return False
            
            return True
    
    def size(self) -> int:
        """Get cache size."""
        with self.lock:
            # Remove expired entries
            expired_keys = [k for k, v in self.cache.items() if v.is_expired()]
            for key in expired_keys:
                del self.cache[key]
            
            return len(self.cache)
    
    def keys(self) -> List[str]:
        """Get all cache keys."""
        with self.lock:
            # Remove expired entries
            expired_keys = [k for k, v in self.cache.items() if v.is_expired()]
            for key in expired_keys:
                del self.cache[key]
            
            return list(self.cache.keys())
    
    def _evict_lru(self):
        """Evict least recently used entry."""
        if not self.cache:
            return
        
        # Find LRU entry
        lru_key = min(self.cache.keys(), 
                     key=lambda k: self.cache[k].last_accessed)
        del self.cache[lru_key]


class FileCacheBackend(CacheBackend):
    """File-based cache backend."""
    
    def __init__(self, cache_directory: str = "./cache"):
        self.cache_directory = Path(cache_directory)
        self.cache_directory.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
    
    def _get_file_path(self, key: str) -> Path:
        """Get file path for cache key."""
        # Hash key to avoid filesystem issues
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_directory / f"{key_hash}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            with self.lock:
                file_path = self._get_file_path(key)
                
                if not file_path.exists():
                    return None
                
                with open(file_path, 'rb') as f:
                    entry = pickle.load(f)
                
                # Check if expired
                if entry.is_expired():
                    file_path.unlink()
                    return None
                
                # Update access info
                entry.touch()
                
                # Save updated entry
                with open(file_path, 'wb') as f:
                    pickle.dump(entry, f)
                
                return entry.value
                
        except Exception as e:
            self.logger.error(f"Failed to get cache entry {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        try:
            with self.lock:
                # Calculate expiration time
                expires_at = None
                if ttl is not None:
                    expires_at = datetime.utcnow() + timedelta(seconds=ttl)
                
                # Create cache entry
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_at=datetime.utcnow(),
                    expires_at=expires_at
                )
                
                # Save to file
                file_path = self._get_file_path(key)
                with open(file_path, 'wb') as f:
                    pickle.dump(entry, f)
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to set cache entry {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            with self.lock:
                file_path = self._get_file_path(key)
                if file_path.exists():
                    file_path.unlink()
                    return True
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete cache entry {key}: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            with self.lock:
                for file_path in self.cache_directory.glob("*.cache"):
                    file_path.unlink()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            with self.lock:
                file_path = self._get_file_path(key)
                
                if not file_path.exists():
                    return False
                
                with open(file_path, 'rb') as f:
                    entry = pickle.load(f)
                
                if entry.is_expired():
                    file_path.unlink()
                    return False
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to check cache entry {key}: {str(e)}")
            return False
    
    def size(self) -> int:
        """Get cache size."""
        try:
            with self.lock:
                count = 0
                for file_path in self.cache_directory.glob("*.cache"):
                    try:
                        with open(file_path, 'rb') as f:
                            entry = pickle.load(f)
                        if not entry.is_expired():
                            count += 1
                        else:
                            file_path.unlink()
                    except Exception:
                        # Remove corrupted files
                        file_path.unlink()
                
                return count
                
        except Exception as e:
            self.logger.error(f"Failed to get cache size: {str(e)}")
            return 0
    
    def keys(self) -> List[str]:
        """Get all cache keys."""
        try:
            with self.lock:
                keys = []
                for file_path in self.cache_directory.glob("*.cache"):
                    try:
                        with open(file_path, 'rb') as f:
                            entry = pickle.load(f)
                        if not entry.is_expired():
                            keys.append(entry.key)
                        else:
                            file_path.unlink()
                    except Exception:
                        # Remove corrupted files
                        file_path.unlink()
                
                return keys
                
        except Exception as e:
            self.logger.error(f"Failed to get cache keys: {str(e)}")
            return []


class RedisCacheBackend(CacheBackend):
    """Redis cache backend."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.redis_client = None
        self.logger = logging.getLogger(__name__)
        self._connect()
    
    def _connect(self):
        """Connect to Redis."""
        try:
            import redis
            self.redis_client = redis.from_url(self.redis_url, decode_responses=False)
            # Test connection
            self.redis_client.ping()
            self.logger.info(f"Connected to Redis: {self.redis_url}")
        except ImportError:
            self.logger.error("Redis package not installed. Install with: pip install redis")
            raise
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {str(e)}")
            raise
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            data = self.redis_client.get(key)
            if data is None:
                return None
            
            entry = pickle.loads(data)
            
            # Check if expired
            if entry.is_expired():
                self.redis_client.delete(key)
                return None
            
            # Update access info
            entry.touch()
            self.redis_client.set(key, pickle.dumps(entry))
            
            return entry.value
            
        except Exception as e:
            self.logger.error(f"Failed to get cache entry {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        try:
            # Calculate expiration time
            expires_at = None
            if ttl is not None:
                expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.utcnow(),
                expires_at=expires_at
            )
            
            # Save to Redis
            self.redis_client.set(key, pickle.dumps(entry), ex=ttl)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set cache entry {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            result = self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            self.logger.error(f"Failed to delete cache entry {key}: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            self.logger.error(f"Failed to check cache entry {key}: {str(e)}")
            return False
    
    def size(self) -> int:
        """Get cache size."""
        try:
            return self.redis_client.dbsize()
        except Exception as e:
            self.logger.error(f"Failed to get cache size: {str(e)}")
            return 0
    
    def keys(self) -> List[str]:
        """Get all cache keys."""
        try:
            return [key.decode() for key in self.redis_client.keys("*")]
        except Exception as e:
            self.logger.error(f"Failed to get cache keys: {str(e)}")
            return []


class CacheManager:
    """Advanced cache manager with multiple backends."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.backend = self._create_backend()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
        self.stats_lock = threading.Lock()
    
    def _create_backend(self) -> CacheBackend:
        """Create cache backend based on configuration."""
        cache_type = self.config.get('cache_type', 'memory')
        
        if cache_type == 'memory':
            max_size = self.config.get('max_cache_size', 1000)
            return MemoryCacheBackend(max_size)
        
        elif cache_type == 'file':
            cache_directory = self.config.get('cache_directory', './cache')
            return FileCacheBackend(cache_directory)
        
        elif cache_type == 'redis':
            redis_url = self.config.get('redis_url', 'redis://localhost:6379/0')
            return RedisCacheBackend(redis_url)
        
        else:
            raise ValueError(f"Unsupported cache type: {cache_type}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.backend.get(key)
            
            with self.stats_lock:
                if value is not None:
                    self.stats['hits'] += 1
                else:
                    self.stats['misses'] += 1
            
            return value
            
        except Exception as e:
            with self.stats_lock:
                self.stats['errors'] += 1
            self.logger.error(f"Cache get error for key {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        try:
            # Use default TTL if not specified
            if ttl is None:
                ttl = self.config.get('cache_ttl', 3600)
            
            success = self.backend.set(key, value, ttl)
            
            with self.stats_lock:
                if success:
                    self.stats['sets'] += 1
                else:
                    self.stats['errors'] += 1
            
            return success
            
        except Exception as e:
            with self.stats_lock:
                self.stats['errors'] += 1
            self.logger.error(f"Cache set error for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            success = self.backend.delete(key)
            
            with self.stats_lock:
                if success:
                    self.stats['deletes'] += 1
                else:
                    self.stats['errors'] += 1
            
            return success
            
        except Exception as e:
            with self.stats_lock:
                self.stats['errors'] += 1
            self.logger.error(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            success = self.backend.clear()
            
            with self.stats_lock:
                if success:
                    # Reset stats
                    self.stats = {
                        'hits': 0,
                        'misses': 0,
                        'sets': 0,
                        'deletes': 0,
                        'errors': 0
                    }
                else:
                    self.stats['errors'] += 1
            
            return success
            
        except Exception as e:
            with self.stats_lock:
                self.stats['errors'] += 1
            self.logger.error(f"Cache clear error: {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return self.backend.exists(key)
        except Exception as e:
            with self.stats_lock:
                self.stats['errors'] += 1
            self.logger.error(f"Cache exists error for key {key}: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.stats_lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'sets': self.stats['sets'],
                'deletes': self.stats['deletes'],
                'errors': self.stats['errors'],
                'hit_rate': hit_rate,
                'size': self.backend.size(),
                'backend_type': self.config.get('cache_type', 'memory')
            }
    
    def get_info(self) -> Dict[str, Any]:
        """Get cache information."""
        return {
            'backend_type': self.config.get('cache_type', 'memory'),
            'ttl': self.config.get('cache_ttl', 3600),
            'max_size': self.config.get('max_cache_size', 1000),
            'size': self.backend.size(),
            'keys': self.backend.keys()[:10],  # First 10 keys
            'stats': self.get_stats()
        }


# Global cache manager instance
_cache_manager = None

def get_cache_manager(config: Dict[str, Any] = None) -> CacheManager:
    """Get global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        if config is None:
            config = {
                'cache_type': 'memory',
                'cache_ttl': 3600,
                'max_cache_size': 1000
            }
        _cache_manager = CacheManager(config)
    return _cache_manager
