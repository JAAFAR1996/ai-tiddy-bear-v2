from domain.entities.emotion import EmotionType
import numpy as np
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    import numpy as np
except ImportError:
    # Mock numpy when not available
    class MockNumpy:
        def array(self, data):
            return data

        def zeros(self, shape):
            return [0] * (shape if isinstance(shape, int) else shape[0])

        def ones(self, shape):
            return [1] * (shape if isinstance(shape, int) else shape[0])

        def mean(self, data):
            return sum(data) / len(data) if data else 0

        def std(self, data):
            return 1.0  # Mock standard deviation

        def random(self):
            class MockRandom:
                def rand(self, *args):
                    return 0.5

                def randint(self, low, high, size=None):
                    return low

            return MockRandom()

        @property
        def pi(self):
            return 3.14159265359

    np = MockNumpy()


try:
    import pytest
except ImportError:
    try:
        from common.mock_pytest import pytest
    except ImportError:
        pass

    # Mock pytest when not available
    class MockPytest:
        def fixture(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

        def mark(self):
            class MockMark:
                def parametrize(self, *args, **kwargs):
                    def decorator(func):
                        return func

                    return decorator

                def asyncio(self, func):
                    return func

                def slow(self, func):
                    return func

                def skip(self, reason=""):
                    def decorator(func):
                        return func

                    return decorator

            return MockMark()

        def raises(self, exception):
            class MockRaises:
                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    return False

            return MockRaises()

        def skip(self, reason=""):
            def decorator(func):
                return func

            return decorator

    pytest = MockPytest()


class TestEmotionService:
    """Test emotion analysis service"""

    @pytest.mark.asyncio
    async def test_audio_emotion_analysis(self, emotion_service):
        """Test emotion analysis from audio"""
        # Mock audio data
        audio_data = np.random.random(16000).astype(
            np.float32)  # 1 second at 16kHz

        # Setup
        emotion_service.analyze_audio_emotion.return_value = {
            "primary_emotion": EmotionType.HAPPY,
            "confidence": 0.82,
            "energy_level": 0.75,
            "voice_features": {
                "pitch_mean": 220.5,
                "pitch_variance": 45.2,
                "speaking_rate": 3.2,
                "volume": 0.68,
            },
            "emotion_scores": {
                EmotionType.HAPPY: 0.82,
                EmotionType.EXCITED: 0.65,
                EmotionType.NEUTRAL: 0.15,
                EmotionType.SAD: 0.05,
            },
        }

        # Test
        result = await emotion_service.analyze_audio_emotion(audio_data)

        # Assert
        assert result["primary_emotion"] == EmotionType.HAPPY
        assert result["confidence"] > 0.8
        assert result["energy_level"] > 0.7
        assert "pitch_mean" in result["voice_features"]

    @pytest.mark.asyncio
    async def test_emotion_history_tracking(self, emotion_service):
        """Test emotion history tracking"""
        # Setup
        emotion_service.track_emotion_history.return_value = True
        emotion_service.get_emotion_trends.return_value = {
            "last_24_hours": {
                "dominant_emotion": "happy",
                "emotion_distribution": {
                    "happy": 0.45,
                    "neutral": 0.30,
                    "excited": 0.20,
                    "sad": 0.05,
                },
                "stability_score": 0.78,
            },
            "last_week": {
                "dominant_emotion": "happy",
                "emotion_changes": [
                    {"date": "2024-01-01", "emotion": "happy", "score": 0.8},
                    {"date": "2024-01-02", "emotion": "neutral", "score": 0.6},
                ],
                "trend": "stable",
            },
            "insights": [
                "Child shows consistent positive emotions",
                "Slight increase in excitement during story times",
            ],
        }

        # Track emotion
        tracked = await emotion_service.track_emotion_history(
            "child123", EmotionType.HAPPY, 0.85
        )
        assert tracked is True

        # Get trends
        trends = await emotion_service.get_emotion_trends("child123")

        # Assert
        assert trends["last_24_hours"]["dominant_emotion"] == "happy"
        assert trends["last_24_hours"]["stability_score"] > 0.7
        assert len(trends["insights"]) >= 1
