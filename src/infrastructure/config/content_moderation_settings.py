"""
Defines content moderation configuration settings for the application.

This module uses Pydantic to manage environment variables and provide
structured access to content filtering rules, such as additional blocked
words, maximum content length, and safety thresholds. It ensures that
content moderation settings are consistently applied across the application.
"""

from typing import List

from pydantic import Field

from src.infrastructure.config.base_settings import BaseApplicationSettings


class ContentModerationSettings(BaseApplicationSettings):
    """Configuration settings for content moderation."""

    ADDITIONAL_BLOCKED_WORDS: List[str] = Field([], env="ADDITIONAL_BLOCKED_WORDS")
    MAX_CONTENT_LENGTH: int = Field(1000, env="MAX_CONTENT_LENGTH")
    SAFETY_THRESHOLD: float = Field(0.7, env="SAFETY_THRESHOLD")
    # Add other content moderation settings here
