from unittest.mock import Mock, patch
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
    from application.services.voice_service import AudioFormat
except ImportError:
    # Fallback for mock environment
    from 1st import AudioFormat


class TestAudioFormatHandling:
    """Test audio format conversion and handling"""

    @pytest.mark.asyncio
    async def test_wav_duration_calculation(
            self, voice_service, sample_wav_data):
        """Test WAV duration calculation"""
        duration = voice_service._get_wav_duration(sample_wav_data)

        # Should be approximately 1 second
        assert 0.9 <= duration <= 1.1

    @pytest.mark.asyncio
    async def test_wav_passthrough(self, voice_service, sample_wav_data):
        """Test WAV audio passes through without conversion"""
        wav_data, duration = await voice_service._convert_to_wav(
            sample_wav_data, AudioFormat.WAV
        )

        assert wav_data == sample_wav_data
        assert 0.9 <= duration <= 1.1

    @pytest.mark.asyncio
    @patch("src.application.services.voice_service.PYDUB_AVAILABLE", True)
    async def test_mp3_to_wav_conversion_with_pydub(
        self, voice_service, sample_mp3_data
    ):
        """Test MP3 to WAV conversion using pydub"""
        with patch("src.application.services.voice_service.AudioSegment") as mock_audio:
            # Mock pydub conversion
            mock_segment = Mock()
            mock_segment.set_frame_rate.return_value = mock_segment
            mock_segment.set_channels.return_value = mock_segment
            mock_segment.set_sample_width.return_value = mock_segment
            mock_segment.__len__.return_value = 1000  # 1 second in ms

            mock_audio.from_file.return_value = mock_segment
            mock_segment.export.return_value = None

            # Mock the WAV export
            with patch("builtins.open", create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.getvalue.return_value = (
                    b"wav_data"
                )

                unused_wav_data, duration = await voice_service._convert_with_pydub(
                    sample_mp3_data, AudioFormat.MP3
                )

                assert duration == 1.0
                mock_audio.from_file.assert_called_once()
