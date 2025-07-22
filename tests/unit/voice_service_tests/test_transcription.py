from unittest.mock import patch
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
        TranscriptionResult,
    )
except ImportError:
    # Fallback for mock environment
    from tests.unit.voice_service_tests.conftest import AudioFormat, TranscriptionResult


class TestTranscriptionFunctionality:
    """Test core transcription functionality"""

    @pytest.mark.asyncio
    async def test_transcribe_audio_with_base64_input(
        self, voice_service, sample_wav_data
    ):
        """Test transcription with base64 encoded audio"""
        # Encode audio to base64
        audio_base64 = base64.b64encode(sample_wav_data).decode("utf-8")

        # Mock the transcription provider
        with patch.object(
            voice_service, "_transcribe_with_provider"
        ) as mock_transcribe:
            mock_transcribe.return_value = (
                "مرحباً دبدوب", 0.9, [], {"test": True})

            result = await voice_service.transcribe_audio(
                audio_data=audio_base64, format=AudioFormat.WAV, language="ar"
            )

            assert isinstance(result, TranscriptionResult)
            assert result.text == "مرحباً دبدوب"
            assert result.confidence == 0.9
            assert result.language == "ar"
            assert result.provider in ["whisper", "fallback"]

    @pytest.mark.asyncio
    async def test_transcribe_audio_with_bytes_input(
        self, voice_service, sample_wav_data
    ):
        """Test transcription with raw bytes"""
        with patch.object(
            voice_service, "_transcribe_with_provider"
        ) as mock_transcribe:
            mock_transcribe.return_value = ("أهلاً وسهلاً", 0.85, [], {})

            result = await voice_service.transcribe_audio(
                audio_data=sample_wav_data, format=AudioFormat.WAV, language="ar"
            )

            assert result.text == "أهلاً وسهلاً"
            assert result.confidence == 0.85

    @pytest.mark.asyncio
    async def test_transcribe_empty_audio_returns_fallback(
            self, voice_service):
        """Test transcription with empty audio returns fallback"""
        result = await voice_service.transcribe_audio(
            audio_data=b"", format=AudioFormat.WAV
        )

        assert result.text == "مرحباً دبدوب"  # Fallback text
        assert result.confidence == 0.0
        assert result.provider == "fallback"
        assert "error" in result.metadata

    @pytest.mark.asyncio
    async def test_transcribe_invalid_base64_returns_fallback(
            self, voice_service):
        """Test transcription with invalid base64 returns fallback"""
        result = await voice_service.transcribe_audio(
            audio_data="invalid_base64_!@#$", format=AudioFormat.WAV
        )

        assert result.provider == "fallback"
        assert "error" in result.metadata

    @pytest.mark.asyncio
    async def test_transcribe_audio_too_long_raises_error(self, voice_service):
        """Test transcription fails for audio exceeding duration limit"""
        # Mock a very long audio duration
        with patch.object(voice_service, "_convert_to_wav") as mock_convert:
            mock_convert.return_value = (b"wav_data", 60.0)  # 60 seconds

            result = await voice_service.transcribe_audio(
                audio_data=b"test_data", format=AudioFormat.WAV
            )

            # Should return fallback due to duration error
            assert result.provider == "fallback"
            assert "error" in result.metadata
