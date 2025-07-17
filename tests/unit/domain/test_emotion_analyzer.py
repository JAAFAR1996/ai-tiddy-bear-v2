"""
Unit tests for EmotionAnalyzer domain service.
Tests emotion detection and child safety features.
"""

import pytest
from src.domain.services.emotion_analyzer import EmotionAnalyzer, EmotionResult


class TestEmotionResult:
    """Test EmotionResult dataclass validation."""

    def test_valid_emotion_result(self):
        """Test creation of valid emotion result."""
        result = EmotionResult(
            primary_emotion="happy",
            confidence=0.9,
            all_emotions={"happy": 0.9, "neutral": 0.1},
            sentiment_score=0.8,
            arousal_score=0.7,
        )

        assert result.primary_emotion == "happy"
        assert result.confidence == 0.9
        assert result.sentiment_score == 0.8
        assert result.arousal_score == 0.7

    def test_confidence_validation(self):
        """Test confidence score validation."""
        # Test invalid confidence (> 1.0)
        with pytest.raises(
            ValueError, match="Confidence must be between 0.0 and 1.0"
        ):
            EmotionResult("happy", 1.5, {"happy": 0.9})

        # Test invalid confidence (< 0.0)
        with pytest.raises(
            ValueError, match="Confidence must be between 0.0 and 1.0"
        ):
            EmotionResult("happy", -0.1, {"happy": 0.9})

    def test_sentiment_validation(self):
        """Test sentiment score validation."""
        # Test invalid sentiment (> 1.0)
        with pytest.raises(
            ValueError, match="Sentiment score must be between -1.0 and 1.0"
        ):
            EmotionResult("happy", 0.9, {"happy": 0.9}, sentiment_score=1.5)

        # Test invalid sentiment (< -1.0)
        with pytest.raises(
            ValueError, match="Sentiment score must be between -1.0 and 1.0"
        ):
            EmotionResult("happy", 0.9, {"happy": 0.9}, sentiment_score=-1.5)

    def test_arousal_validation(self):
        """Test arousal score validation."""
        # Test invalid arousal (> 1.0)
        with pytest.raises(
            ValueError, match="Arousal score must be between 0.0 and 1.0"
        ):
            EmotionResult("happy", 0.9, {"happy": 0.9}, arousal_score=1.5)

        # Test invalid arousal (< 0.0)
        with pytest.raises(
            ValueError, match="Arousal score must be between 0.0 and 1.0"
        ):
            EmotionResult("happy", 0.9, {"happy": 0.9}, arousal_score=-0.1)


class TestEmotionAnalyzer:
    """Test EmotionAnalyzer functionality."""

    @pytest.fixture
    def analyzer(self):
        """Create EmotionAnalyzer instance for testing."""
        return EmotionAnalyzer()

    def test_initialization(self, analyzer):
        """Test analyzer initialization."""
        assert analyzer._positive_emotions == {
            "happy",
            "excited",
            "calm",
            "curious",
            "proud",
        }
        assert analyzer._negative_emotions == {
            "sad",
            "angry",
            "frustrated",
            "scared",
            "worried",
        }
        assert analyzer._neutral_emotions == {"neutral", "focused", "thinking"}

    def test_analyze_happy_text(self, analyzer):
        """Test analysis of happy text."""
        result = analyzer.analyze_text("I am so happy today!")

        assert result.primary_emotion == "happy"
        assert result.confidence == 0.9
        assert result.sentiment_score == 0.8
        assert "happy" in result.all_emotions

    def test_analyze_sad_text(self, analyzer):
        """Test analysis of sad text."""
        result = analyzer.analyze_text("I feel really sad and want to cry")

        assert result.primary_emotion == "sad"
        assert result.confidence == 0.8
        assert result.sentiment_score == -0.6
        assert "sad" in result.all_emotions

    def test_analyze_frustrated_text(self, analyzer):
        """Test analysis of frustrated text."""
        result = analyzer.analyze_text(
            "This makes me so angry and frustrated!"
        )

        assert result.primary_emotion == "frustrated"
        assert result.confidence == 0.7
        assert result.sentiment_score == -0.4
        assert result.arousal_score == 0.8

    def test_analyze_worried_text(self, analyzer):
        """Test analysis of worried text."""
        result = analyzer.analyze_text("I'm scared and worried about this")

        assert result.primary_emotion == "worried"
        assert result.confidence == 0.75
        assert result.sentiment_score == -0.5
        assert result.arousal_score == 0.6

    def test_analyze_calm_text(self, analyzer):
        """Test analysis of calm text."""
        result = analyzer.analyze_text("I feel peaceful and relaxed")

        assert result.primary_emotion == "calm"
        assert result.confidence == 0.8
        assert result.sentiment_score == 0.3
        assert result.arousal_score == 0.2

    def test_analyze_curious_text(self, analyzer):
        """Test analysis of curious text."""
        result = analyzer.analyze_text("I wonder how this works, I'm curious")

        assert result.primary_emotion == "curious"
        assert result.confidence == 0.7
        assert result.sentiment_score == 0.4
        assert result.arousal_score == 0.5

    def test_analyze_neutral_text(self, analyzer):
        """Test analysis of neutral text."""
        result = analyzer.analyze_text("The weather is nice today")

        assert result.primary_emotion == "neutral"
        assert result.confidence == 0.5
        assert result.sentiment_score == 0.0
        assert result.arousal_score == 0.3

    def test_analyze_empty_text(self, analyzer):
        """Test analysis of empty text."""
        result = analyzer.analyze_text("")

        assert result.primary_emotion == "neutral"
        assert result.confidence == 0.5

        result = analyzer.analyze_text("   ")
        assert result.primary_emotion == "neutral"

    def test_analyze_none_text(self, analyzer):
        """Test analysis of None text."""
        result = analyzer.analyze_text(None)

        assert result.primary_emotion == "neutral"
        assert result.confidence == 0.5

    def test_analyze_voice_with_features(self, analyzer):
        """Test voice analysis with audio features."""
        audio_features = {"pitch": 0.8, "energy": 0.7, "tempo": 0.6}

        result = analyzer.analyze_voice(audio_features)

        assert result.primary_emotion == "excited"
        assert result.confidence == 0.8
        assert result.sentiment_score == 0.7
        assert result.arousal_score == 0.9

    def test_analyze_voice_low_energy(self, analyzer):
        """Test voice analysis with low energy."""
        audio_features = {"pitch": 0.2, "energy": 0.3, "tempo": 0.4}

        result = analyzer.analyze_voice(audio_features)

        assert result.primary_emotion == "sad"
        assert result.confidence == 0.7
        assert result.sentiment_score == -0.5
        assert result.arousal_score == 0.3

    def test_analyze_voice_high_energy(self, analyzer):
        """Test voice analysis with high energy."""
        audio_features = {"pitch": 0.5, "energy": 0.9, "tempo": 0.7}

        result = analyzer.analyze_voice(audio_features)

        assert result.primary_emotion == "energetic"
        assert result.confidence == 0.75
        assert result.sentiment_score == 0.4
        assert result.arousal_score == 0.8

    def test_analyze_voice_no_features(self, analyzer):
        """Test voice analysis with no features."""
        result = analyzer.analyze_voice(None)

        assert result.primary_emotion == "neutral"
        assert result.confidence == 0.4

        result = analyzer.analyze_voice({})
        assert result.primary_emotion == "calm"

    def test_get_child_appropriate_emotions(self, analyzer):
        """Test getting child-appropriate emotion descriptions."""
        emotions = analyzer.get_child_appropriate_emotions()

        assert isinstance(emotions, dict)
        assert "happy" in emotions
        assert "sad" in emotions
        assert emotions["happy"] == "feeling joyful and cheerful"
        assert emotions["worried"] == "feeling concerned about something"

    def test_is_emotion_positive(self, analyzer):
        """Test positive emotion detection."""
        assert analyzer.is_emotion_positive("happy") is True
        assert analyzer.is_emotion_positive("excited") is True
        assert analyzer.is_emotion_positive("calm") is True
        assert analyzer.is_emotion_positive("curious") is True
        assert analyzer.is_emotion_positive("proud") is True

        assert analyzer.is_emotion_positive("sad") is False
        assert analyzer.is_emotion_positive("angry") is False
        assert analyzer.is_emotion_positive("frustrated") is False
        assert analyzer.is_emotion_positive("unknown") is False

    def test_requires_attention_negative_emotion(self, analyzer):
        """Test attention requirement for negative emotions."""
        result = EmotionResult("sad", 0.8, {"sad": 0.8}, sentiment_score=-0.5)
        assert analyzer.requires_attention(result) is True

        result = EmotionResult("frustrated", 0.9, {"frustrated": 0.9})
        assert analyzer.requires_attention(result) is True

    def test_requires_attention_low_confidence_negative(self, analyzer):
        """Test attention requirement for low confidence negative emotions."""
        result = EmotionResult("sad", 0.5, {"sad": 0.5}, sentiment_score=-0.5)
        assert analyzer.requires_attention(result) is False

    def test_requires_attention_very_low_sentiment(self, analyzer):
        """Test attention requirement for very low sentiment."""
        result = EmotionResult(
            "neutral", 0.6, {"neutral": 0.6}, sentiment_score=-0.8
        )
        assert analyzer.requires_attention(result) is True

    def test_requires_attention_high_arousal_negative_sentiment(
        self, analyzer
    ):
        """Test attention requirement for high arousal with negative sentiment."""
        result = EmotionResult(
            "excited",
            0.7,
            {"excited": 0.7},
            sentiment_score=-0.4,
            arousal_score=0.9,
        )
        assert analyzer.requires_attention(result) is True

    def test_requires_attention_positive_emotion(self, analyzer):
        """Test attention requirement for positive emotions."""
        result = EmotionResult(
            "happy", 0.9, {"happy": 0.9}, sentiment_score=0.8
        )
        assert analyzer.requires_attention(result) is False

        result = EmotionResult("calm", 0.8, {"calm": 0.8}, sentiment_score=0.3)
        assert analyzer.requires_attention(result) is False

    def test_case_insensitive_analysis(self, analyzer):
        """Test that text analysis is case insensitive."""
        result1 = analyzer.analyze_text("I am HAPPY")
        result2 = analyzer.analyze_text("i am happy")
        result3 = analyzer.analyze_text("I Am Happy")

        assert (
            result1.primary_emotion
            == result2.primary_emotion
            == result3.primary_emotion
        )
        assert result1.confidence == result2.confidence == result3.confidence

    def test_multiple_emotion_words(self, analyzer):
        """Test text with multiple emotion words."""
        # First matching emotion should win
        result = analyzer.analyze_text("I am happy but also a bit sad")
        assert (
            result.primary_emotion == "happy"
        )  # happy comes first in check order

    def test_emotion_confidence_ranges(self, analyzer):
        """Test that emotion confidence is within valid ranges."""
        test_texts = [
            "I am happy",
            "I feel sad",
            "This is frustrating",
            "I'm worried",
            "Feeling calm",
            "I wonder about this",
            "Normal day today",
        ]

        for text in test_texts:
            result = analyzer.analyze_text(text)
            assert 0.0 <= result.confidence <= 1.0
            assert -1.0 <= result.sentiment_score <= 1.0
            assert 0.0 <= result.arousal_score <= 1.0
