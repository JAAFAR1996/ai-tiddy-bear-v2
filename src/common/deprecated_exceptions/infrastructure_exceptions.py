"""Infrastructure-layer exceptions."""

from typing import Optional

from .base_exceptions import AITeddyBaseError, ErrorCategory


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
