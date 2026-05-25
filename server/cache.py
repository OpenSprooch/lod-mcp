"""Cache module for LOD API responses"""
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, Optional


class LODCache:
    """Simple TTL cache for API responses"""
    
    def __init__(self, ttl_seconds: int = 3600, max_size: int = 1000):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def _make_key(self, endpoint: str, params: str) -> str:
        key = f"{endpoint}:{params}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def get(self, endpoint: str, params: str) -> Optional[Any]:
        key = self._make_key(endpoint, params)
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() < entry['expires']:
                self.hits += 1
                return entry['data']
            else:
                del self.cache[key]
        self.misses += 1
        return None
    
    def set(self, endpoint: str, params: str, data: Any):
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k]['expires'])
            del self.cache[oldest_key]
        
        key = self._make_key(endpoint, params)
        self.cache[key] = {
            'data': data,
            'expires': datetime.now() + timedelta(seconds=self.ttl)
        }
    
    def clear(self):
        self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 1),
            'size': len(self.cache)
        }


# Global cache instance
cache = LODCache(ttl_seconds=3600, max_size=500)
