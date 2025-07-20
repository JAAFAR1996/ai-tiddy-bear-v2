"""Child-specific domain exceptions."""

from .base_exceptions import DomainException, NotFoundError, ValidationError


class ChildNotFoundError(NotFoundError):
    """Raised when a child profile cannot be found."""
    pass


class ChildCreationError(DomainException):
    """Raised when child profile creation fails."""
    pass


class ChildAccessDeniedError(DomainException):
    """Raised when access to child data is denied."""
    pass


class InvalidChildAgeError(ValidationError):
    """Raised when child age is invalid."""
    pass
