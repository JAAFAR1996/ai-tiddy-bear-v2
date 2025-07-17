"""
Defines general application configuration settings.

This module uses Pydantic to manage environment variables and provide
structured access to core application settings, such as environment,
debug mode, application name and version, HTTPS enablement, CORS origins,
trusted hosts, session duration, child-specific endpoints, and age limits.
"""

from typing import List, Optional
from pathlib import Path

from pydantic import Field

from src.infrastructure.config.base_settings import BaseApplicationSettings
import src.common.constants as constants  # Import the constants module


class ApplicationSettings(BaseApplicationSettings):
    """General application configuration settings."""

    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    DEBUG: bool = Field(False, env="DEBUG")
    APP_NAME: str = Field("AI Teddy Bear System", env="APP_NAME")
    APP_VERSION: str = Field("2.0.0", env="APP_VERSION")
    ENABLE_HTTPS: bool = Field(True, env="ENABLE_HTTPS")
    CORS_ORIGINS: Optional[List[str]] = Field(None, env="CORS_ORIGINS")
    TRUSTED_HOSTS: Optional[List[str]] = Field(None, env="TRUSTED_HOSTS")
    MAX_SESSION_DURATION_SECONDS: int = Field(
        3600, env="MAX_SESSION_DURATION_SECONDS")
    CHILD_ENDPOINTS: List[str] = Field(
        constants.CHILD_SPECIFIC_API_ENDPOINTS,
        env="CHILD_ENDPOINTS",  # Use the imported constant
    )
    MIN_CHILD_AGE: int = Field(3, env="MIN_CHILD_AGE")
    MAX_CHILD_AGE: int = Field(13, env="MAX_CHILD_AGE")
    PROJECT_ROOT: Path = Field(
        Path(__file__).parent.parent.parent.parent.resolve(), env="PROJECT_ROOT"
    )  # Ensure PROJECT_ROOT is a Path object directly.
    STATIC_FILES_DIR: str = Field("static", env="STATIC_FILES_DIR")
    # Add other general application settings here
