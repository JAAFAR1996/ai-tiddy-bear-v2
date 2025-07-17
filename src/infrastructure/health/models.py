"""Health check models and enums."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class HealthStatus(str, Enum):
    """Health check status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    name: str
    status: HealthStatus
    message: str
    details: dict[str, Any]
    duration_ms: float
    timestamp: datetime


@dataclass
class SystemHealth:
    """Overall system health status."""

    status: HealthStatus
    uptime: float
    checks: list[HealthCheckResult]
    summary: dict[str, Any]
    timestamp: datetime
