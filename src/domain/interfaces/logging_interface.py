"""Domain Logging Interface
Defines the contract for logging services without coupling domain to infrastructure.
This allows domain logic to emit events while remaining infrastructure-agnostic.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any


class LogLevel(Enum):
    """Log severity levels for domain events."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class DomainLoggerInterface(ABC):
    """Interface for domain logging services.
    This interface allows domain entities and services to emit log events
    without depending on specific logging infrastructure.
    """

    @abstractmethod
    def log_domain_event(
        self,
        level: LogLevel,
        message: str,
        context: dict[str, Any] | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        """Log a domain event.

        Args:
            level: Log severity level
            message: Event message
            context: Additional context data
            timestamp: Event timestamp (defaults to now)

        """

    @abstractmethod
    def log_business_rule_violation(
        self,
        rule_name: str,
        entity_id: str,
        violation_details: dict[str, Any],
    ) -> None:
        """Log business rule violations for compliance and debugging.

        Args:
            rule_name: Name of the violated business rule
            entity_id: ID of the entity that violated the rule
            violation_details: Details about the violation

        """

    @abstractmethod
    def log_child_safety_event(
        self,
        child_id: str,
        safety_event: str,
        severity: LogLevel,
        details: dict[str, Any],
    ) -> None:
        """Log child safety events for COPPA compliance.

        Args:
            child_id: Child identifier
            safety_event: Description of safety event
            severity: Event severity
            details: Additional safety details

        """


class NullDomainLogger(DomainLoggerInterface):
    """Null implementation of domain logger for testing.
    This implementation does nothing, allowing domain logic to work
    without logging infrastructure in unit tests.
    """

    def log_domain_event(
        self,
        level: LogLevel,
        message: str,
        context: dict[str, Any] | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        """No-op implementation."""

    def log_business_rule_violation(
        self,
        rule_name: str,
        entity_id: str,
        violation_details: dict[str, Any],
    ) -> None:
        """No-op implementation."""

    def log_child_safety_event(
        self,
        child_id: str,
        safety_event: str,
        severity: LogLevel,
        details: dict[str, Any],
    ) -> None:
        """No-op implementation."""
