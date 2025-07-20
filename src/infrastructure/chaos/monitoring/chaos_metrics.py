from .data_models import ChaosMetric, SystemHealthSnapshot
from .metrics_collector import ChaosMetricsCollector

"""
Chaos Engineering Metrics and Monitoring
Re-export from the modular implementation
"""

# Re-export main classes for backward compatibility
__all__ = [
    "ChaosMetric",
    "ChaosMetricsCollector",
    "SystemHealthSnapshot",
]


# Main entry point
def create_metrics_collector() -> ChaosMetricsCollector:
    """Create and return a metrics collector instance."""
    return ChaosMetricsCollector()
