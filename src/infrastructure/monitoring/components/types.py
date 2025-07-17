from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Optional

# Monitoring types and data classes.

class AlertSeverity(Enum):
    """Alert severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"  # For child safety incidents


class MetricType(Enum):
    """Types of metrics to monitor."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertStatus(Enum):
    """Alert status tracking."""

    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SUPPRESSED = "suppressed"


@dataclass
class MetricValue:
    """Container for metric values."""

    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str]
    labels: Optional[Dict[str, str]] = None

    def __post_init__(self) -> None:
        """Validate metric value after initialization."""
        if self.labels is None:
            self.labels = {}


@dataclass
class Alert:
    """Alert data structure."""

    id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    created_at: datetime
    metric_name: str
    current_value: float
    threshold_value: float
    tags: Dict[str, str]
    child_id: Optional[str] = None
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    escalated: bool = False

    def __post_init__(self) -> None:
        """Initialize alert with defaults."""
        if not self.tags:
            self.tags = {}
