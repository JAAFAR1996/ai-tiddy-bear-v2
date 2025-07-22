from unittest.mock import patch
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
        AudioRequest,
        TranscriptionResult,
    )
except ImportError:
    # Fallback for mock environment
    from tests.unit.voice_service_tests.conftest import AudioFormat, AudioRequest, TranscriptionResult


class TestESP32AudioProcessing:
    """Test ESP32-specific audio processing"""

    @pytest.mark.asyncio
    async def test_process_esp32_audio_request(
        self, voice_service, sample_audio_request
    ):
        """Test processing ESP32 audio request"""
        with patch.object(voice_service, "transcribe_audio") as mock_transcribe:
            mock_result = TranscriptionResult(
                text="مرحباً يا أحمد",
                language="ar",
                confidence=0.9,
                provider="whisper",
                processing_time_ms=500,
                audio_duration_ms=2000,
                segments=[],
                metadata={},
            )
            mock_transcribe.return_value = mock_result

            result = await voice_service.process_esp32_audio(sample_audio_request)

            assert result.text == "مرحباً يا أحمد"
            assert result.metadata["device_id"] == "TEST_ESP32_001"
            assert result.metadata["child_name"] == "أحمد"
            assert result.metadata["child_age"] == 6
            assert result.metadata["source"] == "esp32"

    @pytest.mark.asyncio
    async def test_esp32_audio_with_mp3_format(self, voice_service):
        """Test ESP32 audio processing with MP3 format"""
        mp3_request = AudioRequest(
            audio_data="bXAzIGF1ZGlvIGRhdGE=",  # "mp3 audio data" in base64
            format=AudioFormat.MP3,
            device_id="ESP32_MP3_001",
            language="ar",
        )

        with patch.object(voice_service, "transcribe_audio") as mock_transcribe:
            mock_result = TranscriptionResult(
                text="تم استلام الصوت المضغوط",
                language="ar",
                confidence=0.8,
                provider="whisper",
                processing_time_ms=300,
                audio_duration_ms=1500,
                segments=[],
                metadata={},
            )
            mock_transcribe.return_value = mock_result

            result = await voice_service.process_esp32_audio(mp3_request)

            assert result.metadata["source"] == "esp32"
            assert result.text == "تم استلام الصوت المضغوط"
