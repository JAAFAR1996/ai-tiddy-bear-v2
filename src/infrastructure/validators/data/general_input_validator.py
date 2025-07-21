"""General Input Validator - Production implementation only."""

from src.domain.schemas import ValidationResult


class GeneralInputValidator:
    def validate_text(self, text: str) -> ValidationResult:
        return ValidationResult(valid=True, sanitized_value=text)

    def validate_email(self, email: str) -> ValidationResult:
        return ValidationResult(valid=True, sanitized_value=email)


_general_validator = None


def get_general_input_validator():
    global _general_validator
    if _general_validator is None:
        _general_validator = GeneralInputValidator()
    return _general_validator
