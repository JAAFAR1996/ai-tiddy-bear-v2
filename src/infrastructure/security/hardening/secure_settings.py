"""Secure Settings Configuration for AI Teddy Bear."""

import os

try:
    from pydantic import BaseModel, Field, SecretStr
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError as e:
    logger.critical(f"CRITICAL ERROR: Pydantic is required for production use: {e}")
    logger.critical(
        "Install required dependencies: pip install pydantic pydantic-settings",
    )
    raise ImportError(
        "Missing required dependency: pydantic. This application cannot run without it.",
    ) from e

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class SecureAppSettings(BaseSettings):
    """إعدادات التطبيق الآمنة."""

    # Application Info
    app_name: str = Field(default="AI Teddy Bear", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    environment: str = Field(
        default="development",
        description="Environment (development/staging/production)",
    )
    debug: bool = Field(default=False, description="Debug mode")

    # Security Settings
    secret_key: SecretStr = Field(
        ...,
        min_length=32,
        description="Application secret key",
    )
    jwt_secret: SecretStr = Field(..., min_length=32, description="JWT secret key")
    encryption_key: SecretStr = Field(
        ...,
        min_length=32,
        description="Data encryption key",
    )

    # Database Settings
    database_url: SecretStr = Field(..., description="Database connection URL")
    database_pool_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Database pool size",
    )
    database_max_overflow: int = Field(
        default=20,
        ge=0,
        le=100,
        description="Database max overflow",
    )

    # AI Service Settings
    openai_api_key: SecretStr = Field(..., description="OpenAI API key")
    anthropic_api_key: SecretStr | None = Field(
        default=None,
        description="Anthropic API key",
    )
    azure_speech_key: SecretStr | None = Field(
        default=None,
        description="Azure Speech API key",
    )

    # Security Hardening
    enable_security_headers: bool = Field(
        default=True,
        description="Enable security headers middleware",
    )
    enable_rate_limiting: bool = Field(default=True, description="Enable rate limiting")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def get_secure_settings() -> SecureAppSettings:
    """Get secure settings instance."""
    env_file = os.getenv("ENV_FILE", ".env")
    return SecureAppSettings(_env_file=env_file)
