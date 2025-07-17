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


class ServerSettings(BaseModel):
    """Server configuration settings."""

    SERVER_HOST: str = Field("0.0.0.0", description="Host for the FastAPI server")
    SERVER_PORT: int = Field(8000, description="Port for the FastAPI server")
    WEBSOCKET_PORT: int = Field(8765, description="Port for WebSocket connections")
    ENABLE_CORS: bool = Field(True, description="Enable Cross-Origin Resource Sharing")
    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "https://app.aiteddybear.com",
            "https://api.aiteddybear.com",
        ],
        description="Allowed CORS origins",
    )
    MAX_CONTENT_LENGTH_MB: int = Field(
        50,
        description="Maximum content length for requests in MB",
    )
    REQUEST_TIMEOUT_SECONDS: int = Field(
        60,
        description="Default request timeout in seconds",
    )
    ENABLE_HTTPS: bool = Field(False, description="Enable HTTPS for the server")
    SSL_CERT_PATH: str | None = Field(None, description="Path to SSL certificate file")
    SSL_KEY_PATH: str | None = Field(None, description="Path to SSL key file")


class DatabaseSettings(BaseModel):
    """Database connection settings."""

    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL connection URL - MUST be set in environment for production",
    )
    DATABASE_POOL_SIZE: int = Field(
        20,
        ge=5,
        le=100,
        description="Database connection pool size",
    )
    DATABASE_MAX_OVERFLOW: int = Field(
        0,
        ge=0,
        le=50,
        description="Database connection max overflow",
    )
    DATABASE_POOL_RECYCLE: int = Field(
        300,
        ge=60,
        le=3600,
        description="Database connection pool recycle time in seconds",
    )
    DATABASE_ECHO: bool = Field(False, description="Enable SQLAlchemy echo mode")
    DATABASE_SSL_MODE: str = Field(
        "require",
        description="SSL mode for database connection",
    )


class SecuritySettings(BaseModel):
    """Security-related settings."""

    SECRET_KEY: str = Field(..., description="Secret key for cryptographic operations")
    ALGORITHM: str = Field("HS256", description="Hashing algorithm for JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        30,
        description="Access token expiration time in minutes",
    )
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(
        10080,
        description="Refresh token expiration time in minutes (7 days)",
    )
    PASSWORD_HASHING_ALGORITHM: str = Field(
        "bcrypt",
        description="Algorithm for password hashing",
    )
    RATE_LIMIT_ENABLED: bool = Field(True, description="Enable API rate limiting")
    RATE_LIMIT_PER_MINUTE: int = Field(
        100,
        description="Max requests per minute per IP",
    )


class LoggingSettings(BaseModel):
    """Logging configuration settings."""

    LOG_LEVEL: str = Field("INFO", description="Minimum logging level")
    LOG_TO_FILE: bool = Field(False, description="Enable logging to file")
    LOG_FILE_PATH: str = Field("app.log", description="Path to log file")
    LOG_ROTATION: str = Field(
        "10 MB",
        description="Log file rotation size or frequency",
    )
    LOG_RETENTION: int = Field(7, description="Number of days to retain log files")


class ExternalServicesSettings(BaseModel):
    """Settings for external services integrations."""

    OPENAI_API_KEY: str | None = Field(None, description="OpenAI API Key")
    OPENAI_ORG_ID: str | None = Field(None, description="OpenAI Organization ID")
    STRIPE_API_KEY: str | None = Field(None, description="Stripe API Key")
    SENTRY_DSN: str | None = Field(None, description="Sentry DSN for error tracking")


class COPPAComplianceSettings(BaseModel):
    """Settings related to COPPA compliance."""

    COPPA_ENABLED: bool = Field(True, description="Enable COPPA compliance features")
    MIN_CHILD_AGE: int = Field(13, description="Minimum age for COPPA compliance")
    DATA_RETENTION_DAYS: int = Field(
        90,
        description="Data retention period in days for child data",
    )
    PARENTAL_CONSENT_REQUIRED: bool = Field(
        True,
        description="Require parental consent for data collection",
    )


class FeatureFlagsSettings(BaseModel):
    """Feature flags for toggling application features."""

    NEW_FEATURE_ENABLED: bool = Field(
        False,
        description="Enable new experimental feature",
    )
    A_B_TESTING_ACTIVE: bool = Field(False, description="Activate A/B testing mode")
