"""Centralized configuration management for AI Teddy Bear.

This module aggregates all configuration settings from organized submodules.
"""

from functools import lru_cache

from pydantic_settings import SettingsConfigDict

# Core settings
from src.infrastructure.config.core.application_settings import ApplicationSettings
from src.infrastructure.config.core.base_settings import (
    BaseSettings as CoreBaseSettings,
)
from src.infrastructure.config.core.server_settings import ServerSettings

# Integration settings
from src.infrastructure.config.integrations.database_settings import DatabaseSettings
from src.infrastructure.config.integrations.kafka_settings import KafkaSettings
from src.infrastructure.config.integrations.redis_settings import RedisSettings

# Monitoring settings
from src.infrastructure.config.monitoring.prometheus_settings import PrometheusSettings
from src.infrastructure.config.monitoring.sentry_settings import SentrySettings

# Security settings
from src.infrastructure.config.security.privacy_settings import PrivacySettings
from src.infrastructure.config.security.security_settings import SecuritySettings

# Service settings
from src.infrastructure.config.services.ai_settings import AISettings
from src.infrastructure.config.services.audio_settings import AudioSettings
from src.infrastructure.config.services.content_moderation_settings import (
    ContentModerationSettings,
)
from src.infrastructure.config.services.voice_settings import VoiceSettings
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="config")


class Settings(
    ApplicationSettings,
    AISettings,
    AudioSettings,
    ContentModerationSettings,
    DatabaseSettings,
    KafkaSettings,
    PrivacySettings,
    PrometheusSettings,
    RedisSettings,
    SecuritySettings,
    SentrySettings,
    ServerSettings,
    VoiceSettings,
    CoreBaseSettings,
):
    """Main settings class that combines all configuration modules."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
