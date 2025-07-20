from unittest.mock import patch
import os
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
    from application.services.voice_service import (
        AudioFormat,
        STTProvider,
        VoiceService,
        WhisperModel,
        create_voice_service,
    )
except ImportError:
    # Fallback for mock environment
    from src.application.services.transcription_service import TranscriptionResult
        AudioFormat,
        STTProvider,
        VoiceService,
        WhisperModel,
        create_voice_service,
    )


class TestVoiceServiceInitialization:
    """Test voice service initialization"""

    def test_service_creation_with_default_config(self):
        """Test creating service with default configuration"""
        service = VoiceService()

        assert service.config.default_provider == STTProvider.WHISPER
        assert service.config.whisper_model == WhisperModel.BASE
        assert service.config.max_audio_duration == 30
        assert AudioFormat.WAV in service.config.supported_formats

    def test_service_creation_with_custom_config(self, mock_config):
        """Test creating service with custom configuration"""
        service = VoiceService(mock_config)

        assert service.config.default_provider == STTProvider.WHISPER
        assert service.config.temp_dir == "./test_temp"
        assert service.config.enable_fallback is True

    def test_factory_function(self):
        """Test factory function creates service correctly"""
        with patch.dict(
            os.environ,
            {
                "STT_PROVIDER": "whisper",
                "WHISPER_MODEL": "small",
                "MAX_AUDIO_DURATION": "60",
            },
        ):
            service = create_voice_service()

            assert isinstance(service, VoiceService)
            assert service.config.whisper_model == WhisperModel.SMALL
            assert service.config.max_audio_duration == 60
