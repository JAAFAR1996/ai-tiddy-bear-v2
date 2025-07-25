from pydantic import field_validator

"""Defines secure configuration settings for the AI Teddy Bear project.

This module provides critical security-related settings, including JWT
configuration, rate limiting, content filtering, COPPA compliance parameters,
and session security. It enforces strong secret key validation and ensures
that sensitive configurations are properly managed for a robust and secure
application environment.
"""

import secrets
import sys

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="config")


class SecureSettings(BaseSettings):
    """Security settings for the application."""

    # JWT Configuration
    JWT_SECRET: str = Field(..., min_length=32, description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_EXPIRE_MINUTES: int = Field(
        default=30,
        ge=5,
        le=1440,
        description="JWT expiration in minutes",
    )

    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=60, ge=1, le=1000)
    RATE_LIMIT_BURST: int = Field(default=10, ge=1, le=100)

    # Content Filtering
    CONTENT_FILTER_STRICT_MODE: bool = Field(default=True)
    SAFETY_THRESHOLD: float = Field(default=0.8, ge=0.0, le=1.0)

    # COPPA Compliance
    COPPA_ENABLED: bool = Field(default=True)
    MAX_CHILD_AGE: int = Field(default=12, ge=1, le=18)
    PARENTAL_CONSENT_REQUIRED: bool = Field(default=True)

    # Session Security
    SESSION_SECRET: str = Field(..., min_length=32)
    SESSION_EXPIRE_HOURS: int = Field(default=24, ge=1, le=168)

    @field_validator("JWT_SECRET", "SESSION_SECRET")
    @classmethod
    def validate_secrets(cls, v: str) -> str:
        """Validates the strength of secret keys.

        Args:
            v: The secret key string.

        Returns:
            The validated secret key string.

        Raises:
            ValueError: If the secret key is too short or is a default placeholder.

        """
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters")
        if v in ["CHANGE_THIS_TO_A_STRONG_SECRET_KEY", "your_secret_here"]:
            raise ValueError("Must change default secret key")
        return v

    class Config:
        env_file = ".env"
        extra = "ignore"


# Example usage and generation of a new secret key
def generate_new_secret_key() -> str:
    """Generates a new strong secret key.

    Returns:
        A randomly generated URL-safe text string.

    """
    return secrets.token_urlsafe(32)


if __name__ == "__main__":
    # This block is for demonstration and should not be run in production
    # To generate a new secret key, run this file directly:
    # python -m src.infrastructure.config.secure_settings
    new_secret = generate_new_secret_key()
    print(f"Generated new JWT_SECRET: {new_secret}")
    print(f"Generated new SESSION_SECRET: {secrets.token_urlsafe(32)}")

    # Example of how to load settings (requires .env file or env vars set)
    try:
        settings = SecureSettings()
        print(f"Loaded JWT Algorithm: {settings.JWT_ALGORITHM}")
    except Exception as e:
        print(f"Error loading settings: {e}")
        sys.exit(1)
