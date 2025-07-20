from dataclasses import dataclass
from datetime import datetime
from enum import Enum

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
    tags: dict[str, str]
    labels: dict[str, str] | None = None

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
    tags: dict[str, str]
    child_id: str | None = None
    resolved_at: datetime | None = None
    acknowledged_at: datetime | None = None
    escalated: bool = False

    def __post_init__(self) -> None:
        """Initialize alert with defaults."""
        if not self.tags:
            self.tags = {}
