"""Base settings configuration."""

from pydantic_settings import BaseSettings as PydanticBaseSettings


class BaseSettings(PydanticBaseSettings):
    """Base settings with common configuration."""

    class Config:
        env_file = ".env"
        case_sensitive = False


# Alias for backward compatibility
BaseApplicationSettings = BaseSettings
