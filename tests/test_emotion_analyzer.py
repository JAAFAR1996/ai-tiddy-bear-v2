"""Test emotion analysis service"""

import sys
from pathlib import Path

from domain.services.emotion_analyzer import EmotionAnalyzer, EmotionResult

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import after path setup

# Import numpy with fallback
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


class TestEmotionAnalyzer:
    """Test emotion analysis service"""

    def setup_method(self):
        """Setup test fixtures"""
        self.analyzer = EmotionAnalyzer()

    def test_analyze_happy_text(self):
        """Test analyzing happy text"""
        result = self.analyzer.analyze_text("I am so happy and joyful today!")

        assert result.primary_emotion == "happy"
        assert result.confidence > 0.5
        assert "happy" in result.all_emotions

    def test_analyze_sad_text(self):
        """Test analyzing sad text"""
        result = self.analyzer.analyze_text("I feel sad and want to cry")

        assert result.primary_emotion == "sad"
        assert result.confidence > 0.5

    def test_analyze_neutral_text(self):
        """Test analyzing neutral text"""
        result = self.analyzer.analyze_text("The weather is nice today")

        assert result.primary_emotion == "calm"
        assert isinstance(result.all_emotions, dict)

    def test_analyze_voice_features(self):
        """Test voice emotion analysis"""
        # Mock audio features
        audio_features = np.array([0.1, 0.2, 0.3, 0.4])

        result = self.analyzer.analyze_voice(audio_features)

        assert isinstance(result, EmotionResult)
        assert result.primary_emotion in [
            "happy",
            "sad",
            "angry",
            "excited",
            "calm",
        ]
        assert 0 <= result.confidence <= 1
