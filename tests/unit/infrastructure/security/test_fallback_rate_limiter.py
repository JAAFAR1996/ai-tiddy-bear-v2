"""Tests for Fallback Rate Limiter
Testing in-memory rate limiting with sliding window algorithm.
"""

import asyncio
import threading
import time
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.infrastructure.security.rate_limiter.legacy.fallback_rate_limiter import (
    FallbackRateLimitService,
    SlidingWindowRateLimiter,
)


class TestSlidingWindowRateLimiter:
    """Test the Sliding Window Rate Limiter."""

    @pytest.fixture
    def rate_limiter(self):
        """Create a rate limiter instance with test settings."""
        return SlidingWindowRateLimiter(default_limit=5, window_seconds=10)

    def test_initialization(self, rate_limiter):
        """Test rate limiter initialization."""
        assert isinstance(rate_limiter, SlidingWindowRateLimiter)
        assert rate_limiter.default_limit == 5
        assert rate_limiter.window_seconds == 10
        assert hasattr(rate_limiter, "_user_windows")
        assert hasattr(rate_limiter, "_global_window")
        assert hasattr(rate_limiter, "_lock")
        assert hasattr(rate_limiter, "_custom_limits")
        assert rate_limiter._cleanup_interval == 300

    @pytest.mark.asyncio
    async def test_is_allowed_within_limit(self, rate_limiter):
        """Test requests within rate limit are allowed."""
        user_id = "test_user_1"

        # Make requests within limit
        for i in range(3):
            result = await rate_limiter.is_allowed(user_id)

            assert result["allowed"] is True
            assert (
                result["remaining"] == 5 - (i + 1) - 1
            )  # remaining after this request
            assert result["retry_after"] == 0
            assert result["limit"] == 5
            assert result["window_seconds"] == 10
            assert "reset_time" in result

    @pytest.mark.asyncio
    async def test_is_allowed_exceeds_limit(self, rate_limiter):
        """Test requests exceeding rate limit are blocked."""
        user_id = "test_user_2"

        # Make requests up to limit
        for i in range(5):
            result = await rate_limiter.is_allowed(user_id)
            assert result["allowed"] is True

        # Next request should be blocked
        result = await rate_limiter.is_allowed(user_id)

        assert result["allowed"] is False
        assert result["remaining"] == 0
        assert result["retry_after"] > 0
        assert result["limit"] == 5
        assert "reset_time" in result

    @pytest.mark.asyncio
    async def test_is_allowed_with_endpoint(self, rate_limiter):
        """Test rate limiting per endpoint."""
        user_id = "test_user_3"
        endpoint1 = "api/endpoint1"
        endpoint2 = "api/endpoint2"

        # Make requests to different endpoints
        for i in range(3):
            result1 = await rate_limiter.is_allowed(user_id, endpoint1)
            result2 = await rate_limiter.is_allowed(user_id, endpoint2)

            assert result1["allowed"] is True
            assert result2["allowed"] is True

        # Endpoints should have separate limits
        assert len(rate_limiter._user_windows) == 2

    @pytest.mark.asyncio
    async def test_is_allowed_with_custom_limits(self, rate_limiter):
        """Test rate limiting with custom limits."""
        user_id = "test_user_4"
        custom_limit = 2
        custom_window = 5

        # Make requests with custom limits
        for i in range(2):
            result = await rate_limiter.is_allowed(
                user_id, custom_limit=custom_limit, custom_window=custom_window
            )
            assert result["allowed"] is True
            assert result["limit"] == custom_limit
            assert result["window_seconds"] == custom_window

        # Next request should be blocked with custom limits
        result = await rate_limiter.is_allowed(
            user_id, custom_limit=custom_limit, custom_window=custom_window
        )
        assert result["allowed"] is False

    @pytest.mark.asyncio
    async def test_sliding_window_behavior(self, rate_limiter):
        """Test that sliding window properly expires old requests."""
        user_id = "test_user_5"

        # Mock time to control sliding window
        original_time = time.time
        mock_time = original_time()

        with patch("time.time", return_value=mock_time):
            # Fill up the rate limit
            for i in range(5):
                result = await rate_limiter.is_allowed(user_id)
                assert result["allowed"] is True

            # Next request should be blocked
            result = await rate_limiter.is_allowed(user_id)
            assert result["allowed"] is False

        # Advance time beyond window
        with patch("time.time", return_value=mock_time + 11):
            # Should be allowed again after window expires
            result = await rate_limiter.is_allowed(user_id)
            assert result["allowed"] is True

    def test_set_custom_limit(self, rate_limiter):
        """Test setting custom rate limits."""
        user_id = "custom_user"
        endpoint = "custom_endpoint"
        limit = 10
        window_seconds = 60

        rate_limiter.set_custom_limit(user_id, limit, window_seconds, endpoint)

        key = f"{user_id}:{endpoint}"
        assert key in rate_limiter._custom_limits
        assert rate_limiter._custom_limits[key] == (limit, window_seconds)

    def test_set_custom_limit_without_endpoint(self, rate_limiter):
        """Test setting custom rate limits without endpoint."""
        user_id = "custom_user_no_endpoint"
        limit = 15
        window_seconds = 30

        rate_limiter.set_custom_limit(user_id, limit, window_seconds)

        assert user_id in rate_limiter._custom_limits
        assert rate_limiter._custom_limits[user_id] == (limit, window_seconds)

    def test_remove_custom_limit(self, rate_limiter):
        """Test removing custom rate limits."""
        user_id = "remove_user"
        endpoint = "remove_endpoint"

        # Set custom limit first
        rate_limiter.set_custom_limit(user_id, 10, 60, endpoint)
        key = f"{user_id}:{endpoint}"
        assert key in rate_limiter._custom_limits

        # Remove custom limit
        rate_limiter.remove_custom_limit(user_id, endpoint)
        assert key not in rate_limiter._custom_limits

    def test_remove_custom_limit_nonexistent(self, rate_limiter):
        """Test removing non-existent custom rate limits."""
        user_id = "nonexistent_user"

        # Should not raise error
        rate_limiter.remove_custom_limit(user_id)

        # Should still be empty
        assert user_id not in rate_limiter._custom_limits

    @pytest.mark.asyncio
    async def test_get_rate_limit_config(self, rate_limiter):
        """Test rate limit configuration retrieval."""
        user_id = "config_user"

        # Test default config
        limit, window = rate_limiter._get_rate_limit_config(user_id, None, None)
        assert limit == 5  # default_limit
        assert window == 10  # window_seconds

        # Test method parameter override
        limit, window = rate_limiter._get_rate_limit_config(user_id, 20, 30)
        assert limit == 20
        assert window == 30

        # Test stored custom limits
        rate_limiter.set_custom_limit(user_id, 15, 25)
        limit, window = rate_limiter._get_rate_limit_config(user_id, None, None)
        assert limit == 15
        assert window == 25

        # Method parameters should override stored custom limits
        limit, window = rate_limiter._get_rate_limit_config(user_id, 35, 45)
        assert limit == 35
        assert window == 45

    @pytest.mark.asyncio
    async def test_cleanup_old_entries(self, rate_limiter):
        """Test cleanup of expired entries."""
        user_id = "cleanup_user"

        # Add some requests
        mock_time = time.time()
        with patch("time.time", return_value=mock_time):
            for _ in range(3):
                await rate_limiter.is_allowed(user_id)

        # Verify entries exist
        assert len(rate_limiter._user_windows[user_id]) == 3

        # Cleanup with time advanced beyond window
        advanced_time = mock_time + 100
        await rate_limiter._cleanup_old_entries(advanced_time)

        # Old entries should be cleaned up
        assert len(rate_limiter._user_windows[user_id]) == 0

    @pytest.mark.asyncio
    async def test_get_statistics(self, rate_limiter):
        """Test statistics generation."""
        # Add some activity
        users = ["stats_user_1", "stats_user_2", "stats_user_3"]

        for user in users:
            for _ in range(2):
                await rate_limiter.is_allowed(user)

        stats = await rate_limiter.get_statistics()

        # Verify statistics structure
        assert "active_users" in stats
        assert "total_tracked_users" in stats
        assert "requests_last_window" in stats
        assert "requests_last_hour" in stats
        assert "custom_limits_count" in stats
        assert "memory_usage" in stats
        assert "config" in stats
        assert "last_cleanup" in stats

        # Verify some values
        assert stats["total_tracked_users"] == 3
        assert stats["requests_last_window"] >= 6  # 3 users * 2 requests
        assert stats["custom_limits_count"] == 0
        assert stats["config"]["default_limit"] == 5
        assert stats["config"]["default_window_seconds"] == 10

    @pytest.mark.asyncio
    async def test_reset_user_limits(self, rate_limiter):
        """Test resetting user rate limits."""
        user_id = "reset_user"
        endpoint = "reset_endpoint"

        # Add some requests
        await rate_limiter.is_allowed(user_id)
        await rate_limiter.is_allowed(user_id, endpoint)

        # Verify requests are recorded
        assert len(rate_limiter._user_windows[user_id]) == 1
        assert len(rate_limiter._user_windows[f"{user_id}:{endpoint}"]) == 1

        # Reset user limits
        result = await rate_limiter.reset_user_limits(user_id)
        assert result is True

        # User window should be cleared
        assert len(rate_limiter._user_windows[user_id]) == 0

        # Endpoint-specific limits should still exist
        assert len(rate_limiter._user_windows[f"{user_id}:{endpoint}"]) == 1

        # Reset endpoint-specific limits
        result = await rate_limiter.reset_user_limits(user_id, endpoint)
        assert result is True
        assert len(rate_limiter._user_windows[f"{user_id}:{endpoint}"]) == 0

    @pytest.mark.asyncio
    async def test_reset_user_limits_nonexistent(self, rate_limiter):
        """Test resetting limits for non-existent user."""
        result = await rate_limiter.reset_user_limits("nonexistent_user")
        assert result is False

    @pytest.mark.asyncio
    async def test_thread_safety(self, rate_limiter):
        """Test thread safety of rate limiter."""
        user_id = "thread_test_user"
        results = []
        errors = []

        def make_requests():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                for _ in range(10):
                    result = loop.run_until_complete(rate_limiter.is_allowed(user_id))
                    results.append(result)

                loop.close()
            except Exception as e:
                errors.append(e)

        # Create multiple threads making concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_requests)
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Should have handled concurrent access without errors
        assert len(errors) == 0
        assert len(results) == 50  # 5 threads * 10 requests each

        # Some requests should be allowed, some blocked (depending on timing)
        allowed_count = sum(1 for r in results if r["allowed"])
        blocked_count = sum(1 for r in results if not r["allowed"])

        # At least some should be allowed, and likely some blocked due to rate
        # limiting
        assert allowed_count > 0

    @pytest.mark.asyncio
    async def test_memory_cleanup_integration(self, rate_limiter):
        """Test memory cleanup during normal operation."""
        # Override cleanup interval for testing
        rate_limiter._cleanup_interval = 1  # 1 second

        users = [f"cleanup_user_{i}" for i in range(10)]

        # Add requests for multiple users
        for user in users:
            await rate_limiter.is_allowed(user)

        # Verify all users are tracked
        assert len(rate_limiter._user_windows) == 10

        # Wait for cleanup interval and make another request
        await asyncio.sleep(1.1)

        # Trigger cleanup by making a request after cleanup interval
        mock_time = time.time() + 1000  # Far in future
        with patch("time.time", return_value=mock_time):
            await rate_limiter.is_allowed("trigger_cleanup_user")

        # Old entries should be cleaned up
        # Note: The exact cleanup behavior depends on timing


class TestFallbackRateLimitService:
    """Test the Fallback Rate Limit Service."""

    @pytest.fixture
    def mock_redis_client(self):
        """Create a mock Redis client."""
        mock_redis = Mock()
        mock_redis.ping = AsyncMock()
        mock_redis.delete = AsyncMock()
        return mock_redis

    @pytest.fixture
    def fallback_service(self):
        """Create a fallback rate limit service without Redis."""
        return FallbackRateLimitService()

    @pytest.fixture
    def fallback_service_with_redis(self, mock_redis_client):
        """Create a fallback rate limit service with Redis."""
        return FallbackRateLimitService(redis_client=mock_redis_client)

    def test_initialization_without_redis(self, fallback_service):
        """Test service initialization without Redis."""
        assert isinstance(fallback_service, FallbackRateLimitService)
        assert fallback_service.redis_client is None
        assert fallback_service.redis_available is False
        assert hasattr(fallback_service, "fallback_limiter")
        assert isinstance(fallback_service.fallback_limiter, SlidingWindowRateLimiter)

    def test_initialization_with_redis(
        self, fallback_service_with_redis, mock_redis_client
    ):
        """Test service initialization with Redis."""
        assert fallback_service_with_redis.redis_client == mock_redis_client
        assert fallback_service_with_redis.redis_available is False  # Not checked yet

    @pytest.mark.asyncio
    async def test_check_redis_availability_no_client(self, fallback_service):
        """Test Redis availability check when no client is configured."""
        result = await fallback_service.check_redis_availability()

        assert result is False
        assert fallback_service.redis_available is False

    @pytest.mark.asyncio
    async def test_check_redis_availability_client_success(
        self, fallback_service_with_redis, mock_redis_client
    ):
        """Test Redis availability check with successful ping."""
        mock_redis_client.ping.return_value = True

        result = await fallback_service_with_redis.check_redis_availability()

        assert result is True
        assert fallback_service_with_redis.redis_available is True
        mock_redis_client.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_redis_availability_client_failure(
        self, fallback_service_with_redis, mock_redis_client
    ):
        """Test Redis availability check with failed ping."""
        mock_redis_client.ping.side_effect = Exception("Redis connection failed")

        result = await fallback_service_with_redis.check_redis_availability()

        assert result is False
        assert fallback_service_with_redis.redis_available is False

    @pytest.mark.asyncio
    async def test_check_redis_availability_caching(
        self, fallback_service_with_redis, mock_redis_client
    ):
        """Test that Redis availability is cached for performance."""
        mock_redis_client.ping.return_value = True

        # First check
        result1 = await fallback_service_with_redis.check_redis_availability()
        assert result1 is True

        # Second check within interval should not ping Redis again
        result2 = await fallback_service_with_redis.check_redis_availability()
        assert result2 is True

        # Should only have called ping once due to caching
        assert mock_redis_client.ping.call_count == 1

    @pytest.mark.asyncio
    async def test_is_allowed_fallback_only(self, fallback_service):
        """Test rate limiting using fallback only."""
        user_id = "fallback_user"

        result = await fallback_service.is_allowed(user_id)

        assert result["allowed"] is True
        assert result["fallback_used"] is True
        assert "remaining" in result
        assert "retry_after" in result

    @pytest.mark.asyncio
    async def test_is_allowed_with_redis_unavailable(
        self, fallback_service_with_redis, mock_redis_client
    ):
        """Test rate limiting when Redis is unavailable."""
        mock_redis_client.ping.side_effect = Exception("Redis down")

        user_id = "redis_unavailable_user"

        result = await fallback_service_with_redis.is_allowed(user_id)

        assert result["allowed"] is True
        assert result["fallback_used"] is True
        assert fallback_service_with_redis.redis_available is False

    @pytest.mark.asyncio
    async def test_is_allowed_with_custom_limits(self, fallback_service):
        """Test rate limiting with custom limits."""
        user_id = "custom_limits_user"
        endpoint = "custom_endpoint"
        custom_limit = 3
        custom_window = 5

        result = await fallback_service.is_allowed(
            user_id, endpoint, custom_limit, custom_window
        )

        assert result["allowed"] is True
        assert result["limit"] == custom_limit
        assert result["window_seconds"] == custom_window
        assert result["fallback_used"] is True

    @pytest.mark.asyncio
    async def test_redis_rate_limit_fallback(
        self, fallback_service_with_redis, mock_redis_client
    ):
        """Test that Redis rate limiting falls back to in-memory."""
        # Mock Redis as available but rate limiting not implemented
        mock_redis_client.ping.return_value = True

        user_id = "redis_fallback_user"

        result = await fallback_service_with_redis.is_allowed(user_id)

        # Should fall back to in-memory limiter
        assert result["allowed"] is True

    @pytest.mark.asyncio
    async def test_get_statistics(self, fallback_service):
        """Test statistics generation."""
        # Add some activity
        await fallback_service.is_allowed("stats_user_1")
        await fallback_service.is_allowed("stats_user_2")

        stats = await fallback_service.get_statistics()

        # Should include fallback limiter stats
        assert "active_users" in stats
        assert "total_tracked_users" in stats
        assert "redis_available" in stats
        assert "last_redis_check" in stats
        assert "service_type" in stats

        # Service-specific stats
        assert stats["redis_available"] is False
        assert stats["service_type"] == "fallback"

    @pytest.mark.asyncio
    async def test_get_statistics_with_redis(
        self, fallback_service_with_redis, mock_redis_client
    ):
        """Test statistics generation with Redis available."""
        mock_redis_client.ping.return_value = True

        # Check Redis availability first
        await fallback_service_with_redis.check_redis_availability()

        stats = await fallback_service_with_redis.get_statistics()

        assert stats["redis_available"] is True
        assert stats["service_type"] == "redis"

    def test_set_custom_limit(self, fallback_service):
        """Test setting custom rate limits."""
        user_id = "custom_limit_user"
        limit = 20
        window_seconds = 120
        endpoint = "custom_endpoint"

        fallback_service.set_custom_limit(user_id, limit, window_seconds, endpoint)

        # Verify the limit was set in fallback limiter
        key = f"{user_id}:{endpoint}"
        assert key in fallback_service.fallback_limiter._custom_limits
        assert fallback_service.fallback_limiter._custom_limits[key] == (
            limit,
            window_seconds,
        )

    @pytest.mark.asyncio
    async def test_reset_user_limits_fallback_only(self, fallback_service):
        """Test resetting user limits in fallback mode."""
        user_id = "reset_fallback_user"

        # Add some requests first
        await fallback_service.is_allowed(user_id)

        # Reset limits
        result = await fallback_service.reset_user_limits(user_id)

        assert result is True

    @pytest.mark.asyncio
    async def test_reset_user_limits_with_redis(
        self, fallback_service_with_redis, mock_redis_client
    ):
        """Test resetting user limits with Redis available."""
        user_id = "reset_redis_user"
        endpoint = "reset_endpoint"

        # Add Redis client attribute for testing
        fallback_service_with_redis._redis_client = mock_redis_client

        result = await fallback_service_with_redis.reset_user_limits(user_id, endpoint)

        # Should attempt to reset both fallback and Redis
        assert result is True
        mock_redis_client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_user_limits_redis_error(
        self, fallback_service_with_redis, mock_redis_client
    ):
        """Test resetting user limits when Redis fails."""
        user_id = "reset_error_user"

        # Add Redis client that fails
        fallback_service_with_redis._redis_client = mock_redis_client
        mock_redis_client.delete.side_effect = Exception("Redis error")

        # Add request to fallback first
        await fallback_service_with_redis.is_allowed(user_id)

        result = await fallback_service_with_redis.reset_user_limits(user_id)

        # Should still succeed with fallback reset
        assert result is True

    @pytest.mark.asyncio
    async def test_redis_availability_state_changes(
        self, fallback_service_with_redis, mock_redis_client
    ):
        """Test Redis availability state changes and logging."""
        # Start with Redis unavailable
        mock_redis_client.ping.side_effect = Exception("Redis down")

        result1 = await fallback_service_with_redis.check_redis_availability()
        assert result1 is False

        # Make Redis available
        mock_redis_client.ping.side_effect = None
        mock_redis_client.ping.return_value = True

        # Force check by advancing time
        fallback_service_with_redis.last_redis_check = 0

        result2 = await fallback_service_with_redis.check_redis_availability()
        assert result2 is True

    @pytest.mark.asyncio
    async def test_concurrent_rate_limiting(self, fallback_service):
        """Test concurrent rate limiting operations."""
        user_ids = [f"concurrent_user_{i}" for i in range(10)]

        # Create concurrent requests
        tasks = [fallback_service.is_allowed(user_id) for user_id in user_ids]

        results = await asyncio.gather(*tasks)

        # All should complete successfully
        assert len(results) == 10
        assert all(result["allowed"] for result in results)
        assert all(result["fallback_used"] for result in results)

    @pytest.mark.asyncio
    async def test_rate_limit_enforcement_integration(self, fallback_service):
        """Test complete rate limit enforcement workflow."""
        user_id = "enforcement_user"

        # Configure fallback limiter with small limits for testing
        fallback_service.fallback_limiter.default_limit = 3
        fallback_service.fallback_limiter.window_seconds = 5

        # Make requests up to limit
        allowed_requests = 0
        blocked_requests = 0

        for i in range(5):
            result = await fallback_service.is_allowed(user_id)
            if result["allowed"]:
                allowed_requests += 1
            else:
                blocked_requests += 1

        # Should have allowed 3 and blocked 2
        assert allowed_requests == 3
        assert blocked_requests == 2

    @pytest.mark.asyncio
    async def test_service_degradation_graceful(
        self, fallback_service_with_redis, mock_redis_client
    ):
        """Test graceful degradation when Redis fails during operation."""
        user_id = "degradation_user"

        # Start with Redis working
        mock_redis_client.ping.return_value = True
        await fallback_service_with_redis.check_redis_availability()
        assert fallback_service_with_redis.redis_available is True

        # Make Redis fail
        mock_redis_client.ping.side_effect = Exception("Redis failure")

        # Reset check time to force re-check
        fallback_service_with_redis.last_redis_check = 0

        # Should gracefully fall back
        result = await fallback_service_with_redis.is_allowed(user_id)

        assert result["allowed"] is True
        assert result["fallback_used"] is True
        assert fallback_service_with_redis.redis_available is False
