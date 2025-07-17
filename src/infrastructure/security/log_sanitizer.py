"""Log Sanitization Service for COPPA Compliance

Provides secure logging functions that automatically sanitize sensitive data
before writing to logs, ensuring COPPA compliance and child privacy protection.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Union, List
import hashlib
from src.infrastructure.logging_config import get_logger
import re

logger = get_logger(__name__, component="security")

class SensitiveDataType(Enum):
    """Types of sensitive data that must be sanitized."""
    CHILD_ID = "child_id"
    PARENT_ID = "parent_id"
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    ADDRESS = "address"
    NAME = "name"
    IP_ADDRESS = "ip_address"

@dataclass
class SanitizationRule:
    """Rule for sanitizing specific data types."""
    pattern: str
    replacement: str
    data_type: SensitiveDataType
    enabled: bool = True

class LogSanitizer:
    """
    COPPA-compliant log sanitizer for child safety applications.
    Automatically detects and sanitizes sensitive data in log messages
    before they are written to log files, ensuring compliance with privacy regulations.
    """

    def __init__(self) -> None:
        """Initialize sanitizer with default rules."""
        self._sanitization_rules = self._create_default_rules()
        self._hash_cache: Dict[str, str] = {}

    def _create_default_rules(self) -> List[SanitizationRule]:
        """Create default sanitization rules for common sensitive data."""
        return [
            # Child and Parent IDs
            SanitizationRule(
                pattern=r'\bchild[_\s]+(?:id[_\s]*[:=]?\s*)?([a-f0-9\-]{8,})',
                replacement=lambda m: f"child_id: {self._hash_id(m.group(1))}",
                data_type=SensitiveDataType.CHILD_ID
            ),
            SanitizationRule(
                pattern=r'\bparent[_\s]+(?:id[_\s]*[:=]?\s*)?([a-f0-9\-]{8,})',
                replacement=lambda m: f"parent_id: {self._hash_id(m.group(1))}",
                data_type=SensitiveDataType.PARENT_ID
            ),
            # Email
            SanitizationRule(
                pattern=r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                replacement="[REDACTED_EMAIL]",
                data_type=SensitiveDataType.EMAIL
            ),
            # Phone
            SanitizationRule(
                pattern=r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
                replacement="[REDACTED_PHONE]",
                data_type=SensitiveDataType.PHONE
            ),
            # IP Address
            SanitizationRule(
                pattern=r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
                replacement="[REDACTED_IP]",
                data_type=SensitiveDataType.IP_ADDRESS
            ),
        ]

    def _hash_id(self, id_value: str) -> str:
        """Create a consistent, truncated hash for an ID."""
        if id_value in self._hash_cache:
            return self._hash_cache[id_value]
        hashed = hashlib.sha256(id_value.encode()).hexdigest()[:12]
        self._hash_cache[id_value] = hashed
        return hashed

    def sanitize(self, message: str) -> str:
        """Sanitize a log message by applying all enabled rules."""
        sanitized_message = message
        for rule in self._sanitization_rules:
            if rule.enabled:
                if callable(rule.replacement):
                    sanitized_message = re.sub(rule.pattern, rule.replacement, sanitized_message)
                else:
                    sanitized_message = re.sub(rule.pattern, rule.replacement, sanitized_message)
        return sanitized_message

    def sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize a dictionary."""
        sanitized_dict = {}
        for key, value in data.items():
            if isinstance(value, dict):
                sanitized_dict[key] = self.sanitize_dict(value)
            elif isinstance(value, str):
                sanitized_dict[key] = self.sanitize(value)
            else:
                sanitized_dict[key] = value
        return sanitized_dict