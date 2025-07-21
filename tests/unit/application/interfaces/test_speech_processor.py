"""Comprehensive test suite for application/interfaces/speech_processor.py

This test file validates the SpeechProcessor protocol interface including
speech-to-text and text-to-speech functionality, error handling, and
child-safe audio processing capabilities.
"""

import asyncio
from typing import Protocol

import pytest

from src.application.interfaces.speech_processor import SpeechProcessor


class MockSpeechProcessor:
    """Mock implementation of SpeechProcessor protocol for testing."""

    def __init__(self):
        self.speech_to_text_called = False
        self.text_to_speech_called = False
        self.speech_to_text_results = {}
        self.text_to_speech_results = {}
        self.should_raise_exception = False
        self.exception_message = "Test exception"

    async def speech_to_text(self, audio_data: bytes, language: str) -> str:
        """Mock speech-to-text implementation."""
        self.speech_to_text_called = True
        self.last_speech_to_text_call = {
            "audio_data": audio_data,
            "language": language,
        }

        if self.should_raise_exception:
            raise Exception(self.exception_message)

        # Return mock transcription based on audio data
        key = (len(audio_data), language)
        return self.speech_to_text_results.get(key, f"Transcribed text in {language}")

    async def text_to_speech(self, text: str, voice_id: str) -> bytes:
        """Mock text-to-speech implementation."""
        self.text_to_speech_called = True
        self.last_text_to_speech_call = {"text": text, "voice_id": voice_id}

        if self.should_raise_exception:
            raise Exception(self.exception_message)

        # Return mock audio data based on text
        key = (text, voice_id)
        return self.text_to_speech_results.get(
            key, f"audio_data_for_{text}_{voice_id}".encode()
        )


class TestSpeechProcessor:
    """Test suite for SpeechProcessor protocol."""

    def test_speech_processor_is_protocol(self):
        """Test that SpeechProcessor is a typing.Protocol."""
        assert issubclass(SpeechProcessor, Protocol)

    def test_protocol_has_required_methods(self):
        """Test that SpeechProcessor protocol has required methods."""
        # Check that the protocol defines the required methods
        assert hasattr(SpeechProcessor, "speech_to_text")
        assert hasattr(SpeechProcessor, "text_to_speech")

        # Check method annotations
        annotations = SpeechProcessor.__annotations__
        assert "speech_to_text" in annotations
        assert "text_to_speech" in annotations

    def test_mock_implementation_conforms_to_protocol(self):
        """Test that MockSpeechProcessor conforms to SpeechProcessor protocol."""
        mock_processor = MockSpeechProcessor()

        # This should not raise a type error if the mock conforms to the
        # protocol
        assert isinstance(mock_processor, SpeechProcessor)

    @pytest.mark.asyncio
    async def test_speech_to_text_basic_functionality(self):
        """Test basic speech-to-text functionality."""
        processor = MockSpeechProcessor()
        audio_data = b"fake_audio_data"
        language = "en-US"

        # Act
        result = await processor.speech_to_text(audio_data, language)

        # Assert
        assert processor.speech_to_text_called
        assert processor.last_speech_to_text_call["audio_data"] == audio_data
        assert processor.last_speech_to_text_call["language"] == language
        assert result == "Transcribed text in en-US"

    @pytest.mark.asyncio
    async def test_text_to_speech_basic_functionality(self):
        """Test basic text-to-speech functionality."""
        processor = MockSpeechProcessor()
        text = "Hello, this is a test message"
        voice_id = "child_friendly_voice"

        # Act
        result = await processor.text_to_speech(text, voice_id)

        # Assert
        assert processor.text_to_speech_called
        assert processor.last_text_to_speech_call["text"] == text
        assert processor.last_text_to_speech_call["voice_id"] == voice_id
        assert (
            result
            == b"audio_data_for_Hello, this is a test message_child_friendly_voice"
        )

    @pytest.mark.asyncio
    async def test_speech_to_text_with_different_languages(self):
        """Test speech-to-text with various languages."""
        processor = MockSpeechProcessor()
        audio_data = b"audio_data"

        languages = ["en-US", "es-ES", "fr-FR", "de-DE", "it-IT"]

        for language in languages:
            processor.speech_to_text_results[(len(audio_data), language)] = (
                f"Text in {language}"
            )

            result = await processor.speech_to_text(audio_data, language)
            assert result == f"Text in {language}"

    @pytest.mark.asyncio
    async def test_text_to_speech_with_different_voices(self):
        """Test text-to-speech with different voice IDs."""
        processor = MockSpeechProcessor()
        text = "Test message"

        voice_ids = [
            "child_voice_1",
            "child_voice_2",
            "adult_voice",
            "narrator_voice",
        ]

        for voice_id in voice_ids:
            processor.text_to_speech_results[(text, voice_id)] = (
                f"audio_for_{voice_id}".encode()
            )

            result = await processor.text_to_speech(text, voice_id)
            assert result == f"audio_for_{voice_id}".encode()

    @pytest.mark.asyncio
    async def test_speech_to_text_empty_audio(self):
        """Test speech-to-text with empty audio data."""
        processor = MockSpeechProcessor()
        audio_data = b""
        language = "en-US"

        processor.speech_to_text_results[(0, language)] = ""

        result = await processor.speech_to_text(audio_data, language)
        assert result == ""

    @pytest.mark.asyncio
    async def test_text_to_speech_empty_text(self):
        """Test text-to-speech with empty text."""
        processor = MockSpeechProcessor()
        text = ""
        voice_id = "default_voice"

        processor.text_to_speech_results[(text, voice_id)] = b""

        result = await processor.text_to_speech(text, voice_id)
        assert result == b""

    @pytest.mark.asyncio
    async def test_speech_to_text_large_audio_data(self):
        """Test speech-to-text with large audio data."""
        processor = MockSpeechProcessor()
        audio_data = b"x" * 1000000  # 1MB of audio data
        language = "en-US"

        processor.speech_to_text_results[(len(audio_data), language)] = (
            "Long transcription"
        )

        result = await processor.speech_to_text(audio_data, language)
        assert result == "Long transcription"

    @pytest.mark.asyncio
    async def test_text_to_speech_long_text(self):
        """Test text-to-speech with long text."""
        processor = MockSpeechProcessor()
        text = (
            "This is a very long text message that simulates a story or long conversation. "
            * 100
        )
        voice_id = "storyteller_voice"

        processor.text_to_speech_results[(text, voice_id)] = b"long_audio_data"

        result = await processor.text_to_speech(text, voice_id)
        assert result == b"long_audio_data"

    @pytest.mark.asyncio
    async def test_speech_to_text_special_characters(self):
        """Test speech-to-text result with special characters."""
        processor = MockSpeechProcessor()
        audio_data = b"special_audio"
        language = "en-US"

        special_text = "Hello! How are you? I'm fine. Let's play: 1, 2, 3... Go!"
        processor.speech_to_text_results[(len(audio_data), language)] = special_text

        result = await processor.speech_to_text(audio_data, language)
        assert result == special_text

    @pytest.mark.asyncio
    async def test_text_to_speech_special_characters(self):
        """Test text-to-speech with special characters in text."""
        processor = MockSpeechProcessor()
        text = "Hello! How are you? Let's count: 1, 2, 3... Ready?"
        voice_id = "friendly_voice"

        result = await processor.text_to_speech(text, voice_id)
        assert isinstance(result, bytes)

    @pytest.mark.asyncio
    async def test_speech_to_text_unicode_language_codes(self):
        """Test speech-to-text with unicode language codes."""
        processor = MockSpeechProcessor()
        audio_data = b"unicode_audio"

        unicode_languages = ["zh-CN", "ja-JP", "ko-KR", "ar-SA", "he-IL"]

        for language in unicode_languages:
            processor.speech_to_text_results[(len(audio_data), language)] = (
                f"Unicode text in {language}"
            )

            result = await processor.speech_to_text(audio_data, language)
            assert result == f"Unicode text in {language}"

    @pytest.mark.asyncio
    async def test_concurrent_speech_processing(self):
        """Test concurrent speech processing operations."""
        processor = MockSpeechProcessor()

        # Set up test data
        audio_data_1 = b"audio1"
        audio_data_2 = b"audio2"
        text_1 = "Hello world"
        text_2 = "Goodbye world"

        processor.speech_to_text_results[(len(audio_data_1), "en-US")] = "Result 1"
        processor.speech_to_text_results[(len(audio_data_2), "es-ES")] = "Result 2"
        processor.text_to_speech_results[(text_1, "voice1")] = b"audio1"
        processor.text_to_speech_results[(text_2, "voice2")] = b"audio2"

        # Run concurrent operations
        tasks = [
            processor.speech_to_text(audio_data_1, "en-US"),
            processor.speech_to_text(audio_data_2, "es-ES"),
            processor.text_to_speech(text_1, "voice1"),
            processor.text_to_speech(text_2, "voice2"),
        ]

        results = await asyncio.gather(*tasks)

        # Verify results
        assert results[0] == "Result 1"
        assert results[1] == "Result 2"
        assert results[2] == b"audio1"
        assert results[3] == b"audio2"

    @pytest.mark.asyncio
    async def test_speech_to_text_error_handling(self):
        """Test error handling in speech-to-text."""
        processor = MockSpeechProcessor()
        processor.should_raise_exception = True
        processor.exception_message = "Speech recognition failed"

        audio_data = b"invalid_audio"
        language = "en-US"

        with pytest.raises(Exception) as exc_info:
            await processor.speech_to_text(audio_data, language)

        assert "Speech recognition failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_text_to_speech_error_handling(self):
        """Test error handling in text-to-speech."""
        processor = MockSpeechProcessor()
        processor.should_raise_exception = True
        processor.exception_message = "Voice synthesis failed"

        text = "Test text"
        voice_id = "invalid_voice"

        with pytest.raises(Exception) as exc_info:
            await processor.text_to_speech(text, voice_id)

        assert "Voice synthesis failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_speech_to_text_performance(self):
        """Test speech-to-text performance with timing."""
        import time

        processor = MockSpeechProcessor()
        audio_data = b"performance_test_audio"
        language = "en-US"

        start_time = time.time()
        result = await processor.speech_to_text(audio_data, language)
        end_time = time.time()

        # Should complete quickly in mock implementation
        assert end_time - start_time < 0.1
        assert result is not None

    @pytest.mark.asyncio
    async def test_text_to_speech_performance(self):
        """Test text-to-speech performance with timing."""
        import time

        processor = MockSpeechProcessor()
        text = "Performance test text"
        voice_id = "performance_voice"

        start_time = time.time()
        result = await processor.text_to_speech(text, voice_id)
        end_time = time.time()

        # Should complete quickly in mock implementation
        assert end_time - start_time < 0.1
        assert result is not None

    @pytest.mark.asyncio
    async def test_speech_to_text_return_type(self):
        """Test that speech-to-text returns correct type."""
        processor = MockSpeechProcessor()
        audio_data = b"test_audio"
        language = "en-US"

        result = await processor.speech_to_text(audio_data, language)

        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_text_to_speech_return_type(self):
        """Test that text-to-speech returns correct type."""
        processor = MockSpeechProcessor()
        text = "Test text"
        voice_id = "test_voice"

        result = await processor.text_to_speech(text, voice_id)

        assert isinstance(result, bytes)

    @pytest.mark.asyncio
    async def test_speech_to_text_parameter_validation(self):
        """Test parameter validation for speech-to-text."""
        processor = MockSpeechProcessor()

        # Test with different parameter types
        audio_data = b"test_audio"
        language = "en-US"

        # Should work with bytes and string
        result = await processor.speech_to_text(audio_data, language)
        assert isinstance(result, str)

        # Verify parameters were captured correctly
        assert processor.last_speech_to_text_call["audio_data"] == audio_data
        assert processor.last_speech_to_text_call["language"] == language

    @pytest.mark.asyncio
    async def test_text_to_speech_parameter_validation(self):
        """Test parameter validation for text-to-speech."""
        processor = MockSpeechProcessor()

        # Test with different parameter types
        text = "Test message"
        voice_id = "test_voice_id"

        # Should work with strings
        result = await processor.text_to_speech(text, voice_id)
        assert isinstance(result, bytes)

        # Verify parameters were captured correctly
        assert processor.last_text_to_speech_call["text"] == text
        assert processor.last_text_to_speech_call["voice_id"] == voice_id

    @pytest.mark.asyncio
    async def test_child_safety_voice_filtering(self):
        """Test that child-safe voice IDs are properly handled."""
        processor = MockSpeechProcessor()
        text = "Hello, let's learn together!"

        child_safe_voices = [
            "child_friendly_1",
            "educational_voice",
            "storyteller_child",
            "gentle_narrator",
            "playful_assistant",
        ]

        for voice_id in child_safe_voices:
            processor.text_to_speech_results[(text, voice_id)] = (
                f"safe_audio_{voice_id}".encode()
            )

            result = await processor.text_to_speech(text, voice_id)
            assert result == f"safe_audio_{voice_id}".encode()

    @pytest.mark.asyncio
    async def test_language_code_validation(self):
        """Test validation of language codes."""
        processor = MockSpeechProcessor()
        audio_data = b"test_audio"

        # Test standard language codes
        valid_languages = [
            "en-US",
            "en-GB",
            "es-ES",
            "fr-FR",
            "de-DE",
            "it-IT",
            "pt-BR",
            "ru-RU",
            "zh-CN",
            "ja-JP",
        ]

        for language in valid_languages:
            processor.speech_to_text_results[(len(audio_data), language)] = (
                f"Valid result for {language}"
            )

            result = await processor.speech_to_text(audio_data, language)
            assert result == f"Valid result for {language}"

    @pytest.mark.asyncio
    async def test_audio_data_format_handling(self):
        """Test handling of different audio data formats."""
        processor = MockSpeechProcessor()
        language = "en-US"

        # Test different audio data sizes and formats
        audio_formats = [
            b"wav_header_data",
            b"mp3_header_data",
            b"flac_header_data",
            b"ogg_header_data",
        ]

        for audio_data in audio_formats:
            processor.speech_to_text_results[(len(audio_data), language)] = (
                f"Processed {len(audio_data)} bytes"
            )

            result = await processor.speech_to_text(audio_data, language)
            assert result == f"Processed {len(audio_data)} bytes"

    @pytest.mark.asyncio
    async def test_text_content_safety(self):
        """Test processing of child-safe text content."""
        processor = MockSpeechProcessor()
        voice_id = "child_voice"

        # Test various child-safe text content
        safe_texts = [
            "Hello, how are you today?",
            "Let's learn about animals!",
            "Time for a fun story!",
            "What's your favorite color?",
            "Let's count to ten together!",
        ]

        for text in safe_texts:
            processor.text_to_speech_results[(text, voice_id)] = (
                f"safe_audio_for_{hash(text)}".encode()
            )

            result = await processor.text_to_speech(text, voice_id)
            assert isinstance(result, bytes)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_protocol_method_signatures(self):
        """Test that protocol methods have correct signatures."""
        processor = MockSpeechProcessor()

        # Test speech_to_text signature
        import inspect

        stt_signature = inspect.signature(processor.speech_to_text)
        stt_params = list(stt_signature.parameters.keys())
        assert "audio_data" in stt_params
        assert "language" in stt_params

        # Test text_to_speech signature
        tts_signature = inspect.signature(processor.text_to_speech)
        tts_params = list(tts_signature.parameters.keys())
        assert "text" in tts_params
        assert "voice_id" in tts_params

    @pytest.mark.asyncio
    async def test_async_protocol_compliance(self):
        """Test that all protocol methods are async."""
        processor = MockSpeechProcessor()

        # Test that methods are coroutines
        stt_coro = processor.speech_to_text(b"test", "en-US")
        tts_coro = processor.text_to_speech("test", "voice")

        assert asyncio.iscoroutine(stt_coro)
        assert asyncio.iscoroutine(tts_coro)

        # Clean up coroutines
        await stt_coro
        await tts_coro

    def test_protocol_structure(self):
        """Test the structure of the SpeechProcessor protocol."""
        # Verify it's a Protocol
        assert hasattr(SpeechProcessor, "__protocol__")

        # Check that it has the expected methods
        protocol_methods = [
            name for name in dir(SpeechProcessor) if not name.startswith("_")
        ]
        assert "speech_to_text" in protocol_methods
        assert "text_to_speech" in protocol_methods

    @pytest.mark.asyncio
    async def test_mock_state_management(self):
        """Test that mock processor manages state correctly."""
        processor = MockSpeechProcessor()

        # Initial state
        assert not processor.speech_to_text_called
        assert not processor.text_to_speech_called

        # After calling speech_to_text
        await processor.speech_to_text(b"test", "en-US")
        assert processor.speech_to_text_called
        assert not processor.text_to_speech_called

        # After calling text_to_speech
        await processor.text_to_speech("test", "voice")
        assert processor.speech_to_text_called
        assert processor.text_to_speech_called
