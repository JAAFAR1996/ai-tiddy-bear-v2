"""Base exception classes for the domain layer.
This module defines the core exception hierarchy that all domain
exceptions inherit from, ensuring consistent error handling.
"""

from typing import Any


class DomainException(Exception):
    """Base exception for all domain - related errors.
    This provides a common interface for all domain exceptions
    and includes structured error information.
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        context: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
        }


class ValidationError(DomainException):
    """Raised when domain validation rules are violated."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any | None = None,
        **kwargs,
    ):
        context = kwargs.get("context", {})
        if field:
            context["field"] = field
        if value is not None:
            context["invalid_value"] = str(value)
        super().__init__(message, "VALIDATION_ERROR", context)
        self.field = field
        self.value = value


class AuthorizationError(DomainException):
    """Raised when authorization checks fail."""

    def __init__(
        self,
        message: str = "Access denied",
        resource: str | None = None,
        action: str | None = None,
        **kwargs,
    ):
        context = kwargs.get("context", {})
        if resource:
            context["resource"] = resource
        if action:
            context["action"] = action
        super().__init__(message, "AUTHORIZATION_ERROR", context)
        self.resource = resource
        self.action = action


class NotFoundError(DomainException):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        message: str,
        resource_type: str | None = None,
        resource_id: str | None = None,
        **kwargs,
    ):
        context = kwargs.get("context", {})
        if resource_type:
            context["resource_type"] = resource_type
        if resource_id:
            context["resource_id"] = resource_id
        super().__init__(message, "NOT_FOUND_ERROR", context)
        self.resource_type = resource_type
        self.resource_id = resource_id


class ConflictError(DomainException):
    """Raised when an operation conflicts with current state."""

    def __init__(
        self,
        message: str,
        resource_type: str | None = None,
        conflict_reason: str | None = None,
        **kwargs,
    ):
        context = kwargs.get("context", {})
        if resource_type:
            context["resource_type"] = resource_type
        if conflict_reason:
            context["conflict_reason"] = conflict_reason
        super().__init__(message, "CONFLICT_ERROR", context)
        self.resource_type = resource_type
        self.conflict_reason = conflict_reason
