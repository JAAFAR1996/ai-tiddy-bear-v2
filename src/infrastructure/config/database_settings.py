"""Defines database configuration settings for the application.

This module uses Pydantic to manage environment variables and provide
structured access to database connection URLs. It includes validation
to ensure that appropriate database types are used for different
environments (e.g., PostgreSQL for production, SQLite or PostgreSQL for development).
"""
import os
from pydantic import Field, field_validator
from src.infrastructure.config.base_settings import BaseApplicationSettings

class DatabaseSettings(BaseApplicationSettings):
    """Configuration settings for database connections."""

    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    ASYNC_DATABASE_URL: str = Field(..., env="ASYNC_DATABASE_URL")
    
    # إضافة المتغيرات المفقودة
    DB_HOST: str = Field("localhost", env="DB_HOST")
    DB_PORT: str = Field("5432", env="DB_PORT")
    DB_NAME: str = Field("ai_teddy", env="DB_NAME")
    DB_PASSWORD: str | None = Field(None, env="DB_PASSWORD")
    
    ENABLE_DATABASE: bool = Field(True, env="ENABLE_DATABASE")

    @field_validator("DATABASE_URL", "ASYNC_DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validates the database URL based on the environment.

        Args:
            v: The database URL string.

        Returns:
            The validated database URL string.

        Raises:
            ValueError: If the database URL is invalid for the current environment.

        """
        if os.getenv("ENVIRONMENT") == "production":
            if not v.startswith("postgresql"):
                raise ValueError("PostgreSQL is required for production environments.")
        elif not (v.startswith("sqlite") or v.startswith("postgresql")):
            raise ValueError(
                "Only SQLite or PostgreSQL are allowed for development/testing.",
            )
        return v
