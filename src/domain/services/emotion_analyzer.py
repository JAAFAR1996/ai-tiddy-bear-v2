import logging
from dataclasses import dataclass
from typing import Any, Dict

try:
    import librosa
    import numpy as np

    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

# Threshold constants
PITCH_EXCITED = 200
ENERGY_EXCITED = 0.1
PITCH_SAD = 120
ENERGY_SAD = 0.05
ENERGY_ENERGETIC = 0.15


@dataclass
class EmotionResult:
    """Result of emotion analysis with comprehensive emotion data."""

    primary_emotion: str
    confidence: float
    all_emotions: Dict[str, float]
    sentiment_score: float = 0.0
    arousal_score: float = 0.0

    def __post_init__(self):
        assert 0.0 <= self.confidence <= 1.0, "Confidence must be between 0.0 and 1.0"
        assert (
            -1.0 <= self.sentiment_score <= 1.0
        ), "Sentiment score must be between -1.0 and 1.0"
        assert (
            0.0 <= self.arousal_score <= 1.0
        ), "Arousal score must be between 0.0 and 1.0"


class EmotionAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger("emotion_analyzer")
        self._positive_emotions = {
            "happy",
            "excited",
            "calm",
            "curious",
            "proud",
            "energetic",
        }
        self._negative_emotions = {"sad", "frustrated", "worried"}

    def analyze_text(self, text: str) -> EmotionResult:
        if not isinstance(text, str) or not text.strip():
            return EmotionResult("neutral", 0.5, {"neutral": 0.5})

        text_lower = text.lower()
        if any(
            word in text_lower for word in ["happy", "joy", "excited", "fun", "yay"]
        ):
            return EmotionResult("happy", 0.9, {"happy": 0.9}, sentiment_score=0.8)
        if any(word in text_lower for word in ["sad", "cry", "upset", "down"]):
            return EmotionResult("sad", 0.8, {"sad": 0.8}, sentiment_score=-0.6)
        if any(word in text_lower for word in ["angry", "mad", "frustrated"]):
            return EmotionResult(
                "frustrated",
                0.7,
                {"frustrated": 0.7},
                sentiment_score=-0.4,
                arousal_score=0.8,
            )
        if any(word in text_lower for word in ["scared", "afraid", "worried"]):
            return EmotionResult(
                "worried",
                0.75,
                {"worried": 0.75},
                sentiment_score=-0.5,
                arousal_score=0.6,
            )
        if any(word in text_lower for word in ["calm", "peaceful", "relaxed"]):
            return EmotionResult(
                "calm", 0.8, {"calm": 0.8}, sentiment_score=0.3, arousal_score=0.2
            )
        if any(word in text_lower for word in ["curious", "wonder", "question"]):
            return EmotionResult(
                "curious", 0.7, {"curious": 0.7}, sentiment_score=0.4, arousal_score=0.5
            )
        return EmotionResult(
            "neutral", 0.5, {"neutral": 0.5}, sentiment_score=0.0, arousal_score=0.3
        )

    def analyze_voice(self, audio_features: dict[str, Any] | None) -> EmotionResult:
        if not audio_features or "audio_path" not in audio_features:
            self.logger.warning(
                "No audio_path provided to analyze_voice; returning neutral emotion result."
            )
            return EmotionResult("neutral", 0.4, {"neutral": 0.4})
        if not LIBROSA_AVAILABLE:
            self.logger.error(
                "librosa is not installed; cannot perform real voice emotion analysis."
            )
            return EmotionResult("neutral", 0.3, {"neutral": 0.3})
        try:
            audio_path = audio_features["audio_path"]
            y, sr = librosa.load(audio_path, sr=None)
            pitch = float(np.mean(librosa.yin(y, fmin=50, fmax=500, sr=sr)))
            energy = float(np.mean(librosa.feature.rms(y=y)))
            # Optionally add tempo analysis here
            if pitch > PITCH_EXCITED and energy > ENERGY_EXCITED:
                return EmotionResult(
                    "excited",
                    0.85,
                    {"excited": 0.85},
                    sentiment_score=0.7,
                    arousal_score=0.9,
                )
            if pitch < PITCH_SAD and energy < ENERGY_SAD:
                return EmotionResult(
                    "sad", 0.8, {"sad": 0.8}, sentiment_score=-0.6, arousal_score=0.3
                )
            if energy > ENERGY_ENERGETIC:
                return EmotionResult(
                    "energetic",
                    0.8,
                    {"energetic": 0.8},
                    sentiment_score=0.5,
                    arousal_score=0.8,
                )
            return EmotionResult(
                "calm", 0.7, {"calm": 0.7}, sentiment_score=0.2, arousal_score=0.3
            )
        except Exception as e:
            self.logger.error(f"Voice emotion analysis failed: {e}", exc_info=True)
            return EmotionResult("neutral", 0.3, {"neutral": 0.3})

    def get_child_appropriate_emotions(self) -> dict[str, str]:
        return {
            "happy": "feeling joyful and cheerful",
            "excited": "feeling energetic and enthusiastic",
            "calm": "feeling peaceful and relaxed",
            "curious": "feeling interested and wondering",
            "sad": "feeling down or upset",
            "frustrated": "feeling a bit annoyed",
            "worried": "feeling concerned about something",
            "neutral": "feeling normal and okay",
            "proud": "feeling good about an achievement",
            "energetic": "feeling full of energy",
        }

    def is_emotion_positive(self, emotion: str) -> bool:
        return emotion in self._positive_emotions

    def requires_attention(self, emotion_result: EmotionResult) -> bool:
        if (
            emotion_result.primary_emotion in self._negative_emotions
            and emotion_result.confidence > 0.7
        ):
            return True
        if emotion_result.sentiment_score < -0.7:
            return True
        return bool(
            emotion_result.arousal_score > 0.8 and emotion_result.sentiment_score < -0.3
        )
