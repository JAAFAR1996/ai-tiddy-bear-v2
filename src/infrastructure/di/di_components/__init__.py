"""Dependency Injection Components Package.

This package contains the core components for dependency injection,
including wiring configurations and service factories.

Note: APIWiringConfig, DashboardWiringConfig, and CoreWiringConfig
were removed as part of architectural simplification. The project
now uses FullWiringConfig directly.
"""

from .wiring_config import FullWiringConfig, WiringConfig

__all__ = [
    "WiringConfig",
    "FullWiringConfig",
]
