"""from dataclasses import dataclassfrom datetime import datetimefrom typing import Dict"""
"""Data Models for Chaos Metrics"""

@dataclass
class ChaosMetric:
    """Individual chaos metric data point"""
    timestamp: datetime
    experiment_id: str
    service_name: str
    metric_name: str
    metric_value: float
    tags: Dict[str, str]

@dataclass
class SystemHealthSnapshot:
    """System health snapshot during chaos"""
    timestamp: datetime
    experiment_id: str
    services_healthy: int
    services_total: int
    avg_response_time: float
    error_rate: float
    throughput: float
    safety_violations: int

@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    condition: str
    threshold: float
    severity: str
    notification_channels: list

@dataclass
class ChaosExperimentResult:
    """Results from a chaos experiment"""
    experiment_id: str
    start_time: datetime
    end_time: datetime
    success: bool
    metrics: list
    alerts_triggered: list
    recovery_time: float