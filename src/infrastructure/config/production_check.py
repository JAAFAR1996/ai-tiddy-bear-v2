"""
Provides critical safety checks and enforces production environment settings.

This module ensures that the application adheres to strict security and
compliance standards when running in a production environment. It forces
certain environment variables to secure values, logs potential security
violations, and performs validations to prevent misconfigurations that
could compromise child safety or data integrity.
"""

import logging
import os
import sys
from typing import List, Optional

from src.infrastructure.config.env_security import SecureEnvironmentManager
from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.main_security_service import (
    MainSecurityService,
)  # Import the new security service
from src.infrastructure.di.container import container
from src.domain.exceptions.base import (
    StartupValidationException,
)  # Import custom exception

logger = get_logger(__name__, component="config")

_env_manager = SecureEnvironmentManager()


def env_get(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Retrieves an environment variable's value using the secure environment manager.

    Args:
        key: The environment variable key.
        default: The default value to return if the key is not found.

    Returns:
        The value of the environment variable, or the default value.
    """
    return _env_manager.get_env_var(key, default)


def env_set_secure(key: str, value: str) -> None:
    """
    Sets an environment variable securely.

    Args:
        key: The environment variable key.
        value: The value to set.
    """
    os.environ[key] = value


# Removed validate_production_environment - now part of MainSecurityService
# def validate_production_environment() -> List[str]:
#     """
#     Validates production environment security settings.
#
#     Returns:
#         A list of error messages if any validation fails.
#     """
#     # This function would ideally be part of SecureEnvironmentManager
#     # For now, it's a placeholder.
#     errors = []
#     if env_get("DEBUG", "True").lower() == "true":
#         errors.append("DEBUG mode is enabled in production.")
#     if env_get("COPPA_COMPLIANCE_MODE", "False").lower() == "false":
#         errors.append("COPPA_COMPLIANCE_MODE is disabled in production.")
#     return errors


def enforce_production_safety() -> None:
    """
    Enforces production safety settings regardless of configuration.

    This function has side effects and will exit if validation fails in production.
    """
    environment = env_get("ENVIRONMENT", "development").lower()
    if environment == "production":
        # Force critical security settings
        env_set_secure("DEBUG", "False")
        env_set_secure("CONTENT_MODERATION_ENABLED", "True")
        env_set_secure("COPPA_COMPLIANCE_MODE", "True")
        env_set_secure("CHILD_SAFETY_ENABLED", "True")
        env_set_secure("SECURE_COOKIES", "True")
        env_set_secure("FORCE_HTTPS", "True")

        logger.warning(
            "Production environment detected - enforcing security settings:")
        logger.warning("  - DEBUG: False (forced)")
        logger.warning("  - CONTENT_MODERATION_ENABLED: True (forced)")
        logger.warning("  - COPPA_COMPLIANCE_MODE: True (forced)")
        logger.warning("  - CHILD_SAFETY_ENABLED: True (forced)")
        logger.warning("  - SECURE_COOKIES: True (forced)")
        logger.warning("  - FORCE_HTTPS: True (forced)")

        # Double-check DEBUG is not set in any form
        debug_variants = [
            "DEBUG",
            "FLASK_DEBUG",
            "DJANGO_DEBUG",
            "FASTAPI_DEBUG",
            "STARLETTE_DEBUG",
        ]
        for variant in debug_variants:
            if env_get(variant, "").lower() in ["true", "1", "yes", "on"]:
                logger.critical(
                    f"SECURITY VIOLATION: {variant} was set to True in production!"
                )
                env_set_secure(variant, "False")

        # Use the security service to validate production environment
        security_service = (
            container.security_service()
        )  # Assuming security_service is wired
        errors = security_service.validate_production_environment_security()

        if errors:
            error_messages = "; ".join(errors)
            logger.critical(
                f"Production environment validation failed: {error_messages}"
            )
            raise StartupValidationException(
                f"Critical production environment security checks failed: {error_messages}"
            )
