from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Any
import time


# Child Safety Monitoring Component.
# Specialized monitoring for child safety events and pattern detection.

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="monitoring")


class ChildSafetyMonitor:
    """Specialized monitoring for child safety events."""

    def __init__(self) -> None:
        """Initialize child safety monitor."""
        self.safety_events = deque(maxlen=10000)
        self.safety_alerts: Dict[str, Dict[str, Any]] = {}
        self.emergency_contacts: List[str] = []
        # Child safety thresholds
        self.inappropriate_content_threshold = 5  # Per hour
        self.emotional_distress_threshold = 3  # Per hour
        self.unusual_activity_threshold = 20  # Per hour
        logger.info("Child safety monitor initialized")

    def record_safety_event(
        self,
        child_id: str,
        event_type: str,
        severity: str,
        details: Dict[str, Any],
    ) -> None:
        """Record a child safety event."""
        event = {
            "child_id": child_id,
            "event_type": event_type,
            "severity": severity,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.safety_events.append(event)
        # Check for emergency conditions
        if severity == "emergency" or event_type in [
            "abuse_detected",
            "severe_distress",
        ]:
            self._trigger_emergency_alert(child_id, event_type, details)
        # Check for patterns
        self._check_safety_patterns(child_id, event_type)
        logger.warning(
            f"Child safety event recorded: {event_type} for child {child_id}"
        )

    def _trigger_emergency_alert(
        self, child_id: str, event_type: str, details: Dict[str, Any]
    ) -> None:
        """Trigger emergency alert for critical child safety events."""
        alert_id = f"emergency_{child_id}_{int(time.time())}"
        emergency_alert = {
            "alert_id": alert_id,
            "child_id": child_id,
            "event_type": event_type,
            "severity": "EMERGENCY",
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "requires_immediate_attention": True,
        }
        self.safety_alerts[alert_id] = emergency_alert
        # Log critical alert
        logger.critical(
            f"EMERGENCY CHILD SAFETY ALERT: {event_type} for child {child_id}"
        )
        # In production, this would trigger immediate notifications
        # to parents, administrators, and possibly authorities

    def _check_safety_patterns(self, child_id: str, event_type: str) -> None:
        """Check for concerning patterns in child safety events."""
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        # Count recent events for this child
        recent_events = [
            event
            for event in self.safety_events
            if (
                event["child_id"] == child_id
                and datetime.fromisoformat(event["timestamp"]) > one_hour_ago
            )
        ]
        event_counts = defaultdict(int)
        for event in recent_events:
            event_counts[event["event_type"]] += 1
        # Check thresholds
        if (
            event_counts["inappropriate_content"]
            >= self.inappropriate_content_threshold
        ):
            self._create_pattern_alert(
                child_id,
                "excessive_inappropriate_content",
                event_counts["inappropriate_content"],
            )
        if (
            event_counts["emotional_distress"]
            >= self.emotional_distress_threshold
        ):
            self._create_pattern_alert(
                child_id,
                "repeated_emotional_distress",
                event_counts["emotional_distress"],
            )

    def _create_pattern_alert(
        self, child_id: str, pattern_type: str, count: int
    ) -> None:
        """Create alert for concerning patterns."""
        alert_id = f"pattern_{child_id}_{pattern_type}_{int(time.time())}"
        pattern_alert = {
            "alert_id": alert_id,
            "child_id": child_id,
            "pattern_type": pattern_type,
            "event_count": count,
            "severity": "HIGH",
            "timestamp": datetime.utcnow().isoformat(),
            "requires_parent_notification": True,
        }
        self.safety_alerts[alert_id] = pattern_alert
        logger.error(
            f"Pattern alert created: {pattern_type} for child {child_id} (count: {count})"
        )

    def get_child_safety_status(self, child_id: str) -> Dict[str, Any]:
        """Get safety status for a specific child."""
        now = datetime.utcnow()
        twenty_four_hours_ago = now - timedelta(hours=24)
        # Get recent events for this child
        recent_events = [
            event
            for event in self.safety_events
            if (
                event["child_id"] == child_id
                and datetime.fromisoformat(event["timestamp"])
                > twenty_four_hours_ago
            )
        ]
        # Get active alerts for this child
        active_alerts = [
            alert
            for alert in self.safety_alerts.values()
            if alert.get("child_id") == child_id
        ]
        return {
            "child_id": child_id,
            "recent_events_count": len(recent_events),
            "active_alerts_count": len(active_alerts),
            "safety_score": self._calculate_safety_score(recent_events),
            "last_activity": (
                recent_events[-1]["timestamp"] if recent_events else None
            ),
            "active_alerts": active_alerts,
        }

    def _calculate_safety_score(self, events: List[Dict[str, Any]]) -> float:
        """Calculate a safety score based on recent events."""
        if not events:
            return 100.0
        # Score starts at 100 and decreases based on event severity
        score = 100.0
        for event in events:
            severity = event.get("severity", "low")
            if severity == "emergency":
                score -= 20.0
            elif severity == "high":
                score -= 10.0
            elif severity == "medium":
                score -= 5.0
            elif severity == "low":
                score -= 1.0
        return max(0.0, score)
