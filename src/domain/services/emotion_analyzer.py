"""Emotion Analyzer Service - Domain Layer
Provides emotion analysis functionality for child interactions
without external ML library dependencies.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class EmotionResult:
    """Result of emotion analysis with comprehensive emotion data."""

    primary_emotion: str
    confidence: float
    all_emotions: dict[str, float]
    sentiment_score: float = 0.0
    arousal_score: float = 0.0

    def __post_init__(self) -> None:
        """Validate emotion result data."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        if not -1.0 <= self.sentiment_score <= 1.0:
            raise ValueError("Sentiment score must be between -1.0 and 1.0")
        if not 0.0 <= self.arousal_score <= 1.0:
            raise ValueError("Arousal score must be between 0.0 and 1.0")


class EmotionAnalyzer:
    """Analyzes emotions from text and voice for child safety monitoring."""

    def __init__(self) -> None:
        """Initialize emotion analyzer with child-safe emotion categories."""
        self._positive_emotions = {"happy", "excited", "calm", "curious", "proud"}
        self._negative_emotions = {"sad", "angry", "frustrated", "scared", "worried"}
        self._neutral_emotions = {"neutral", "focused", "thinking"}

    def analyze_text(self, text: str) -> EmotionResult:
        """Analyze emotion from text input with child-appropriate detection.

        Args:
            text: Text input to analyze
        Returns:
            EmotionResult with detected emotion and confidence

        """
        if not isinstance(text, str) or not text.strip():
            return EmotionResult("neutral", 0.5, {"neutral": 0.5})

        text_lower = text.lower()
        # Enhanced emotion detection for children
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
                "calm",
                0.8,
                {"calm": 0.8},
                sentiment_score=0.3,
                arousal_score=0.2,
            )
        if any(word in text_lower for word in ["curious", "wonder", "question"]):
            return EmotionResult(
                "curious",
                0.7,
                {"curious": 0.7},
                sentiment_score=0.4,
                arousal_score=0.5,
            )
        return EmotionResult(
            "neutral",
            0.5,
            {"neutral": 0.5},
            sentiment_score=0.0,
            arousal_score=0.3,
        )

    def analyze_voice(self, audio_features: dict[str, Any] | None) -> EmotionResult:
        """Analyze emotion from voice audio features.

        Args:
            audio_features: Dictionary containing audio feature data
        Returns:
            EmotionResult with detected vocal emotion

        """
        if not audio_features:
            return EmotionResult("neutral", 0.4, {"neutral": 0.4})
        # Placeholder for advanced voice emotion analysis
        # In production, this would use audio processing libraries
        pitch = audio_features.get("pitch", 0.5)
        energy = audio_features.get("energy", 0.5)
        audio_features.get("tempo", 0.5)
        # Simple emotion detection based on audio features
        if pitch > 0.7 and energy > 0.6:
            return EmotionResult(
                "excited",
                0.8,
                {"excited": 0.8},
                sentiment_score=0.7,
                arousal_score=0.9,
            )
        if pitch < 0.3 and energy < 0.4:
            return EmotionResult(
                "sad",
                0.7,
                {"sad": 0.7},
                sentiment_score=-0.5,
                arousal_score=0.3,
            )
        if energy > 0.8:
            return EmotionResult(
                "energetic",
                0.75,
                {"energetic": 0.75},
                sentiment_score=0.4,
                arousal_score=0.8,
            )
        return EmotionResult(
            "calm",
            0.7,
            {"calm": 0.7},
            sentiment_score=0.2,
            arousal_score=0.3,
        )

    def get_child_appropriate_emotions(self) -> dict[str, str]:
        """Get mapping of emotions to child-friendly descriptions.

        Returns:
            Dictionary mapping emotion names to child-friendly descriptions

        """
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
        """Check if an emotion is considered positive for children.

        Args:
            emotion: Emotion name to check
        Returns:
            True if emotion is positive, False otherwise

        """
        return emotion in self._positive_emotions

    def requires_attention(self, emotion_result: EmotionResult) -> bool:
        """Determine if emotion result requires adult attention.

        Args:
            emotion_result: Emotion analysis result
        Returns:
            True if adult attention may be needed

        """
        # High confidence negative emotions may need attention
        if (
            emotion_result.primary_emotion in self._negative_emotions
            and emotion_result.confidence > 0.7
        ):
            return True
        # Very low sentiment scores may indicate distress
        if emotion_result.sentiment_score < -0.7:
            return True
        # Very high arousal with negative sentiment may indicate agitation
        return bool(emotion_result.arousal_score > 0.8 and emotion_result.sentiment_score < -0.3)
