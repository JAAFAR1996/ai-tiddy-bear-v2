"""Standardized Logging Infrastructure.
==================================
Provides consistent logging patterns across all AI Teddy Bear services
with special focus on child safety and COPPA compliance logging.
"""

from src.domain.interfaces.logging_interface import LogLevel

from .standards import LogCategory
from .standards import StandardizedLogger as StandardLogger
from .standards import get_standardized_logger as get_standard_logger

__all__ = [
    "LogCategory",
    "LogLevel",
    "StandardLogger",
    "configure_logging",
    "get_standard_logger",
]
