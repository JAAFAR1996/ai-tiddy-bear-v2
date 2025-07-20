"""Input Sanitization Logic
Extracted from input_validation.py to reduce file size
"""

import re
from typing import Any

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")

try:
    from .validation_config import InputValidationConfig, ValidationSeverity
    from .validation_rules import get_default_validation_rules, get_profanity_words
except ImportError:
    # Fallback definitions for missing dependencies
    from dataclasses import dataclass
    from enum import Enum

    class ValidationSeverity(Enum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"

    @dataclass
    class ValidationRule:
        pattern: str
        message: str
        severity: ValidationSeverity
        action: str = "warn"

    @dataclass
    class InputValidationConfig:
        dangerous_patterns: list[ValidationRule] = None
        enable_profanity_filter: bool = True
        child_max_string_length: int = 100
        max_string_length: int = 1000
        child_safe_pattern: str = r"^[a-zA-Z0-9\s\.\,\!\?\-\'\"]*$"
        max_object_depth: int = 10
        max_array_length: int = 100
        child_max_array_length: int = 50

    def get_default_validation_rules():
        return [
            ValidationRule(
                pattern=r"<script[^>]*>.*?</script>",
                message="XSS script tag detected",
                severity=ValidationSeverity.HIGH,
                action="block",
            ),
            ValidationRule(
                pattern=r"javascript:",
                message="JavaScript injection attempt",
                severity=ValidationSeverity.HIGH,
                action="block",
            ),
            ValidationRule(
                pattern=r"(\b(DROP|DELETE|INSERT|UPDATE|SELECT)\b)",
                message="SQL injection attempt",
                severity=ValidationSeverity.CRITICAL,
                action="block",
            ),
        ]

    def get_profanity_words():
        # Basic profanity list - in production, use a comprehensive list
        return {
            "bad",
            "ugly",
            "stupid",
            "hate",
            "kill",
            "die",
            "damn",
            "hell",
            "idiot",
            "moron",
            "loser",
            "freak",
            "weird",
            "gross",
            "sick",
        }


class InputSanitizer:
    """Sanitizes user input for child safety and security."""

    def __init__(self, config: InputValidationConfig) -> None:
        self.config = config or InputValidationConfig()
        # Set default patterns if not provided
        if not self.config.dangerous_patterns:
            self.config.dangerous_patterns = get_default_validation_rules()
        self.compiled_patterns = self._compile_patterns()
        # Load profanity words if enabled
        if self.config.enable_profanity_filter:
            self.profanity_words = get_profanity_words()
        else:
            self.profanity_words = set()

    def _compile_patterns(self) -> list[tuple]:
        """Compile regex patterns for performance."""
        compiled = []
        for rule in self.config.dangerous_patterns:
            try:
                pattern = re.compile(rule.pattern, re.IGNORECASE | re.DOTALL)
                compiled.append((pattern, rule))
            except re.error as e:
                logger.error(f"Invalid regex pattern '{rule.pattern}': {e}")
        return compiled

    def sanitize_string(
        self,
        value: str,
        is_child_input: bool = False,
        context: str = "general",
    ) -> dict[str, Any]:
        """Sanitize string input with comprehensive validation

        Args:
            value: String to sanitize
            is_child_input: Whether input comes from child user
            context: Context of the input (message, name, etc.)

        Returns:
            Dict with sanitized value and validation results.
        """
        result = {
            "original": value,
            "sanitized": value,
            "is_safe": True,
            "violations": [],
            "warnings": [],
        }
        try:
            # Check length limits
            max_length = (
                self.config.child_max_string_length
                if is_child_input
                else self.config.max_string_length
            )
            if len(value) > max_length:
                result["violations"].append(
                    {
                        "type": "length_exceeded",
                        "severity": "medium",
                        "message": f"Input length ({len(value)}) exceeds limit ({max_length})",
                    },
                )
                result["sanitized"] = value[:max_length]
                result["is_safe"] = False

            # Check child-safe characters
            if is_child_input:
                if not re.match(self.config.child_safe_pattern, value):
                    result["violations"].append(
                        {
                            "type": "unsafe_characters",
                            "severity": "high",
                            "message": "Input contains characters not suitable for children",
                        },
                    )
                    # Remove unsafe characters
                    result["sanitized"] = re.sub(
                        r"[^a-zA-Z0-9\\s\\.\\,\\!\\?\\-\\\'\\\"]",
                        "",
                        result["sanitized"],
                    )
                    result["is_safe"] = False

            # Check for dangerous patterns
            for pattern, rule in self.compiled_patterns:
                if pattern.search(result["sanitized"]):
                    violation = {
                        "type": "dangerous_pattern",
                        "severity": rule.severity.value,
                        "message": rule.message,
                        "pattern": rule.pattern,
                    }
                    if rule.action == "block":
                        result["violations"].append(violation)
                        result["is_safe"] = False
                        if rule.severity in [
                            ValidationSeverity.CRITICAL,
                            ValidationSeverity.HIGH,
                        ]:
                            result["sanitized"] = "[BLOCKED: UNSAFE CONTENT]"
                            break
                    elif rule.action == "sanitize":
                        result["warnings"].append(violation)
                        result["sanitized"] = pattern.sub(
                            "[REDACTED]",
                            result["sanitized"],
                        )
                    elif rule.action == "warn":
                        result["warnings"].append(violation)

            # Profanity filter
            if self.config.enable_profanity_filter and self.profanity_words:
                words = result["sanitized"].lower().split()
                contains_profanity = any(word in self.profanity_words for word in words)
                if contains_profanity:
                    result["violations"].append(
                        {
                            "type": "profanity",
                            "severity": "high" if is_child_input else "medium",
                            "message": "Inappropriate language detected",
                        },
                    )
                    # Replace profanity with asterisks
                    for word in words:
                        if word in self.profanity_words:
                            result["sanitized"] = result["sanitized"].replace(
                                word,
                                "*" * len(word),
                            )
                    result["is_safe"] = False

            # Log violations for audit
            if result["violations"]:
                logger.warning(
                    f"Input validation violations in {context}: "
                    f"{[v['type'] for v in result['violations']]}",
                )
            return result
        except Exception as e:
            logger.error(f"Error sanitizing string input: {e}")
            return {
                "original": value,
                "sanitized": "[ERROR: PROCESSING FAILED]",
                "is_safe": False,
                "violations": [
                    {
                        "type": "processing_error",
                        "severity": "critical",
                        "message": "Failed to process input safely",
                    },
                ],
                "warnings": [],
            }

    def sanitize_json(self, data: Any, is_child_input: bool = False) -> dict[str, Any]:
        """Sanitize JSON data recursively."""
        result = {
            "original": data,
            "sanitized": data,
            "is_safe": True,
            "violations": [],
            "warnings": [],
        }
        try:
            result["sanitized"] = self._sanitize_json_recursive(
                data,
                is_child_input,
                0,
                result,
            )
            return result
        except Exception as e:
            logger.error(f"Error sanitizing JSON: {e}")
            result["is_safe"] = False
            result["violations"].append(
                {
                    "type": "json_processing_error",
                    "severity": "critical",
                    "message": f"Failed to process JSON safely: {e!s}",
                },
            )
            return result

    def _sanitize_json_recursive(
        self,
        data: Any,
        is_child_input: bool,
        depth: int,
        result: dict,
    ) -> Any:
        """Recursively sanitize JSON data."""
        # Check depth limit
        if depth > self.config.max_object_depth:
            result["violations"].append(
                {
                    "type": "depth_exceeded",
                    "severity": "high",
                    "message": f"Object depth ({depth}) exceeds limit ({self.config.max_object_depth})",
                },
            )
            result["is_safe"] = False
            return None

        if isinstance(data, dict):
            # Check object size
            if len(data) > self.config.max_array_length:
                result["violations"].append(
                    {
                        "type": "object_size_exceeded",
                        "severity": "medium",
                        "message": "Object size exceeds limit",
                    },
                )
                result["is_safe"] = False
            sanitized = {}
            for key, value in data.items():
                # Sanitize key
                key_result = self.sanitize_string(
                    str(key),
                    is_child_input,
                    "object_key",
                )
                if not key_result["is_safe"]:
                    result["violations"].extend(key_result["violations"])
                    result["is_safe"] = False
                # Sanitize value
                sanitized[key_result["sanitized"]] = self._sanitize_json_recursive(
                    value,
                    is_child_input,
                    depth + 1,
                    result,
                )
            return sanitized
        if isinstance(data, list):
            # Check array size
            max_length = (
                self.config.child_max_array_length
                if is_child_input
                else self.config.max_array_length
            )
            if len(data) > max_length:
                result["violations"].append(
                    {
                        "type": "array_size_exceeded",
                        "severity": "medium",
                        "message": "Array size exceeds limit",
                    },
                )
                result["is_safe"] = False
                data = data[:max_length]
            return [
                self._sanitize_json_recursive(item, is_child_input, depth + 1, result)
                for item in data
            ]
        if isinstance(data, str):
            string_result = self.sanitize_string(data, is_child_input, "json_string")
            if not string_result["is_safe"]:
                result["violations"].extend(string_result["violations"])
                result["warnings"].extend(string_result["warnings"])
                result["is_safe"] = False
            return string_result["sanitized"]
        # Numbers, booleans, None - return as-is
        return data


# Global instance for easy access
_sanitizer_instance = None


def get_input_sanitizer(config: InputValidationConfig = None) -> InputSanitizer:
    """Get global input sanitizer instance."""
    global _sanitizer_instance
    if _sanitizer_instance is None:
        _sanitizer_instance = InputSanitizer(config or InputValidationConfig())
    return _sanitizer_instance


# Convenience functions
def sanitize_child_input(text: str, context: str = "message") -> dict[str, Any]:
    """Quick sanitization for child input."""
    sanitizer = get_input_sanitizer()
    return sanitizer.sanitize_string(text, is_child_input=True, context=context)


def sanitize_adult_input(text: str, context: str = "general") -> dict[str, Any]:
    """Quick sanitization for adult input."""
    sanitizer = get_input_sanitizer()
    return sanitizer.sanitize_string(text, is_child_input=False, context=context)


def is_safe_for_children(text: str) -> bool:
    """Quick check if text is safe for children."""
    result = sanitize_child_input(text)
    return result["is_safe"]
