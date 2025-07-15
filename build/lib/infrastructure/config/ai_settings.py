"""
Defines AI-related configuration settings for the application.

This module uses Pydantic to manage environment variables and provide
structured access to AI service configurations, such as OpenAI API key,
model name, temperature, and maximum tokens. It ensures that AI settings
are loaded securely and consistently across the application.
"""

from pydantic import Field

from src.infrastructure.config.base_settings import BaseApplicationSettings


class AISettings(BaseApplicationSettings):
    """Configuration settings for AI services."""

    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field("gpt-4-turbo-preview", env="OPENAI_MODEL")
    OPENAI_TEMPERATURE: float = Field(0.7, env="OPENAI_TEMPERATURE")
    OPENAI_MAX_TOKENS: int = Field(200, env="OPENAI_MAX_TOKENS")
    # Add other AI-related settings here
