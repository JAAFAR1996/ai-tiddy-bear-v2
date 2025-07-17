"""Domain Exception Base Classes
Comprehensive exception hierarchy for the AI Teddy Bear system with
child safety focus and improved error handling.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class ErrorSeverity(Enum):
    """
    Error severity levels for proper escalation and logging.
    Used to categorize errors by their impact on child safety and system operation.
    """

    LOW = "low"  # Minor issues, system continues normally
    MEDIUM = "medium"  # Notable issues, may affect user experience
    HIGH = "high"  # Serious issues, may affect functionality
    CRITICAL = "critical"  # Critical issues, may affect child safety


class ErrorContext:
    """
    Enhanced error context for comprehensive debugging and audit trails.
    Provides detailed context information for errors including child safety
    implications and system state information.
    """

    def __init__(
        self,
        child_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        feature: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize error context with comprehensive details.
        Args:
            child_id: Child identifier if error relates to specific child
            parent_id: Parent identifier if error relates to parental controls
            feature: Feature name where error occurred
            timestamp: When the error occurred (defaults to now)
            additional_data: Additional context information
        """
        self.child_id = child_id
        self.parent_id = parent_id
        self.feature = feature
        self.timestamp = timestamp or datetime.utcnow()
        self.additional_data = additional_data or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for logging and serialization."""
        return {
            "child_id": self.child_id,
            "parent_id": self.parent_id,
            "feature": self.feature,
            "timestamp": self.timestamp.isoformat(),
            "additional_data": self.additional_data,
        }


class TeddyBearException(Exception):
    """
    Base exception class for all AI Teddy Bear system errors.
    Provides structured error handling with severity levels, context,
    and child safety considerations.
    """

    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[ErrorContext] = None,
        user_message: Optional[str] = None,
    ) -> None:
        """
        Initialize exception with comprehensive error information.
        Args:
            message: Technical error message for developers
            severity: Error severity level
            context: Additional context information
            user_message: Child-friendly error message for users
        """
        super().__init__(message)
        self.severity = severity
        self.context = context or ErrorContext()
        self.user_message = user_message or self._generate_child_friendly_message()

    def _generate_child_friendly_message(self) -> str:
        """Generate appropriate error message for children."""
        if self.severity == ErrorSeverity.CRITICAL:
            return (
                "I need to talk to your parent or guardian about something important."
            )
        elif self.severity == ErrorSeverity.HIGH:
            return "Something isn't working right now. Let's try again in a moment."
        else:
            return "Oops! Let me try that again for you."

    def __str__(self) -> str:
        """Return comprehensive error string for logging."""
        return (
            f"{self.__class__.__name__}: {self.args[0]} "
            f"(Severity: {self.severity.value})"
        )


class ParentalConsentRequiredException(TeddyBearException):
    """
    Exception raised when parental consent is required for an action.
    This is a critical child safety exception that should always be handled
    with proper escalation to parents or guardians.
    """

    def __init__(
        self,
        feature: str,
        child_id: Optional[str] = None,
        context: Optional[ErrorContext] = None,
    ) -> None:
        """
        Initialize parental consent exception.
        Args:
            feature: Feature requiring consent
            child_id: Child identifier
            context: Additional context
        """
        message = f"Parental consent required for feature: {feature}"
        user_message = "I need permission from your parent or guardian to do that."
        # Enhance context with consent-specific information
        if context is None:
            context = ErrorContext()
        context.feature = feature
        context.child_id = child_id
        context.additional_data.update(
            {"consent_required": True, "feature_requested": feature}
        )
        super().__init__(
            message=message,
            severity=ErrorSeverity.CRITICAL,
            context=context,
            user_message=user_message,
        )


class CircuitBreakerOpenException(TeddyBearException):
    """
    Exception raised when circuit breaker is open due to service failures.
    Indicates that a service is temporarily unavailable for safety reasons.
    """

    def __init__(
        self, service_name: str, context: Optional[ErrorContext] = None
    ) -> None:
        """
        Initialize circuit breaker exception.
        Args:
            service_name: Name of the affected service
            context: Additional context
        """
        message = (
            f"Service temporarily unavailable: {service_name} (circuit breaker open)"
        )
        user_message = "I'm having trouble right now. Let's try again in a few minutes!"
        # Enhance context with circuit breaker information
        if context is None:
            context = ErrorContext()
        context.additional_data.update(
            {"service_name": service_name, "circuit_breaker_open": True}
        )
        super().__init__(
            message=message,
            severity=ErrorSeverity.HIGH,
            context=context,
            user_message=user_message,
        )


class StartupValidationException(TeddyBearException):
    """
    Custom exception for security-related issues during application startup.
    This exception is raised when a security-sensitive configuration
    or operation fails validation, indicating a potential vulnerability
    or misconfiguration that could compromise the system.
    """

    def __init__(
        self,
        message: str = "Application startup validation failed",
        context: Optional[ErrorContext] = None,
    ) -> None:
        # Ensure it's always treated as a critical issue for startup failures
        super().__init__(
            message=message, severity=ErrorSeverity.CRITICAL, context=context
        )
