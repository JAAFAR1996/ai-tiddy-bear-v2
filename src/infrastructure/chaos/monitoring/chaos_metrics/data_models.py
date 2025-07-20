from dataclasses import dataclass
from datetime import datetime

"""Data Models for Chaos Metrics"""


@dataclass
class ChaosMetric:
    """Individual chaos metric data point."""

    timestamp: datetime
    experiment_id: str
    service_name: str
    metric_name: str
    metric_value: float
    tags: dict[str, str]


@dataclass
class SystemHealthSnapshot:
    """System health snapshot during chaos."""

    timestamp: datetime
    experiment_id: str
    services_healthy: int
    services_total: int
    avg_response_time: float
    error_rate: float
    throughput: float
    safety_violations: int


@dataclass
class ChaosAlertRule:
    """Alert rule configuration."""

    name: str
    condition: str
    threshold: float
    severity: str
    notification_channels: list[str]


@dataclass
class ChaosExperimentResult:
    """Results from a chaos experiment."""

    experiment_id: str
    start_time: datetime
    end_time: datetime
    success: bool
    metrics: list[ChaosMetric]
    alerts_triggered: list[ChaosAlertRule]
    recovery_time: float
