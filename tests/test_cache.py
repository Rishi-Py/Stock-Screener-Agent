"""
Tests for cache manager.
"""

import pytest
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from src.utils.cache import CacheManager


@pytest.fixture
def cache_manager():
    """Create a temporary cache manager for testing."""
    temp_dir = tempfile.mkdtemp()
    manager = CacheManager(cache_dir=temp_dir, ttl_hours=1)
    yield manager
    # Cleanup
    shutil.rmtree(temp_dir)


def test_cache_set_and_get(cache_manager):
    """Test setting and getting cache data."""
    data = {"symbol": "AAPL", "price": 150.0}
    assert cache_manager.set("AAPL", data)
    
    cached = cache_manager.get("AAPL")
    assert cached is not None
    assert cached["symbol"] == "AAPL"
    assert cached["price"] == 150.0


def test_cache_get_nonexistent(cache_manager):
    """Test getting non-existent cache."""
    assert cache_manager.get("NONEXISTENT") is None


def test_cache_clear_specific(cache_manager):
    """Test clearing specific cache entry."""
    cache_manager.set("AAPL", {"price": 150.0})
    cache_manager.set("MSFT", {"price": 300.0})
    
    assert cache_manager.clear("AAPL")
    assert cache_manager.get("AAPL") is None
    assert cache_manager.get("MSFT") is not None


def test_cache_clear_all(cache_manager):
    """Test clearing all cache."""
    cache_manager.set("AAPL", {"price": 150.0})
    cache_manager.set("MSFT", {"price": 300.0})
    
    assert cache_manager.clear()
    assert cache_manager.get("AAPL") is None
    assert cache_manager.get("MSFT") is None


def test_cache_ttl(cache_manager):
    """Test cache TTL expiration."""
    # Create a short TTL cache manager
    temp_dir = tempfile.mkdtemp()
    short_ttl_manager = CacheManager(cache_dir=temp_dir, ttl_hours=0)
    
    try:
        data = {"symbol": "AAPL", "price": 150.0}
        short_ttl_manager.set("AAPL", data)
        
        # Cache should be immediately expired with 0 hour TTL
        cached = short_ttl_manager.get("AAPL")
        assert cached is None
    finally:
        shutil.rmtree(temp_dir)
