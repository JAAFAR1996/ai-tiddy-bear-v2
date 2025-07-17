"""Standardized Logging Infrastructure.
==================================
Provides consistent logging patterns across all AI Teddy Bear services
with special focus on child safety and COPPA compliance logging.
"""

from .standards import (
    LogCategory,
    LogLevel,
    StandardLogger,
    configure_logging,
    get_standard_logger,
)

__all__ = [
    "LogCategory",
    "LogLevel",
    "StandardLogger",
    "configure_logging",
    "get_standard_logger",
]
