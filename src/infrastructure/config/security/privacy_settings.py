"""Defines privacy-related configuration settings for the application.

This module uses Pydantic to manage environment variables and provide
structured access to privacy controls, such as COPPA compliance enablement.
It ensures that privacy settings are consistently applied across the application,
supporting regulatory adherence and user data protection.
"""

from pydantic import Field

from src.infrastructure.config.core.base_settings import BaseApplicationSettings


class PrivacySettings(BaseApplicationSettings):
    """Configuration settings for privacy and COPPA compliance."""

    COPPA_ENABLED: bool = Field(True, env="COPPA_ENABLED")
    MAX_CHILD_AGE: int = Field(12, env="MAX_CHILD_AGE")
    PARENTAL_CONSENT_REQUIRED: bool = Field(True, env="PARENTAL_CONSENT_REQUIRED")

    # إعدادات الاحتفاظ بالبيانات
    DATA_RETENTION_DAYS: int = Field(90, env="DATA_RETENTION_DAYS")
    AUTO_DELETE_ENABLED: bool = Field(True, env="AUTO_DELETE_ENABLED")
    DATA_EXPORT_ENABLED: bool = Field(True, env="DATA_EXPORT_ENABLED")
