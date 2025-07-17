from datetime import datetime
from typing import Any

from fastapi import Depends

from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.logging_config import get_logger


class SafetyMonitorService:
    """Service for monitoring and reporting on child safety incidents."""

    def __init__(self, settings: Settings = Depends(get_settings)) -> None:
        self.logger = get_logger(__name__, component="security")
        self.settings = settings
        self.blocked_words = self._load_blocked_words()
        self.safety_rules = self._load_safety_rules()

    def _load_blocked_words(self) -> list[str]:
        """Load blocked words from configuration."""
        # Default blocked words for child safety
        default_blocked_words = [
            "violence",
            "kill",
            "death",
            "weapon",
            "gun",
            "knife",
            "blood",
            "hate",
            "stupid",
            "idiot",
            "dumb",
            "moron",
            "loser",
            "scary",
            "nightmare",
            "monster",
            "demon",
            "evil",
            "adult",
            "mature",
            "inappropriate",
            "explicit",
        ]

        # Load additional words from settings if available
        if self.settings.content_moderation.ADDITIONAL_BLOCKED_WORDS:
            default_blocked_words.extend(
                self.settings.content_moderation.ADDITIONAL_BLOCKED_WORDS,
            )

        self.logger.info(
            f"Loaded {len(default_blocked_words)} blocked words from configuration",
        )
        return default_blocked_words

    def _load_safety_rules(self) -> dict[str, Any]:
        """Load safety rules from configuration."""
        # Default safety rules
        safety_rules = {
            "max_content_length": self.settings.content_moderation.MAX_CONTENT_LENGTH,
            "allow_personal_info": False,
            "require_age_appropriate": True,
            "violence_threshold": self.settings.content_moderation.SAFETY_THRESHOLD,
            "adult_content_threshold": 0.0,
            "language_filter_enabled": True,
            "emotional_safety_enabled": True,
        }

        self.logger.info(f"Loaded {len(safety_rules)} safety rules from configuration")
        return safety_rules

    async def check_content(self, content: str) -> dict[str, Any]:
        """Check if content is safe for children."""
        try:
            flags = []
            safety_score = 1.0

            # Check content length
            if len(content) > self.safety_rules["max_content_length"]:
                flags.append("Content too long")
                safety_score -= 0.1

            # Check for blocked words
            content_lower = content.lower()
            for word in self.blocked_words:
                if word in content_lower:
                    flags.append(f"Blocked word detected: {word}")
                    safety_score -= 0.3

            # Check for personal information patterns
            if self.safety_rules["allow_personal_info"] is False:
                if self._contains_personal_info(content):
                    flags.append("Personal information detected")
                    safety_score -= 0.5

            # Determine if content is safe
            is_safe = (
                safety_score >= self.settings.content_moderation.SAFETY_THRESHOLD
                and len(flags) == 0
            )

            result = {
                "safe": is_safe,
                "confidence": max(0.0, min(1.0, safety_score)),
                "flags": flags,
                "timestamp": datetime.utcnow().isoformat(),
            }

            self.logger.info(
                f"Content safety check: {is_safe}, score: {safety_score:.2f}",
            )
            return result
        except Exception as e:
            self.logger.error(f"Error checking content safety: {e!s}")
            return {
                "safe": False,
                "confidence": 0.0,
                "flags": ["Error during safety check"],
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _contains_personal_info(self, content: str) -> bool:
        """Check if content contains personal information."""
        import re

        # Simple patterns for personal information
        patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN pattern
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email pattern
            r"\b\d{3}-\d{3}-\d{4}\b",  # Phone pattern
            r"\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b",  # Credit card pattern
        ]

        return any(re.search(pattern, content) for pattern in patterns)

    async def check_audio(self, audio_data: bytes) -> dict[str, Any]:
        """Check if audio content is appropriate for children."""
        try:
            # Enhanced audio safety checks
            flags = []
            safety_score = 0.90

            # Check audio data size
            if len(audio_data) == 0:
                flags.append("Empty audio data")
                safety_score = 0.0
            elif len(audio_data) > 10 * 1024 * 1024:  # 10MB limit
                flags.append("Audio file too large")
                safety_score -= 0.2

            # Check audio duration estimate (basic)
            estimated_duration = len(audio_data) / (16000 * 2)  # Assuming 16kHz, 16-bit
            if estimated_duration > 300:  # 5 minutes max
                flags.append("Audio duration too long")
                safety_score -= 0.1

            # Check for basic audio format validity
            if not self._is_valid_audio_format(audio_data):
                flags.append("Invalid audio format")
                safety_score -= 0.3

            # Enhanced implementation would include:
            # 1. Speech-to-text transcription using Whisper
            # 2. Content analysis of transcribed text
            # 3. Audio pattern analysis for volume/tone
            # 4. Language detection and appropriateness
            # 5. Emotional tone analysis

            # For now, we implement basic audio validation
            is_safe = safety_score >= 0.7 and len(flags) == 0

            result = {
                "safe": is_safe,
                "confidence": safety_score,
                "flags": flags,
                "timestamp": datetime.utcnow().isoformat(),
                "audio_size_bytes": len(audio_data),
                "estimated_duration_seconds": round(estimated_duration, 2),
            }

            self.logger.info(
                f"Audio safety check: {is_safe}, score: {safety_score:.2f}, duration: {estimated_duration:.1f}s",
            )
            return result
        except Exception as e:
            self.logger.error(f"Error checking audio safety: {e!s}")
            return {
                "safe": False,
                "confidence": 0.0,
                "flags": ["Error during audio safety check"],
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _is_valid_audio_format(self, audio_data: bytes) -> bool:
        """Basic check for valid audio format."""
        if len(audio_data) < 44:  # Minimum WAV header size
            return False

        # Check for common audio file headers
        if audio_data[:4] == b"RIFF" and audio_data[8:12] == b"WAVE":
            return True  # WAV format
        if audio_data[:3] == b"ID3" or audio_data[:2] == b"\xff\xfb":
            return True  # MP3 format
        if audio_data[:4] == b"OggS":
            return True  # OGG format
        if audio_data[:4] == b"fLaC":
            return True  # FLAC format

        return False
