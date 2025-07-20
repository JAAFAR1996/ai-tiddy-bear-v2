from datetime import datetime
from typing import Any

"""Base Speech Analysis Components
Core classes and utilities for speech disorder detection"""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="infrastructure")


class SpeechAnalysisConfig:
    """Configuration for speech analysis."""

    def __init__(self) -> None:
        self.supported_formats = ["wav", "mp3", "ogg", "flac"]
        self.min_audio_duration = 2.0  # seconds
        self.max_audio_duration = 30.0  # seconds
        # Common speech disorder patterns
        self.disorder_patterns = {
            "stuttering": {
                "indicators": [
                    "repeated_syllables",
                    "prolonged_sounds",
                    "blocks",
                ],
                "confidence_threshold": 0.7,
            },
            "lisping": {
                "indicators": ["s_sound_distortion", "th_substitution"],
                "confidence_threshold": 0.6,
            },
            "articulation_disorder": {
                "indicators": [
                    "sound_substitution",
                    "sound_omission",
                    "sound_distortion",
                ],
                "confidence_threshold": 0.65,
            },
            "voice_disorder": {
                "indicators": ["hoarseness", "breathiness", "vocal_strain"],
                "confidence_threshold": 0.7,
            },
        }


class AudioValidator:
    """Audio data validation utility."""

    def __init__(self, config: SpeechAnalysisConfig) -> None:
        self.config = config

    async def validate_audio_data(self, audio_data: bytes) -> dict[str, Any]:
        """Validate audio data format and quality."""
        try:
            if not audio_data:
                return {"valid": False, "error": "Empty audio data provided"}
            if len(audio_data) < 1024:  # Minimum size check
                return {
                    "valid": False,
                    "error": "Audio data too small to analyze",
                }
            # Basic audio format validation (simplified for mock)
            estimated_duration = len(audio_data) / 44100 / 2  # Rough estimate
            if estimated_duration < self.config.min_audio_duration:
                return {
                    "valid": False,
                    "error": f"Audio too short (minimum {self.config.min_audio_duration}s)",
                }
            if estimated_duration > self.config.max_audio_duration:
                return {
                    "valid": False,
                    "error": f"Audio too long (maximum {self.config.max_audio_duration}s)",
                }
            return {
                "valid": True,
                "duration": estimated_duration,
                "size": len(audio_data),
            }
        except Exception as e:
            logger.error(f"Audio validation error: {e}")
            return {"valid": False, "error": f"Audio validation failed: {e!s}"}


class FeatureExtractor:
    """Audio feature extraction for speech analysis."""

    def __init__(self, config: SpeechAnalysisConfig) -> None:
        self.config = config

    async def extract_audio_features(self, audio_data: bytes) -> dict[str, Any]:
        """Extract features from audio data for analysis."""
        try:
            # Mock feature extraction (in real implementation would use librosa/pyaudio)
            features = {
                "spectral_features": {
                    "mfcc": [
                        1.2,
                        -0.8,
                        0.5,
                        2.1,
                        -1.3,
                    ],  # Mock MFCC coefficients
                    "spectral_centroid": 2500.0,
                    "zero_crossing_rate": 0.15,
                },
                "temporal_features": {
                    "duration": len(audio_data) / 44100 / 2,  # Estimated duration
                    "silence_ratio": 0.12,
                    "speech_rate": 4.5,  # syllables per second
                },
                "prosodic_features": {
                    "fundamental_frequency": 180.0,  # Hz
                    "intensity": 65.0,  # dB
                    "pitch_variation": 0.25,
                },
            }
            logger.info("Audio features extracted successfully")
            return features
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            return {"error": f"Feature extraction failed: {e!s}"}


def create_response_template() -> dict[str, Any]:
    """Create standard response template."""
    return {
        "analysis_timestamp": datetime.now().isoformat(),
        "disorders_detected": [],
        "confidence_scores": {},
        "recommendations": [],
        "severity_level": "normal",
        "professional_referral_needed": False,
        "analysis_quality": "good",
    }
