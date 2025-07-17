"""Standardized Logging Infrastructure
==================================
Provides consistent logging patterns across all AI Teddy Bear services
with special focus on child safety and COPPA compliance logging."""

from .standards import (
    StandardLogger,
    LogLevel,
    LogCategory,
    get_standard_logger,
    configure_logging)

__all__ = [
    "StandardLogger",
    "LogLevel",
    "LogCategory",
    "get_standard_logger",
    "configure_logging"
]