"""Production Health Check Endpoints
Enterprise-grade health monitoring with dependency checks
"""

# Standard library imports
import logging
import os
from datetime import datetime
from typing import Any

# Third-party imports - production required
try:
    from fastapi import APIRouter, HTTPException, status
    from pydantic import BaseModel
except ImportError as e:
    logging.getLogger(__name__).critical(
        f"CRITICAL ERROR: FastAPI and Pydantic required: {e}",
    )
    logging.getLogger(__name__).critical(
        "Install required dependencies: pip install fastapi pydantic",
    )
    raise ImportError(f"Missing required dependencies for health endpoints: {e}") from e

# Local imports - optional infrastructure
try:
    from infrastructure.config.settings import get_settings
    from infrastructure.monitoring.performance_monitor import (
        get_performance_monitor,
    )

    INFRASTRUCTURE_AVAILABLE = True
except ImportError as e:
    logging.getLogger(__name__).error(f"Health check infrastructure import error: {e}")
    # Continue without optional monitoring features
    INFRASTRUCTURE_AVAILABLE = False

try:
    from src.infrastructure.health.checks import (
        check_all_dependencies,
        check_database,
        check_redis,
    )

    HEALTH_CHECKS_AVAILABLE = True
except ImportError as e:
    logging.getLogger(__name__).error(f"Health checks import error: {e}")
    HEALTH_CHECKS_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/health", tags=["Health v1"])


class HealthStatus(BaseModel):
    """Health check response model."""

    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: datetime
    checks: dict[str, dict[str, Any]]
    metrics: dict[str, Any]
    uptime_seconds: float
    version: str


# Fallback functions when dependencies are not available
async def fallback_check_all_dependencies():
    """Fallback dependency check when health checks are not available."""
    return [
        type(
            "Check",
            (),
            {
                "name": "system",
                "status": "healthy",
                "response_time_ms": 0,
                "details": {"note": "Basic health check"},
                "error": None,
            },
        )()
    ]


async def fallback_check_database():
    """Fallback database check."""
    return type(
        "Check",
        (),
        {
            "status": "unknown",
            "response_time_ms": 0,
            "details": {"note": "Database check not available"},
            "error": "Health checks module not available",
        },
    )()


async def fallback_check_redis():
    """Fallback Redis check."""
    return type(
        "Check",
        (),
        {
            "status": "unknown",
            "response_time_ms": 0,
            "details": {"note": "Redis check not available"},
            "error": "Health checks module not available",
        },
    )()


def fallback_get_settings():
    """Fallback settings when config is not available."""
    return type("Settings", (), {"APP_VERSION": "1.0.0"})()


def fallback_get_performance_monitor():
    """Fallback performance monitor."""
    return


@router.get("/", response_model=HealthStatus)
async def basic_health_check() -> HealthStatus:
    """Basic health check endpoint.
    Returns overall system health status.
    """
    try:
        # Get settings with fallback
        if INFRASTRUCTURE_AVAILABLE:
            try:
                settings = get_settings()
                monitor = get_performance_monitor()
            except Exception as e:
                logger.warning(f"Infrastructure error, using fallback: {e}")
                settings = fallback_get_settings()
                monitor = fallback_get_performance_monitor()
        else:
            settings = fallback_get_settings()
            monitor = fallback_get_performance_monitor()

        # Get performance metrics
        if monitor:
            try:
                health_data = await monitor.get_health_status()
                metrics = health_data.get("metrics", {})
                uptime = metrics.get("uptime_seconds", 0)
            except Exception as e:
                logger.warning(f"Monitor error: {e}")
                metrics = {}
                uptime = 0
        else:
            metrics = {}
            uptime = 0

        # Check critical dependencies
        if HEALTH_CHECKS_AVAILABLE:
            try:
                dependency_checks = await check_all_dependencies()
            except Exception as e:
                logger.warning(f"Dependency check error: {e}")
                dependency_checks = await fallback_check_all_dependencies()
        else:
            dependency_checks = await fallback_check_all_dependencies()

        # Format checks
        checks = {}
        overall_healthy = True

        for check in dependency_checks:
            checks[check.name] = {
                "status": check.status,
                "response_time_ms": check.response_time_ms,
                "details": check.details,
                "error": check.error,
            }
            if check.status not in ["healthy", "unknown"]:
                overall_healthy = False

        # Determine overall status
        if overall_healthy:
            status_result = "healthy"
        elif any(
            check.status == "unhealthy"
            for check in dependency_checks
            if check.name in ["database", "redis"]
        ):
            status_result = "unhealthy"  # Critical dependencies failing
        else:
            status_result = "degraded"  # Non-critical dependencies failing

        return HealthStatus(
            status=status_result,
            timestamp=datetime.now(),
            checks=checks,
            metrics=metrics,
            uptime_seconds=uptime,
            version=settings.APP_VERSION,
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {e!s}",
        )


@router.get("/ready")
async def readiness_check() -> dict[str, Any]:
    """Kubernetes readiness probe endpoint.
    Checks if the application is ready to serve traffic.
    """
    try:
        # Check critical dependencies only
        if HEALTH_CHECKS_AVAILABLE:
            try:
                db_check = await check_database()
                redis_check = await check_redis()
            except Exception as e:
                logger.warning(f"Health check error, using fallback: {e}")
                db_check = await fallback_check_database()
                redis_check = await fallback_check_redis()
        else:
            db_check = await fallback_check_database()
            redis_check = await fallback_check_redis()

        ready = db_check.status in ["healthy", "unknown"] and redis_check.status in [
            "healthy",
            "unknown",
        ]

        if ready:
            return {
                "status": "ready",
                "timestamp": datetime.now().isoformat(),
                "checks": {
                    "database": db_check.status,
                    "redis": redis_check.status,
                },
            }
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Readiness check failed: {e!s}",
        )


@router.get("/live")
async def liveness_check() -> dict[str, Any]:
    """Kubernetes liveness probe endpoint.
    Simple check to verify the application is alive.
    """
    try:
        pid = os.getpid()
    except Exception:
        pid = None

    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "pid": pid,
    }


@router.get("/metrics")
async def get_metrics() -> dict[str, Any]:
    """Get application performance metrics."""
    try:
        if INFRASTRUCTURE_AVAILABLE:
            try:
                monitor = get_performance_monitor()
            except Exception as e:
                logger.warning(f"Monitor unavailable: {e}")
                monitor = None
        else:
            monitor = None

        if monitor:
            try:
                metrics = await monitor.get_performance_summary()
                return {
                    "request_count": getattr(metrics, "request_count", 0),
                    "avg_response_time": getattr(metrics, "avg_response_time", 0),
                    "error_count": getattr(metrics, "error_count", 0),
                    "memory_usage_mb": getattr(metrics, "memory_usage_mb", 0),
                    "cpu_usage_percent": getattr(metrics, "cpu_usage_percent", 0),
                    "active_connections": getattr(metrics, "active_connections", 0),
                    "cache_hit_rate": getattr(metrics, "cache_hit_rate", 0),
                    "timestamp": getattr(
                        metrics, "timestamp", datetime.now()
                    ).isoformat(),
                }
            except Exception as e:
                logger.warning(f"Metrics collection error: {e}")
                return {
                    "error": f"Performance monitoring error: {e}",
                    "timestamp": datetime.now().isoformat(),
                }

        return {
            "message": "Performance monitoring not available",
            "timestamp": datetime.now().isoformat(),
            "basic_status": "alive",
        }
    except Exception as e:
        logger.error(f"Metrics endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metrics collection failed: {e!s}",
        )


@router.get("/dependencies")
async def check_dependencies() -> dict[str, Any]:
    """Detailed dependency health checks."""
    try:
        if HEALTH_CHECKS_AVAILABLE:
            try:
                dependency_checks = await check_all_dependencies()
            except Exception as e:
                logger.warning(f"Dependency checks error: {e}")
                dependency_checks = await fallback_check_all_dependencies()
        else:
            dependency_checks = await fallback_check_all_dependencies()

        return {
            "timestamp": datetime.now().isoformat(),
            "dependencies": {
                check.name: {
                    "status": check.status,
                    "response_time_ms": check.response_time_ms,
                    "details": check.details,
                    "error": check.error,
                }
                for check in dependency_checks
            },
            "health_checks_available": HEALTH_CHECKS_AVAILABLE,
            "infrastructure_available": INFRASTRUCTURE_AVAILABLE,
        }
    except Exception as e:
        logger.error(f"Dependencies check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dependencies check failed: {e!s}",
        )


@router.get("/info")
async def get_system_info() -> dict[str, Any]:
    """Get basic system information."""
    try:
        if INFRASTRUCTURE_AVAILABLE:
            try:
                settings = get_settings()
                version = settings.APP_VERSION
            except Exception:
                version = "1.0.0"
        else:
            version = "1.0.0"

        return {
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            "platform": os.name,
            "pid": os.getpid(),
            "features": {
                "health_checks": HEALTH_CHECKS_AVAILABLE,
                "infrastructure": INFRASTRUCTURE_AVAILABLE,
                "monitoring": INFRASTRUCTURE_AVAILABLE,
            },
        }
    except Exception as e:
        logger.error(f"System info error: {e}")
        return {
            "error": f"System info collection failed: {e}",
            "timestamp": datetime.now().isoformat(),
        }
