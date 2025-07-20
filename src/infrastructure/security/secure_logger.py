"""Unified Secure Logging Utility
Combines COPPA compliance features with advanced sanitization
Replaces both secure_logger.py and secure_logging.py
"""

import hashlib
import logging
import re
from typing import Any, Callable

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.log_sanitization_config import (
    LogSanitizationConfig,
    get_default_log_sanitization_config,
)

try:
    from ..config.coppa_config import requires_coppa_audit_logging
except ImportError:
    # Fallback if COPPA config not available
    def requires_coppa_audit_logging() -> bool:
        return True


class SecureLogger:
    """Unified secure logger with COPPA compliance and advanced sanitization."""

    def __init__(
        self,
        name: str,
        logger: logging.Logger = None,
        config: LogSanitizationConfig = None,
    ):
        self.name = name
        self.logger = logger or get_logger(name, component="security")
        self.config = config or get_default_log_sanitization_config()
        
        # COPPA-specific settings
        self._salt = "teddy_bear_secure_log_2025"
        
        # Compile regex patterns for performance
        self.redact_regex = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.config.redact_patterns
        ]
        self.mask_regex = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.config.mask_patterns
        ]

    # =====================================
    # COPPA-Specific ID Sanitization
    # =====================================
    
    def _sanitize_child_id(self, child_id: str) -> str:
        """Convert child_id to a safe hash for COPPA compliance."""
        if not child_id:
            return "[EMPTY_CHILD_ID]"
        
        hash_obj = hashlib.sha256(f"{self._salt}_{child_id}".encode())
        short_hash = hash_obj.hexdigest()[:8]
        return f"child_{short_hash}"

    def _sanitize_parent_id(self, parent_id: str) -> str:
        """Convert parent_id to a safe hash for logging."""
        if not parent_id:
            return "[EMPTY_PARENT_ID]"
        
        hash_obj = hashlib.sha256(f"{self._salt}_{parent_id}".encode())
        short_hash = hash_obj.hexdigest()[:8]
        return f"parent_{short_hash}"

    def _sanitize_email(self, email: str) -> str:
        """Mask email address for logging."""
        if not email or "@" not in email:
            return "[INVALID_EMAIL]"
        
        parts = email.split("@")
        masked_local = "***" if len(parts[0]) <= 2 else parts[0][:2] + "***"
        return f"{masked_local}@{parts[1]}"

    def _sanitize_phone(self, phone: str) -> str:
        """Mask phone number for logging."""
        if not phone:
            return "[EMPTY_PHONE]"
        
        digits_only = re.sub(r"\D", "", phone)
        if len(digits_only) < 5:
            return "***"
        if len(digits_only) >= 10:
            return digits_only[:3] + "***" + digits_only[-2:]
        return digits_only[:2] + "***"

    # =====================================
    # Advanced Value Sanitization
    # =====================================
    
    def _sanitize_value(self, key: str, value: Any) -> str:
        """Sanitize a single value based on its key and content."""
        if value is None:
            return "None"

        key_lower = key.lower()
        str_value = str(value)

        # COPPA-specific handling
        if key_lower == "child_id":
            return self._sanitize_child_id(str_value)
        elif key_lower == "parent_id":
            return self._sanitize_parent_id(str_value)
        elif key_lower == "email":
            return self._sanitize_email(str_value)
        elif key_lower == "phone":
            return self._sanitize_phone(str_value)

        # Check if field is forbidden
        if key_lower in [field.lower() for field in self.config.forbidden_fields]:
            return "[REDACTED]"

        # Check for redaction patterns
        for regex in self.redact_regex:
            if regex.search(key_lower) or regex.search(str_value):
                return "[REDACTED]"

        # Check for masking patterns
        for regex in self.mask_regex:
            if regex.search(key_lower):
                return self._mask_value(str_value)

        # Truncate long values
        if len(str_value) > self.config.max_value_length:
            return str_value[:self.config.max_value_length] + "...[TRUNCATED]"

        return str_value

    def _mask_value(self, value: str) -> str:
        """Partially mask a value (show first and last few characters)."""
        if len(value) <= 6:
            return "*" * len(value)
        if len(value) <= 10:
            return value[:1] + "*" * (len(value) - 2) + value[-1:]
        return value[:3] + "*" * (len(value) - 6) + value[-3:]

    def _sanitize_dict(self, data: dict[str, Any], max_depth: int = 3) -> dict[str, Any]:
        """Recursively sanitize a dictionary."""
        if max_depth <= 0:
            return {"[MAX_DEPTH_REACHED]": "Data structure too deep"}

        sanitized = {}
        for key, value in data.items():
            if isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value, max_depth - 1)
            elif isinstance(value, (list, tuple)):
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
            elif isinstance(item, (list, tuple)):
                sanitized.append(self._sanitize_list(item, max_depth - 1))
            else:
                sanitized.append(self._sanitize_value(f"item_{i}", item))
        return sanitized

    def _sanitize_message(self, message: str, **kwargs) -> str:
        """Sanitize a log message by replacing sensitive data."""
        sanitized = message

        # Handle kwargs that might contain sensitive data
        for key, value in kwargs.items():
            if key == "child_id" and value:
                sanitized_value = self._sanitize_child_id(str(value))
                kwargs[key] = sanitized_value
            elif key == "parent_id" and value:
                sanitized_value = self._sanitize_parent_id(str(value))
                kwargs[key] = sanitized_value
            elif key == "email" and value:
                sanitized_value = self._sanitize_email(str(value))
                kwargs[key] = sanitized_value
            elif key == "phone" and value:
                sanitized_value = self._sanitize_phone(str(value))
                kwargs[key] = sanitized_value

        # Pattern-based sanitization for embedded sensitive data
        patterns = {
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b": lambda m: self._sanitize_email(m.group(0)),
            r"\+?[\d\s\-\(\)]{10,}": lambda m: self._sanitize_phone(m.group(0)),
            r"\bchild_[a-zA-Z0-9\-_]{8,}": lambda m: self._sanitize_child_id(m.group(0)),
            r"\bparent_[a-zA-Z0-9\-_]{8,}": lambda m: self._sanitize_parent_id(m.group(0)),
            r"password[=:\s]+\S+": lambda m: "password=[REDACTED]",
            r"token[=:\s]+\S+": lambda m: "token=[REDACTED]",
            r"api_key[=:\s]+\S+": lambda m: "api_key=[REDACTED]",
            r"secret[=:\s]+\S+": lambda m: "secret=[REDACTED]",
        }

        for pattern, replacer in patterns.items():
            sanitized = re.sub(pattern, replacer, sanitized)

        return sanitized

    def _prepare_log_data(self, message: str, *args, **kwargs) -> tuple:
        """Prepare log data by sanitizing message and arguments."""
        sanitized_message = self._sanitize_message(message, **kwargs)

        sanitized_args = []
        for arg in args:
            if isinstance(arg, dict):
                sanitized_args.append(self._sanitize_dict(arg))
            elif isinstance(arg, (list, tuple)):
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
            elif isinstance(value, (list, tuple)):
                sanitized_kwargs[key] = self._sanitize_list(value)
            else:
                sanitized_kwargs[key] = self._sanitize_value(key, value)

        return sanitized_message, tuple(sanitized_args), sanitized_kwargs

    # =====================================
    # Standard Logging Methods
    # =====================================
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug message with sanitization."""
        msg, sanitized_args, sanitized_kwargs = self._prepare_log_data(message, *args, **kwargs)
        self.logger.debug(msg, *sanitized_args, **sanitized_kwargs)

    def info(self, message: str, *args, **kwargs):
        """Log info message with sanitization."""
        msg, sanitized_args, sanitized_kwargs = self._prepare_log_data(message, *args, **kwargs)
        self.logger.info(msg, *sanitized_args, **sanitized_kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log warning message with sanitization."""
        msg, sanitized_args, sanitized_kwargs = self._prepare_log_data(message, *args, **kwargs)
        self.logger.warning(msg, *sanitized_args, **sanitized_kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log error message with sanitization."""
        msg, sanitized_args, sanitized_kwargs = self._prepare_log_data(message, *args, **kwargs)
        self.logger.error(msg, *sanitized_args, **sanitized_kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Log critical message with sanitization."""
        msg, sanitized_args, sanitized_kwargs = self._prepare_log_data(message, *args, **kwargs)
        self.logger.critical(msg, *sanitized_args, **sanitized_kwargs)

    # =====================================
    # Specialized COPPA Logging Methods
    # =====================================
    
    def log_child_activity(self, child_id: str, activity: str, details: dict = None) -> None:
        """Log child activity with automatic ID sanitization."""
        safe_child_id = self._sanitize_child_id(child_id)
        if details:
            sanitized_details = self._sanitize_dict(details)
            self.info(f"Child activity: {safe_child_id} - {activity}", extra={"details": sanitized_details})
        else:
            self.info(f"Child activity: {safe_child_id} - {activity}")

    def log_parent_action(self, parent_id: str, action: str, child_id: str = None) -> None:
        """Log parent action with automatic ID sanitization."""
        safe_parent_id = self._sanitize_parent_id(parent_id)
        if child_id:
            safe_child_id = self._sanitize_child_id(child_id)
            self.info(f"Parent action: {safe_parent_id} - {action} - child: {safe_child_id}")
        else:
            self.info(f"Parent action: {safe_parent_id} - {action}")

    def log_safety_event(self, child_id: str, event_type: str, severity: str, details: str = None) -> None:
        """Log safety event with automatic sanitization."""
        safe_child_id = self._sanitize_child_id(child_id)
        if details:
            self.warning(f"Safety event: {safe_child_id} - {event_type} ({severity}) - {details}")
        else:
            self.warning(f"Safety event: {safe_child_id} - {event_type} ({severity})")

    def log_coppa_event(self, child_id: str, event_type: str, consent_status: str) -> None:
        """Log COPPA compliance event with sanitization."""
        if not requires_coppa_audit_logging():
            return  # Skip when COPPA disabled
        
        safe_child_id = self._sanitize_child_id(child_id)
        self.info(f"COPPA event: {safe_child_id} - {event_type} - consent: {consent_status}")

    def log_child_interaction(self, child_id: str, interaction_type: str, success: bool, **metadata):
        """Specialized logging for child interactions with COPPA compliance."""
        safe_metadata = {
            "interaction_type": interaction_type,
            "success": success,
            "timestamp": metadata.get("timestamp"),
            "safety_score": metadata.get("safety_score"),
            "content_filtered": metadata.get("content_filtered", False),
        }

        masked_child_id = self._sanitize_child_id(child_id)
        self.info(
            f"Child interaction: {masked_child_id}, type={interaction_type}, success={success}",
            extra={"child_interaction": safe_metadata}
        )

    def log_security_event(self, event_type: str, severity: str, **details):
        """Log security events with appropriate sanitization."""
        sanitized_details = self._sanitize_dict(details)
        self.warning(
            f"Security event: {event_type} [severity: {severity}]",
            extra={"security_event": sanitized_details}
        )


# =====================================
# Global Instance Management
# =====================================

_secure_loggers: dict[str, SecureLogger] = {}


def get_secure_logger(name: str, config: LogSanitizationConfig = None) -> SecureLogger:
    """Get a secure logger instance for the given name."""
    if name not in _secure_loggers:
        _secure_loggers[name] = SecureLogger(name, config=config)
    return _secure_loggers[name]


def create_child_safe_logger(name: str) -> SecureLogger:
    """Create a logger specifically configured for child-safe logging."""
    config = LogSanitizationConfig(
        redact_patterns=[
            r"password", r"secret", r"token", r"api_key", r"private_key",
            r"auth", r"credential", r"session", r"cookie", r"bearer",
            r"personal", r"contact", r"address", r"phone"
        ],
        mask_patterns=[
            r"child_id", r"parent_id", r"user_id", r"email", r"name"
        ],
        forbidden_fields=[
            "password", "secret_key", "api_key", "private_key", "token",
            "session_id", "auth_header", "bearer_token", "child_name",
            "parent_name", "child_personal_info", "parent_contact_info",
            "voice_data", "conversation_content"
        ],
        max_value_length=50,  # Shorter for child safety
    )
    return SecureLogger(name, config=config)


# =====================================
# Convenience Functions
# =====================================

def log_child_activity(child_id: str, activity: str, details: dict = None) -> None:
    """Quick child activity logging."""
    logger = get_secure_logger("child_activity")
    logger.log_child_activity(child_id, activity, details)


def log_parent_action(parent_id: str, action: str, child_id: str = None) -> None:
    """Quick parent action logging."""
    logger = get_secure_logger("parent_activity")
    logger.log_parent_action(parent_id, action, child_id)


def log_safety_event(child_id: str, event_type: str, severity: str, details: str = None) -> None:
    """Quick safety event logging."""
    logger = get_secure_logger("child_safety")
    logger.log_safety_event(child_id, event_type, severity, details)


def log_coppa_event(child_id: str, event_type: str, consent_status: str) -> None:
    """Quick COPPA event logging."""
    logger = get_secure_logger("coppa_compliance")
    logger.log_coppa_event(child_id, event_type, consent_status)


# =====================================
# Decorators
# =====================================

def secure_log_call(func: Callable) -> Callable:
    """Decorator to add secure logging to function calls."""
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = get_secure_logger(func.__module__)

        # Log function entry (sanitized)
        sanitized_args = []
        for arg in args:
            if isinstance(arg, str) and ("child_" in arg or "parent_" in arg):
                if "child_" in arg:
                    sanitized_args.append(logger._sanitize_child_id(arg))
                else:
                    sanitized_args.append(logger._sanitize_parent_id(arg))
            else:
                sanitized_args.append(str(arg)[:50])  # Truncate long args

        logger.debug(f"Function call: {func.__name__}({', '.join(sanitized_args)})")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"Function success: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Function error: {func.__name__} - {type(e).__name__}")
            raise

    return wrapper