"""Application settings and configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.infrastructure.config.ai_settings import AISettings
from src.infrastructure.config.application_settings import ApplicationSettings
from src.infrastructure.config.audio_settings import AudioSettings
from src.infrastructure.config.content_moderation_settings import (
    ContentModerationSettings,
)
from src.infrastructure.config.database_settings import DatabaseSettings
from src.infrastructure.config.kafka_settings import KafkaSettings
from src.infrastructure.config.privacy_settings import PrivacySettings
from src.infrastructure.config.prometheus_settings import PrometheusSettings
from src.infrastructure.config.redis_settings import RedisSettings
from src.infrastructure.config.security_settings import SecuritySettings
from src.infrastructure.config.sentry_settings import SentrySettings
from src.infrastructure.config.server_settings import ServerSettings
from src.infrastructure.config.voice_settings import VoiceSettings
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="config")


class Settings(BaseSettings):
    """Main application settings composed of modular configuration classes."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        validate_assignment=True,
        extra="forbid",
    )
    application: ApplicationSettings = ApplicationSettings()
    database: DatabaseSettings = DatabaseSettings()
    kafka: KafkaSettings = KafkaSettings()
    redis: RedisSettings = RedisSettings()
    security: SecuritySettings = SecuritySettings()
    sentry: SentrySettings = SentrySettings()
    prometheus: PrometheusSettings = PrometheusSettings()
    voice: VoiceSettings = VoiceSettings()
    audio: AudioSettings = AudioSettings()
    ai: AISettings = AISettings()
    privacy: PrivacySettings = PrivacySettings()
    content_moderation: ContentModerationSettings = ContentModerationSettings()
    server: ServerSettings = ServerSettings()

    def model_post_init(self, __context) -> None:
        """Perform additional validation after model initialization."""
        env = self.application.ENVIRONMENT

        # Production-specific validations
        if env == "production":
            if self.application.DEBUG:
                raise ValueError(
                    "DEBUG must be False in production environment for security.",
                )

            # Critical security and infrastructure keys
            if not self.security.SECRET_KEY or len(self.security.SECRET_KEY) < 32:
                raise ValueError(
                    "SECRET_KEY must be set and at least 32 characters long in production.",
                )
            if (
                not self.security.JWT_SECRET_KEY
                or len(self.security.JWT_SECRET_KEY) < 32
            ):
                raise ValueError(
                    "JWT_SECRET_KEY must be set and at least 32 characters long in production.",
                )
            if (
                not self.security.COPPA_ENCRYPTION_KEY
                or len(self.security.COPPA_ENCRYPTION_KEY) != 44
            ):
                raise ValueError(
                    "COPPA_ENCRYPTION_KEY must be a valid Fernet key (44 characters) in production.",
                )

            # Essential external service URLs
            if not self.database.DATABASE_URL:
                raise ValueError("DATABASE_URL must be set in production.")
            if not self.redis.REDIS_URL:
                raise ValueError("REDIS_URL must be set in production.")
            if not self.ai.OPENAI_API_KEY or not self.ai.OPENAI_API_KEY.startswith(
                "sk-",
            ):
                raise ValueError(
                    "OPENAI_API_KEY must be a valid OpenAI API key in production.",
                )

            # Sentry DSN for error monitoring
            if not self.sentry.SENTRY_DSN:
                logger.warning(
                    "SENTRY_DSN is not set in production. Error monitoring will be limited.",
                )

        # Cross-component logical validations
        if self.security.ACCESS_TOKEN_EXPIRE_MINUTES >= (
            self.security.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60
        ):
            raise ValueError(
                "ACCESS_TOKEN_EXPIRE_MINUTES cannot exceed REFRESH_TOKEN_EXPIRE_DAYS.",
            )

        logger.info(f"Configuration validated for environment: {env}")


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


__all__ = ["Settings", "get_settings"]
