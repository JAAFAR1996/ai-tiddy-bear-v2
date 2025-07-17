"""from .validation_config import ValidationRule, ValidationSeverity."""

"""Validation Rules and Patterns
Extracted from input_validation.py to reduce file size"""


def get_default_validation_rules() -> list[ValidationRule]:
    """Get default validation rules for child safety."""
    return [
        # Script injection attempts
        ValidationRule(
            pattern=r"<script[^>]*>.*?</script>",
            message="Script tags detected",
            severity=ValidationSeverity.CRITICAL,
        ),
        ValidationRule(
            pattern=r"javascript:",
            message="JavaScript protocol detected",
            severity=ValidationSeverity.CRITICAL,
        ),
        ValidationRule(
            pattern=r"on\\w+\\s*=",
            message="Event handler attributes detected",
            severity=ValidationSeverity.HIGH,
        ),
        # SQL injection attempts
        ValidationRule(
            pattern=r"(union|select|insert|delete|update|drop|create|alter)\\s+",
            message="SQL keywords detected",
            severity=ValidationSeverity.HIGH,
        ),
        ValidationRule(
            pattern=r"[\'\"]\\s*(or|and)\\s*[\'\"]\\s*=\\s*[\'\"]\\s*[\'\"]\\s*",
            message="SQL injection pattern detected",
            severity=ValidationSeverity.CRITICAL,
        ),
        # Command injection
        ValidationRule(
            pattern=r"[\\;\\|\\&\\$\\`]",
            message="Command injection characters detected",
            severity=ValidationSeverity.HIGH,
        ),
        # Path traversal
        ValidationRule(
            pattern=r"\\.\\./|\\.\\.\\.",
            message="Path traversal attempt detected",
            severity=ValidationSeverity.HIGH,
        ),
        # Personal information (for child safety)
        ValidationRule(
            pattern=r"\\b\\d{3}-\\d{2}-\\d{4}\\b",
            message="Social security number pattern detected",
            severity=ValidationSeverity.CRITICAL,
            action="block",
        ),
        ValidationRule(
            pattern=r"\\b\\d{4}[\\s\\-]?\\d{4}[\\s\\-]?\\d{4}[\\s\\-]?\\d{4}\\b",
            message="Credit card number pattern detected",
            severity=ValidationSeverity.CRITICAL,
            action="block",
        ),
        ValidationRule(
            pattern=r"\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b",
            message="Email address detected in child input",
            severity=ValidationSeverity.MEDIUM,
            action="sanitize",
        ),
    ]


def get_profanity_words() -> set[str]:
    """Get profanity words list(placeholder)
    In production, load from external file or service.
    """
    return {
        "badword1",
        "badword2",
        "inappropriate",
        # Add actual profanity words list
    }
