"""
from datetime import datetime
from typing import Dict, Any
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.infrastructure.health.health_checks import (
"""

Health Check API Endpoints for AI Teddy Bear
Production - ready health monitoring endpoints with detailed diagnostics
"""
    get_health_manager,
    HealthCheckManager,
    SystemHealth,
    HealthStatus)
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="api")

router = APIRouter(tags=["Health"])

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    uptime: float
    version: str = "1.0.0"
    environment: str = "production"

class DetailedHealthResponse(BaseModel):
    """Detailed health check response model"""
    status: str
    timestamp: str
    uptime: float
    uptime_formatted: str
    version: str = "1.0.0"
    environment: str = "production"
    checks: Dict[str, Any]
    summary: Dict[str, Any]

class ReadinessResponse(BaseModel):
    """Readiness check response model"""
    ready: bool
    timestamp: str
    critical_services: Dict[str, str]

class LivenessResponse(BaseModel):
    """Liveness check response model"""
    alive: bool
    timestamp: str
    uptime: float

@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint
    Returns simple health status for load balancer health checks
    """
    try:
        health_manager = get_health_manager()
        system_health = await health_manager.run_all_checks()
        
        # Return simplified response for load balancer
        is_healthy = system_health.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
        response = HealthResponse(
            status="healthy" if is_healthy else "unhealthy",
            timestamp=system_health.timestamp.isoformat(),
            uptime=system_health.uptime
        )
        
        # Return appropriate HTTP status code
        status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return JSONResponse(
            content=response.dict(),
            status_code=status_code
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": "Health check system failure"
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check() -> DetailedHealthResponse:
    """
    Detailed health check endpoint
    Returns comprehensive health information for monitoring and debugging
    """
    try:
        health_manager = get_health_manager()
        system_health = await health_manager.run_all_checks()
        
        # Convert check results to dict format
        checks_dict = {}
        for check in system_health.checks:
            checks_dict[check.name] = {
                "status": check.status,
                "message": check.message,
                "duration_ms": check.duration_ms,
                "timestamp": check.timestamp.isoformat(),
                "details": check.details
            }
        
        response = DetailedHealthResponse(
            status=system_health.status,
            timestamp=system_health.timestamp.isoformat(),
            uptime=system_health.uptime,
            uptime_formatted=system_health.summary.get("uptime_formatted", ""),
            checks=checks_dict,
            summary=system_health.summary
        )
        
        # Return appropriate HTTP status code
        is_healthy = system_health.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
        status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return JSONResponse(
            content=response.dict(),
            status_code=status_code
        )
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": "Health check system failure",
                "checks": {},
                "summary": {}
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness_check():
    """
    Kubernetes readiness probe endpoint
    Checks if the application is ready to serve traffic
    """
    try:
        health_manager = get_health_manager()
        system_health = await health_manager.run_all_checks()
        
        # Check critical services for readiness
        critical_services = {}
        ready = True
        
        for check in system_health.checks:
            if check.name in ["database", "redis"]:  # Critical services
                critical_services[check.name] = check.status
                if check.status in [HealthStatus.CRITICAL, HealthStatus.UNHEALTHY]:
                    ready = False
        
        response = ReadinessResponse(
            ready=ready,
            timestamp=datetime.utcnow().isoformat(),
            critical_services=critical_services
        )
        
        status_code = status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return JSONResponse(
            content=response.dict(),
            status_code=status_code
        )
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            content={
                "ready": False,
                "timestamp": datetime.utcnow().isoformat(),
                "critical_services": {},
                "error": "Readiness check failure"
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

@router.get("/health/live", response_model=LivenessResponse)
async def liveness_check():
    """
    Kubernetes liveness probe endpoint
    Simple check to verify the application process is alive
    """
    try:
        health_manager = get_health_manager()
        # Simple check - if we can get the manager and calculate uptime, we're alive
        uptime = health_manager.start_time if hasattr(health_manager, 'start_time') else 0
        current_uptime = datetime.utcnow().timestamp() - uptime if uptime else 0
        
        response = LivenessResponse(
            alive=True,
            timestamp=datetime.utcnow().isoformat(),
            uptime=current_uptime
        )
        
        return JSONResponse(
            content=response.dict(),
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        # Even if there's an error, if we can respond, we're technically alive
        return JSONResponse(
            content={
                "alive": True,  # Process is responding
                "timestamp": datetime.utcnow().isoformat(),
                "uptime": 0,
                "note": "Error in liveness check but process responding"
            },
            status_code=status.HTTP_200_OK
        )

@router.get("/health/startup")
async def startup_check():
    """
    Kubernetes startup probe endpoint
    Checks if the application has finished starting up
    """
    try:
        health_manager = get_health_manager()
        system_health = await health_manager.run_all_checks()
        
        # Consider startup complete if critical services are at least degraded
        startup_complete = True
        startup_issues = []
        
        for check in system_health.checks:
            if check.name in ["database"]:  # Essential for startup
                if check.status in [HealthStatus.CRITICAL, HealthStatus.UNHEALTHY]:
                    startup_complete = False
                    startup_issues.append(f"{check.name}: {check.message}")
        
        response = {
            "startup_complete": startup_complete,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": system_health.uptime,
            "issues": startup_issues
        }
        
        status_code = status.HTTP_200_OK if startup_complete else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return JSONResponse(
            content=response,
            status_code=status_code
        )
    except Exception as e:
        logger.error(f"Startup check failed: {e}")
        return JSONResponse(
            content={
                "startup_complete": False,
                "timestamp": datetime.utcnow().isoformat(),
                "uptime": 0,
                "issues": [f"Startup check failure: {str(e)}"]
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

@router.get("/health/metrics")
async def health_metrics():
    """
    Prometheus - compatible metrics endpoint
    Returns health metrics in a format suitable for monitoring
    """
    try:
        health_manager = get_health_manager()
        system_health = await health_manager.run_all_checks()
        
        # Build metrics in Prometheus format
        metrics = []
        
        # Overall health status (1 = healthy, 0 = unhealthy)
        overall_healthy = 1 if system_health.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED] else 0
        metrics.append(f'ai_teddy_health_status {overall_healthy}')
        
        # Individual check statuses
        status_values = {
            HealthStatus.HEALTHY: 1,
            HealthStatus.DEGRADED: 0.5,
            HealthStatus.UNHEALTHY: 0,
            HealthStatus.CRITICAL: -1
        }
        
        for check in system_health.checks:
            status_value = status_values.get(check.status, 0)
            metrics.append(f'ai_teddy_health_check_status{{check="{check.name}"}} {status_value}')
            metrics.append(f'ai_teddy_health_check_duration_ms{{check="{check.name}"}} {check.duration_ms}')
        
        # System metrics
        metrics.append(f'ai_teddy_uptime_seconds {system_health.uptime}')
        metrics.append(f'ai_teddy_health_checks_total {len(system_health.checks)}')
        
        # Add resource metrics if available
        for check in system_health.checks:
            if check.name == "system_resources" and "details" in check.details:
                details = check.details["details"]
                if "cpu_percent" in details:
                    metrics.append(f'ai_teddy_cpu_usage_percent {details["cpu_percent"]}')
                if "memory_percent" in details:
                    metrics.append(f'ai_teddy_memory_usage_percent {details["memory_percent"]}')
                if "disk_percent" in details:
                    metrics.append(f'ai_teddy_disk_usage_percent {details["disk_percent"]}')
        
        # Return as plain text
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse('\n'.join(metrics) + '\n')
    except Exception as e:
        logger.error(f"Health metrics failed: {e}")
        return PlainTextResponse(
            f'ai_teddy_health_status 0\n'
            f'ai_teddy_health_error{{error="metrics_failure"}} 1\n',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )