"""
Cache manager for storing and retrieving stock data.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional
from loguru import logger


class CacheManager:
    """Manages caching of stock data to reduce API calls."""
    
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live for cached data in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        logger.info(f"Cache manager initialized with TTL: {ttl_hours} hours")
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve data from cache.
        
        Args:
            key: Cache key (typically stock symbol)
            
        Returns:
            Cached data if found and not expired, None otherwise
        """
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cached['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                logger.debug(f"Cache expired for {key}")
                return None
            
            logger.debug(f"Cache hit for {key}")
            return cached['data']
            
        except Exception as e:
            logger.warning(f"Error reading cache for {key}: {str(e)}")
            return None
    
    def set(self, key: str, data: Dict[str, Any]) -> bool:
        """
        Store data in cache.
        
        Args:
            key: Cache key (typically stock symbol)
            data: Data to cache
            
        Returns:
            True if successful, False otherwise
        """
        cache_file = self.cache_dir / f"{key}.json"
        
        try:
            cached = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cached, f, indent=2)
            
            logger.debug(f"Cached data for {key}")
            return True
            
        except Exception as e:
            logger.warning(f"Error writing cache for {key}: {str(e)}")
            return False
    
    def clear(self, key: Optional[str] = None) -> bool:
        """
        Clear cache.
        
        Args:
            key: Specific key to clear, or None to clear all
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if key:
                cache_file = self.cache_dir / f"{key}.json"
                if cache_file.exists():
                    cache_file.unlink()
                    logger.info(f"Cleared cache for {key}")
            else:
                for cache_file in self.cache_dir.glob("*.json"):
                    cache_file.unlink()
                logger.info("Cleared all cache")
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False
    
    def cleanup_expired(self) -> int:
        """
        Remove expired cache files.
        
        Returns:
            Number of files removed
        """
        removed = 0
        
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                
                cached_time = datetime.fromisoformat(cached['timestamp'])
                if datetime.now() - cached_time > self.ttl:
                    cache_file.unlink()
                    removed += 1
            
            if removed > 0:
                logger.info(f"Cleaned up {removed} expired cache files")
            
        except Exception as e:
            logger.error(f"Error during cache cleanup: {str(e)}")
        
        return removed
