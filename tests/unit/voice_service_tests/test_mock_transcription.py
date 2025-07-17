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


class TestMockTranscription:
    """Test mock transcription provider"""

    @pytest.mark.asyncio
    async def test_mock_transcription_returns_arabic_text(self, voice_service):
        """Test mock transcription returns appropriate Arabic text"""
        text, confidence, segments, metadata = await voice_service._transcribe_mock(
            b"test_audio", "ar"
        )

        assert isinstance(text, str)
        assert len(text) > 0
        assert 0.0 <= confidence <= 1.0
        assert isinstance(segments, list)
        assert metadata["provider"] == "mock"
        assert metadata["simulated"] is True

        # Should be Arabic text
        arabic_words = ["مرحباً", "دبدوب", "أريد", "احكِ", "أحبك", "ما"]
        assert any(word in text for word in arabic_words)
