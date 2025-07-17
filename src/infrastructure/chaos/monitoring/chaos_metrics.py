"""from .chaos_metrics.data_models import ChaosMetric, SystemHealthSnapshotfrom .chaos_metrics.metrics_collector import ChaosMetricsCollector"""
"""Chaos Engineering Metrics and MonitoringRe - export from the modular implementation"""

# Re-export main classes for backward compatibility
__all__ = [
    "ChaosMetricsCollector",
    "ChaosMetric",
    "SystemHealthSnapshot"
]

# Main entry point
def create_metrics_collector() -> MetricsCollector:
    """Create and return a metrics collector instance"""
    return ChaosMetricsCollector()