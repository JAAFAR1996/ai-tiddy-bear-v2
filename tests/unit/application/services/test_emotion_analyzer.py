"""
Tests for Emotion Analyzer Service
Testing emotion analysis from text and multimodal inputs.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from src.application.services.emotion_analyzer import EmotionAnalyzer, EmotionResult


class TestEmotionAnalyzer:
    """Test the Emotion Analyzer Service."""

    @pytest.fixture
    def service(self):
        """Create an emotion analyzer instance."""
        return EmotionAnalyzer()

    def test_initialization_no_args(self):
        """Test service initialization without arguments."""
        service = EmotionAnalyzer()
        assert isinstance(service, EmotionAnalyzer)

    def test_initialization_with_args(self):
        """Test service initialization with various arguments."""
        # Should accept any arguments
        service1 = EmotionAnalyzer("arg1", "arg2")
        assert isinstance(service1, EmotionAnalyzer)

        service2 = EmotionAnalyzer(config={"key": "value"}, debug=True)
        assert isinstance(service2, EmotionAnalyzer)

    @pytest.mark.asyncio
    async def test_analyze_text_returns_emotion_result(self, service):
        """Test that analyze_text returns an EmotionResult."""
        # Arrange
        text = "I am so happy today!"

        # Act
        result = await service.analyze_text(text)

        # Assert
        assert isinstance(result, EmotionResult)
        assert hasattr(result, "primary_emotion")
        assert hasattr(result, "confidence")
        assert hasattr(result, "emotion_scores")
        assert hasattr(result, "arousal")
        assert hasattr(result, "valence")

    @pytest.mark.asyncio
    async def test_analyze_text_default_values(self, service):
        """Test default values returned by analyze_text."""
        # Arrange
        text = "Test text"

        # Act
        result = await service.analyze_text(text)

        # Assert - current implementation returns default values
        assert result.primary_emotion == "neutral"
        assert result.confidence == 0.5
        assert result.emotion_scores == {}
        assert result.arousal == 0.0
        assert result.valence == 0.0

    @pytest.mark.asyncio
    async def test_analyze_text_empty_string(self, service):
        """Test analyzing empty text."""
        # Act
        result = await service.analyze_text("")

        # Assert - should handle gracefully
        assert isinstance(result, EmotionResult)
        assert result.primary_emotion == "neutral"

    @pytest.mark.asyncio
    async def test_analyze_text_long_text(self, service):
        """Test analyzing very long text."""
        # Arrange
        long_text = "This is a very long text. " * 1000

        # Act
        result = await service.analyze_text(long_text)

        # Assert - should handle gracefully
        assert isinstance(result, EmotionResult)

    @pytest.mark.asyncio
    async def test_analyze_text_special_characters(self, service):
        """Test analyzing text with special characters."""
        # Arrange
        special_texts = [
            "I'm so happy! 😊",
            "This is amazing!!! ❤️❤️❤️",
            "¿Cómo estás? 🤔",
            "Hello\nWorld\tTab",
            "Special chars: @#$%^&*()",
        ]

        for text in special_texts:
            # Act
            result = await service.analyze_text(text)

            # Assert
            assert isinstance(result, EmotionResult)

    @pytest.mark.asyncio
    async def test_analyze_multimodal_returns_dict(self, service):
        """Test that analyze_multimodal returns a dictionary."""
        # Arrange
        text = "Hello, how are you?"
        audio_data = b"fake_audio_data"
        context = {"session_id": "123", "child_age": 8}

        # Act
        result = await service.analyze_multimodal(text, audio_data, context)

        # Assert
        assert isinstance(result, dict)
        assert "primary" in result
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_analyze_multimodal_default_values(self, service):
        """Test default values returned by analyze_multimodal."""
        # Arrange
        text = "Test"
        audio_data = b"audio"
        context = {}

        # Act
        result = await service.analyze_multimodal(text, audio_data, context)

        # Assert
        assert result["primary"] == "neutral"
        assert result["confidence"] == 0.5

    @pytest.mark.asyncio
    async def test_analyze_multimodal_empty_inputs(self, service):
        """Test multimodal analysis with empty inputs."""
        # Act
        result = await service.analyze_multimodal("", b"", {})

        # Assert
        assert isinstance(result, dict)
        assert result["primary"] == "neutral"

    @pytest.mark.asyncio
    async def test_analyze_multimodal_large_audio(self, service):
        """Test multimodal analysis with large audio data."""
        # Arrange
        text = "Testing with large audio"
        large_audio = b"x" * 10 * 1024 * 1024  # 10MB of audio data
        context = {"quality": "high"}

        # Act
        result = await service.analyze_multimodal(text, large_audio, context)

        # Assert
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_analyze_multimodal_complex_context(self, service):
        """Test multimodal analysis with complex context."""
        # Arrange
        text = "I'm feeling great!"
        audio_data = b"audio_sample"
        complex_context = {
            "session_id": "abc-123",
            "child_id": "child-456",
            "timestamp": "2024-01-15T10:30:00Z",
            "previous_emotions": ["happy", "excited"],
            "interaction_count": 5,
            "metadata": {
                "device": "teddy_bear_v2",
                "location": "bedroom",
                "volume_level": 0.7,
            },
        }

        # Act
        result = await service.analyze_multimodal(text, audio_data, complex_context)

        # Assert
        assert isinstance(result, dict)
        assert "primary" in result
        assert "confidence" in result

    def test_map_emotion_to_voice_with_emotion_result(self, service):
        """Test mapping emotion result to voice."""
        # Arrange
        emotion_results = [
            EmotionResult(
                "happy", 0.9, {
                    "happy": 0.9, "neutral": 0.1}, 0.8, 0.7),
            EmotionResult(
                "sad", 0.8, {
                    "sad": 0.8, "neutral": 0.2}, -0.5, -0.6),
            EmotionResult(
                "angry", 0.85, {
                    "angry": 0.85, "neutral": 0.15}, 0.9, -0.8),
            EmotionResult(
                "neutral", 0.6, {
                    "neutral": 0.6, "happy": 0.4}, 0.0, 0.0),
        ]

        for emotion_result in emotion_results:
            # Act
            voice = service.map_emotion_to_voice(emotion_result)

            # Assert
            assert isinstance(voice, str)
            assert voice == "neutral"  # Current implementation always returns "neutral"

    def test_map_emotion_to_voice_edge_cases(self, service):
        """Test voice mapping with edge case emotion results."""
        # Arrange
        edge_cases = [
            # Very low confidence
            EmotionResult("happy", 0.1, {}, 0.0, 0.0),
            # Very high arousal and valence
            EmotionResult("excited", 1.0, {"excited": 1.0}, 1.0, 1.0),
            # Negative arousal and valence
            EmotionResult("depressed", 0.7, {"depressed": 0.7}, -1.0, -1.0),
            # Mixed emotions
            EmotionResult(
                "confused", 0.5, {
                    "happy": 0.3, "sad": 0.3, "confused": 0.4}, 0.2, -0.1
            ),
        ]

        for emotion_result in edge_cases:
            # Act
            voice = service.map_emotion_to_voice(emotion_result)

            # Assert
            assert isinstance(voice, str)

    def test_emotion_result_dataclass(self):
        """Test EmotionResult dataclass functionality."""
        # Test creation
        result = EmotionResult(
            primary_emotion="happy",
            confidence=0.85,
            emotion_scores={"happy": 0.85, "neutral": 0.15},
            arousal=0.7,
            valence=0.8,
        )

        # Test attributes
        assert result.primary_emotion == "happy"
        assert result.confidence == 0.85
        assert result.emotion_scores == {"happy": 0.85, "neutral": 0.15}
        assert result.arousal == 0.7
        assert result.valence == 0.8

        # Test immutability (dataclass default)
        with pytest.raises(AttributeError):
            result.primary_emotion = "sad"

    @pytest.mark.asyncio
    async def test_analyze_text_various_emotions(self, service):
        """Test text analysis with various emotional texts."""
        # Note: Current implementation returns fixed values,
        # but we test the interface for future implementations
        emotional_texts = {
            "happy": "I'm so happy and excited about this!",
            "sad": "I feel really sad and lonely today.",
            "angry": "This makes me so angry and frustrated!",
            "fear": "I'm scared and worried about what might happen.",
            "surprise": "Wow! I can't believe this happened!",
            "disgust": "This is gross and disgusting.",
            "neutral": "The weather is cloudy today.",
        }

        for emotion, text in emotional_texts.items():
            # Act
            result = await service.analyze_text(text)

            # Assert
            assert isinstance(result, EmotionResult)
            # In a real implementation, we might check:
            # assert result.primary_emotion == emotion

    @pytest.mark.asyncio
    async def test_concurrent_analysis(self, service):
        """Test concurrent emotion analysis."""
        import asyncio

        # Arrange
        texts = [f"Text {i}" for i in range(10)]

        # Act - analyze multiple texts concurrently
        tasks = [service.analyze_text(text) for text in texts]
        results = await asyncio.gather(*tasks)

        # Assert
        assert len(results) == 10
        assert all(isinstance(r, EmotionResult) for r in results)

    @pytest.mark.asyncio
    async def test_analyze_multimodal_different_audio_formats(self, service):
        """Test multimodal analysis with different audio data formats."""
        # Arrange
        text = "Testing audio"
        audio_formats = [
            b"",  # Empty audio
            b"RIFF",  # WAV header
            b"\xff\xfb",  # MP3 header
            b"OggS",  # OGG header
            bytes([i for i in range(256)]),  # All byte values
        ]

        for audio_data in audio_formats:
            # Act
            result = await service.analyze_multimodal(text, audio_data, {})

            # Assert
            assert isinstance(result, dict)

    def test_map_emotion_to_voice_all_basic_emotions(self, service):
        """Test voice mapping for all basic emotions."""
        basic_emotions = [
            "anger",
            "anticipation",
            "disgust",
            "fear",
            "joy",
            "sadness",
            "surprise",
            "trust",
        ]

        for emotion in basic_emotions:
            emotion_result = EmotionResult(
                primary_emotion=emotion,
                confidence=0.8,
                emotion_scores={emotion: 0.8, "neutral": 0.2},
                arousal=0.5,
                valence=0.5,
            )

            voice = service.map_emotion_to_voice(emotion_result)

            assert isinstance(voice, str)
            # In a real implementation, might return emotion-specific voices

    @pytest.mark.parametrize("confidence", [0.0, 0.1, 0.5, 0.9, 1.0])
    def test_map_emotion_to_voice_different_confidences(
            self, service, confidence):
        """Test voice mapping with different confidence levels."""
        emotion_result = EmotionResult(
            primary_emotion="happy",
            confidence=confidence,
            emotion_scores={"happy": confidence},
            arousal=0.5,
            valence=0.5,
        )

        voice = service.map_emotion_to_voice(emotion_result)

        assert isinstance(voice, str)

    @pytest.mark.parametrize(
        "arousal,valence",
        [
            (-1.0, -1.0),  # Low arousal, low valence (sad, depressed)
            (-1.0, 1.0),  # Low arousal, high valence (calm, relaxed)
            (1.0, -1.0),  # High arousal, low valence (angry, stressed)
            (1.0, 1.0),  # High arousal, high valence (excited, happy)
            (0.0, 0.0),  # Neutral
        ],
    )
    def test_map_emotion_to_voice_arousal_valence_combinations(
        self, service, arousal, valence
    ):
        """Test voice mapping with different arousal/valence combinations."""
        emotion_result = EmotionResult(
            primary_emotion="dynamic",
            confidence=0.8,
            emotion_scores={},
            arousal=arousal,
            valence=valence,
        )

        voice = service.map_emotion_to_voice(emotion_result)

        assert isinstance(voice, str)
