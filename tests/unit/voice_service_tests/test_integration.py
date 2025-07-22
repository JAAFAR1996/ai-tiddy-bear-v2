import base64
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

try:
    from application.services.voice_service import (
        AudioFormat,
        STTProvider,
        TranscriptionResult,
    )
except ImportError:
    # Fallback for mock environment
    from tests.unit.voice_service_tests.conftest import AudioFormat, STTProvider, TranscriptionResult


class TestVoiceServiceIntegration:
    """Integration tests for voice service components"""

    @pytest.mark.asyncio
    async def test_full_pipeline_with_mock_providers(
        self, voice_service, sample_wav_data
    ):
        """Test full audio processing pipeline"""
        audio_base64 = base64.b64encode(sample_wav_data).decode("utf-8")

        # Test the full pipeline
        result = await voice_service.transcribe_audio(
            audio_data=audio_base64,
            format=AudioFormat.WAV,
            language="ar",
            provider=STTProvider.WHISPER,  # Will fall back to mock if Whisper not available
        )

        assert isinstance(result, TranscriptionResult)
        assert len(result.text) > 0
        assert result.language == "ar"
        assert result.processing_time_ms > 0
        assert result.audio_duration_ms > 0
