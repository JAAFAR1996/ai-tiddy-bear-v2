from datetime import datetime
from typing import Optional
import logging
import time
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import HealthCheckResult, HealthStatus

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="infrastructure")


class DatabaseHealthCheck:
    """Database connectivity and performance health check."""

    def __init__(
        self, database_session: Optional[AsyncSession] = None
    ) -> None:
        self.database_session = database_session

    async def check(self) -> HealthCheckResult:
        """Check database health."""
        start_time = time.time()
        try:
            if not self.database_session:
                return HealthCheckResult(
                    name="database",
                    status=HealthStatus.UNHEALTHY,
                    message="Database not configured",
                    details={"error": "No database session available"},
                    duration_ms=(time.time() - start_time) * 1000,
                    timestamp=datetime.utcnow(),
                )

            # Test database connectivity
            async with self.database_session() as session:
                result = await session.execute(text("SELECT 1"))
                result.scalar()

                # Check tables exist
                tables_result = await session.execute(
                    text(
                        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"
                    )
                )
                table_count = tables_result.scalar()

                # Check connection pool stats
                pool_stats = {
                    "size": (
                        session.bind.pool.size()
                        if hasattr(session.bind, "pool")
                        else 0
                    ),
                    "checked_in": (
                        session.bind.pool.checkedin()
                        if hasattr(session.bind, "pool")
                        else 0
                    ),
                    "overflow": (
                        session.bind.pool.overflow()
                        if hasattr(session.bind, "pool")
                        else 0
                    ),
                }

                duration = (time.time() - start_time) * 1000
                if duration > 100:  # Slow query
                    status = HealthStatus.DEGRADED
                    message = f"Database responding slowly ({duration:.0f}ms)"
                else:
                    status = HealthStatus.HEALTHY
                    message = "Database is healthy"

                return HealthCheckResult(
                    name="database",
                    status=status,
                    message=message,
                    details={
                        "tables": table_count,
                        "response_time_ms": duration,
                        "pool_stats": pool_stats,
                    },
                    duration_ms=duration,
                    timestamp=datetime.utcnow(),
                )
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return HealthCheckResult(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database check failed: {e!s}",
                details={"error": str(e)},
                duration_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
            )
