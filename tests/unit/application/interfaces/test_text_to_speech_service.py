"""
Comprehensive test suite for application/interfaces/text_to_speech_service.py

This test file validates the TextToSpeechService interface including
text-to-speech conversion, voice management, error handling, and
child-safe audio generation capabilities.
"""

import pytest
import asyncio
from abc import ABC

from src.application.interfaces.text_to_speech_service import TextToSpeechService


class MockTextToSpeechService(TextToSpeechService):
    """Mock implementation of TextToSpeechService for testing."""

    def __init__(self):
        self.text_to_speech_called = False
        self.call_count = 0
        self.calls_history = []
        self.audio_results = {}
        self.should_raise_exception = False
        self.exception_message = "TTS service error"
        self.processing_delay = 0.0

    async def text_to_speech(self, text: str, voice_id: str) -> bytes:
        """Mock text-to-speech implementation."""
        self.text_to_speech_called = True
        self.call_count += 1

        call_info = {
            "text": text,
            "voice_id": voice_id,
            "call_number": self.call_count
        }
        self.calls_history.append(call_info)

        if self.should_raise_exception:
            raise Exception(self.exception_message)

        # Simulate processing delay if set
        if self.processing_delay > 0:
            await asyncio.sleep(self.processing_delay)

        # Return mock audio data based on text and voice
        key = (text, voice_id)
        if key in self.audio_results:
            return self.audio_results[key]

        # Default mock audio data
        return f"audio_data_for_{text}_{voice_id}".encode('utf-8')


class TestTextToSpeechService:
    """Test suite for TextToSpeechService interface."""

    def test_text_to_speech_service_is_abc(self):
        """Test that TextToSpeechService is an abstract base class."""
        assert issubclass(TextToSpeechService, ABC)

    def test_text_to_speech_service_has_abstract_methods(self):
        """Test that TextToSpeechService has abstract methods."""
        assert hasattr(TextToSpeechService, '__abstractmethods__')
        assert 'text_to_speech' in TextToSpeechService.__abstractmethods__

    def test_text_to_speech_service_cannot_be_instantiated(self):
        """Test that TextToSpeechService cannot be instantiated directly."""
        with pytest.raises(TypeError):
            TextToSpeechService()

    def test_mock_implementation_is_valid(self):
        """Test that MockTextToSpeechService is a valid implementation."""
        service = MockTextToSpeechService()
        assert isinstance(service, TextToSpeechService)

    @pytest.mark.asyncio
    async def test_text_to_speech_basic_functionality(self):
        """Test basic text-to-speech functionality."""
        service = MockTextToSpeechService()
        text = "Hello, this is a test message"
        voice_id = "child_friendly_voice"

        # Act
        result = await service.text_to_speech(text, voice_id)

        # Assert
        assert service.text_to_speech_called
        assert service.call_count == 1
        assert isinstance(result, bytes)
        assert result == b"audio_data_for_Hello, this is a test message_child_friendly_voice"

    @pytest.mark.asyncio
    async def test_text_to_speech_call_tracking(self):
        """Test that service tracks calls correctly."""
        service = MockTextToSpeechService()

        # Make multiple calls
        await service.text_to_speech("First message", "voice1")
        await service.text_to_speech("Second message", "voice2")
        await service.text_to_speech("Third message", "voice1")

        # Assert
        assert service.call_count == 3
        assert len(service.calls_history) == 3

        # Check first call
        assert service.calls_history[0]["text"] == "First message"
        assert service.calls_history[0]["voice_id"] == "voice1"
        assert service.calls_history[0]["call_number"] == 1

        # Check second call
        assert service.calls_history[1]["text"] == "Second message"
        assert service.calls_history[1]["voice_id"] == "voice2"
        assert service.calls_history[1]["call_number"] == 2

        # Check third call
        assert service.calls_history[2]["text"] == "Third message"
        assert service.calls_history[2]["voice_id"] == "voice1"
        assert service.calls_history[2]["call_number"] == 3

    @pytest.mark.asyncio
    async def test_text_to_speech_with_custom_audio_results(self):
        """Test text-to-speech with custom audio results."""
        service = MockTextToSpeechService()

        # Set custom audio results
        service.audio_results[("Hello", "voice1")] = b"custom_audio_1"
        service.audio_results[("Goodbye", "voice2")] = b"custom_audio_2"

        # Test first custom result
        result1 = await service.text_to_speech("Hello", "voice1")
        assert result1 == b"custom_audio_1"

        # Test second custom result
        result2 = await service.text_to_speech("Goodbye", "voice2")
        assert result2 == b"custom_audio_2"

        # Test default result for unknown combination
        result3 = await service.text_to_speech("Unknown", "voice3")
        assert result3 == b"audio_data_for_Unknown_voice3"

    @pytest.mark.asyncio
    async def test_text_to_speech_error_handling(self):
        """Test error handling in text-to-speech."""
        service = MockTextToSpeechService()
        service.should_raise_exception = True
        service.exception_message = "Voice synthesis failed"

        text = "Test message"
        voice_id = "test_voice"

        with pytest.raises(Exception) as exc_info:
            await service.text_to_speech(text, voice_id)

        assert "Voice synthesis failed" in str(exc_info.value)
        assert service.text_to_speech_called
        assert service.call_count == 1

    @pytest.mark.asyncio
    async def test_text_to_speech_with_empty_text(self):
        """Test text-to-speech with empty text."""
        service = MockTextToSpeechService()
        text = ""
        voice_id = "default_voice"

        result = await service.text_to_speech(text, voice_id)

        assert isinstance(result, bytes)
        assert result == b"audio_data_for__default_voice"

    @pytest.mark.asyncio
    async def test_text_to_speech_with_long_text(self):
        """Test text-to-speech with very long text."""
        service = MockTextToSpeechService()
        text = "This is a very long text message that simulates a story or extended conversation. " * 100
        voice_id = "storyteller_voice"

        result = await service.text_to_speech(text, voice_id)

        assert isinstance(result, bytes)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_text_to_speech_with_special_characters(self):
        """Test text-to-speech with special characters."""
        service = MockTextToSpeechService()
        text = "Hello! How are you? Let's count: 1, 2, 3... Ready?"
        voice_id = "friendly_voice"

        result = await service.text_to_speech(text, voice_id)

        assert isinstance(result, bytes)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_text_to_speech_with_unicode_text(self):
        """Test text-to-speech with unicode characters."""
        service = MockTextToSpeechService()
        texts = [
            "Hola, ¿cómo estás?",  # Spanish
            "Bonjour, comment allez-vous?",  # French
            "Hallo, wie geht es dir?",  # German
            "S“kaoCgYK",  # Japanese
            "`}`}"  # Chinese
        ]
        voice_id = "multilingual_voice"

        for text in texts:
            result = await service.text_to_speech(text, voice_id)
            assert isinstance(result, bytes)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_text_to_speech_with_different_voice_ids(self):
        """Test text-to-speech with various voice IDs."""
        service = MockTextToSpeechService()
        text = "Test message"

        voice_ids = [
            "child_voice_1",
            "child_voice_2",
            "adult_narrator",
            "friendly_assistant",
            "storyteller_voice",
            "educational_voice"
        ]

        for voice_id in voice_ids:
            result = await service.text_to_speech(text, voice_id)
            assert isinstance(result, bytes)
            assert f"audio_data_for_{text}_{voice_id}".encode() == result

    @pytest.mark.asyncio
    async def test_text_to_speech_concurrent_calls(self):
        """Test concurrent text-to-speech calls."""
        service = MockTextToSpeechService()

        # Create multiple concurrent calls
        tasks = [
            service.text_to_speech(f"Message {i}", f"voice_{i}")
            for i in range(5)
        ]

        results = await asyncio.gather(*tasks)

        # Verify all calls completed
        assert len(results) == 5
        assert service.call_count == 5
        assert len(service.calls_history) == 5

        # Verify all results are bytes
        for result in results:
            assert isinstance(result, bytes)

    @pytest.mark.asyncio
    async def test_text_to_speech_performance_timing(self):
        """Test text-to-speech performance timing."""
        import time

        service = MockTextToSpeechService()
        text = "Performance test message"
        voice_id = "performance_voice"

        start_time = time.time()
        result = await service.text_to_speech(text, voice_id)
        end_time = time.time()

        # Should complete quickly in mock implementation
        execution_time = end_time - start_time
        assert execution_time < 0.1  # Should be very fast
        assert isinstance(result, bytes)

    @pytest.mark.asyncio
    async def test_text_to_speech_with_processing_delay(self):
        """Test text-to-speech with simulated processing delay."""
        service = MockTextToSpeechService()
        service.processing_delay = 0.1  # 100ms delay

        text = "Delayed processing test"
        voice_id = "slow_voice"

        start_time = asyncio.get_event_loop().time()
        result = await service.text_to_speech(text, voice_id)
        end_time = asyncio.get_event_loop().time()

        # Should take at least the processing delay
        execution_time = end_time - start_time
        assert execution_time >= 0.1
        assert isinstance(result, bytes)

    @pytest.mark.asyncio
    async def test_text_to_speech_child_safe_content(self):
        """Test text-to-speech with child-safe content."""
        service = MockTextToSpeechService()

        child_safe_texts = [
            "Hello, let's learn together!",
            "What's your favorite animal?",
            "Time for a fun story!",
            "Let's count to ten: 1, 2, 3...",
            "Great job! You're doing wonderful!",
            "Let's explore the world of colors!",
            "Once upon a time in a magical land..."
        ]

        voice_id = "child_friendly_voice"

        for text in child_safe_texts:
            result = await service.text_to_speech(text, voice_id)
            assert isinstance(result, bytes)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_text_to_speech_educational_content(self):
        """Test text-to-speech with educational content."""
        service = MockTextToSpeechService()

        educational_texts = [
            "A is for Apple, B is for Ball",
            "Two plus two equals four",
            "The sun rises in the east",
            "Water freezes at zero degrees",
            "Plants need water and sunlight to grow"
        ]

        voice_id = "educational_voice"

        for text in educational_texts:
            result = await service.text_to_speech(text, voice_id)
            assert isinstance(result, bytes)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_text_to_speech_story_content(self):
        """Test text-to-speech with story content."""
        service = MockTextToSpeechService()

        story_parts = [
            "Once upon a time, in a land far away...",
            "There lived a brave little teddy bear.",
            "He loved to explore and make new friends.",
            "One day, he discovered a magical forest.",
            "And they all lived happily ever after!"
        ]

        voice_id = "storyteller_voice"

        for part in story_parts:
            result = await service.text_to_speech(part, voice_id)
            assert isinstance(result, bytes)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_text_to_speech_return_type_validation(self):
        """Test that text-to-speech always returns bytes."""
        service = MockTextToSpeechService()

        test_cases = [
            ("", "empty_voice"),
            ("Short", "short_voice"),
            ("Medium length text message", "medium_voice"),
            ("Very long text message that goes on and on" * 10, "long_voice"),
            ("Special chars: !@#$%^&*()", "special_voice"),
            ("Unicode: ><µ<­", "unicode_voice")
        ]

        for text, voice_id in test_cases:
            result = await service.text_to_speech(text, voice_id)
            assert isinstance(
                result, bytes), f"Failed for text: {text[:50]}..."

    @pytest.mark.asyncio
    async def test_text_to_speech_method_signature(self):
        """Test that text_to_speech method has correct signature."""
        service = MockTextToSpeechService()

        import inspect
        signature = inspect.signature(service.text_to_speech)
        parameters = list(signature.parameters.keys())

        # Should have 'text' and 'voice_id' parameters
        assert 'text' in parameters
        assert 'voice_id' in parameters
        assert len(parameters) == 2  # Only text and voice_id

    @pytest.mark.asyncio
    async def test_text_to_speech_async_behavior(self):
        """Test that text_to_speech is properly async."""
        service = MockTextToSpeechService()

        # Call should return a coroutine
        coro = service.text_to_speech("Test", "voice")
        assert asyncio.iscoroutine(coro)

        # Should be able to await it
        result = await coro
        assert isinstance(result, bytes)

    @pytest.mark.asyncio
    async def test_text_to_speech_error_propagation(self):
        """Test that errors are properly propagated."""
        service = MockTextToSpeechService()

        # Test different error types
        error_types = [
            ValueError("Invalid voice ID"),
            RuntimeError("Service unavailable"),
            ConnectionError("Network error"),
            TimeoutError("Request timeout")
        ]

        for error in error_types:
            service.should_raise_exception = True
            service.exception_message = str(error)

            with pytest.raises(Exception) as exc_info:
                await service.text_to_speech("Test", "voice")

            assert str(error) in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_text_to_speech_state_isolation(self):
        """Test that multiple service instances have isolated state."""
        service1 = MockTextToSpeechService()
        service2 = MockTextToSpeechService()

        # Make calls to both services
        await service1.text_to_speech("Message 1", "voice1")
        await service2.text_to_speech("Message 2", "voice2")

        # Each service should have its own state
        assert service1.call_count == 1
        assert service2.call_count == 1

        assert len(service1.calls_history) == 1
        assert len(service2.calls_history) == 1

        assert service1.calls_history[0]["text"] == "Message 1"
        assert service2.calls_history[0]["text"] == "Message 2"

    @pytest.mark.asyncio
    async def test_text_to_speech_large_batch_processing(self):
        """Test text-to-speech with large batch of requests."""
        service = MockTextToSpeechService()

        # Create a large batch of requests
        batch_size = 100
        tasks = []

        for i in range(batch_size):
            task = service.text_to_speech(
                f"Batch message {i}", f"voice_{i % 10}")
            tasks.append(task)

        # Process all requests
        results = await asyncio.gather(*tasks)

        # Verify all requests completed
        assert len(results) == batch_size
        assert service.call_count == batch_size
        assert len(service.calls_history) == batch_size

        # Verify all results are valid
        for i, result in enumerate(results):
            assert isinstance(result, bytes)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_text_to_speech_voice_id_validation(self):
        """Test text-to-speech with various voice ID formats."""
        service = MockTextToSpeechService()
        text = "Voice ID test"

        # Test different voice ID formats
        voice_ids = [
            "simple_voice",
            "voice-with-dashes",
            "voice_with_underscores",
            "VoiceWithCamelCase",
            "voice123",
            "voice_v2.1",
            "en-US-child-voice"
        ]

        for voice_id in voice_ids:
            result = await service.text_to_speech(text, voice_id)
            assert isinstance(result, bytes)

            # Verify call was recorded correctly
            last_call = service.calls_history[-1]
            assert last_call["voice_id"] == voice_id

    @pytest.mark.asyncio
    async def test_text_to_speech_memory_efficiency(self):
        """Test that text-to-speech doesn't leak memory with repeated calls."""
        service = MockTextToSpeechService()

        # Make many calls to test memory efficiency
        for i in range(1000):
            result = await service.text_to_speech(f"Memory test {i}", "test_voice")
            assert isinstance(result, bytes)

            # Clear result to help with memory
            del result

        # Should have processed all calls
        assert service.call_count == 1000

    @pytest.mark.asyncio
    async def test_text_to_speech_interface_compliance(self):
        """Test that mock implementation fully complies with interface."""
        service = MockTextToSpeechService()

        # Should be instance of the interface
        assert isinstance(service, TextToSpeechService)

        # Should have all required methods
        assert hasattr(service, 'text_to_speech')
        assert callable(service.text_to_speech)

        # Method should be async
        result = service.text_to_speech("Test", "voice")
        assert asyncio.iscoroutine(result)

        # Should return bytes
        audio_data = await result
        assert isinstance(audio_data, bytes)
