"""
Standardized exception hierarchy for AI Teddy Bear backend.

Provides consistent error types and messaging across the application.
"""

from typing import Optional, Dict, Any


class AITeddyError(Exception):
    """Base exception for all AI Teddy Bear specific errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        http_status: int = 500,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.http_status = http_status


class ValidationError(AITeddyError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str = "Input validation failed",
        field: Optional[str] = None,
        value: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if field:
            details["field"] = field
        if value:
            details["value"] = str(value)[:100]  # Truncate for security
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            http_status=400,
        )


class AuthenticationError(AITeddyError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            http_status=401,
            **kwargs,
        )


class AuthorizationError(AITeddyError):
    """Raised when authorization fails."""

    def __init__(
        self,
        message: str = "Access denied",
        resource: Optional[str] = None,
        action: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if resource:
            details["resource"] = resource
        if action:
            details["action"] = action
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            http_status=403,
            details=details,
            **kwargs,
        )


class ExternalServiceError(AITeddyError):
    """Raised for errors related to external services (e.g., OpenAI, Azure)."""

    def __init__(
        self,
        service_name: str,
        message: str = "External service error",
        **kwargs,
    ):
        details = kwargs.get("details", {})
        details["service"] = service_name
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
            http_status=502,  # Bad Gateway
            **kwargs,
        )


class DatabaseError(AITeddyError):
    """Raised for database-related errors."""

    def __init__(self, message: str = "Database error", **kwargs):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            http_status=500,
            **kwargs,
        )


class SystemError(AITeddyError):
    """Raised for general system errors."""

    def __init__(self, message: str = "System error", **kwargs):
        super().__init__(
            message=message,
            error_code="SYSTEM_ERROR",
            http_status=500,
            **kwargs,
        )


class ChildSafetyError(AITeddyError):
    """Raised when a child safety rule is violated."""

    def __init__(
        self,
        message: str = "Child safety violation",
        reason: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if reason:
            details["reason"] = reason
        super().__init__(
            message=message,
            error_code="CHILD_SAFETY_VIOLATION",
            details=details,
            http_status=400,
            **kwargs,
        )


class NotFoundError(AITeddyError):
    """Raised when a resource is not found."""

    def __init__(
        self, resource_name: str, resource_id: Optional[str] = None, **kwargs
    ):
        message = f"{resource_name} not found"
        if resource_id:
            message += f" with ID: {resource_id}"
        super().__init__(
            message=message, error_code="NOT_FOUND", http_status=404, **kwargs
        )


class ConflictError(AITeddyError):
    """Raised when there is a conflict with the current state of a resource."""

    def __init__(
        self,
        resource_name: str,
        conflicting_field: Optional[str] = None,
        **kwargs,
    ):
        message = f"Conflict with {resource_name}"
        details = kwargs.get("details", {})
        if conflicting_field:
            details["conflicting_field"] = conflicting_field
        super().__init__(
            message=message,
            error_code="CONFLICT",
            details=details,
            http_status=409,
            **kwargs,
        )


class RateLimitError(AITeddyError):
    """Raised when a rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
            http_status=429,
            **kwargs,
        )
