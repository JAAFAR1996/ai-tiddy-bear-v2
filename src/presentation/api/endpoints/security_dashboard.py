"""Security Dashboard API Endpoints

This module provides API endpoints for the security monitoring dashboard,
allowing operations teams to monitor security events, system health, and
threat intelligence in real-time.

SECURITY FEATURES:
- Real-time security metrics and events
- COPPA-compliant reporting (no PII exposure)
- Comprehensive system health monitoring
- Threat intelligence dashboard
- Audit trail access for compliance
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.infrastructure.logging_config import get_logger
from src.infrastructure.monitoring.security_monitoring_system import (
    AlertLevel,
    SecurityEventType,
    SecurityMonitoringSystem,
    get_security_monitoring_system,
)

logger = get_logger(__name__, component="security_dashboard")

router = APIRouter(prefix="/api/v1/security", tags=["Security Dashboard"])


class SecurityDashboardResponse(BaseModel):
    """Response model for security dashboard data."""

    metrics: Dict[str, Any] = Field(..., description="Security metrics summary")
    recent_events: List[Dict[str, Any]] = Field(
        ..., description="Recent security events"
    )
    system_health: Dict[str, Any] = Field(..., description="System health status")
    threat_summary: Dict[str, Any] = Field(
        ..., description="Threat intelligence summary"
    )
    timestamp: str = Field(..., description="Dashboard data timestamp")


class SecurityEventResponse(BaseModel):
    """Response model for security events."""

    event_id: str
    event_type: str
    alert_level: str
    timestamp: str
    child_related: bool
    source_ip: Optional[str] = None
    endpoint: Optional[str] = None
    response_action: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class SystemHealthResponse(BaseModel):
    """Response model for system health."""

    vault_health_score: float = Field(..., description="Vault health score (0-100)")
    average_response_time: float = Field(..., description="Average response time in ms")
    total_events: int = Field(..., description="Total security events")
    critical_events: int = Field(..., description="Critical security events")
    child_safety_alerts: int = Field(..., description="Child safety alerts")
    uptime_percentage: float = Field(..., description="System uptime percentage")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")


async def get_security_monitoring(request: Request) -> SecurityMonitoringSystem:
    """Dependency to get security monitoring system."""
    try:
        # Try to get from app state first (if initialized during startup)
        if hasattr(request.app.state, "security_monitoring"):
            return request.app.state.security_monitoring

        # Fallback to global instance
        return await get_security_monitoring_system()
    except Exception as e:
        logger.error(f"Failed to get security monitoring system: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Security monitoring system unavailable",
        )


@router.get(
    "/dashboard",
    response_model=SecurityDashboardResponse,
    summary="Get comprehensive security dashboard data",
    description="Returns real-time security metrics, events, and system health data",
)
async def get_security_dashboard(
    monitoring: SecurityMonitoringSystem = Depends(get_security_monitoring),
) -> SecurityDashboardResponse:
    """Get comprehensive security dashboard data."""
    try:
        logger.info("Security dashboard data requested")

        dashboard_data = monitoring.get_security_dashboard_data()

        return SecurityDashboardResponse(
            metrics=dashboard_data["metrics"],
            recent_events=dashboard_data["recent_events"],
            system_health=dashboard_data["system_health"],
            threat_summary=dashboard_data["threat_summary"],
            timestamp=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error(f"Failed to get security dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security dashboard data",
        )


@router.get(
    "/health",
    response_model=SystemHealthResponse,
    summary="Get system health status",
    description="Returns current system health metrics and status",
)
async def get_system_health(
    monitoring: SecurityMonitoringSystem = Depends(get_security_monitoring),
) -> SystemHealthResponse:
    """Get system health status."""
    try:
        logger.info("System health check requested")

        health_data = await monitoring.perform_system_health_check()

        return SystemHealthResponse(
            vault_health_score=health_data["vault_health_score"],
            average_response_time=health_data["average_response_time"],
            total_events=health_data["total_events"],
            critical_events=health_data["critical_events"],
            child_safety_alerts=health_data["child_safety_alerts"],
            uptime_percentage=100.0,  # TODO: Implement actual uptime calculation
            last_updated=health_data["last_updated"],
        )

    except Exception as e:
        logger.error(f"Failed to get system health data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system health data",
        )


@router.get(
    "/events",
    response_model=List[SecurityEventResponse],
    summary="Get security events",
    description="Returns security events with optional filtering",
)
async def get_security_events(
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of events to return"
    ),
    event_type: Optional[SecurityEventType] = Query(
        None, description="Filter by event type"
    ),
    alert_level: Optional[AlertLevel] = Query(
        None, description="Filter by alert level"
    ),
    child_related: Optional[bool] = Query(
        None, description="Filter child-related events"
    ),
    hours_back: int = Query(24, ge=1, le=168, description="Hours back to search"),
    monitoring: SecurityMonitoringSystem = Depends(get_security_monitoring),
) -> List[SecurityEventResponse]:
    """Get security events with optional filtering."""
    try:
        logger.info(
            f"Security events requested: limit={limit}, event_type={event_type}, alert_level={alert_level}"
        )

        # Get all recent events
        all_events = list(monitoring.security_events)

        # Filter by time
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        filtered_events = [
            event for event in all_events if event.timestamp >= cutoff_time
        ]

        # Apply filters
        if event_type:
            filtered_events = [
                event for event in filtered_events if event.event_type == event_type
            ]

        if alert_level:
            filtered_events = [
                event for event in filtered_events if event.alert_level == alert_level
            ]

        if child_related is not None:
            filtered_events = [
                event
                for event in filtered_events
                if event.child_related == child_related
            ]

        # Sort by timestamp (most recent first) and limit
        filtered_events.sort(key=lambda x: x.timestamp, reverse=True)
        filtered_events = filtered_events[:limit]

        # Convert to response format
        return [
            SecurityEventResponse(
                event_id=event.event_id,
                event_type=event.event_type.value,
                alert_level=event.alert_level.value,
                timestamp=event.timestamp.isoformat(),
                child_related=event.child_related,
                source_ip=event.source_ip,
                endpoint=event.endpoint,
                response_action=event.response_action,
                details=event.details,
            )
            for event in filtered_events
        ]

    except Exception as e:
        logger.error(f"Failed to get security events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security events",
        )


@router.get(
    "/metrics",
    summary="Get security metrics",
    description="Returns current security metrics and statistics",
)
async def get_security_metrics(
    monitoring: SecurityMonitoringSystem = Depends(get_security_monitoring),
) -> Dict[str, Any]:
    """Get current security metrics."""
    try:
        logger.info("Security metrics requested")

        dashboard_data = monitoring.get_security_dashboard_data()

        # Return just the metrics portion
        return {
            "metrics": dashboard_data["metrics"],
            "threat_summary": dashboard_data["threat_summary"],
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get security metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security metrics",
        )


@router.get(
    "/threats/summary",
    summary="Get threat intelligence summary",
    description="Returns threat intelligence and attack pattern analysis",
)
async def get_threat_summary(
    monitoring: SecurityMonitoringSystem = Depends(get_security_monitoring),
) -> Dict[str, Any]:
    """Get threat intelligence summary."""
    try:
        logger.info("Threat summary requested")

        dashboard_data = monitoring.get_security_dashboard_data()

        return {
            "threat_summary": dashboard_data["threat_summary"],
            "analysis_period": "Last 1000 events",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get threat summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve threat summary",
        )


@router.get(
    "/child-safety/events",
    response_model=List[SecurityEventResponse],
    summary="Get child safety events",
    description="Returns events specifically related to child safety and COPPA compliance",
)
async def get_child_safety_events(
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of events to return"
    ),
    hours_back: int = Query(24, ge=1, le=168, description="Hours back to search"),
    monitoring: SecurityMonitoringSystem = Depends(get_security_monitoring),
) -> List[SecurityEventResponse]:
    """Get child safety related events."""
    try:
        logger.info(
            f"Child safety events requested: limit={limit}, hours_back={hours_back}"
        )

        # Get all recent events
        all_events = list(monitoring.security_events)

        # Filter for child-related events
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        child_events = [
            event
            for event in all_events
            if event.child_related and event.timestamp >= cutoff_time
        ]

        # Sort by timestamp (most recent first) and limit
        child_events.sort(key=lambda x: x.timestamp, reverse=True)
        child_events = child_events[:limit]

        # Convert to response format (with extra privacy protection)
        return [
            SecurityEventResponse(
                event_id=event.event_id,
                event_type=event.event_type.value,
                alert_level=event.alert_level.value,
                timestamp=event.timestamp.isoformat(),
                child_related=True,
                source_ip=event.source_ip,
                endpoint=event.endpoint,
                response_action=event.response_action,
                details={
                    k: v
                    for k, v in (event.details or {}).items()
                    if k
                    not in [
                        "child_id",
                        "child_name",
                        "personal_info",
                    ]  # Extra PII protection
                },
            )
            for event in child_events
        ]

    except Exception as e:
        logger.error(f"Failed to get child safety events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve child safety events",
        )


@router.post(
    "/alerts/webhook",
    summary="Security alert webhook",
    description="Webhook endpoint for external security alert integration",
)
async def security_alert_webhook(
    alert_data: Dict[str, Any],
    monitoring: SecurityMonitoringSystem = Depends(get_security_monitoring),
) -> JSONResponse:
    """Webhook endpoint for external security alerts."""
    try:
        logger.info("Security alert webhook triggered")

        # Process external alert
        # This could integrate with external security tools, SIEM systems, etc.

        logger.info(
            f"External security alert received: {alert_data.get('alert_type', 'unknown')}"
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "received",
                "message": "Security alert processed",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    except Exception as e:
        logger.error(f"Failed to process security alert webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process security alert",
        )


# Health check endpoint for monitoring systems
@router.get(
    "/healthz",
    summary="Security monitoring health check",
    description="Health check endpoint for monitoring the security monitoring system",
)
async def security_monitoring_health(
    monitoring: SecurityMonitoringSystem = Depends(get_security_monitoring),
) -> JSONResponse:
    """Health check for security monitoring system."""
    try:
        health_data = await monitoring.perform_system_health_check()

        is_healthy = (
            health_data["vault_health_score"] > 80
            and health_data["average_response_time"] < 5000
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK
            if is_healthy
            else status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "healthy" if is_healthy else "unhealthy",
                "vault_health_score": health_data["vault_health_score"],
                "average_response_time": health_data["average_response_time"],
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    except Exception as e:
        logger.error(f"Security monitoring health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
