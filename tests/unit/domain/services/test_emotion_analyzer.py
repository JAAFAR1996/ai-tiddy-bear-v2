"""
Comprehensive tests for Emotion Analyzer Service
Tests emotion detection from text and voice for child safety monitoring.
"""

import pytest
from typing import Dict, Any

from src.domain.services.emotion_analyzer import EmotionAnalyzer, EmotionResult


class TestEmotionResult:
    """Test EmotionResult dataclass validation."""

    def test_valid_emotion_result(self):
        """Test creating valid emotion result."""
        result = EmotionResult(
            primary_emotion="happy",
            confidence=0.9,
            all_emotions={"happy": 0.9, "excited": 0.1},
            sentiment_score=0.8,
            arousal_score=0.6
        )
        assert result.primary_emotion == "happy"
        assert result.confidence == 0.9
        assert result.sentiment_score == 0.8
        assert result.arousal_score == 0.6

    def test_emotion_result_defaults(self):
        """Test emotion result with default values."""
        result = EmotionResult(
            primary_emotion="neutral",
            confidence=0.5,
            all_emotions={"neutral": 0.5}
        )
        assert result.sentiment_score == 0.0
        assert result.arousal_score == 0.0

    def test_invalid_confidence(self):
        """Test emotion result with invalid confidence."""
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            EmotionResult(
                primary_emotion="happy",
                confidence=1.5,
                all_emotions={"happy": 1.5}
            )

        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            EmotionResult(
                primary_emotion="happy",
                confidence=-0.1,
                all_emotions={"happy": -0.1}
            )

    def test_invalid_sentiment_score(self):
        """Test emotion result with invalid sentiment score."""
        with pytest.raises(ValueError, match="Sentiment score must be between -1.0 and 1.0"):
            EmotionResult(
                primary_emotion="happy",
                confidence=0.9,
                all_emotions={"happy": 0.9},
                sentiment_score=1.5
            )

        with pytest.raises(ValueError, match="Sentiment score must be between -1.0 and 1.0"):
            EmotionResult(
                primary_emotion="sad",
                confidence=0.9,
                all_emotions={"sad": 0.9},
                sentiment_score=-1.5
            )

    def test_invalid_arousal_score(self):
        """Test emotion result with invalid arousal score."""
        with pytest.raises(ValueError, match="Arousal score must be between 0.0 and 1.0"):
            EmotionResult(
                primary_emotion="excited",
                confidence=0.9,
                all_emotions={"excited": 0.9},
                arousal_score=1.5
            )

        with pytest.raises(ValueError, match="Arousal score must be between 0.0 and 1.0"):
            EmotionResult(
                primary_emotion="calm",
                confidence=0.9,
                all_emotions={"calm": 0.9},
                arousal_score=-0.1
            )


class TestEmotionAnalyzer:
    """Test suite for emotion analyzer functionality."""

    @pytest.fixture
    def analyzer(self):
        """Create emotion analyzer instance."""
        return EmotionAnalyzer()

    def test_initialization(self, analyzer):
        """Test analyzer initialization."""
        assert len(analyzer._positive_emotions) == 5
        assert len(analyzer._negative_emotions) == 5
        assert len(analyzer._neutral_emotions) == 3
        assert "happy" in analyzer._positive_emotions
        assert "sad" in analyzer._negative_emotions
        assert "neutral" in analyzer._neutral_emotions

    def test_analyze_text_empty(self, analyzer):
        """Test emotion analysis with empty text."""
        result = analyzer.analyze_text("")
        assert result.primary_emotion == "neutral"
        assert result.confidence == 0.5
        assert result.all_emotions == {"neutral": 0.5}

        result = analyzer.analyze_text("   ")
        assert result.primary_emotion == "neutral"
        assert result.confidence == 0.5

    def test_analyze_text_none(self, analyzer):
        """Test emotion analysis with None text."""
        result = analyzer.analyze_text(None)
        assert result.primary_emotion == "neutral"
        assert result.confidence == 0.5

    def test_analyze_text_happy_emotions(self, analyzer):
        """Test detection of happy emotions."""
        happy_texts = [
            "I'm so happy today!",
            "This is so much fun!",
            "Yay! I love this!",
            "I feel joyful",
            "I'm excited about tomorrow"
        ]

        for text in happy_texts:
            result = analyzer.analyze_text(text)
            assert result.primary_emotion == "happy"
            assert result.confidence == 0.9
            assert result.sentiment_score == 0.8
            assert "happy" in result.all_emotions

    def test_analyze_text_sad_emotions(self, analyzer):
        """Test detection of sad emotions."""
        sad_texts = [
            "I feel sad",
            "I want to cry",
            "I'm upset about this",
            "I feel down today"
        ]

        for text in sad_texts:
            result = analyzer.analyze_text(text)
            assert result.primary_emotion == "sad"
            assert result.confidence == 0.8
            assert result.sentiment_score == -0.6
            assert "sad" in result.all_emotions

    def test_analyze_text_frustrated_emotions(self, analyzer):
        """Test detection of frustrated emotions."""
        frustrated_texts = [
            "I'm so angry!",
            "This makes me mad",
            "I'm frustrated with this"
        ]

        for text in frustrated_texts:
            result = analyzer.analyze_text(text)
            assert result.primary_emotion == "frustrated"
            assert result.confidence == 0.7
            assert result.sentiment_score == -0.4
            assert result.arousal_score == 0.8
            assert "frustrated" in result.all_emotions

    def test_analyze_text_worried_emotions(self, analyzer):
        """Test detection of worried emotions."""
        worried_texts = [
            "I'm scared",
            "I feel afraid",
            "I'm worried about this"
        ]

        for text in worried_texts:
            result = analyzer.analyze_text(text)
            assert result.primary_emotion == "worried"
            assert result.confidence == 0.75
            assert result.sentiment_score == -0.5
            assert result.arousal_score == 0.6
            assert "worried" in result.all_emotions

    def test_analyze_text_calm_emotions(self, analyzer):
        """Test detection of calm emotions."""
        calm_texts = [
            "I feel calm",
            "Everything is peaceful",
            "I'm relaxed"
        ]

        for text in calm_texts:
            result = analyzer.analyze_text(text)
            assert result.primary_emotion == "calm"
            assert result.confidence == 0.8
            assert result.sentiment_score == 0.3
            assert result.arousal_score == 0.2
            assert "calm" in result.all_emotions

    def test_analyze_text_curious_emotions(self, analyzer):
        """Test detection of curious emotions."""
        curious_texts = [
            "I'm curious about this",
            "I wonder why",
            "I have a question"
        ]

        for text in curious_texts:
            result = analyzer.analyze_text(text)
            assert result.primary_emotion == "curious"
            assert result.confidence == 0.7
            assert result.sentiment_score == 0.4
            assert result.arousal_score == 0.5
            assert "curious" in result.all_emotions

    def test_analyze_text_neutral(self, analyzer):
        """Test neutral emotion detection."""
        neutral_texts = [
            "The sky is blue",
            "I went to school today",
            "This is a book"
        ]

        for text in neutral_texts:
            result = analyzer.analyze_text(text)
            assert result.primary_emotion == "neutral"
            assert result.confidence == 0.5
            assert result.sentiment_score == 0.0
            assert result.arousal_score == 0.3

    def test_analyze_text_case_insensitive(self, analyzer):
        """Test case insensitive emotion detection."""
        texts = [
            ("I'M SO HAPPY!", "happy"),
            ("i feel sad", "sad"),
            ("I AM ANGRY", "frustrated"),
            ("i'm ScArEd", "worried")
        ]

        for text, expected_emotion in texts:
            result = analyzer.analyze_text(text)
            assert result.primary_emotion == expected_emotion

    def test_analyze_voice_none(self, analyzer):
        """Test voice analysis with None features."""
        result = analyzer.analyze_voice(None)
        assert result.primary_emotion == "neutral"
        assert result.confidence == 0.4
        assert result.all_emotions == {"neutral": 0.4}

    def test_analyze_voice_empty(self, analyzer):
        """Test voice analysis with empty features."""
        result = analyzer.analyze_voice({})
        assert result.primary_emotion == "calm"
        assert result.confidence == 0.7
        assert result.sentiment_score == 0.2
        assert result.arousal_score == 0.3

    def test_analyze_voice_excited(self, analyzer):
        """Test voice analysis for excited emotion."""
        audio_features = {
            "pitch": 0.8,
            "energy": 0.7,
            "tempo": 0.6
        }
        result = analyzer.analyze_voice(audio_features)
        assert result.primary_emotion == "excited"
        assert result.confidence == 0.8
        assert result.sentiment_score == 0.7
        assert result.arousal_score == 0.9

    def test_analyze_voice_sad(self, analyzer):
        """Test voice analysis for sad emotion."""
        audio_features = {
            "pitch": 0.2,
            "energy": 0.3,
            "tempo": 0.4
        }
        result = analyzer.analyze_voice(audio_features)
        assert result.primary_emotion == "sad"
        assert result.confidence == 0.7
        assert result.sentiment_score == -0.5
        assert result.arousal_score == 0.3

    def test_analyze_voice_energetic(self, analyzer):
        """Test voice analysis for energetic emotion."""
        audio_features = {
            "pitch": 0.5,
            "energy": 0.9,
            "tempo": 0.7
        }
        result = analyzer.analyze_voice(audio_features)
        assert result.primary_emotion == "energetic"
        assert result.confidence == 0.75
        assert result.sentiment_score == 0.4
        assert result.arousal_score == 0.8

    def test_analyze_voice_calm(self, analyzer):
        """Test voice analysis for calm emotion."""
        audio_features = {
            "pitch": 0.5,
            "energy": 0.5,
            "tempo": 0.5
        }
        result = analyzer.analyze_voice(audio_features)
        assert result.primary_emotion == "calm"
        assert result.confidence == 0.7
        assert result.sentiment_score == 0.2
        assert result.arousal_score == 0.3

    def test_analyze_voice_default_values(self, analyzer):
        """Test voice analysis with missing feature values."""
        audio_features = {
            "pitch": 0.8  # Missing energy and tempo
        }
        result = analyzer.analyze_voice(audio_features)
        # Default values are 0.5, so won't trigger excited (needs high energy too)
        assert result.primary_emotion == "calm"

    def test_get_child_appropriate_emotions(self, analyzer):
        """Test getting child-appropriate emotion descriptions."""
        emotions = analyzer.get_child_appropriate_emotions()
        
        assert len(emotions) == 10
        assert "happy" in emotions
        assert "feeling joyful and cheerful" in emotions["happy"]
        assert "sad" in emotions
        assert "feeling down or upset" in emotions["sad"]
        assert "neutral" in emotions
        assert "feeling normal and okay" in emotions["neutral"]

    def test_is_emotion_positive(self, analyzer):
        """Test positive emotion identification."""
        positive_emotions = ["happy", "excited", "calm", "curious", "proud"]
        for emotion in positive_emotions:
            assert analyzer.is_emotion_positive(emotion) is True

        negative_emotions = ["sad", "angry", "frustrated", "scared", "worried"]
        for emotion in negative_emotions:
            assert analyzer.is_emotion_positive(emotion) is False

        # Test non-categorized emotions
        assert analyzer.is_emotion_positive("neutral") is False
        assert analyzer.is_emotion_positive("energetic") is False

    def test_requires_attention_high_confidence_negative(self, analyzer):
        """Test attention requirement for high confidence negative emotions."""
        # High confidence negative emotion
        emotion_result = EmotionResult(
            primary_emotion="sad",
            confidence=0.8,
            all_emotions={"sad": 0.8},
            sentiment_score=-0.5,
            arousal_score=0.3
        )
        assert analyzer.requires_attention(emotion_result) is True

        # Low confidence negative emotion
        emotion_result = EmotionResult(
            primary_emotion="sad",
            confidence=0.6,
            all_emotions={"sad": 0.6},
            sentiment_score=-0.3,
            arousal_score=0.3
        )
        assert analyzer.requires_attention(emotion_result) is False

    def test_requires_attention_very_low_sentiment(self, analyzer):
        """Test attention requirement for very low sentiment scores."""
        emotion_result = EmotionResult(
            primary_emotion="neutral",
            confidence=0.5,
            all_emotions={"neutral": 0.5},
            sentiment_score=-0.8,  # Very low
            arousal_score=0.5
        )
        assert analyzer.requires_attention(emotion_result) is True

    def test_requires_attention_high_arousal_negative_sentiment(self, analyzer):
        """Test attention requirement for high arousal with negative sentiment."""
        emotion_result = EmotionResult(
            primary_emotion="frustrated",
            confidence=0.6,
            all_emotions={"frustrated": 0.6},
            sentiment_score=-0.4,
            arousal_score=0.9  # Very high arousal
        )
        assert analyzer.requires_attention(emotion_result) is True

    def test_requires_attention_positive_emotion(self, analyzer):
        """Test that positive emotions don't require attention."""
        emotion_result = EmotionResult(
            primary_emotion="happy",
            confidence=0.9,
            all_emotions={"happy": 0.9},
            sentiment_score=0.8,
            arousal_score=0.7
        )
        assert analyzer.requires_attention(emotion_result) is False

    def test_requires_attention_edge_cases(self, analyzer):
        """Test edge cases for attention requirement."""
        # Exactly at threshold
        emotion_result = EmotionResult(
            primary_emotion="sad",
            confidence=0.7,  # Exactly at threshold
            all_emotions={"sad": 0.7},
            sentiment_score=-0.5,
            arousal_score=0.3
        )
        assert analyzer.requires_attention(emotion_result) is False

        # Multiple conditions met
        emotion_result = EmotionResult(
            primary_emotion="angry",
            confidence=0.9,
            all_emotions={"angry": 0.9},
            sentiment_score=-0.9,
            arousal_score=0.9
        )
        assert analyzer.requires_attention(emotion_result) is True

    def test_emotion_categories_consistency(self, analyzer):
        """Test that emotion categories are mutually exclusive."""
        all_emotions = (
            analyzer._positive_emotions |
            analyzer._negative_emotions |
            analyzer._neutral_emotions
        )
        
        # Check no emotion appears in multiple categories
        positive_negative_overlap = analyzer._positive_emotions & analyzer._negative_emotions
        positive_neutral_overlap = analyzer._positive_emotions & analyzer._neutral_emotions
        negative_neutral_overlap = analyzer._negative_emotions & analyzer._neutral_emotions
        
        assert len(positive_negative_overlap) == 0
        assert len(positive_neutral_overlap) == 0
        assert len(negative_neutral_overlap) == 0

    def test_text_analysis_priority(self, analyzer):
        """Test that first matching emotion keyword takes priority."""
        # Text with multiple emotion keywords
        text = "I'm happy but also sad"
        result = analyzer.analyze_text(text)
        # Should match "happy" first
        assert result.primary_emotion == "happy"
        assert result.sentiment_score == 0.8

    def test_voice_analysis_edge_values(self, analyzer):
        """Test voice analysis with edge case values."""
        # All features at maximum
        audio_features = {
            "pitch": 1.0,
            "energy": 1.0,
            "tempo": 1.0
        }
        result = analyzer.analyze_voice(audio_features)
        assert result.primary_emotion == "excited"

        # All features at minimum
        audio_features = {
            "pitch": 0.0,
            "energy": 0.0,
            "tempo": 0.0
        }
        result = analyzer.analyze_voice(audio_features)
        assert result.primary_emotion == "sad"

    def test_text_with_special_characters(self, analyzer):
        """Test text analysis with special characters."""
        texts = [
            "I'm happy! :)",
            "So sad... :(",
            "Really angry!!!",
            "Curious???",
        ]
        expected_emotions = ["happy", "sad", "frustrated", "curious"]

        for text, expected in zip(texts, expected_emotions):
            result = analyzer.analyze_text(text)
            assert result.primary_emotion == expected