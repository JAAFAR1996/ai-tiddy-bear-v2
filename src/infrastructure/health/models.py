"""Health check models and enums"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any

class HealthStatus(str, Enum):
    """Health check status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

@dataclass
class HealthCheckResult:
    """Result of a health check"""
    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any]
    duration_ms: float
    timestamp: datetime

@dataclass
class SystemHealth:
    """Overall system health status"""
    status: HealthStatus
    uptime: float
    checks: List[HealthCheckResult]
    summary: Dict[str, Any]
    timestamp: datetime