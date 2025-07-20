"""Redis health check module."""

import time
from datetime import datetime

import redis.asyncio as redis

from src.infrastructure.logging_config import get_logger

from ..models import HealthCheckResult, HealthStatus

logger = get_logger(__name__, component="infrastructure")


class RedisHealthCheck:
    """Redis connectivity and performance health check."""

    def __init__(self, redis_client: redis.Redis | None = None) -> None:
        self.redis_client = redis_client

    async def check(self) -> HealthCheckResult:
        """Check Redis health."""
        start_time = time.time()
        try:
            if not self.redis_client:
                return HealthCheckResult(
                    name="redis",
                    status=HealthStatus.UNHEALTHY,
                    message="Redis not configured",
                    details={"error": "No Redis client available"},
                    duration_ms=(time.time() - start_time) * 1000,
                    timestamp=datetime.utcnow(),
                )

            # Test Redis connectivity
            test_key = f"health_check_{int(time.time())}"
            test_value = "test_value"

            # Set test value
            await self.redis_client.setex(test_key, 10, test_value)

            # Get test value
            retrieved = await self.redis_client.get(test_key)

            # Clean up
            await self.redis_client.delete(test_key)

            if retrieved != test_value.encode():
                raise ValueError("Redis read/write test failed")

            # Get Redis info
            info = await self.redis_client.info()
            memory_info = info.get("used_memory_human", "N/A")
            connected_clients = info.get("connected_clients", 0)

            duration = (time.time() - start_time) * 1000
            if duration > 50:  # Slow response
                status = HealthStatus.DEGRADED
                message = f"Redis responding slowly ({duration:.0f}ms)"
            else:
                status = HealthStatus.HEALTHY
                message = "Redis is healthy"

            return HealthCheckResult(
                name="redis",
                status=status,
                message=message,
                details={
                    "memory_usage": memory_info,
                    "connected_clients": connected_clients,
                    "response_time_ms": duration,
                },
                duration_ms=duration,
                timestamp=datetime.utcnow(),
            )
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return HealthCheckResult(
                name="redis",
                status=HealthStatus.UNHEALTHY,
                message=f"Redis check failed: {e!s}",
                details={"error": str(e)},
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
            )
