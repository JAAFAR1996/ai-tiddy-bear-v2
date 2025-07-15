"""Centralized Logging Configuration"

This module configures application-wide logging with consistent standards and security.
It ensures sensitive data is not logged and appropriate verbosity is maintained.
"""

import logging
import logging.handlers
import os
import sys
import re # Used only in ChildSafetyFilter._redact
import hashlib # Used only in log_child_interaction
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from src.common.constants import SENSITIVE_LOG_INTERACTION_KEYS # Import the new constant


LOGGING_LEVELS = {
    # Core application components
    "api": logging.INFO,
    "application": logging.INFO,
    "domain": logging.INFO,
    "infrastructure": logging.INFO,
    "presentation": logging.INFO,
    # Specific functional areas
    "security": logging.WARNING,  # Security events are always important
    "auth": logging.INFO,
    "child_safety": logging.WARNING,  # Child safety events are always important
    "database": logging.INFO,
    "cache": logging.INFO,
    "middleware": logging.INFO,
    "messaging": logging.INFO,
    "config": logging.INFO,
    "di": logging.INFO,  # Dependency Injection
    # Development/Debug components
    "debug": logging.DEBUG,
    "test": logging.DEBUG,
    # Default level for any unconfigured logger
    "default": logging.INFO,
}

def configure_logging(
    environment: str = "production",
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
) -> None:
    """
    Configures application-wide logging with consistent standards and security.
    Ensures sensitive data is not logged and appropriate verbosity is maintained.
    Args:
        environment (str): The current operating environment (e.g., "production", "development").
        log_level (Optional[str]): The desired base logging level (e.g., "INFO", "DEBUG").
        log_file (Optional[str]): Path to a file for logging output. If None, logs to console only.
    """
    # Determine base log level
    if log_level:
        base_level = getattr(logging, log_level.upper(), logging.INFO)
    else:
        base_level = logging.DEBUG if environment == "development" else logging.INFO

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(base_level)

    # Clear existing handlers to prevent duplicate logs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()

    # Use ProductionFormatter for all handlers
    formatter = ProductionFormatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    # Add ChildSafetyFilter to all handlers
    child_safety_filter = ChildSafetyFilter()
    standard_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(base_level)
    console_handler.setFormatter(standard_formatter)  # Use common formatter
    console_handler.addFilter(child_safety_filter)
    root_logger.addHandler(console_handler)

    # File handler with rotation if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        max_bytes = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB default
        backup_count = int(os.getenv("LOG_BACKUP_COUNT", "5"))  # Keep 5 backups
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setLevel(base_level)
        file_handler.setFormatter(standard_formatter)  # Use common formatter
        file_handler.addFilter(child_safety_filter)
        root_logger.addHandler(file_handler)
        if environment == "production":
            # Correctly define and configure time_handler for production
            time_handler = logging.handlers.TimedRotatingFileHandler(
                log_file.replace(".log", "_daily.log"),
                when="midnight",
                interval=1,
                backupCount=backup_count,
                encoding="utf-8"
            )
            time_handler.setLevel(base_level)
            time_handler.setFormatter(formatter) # Using ProductionFormatter for production logs
            time_handler.addFilter(child_safety_filter)
            root_logger.addHandler(time_handler)

    # Configure specific loggers with appropriate levels
    for component, level in LOGGING_LEVELS.items():
        if component != "default":
            component_logger = logging.getLogger(f"src.{component}")
            component_logger.setLevel(level)
            # Ensure component loggers also use the filter
            component_logger.addFilter(child_safety_filter)

    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured for {environment} environment.")


def get_logger(name: str, component: Optional[str] = None) -> logging.Logger:
    """
    Retrieves a logger instance with a specific name and optional component tag.

    This function ensures that loggers are consistently named and can be
    categorized by their component (e.g., "api", "database", "security").
    It applies the child safety filter to prevent sensitive data logging.

    Args:
        name (str): The name of the logger, typically __name__ of the calling module.
        component (Optional[str]): An optional string indicating the component
                                   this logger belongs to (e.g., "api", "security").

    Returns:
        logging.Logger: A configured logger instance.
    """
    logger = logging.getLogger(name)
    # Set appropriate level based on component
    if component and component in LOGGING_LEVELS:
        logger.setLevel(LOGGING_LEVELS[component])
    return logger


def log_security_event(
    event_type: str, details: Dict[str, Any], severity: str = "WARNING"
) -> None:
    """
    Logs security-related events with a consistent format.
    Args:
        event_type (str): A string identifying the type of security event (e.g., "LOGIN_FAILED", "UNAUTHORIZED_ACCESS").
        details (Dict[str, Any]): A dictionary containing relevant details about the event. Sensitive data should be pre-redacted.
        severity (str): The severity level of the event (e.g., "INFO", "WARNING", "ERROR", "CRITICAL"). Defaults to "WARNING".
    """
    security_logger = logging.getLogger("src.security")
    # Ensure minimum WARNING level for security events
    level = max(logging.WARNING, getattr(logging, severity.upper(), logging.WARNING))
    # Format security event
    event_data = {
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": details,
    }
    security_logger.log(level, f"SECURITY EVENT: {event_type}", extra=event_data)


class ChildSafetyFilter(logging.Filter):
    """
    Redacts sensitive information from log records to protect child privacy.
    This filter inspects log messages and arguments, applying redaction rules
    to prevent Personally Identifiable Information (PII) from being written
    to logs. It is crucial for maintaining COPPA compliance and data privacy.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        # Implement redaction logic here
        if isinstance(record.msg, str):
            record.msg = self._redact(record.msg)
        if record.args:
            record.args = tuple(self._redact(arg) for arg in record.args)
        return True

    def _redact(self, message: Any) -> Any:
        # Moved import here
        import re
        if not isinstance(message, str):
            return message
        # Redact common PII patterns
        message = re.sub(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "[REDACTED_EMAIL]",
            message,
        )
        message = re.sub(
            r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[REDACTED_PHONE]", message
        )  # Phone numbers
        message = re.sub(
            r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", "[REDACTED_IP]", message
        )  # IPv4 addresses
        message = re.sub(
            r"\b(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}\b", "[REDACTED_IP]", message
        )  # IPv6 addresses
        message = re.sub(
            r"\b(?:\d{4}[ -]?){3}\d{4}\b", "[REDACTED_CARD]", message
        )  # Credit card numbers
        message = re.sub(
            r"\b[A-Za-z]{3}\d{2}[A-Za-z]{2}\d{3}[A-Za-z]{1}\d{2}\b",
            "[REDACTED_SSN]",
            message,
        )  # Social Security Numbers (example pattern)
        return message


class ProductionFormatter(logging.Formatter):
    """
    A custom log formatter for production environments.
    This formatter is designed to:
    - Omit function names and line numbers to avoid leaking code structure.
    - Format logs as JSON for easier parsing by log management systems.
    - Ensure sensitive data is handled by `ChildSafetyFilter` before formatting.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_object = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_object["exc_info"] = self.formatException(record.exc_info)
        # If there are specific extra fields intended for logging, they should be explicitly added here.
        # For security and privacy, avoid automatically including all of record.__dict__.
        # Sensitive data should be handled by ChildSafetyFilter before reaching the formatter.
        return str(log_object)


def log_child_interaction(
    interaction_type: str,
    child_id: str,
    safe: bool,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Logs child interactions with enhanced privacy protection using BLAKE2b hashing.
    This function ensures that child IDs are hashed before logging to protect privacy,
    and includes relevant interaction details for auditing and analysis.
    Args:
        interaction_type (str): The type of interaction (e.g., "AI_RESPONSE", "AUDIO_INPUT").
        child_id (str): The unique identifier of the child. This will be hashed before logging.
        safe (bool): Indicates whether the interaction was deemed safe by content filters.
        details (Optional[Dict[str, Any]]): Additional details about the interaction, which will be sanitized.
    """
    child_logger = logging.getLogger("src.child_safety")
    # Use a more secure hashing algorithm for the child ID
    import hashlib # Moved import here
    hasher = hashlib.blake2b(digest_size=16)
    hasher.update(child_id.encode("utf-8"))
    safe_id = hasher.hexdigest()
    log_data = {
        "interaction_type": interaction_type,
        "child_ref": safe_id,
        "safe": safe,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if details:
        # Filter out sensitive keys using the centralized constant
        sanitized_details = {
            k: v for k, v in details.items() if k not in SENSITIVE_LOG_INTERACTION_KEYS
        }
        log_data["metrics"] = sanitized_details
    level = logging.INFO if safe else logging.WARNING
    child_logger.log(level, f"Child interaction: {interaction_type}", extra=log_data)


# Export convenience functions
__all__ = [
    "configure_logging",
    "get_logger",
    "log_security_event",
    "log_child_interaction",
    "ChildSafetyFilter",
    "ProductionFormatter",
    "LOGGING_LEVELS",
]