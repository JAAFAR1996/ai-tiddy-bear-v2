"""Base validators for AI Teddy Bear system."""

import re
from abc import ABC, abstractmethod
from typing import Any, Protocol


class ValidatorProtocol(Protocol):
    """Protocol for all validators."""

    def validate(self, value: Any) -> bool:
        """Validate a value."""
        ...

    def sanitize(self, value: Any) -> Any:
        """Sanitize a value."""
        ...


class BaseValidator(ABC):
    """Abstract base class for all validators."""

    @abstractmethod
    def validate(self, value: Any) -> bool:
        """Validate a value. Must be implemented by subclasses."""

    @abstractmethod
    def sanitize(self, value: Any) -> Any:
        """Sanitize a value. Must be implemented by subclasses."""

    @staticmethod
    def is_safe_string(value: str, max_length: int = 255) -> bool:
        """Check if string is safe from injection attacks."""
        if not value or len(value) > max_length:
            return False

        # Check for dangerous patterns
        dangerous_patterns = [
            r"<script",
            r"javascript:",
            r"onclick=",
            r"onerror=",
            r"--",
            r";\s*(DROP|DELETE|INSERT|UPDATE|SELECT)",
            r"UNION\s+SELECT",
            r"xp_cmdshell",
            r"exec\s*\(",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return False

        return True

    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize string by removing dangerous characters."""
        if not value:
            return value

        # Remove null bytes and control characters
        value = value.replace("\x00", "")
        value = "".join(char for char in value if ord(char) >= 32 or char in "\n\r\t")

        # HTML entity encoding for special characters
        replacements = {
            "<": "&lt;",
            ">": "&gt;",
            "&": "&amp;",
            '"': "&quot;",
            "'": "&#x27;",
        }

        for char, replacement in replacements.items():
            value = value.replace(char, replacement)

        return value.strip()


class ChildSafetyValidator(BaseValidator):
    """Validator for child safety compliance."""

    MINIMUM_AGE = 1
    MAXIMUM_AGE = 13  # COPPA compliance

    INAPPROPRIATE_WORDS = [
        # Add comprehensive list of inappropriate words
        # This should be loaded from a configuration file in production
    ]

    def validate(self, value: Any) -> bool:
        """Validate value for child safety."""
        if isinstance(value, str):
            return self.validate_content(value)
        elif isinstance(value, int):
            return self.validate_age(value)
        return False

    def sanitize(self, value: Any) -> Any:
        """Sanitize value for child safety."""
        if isinstance(value, str):
            return self.sanitize_string(value)
        return value

    @classmethod
    def validate_age(cls, age: int) -> bool:
        """Validate child age for COPPA compliance."""
        return cls.MINIMUM_AGE <= age <= cls.MAXIMUM_AGE

    @classmethod
    def validate_content(cls, content: str) -> bool:
        """Validate content is child-appropriate."""
        if not content:
            return True

        content_lower = content.lower()

        # Check for inappropriate words
        for word in cls.INAPPROPRIATE_WORDS:
            if word in content_lower:
                return False

        return True

    @classmethod
    def validate_child_name(cls, name: str) -> bool:
        """Validate child name."""
        if not name or not name.strip():
            return False

        # Check basic safety
        if not cls.is_safe_string(name, max_length=50):
            return False

        # Check for inappropriate content in name
        if not cls.validate_content(name):
            return False

        return True
