"""
Defines audio-related configuration settings for the application.

This module uses Pydantic to manage environment variables and provide
structured access to audio processing configurations, such as maximum
audio duration, maximum file size, and supported audio formats.
It ensures consistent and validated audio settings across the application.
"""

from pydantic import Field

from src.infrastructure.config.base_settings import BaseApplicationSettings


class AudioSettings(BaseApplicationSettings):
    """Configuration settings for audio processing."""

    MAX_AUDIO_DURATION_SECONDS: int = Field(30, env="MAX_AUDIO_DURATION_SECONDS")
    MAX_FILE_SIZE_MB: int = Field(10, env="MAX_FILE_SIZE_MB")
    SUPPORTED_AUDIO_FORMATS: str = Field(
        "audio/wav,audio/mpeg,audio/mp3", env="SUPPORTED_AUDIO_FORMATS"
    )
    # Add other audio-related settings here
