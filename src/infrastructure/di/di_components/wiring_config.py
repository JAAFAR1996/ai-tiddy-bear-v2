"""Wiring configuration for different application modules.

This module defines the wiring configurations for various application components,
centralizing the mapping of abstract interfaces to concrete implementations.
"""

from typing import List


class WiringConfig:
    """Base wiring configuration.

    Provides a base for specific wiring configurations.
    """

    modules: List[str] = []


# APIWiringConfig, DashboardWiringConfig, and CoreWiringConfig were unused and have been removed.
# The project now uses FullWiringConfig directly, reducing complexity.


class FullWiringConfig(WiringConfig):
    """Complete wiring configuration for all modules.

    Aggregates all necessary module paths for dependency injection wiring.
    """

    modules = [
        "src.presentation.api.esp32_endpoints",
        "src.presentation.api.parental_dashboard",
        "src.presentation.api.health_endpoints",
        "src.presentation.dependencies",
        # Add other top-level modules that require wiring here
    ]
