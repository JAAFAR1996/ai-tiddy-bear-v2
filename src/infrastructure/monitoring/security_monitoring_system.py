"""Production-Grade Security Monitoring System for AI Teddy Bear Project

This module implements a comprehensive security monitoring system that:
- Real-time threat detection and alerting
- COPPA compliance monitoring for child data
- Vault health and secrets monitoring
- Security incident tracking and response
- Performance and availability monitoring
- Audit trail generation with secure logging

CRITICAL SECURITY FEATURES:
- NO sensitive data logged (COPPA compliant)
- Real-time security event correlation
- Automated incident response triggers
- Comprehensive audit trails
- Performance degradation detection
- Child safety monitoring with zero tolerance
"""

import asyncio
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security_monitoring")


class SecurityEventType(str, Enum):
    """Types of security events for classification and handling."""

    # Authentication & Authorization
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    AUTH_BRUTE_FORCE = "auth_brute_force"
    UNAUTHORIZED_ACCESS = "unauthorized_access"

    # Input Validation & Injection Attacks
    SQL_INJECTION_ATTEMPT = "sql_injection_attempt"
    XSS_ATTEMPT = "xss_attempt"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL_ATTEMPT = "path_traversal_attempt"

    # Child Safety & COPPA
    CHILD_DATA_ACCESS = "child_data_access"
    COPPA_VIOLATION_ATTEMPT = "coppa_violation_attempt"
    CHILD_SAFETY_ALERT = "child_safety_alert"
    PARENTAL_CONSENT_VIOLATION = "parental_consent_violation"

    # API Security
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    API_ABUSE_DETECTED = "api_abuse_detected"
    INVALID_TOKEN = "invalid_token"
    TOKEN_EXPIRY = "token_expiry"

    # System Security
    VAULT_CONNECTIVITY_LOSS = "vault_connectivity_loss"
    ENCRYPTION_FAILURE = "encryption_failure"
    SECRET_ACCESS_FAILURE = "secret_access_failure"
    DATABASE_CONNECTION_FAILURE = "database_connection_failure"

    # Performance & Availability
    HIGH_LATENCY = "high_latency"
    MEMORY_THRESHOLD_EXCEEDED = "memory_threshold_exceeded"
    DISK_SPACE_LOW = "disk_space_low"
    SERVICE_UNAVAILABLE = "service_unavailable"

    # Audit & Compliance
    AUDIT_LOG_FAILURE = "audit_log_failure"
    COMPLIANCE_CHECK_FAILURE = "compliance_check_failure"
    DATA_RETENTION_VIOLATION = "data_retention_violation"


class AlertLevel(str, Enum):
    """Alert severity levels for incident response."""

    CRITICAL = "critical"  # Immediate response required
    HIGH = "high"  # Response within 15 minutes
    MEDIUM = "medium"  # Response within 1 hour
    LOW = "low"  # Response within 24 hours
    INFO = "info"  # Informational only


@dataclass
class SecurityEvent:
    """Security event data structure."""

    event_id: str
    event_type: SecurityEventType
    alert_level: AlertLevel
    timestamp: datetime
    source_ip: Optional[str] = None
    user_id: Optional[str] = None
    endpoint: Optional[str] = None
    user_agent: Optional[str] = None
    details: Dict[str, Any] = None
    child_related: bool = False
    coppa_sensitive: bool = False
    response_action: Optional[str] = None


@dataclass
class SecurityMetrics:
    """Security metrics for monitoring dashboard."""

    total_events: int = 0
    critical_events: int = 0
    high_events: int = 0
    auth_failures: int = 0
    injection_attempts: int = 0
    child_safety_alerts: int = 0
    vault_health_score: float = 100.0
    average_response_time: float = 0.0
    uptime_percentage: float = 100.0
    last_updated: datetime = None


class ThreatDetectionEngine:
    """Advanced threat detection with pattern recognition and correlation."""

    def __init__(self):
        self.attack_patterns = {
            "sql_injection": [
                r"union\s+select",
                r"drop\s+table",
                r"insert\s+into",
                r"delete\s+from",
                r"update\s+.*set",
                r"exec\s*\(",
                r"script\s*>",
                r"<\s*script",
                r"javascript:",
                r"on\w+\s*=",
                r"eval\s*\(",
                r"expression\s*\(",
            ],
            "xss_patterns": [
                r"<script",
                r"javascript:",
                r"on\w+\s*=",
                r"eval\s*\(",
                r"alert\s*\(",
                r"document\.",
            ],
            "child_data_targeting": [
                r"age.*(?:between|<|>|=)",
                r"birth.*(?:date|year)",
                r"child.*(?:name|info|data)",
                r"parent.*(?:email|phone)",
                r"medical.*(?:condition|allergy)",
                r"school.*(?:name|address)",
            ],
        }

        # Sliding window for attack correlation
        self.recent_events = deque(maxlen=1000)
        self.ip_tracking = defaultdict(list)
        self.user_tracking = defaultdict(list)

    def analyze_request(self, request_data: Dict[str, Any]) -> List[SecurityEvent]:
        """Analyze incoming request for security threats."""
        events = []
        current_time = datetime.utcnow()
        source_ip = request_data.get("source_ip")
        user_id = request_data.get("user_id")

        # Check for injection patterns
        content = str(request_data.get("content", ""))
        for pattern_type, patterns in self.attack_patterns.items():
            for pattern in patterns:
                if self._pattern_match(pattern, content):
                    event_type = self._get_event_type_from_pattern(pattern_type)
                    alert_level = (
                        AlertLevel.HIGH
                        if "child" in pattern_type
                        else AlertLevel.MEDIUM
                    )

                    events.append(
                        SecurityEvent(
                            event_id=f"threat_{int(time.time())}_{pattern_type}",
                            event_type=event_type,
                            alert_level=alert_level,
                            timestamp=current_time,
                            source_ip=source_ip,
                            user_id=user_id,
                            details={
                                "pattern_matched": pattern_type,
                                "threat_score": 85,
                            },
                            child_related="child" in pattern_type,
                            coppa_sensitive="child" in pattern_type,
                        )
                    )

        # Check for brute force attacks
        if source_ip:
            self.ip_tracking[source_ip].append(current_time)
            recent_attempts = [
                t
                for t in self.ip_tracking[source_ip]
                if current_time - t < timedelta(minutes=5)
            ]

            if len(recent_attempts) > 10:  # 10 attempts in 5 minutes
                events.append(
                    SecurityEvent(
                        event_id=f"brute_force_{int(time.time())}_{source_ip}",
                        event_type=SecurityEventType.AUTH_BRUTE_FORCE,
                        alert_level=AlertLevel.HIGH,
                        timestamp=current_time,
                        source_ip=source_ip,
                        details={"attempt_count": len(recent_attempts)},
                        response_action="ip_block_recommended",
                    )
                )

        return events

    def _pattern_match(self, pattern: str, content: str) -> bool:
        """Enhanced pattern matching with context awareness."""
        import re

        try:
            return bool(re.search(pattern, content, re.IGNORECASE))
        except re.error:
            return False

    def _get_event_type_from_pattern(self, pattern_type: str) -> SecurityEventType:
        """Map pattern types to security event types."""
        mapping = {
            "sql_injection": SecurityEventType.SQL_INJECTION_ATTEMPT,
            "xss_patterns": SecurityEventType.XSS_ATTEMPT,
            "child_data_targeting": SecurityEventType.CHILD_SAFETY_ALERT,
        }
        return mapping.get(pattern_type, SecurityEventType.API_ABUSE_DETECTED)


class ChildSafetyMonitor:
    """Specialized monitoring for COPPA compliance and child safety."""

    # COPPA-sensitive operations that require special monitoring
    COPPA_SENSITIVE_OPERATIONS = [
        "child_profile_create",
        "child_data_access",
        "child_info_update",
        "parental_consent_check",
        "child_content_generation",
    ]

    def __init__(self):
        self.child_access_log = deque(maxlen=10000)  # Last 10k child-related events
        self.consent_violations = []
        self.data_retention_alerts = []

    def monitor_child_operation(
        self, operation: str, user_id: str, child_id: str, details: Dict[str, Any]
    ) -> Optional[SecurityEvent]:
        """Monitor child-related operations for COPPA compliance."""
        current_time = datetime.utcnow()

        # Log access for audit trail (NO PII)
        access_record = {
            "timestamp": current_time,
            "operation": operation,
            "user_id": user_id,
            "child_id_hash": self._safe_hash(child_id),  # Hash for privacy
            "operation_type": details.get("operation_type", "unknown"),
        }
        self.child_access_log.append(access_record)

        # Check for potential violations
        if operation in self.COPPA_SENSITIVE_OPERATIONS:
            # Verify parental consent
            consent_status = details.get("parental_consent", False)
            if not consent_status:
                return SecurityEvent(
                    event_id=f"coppa_violation_{int(time.time())}",
                    event_type=SecurityEventType.PARENTAL_CONSENT_VIOLATION,
                    alert_level=AlertLevel.CRITICAL,
                    timestamp=current_time,
                    user_id=user_id,
                    details={
                        "operation": operation,
                        "violation_type": "missing_parental_consent",
                        "child_id_hash": self._safe_hash(child_id),
                    },
                    child_related=True,
                    coppa_sensitive=True,
                    response_action="block_operation",
                )

        return None

    def check_data_retention_compliance(self) -> List[SecurityEvent]:
        """Check for data retention policy violations."""
        events = []
        current_time = datetime.utcnow()

        # Check for records older than retention period (example: 2 years for COPPA)
        retention_limit = current_time - timedelta(days=730)  # 2 years

        old_records = [
            record
            for record in self.child_access_log
            if record["timestamp"] < retention_limit
        ]

        if old_records:
            events.append(
                SecurityEvent(
                    event_id=f"retention_violation_{int(time.time())}",
                    event_type=SecurityEventType.DATA_RETENTION_VIOLATION,
                    alert_level=AlertLevel.HIGH,
                    timestamp=current_time,
                    details={
                        "old_records_count": len(old_records),
                        "retention_limit": retention_limit.isoformat(),
                    },
                    child_related=True,
                    coppa_sensitive=True,
                    response_action="data_purge_required",
                )
            )

        return events

    def _safe_hash(self, value: str) -> str:
        """Create a safe hash for audit trails without exposing PII."""
        import hashlib

        return hashlib.sha256(value.encode()).hexdigest()[:16]


class VaultHealthMonitor:
    """Monitor HashiCorp Vault health and secrets management."""

    def __init__(self, vault_client=None):
        self.vault_client = vault_client
        self.health_history = deque(maxlen=100)
        self.last_health_check = None
        self.consecutive_failures = 0

    async def perform_health_check(self) -> List[SecurityEvent]:
        """Perform comprehensive Vault health monitoring."""
        events = []
        current_time = datetime.utcnow()

        try:
            if not self.vault_client:
                events.append(
                    SecurityEvent(
                        event_id=f"vault_unavailable_{int(time.time())}",
                        event_type=SecurityEventType.VAULT_CONNECTIVITY_LOSS,
                        alert_level=AlertLevel.CRITICAL,
                        timestamp=current_time,
                        details={"error": "vault_client_not_configured"},
                        response_action="fallback_to_local_secrets",
                    )
                )
                return events

            # Test Vault connectivity
            health_result = await self.vault_client.health_check()

            if not health_result.get("is_healthy", False):
                self.consecutive_failures += 1

                alert_level = (
                    AlertLevel.CRITICAL
                    if self.consecutive_failures > 3
                    else AlertLevel.HIGH
                )

                events.append(
                    SecurityEvent(
                        event_id=f"vault_unhealthy_{int(time.time())}",
                        event_type=SecurityEventType.VAULT_CONNECTIVITY_LOSS,
                        alert_level=alert_level,
                        timestamp=current_time,
                        details={
                            "vault_status": health_result.get("status", "unknown"),
                            "consecutive_failures": self.consecutive_failures,
                            "error": health_result.get("error", "unknown"),
                        },
                        response_action="escalate_to_security_team",
                    )
                )
            else:
                self.consecutive_failures = 0

            # Record health metrics
            self.health_history.append(
                {
                    "timestamp": current_time,
                    "is_healthy": health_result.get("is_healthy", False),
                    "response_time": health_result.get("response_time_ms", 0),
                    "vault_version": health_result.get("version", "unknown"),
                }
            )

        except Exception as e:
            self.consecutive_failures += 1
            events.append(
                SecurityEvent(
                    event_id=f"vault_error_{int(time.time())}",
                    event_type=SecurityEventType.VAULT_CONNECTIVITY_LOSS,
                    alert_level=AlertLevel.CRITICAL,
                    timestamp=current_time,
                    details={
                        "error": str(e),
                        "consecutive_failures": self.consecutive_failures,
                    },
                    response_action="immediate_investigation_required",
                )
            )

        return events


class SecurityMonitoringSystem:
    """Main security monitoring system orchestrating all components."""

    def __init__(self, vault_client=None):
        self.threat_detector = ThreatDetectionEngine()
        self.child_safety_monitor = ChildSafetyMonitor()
        self.vault_monitor = VaultHealthMonitor(vault_client)

        # Event storage and metrics
        self.security_events = deque(maxlen=50000)  # Last 50k events
        self.metrics = SecurityMetrics()
        self.alert_callbacks: List[Callable] = []

        # Performance monitoring
        self.response_times = deque(maxlen=1000)
        self.error_rates = defaultdict(int)

        # Configuration
        self.alert_thresholds = {
            "max_response_time_ms": 5000,
            "max_error_rate_per_minute": 50,
            "max_failed_auth_per_ip": 10,
            "vault_health_check_interval": 300,  # 5 minutes
        }

        logger.info(
            "SecurityMonitoringSystem initialized with comprehensive monitoring"
        )

    def register_alert_callback(self, callback: Callable[[SecurityEvent], None]):
        """Register callback for real-time alert notifications."""
        self.alert_callbacks.append(callback)

    async def process_security_event(self, event: SecurityEvent) -> None:
        """Process and store security events with real-time analysis."""
        # Store event
        self.security_events.append(event)

        # Update metrics
        self.metrics.total_events += 1
        if event.alert_level == AlertLevel.CRITICAL:
            self.metrics.critical_events += 1
        elif event.alert_level == AlertLevel.HIGH:
            self.metrics.high_events += 1

        if event.event_type in [
            SecurityEventType.AUTH_FAILURE,
            SecurityEventType.AUTH_BRUTE_FORCE,
        ]:
            self.metrics.auth_failures += 1

        if event.event_type in [
            SecurityEventType.SQL_INJECTION_ATTEMPT,
            SecurityEventType.XSS_ATTEMPT,
        ]:
            self.metrics.injection_attempts += 1

        if event.child_related or event.coppa_sensitive:
            self.metrics.child_safety_alerts += 1

        self.metrics.last_updated = datetime.utcnow()

        # Trigger alerts for critical events
        if event.alert_level in [AlertLevel.CRITICAL, AlertLevel.HIGH]:
            await self._trigger_alerts(event)

        # Log event (secure logging - no sensitive data)
        self._log_security_event(event)

    async def monitor_request(
        self, request_data: Dict[str, Any]
    ) -> List[SecurityEvent]:
        """Monitor incoming request for security threats."""
        start_time = time.time()

        try:
            # Threat detection
            threat_events = self.threat_detector.analyze_request(request_data)

            # Process each detected threat
            for event in threat_events:
                await self.process_security_event(event)

            # Monitor response time
            response_time = (time.time() - start_time) * 1000  # ms
            self.response_times.append(response_time)

            # Check for performance issues
            if response_time > self.alert_thresholds["max_response_time_ms"]:
                performance_event = SecurityEvent(
                    event_id=f"performance_{int(time.time())}",
                    event_type=SecurityEventType.HIGH_LATENCY,
                    alert_level=AlertLevel.MEDIUM,
                    timestamp=datetime.utcnow(),
                    source_ip=request_data.get("source_ip"),
                    endpoint=request_data.get("endpoint"),
                    details={"response_time_ms": response_time},
                )
                await self.process_security_event(performance_event)

            return threat_events

        except Exception as e:
            error_event = SecurityEvent(
                event_id=f"monitoring_error_{int(time.time())}",
                event_type=SecurityEventType.SERVICE_UNAVAILABLE,
                alert_level=AlertLevel.HIGH,
                timestamp=datetime.utcnow(),
                details={"error": str(e), "component": "security_monitoring"},
            )
            await self.process_security_event(error_event)
            return []

    async def monitor_child_operation(
        self, operation: str, user_id: str, child_id: str, details: Dict[str, Any]
    ) -> None:
        """Monitor child-related operations for COPPA compliance."""
        child_event = self.child_safety_monitor.monitor_child_operation(
            operation, user_id, child_id, details
        )

        if child_event:
            await self.process_security_event(child_event)

    async def perform_system_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive system health check."""
        logger.info("Performing comprehensive security health check")

        # Vault health monitoring
        vault_events = await self.vault_monitor.perform_health_check()
        for event in vault_events:
            await self.process_security_event(event)

        # Child data retention compliance
        retention_events = self.child_safety_monitor.check_data_retention_compliance()
        for event in retention_events:
            await self.process_security_event(event)

        # Calculate system health metrics
        vault_health_score = self._calculate_vault_health_score()
        avg_response_time = self._calculate_average_response_time()

        self.metrics.vault_health_score = vault_health_score
        self.metrics.average_response_time = avg_response_time

        return {
            "vault_health_score": vault_health_score,
            "average_response_time": avg_response_time,
            "total_events": self.metrics.total_events,
            "critical_events": self.metrics.critical_events,
            "child_safety_alerts": self.metrics.child_safety_alerts,
            "last_updated": self.metrics.last_updated.isoformat()
            if self.metrics.last_updated
            else None,
        }

    def get_security_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive security dashboard data."""
        recent_events = [
            {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "alert_level": event.alert_level.value,
                "timestamp": event.timestamp.isoformat(),
                "child_related": event.child_related,
                "source_ip": event.source_ip,
                "response_action": event.response_action,
            }
            for event in list(self.security_events)[-100:]  # Last 100 events
        ]

        return {
            "metrics": asdict(self.metrics),
            "recent_events": recent_events,
            "system_health": {
                "vault_health_score": self.metrics.vault_health_score,
                "average_response_time": self.metrics.average_response_time,
                "uptime_percentage": self.metrics.uptime_percentage,
            },
            "threat_summary": self._generate_threat_summary(),
        }

    async def _trigger_alerts(self, event: SecurityEvent) -> None:
        """Trigger real-time alerts for critical security events."""
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")

    def _log_security_event(self, event: SecurityEvent) -> None:
        """Log security event with secure, COPPA-compliant logging."""
        # Create sanitized log entry (NO sensitive data)
        log_data = {
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "alert_level": event.alert_level.value,
            "timestamp": event.timestamp.isoformat(),
            "child_related": event.child_related,
            "coppa_sensitive": event.coppa_sensitive,
            "response_action": event.response_action,
        }

        # Only log non-sensitive details
        if event.details:
            safe_details = {
                k: v
                for k, v in event.details.items()
                if k not in ["user_data", "child_info", "personal_info", "raw_content"]
            }
            log_data["details"] = safe_details

        if event.alert_level == AlertLevel.CRITICAL:
            logger.critical(f"SECURITY ALERT: {event.event_type.value}", extra=log_data)
        elif event.alert_level == AlertLevel.HIGH:
            logger.error(f"Security Event: {event.event_type.value}", extra=log_data)
        elif event.alert_level == AlertLevel.MEDIUM:
            logger.warning(f"Security Event: {event.event_type.value}", extra=log_data)
        else:
            logger.info(f"Security Event: {event.event_type.value}", extra=log_data)

    def _calculate_vault_health_score(self) -> float:
        """Calculate Vault health score based on recent checks."""
        if not self.vault_monitor.health_history:
            return 0.0

        recent_checks = list(self.vault_monitor.health_history)[-10:]  # Last 10 checks
        healthy_count = sum(1 for check in recent_checks if check["is_healthy"])

        return (healthy_count / len(recent_checks)) * 100.0

    def _calculate_average_response_time(self) -> float:
        """Calculate average response time from recent requests."""
        if not self.response_times:
            return 0.0

        return sum(self.response_times) / len(self.response_times)

    def _generate_threat_summary(self) -> Dict[str, Any]:
        """Generate threat intelligence summary."""
        recent_events = list(self.security_events)[-1000:]  # Last 1000 events

        threat_types = defaultdict(int)
        source_ips = defaultdict(int)
        alert_levels = defaultdict(int)

        for event in recent_events:
            threat_types[event.event_type.value] += 1
            alert_levels[event.alert_level.value] += 1
            if event.source_ip:
                source_ips[event.source_ip] += 1

        return {
            "top_threats": dict(
                sorted(threat_types.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
            "alert_distribution": dict(alert_levels),
            "top_source_ips": dict(
                sorted(source_ips.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
            "total_analyzed": len(recent_events),
        }


# Global instance for singleton access
_security_monitoring_system: Optional[SecurityMonitoringSystem] = None


async def get_security_monitoring_system(vault_client=None) -> SecurityMonitoringSystem:
    """Get the global security monitoring system instance."""
    global _security_monitoring_system

    if _security_monitoring_system is None:
        _security_monitoring_system = SecurityMonitoringSystem(vault_client)
        logger.info("Global SecurityMonitoringSystem instance created")

    return _security_monitoring_system


async def initialize_security_monitoring(vault_client=None) -> SecurityMonitoringSystem:
    """Initialize security monitoring system for application startup."""
    monitoring_system = await get_security_monitoring_system(vault_client)

    # Perform initial health check
    await monitoring_system.perform_system_health_check()

    logger.info("Security monitoring system fully initialized and operational")
    return monitoring_system
