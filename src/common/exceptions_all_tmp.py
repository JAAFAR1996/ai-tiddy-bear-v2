"""Centralized exception system for AI Teddy Bear.
All exceptions should be imported from this module.
"""

from enum import Enum

# Application exceptions
from typing import Any, Dict, Optional

from .application_exceptions import (
    ApplicationException,
    InvalidInputError,
    ResourceNotFoundError,
    ServiceUnavailableError,
    StartupValidationException,
    TimeoutError,
)

# Base exceptions
from .base_exceptions import AITeddyBaseError, ErrorCategory

# Domain exceptions
from .domain_exceptions import (
    AgeRestrictionException,
    ChildSafetyException,
    ConsentException,
    DomainException,
)

# Infrastructure exceptions
from .infrastructure_exceptions import (
    ConfigurationError,
    DatabaseConnectionError,
    ExternalServiceError,
    InfrastructureException,
    RateLimitExceededError,
    SecurityError,
)

__all__ = [
    # Base
    "AITeddyBaseError",
    "ErrorCategory",
    # Domain
    "DomainException",
    "ChildSafetyException",
    "ConsentException",
    "AgeRestrictionException",
    # Application
    "ApplicationException",
    "ServiceUnavailableError",
    "InvalidInputError",
    "TimeoutError",
    "ResourceNotFoundError",
    "StartupValidationException",
    # Infrastructure
    "InfrastructureException",
    "DatabaseConnectionError",
    "ConfigurationError",
    "ExternalServiceError",
    "SecurityError",
    "RateLimitExceededError",
]


class ApplicationException(AITeddyBaseError):
    """Base application exception."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.APPLICATION, **kwargs)


class ServiceUnavailableError(ApplicationException):
    """Service unavailability errors."""

    def __init__(self, message: str = "Service temporarily unavailable", **kwargs):
        super().__init__(message=message, error_code="SERVICE_UNAVAILABLE", **kwargs)


class InvalidInputError(ApplicationException):
    """Invalid input errors."""

    def __init__(self, message: str = "Invalid input provided", **kwargs):
        super().__init__(message=message, error_code="INVALID_INPUT", **kwargs)


class TimeoutError(ApplicationException):
    """Operation timeout errors."""

    def __init__(self, message: str = "Operation timed out", **kwargs):
        super().__init__(message=message, error_code="TIMEOUT", **kwargs)


class ResourceNotFoundError(ApplicationException):
    """Resource not found errors."""

    def __init__(self, resource: str, identifier: Any, **kwargs):
        super().__init__(
            message=f"{resource} with ID '{identifier}' not found",
            error_code="RESOURCE_NOT_FOUND",
            details={"resource": resource, "identifier": str(identifier)},
            **kwargs,
        )


class StartupValidationException(ApplicationException):
    """Startup validation errors."""

    def __init__(self, message: str = "Startup validation failed", **kwargs):
        super().__init__(
            message=message, error_code="STARTUP_VALIDATION_FAILED", **kwargs
        )


"""Base exceptions for AI Teddy Bear system.
Central location for all base exception classes.
"""


class ErrorCategory(Enum):
    """Categories for error classification."""

    DOMAIN = "domain"
    APPLICATION = "application"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    VALIDATION = "validation"


class AITeddyBaseError(Exception):
    """Base exception for all AI Teddy Bear errors."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
    ):
        self.message = message
        self.category = category
        self.details = details or {}
        self.error_code = error_code
        super().__init__(self.message)


"""Domain-specific exceptions."""


class DomainException(AITeddyBaseError):
    """Base domain exception."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.DOMAIN, **kwargs)


class ChildSafetyException(DomainException):
    """Child safety violations."""

    def __init__(self, message: str = "Child safety violation detected", **kwargs):
        super().__init__(message=message, error_code="CHILD_SAFETY_VIOLATION", **kwargs)


class ConsentException(DomainException):
    """Consent-related errors."""

    def __init__(self, message: str = "Parental consent required", **kwargs):
        super().__init__(message=message, error_code="CONSENT_REQUIRED", **kwargs)


class AgeRestrictionException(DomainException):
    """Age restriction violations."""

    def __init__(self, message: str = "Age restriction violation", **kwargs):
        super().__init__(message=message, error_code="AGE_RESTRICTION", **kwargs)


# Additional domain exceptions from old files
class ChildNotFoundException(DomainException):
    """Child not found error."""

    def __init__(self, child_id: str, **kwargs):
        super().__init__(
            message=f"Child with ID '{child_id}' not found",
            error_code="CHILD_NOT_FOUND",
            details={"child_id": child_id},
            **kwargs,
        )


class InvalidChildDataException(DomainException):
    """Invalid child data error."""

    def __init__(self, field: str, reason: str, **kwargs):
        super().__init__(
            message=f"Invalid child data for field '{field}': {reason}",
            error_code="INVALID_CHILD_DATA",
            details={"field": field, "reason": reason},
            **kwargs,
        )


class AuthenticationFailedException(DomainException):
    """Authentication failed error."""

    def __init__(self, reason: str = "Authentication failed", **kwargs):
        super().__init__(message=reason, error_code="AUTHENTICATION_FAILED", **kwargs)


class InsufficientPermissionsException(DomainException):
    """Insufficient permissions error."""

    def __init__(self, required_permission: str, **kwargs):
        super().__init__(
            message=f"Insufficient permissions. Required: {required_permission}",
            error_code="INSUFFICIENT_PERMISSIONS",
            details={"required_permission": required_permission},
            **kwargs,
        )


class ConsentError(DomainException):
    """Raised when consent verification fails."""


"""Infrastructure-layer exceptions."""


class InfrastructureException(AITeddyBaseError):
    """Base infrastructure exception."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.INFRASTRUCTURE, **kwargs)


class DatabaseConnectionError(InfrastructureException):
    """Database connection errors."""

    def __init__(self, message: str = "Database connection failed", **kwargs):
        super().__init__(
            message=message, error_code="DATABASE_CONNECTION_ERROR", **kwargs
        )


class ConfigurationError(InfrastructureException):
    """Configuration errors."""

    def __init__(self, message: str = "Configuration error", **kwargs):
        super().__init__(message=message, error_code="CONFIGURATION_ERROR", **kwargs)


class ExternalServiceError(InfrastructureException):
    """External service errors."""

    def __init__(
        self, service: str, original_error: Optional[Exception] = None, **kwargs
    ):
        details = kwargs.get("details", {})
        details["service"] = service
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(
            message=f"External service error: {service}",
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
            **kwargs,
        )


class SecurityError(InfrastructureException):
    """Security-related errors."""

    def __init__(self, message: str = "Security violation", **kwargs):
        super().__init__(message=message, error_code="SECURITY_ERROR", **kwargs)


class RateLimitExceededError(InfrastructureException):
    """Rate limit errors."""

    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(message=message, error_code="RATE_LIMIT_EXCEEDED", **kwargs)
