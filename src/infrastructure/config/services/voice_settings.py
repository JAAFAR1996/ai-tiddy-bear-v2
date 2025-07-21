from pydantic import Field

from src.infrastructure.config.core.base_settings import BaseApplicationSettings


class VoiceSettings(BaseApplicationSettings):
    VOICE_PROVIDER: str | None = Field(None, env="VOICE_PROVIDER")

    def get_provider(self) -> str:
        if not self.VOICE_PROVIDER:
            raise RuntimeError("VOICE_PROVIDER environment variable must be set for production use.")
        return self.VOICE_PROVIDER
    VOICE_API_KEY: str | None = Field(None, env="VOICE_API_KEY")
    # Add other voice-related settings here
