"""
Defines privacy-related configuration settings for the application.

This module uses Pydantic to manage environment variables and provide
structured access to privacy controls, such as COPPA compliance enablement.
It ensures that privacy settings are consistently applied across the application,
supporting regulatory adherence and user data protection.
"""

from pydantic import Field

from src.infrastructure.config.base_settings import BaseApplicationSettings


class PrivacySettings(BaseApplicationSettings):
    """Configuration settings for privacy controls."""

    COPPA_ENABLED: bool = Field(False, env="COPPA_ENABLED")
    # Add other privacy-related settings here
