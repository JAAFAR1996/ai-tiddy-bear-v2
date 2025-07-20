from pydantic import Field

from src.infrastructure.config.base_settings import BaseApplicationSettings


class VoiceSettings(BaseApplicationSettings):
    VOICE_PROVIDER: str = Field("mock", env="VOICE_PROVIDER")
    VOICE_API_KEY: str | None = Field(None, env="VOICE_API_KEY")
    # Add other voice-related settings here
