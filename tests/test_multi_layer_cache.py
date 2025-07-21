import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

"""
Unit tests for Multi-Layer Caching System.

Performance Team Implementation - Task 12
Author: Performance Team Lead
"""


# Import pytest with fallback to mock
pytest = None
try:
    import pytest
except ImportError:
    try:
        from common.mock_pytest import pytest
    except ImportError:
        # Mock pytest when not available
        class MockPytest:
            def fixture(self, *args, **kwargs):
                def decorator(func):
                    return func

                return decorator

            def mark(self):
                class MockMark:
                    def parametrize(self, *args, **kwargs):
                        def decorator(func):
                            return func

                        return decorator

                    def asyncio(self, func):
                        return func

                    def slow(self, func):
                        return func

                    def skip(self, reason=""):
                        def decorator(func):
                            return func

                        return decorator

                return MockMark()

            def raises(self, exception):
                class MockRaises:
                    def __enter__(self):
                        return self

                    def __exit__(self, *args):
                        return False

                return MockRaises()

            def skip(self, reason=""):
                def decorator(func):
                    return func

                return decorator

        pytest = MockPytest()

# Test imports
try:
    from infrastructure.cache.multi_layer_cache import (
        CacheConfig,
        CacheMetrics,
        ContentType,
        L1MemoryCache,
        MultiLayerCache,
    )

    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False


@pytest.fixture
def cache_config():
    """Test cache configuration."""
    return CacheConfig(
        l1_enabled=True,
        l1_max_size_mb=64,
        l1_ttl_seconds=300,
        l2_enabled=True,
        l2_redis_url="redis://localhost:6379",
        l3_enabled=True,
        compression_enabled=True,
        async_write_enabled=True,
        cache_warming_enabled=False,
        metrics_enabled=True,
    )


@pytest.fixture
async def multi_layer_cache(cache_config):
    """Multi-layer cache fixture."""
    if not CACHE_AVAILABLE:
        pytest.skip("Multi-layer cache not available")

    cache = MultiLayerCache(cache_config)
    await cache.initialize()
    yield cache
    await cache.cleanup()


def test_default_config():
    """Test default configuration values."""
    config = CacheConfig()
    assert config.l1_enabled is True
    assert config.l1_max_size_mb == 256
    assert config.l2_enabled is True
    assert config.l3_enabled is True
    assert config.compression_enabled is True


def test_custom_config():
    """Test custom configuration."""
    config = CacheConfig(
        l1_max_size_mb=128,
        l2_ttl_seconds=7200,
        compression_threshold_bytes=2048,
    )
    assert config.l1_max_size_mb == 128
    assert config.l2_ttl_seconds == 7200
    assert config.compression_threshold_bytes == 2048


class TestL1MemoryCache:
    """Test L1 memory cache functionality."""

    @pytest.fixture
    def l1_cache(self, cache_config):
        """L1 cache fixture."""
        return L1MemoryCache(cache_config)

    @pytest.mark.asyncio
    async def test_basic_operations(self, l1_cache):
        """Test basic cache operations."""
        # Test set and get
        result = await l1_cache.set(
            "test_key", "test_value", ContentType.AI_RESPONSE, 300
        )
        assert result is True

        value = await l1_cache.get("test_key")
        assert value == "test_value"

        # Test delete
        deleted = await l1_cache.delete("test_key")
        assert deleted is True

        value = await l1_cache.get("test_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_ttl_expiration(self, l1_cache):
        """Test TTL expiration."""
        # Set with very short TTL
        await l1_cache.set(
            "expire_key", "expire_value", ContentType.AI_RESPONSE, 1
        )  # 1 second

        # Should be available immediately
        value = await l1_cache.get("expire_key")
        assert value == "expire_value"

        # Wait for expiration
        await asyncio.sleep(1.1)

        # Should be expired
        value = await l1_cache.get("expire_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_lru_eviction(self, cache_config):
        """Test LRU eviction."""
        # Create cache with small size
        config = CacheConfig(l1_max_items=2)
        l1_cache = L1MemoryCache(config)

        # Add items
        await l1_cache.set("key1", "value1", ContentType.AI_RESPONSE, 300)
        await l1_cache.set("key2", "value2", ContentType.AI_RESPONSE, 300)
        await l1_cache.set("key3", "value3", ContentType.AI_RESPONSE, 300)

        # key1 should be evicted
        assert await l1_cache.get("key1") is None
        assert await l1_cache.get("key2") == "value2"
        assert await l1_cache.get("key3") == "value3"

    @pytest.mark.asyncio
    async def test_cache_stats(self, l1_cache):
        """Test cache statistics."""
        # Add some data
        await l1_cache.set("stat_key", "stat_value", ContentType.AI_RESPONSE, 300)

        stats = l1_cache.get_stats()

        assert "size" in stats
        assert "max_items" in stats
        assert "size_bytes" in stats
        assert stats["size"] >= 1


@pytest.mark.skipif(not CACHE_AVAILABLE, reason="Cache system not available")
class TestMultiLayerCache:
    """Test multi-layer cache system."""

    @pytest.mark.asyncio
    async def test_cache_initialization(self, cache_config):
        """Test cache system initialization."""
        cache = MultiLayerCache(cache_config)
        await cache.initialize()

        assert cache.l1_cache is not None
        assert cache.l2_cache is not None
        assert cache.l3_cache is not None

        await cache.cleanup()

    @pytest.mark.asyncio
    async def test_cache_fallback(self, multi_layer_cache):
        """Test cache fallback mechanism."""
        # Test with compute function
        compute_calls = 0

        async def compute_fn():
            nonlocal compute_calls
            compute_calls += 1
            return "computed_value"

        # First call should compute and cache
        result = await multi_layer_cache.get_with_fallback(
            "fallback_key", ContentType.AI_RESPONSE, compute_fn
        )

        assert result == "computed_value"
        assert compute_calls == 1

        # Second call should use cache
        result = await multi_layer_cache.get_with_fallback(
            "fallback_key", ContentType.AI_RESPONSE, compute_fn
        )

        assert result == "computed_value"
        assert compute_calls == 1  # Should not compute again

    @pytest.mark.asyncio
    async def test_multi_layer_set(self, multi_layer_cache):
        """Test setting values across multiple layers."""
        result = await multi_layer_cache.set_multi_layer(
            "multi_key", "multi_value", ContentType.AI_RESPONSE
        )

        assert result is True

        # Should be available in L1
        if multi_layer_cache.l1_cache:
            value = await multi_layer_cache.l1_cache.get("multi_key")
            assert value == "multi_value"

    @pytest.mark.asyncio
    async def test_cache_invalidation(self, multi_layer_cache):
        """Test cache invalidation."""
        # Set value
        await multi_layer_cache.set_multi_layer(
            "invalid_key", "invalid_value", ContentType.AI_RESPONSE
        )

        # Verify it's cached
        value = await multi_layer_cache.get_with_fallback(
            "invalid_key", ContentType.AI_RESPONSE
        )
        pytest.assume(value == "invalid_value")

        # Invalidate
        result = await multi_layer_cache.invalidate("invalid_key")
        assert result is True

        # Should not be in cache anymore
        value = await multi_layer_cache.get_with_fallback(
            "invalid_key", ContentType.AI_RESPONSE
        )
        assert value is None

    @pytest.mark.asyncio
    async def test_cache_warming(self, multi_layer_cache):
        """Test cache warming functionality."""
        warm_data = [
            ("warm_key1", "warm_value1", ContentType.AI_RESPONSE),
            ("warm_key2", "warm_value2", ContentType.CONFIGURATION),
            ("warm_key3", "warm_value3", ContentType.EMOTION_ANALYSIS),
        ]

        success_count = await multi_layer_cache.warm_cache(warm_data)
        assert success_count == 3

        # Verify cached values
        for key, expected_value, content_type in warm_data:
            value = await multi_layer_cache.get_with_fallback(key, content_type)
            assert value == expected_value

    @pytest.mark.asyncio
    async def test_cache_decorator(self, multi_layer_cache):
        """Test cache decorator functionality."""
        call_count = 0

        @multi_layer_cache.cached(
            content_type=ContentType.AI_RESPONSE, key_prefix="test_decorator"
        )
        async def expensive_function(param):
            nonlocal call_count
            call_count += 1
            return f"result_{param}"

        # First call
        result1 = await expensive_function("test")
        assert result1 == "result_test"
        assert call_count == 1

        # Second call should use cache
        result2 = await expensive_function("test")
        assert result2 == "result_test"
        assert call_count == 1  # Should not increment

        # Different parameter should compute again
        result3 = await expensive_function("different")
        assert result3 == "result_different"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_performance_metrics(self, multi_layer_cache):
        """Test performance metrics collection."""
        # Perform some operations
        await multi_layer_cache.set_multi_layer(
            "metrics_key", "metrics_value", ContentType.AI_RESPONSE
        )

        await multi_layer_cache.get_with_fallback(
            "metrics_key", ContentType.AI_RESPONSE
        )

        await multi_layer_cache.get_with_fallback(
            "nonexistent_key", ContentType.AI_RESPONSE
        )

        # Get metrics
        metrics = multi_layer_cache.get_performance_metrics()

        assert "total_requests" in metrics
        assert "l1_hits" in metrics
        assert "l1_misses" in metrics
        assert "hit_rate_by_layer" in metrics
        assert "cache_efficiency" in metrics

        # Should have at least one request
        pytest.assume(metrics["total_requests"] >= 1)

    @pytest.mark.asyncio
    async def test_content_type_strategies(self, multi_layer_cache):
        """Test different content type caching strategies."""
        # Test static assets (should use L3)
        await multi_layer_cache.set_multi_layer(
            "static_key", "static_content", ContentType.STATIC_ASSETS
        )

        # Test user session (should not use L3)
        await multi_layer_cache.set_multi_layer(
            "session_key",
            {"user_id": "123", "data": "session_data"},
            ContentType.USER_SESSION,
        )

        # Test model weights (should use L2 and L3, not L1)
        await multi_layer_cache.set_multi_layer(
            "model_key",
            {"weights": "large_model_data"},
            ContentType.MODEL_WEIGHTS,
        )

        # Verify values are retrievable
        static_value = await multi_layer_cache.get_with_fallback(
            "static_key", ContentType.STATIC_ASSETS
        )
        assert static_value == "static_content"

        session_value = await multi_layer_cache.get_with_fallback(
            "session_key", ContentType.USER_SESSION
        )
        assert session_value["user_id"] == "123"


def test_metrics_initialization():
    """Test metrics initialization."""
    metrics = CacheMetrics()
    assert metrics.total_requests == 0
    assert metrics.l1_hits == 0
    assert metrics.hit_rate == 0.0
    assert metrics.last_updated is not None


def test_hit_rate_calculation():
    """Test hit rate calculation."""
    metrics = CacheMetrics()
    metrics.l1_hits = 70
    metrics.l2_hits = 20
    metrics.l1_misses = 10
    assert metrics.total_hits == 90
    assert metrics.total_misses == 10
    assert metrics.hit_rate == 0.9


def test_average_latency_calculation():
    """Test average latency calculation."""
    metrics = CacheMetrics()
    metrics.total_requests = 100
    metrics.total_latency_ms = 5000.0
    assert metrics.average_latency_ms == 50.0


@pytest.mark.asyncio
async def test_cache_performance_under_load():
    """Test cache performance under concurrent load."""
    if not CACHE_AVAILABLE:
        pytest.skip("Cache system not available")

    cache = MultiLayerCache(CacheConfig(l1_max_size_mb=32))
    await cache.initialize()

    try:
        # Concurrent operations
        async def cache_operation(i):
            key = f"load_key_{i}"
            value = f"load_value_{i}"

            # Set value
            await cache.set_multi_layer(key, value, ContentType.AI_RESPONSE)

            # Get value
            result = await cache.get_with_fallback(key, ContentType.AI_RESPONSE)
            assert result == value

            return True

        # Run concurrent operations
        tasks = [cache_operation(i) for i in range(50)]
        results = await asyncio.gather(*tasks)

        assert all(results)

        # Check metrics
        metrics = cache.get_performance_metrics()
        pytest.assume(metrics["total_requests"] >= 50)

    finally:
        await cache.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
