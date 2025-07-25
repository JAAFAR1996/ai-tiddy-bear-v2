"""Application-layer exceptions."""

from typing import Any

from .base_exceptions import AITeddyBaseError, ErrorCategory


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
