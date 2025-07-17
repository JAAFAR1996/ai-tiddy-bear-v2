"""
Defines security-related configuration settings for the application.

This module uses Pydantic to manage environment variables and provide
structured access to various security parameters, including secret keys,
JWT configuration, COPPA encryption keys, rate limiting, login attempt limits,
and lockout durations. It centralizes security configurations to ensure
consistent application of security policies.
"""

from typing import Dict

from pydantic import Field, SecretStr, model_validator

from src.infrastructure.config.base_settings import BaseApplicationSettings


class SecuritySettings(BaseApplicationSettings):
    """Configuration settings for application security."""

    # Constants for key lengths
    MIN_SECRET_KEY_LENGTH: int = 32
    MIN_JWT_SECRET_KEY_LENGTH: int = 32
    COPPA_ENCRYPTION_KEY_LENGTH: int = 44

    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    COPPA_ENCRYPTION_KEY: str = Field(..., env="COPPA_ENCRYPTION_KEY")

    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(
        60, env="RATE_LIMIT_REQUESTS_PER_MINUTE"
    )
    RATE_LIMIT_REQUESTS_PER_HOUR: int = Field(
        3600, env="RATE_LIMIT_REQUESTS_PER_HOUR")
    MAX_LOGIN_ATTEMPTS: int = Field(5, env="MAX_LOGIN_ATTEMPTS")
    LOCKOUT_DURATION_SECONDS: int = Field(300, env="LOCKOUT_DURATION_SECONDS")

    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    VAULT_URL: str | None = Field(None, env="VAULT_URL")
    VAULT_TOKEN: SecretStr | None = Field(None, env="VAULT_TOKEN")

    RATE_LIMITS: Dict[str, Dict[str, int]] = Field(
        {
            "/auth/login": {"requests": 5, "window": 60},
            "/auth/register": {"requests": 3, "window": 60},
            "/auth/refresh": {"requests": 10, "window": 60},
            "/auth/password-reset": {"requests": 3, "window": 3600},
            "/esp32": {"requests": 30, "window": 60},
            "/ai/generate": {"requests": 20, "window": 60},
            "/audio": {"requests": 15, "window": 60},
            "/api/v1/conversation": {"requests": 30, "window": 300},
            "/api/v1/voice": {"requests": 10, "window": 300},
            "/dashboard": {"requests": 100, "window": 60},
            "/children": {"requests": 50, "window": 60},
            "/reports": {"requests": 30, "window": 60},
            "/health": {"requests": 1000, "window": 60},
            "/metrics": {"requests": 1000, "window": 60},
            "/docs": {"requests": 60, "window": 60},
            "/redoc": {"requests": 60, "window": 60},
        }
    )

    @model_validator(mode="after")
    def validate_token_expiration(self) -> "SecuritySettings":
        """Validate that access token expiration does not exceed refresh token expiration."""
        if self.ACCESS_TOKEN_EXPIRE_MINUTES >= (
            self.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60
        ):
            raise ValueError(
                "ACCESS_TOKEN_EXPIRE_MINUTES cannot exceed REFRESH_TOKEN_EXPIRE_DAYS."
            )
        return self
