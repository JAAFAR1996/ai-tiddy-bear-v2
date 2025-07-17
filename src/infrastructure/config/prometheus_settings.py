"""Defines Prometheus-related configuration settings for the application.

This module uses Pydantic to manage environment variables and provide
structured access to Prometheus integration settings, primarily whether
Prometheus metrics collection is enabled. It ensures consistent and
validated monitoring configurations across the application.
"""

from pydantic import Field

from src.infrastructure.config.base_settings import BaseApplicationSettings


class PrometheusSettings(BaseApplicationSettings):
    """Configuration settings for Prometheus monitoring."""

    PROMETHEUS_ENABLED: bool = Field(False, env="PROMETHEUS_ENABLED")
