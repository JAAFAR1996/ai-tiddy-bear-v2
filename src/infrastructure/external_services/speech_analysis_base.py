import io
from datetime import datetime
from typing import Any

import numpy as np

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
        """Validate audio data format and quality using librosa (production only)."""
        try:
            if not audio_data:
                return {"valid": False, "error": "Empty audio data provided"}
            if len(audio_data) < 1024:  # Minimum size check
                return {
                    "valid": False,
                    "error": "Audio data too small to analyze",
                }
            if not LIBROSA_AVAILABLE:
                logger.error("librosa not installed. Cannot validate audio data.")
                raise RuntimeError("librosa not installed. Please install librosa.")
            audio_buffer = io.BytesIO(audio_data)
            import librosa

            y, sr = librosa.load(audio_buffer, sr=None, mono=True)
            duration = librosa.get_duration(y=y, sr=sr)
            if duration < self.config.min_audio_duration:
                return {
                    "valid": False,
                    "error": f"Audio too short (minimum {self.config.min_audio_duration}s)",
                }
            if duration > self.config.max_audio_duration:
                return {
                    "valid": False,
                    "error": f"Audio too long (maximum {self.config.max_audio_duration}s)",
                }
            return {
                "valid": True,
                "duration": duration,
                "size": len(audio_data),
            }
        except Exception as e:
            logger.error(f"Audio validation error: {e}")
            return {"valid": False, "error": f"Audio validation failed: {e!s}"}


try:
    import librosa

    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False


class FeatureExtractor:
    """Audio feature extraction for speech analysis using librosa."""

    def __init__(self, config: SpeechAnalysisConfig) -> None:
        self.config = config

    async def extract_audio_features(self, audio_data: bytes) -> dict[str, Any]:
        """Extract features from audio data for analysis using librosa."""
        if not LIBROSA_AVAILABLE:
            logger.error("librosa not installed. Cannot extract audio features.")
            raise RuntimeError("librosa not installed. Please install librosa.")
        try:
            # Load audio from bytes
            audio_buffer = io.BytesIO(audio_data)
            y, sr = librosa.load(audio_buffer, sr=None, mono=True)
            duration = librosa.get_duration(y=y, sr=sr)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=5)
            mfcc_mean = np.mean(mfcc, axis=1).tolist()
            spectral_centroid = float(
                np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            )
            zero_crossing_rate = float(np.mean(librosa.feature.zero_crossing_rate(y)))
            # Estimate silence ratio
            rms = librosa.feature.rms(y=y)[0]
            silence_ratio = float(np.sum(rms < 0.01) / len(rms))
            # Estimate speech rate (very basic: number of zero crossings per second)
            speech_rate = zero_crossing_rate * sr
            # Prosodic features (basic)
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            fundamental_frequency = (
                float(np.mean(pitches[pitches > 0])) if np.any(pitches > 0) else 0.0
            )
            intensity = float(np.mean(librosa.feature.rms(y=y))) * 100
            pitch_variation = (
                float(np.std(pitches[pitches > 0])) if np.any(pitches > 0) else 0.0
            )

            features = {
                "spectral_features": {
                    "mfcc": mfcc_mean,
                    "spectral_centroid": spectral_centroid,
                    "zero_crossing_rate": zero_crossing_rate,
                },
                "temporal_features": {
                    "duration": duration,
                    "silence_ratio": silence_ratio,
                    "speech_rate": speech_rate,
                },
                "prosodic_features": {
                    "fundamental_frequency": fundamental_frequency,
                    "intensity": intensity,
                    "pitch_variation": pitch_variation,
                },
            }
            logger.info("Audio features extracted successfully using librosa.")
            return features
        except Exception:
            logger.exception("Feature extraction error")
            return {"error": "Feature extraction failed."}


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
