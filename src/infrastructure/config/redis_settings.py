"""
Defines Redis-related configuration settings for the application.

This module uses Pydantic to manage environment variables and provide
structured access to Redis connection details, primarily the Redis URL.
It ensures that Redis settings are loaded securely and consistently
across the application, supporting caching and session management.
"""

from pydantic import Field, RedisDsn

from src.infrastructure.config.base_settings import BaseApplicationSettings


class RedisSettings(BaseApplicationSettings):
    """Configuration settings for Redis integration."""

    REDIS_URL: RedisDsn = Field(..., env="REDIS_URL")
