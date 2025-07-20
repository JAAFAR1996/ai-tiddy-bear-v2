from datetime import datetime, timedelta
from typing import Any

from src.infrastructure.logging_config import get_logger
from src.infrastructure.monitoring import (
    AlertStatus,
    monitoring_service,
)
from src.infrastructure.pagination import (
    PaginationService,
)

logger = get_logger(__name__, component="api")

# Import FastAPI dependencies
try:
    from fastapi import APIRouter, HTTPException, Query, status

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    logger.warning("FastAPI not available, using mock classes")

    class APIRouter:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def get(self, path: str, **kwargs):
            def decorator(func):
                return func

            return decorator


class MonitoringDashboardService:
    """Service for monitoring dashboard operations."""

    def __init__(self) -> None:
        """Initialize monitoring dashboard service."""
        self.pagination_service = PaginationService()
        logger.info("Monitoring dashboard service initialized")

    async def get_system_health(self) -> dict[str, Any]:
        """Get overall system health status."""
        try:
            metrics_summary = monitoring_service.get_metrics_summary()

            # Calculate health indicators
            health_status = self._calculate_health_status(metrics_summary)

            # Get recent alerts
            recent_alerts = self._get_recent_alerts(hours=24)

            # Get child safety summary
            safety_summary = self._get_child_safety_summary()

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_health": health_status,
                "metrics_summary": metrics_summary,
                "recent_alerts": recent_alerts,
                "child_safety": safety_summary,
                "system_status": (
                    "operational" if health_status["score"] > 0.8 else "degraded"
                ),
            }
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get system health: {e!s}",
            )

    async def get_metrics_dashboard(self, time_range: str = "1h") -> dict[str, Any]:
        """Get metrics for dashboard display."""
        try:
            # Parse time range
            hours = self._parse_time_range(time_range)
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            # Get metrics data
            dashboard_metrics = {}
            for (
                metric_name,
                metric_values,
            ) in monitoring_service.metrics.items():
                recent_values = [m for m in metric_values if m.timestamp > cutoff_time]

                if recent_values:
                    dashboard_metrics[metric_name] = {
                        "current_value": recent_values[-1].value,
                        "min_value": min(m.value for m in recent_values),
                        "max_value": max(m.value for m in recent_values),
                        "avg_value": sum(m.value for m in recent_values)
                        / len(recent_values),
                        "data_points": len(recent_values),
                        "last_updated": recent_values[-1].timestamp.isoformat(),
                    }

            return {
                "time_range": time_range,
                "metrics": dashboard_metrics,
                "generated_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting metrics dashboard: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get metrics dashboard: {e!s}",
            )

    async def get_child_safety_dashboard(self) -> dict[str, Any]:
        """Get child safety monitoring dashboard."""
        try:
            safety_monitor = monitoring_service.child_safety_monitor

            # Get recent safety events
            recent_events = list(safety_monitor.safety_events)[-100:]  # Last 100 events

            # Group events by type
            event_counts = {}
            severity_counts = {}
            for event in recent_events:
                event_type = event["event_type"]
                severity = event["severity"]
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

            # Get active safety alerts
            active_safety_alerts = [
                alert
                for alert in safety_monitor.safety_alerts.values()
                if alert.get("severity") in ["HIGH", "CRITICAL", "EMERGENCY"]
            ]

            return {
                "total_events": len(recent_events),
                "event_types": event_counts,
                "severity_distribution": severity_counts,
                "active_alerts": len(active_safety_alerts),
                "critical_alerts": active_safety_alerts,
                "last_updated": datetime.utcnow().isoformat(),
                "monitoring_status": "active",
            }
        except Exception as e:
            logger.error(f"Error getting child safety dashboard: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get child safety dashboard: {e!s}",
            )

    async def get_security_dashboard(self) -> dict[str, Any]:
        """Get security monitoring dashboard."""
        try:
            # Get recent security events
            recent_security = list(monitoring_service.suspicious_activities)[-100:]

            # Group by event type
            security_counts = {}
            for event in recent_security:
                event_type = event["event_type"]
                security_counts[event_type] = security_counts.get(event_type, 0) + 1

            # Get failed auth attempts
            failed_auth_summary = dict(monitoring_service.failed_auth_attempts)

            # Calculate threat level
            threat_level = self._calculate_threat_level(
                security_counts, failed_auth_summary
            )

            return {
                "total_security_events": len(recent_security),
                "event_types": security_counts,
                "failed_auth_attempts": failed_auth_summary,
                "threat_level": threat_level,
                "last_updated": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting security dashboard: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get security dashboard: {e!s}",
            )

    async def get_coppa_compliance_dashboard(self) -> dict[str, Any]:
        """Get COPPA compliance monitoring dashboard."""
        try:
            # Get recent COPPA events
            recent_coppa = list(monitoring_service.data_access_logs)[-100:]
            consent_violations = list(monitoring_service.consent_violations)

            # Group events by type
            coppa_counts = {}
            for event in recent_coppa:
                event_type = event["event_type"]
                coppa_counts[event_type] = coppa_counts.get(event_type, 0) + 1

            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(
                coppa_counts, consent_violations
            )

            return {
                "total_coppa_events": len(recent_coppa),
                "event_types": coppa_counts,
                "consent_violations": len(consent_violations),
                "compliance_score": compliance_score,
                "compliance_status": (
                    "compliant" if compliance_score > 0.9 else "needs_attention"
                ),
                "last_updated": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting COPPA compliance dashboard: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get COPPA compliance dashboard: {e!s}",
            )

    def _calculate_health_status(
        self, metrics_summary: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate overall system health status."""
        health_score = 1.0
        issues = []

        # Check error rate
        latest_metrics = metrics_summary.get("latest_metrics", {})
        error_rate = latest_metrics.get("error_rate", 0)
        if error_rate > 0.05:  # 5% threshold
            health_score -= 0.2
            issues.append(f"High error rate: {error_rate:.2%}")

        # Check response time
        avg_response_time = latest_metrics.get("avg_response_time", 0)
        if avg_response_time > 2.0:  # 2 second threshold
            health_score -= 0.1
            issues.append(f"Slow response time: {avg_response_time:.2f}s")

        # Check memory usage
        memory_usage = latest_metrics.get("memory_usage", 0)
        if memory_usage > 0.8:  # 80% threshold
            health_score -= 0.15
            issues.append(f"High memory usage: {memory_usage:.1%}")

        # Check child safety events
        if metrics_summary.get("child_safety_events", 0) > 0:
            health_score -= 0.05
            issues.append("Recent child safety events detected")

        health_score = max(0.0, min(1.0, health_score))

        return {
            "score": health_score,
            "status": self._get_health_status_text(health_score),
            "issues": issues,
            "last_calculated": datetime.utcnow().isoformat(),
        }

    def _get_health_status_text(self, score: float) -> str:
        """Convert health score to text status."""
        if score >= 0.9:
            return "excellent"
        if score >= 0.8:
            return "good"
        if score >= 0.6:
            return "fair"
        if score >= 0.4:
            return "poor"
        return "critical"

    def _get_recent_alerts(self, hours: int = 24) -> list[dict[str, Any]]:
        """Get recent alerts within specified hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_alerts = []

        for alert in monitoring_service.alerts.values():
            if (
                alert.last_triggered
                and alert.last_triggered > cutoff_time
                and alert.status == AlertStatus.ACTIVE
            ):
                recent_alerts.append(
                    {
                        "alert_id": alert.alert_id,
                        "name": alert.name,
                        "description": alert.description,
                        "severity": alert.severity.value,
                        "last_triggered": alert.last_triggered.isoformat(),
                        "trigger_count": alert.trigger_count,
                    }
                )

        return sorted(recent_alerts, key=lambda x: x["last_triggered"], reverse=True)

    def _get_child_safety_summary(self) -> dict[str, Any]:
        """Get child safety monitoring summary."""
        safety_monitor = monitoring_service.child_safety_monitor

        # Count recent events (last 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        recent_events = [
            event
            for event in safety_monitor.safety_events
            if datetime.fromisoformat(event["timestamp"]) > cutoff_time
        ]

        return {
            "total_events_24h": len(recent_events),
            "active_safety_alerts": len(safety_monitor.safety_alerts),
            "monitoring_active": True,
            "last_event": (recent_events[-1]["timestamp"] if recent_events else None),
        }

    def _parse_time_range(self, time_range: str) -> int:
        """Parse time range string to hours."""
        time_map = {
            "1h": 1,
            "6h": 6,
            "12h": 12,
            "24h": 24,
            "7d": 168,  # 7 days
            "30d": 720,  # 30 days
        }
        return time_map.get(time_range, 1)

    def _calculate_threat_level(
        self, security_counts: dict[str, int], failed_auth: dict[str, int]
    ) -> str:
        """Calculate current threat level."""
        total_security_events = sum(security_counts.values())
        total_failed_auth = sum(failed_auth.values())

        if total_security_events > 50 or total_failed_auth > 100:
            return "high"
        if total_security_events > 20 or total_failed_auth > 50:
            return "medium"
        if total_security_events > 5 or total_failed_auth > 10:
            return "low"
        return "minimal"

    def _calculate_compliance_score(
        self, coppa_counts: dict[str, int], violations: list[dict[str, Any]]
    ) -> float:
        """Calculate COPPA compliance score."""
        total_events = sum(coppa_counts.values())
        violation_count = len(violations)

        if total_events == 0:
            return 1.0

        # Calculate compliance based on violation ratio
        violation_ratio = violation_count / total_events
        compliance_score = 1.0 - min(violation_ratio, 1.0)

        return max(0.0, compliance_score)


# Initialize service
dashboard_service = MonitoringDashboardService()

# Create router
router = APIRouter(prefix="/api/v1/monitoring", tags=["Monitoring Dashboard"])

if FASTAPI_AVAILABLE:

    @router.get("/health")
    async def get_system_health():
        """Get overall system health status."""
        return await dashboard_service.get_system_health()

    @router.get("/metrics")
    async def get_metrics_dashboard(
        time_range: str = Query(
            "1h",
            regex="^(1h|6h|12h|24h|7d|30d)$",
            description="Time range for metrics",
        )
    ):
        """Get metrics dashboard data."""
        return await dashboard_service.get_metrics_dashboard(time_range)

    @router.get("/child-safety")
    async def get_child_safety_dashboard():
        """Get child safety monitoring dashboard."""
        return await dashboard_service.get_child_safety_dashboard()

    @router.get("/security")
    async def get_security_dashboard():
        """Get security monitoring dashboard."""
        return await dashboard_service.get_security_dashboard()

    @router.get("/coppa-compliance")
    async def get_coppa_compliance_dashboard():
        """Get COPPA compliance monitoring dashboard."""
        return await dashboard_service.get_coppa_compliance_dashboard()

    @router.get("/alerts")
    async def get_active_alerts(
        severity: str | None = Query(
            None,
            regex="^(low|medium|high|critical|emergency)$",
            description="Filter by alert severity",
        )
    ):
        """Get active alerts with optional severity filter."""
        try:
            active_alerts = []
            for alert in monitoring_service.alerts.values():
                if alert.status == AlertStatus.ACTIVE:
                    if severity is None or alert.severity.value == severity:
                        active_alerts.append(
                            {
                                "alert_id": alert.alert_id,
                                "name": alert.name,
                                "description": alert.description,
                                "severity": alert.severity.value,
                                "created_at": alert.created_at.isoformat(),
                                "last_triggered": (
                                    alert.last_triggered.isoformat()
                                    if alert.last_triggered
                                    else None
                                ),
                                "trigger_count": alert.trigger_count,
                                "metric_name": alert.metric_name,
                                "threshold": alert.threshold,
                            }
                        )

            return {
                "alerts": sorted(
                    active_alerts, key=lambda x: x["severity"], reverse=True
                ),
                "total_count": len(active_alerts),
                "generated_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get active alerts: {e!s}",
            )


# Export for use in main application
__all__ = ["MonitoringDashboardService", "dashboard_service", "router"]
