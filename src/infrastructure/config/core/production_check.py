"""Production environment validation and checks."""

import os
import sys
from pathlib import Path
from typing import List

from src.infrastructure.config.settings import get_settings
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__)


def check_production_requirements() -> None:
    """Validate all production requirements are met."""
    logger.info("Running production environment checks...")

    errors: List[str] = []
    warnings: List[str] = []

    # Check environment variables
    required_vars = [
        "OPENAI_API_KEY",
        "DATABASE_URL",
        "REDIS_URL",
        "JWT_SECRET_KEY",
    ]

    for var in required_vars:
        if not os.getenv(var):
            errors.append(f"Missing required environment variable: {var}")

    # Check SSL certificates
    ssl_cert = Path("/etc/ssl/certs/teddy-bear.crt")
    ssl_key = Path("/etc/ssl/private/teddy-bear.key")

    if not ssl_cert.exists():
        warnings.append("SSL certificate not found")
    if not ssl_key.exists():
        warnings.append("SSL key not found")

    # Display results
    if errors:
        logger.error("Production check failed!")
        for error in errors:
            logger.error(f"  ❌ {error}")
        sys.exit(1)

    if warnings:
        logger.warning("Production warnings:")
        for warning in warnings:
            logger.warning(f"  ⚠️  {warning}")

    logger.info("✅ Production checks passed!")


def display_startup_banner() -> None:
    """Display application startup banner."""
    banner = """
    🧸 AI Teddy Bear v1.0.0
    ========================
    Safe AI Companion for Children

    Environment: {}
    Debug Mode: {}
    """.format(
        get_settings().ENVIRONMENT, get_settings().DEBUG
    )
    print(banner)


def enforce_production_safety() -> None:
    """Enforce production safety requirements."""
    settings = get_settings()

    if settings.ENVIRONMENT == "production":
        check_production_requirements()
    else:
        logger.info(
            f"Running in {settings.ENVIRONMENT} mode - skipping production checks"
        )
        logger.info(
            f"Running in {settings.ENVIRONMENT} mode - skipping production checks"
        )
