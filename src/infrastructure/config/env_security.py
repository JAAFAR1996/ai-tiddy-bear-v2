"""
Provides secure management of environment variables with validation and protection.

This module defines classes and utilities for handling sensitive environment
variables, including their validation, logging, and masking. It ensures that
confidential information is not exposed and that environment configurations
adhere to security best practices.
"""

import hashlib
import logging
import os
import re
from collections import OrderedDict
from datetime import datetime
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, List, Optional, Set

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="config")


class EnvVar(str, Enum):
    """Enumeration of recognized environment variables."""

    SECRET_KEY = "SECRET_KEY"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    DATABASE_URL = "DATABASE_URL"
    ENVIRONMENT = "ENVIRONMENT"
    DEBUG = "DEBUG"
    CONTENT_MODERATION_ENABLED = "CONTENT_MODERATION_ENABLED"
    COPPA_COMPLIANCE_MODE = "COPPA_COMPLIANCE_MODE"
    CHILD_SAFETY_ENABLED = "CHILD_SAFETY_ENABLED"
    OPENAI_API_KEY = "OPENAI_API_KEY"
    REDIS_URL = "REDIS_URL"
    SECURE_COOKIES = "SECURE_COOKIES"
    FORCE_HTTPS = "FORCE_HTTPS"
    WORKERS = "WORKERS"
    PORT = "PORT"
    SSL_KEYFILE = "SSL_KEYFILE"
    SSL_CERTFILE = "SSL_CERTFILE"
    SSL_OFFLOADED = "SSL_OFFLOADED"
    STATIC_FILES_DIR = "STATIC_FILES_DIR"
    LOG_MAX_BYTES = "LOG_MAX_BYTES"
    LOG_BACKUP_COUNT = "LOG_BACKUP_COUNT"
    # Add other environment variables as needed


class EnvValue(str, Enum):
    """Enumeration of common environment variable values."""

    TRUE = "True"
    FALSE = "False"
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    # Add other specific values as needed


class EnvPattern(str, Enum):
    """Enumeration of regex patterns for sensitive environment variables."""

    KEY = r".*_KEY$"
    SECRET = r".*_SECRET$"
    PASSWORD = r".*_PASSWORD$"
    TOKEN = r".*_TOKEN$"
    CREDENTIALS = r".*_CREDENTIALS$"
    JWT = r"^JWT_.*"
    DATABASE_URL = r"^DATABASE_URL$"
    REDIS_URL = r"^REDIS_URL$"
    OPENAI = r"^OPENAI_.*"
    AWS = r"^AWS_.*"
    STRIPE = r"^STRIPE_.*"
    SENDGRID = r"^SENDGRID_.*"
    TWILIO = r"^TWILIO_.*"
    # Add other sensitive patterns as needed

    class EnvDebugVariant(str, Enum):
    """Enumeration of common debug-related environment variable names."""

    DEBUG = EnvVar.DEBUG.value
    FLASK_DEBUG = "FLASK_DEBUG"
    DJANGO_DEBUG = "DJANGO_DEBUG"
    FASTAPI_DEBUG = "FASTAPI_DEBUG"
    STARLETTE_DEBUG = "STARLETTE_DEBUG"
    # Add other debug variants as needed


class EnvDatabaseType(str, Enum):
    """Enumeration of common database connection string prefixes."""

    POSTGRESQL = "postgresql://"
    # Add other database types as needed


# Sensitive environment variable patterns (regex)
SENSITIVE_PATTERNS: List[re.Pattern] = [
    re.compile(pattern, re.IGNORECASE) for pattern in EnvPattern
]


class SecureEnvironmentManager:
    """Secure management of environment variables with validation and protection."""

    def __init__(self) -> None:
        """Initializes the SecureEnvironmentManager."""
        self._loaded_env_vars: Dict[str, str] = OrderedDict()
        self._sensitive_env_vars: Set[str] = set()
        self.errors: List[str] = []  # Initialize errors list
        self._load_environment()

    def _load_environment(self) -> None:
        """
        Loads environment variables and identifies sensitive ones.
        """
        for key, value in os.environ.items():
            self._loaded_env_vars[key] = value
            if self._is_sensitive(key):
                self._sensitive_env_vars.add(key)

    def _is_sensitive(self, key: str) -> bool:
        """
        Checks if an environment variable key matches any sensitive patterns.

        Args:
            key: The environment variable key.

        Returns:
            True if the key is sensitive, False otherwise.
        """
        for pattern in SENSITIVE_PATTERNS:
            if pattern.match(key):
                return True
        return False

    def get_env_var(self, key: str,
                    default: Optional[str] = None) -> Optional[str]:
        """
        Retrieves an environment variable's value.

        Args:
            key: The environment variable key.
            default: The default value to return if the key is not found.

        Returns:
            The value of the environment variable, or the default value.
        """
        value = self._loaded_env_vars.get(key, default)
        if key in self._sensitive_env_vars:
            logger.debug(f"Accessing sensitive environment variable: {key}")
        return value

    def get_masked_env_vars(self) -> Dict[str, str]:
        """
        Returns a dictionary of all environment variables with sensitive ones masked.

        Returns:
            A dictionary of environment variables with sensitive values replaced by asterisks.
        """
        masked_vars = {}
        for key, value in self._loaded_env_vars.items():
            if key in self._sensitive_env_vars:
                masked_vars[key] = "********"
            else:
                masked_vars[key] = value
        return masked_vars

    def validate_required_env_vars(self, required_vars: List[EnvVar]) -> None:
        """
        Validates that all required environment variables are set.

        Args:
            required_vars: A list of EnvVar enums representing required variables.

        Raises:
            ValueError: If any required environment variable is missing.
        """
        missing_vars = [
            var.value for var in required_vars if var.value not in self._loaded_env_vars
        ]
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {missing_vars}")

    def hash_sensitive_value(self, value: str) -> str:
        """
        Hashes a sensitive string value using SHA256.

        Args:
            value: The string value to hash.

        Returns:
            The SHA256 hash of the value.
        """
        return hashlib.sha256(value.encode()).hexdigest()

    @lru_cache(maxsize=1)
    def get_instance(self) -> "SecureEnvironmentManager":
        """
        Returns a singleton instance of SecureEnvironmentManager.

        Returns:
            The singleton instance of SecureEnvironmentManager.
        """
        return self
