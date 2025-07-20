"""Service factory for creating mock or real service implementations."""

from typing import Any

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="infrastructure")


class ServiceFactory:
    """Factory for creating service implementations with proper error handling for missing services."""

    def __init__(self, use_mocks: bool = False) -> None:
        self.use_mocks = use_mocks

    def create_speech_processor(self, settings: Any) -> Any:
        """Create speech processor service with fallback handling."""
        try:
            from infrastructure.external_apis.whisper_client import (
                WhisperClient,
            )

            return WhisperClient(model_name=settings.WHISPER_MODEL)
        except ImportError as e:
            logger.critical(f"CRITICAL ERROR: Whisper client dependency missing: {e}")
            logger.critical("Install required dependencies: pip install whisper")
            raise ImportError("Missing speech processor dependency: whisper") from e
        except AttributeError as e:
            logger.critical(f"CRITICAL ERROR: Missing WHISPER_MODEL in settings: {e}")
            raise ValueError("WHISPER_MODEL configuration required") from e
        except Exception as e:
            logger.critical(f"CRITICAL ERROR: Failed to create speech processor: {e}")
            raise RuntimeError("Speech processor service creation failed") from e

    def create_openai_client(self, settings: Any) -> Any:
        """Create OpenAI client service with fallback handling."""
        try:
            from infrastructure.external_apis.openai_client import OpenAIClient

            if not hasattr(settings, "OPENAI_API_KEY") or not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is required")
            return OpenAIClient(api_key=settings.OPENAI_API_KEY)
        except ImportError as e:
            logger.critical(f"CRITICAL ERROR: OpenAI client dependency missing: {e}")
            logger.critical("Install required dependencies: pip install openai")
            raise ImportError("Missing OpenAI dependency: openai") from e
        except AttributeError as e:
            logger.critical(f"CRITICAL ERROR: Missing OPENAI_API_KEY in settings: {e}")
            raise ValueError("OPENAI_API_KEY configuration required") from e
        except Exception as e:
            logger.critical(f"CRITICAL ERROR: Failed to create OpenAI client: {e}")
            raise RuntimeError("OpenAI service creation failed") from e

    def create_tts_service(self, settings: Any) -> Any:
        """Create text-to-speech service with fallback handling."""
        try:
            from infrastructure.external_apis.elevenlabs_client import (
                ElevenLabsClient,
            )

            if (
                not hasattr(settings, "ELEVENLABS_API_KEY")
                or not settings.ELEVENLABS_API_KEY
            ):
                raise ValueError("ELEVENLABS_API_KEY is required")
            return ElevenLabsClient(api_key=settings.ELEVENLABS_API_KEY)
        except ImportError as e:
            logger.critical(
                f"CRITICAL ERROR: ElevenLabs client dependency missing: {e}",
            )
            logger.critical("Install required dependencies: pip install elevenlabs")
            raise ImportError("Missing TTS dependency: elevenlabs") from e
        except AttributeError as e:
            logger.critical(
                f"CRITICAL ERROR: Missing ELEVENLABS_API_KEY in settings: {e}",
            )
            raise ValueError("ELEVENLABS_API_KEY configuration required") from e
        except Exception as e:
            logger.critical(f"CRITICAL ERROR: Failed to create TTS service: {e}")
            raise RuntimeError("TTS service creation failed") from e

    def create_database(self, settings: Any) -> Any:
        """Create database implementation with fallback handling."""
        try:
            from infrastructure.persistence.database import Database

            if not hasattr(settings, "database") or not settings.database.DATABASE_URL:
                raise ValueError("DATABASE_URL is required in settings.database")

            # Pass connection pooling settings from main settings to Database
            # constructor
            return Database(
                database_url=settings.database.DATABASE_URL,
                pool_size=settings.database.POOL_SIZE,
                max_overflow=settings.database.MAX_OVERFLOW,
                pool_recycle=settings.database.POOL_RECYCLE,
                pool_pre_ping=settings.database.POOL_PRE_PING,
                pool_timeout=settings.database.POOL_TIMEOUT,
            )
        except ImportError as e:
            logger.critical(f"CRITICAL ERROR: Database dependency missing: {e}")
            logger.critical(
                "Install required dependencies: pip install sqlalchemy asyncpg",
            )
            raise ImportError("Missing database dependency") from e
        except AttributeError as e:
            logger.critical(f"CRITICAL ERROR: Missing database settings: {e}")
            raise ValueError("Database configuration required") from e
        except Exception as e:
            logger.critical(f"CRITICAL ERROR: Failed to create database: {e}")
            raise RuntimeError("Database service creation failed") from e
