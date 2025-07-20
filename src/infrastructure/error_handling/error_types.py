"""Error types required by decorators.py"""

from enum import Enum


class ErrorType(Enum):
    """Types of errors in the system."""
    INTERNAL_ERROR = "internal_error"
    SERVICE_UNAVAILABLE = "service_unavailable"


class ErrorSeverity(Enum):
    """Severity levels for errors."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BaseApplicationError(Exception):
    """Base application error that decorators.py expects."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ExternalServiceError(BaseApplicationError):
    """External service error that decorators.py expects."""
    
    def __init__(self, message: str):
        super().__init__(message)


class ErrorContext:
    """Context information for errors."""
    
    def __init__(self, error_type: ErrorType, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
        self.error_type = error_type
        self.severity = severity
