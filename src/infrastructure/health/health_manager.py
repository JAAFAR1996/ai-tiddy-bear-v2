"""Health check manager - coordinates all health checks.

This module provides a centralized health check manager that aggregates
status from various application components and external dependencies.
"""

import asyncio
from datetime import datetime
from typing import Any

from src.infrastructure.health.checks.database_check import DatabaseHealthCheck
from src.infrastructure.health.checks.redis_check import RedisHealthCheck
from src.infrastructure.health.checks.system_check import SystemHealthCheck
from src.domain.models.health_models import (
    HealthCheckResult,
    HealthStatus,
    SystemHealth,
)
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="infrastructure")


class HealthCheckManager:
    """Manages and coordinates all health checks."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.start_time = datetime.utcnow()
        # Initialize health checks
        self.database_check = DatabaseHealthCheck(self.config.get("database_session"))
        self.redis_check = RedisHealthCheck(self.config.get("redis_client"))
        self.system_check = SystemHealthCheck()
        # Cache for health check results with thread safety
        self._last_check_time = None
        self._cached_result = None
        self._cache_duration = 10  # seconds
        self._cache_lock = asyncio.Lock()

    async def check_health(self, detailed: bool = False) -> SystemHealth:
        """Run all health checks and return system health status."""
        # Thread-safe cache check
        async with self._cache_lock:
            # Use cache if available and fresh
            if (
                self._cached_result
                and self._last_check_time
                and (datetime.utcnow() - self._last_check_time).total_seconds()
                < self._cache_duration
            ):
                return self._cached_result

        # Run all checks in parallel
        tasks = [
            self.system_check.check(),
            self.database_check.check(),
            self.redis_check.check(),
        ]
        if detailed:
            # Add more detailed checks if requested
            pass
        check_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        health_checks = []
        failed_checks = 0
        degraded_checks = 0
        for result in check_results:
            if isinstance(result, Exception):
                logger.error(f"Health check failed with exception: {result}")
                health_checks.append(
                    HealthCheckResult(
                        name="unknown",
                        status=HealthStatus.UNHEALTHY,
                        message=f"Check failed: {result!s}",
                        details={"error": str(result)},
                        duration_ms=0,
                        timestamp=datetime.utcnow(),
                    ),
                )
                failed_checks += 1
            else:
                health_checks.append(result)
                if result.status == HealthStatus.UNHEALTHY:
                    failed_checks += 1
                elif result.status == HealthStatus.DEGRADED:
                    degraded_checks += 1

        # Determine overall status
        if failed_checks > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif degraded_checks > 0:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY

        # Calculate uptime
        uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()

        # Create summary
        summary = {
            "total_checks": len(health_checks),
            "healthy_checks": sum(
                1 for c in health_checks if c.status == HealthStatus.HEALTHY
            ),
            "degraded_checks": degraded_checks,
            "failed_checks": failed_checks,
            "uptime_hours": round(uptime_seconds / 3600, 2),
        }

        result = SystemHealth(
            status=overall_status,
            uptime=uptime_seconds,
            checks=health_checks,
            summary=summary,
            timestamp=datetime.utcnow(),
        )
        # Thread-safe cache update
        async with self._cache_lock:
            self._cached_result = result
            self._last_check_time = datetime.utcnow()
        return result

    async def get_readiness(self) -> dict[str, Any]:
        """Check if system is ready to serve requests."""
        health = await self.check_health()
        return {
            "ready": health.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED],
            "status": health.status,
            "checks": {
                check.name: {"status": check.status, "message": check.message}
                for check in health.checks
            },
        }

    async def get_liveness(self) -> dict[str, Any]:
        """Check if system is alive (basic health check)."""
        try:
            # Simple check - just verify the service is responsive
            return {
                "alive": True,
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            }
        except Exception as e:
            logger.error(f"Liveness check failed: {e}")
            return {
                "alive": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }


# Global instance
_health_manager: HealthCheckManager | None = None


def get_health_manager(
    config: dict[str, Any] | None = None,
) -> HealthCheckManager:
    """Get or create health check manager instance."""
    global _health_manager
    if _health_manager is None:
        _health_manager = HealthCheckManager(config)
    return _health_manager
