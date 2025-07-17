"""
Tests for AI Transcription Service Module
Testing production-grade audio transcription with child safety filtering.
"""

import pytest
from unittest.mock import Mock, patch
import tempfile
import os
import asyncio

from src.application.services.ai.modules.transcription_service import (
    TranscriptionService,
)


class TestTranscriptionService:
    """Test the AI Transcription Service."""

    @pytest.fixture
    def service_with_engines(self):
        """Create transcription service with mocked engines."""
        with patch(
            "src.application.services.ai.modules.transcription_service.SPEECH_RECOGNITION_AVAILABLE",
            True,
        ):
            with patch(
                "src.application.services.ai.modules.transcription_service.AUDIO_PROCESSING_AVAILABLE",
                True,
            ):
                with patch(
                    "src.application.services.ai.modules.transcription_service.whisper"
                ) as mock_whisper:
                    with patch(
                        "src.application.services.ai.modules.transcription_service.sr"
                    ) as mock_sr:
                        mock_whisper.load_model.return_value = Mock()
                        mock_sr.Recognizer.return_value = Mock()

                        service = TranscriptionService(
                            model_size="base", language_default="ar"
                        )
                        return service

    @pytest.fixture
    def service_without_engines(self):
        """Create transcription service without speech recognition engines."""
        with patch(
            "src.application.services.ai.modules.transcription_service.SPEECH_RECOGNITION_AVAILABLE",
            False,
        ):
            with patch(
                "src.application.services.ai.modules.transcription_service.AUDIO_PROCESSING_AVAILABLE",
                False,
            ):
                return TranscriptionService()

    @pytest.fixture
    def sample_audio_data(self):
        """Create sample audio data for testing."""
        # Create minimal WAV header + some data
        wav_header = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x08\x00data\x00\x00\x00\x00"
        audio_samples = b"\x00" * 100  # Simple audio data
        return wav_header + audio_samples

    def test_initialization_with_engines(self, service_with_engines):
        """Test service initialization with speech recognition engines."""
        assert service_with_engines.model_size == "base"
        assert service_with_engines.language_default == "ar"
        assert service_with_engines.max_audio_duration == 300
        assert service_with_engines.max_audio_size == 25 * 1024 * 1024
        assert "ar" in service_with_engines.supported_languages
        assert "en" in service_with_engines.supported_languages
        assert service_with_engines.content_filter_enabled is True
        assert service_with_engines.whisper_model is not None
        assert service_with_engines.google_recognizer is not None

    def test_initialization_without_engines(self, service_without_engines):
        """Test service initialization without speech recognition engines."""
        assert service_without_engines.whisper_model is None
        assert service_without_engines.google_recognizer is None
        assert service_without_engines.content_filter_enabled is True
        assert service_without_engines.supported_languages == [
            "ar",
            "en",
            "fr",
            "es",
        ]

    def test_unsafe_patterns_configuration(self, service_with_engines):
        """Test that unsafe patterns are properly configured."""
        expected_patterns = [
            r"\b(?:password|secret|address|phone)\b",
            r"\b(?:meet\s+me|where\s+do\s+you\s+live)\b",
            r"\b(?:send\s+photo|personal\s+information)\b",
            r"\b(?:credit\s+card|bank\s+account)\b",
        ]

        for pattern in expected_patterns:
            assert pattern in service_with_engines.unsafe_patterns

    @pytest.mark.asyncio
    async def test_transcribe_audio_invalid_input(self, service_with_engines):
        """Test transcription with invalid input."""
        # None input
        with pytest.raises(ValueError, match="Valid audio data required"):
            await service_with_engines.transcribe_audio(None)

        # Non-bytes input
        with pytest.raises(ValueError, match="Valid audio data required"):
            await service_with_engines.transcribe_audio("not bytes")

        # Empty bytes
        with pytest.raises(ValueError, match="Valid audio data required"):
            await service_with_engines.transcribe_audio(b"")

    @pytest.mark.asyncio
    async def test_transcribe_audio_too_large(self, service_with_engines):
        """Test transcription with audio data that's too large."""
        large_audio = b"x" * (service_with_engines.max_audio_size + 1)

        with pytest.raises(ValueError, match="Audio too large"):
            await service_with_engines.transcribe_audio(large_audio)

    @pytest.mark.asyncio
    async def test_transcribe_audio_unsupported_language(
        self, service_with_engines, sample_audio_data
    ):
        """Test transcription with unsupported language."""
        with patch.object(
            service_with_engines, "_validate_audio_file"
        ) as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "duration": 5.0,
                "error": None,
            }

            with patch.object(
                service_with_engines, "_perform_transcription"
            ) as mock_transcribe:
                mock_transcribe.return_value = {
                    "text": "transcribed text",
                    "confidence": 0.8,
                    "engine": "whisper",
                }

                with patch.object(
                    service_with_engines, "_apply_safety_filters"
                ) as mock_filter:
                    mock_filter.return_value = {
                        "text": "transcribed text",
                        "safe": True,
                        "warnings": [],
                    }

                    result = await service_with_engines.transcribe_audio(
                        sample_audio_data,
                        language="unsupported",
                        child_id="child_123",
                    )

                    assert result["success"] is True
                    # Should default to Arabic
                    assert result["language"] == "ar"

    @pytest.mark.asyncio
    async def test_transcribe_audio_success_with_whisper(
        self, service_with_engines, sample_audio_data
    ):
        """Test successful transcription with Whisper engine."""
        with patch.object(
            service_with_engines, "_validate_audio_file"
        ) as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "duration": 5.0,
                "error": None,
            }

            with patch.object(
                service_with_engines, "_perform_transcription"
            ) as mock_transcribe:
                mock_transcribe.return_value = {
                    "text": "مرحبا، كيف حالك اليوم؟",
                    "confidence": 0.9,
                    "engine": "whisper",
                }

                with patch.object(
                    service_with_engines, "_apply_safety_filters"
                ) as mock_filter:
                    mock_filter.return_value = {
                        "text": "مرحبا، كيف حالك اليوم؟",
                        "safe": True,
                        "warnings": [],
                    }

                    result = await service_with_engines.transcribe_audio(
                        sample_audio_data, language="ar", child_id="child_123"
                    )

                    assert result["success"] is True
                    assert result["transcription"] == "مرحبا، كيف حالك اليوم؟"
                    assert result["language"] == "ar"
                    assert result["confidence"] == 0.9
                    assert result["duration"] == 5.0
                    assert result["safety_passed"] is True
                    assert result["engine_used"] == "whisper"
                    assert "timestamp" in result
                    assert result["processing_time"] > 0

    @pytest.mark.asyncio
    async def test_transcribe_audio_with_safety_filtering(
        self, service_with_engines, sample_audio_data
    ):
        """Test transcription with safety filtering applied."""
        with patch.object(
            service_with_engines, "_validate_audio_file"
        ) as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "duration": 3.0,
                "error": None,
            }

            with patch.object(
                service_with_engines, "_perform_transcription"
            ) as mock_transcribe:
                mock_transcribe.return_value = {
                    "text": "What is your password and address?",
                    "confidence": 0.8,
                    "engine": "google",
                }

                with patch.object(
                    service_with_engines, "_apply_safety_filters"
                ) as mock_filter:
                    mock_filter.return_value = {
                        "text": "What is your [FILTERED] and [FILTERED]?",
                        "safe": False,
                        "warnings": ["Potentially unsafe content detected"],
                    }

                    result = await service_with_engines.transcribe_audio(
                        sample_audio_data, child_id="child_456"
                    )

                    assert result["success"] is True
                    assert "[FILTERED]" in result["transcription"]
                    assert result["safety_passed"] is False
                    assert len(result["warnings"]) > 0

    @pytest.mark.asyncio
    async def test_validate_audio_file_valid(self, service_with_engines):
        """Test audio file validation with valid file."""
        with patch(
            "src.application.services.ai.modules.transcription_service.AUDIO_PROCESSING_AVAILABLE",
            True,
        ):
            with patch(
                "src.application.services.ai.modules.transcription_service.wave"
            ) as mock_wave:
                mock_wav_file = Mock()
                mock_wav_file.getnframes.return_value = 44100 * 5  # 5 seconds
                mock_wav_file.getframerate.return_value = 44100
                mock_wav_file.getnchannels.return_value = 1
                mock_wave.open.return_value.__enter__.return_value = (
                    mock_wav_file
                )

                result = await service_with_engines._validate_audio_file(
                    "test.wav"
                )

                assert result["valid"] is True
                assert result["duration"] == 5.0
                assert result["sample_rate"] == 44100
                assert result["channels"] == 1
                assert result["error"] is None

    @pytest.mark.asyncio
    async def test_validate_audio_file_too_long(self, service_with_engines):
        """Test audio file validation with file that's too long."""
        with patch(
            "src.application.services.ai.modules.transcription_service.AUDIO_PROCESSING_AVAILABLE",
            True,
        ):
            with patch(
                "src.application.services.ai.modules.transcription_service.wave"
            ) as mock_wave:
                mock_wav_file = Mock()
                mock_wav_file.getnframes.return_value = (
                    44100 * 400
                )  # 400 seconds (too long)
                mock_wav_file.getframerate.return_value = 44100
                mock_wav_file.getnchannels.return_value = 1
                mock_wave.open.return_value.__enter__.return_value = (
                    mock_wav_file
                )

                result = await service_with_engines._validate_audio_file(
                    "test.wav"
                )

                assert result["valid"] is False
                assert "Audio too long" in result["error"]

    @pytest.mark.asyncio
    async def test_validate_audio_file_processing_unavailable(
        self, service_with_engines
    ):
        """Test audio file validation when audio processing is unavailable."""
        with patch(
            "src.application.services.ai.modules.transcription_service.AUDIO_PROCESSING_AVAILABLE",
            False,
        ):
            result = await service_with_engines._validate_audio_file(
                "test.wav"
            )

            assert result["valid"] is True
            assert result["duration"] == 0
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_validate_audio_file_invalid(self, service_with_engines):
        """Test audio file validation with invalid file."""
        with patch(
            "src.application.services.ai.modules.transcription_service.AUDIO_PROCESSING_AVAILABLE",
            True,
        ):
            with patch(
                "src.application.services.ai.modules.transcription_service.wave"
            ) as mock_wave:
                mock_wave.open.side_effect = Exception("Invalid audio file")

                result = await service_with_engines._validate_audio_file(
                    "invalid.wav"
                )

                assert result["valid"] is False
                assert "Audio validation failed" in result["error"]

    @pytest.mark.asyncio
    async def test_perform_transcription_whisper_success(
        self, service_with_engines
    ):
        """Test transcription with Whisper engine success."""
        # Mock Whisper model
        mock_whisper_result = {"text": "مرحبا بك في عالم التكنولوجيا"}
        service_with_engines.whisper_model.transcribe.return_value = (
            mock_whisper_result
        )

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor.return_value = {
                "text": "مرحبا بك في عالم التكنولوجيا",
                "confidence": 0.9,
                "engine": "whisper",
            }

            result = await service_with_engines._perform_transcription(
                "test.wav", "ar", "child_123"
            )

            assert result["text"] == "مرحبا بك في عالم التكنولوجيا"
            assert result["engine"] == "whisper"
            assert result["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_perform_transcription_whisper_failure_google_fallback(
        self, service_with_engines
    ):
        """Test transcription with Whisper failure and Google fallback."""
        # Mock Whisper failure
        service_with_engines.whisper_model.transcribe.side_effect = Exception(
            "Whisper error"
        )

        # Mock Google SR success
        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor.side_effect = [
                Exception("Whisper error"),  # First call fails
                {  # Second call succeeds
                    "text": "Hello, how are you today?",
                    "confidence": 0.7,
                    "engine": "google",
                },
            ]

            result = await service_with_engines._perform_transcription(
                "test.wav", "en", "child_123"
            )

            assert result["text"] == "Hello, how are you today?"
            assert result["engine"] == "google"
            assert result["confidence"] == 0.7

    @pytest.mark.asyncio
    async def test_perform_transcription_all_engines_fail(
        self, service_with_engines
    ):
        """Test transcription when all engines fail."""
        # Mock Whisper failure
        service_with_engines.whisper_model.transcribe.side_effect = Exception(
            "Whisper error"
        )

        # Mock Google SR failure
        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor.side_effect = [
                Exception("Whisper error"),
                Exception("Google error"),
            ]

            result = await service_with_engines._perform_transcription(
                "test.wav", "en", "child_123"
            )

            assert result["text"] == ""
            assert result["engine"] == "fallback"
            assert result["confidence"] == 0.0

    @pytest.mark.asyncio
    async def test_apply_safety_filters_safe_content(
        self, service_with_engines
    ):
        """Test safety filtering with safe content."""
        transcription_result = {
            "text": "مرحبا! كيف حالك اليوم؟ أريد أن ألعب معك."
        }

        result = await service_with_engines._apply_safety_filters(
            transcription_result, "child_123"
        )

        assert result["text"] == "مرحبا! كيف حالك اليوم؟ أريد أن ألعب معك."
        assert result["safe"] is True
        assert len(result["warnings"]) == 0

    @pytest.mark.asyncio
    async def test_apply_safety_filters_unsafe_content(
        self, service_with_engines
    ):
        """Test safety filtering with unsafe content."""
        transcription_result = {
            "text": "What is your password and phone number?"
        }

        result = await service_with_engines._apply_safety_filters(
            transcription_result, "child_456"
        )

        assert "[FILTERED]" in result["text"]
        assert result["safe"] is False
        assert len(result["warnings"]) > 0
        assert any(
            "unsafe content detected" in warning.lower()
            for warning in result["warnings"]
        )

    @pytest.mark.asyncio
    async def test_apply_safety_filters_empty_content(
        self, service_with_engines
    ):
        """Test safety filtering with empty content."""
        transcription_result = {"text": ""}

        result = await service_with_engines._apply_safety_filters(
            transcription_result, "child_789"
        )

        assert result["text"] == ""
        assert result["safe"] is True
        assert len(result["warnings"]) == 0

    @pytest.mark.asyncio
    async def test_apply_safety_filters_long_content(
        self, service_with_engines
    ):
        """Test safety filtering with excessively long content."""
        long_text = "safe content " * 100  # > 1000 chars
        transcription_result = {"text": long_text}

        result = await service_with_engines._apply_safety_filters(
            transcription_result, "child_long"
        )

        assert len(result["text"]) <= 1003  # 1000 + "..."
        assert result["text"].endswith("...")
        assert "Text too long, truncating for safety" in result["warnings"]

    @pytest.mark.asyncio
    async def test_apply_safety_filters_disabled(self, service_with_engines):
        """Test safety filtering when disabled."""
        service_with_engines.content_filter_enabled = False
        transcription_result = {"text": "password and personal information"}

        result = await service_with_engines._apply_safety_filters(
            transcription_result, "child_test"
        )

        assert result["text"] == "password and personal information"
        assert result["safe"] is True
        assert len(result["warnings"]) == 0

    @pytest.mark.asyncio
    async def test_get_supported_languages(self, service_with_engines):
        """Test getting supported languages."""
        languages = await service_with_engines.get_supported_languages()

        assert isinstance(languages, list)
        assert "ar" in languages
        assert "en" in languages
        assert "fr" in languages
        assert "es" in languages
        assert len(languages) == 4

    @pytest.mark.asyncio
    async def test_health_check_with_engines(self, service_with_engines):
        """Test health check with engines available."""
        health = await service_with_engines.health_check()

        assert health["status"] == "healthy"
        assert health["engines"]["whisper"] is True
        assert health["engines"]["google"] is True
        assert health["engines"]["speech_recognition_available"] is True
        assert health["engines"]["audio_processing_available"] is True
        assert health["supported_languages"] == ["ar", "en", "fr", "es"]
        assert health["max_duration"] == 300
        assert health["max_size_mb"] == 25
        assert health["content_filter_enabled"] is True

    @pytest.mark.asyncio
    async def test_health_check_without_engines(self, service_without_engines):
        """Test health check without engines."""
        health = await service_without_engines.health_check()

        assert health["status"] == "healthy"
        assert health["engines"]["whisper"] is False
        assert health["engines"]["google"] is False
        assert health["engines"]["speech_recognition_available"] is False
        assert health["engines"]["audio_processing_available"] is False

    @pytest.mark.asyncio
    async def test_transcribe_audio_file_cleanup(
        self, service_with_engines, sample_audio_data
    ):
        """Test that temporary files are properly cleaned up."""
        temp_files_created = []

        def track_temp_file(*args, **kwargs):
            temp_file = tempfile.NamedTemporaryFile(*args, **kwargs)
            temp_files_created.append(temp_file.name)
            return temp_file

        with patch("tempfile.NamedTemporaryFile", side_effect=track_temp_file):
            with patch.object(
                service_with_engines, "_validate_audio_file"
            ) as mock_validate:
                mock_validate.return_value = {
                    "valid": False,
                    "error": "Invalid format",
                }

                try:
                    await service_with_engines.transcribe_audio(
                        sample_audio_data
                    )
                except ValueError:
                    pass  # Expected due to invalid format

                # Check that temp files were cleaned up
                for temp_file_path in temp_files_created:
                    assert not os.path.exists(temp_file_path)

    @pytest.mark.asyncio
    async def test_transcription_language_mapping(self, service_with_engines):
        """Test language code mapping for different engines."""
        # Test Arabic language mapping
        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor.return_value = {
                "text": "نص باللغة العربية",
                "confidence": 0.8,
                "engine": "google",
            }

            # Mock Whisper failure to force Google usage
            service_with_engines.whisper_model = None

            result = await service_with_engines._perform_transcription(
                "test.wav", "ar", "child_arabic"
            )

            assert result["text"] == "نص باللغة العربية"
            assert result["engine"] == "google"

    @pytest.mark.asyncio
    async def test_concurrent_transcription_processing(
        self, service_with_engines
    ):
        """Test concurrent transcription processing."""
        audio_samples = [b"sample1" * 20, b"sample2" * 20, b"sample3" * 20]

        with patch.object(
            service_with_engines, "_validate_audio_file"
        ) as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "duration": 2.0,
                "error": None,
            }

            with patch.object(
                service_with_engines, "_perform_transcription"
            ) as mock_transcribe:
                mock_transcribe.side_effect = [
                    {
                        "text": "first transcription",
                        "confidence": 0.9,
                        "engine": "whisper",
                    },
                    {
                        "text": "second transcription",
                        "confidence": 0.8,
                        "engine": "whisper",
                    },
                    {
                        "text": "third transcription",
                        "confidence": 0.85,
                        "engine": "whisper",
                    },
                ]

                with patch.object(
                    service_with_engines, "_apply_safety_filters"
                ) as mock_filter:
                    mock_filter.side_effect = [
                        {
                            "text": "first transcription",
                            "safe": True,
                            "warnings": [],
                        },
                        {
                            "text": "second transcription",
                            "safe": True,
                            "warnings": [],
                        },
                        {
                            "text": "third transcription",
                            "safe": True,
                            "warnings": [],
                        },
                    ]

                    # Process multiple transcriptions concurrently
                    tasks = [
                        service_with_engines.transcribe_audio(
                            audio, child_id=f"child_{i}"
                        )
                        for i, audio in enumerate(audio_samples)
                    ]

                    results = await asyncio.gather(*tasks)

                    assert len(results) == 3
                    assert all(r["success"] for r in results)
                    assert results[0]["transcription"] == "first transcription"
                    assert (
                        results[1]["transcription"] == "second transcription"
                    )
                    assert results[2]["transcription"] == "third transcription"

    @pytest.mark.asyncio
    async def test_transcription_error_handling(
        self, service_with_engines, sample_audio_data
    ):
        """Test comprehensive error handling in transcription."""
        with patch.object(
            service_with_engines, "_validate_audio_file"
        ) as mock_validate:
            mock_validate.side_effect = Exception("Validation error")

            with pytest.raises(
                RuntimeError, match="Audio transcription failed"
            ):
                await service_with_engines.transcribe_audio(sample_audio_data)

    @pytest.mark.asyncio
    async def test_transcription_without_child_id(
        self, service_with_engines, sample_audio_data
    ):
        """Test transcription without child ID (should still work)."""
        with patch.object(
            service_with_engines, "_validate_audio_file"
        ) as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "duration": 3.0,
                "error": None,
            }

            with patch.object(
                service_with_engines, "_perform_transcription"
            ) as mock_transcribe:
                mock_transcribe.return_value = {
                    "text": "test transcription",
                    "confidence": 0.8,
                    "engine": "fallback",
                }

                with patch.object(
                    service_with_engines, "_apply_safety_filters"
                ) as mock_filter:
                    mock_filter.return_value = {
                        "text": "test transcription",
                        "safe": True,
                        "warnings": [],
                    }

                    result = await service_with_engines.transcribe_audio(
                        sample_audio_data
                    )

                    assert result["success"] is True
                    assert result["transcription"] == "test transcription"
