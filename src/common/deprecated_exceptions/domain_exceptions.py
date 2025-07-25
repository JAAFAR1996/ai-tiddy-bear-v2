"""Domain-specific exceptions."""

from .base_exceptions import AITeddyBaseError, ErrorCategory


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
