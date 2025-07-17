"""
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import threading
import time
from .child_safety_monitor import ChildSafetyMonitor
from .types import Alert, AlertSeverity, MetricValue, MetricType, AlertStatus
"""

Comprehensive Monitoring Service.
Enterprise monitoring service with child safety focus.
"""

from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="monitoring")

class ComprehensiveMonitoringService:
    """
    Enterprise monitoring service with child safety focus.
    Features: 
    - Real - time metrics collection 
    - Child safety event monitoring 
    - Performance metrics tracking 
    - Security event detection 
    - Automated alerting 
    - COPPA compliance monitoring
    """
    def __init__(self) -> None:
        """Initialize comprehensive monitoring service."""
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: List[Dict[str, Any]] = []
        self.child_safety_monitor = ChildSafetyMonitor()
        
        # Performance tracking
        self.request_times = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.active_connections = 0
        
        # Security monitoring
        self.failed_auth_attempts = defaultdict(int)
        self.suspicious_activities = deque(maxlen=1000)
        
        # COPPA compliance tracking
        self.consent_violations = deque(maxlen=1000)
        self.data_access_logs = deque(maxlen=10000)
        
        # Monitoring thread
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitoring_thread.start()
        
        # Initialize default alert rules
        self._setup_default_alerts()
        
        logger.info("Comprehensive monitoring service initialized")

    def record_metric(self, name: str, value: float, metric_type: MetricType = MetricType.GAUGE,
                     tags: Optional[Dict[str, str]] = None) -> None:
        """Record a metric value."""
        if tags is None:
            tags = {}
        
        metric = MetricValue(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.utcnow(),
            tags=tags
        )
        
        self.metrics[name].append(metric)
        
        # Check if this metric triggers any alerts
        self._check_alert_rules(metric)
        
        logger.debug(f"Metric recorded: {name}={value} ({metric_type.value})")

    def record_request_time(self, endpoint: str, duration: float, status_code: int) -> None:
        """Record API request performance."""
        self.request_times.append({
            "endpoint": endpoint,
            "duration": duration,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Record as metric
        self.record_metric(
            "request_duration",
            duration,
            MetricType.TIMER,
            {"endpoint": endpoint, "status": str(status_code)}
        )
        
        # Track errors
        if status_code >= 400:
            self.error_counts[endpoint] += 1

    def record_security_event(self, event_type: str, details: Dict[str, Any],
                            severity: str = "medium") -> None:
        """Record security - related events."""
        security_event = {
            "event_type": event_type,
            "details": details,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.suspicious_activities.append(security_event)
        
        # Special handling for auth failures
        if event_type == "auth_failure":
            client_ip = details.get("client_ip", "unknown")
            self.failed_auth_attempts[client_ip] += 1
            
            # Alert on excessive failures
            if self.failed_auth_attempts[client_ip] > 10:
                self._create_alert(
                    f"excessive_auth_failures_{client_ip}",
                    "Excessive Authentication Failures",
                    f"Too many auth failures from IP: {client_ip}",
                    AlertSeverity.HIGH
                )
        
        logger.warning(f"Security event recorded: {event_type}")

    def record_child_safety_event(self, child_id: str, event_type: str,
                                 severity: str, details: Dict[str, Any]) -> None:
        """Record child safety events."""
        self.child_safety_monitor.record_safety_event(child_id, event_type, severity, details)
        
        # Also record as general metric for trending
        self.record_metric(
            "child_safety_events",
            1,
            MetricType.COUNTER,
            {"child_id": child_id, "event_type": event_type, "severity": severity}
        )

    def _setup_default_alerts(self) -> None:
        """Setup default monitoring alerts."""
        default_alerts = [
            {
                "name": "High Error Rate",
                "description": "Error rate exceeds 5%",
                "severity": AlertSeverity.HIGH,
                "metric": "error_rate",
                "threshold": 0.05,
                "comparison": ">"
            },
            {
                "name": "High Response Time",
                "description": "Average response time exceeds 2 seconds",
                "severity": AlertSeverity.MEDIUM,
                "metric": "avg_response_time",
                "threshold": 2.0,
                "comparison": ">"
            },
            {
                "name": "Database Connection Pool Exhaustion",
                "description": "Database connection pool is near capacity",
                "severity": AlertSeverity.HIGH,
                "metric": "db_pool_usage",
                "threshold": 0.9,
                "comparison": ">"
            },
            {
                "name": "Memory Usage High",
                "description": "Memory usage exceeds 85%",
                "severity": AlertSeverity.MEDIUM,
                "metric": "memory_usage",
                "threshold": 0.85,
                "comparison": ">"
            }
        ]
        
        self.alert_rules.extend(default_alerts)
        logger.info(f"Setup {len(default_alerts)} default alert rules")

    def _check_alert_rules(self, metric: MetricValue) -> None:
        """Check if metric triggers any alert rules."""
        for rule in self.alert_rules:
            if rule["metric"] == metric.name:
                threshold = rule["threshold"]
                comparison = rule["comparison"]
                should_alert = False
                
                if comparison == ">" and metric.value > threshold:
                    should_alert = True
                elif comparison == "<" and metric.value < threshold:
                    should_alert = True
                elif comparison == "==" and metric.value == threshold:
                    should_alert = True
                
                if should_alert:
                    alert_id = f"{rule['name'].lower().replace(' ', '_')}_{int(time.time())}"
                    self._create_alert(
                        alert_id,
                        rule["name"],
                        rule["description"],
                        rule["severity"],
                        metric.name,
                        metric.value,
                        threshold
                    )

    def _create_alert(self, alert_id: str, title: str, description: str,
                     severity: AlertSeverity, metric_name: str = "",
                     current_value: float = 0.0, threshold_value: float = 0.0) -> None:
        """Create a new alert."""
        alert = Alert(
            id=alert_id,
            title=title,
            description=description,
            severity=severity,
            status=AlertStatus.ACTIVE,
            created_at=datetime.utcnow(),
            metric_name=metric_name,
            current_value=current_value,
            threshold_value=threshold_value,
            tags={}
        )
        
        self.alerts[alert_id] = alert
        logger.warning(f"Alert created: {title} ({severity.value})")

    def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        while self._monitoring_active:
            try:
                self._perform_health_checks()
                self._cleanup_old_data()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Shorter sleep on error

    def _perform_health_checks(self) -> None:
        """Perform periodic health checks."""
        # Calculate error rate
        if self.request_times:
            total_requests = len(self.request_times)
            error_requests = sum(1 for req in self.request_times if req.get("status_code", 200) >= 400)
            error_rate = error_requests / total_requests if total_requests > 0 else 0
            self.record_metric("error_rate", error_rate, MetricType.GAUGE)
        
        # Calculate average response time
        if self.request_times:
            avg_response_time = sum(req.get("duration", 0) for req in self.request_times) / len(self.request_times)
            self.record_metric("avg_response_time", avg_response_time, MetricType.GAUGE)
        
        # Record active connections
        self.record_metric("active_connections", self.active_connections, MetricType.GAUGE)

    def _cleanup_old_data(self) -> None:
        """Clean up old monitoring data."""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Clean old failed auth attempts
        for ip in list(self.failed_auth_attempts.keys()):
            # Reset counter daily
            self.failed_auth_attempts[ip] = 0
        
        # Auto-resolve old alerts
        for alert_id, alert in list(self.alerts.items()):
            if alert.created_at < cutoff_time and alert.status == AlertStatus.ACTIVE:
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.utcnow()
                logger.info(f"Auto-resolved old alert: {alert.title}")

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of current metrics."""
        return {
            "total_metrics": len(self.metrics),
            "active_alerts": len([a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE]),
            "total_requests": len(self.request_times),
            "error_rate": self._calculate_error_rate(),
            "avg_response_time": self._calculate_avg_response_time(),
            "active_connections": self.active_connections,
            "child_safety_events": len(self.child_safety_monitor.safety_events)
        }

    def _calculate_error_rate(self) -> float:
        """Calculate current error rate."""
        if not self.request_times:
            return 0.0
        
        error_count = sum(1 for req in self.request_times if req.get("status_code", 200) >= 400)
        return error_count / len(self.request_times)

    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time."""
        if not self.request_times:
            return 0.0
        
        total_time = sum(req.get("duration", 0) for req in self.request_times)
        return total_time / len(self.request_times)

    def shutdown(self) -> None:
        """Shutdown monitoring service."""
        self._monitoring_active = False
        if self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=5)
        
        logger.info("Monitoring service shutdown complete")