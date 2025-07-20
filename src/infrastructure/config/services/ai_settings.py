
from pydantic import Field
from src.infrastructure.config.core.base_settings import BaseApplicationSettings

class AISettings(BaseApplicationSettings):
    """Configuration settings for AI services."""

    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field("gpt-4-turbo-preview", env="OPENAI_MODEL")
    OPENAI_TEMPERATURE: float = Field(0.7, env="OPENAI_TEMPERATURE")
    OPENAI_MAX_TOKENS: int = Field(200, env="OPENAI_MAX_TOKENS")
    WHISPER_MODEL: str = Field("medium", env="WHISPER_MODEL")
    ELEVENLABS_API_KEY: str | None = Field(None, env="ELEVENLABS_API_KEY")