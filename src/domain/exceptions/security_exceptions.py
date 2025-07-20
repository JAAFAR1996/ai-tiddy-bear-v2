"""Security-specific domain exceptions."""

from .base_exceptions import DomainException, ValidationError


class SecurityValidationError(ValidationError):
    """Raised when security validation fails."""
    pass


class AuthenticationError(DomainException):
    """Raised when authentication fails."""
    pass


class PermissionDeniedError(DomainException):
    """Raised when permission is denied."""
    pass


class ContentSafetyError(DomainException):
    """Raised when content safety validation fails."""
    pass
