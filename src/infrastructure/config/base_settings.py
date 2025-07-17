"""
Defines the base configuration settings for the application.

This module provides the `BaseApplicationSettings` class, which serves as
the foundation for all environment-specific and feature-specific settings.
It includes common configurations for environment, logging, application
information, and server parameters, ensuring consistency and reusability
across different parts of the application.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class BaseApplicationSettings(BaseSettings):
    """Base settings for all environments."""

    # ================================
    # Environment Configuration
    # ================================
    environment: str = Field(
        "production", pattern="^(development|staging|production|testing)$"
    )
    debug: bool = Field(default=False)
    log_level: str = Field(
        "INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")

    # ================================
    # Application Information
    # ================================
    app_name: str = "AI Teddy Bear"
    app_version: str = "1.0.0"
    app_description: str = (
        "Enterprise-grade AI companion for children with COPPA compliance"
    )

    # ================================
    # Server Configuration
    # ================================
    host: str = "0.0.0.0"
    port: int = Field(8000, ge=1, le=65535)
    workers: int = Field(4, ge=1, le=32)
    worker_class: str = "uvicorn.workers.UvicornWorker"
