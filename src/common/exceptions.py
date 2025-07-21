"""Centralized exception system for AI Teddy Bear.
All exceptions should be imported from this module.
"""

from typing import Any, Dict, Optional
from enum import Enum

# ===================
# 1. التصنيفات (Enum)
# ===================


class ErrorCategory(Enum):
    """Categories for error classification."""
    DOMAIN = "domain"
    APPLICATION = "application"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    VALIDATION = "validation"

# =============================
# 2. الأساس الأعلى Base Error
# =============================


class AITeddyBaseError(Exception):
    """Base exception for all AI Teddy Bear errors."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None
    ):
        self.message = message
        self.category = category
        self.details = details or {}
        self.error_code = error_code
        super().__init__(self.message)

# ========================
# 3. استثناءات الدومين Domain
# ========================


class DomainException(AITeddyBaseError):
    """Base domain exception."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.DOMAIN, **kwargs)


class ChildSafetyException(DomainException):
    """Child safety errors."""

    def __init__(self, message: str = "Child safety violation", **kwargs):
        super().__init__(message, **kwargs)


class ConsentError(DomainException):
    """Raised when consent-related operations fail."""
    """Consent handling errors."""

    def __init__(self, message: str = "Consent error", **kwargs):
        super().__init__(message, **kwargs)


class AgeRestrictionException(DomainException):
    """Age restriction errors."""

    def __init__(self, message: str = "Age restriction error", **kwargs):
        super().__init__(message, **kwargs)

# ===========================
# 4. استثناءات التطبيق Application
# ===========================


class ApplicationException(AITeddyBaseError):
    """Base application exception."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.APPLICATION, **kwargs)


class ServiceUnavailableError(ApplicationException):
    """Service unavailability errors."""

    def __init__(self, message: str = "Service temporarily unavailable", **kwargs):
        super().__init__(
            message=message,
            error_code="SERVICE_UNAVAILABLE",
            **kwargs
        )


class InvalidInputError(ApplicationException):
    """Invalid input errors."""

    def __init__(self, message: str = "Invalid input provided", **kwargs):
        super().__init__(
            message=message,
            error_code="INVALID_INPUT",
            **kwargs
        )


class TimeoutError(ApplicationException):
    """Operation timeout errors."""

    def __init__(self, message: str = "Operation timed out", **kwargs):
        super().__init__(
            message=message,
            error_code="TIMEOUT",
            **kwargs
        )


class ResourceNotFoundError(ApplicationException):
    """Resource not found errors."""

    def __init__(self, resource: str, identifier: Any, **kwargs):
        super().__init__(
            message=f"{resource} with ID '{identifier}' not found",
            error_code="RESOURCE_NOT_FOUND",
            details={"resource": resource, "identifier": str(identifier)},
            **kwargs
        )


class StartupValidationException(ApplicationException):
    """Startup validation errors."""

    def __init__(self, message: str = "Startup validation failed", **kwargs):
        super().__init__(
            message=message,
            error_code="STARTUP_VALIDATION_FAILED",
            **kwargs
        )

# ================================
# 5. استثناءات البنية التحتية Infrastructure
# ================================


class InfrastructureException(AITeddyBaseError):
    """Base infrastructure exception."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.INFRASTRUCTURE, **kwargs)


class DatabaseConnectionError(InfrastructureException):
    """Database connection errors."""

    def __init__(self, message: str = "Database connection failed", **kwargs):
        super().__init__(message, **kwargs)


class ConfigurationError(InfrastructureException):
    """Configuration errors."""

    def __init__(self, message: str = "Invalid configuration", **kwargs):
        super().__init__(message, **kwargs)


class ExternalServiceError(InfrastructureException):
    """External service errors."""

    def __init__(self, message: str = "External service failure", **kwargs):
        super().__init__(message, **kwargs)


class SecurityError(InfrastructureException):
    """Security-related infrastructure errors."""

    def __init__(self, message: str = "Security error", **kwargs):
        super().__init__(message, **kwargs)


class RateLimitExceededError(InfrastructureException):
    """Rate limit exceeded errors."""

    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(message, **kwargs)


# ===========
# 6. __all__
# ===========
__all__ = [
    # Base
    "AITeddyBaseError",
    "ErrorCategory",
    # Domain
    "DomainException",
    "ChildSafetyException",
    "ConsentError",
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
