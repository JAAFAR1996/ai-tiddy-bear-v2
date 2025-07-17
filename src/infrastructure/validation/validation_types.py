"""
Validation Types and Data Structures
Common types, enums, and data classes used across validation modules.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any


@dataclass
class ValidationResult:
    """Structured validation result with comprehensive metadata."""

    valid: bool
    sanitized_value: Optional[Any] = None
    original_value: Optional[Any] = None
    errors: List[str] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None
    security_flags: List[str] = None

    def __post_init__(self) -> None:
        """Initialize default values for lists and dicts."""
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}
        if self.security_flags is None:
            self.security_flags = []


class ValidationSeverity(Enum):
    """Validation issue severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationError(Exception):
    """Custom exception for validation errors with enhanced context."""

    def __init__(
        self,
        message: str,
        field: str = None,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        original_value: Any = None,
        security_risk: bool = False,
    ) -> None:
        """Initialize validation error with context."""
        super().__init__(message)
        self.field = field
        self.severity = severity
        self.original_value = original_value
        self.security_risk = security_risk
        self.timestamp = None  # Could be added for audit trails


# Common validation patterns
PATTERNS = {
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "phone": r"^\+?[\d\s\-\(\)]{7,15}$",
    "url": r"^https?://[^\s/$.?#].[^\s]*$",
    "child_id": r"^child_[a-zA-Z0-9]{8,16}$",
    "parent_id": r"^parent_[a-zA-Z0-9]{8,16}$",
    "safe_text": r"^[\w\s\.\,\!\?\-\'\"]*$",
}

# Age-based validation thresholds
AGE_THRESHOLDS = {
    "min_age": 3,
    "max_age": 17,
    "coppa_age": 13,
    "teen_age": 13,
}

# Content length limits
LENGTH_LIMITS = {
    "child_name": {"min": 1, "max": 50},
    "parent_name": {"min": 1, "max": 100},
    "message": {"min": 1, "max": 1000},
    "email": {"min": 5, "max": 254},
    "phone": {"min": 7, "max": 15},
    "address": {"min": 5, "max": 200},
}

# Dangerous patterns to detect
SECURITY_PATTERNS = {
    "sql_injection": [
        r"(union|select|insert|update|delete|drop|create|alter|exec|execute)",
        r"('|(\x27)|(\x2D)|(\x23)|(\x3B))",
        r"(--|#|/\*|\*/|@|\||`)",
    ],
    "xss": [
        r"<script|</script>|javascript:|onclick|onload|onerror",
        r"expression\(|eval\(|setTimeout\(|setInterval\(",
        r"document\.|window\.|location\.",
    ],
    "path_traversal": [
        r"\.\./|\.\.\\/|/\.\./|\\\.\.\\",
        r"(\x2e\x2e\x2f|%2e%2e%2f|\x2e\x2e/)",
    ],
    "command_injection": [
        r"(;|\|&|&&|\|\||`|\$\()",
        r"(exec|system|eval|shell_exec|passthru)",
        r"(nc|netcat|telnet|wget|curl|ping)",
    ],
}
