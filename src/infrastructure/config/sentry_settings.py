"""Defines Sentry-related configuration settings for error tracking.

This module uses Pydantic to manage environment variables and provide
structured access to the Sentry DSN (Data Source Name). It ensures that
Sentry integration settings are consistently applied across the application,
enabling effective error monitoring and reporting.
"""

from pydantic import Field

from src.infrastructure.config.base_settings import BaseApplicationSettings


class SentrySettings(BaseApplicationSettings):
    """Configuration settings for Sentry error tracking."""

    SENTRY_DSN: str | None = Field(None, env="SENTRY_DSN")
