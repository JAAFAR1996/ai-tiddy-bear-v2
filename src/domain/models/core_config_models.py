"""Defines Pydantic models for various application configuration settings.

This module centralizes the schema definitions for application-wide settings,
including general application parameters, server configurations, database
connection details, and more. These models facilitate type-safe and validated
access to configuration values throughout the application.
"""

from pydantic import BaseModel, Field


class AppSettings(BaseModel):
    """Application-wide settings."""

    APP_NAME: str = Field("AI Teddy Bear", description="Name of the application")
    APP_VERSION: str = Field("2.0.0", description="Version of the application")
    ENVIRONMENT: str = Field(
        "production",
        pattern="^(development|testing|staging|production)$",
        description="Application environment (development, testing, staging, production)",
    )
    DEBUG: bool = Field(False, description="Enable debug mode")
    TIMEZONE: str = Field("UTC", description="Application timezone")


