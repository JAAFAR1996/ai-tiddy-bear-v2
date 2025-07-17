"""Secure Logging Utility - Prevents sensitive data from being logged."""

import logging
import re
from typing import Any

from src.infrastructure.security.log_sanitization_config import (
    LogSanitizationConfig,
    get_default_log_sanitization_config,
)


class SecureLogger:
    """Logger wrapper that automatically sanitizes sensitive information."""

    def __init__(
        self,
        logger: logging.Logger,
        config: LogSanitizationConfig | None = None,
    ):
        self.logger = logger
        self.config = config or get_default_log_sanitization_config()

        # Compile regex patterns for better performance
        self.redact_regex = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.config.redact_patterns
        ]
        self.mask_regex = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.config.mask_patterns
        ]

    def _sanitize_value(self, key: str, value: Any) -> str:
        """Sanitize a single value based on its key and content."""
        if value is None:
            return "None"

        key_lower = key.lower()
        str_value = str(value)

        # Check if field is forbidden
        if key_lower in [field.lower() for field in self.config.forbidden_fields]:
            return "[REDACTED]"

        # Check for redaction patterns
        for regex in self.redact_regex:
            if regex.search(key_lower):
                return "[REDACTED]"

        # Check for masking patterns
        for regex in self.mask_regex:
            if regex.search(key_lower):
                return self._mask_value(str_value)

        # Truncate long values
        if len(str_value) > self.config.max_value_length:
            return str_value[: self.config.max_value_length] + "...[TRUNCATED]"

        # Check for patterns in the value itself that might be sensitive
        for regex in self.redact_regex:
            if regex.search(str_value):
                return "[CONTAINS_SENSITIVE_DATA]"

        return str_value

    def _mask_value(self, value: str) -> str:
        """Partially mask a value (show first and last few characters)."""
        if len(value) <= 6:
            return "*" * len(value)

        if len(value) <= 10:
            return value[:1] + "*" * (len(value) - 2) + value[-1:]

        return value[:3] + "*" * (len(value) - 6) + value[-3:]

    def _sanitize_dict(
        self,
        data: dict[str, Any],
        max_depth: int = 3,
    ) -> dict[str, Any]:
        """Recursively sanitize a dictionary."""
        if max_depth <= 0:
            return {"[MAX_DEPTH_REACHED]": "Data structure too deep"}

        sanitized = {}
        for key, value in data.items():
            if isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value, max_depth - 1)
            elif isinstance(value, list | tuple):
                sanitized[key] = self._sanitize_list(value, max_depth - 1)
            else:
                sanitized[key] = self._sanitize_value(key, value)

        return sanitized

    def _sanitize_list(self, data: list[Any], max_depth: int = 3) -> list[Any]:
        """Recursively sanitize a list."""
        if max_depth <= 0:
            return ["[MAX_DEPTH_REACHED]"]

        sanitized = []
        for i, item in enumerate(data):
            if isinstance(item, dict):
                sanitized.append(self._sanitize_dict(item, max_depth - 1))
            elif isinstance(item, list | tuple):
                sanitized.append(self._sanitize_list(item, max_depth - 1))
            else:
                sanitized.append(self._sanitize_value(f"item_{i}", item))

        return sanitized

    def _sanitize_message(self, message: str) -> str:
        """Sanitize a log message for sensitive patterns."""
        # Simple pattern matching for common sensitive data in messages
        sensitive_patterns = [
            (r"password[=:\s]+\S+", "password=[REDACTED]"),
            (r"token[=:\s]+\S+", "token=[REDACTED]"),
            (r"api_key[=:\s]+\S+", "api_key=[REDACTED]"),
            (r"secret[=:\s]+\S+", "secret=[REDACTED]"),
            (
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "[EMAIL_REDACTED]",
            ),
            (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN_REDACTED]"),
            (r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "[CARD_REDACTED]"),
        ]

        sanitized_message = message
        for pattern, replacement in sensitive_patterns:
            sanitized_message = re.sub(
                pattern,
                replacement,
                sanitized_message,
                flags=re.IGNORECASE,
            )

        return sanitized_message

    def _prepare_log_data(self, message: str, *args, **kwargs) -> tuple:
        """Prepare log data by sanitizing message and arguments."""
        sanitized_message = self._sanitize_message(message)

        sanitized_args = []
        for arg in args:
            if isinstance(arg, dict):
                sanitized_args.append(self._sanitize_dict(arg))
            elif isinstance(arg, list | tuple):
                sanitized_args.append(self._sanitize_list(arg))
            else:
                sanitized_args.append(self._sanitize_value("arg", arg))

        sanitized_kwargs = {}
        for key, value in kwargs.items():
            if key in ["exc_info", "stack_info", "stacklevel"]:
                # Preserve logging-specific kwargs
                sanitized_kwargs[key] = value
            elif isinstance(value, dict):
                sanitized_kwargs[key] = self._sanitize_dict(value)
            elif isinstance(value, list | tuple):
                sanitized_kwargs[key] = self._sanitize_list(value)
            else:
                sanitized_kwargs[key] = self._sanitize_value(key, value)

        return sanitized_message, tuple(sanitized_args), sanitized_kwargs

    def debug(self, message: str, *args, **kwargs):
        """Log debug message with sanitization."""
        msg, sanitized_args, sanitized_kwargs = self._prepare_log_data(
            message,
            *args,
            **kwargs,
        )
        self.logger.debug(msg, *sanitized_args, **sanitized_kwargs)

    def info(self, message: str, *args, **kwargs):
        """Log info message with sanitization."""
        msg, sanitized_args, sanitized_kwargs = self._prepare_log_data(
            message,
            *args,
            **kwargs,
        )
        self.logger.info(msg, *sanitized_args, **sanitized_kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log warning message with sanitization."""
        msg, sanitized_args, sanitized_kwargs = self._prepare_log_data(
            message,
            *args,
            **kwargs,
        )
        self.logger.warning(msg, *sanitized_args, **sanitized_kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log error message with sanitization."""
        msg, sanitized_args, sanitized_kwargs = self._prepare_log_data(
            message,
            *args,
            **kwargs,
        )
        self.logger.error(msg, *sanitized_args, **sanitized_kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Log critical message with sanitization."""
        msg, sanitized_args, sanitized_kwargs = self._prepare_log_data(
            message,
            *args,
            **kwargs,
        )
        self.logger.critical(msg, *sanitized_args, **sanitized_kwargs)

    def log_child_interaction(
        self,
        child_id: str,
        interaction_type: str,
        success: bool,
        **metadata,
    ):
        """Specialized logging for child interactions with COPPA compliance."""
        # Only log non-sensitive metadata
        safe_metadata = {
            "interaction_type": interaction_type,
            "success": success,
            "timestamp": metadata.get("timestamp"),
            "safety_score": metadata.get("safety_score"),
            "content_filtered": metadata.get("content_filtered", False),
        }

        # Mask child ID for privacy
        masked_child_id = self._mask_value(child_id)
        self.info(
            f"Child interaction logged: child={masked_child_id}, type={interaction_type}, success={success}",
            extra={"child_interaction": safe_metadata},
        )

    def log_security_event(self, event_type: str, severity: str, **details):
        """Log security events with appropriate sanitization."""
        sanitized_details = self._sanitize_dict(details)
        self.warning(
            f"Security event: {event_type} [severity: {severity}]",
            extra={"security_event": sanitized_details},
        )


def get_secure_logger(
    name: str,
    config: LogSanitizationConfig | None = None,
) -> SecureLogger:
    """Get a secure logger instance."""
    from src.infrastructure.logging_config import get_logger

    logger = get_logger(__name__, component="security")
    return SecureLogger(logger, config)


# Convenience function for common use cases
def create_child_safe_logger(name: str) -> SecureLogger:
    """Create a logger specifically configured for child-safe logging."""
    config = LogSanitizationConfig(
        redact_patterns=[
            r"password",
            r"secret",
            r"token",
            r"api_key",
            r"private_key",
            r"auth",
            r"credential",
            r"session",
            r"cookie",
            r"bearer",
            r"personal",
            r"contact",
            r"address",
            r"phone",
        ],
        mask_patterns=[
            r"child_id",
            r"parent_id",
            r"user_id",
            r"email",
            r"name",
        ],
        forbidden_fields=[
            "password",
            "secret_key",
            "api_key",
            "private_key",
            "token",
            "session_id",
            "auth_header",
            "bearer_token",
            "child_name",
            "parent_name",
            "child_personal_info",
            "parent_contact_info",
            "voice_data",
            "conversation_content",
        ],
        max_value_length=50,  # Shorter for child safety
    )
    return get_secure_logger(name, config)
