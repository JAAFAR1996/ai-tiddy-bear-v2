"""
Comprehensive test suite for application/services/audio_processing_service.py

This test file validates the AudioProcessingService including
audio input processing, safety monitoring, speech-to-text conversion,
text-to-speech generation, and child-safe audio handling.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Optional

from src.application.services.audio_processing_service import AudioProcessingService
from src.application.interfaces.safety_monitor import SafetyMonitor
from src.application.interfaces.speech_processor import SpeechProcessor
from src.application.interfaces.text_to_speech_service import TextToSpeechService
from src.domain.value_objects.safety_level import SafetyLevel


class MockSpeechProcessor:
    """Mock implementation of SpeechProcessor for testing."""
    
    def __init__(self):
        self.speech_to_text_called = False
        self.text_to_speech_called = False
        self.speech_to_text_result = "Mock transcription"
        self.text_to_speech_result = b"mock_audio_data"
        self.should_raise_exception = False
        self.exception_message = "Speech processor error"
        self.call_history = []
    
    async def speech_to_text(self, audio_data: bytes, language: str) -> str:
        """Mock speech-to-text implementation."""
        self.speech_to_text_called = True
        self.call_history.append(("speech_to_text", audio_data, language))
        
        if self.should_raise_exception:
            raise Exception(self.exception_message)
        
        return self.speech_to_text_result
    
    async def text_to_speech(self, text: str, voice_id: str) -> bytes:
        """Mock text-to-speech implementation."""
        self.text_to_speech_called = True
        self.call_history.append(("text_to_speech", text, voice_id))
        
        if self.should_raise_exception:
            raise Exception(self.exception_message)
        
        return self.text_to_speech_result


class MockSafetyMonitor:
    """Mock implementation of SafetyMonitor for testing."""
    
    def __init__(self):
        self.check_audio_safety_called = False
        self.check_content_safety_called = False
        self.audio_safety_result = SafetyLevel.NONE
        self.content_safety_result = None
        self.should_raise_exception = False
        self.exception_message = "Safety monitor error"
        self.call_history = []
    
    async def check_audio_safety(self, audio_data: bytes) -> SafetyLevel:
        """Mock check_audio_safety implementation."""
        self.check_audio_safety_called = True
        self.call_history.append(("check_audio_safety", audio_data))
        
        if self.should_raise_exception:
            raise Exception(self.exception_message)
        
        return self.audio_safety_result
    
    async def check_content_safety(
        self, 
        content: str, 
        child_age: int = 0, 
        conversation_history: Optional[List[str]] = None
    ):
        """Mock check_content_safety implementation."""
        self.check_content_safety_called = True
        self.call_history.append(("check_content_safety", content, child_age, conversation_history))
        
        if self.should_raise_exception:
            raise Exception(self.exception_message)
        
        return self.content_safety_result


class MockTextToSpeechService:
    """Mock implementation of TextToSpeechService for testing."""
    
    def __init__(self):
        self.text_to_speech_called = False
        self.text_to_speech_result = b"mock_tts_audio"
        self.should_raise_exception = False
        self.exception_message = "TTS service error"
        self.call_history = []
    
    async def text_to_speech(self, text: str, voice_id: str) -> bytes:
        """Mock text-to-speech implementation."""
        self.text_to_speech_called = True
        self.call_history.append(("text_to_speech", text, voice_id))
        
        if self.should_raise_exception:
            raise Exception(self.exception_message)
        
        return self.text_to_speech_result


@pytest.fixture
def mock_speech_processor():
    """Create a mock speech processor."""
    return MockSpeechProcessor()


@pytest.fixture
def mock_safety_monitor():
    """Create a mock safety monitor."""
    return MockSafetyMonitor()


@pytest.fixture
def mock_tts_service():
    """Create a mock text-to-speech service."""
    return MockTextToSpeechService()


@pytest.fixture
def audio_processing_service(mock_speech_processor, mock_safety_monitor, mock_tts_service):
    """Create AudioProcessingService with mock dependencies."""
    return AudioProcessingService(
        speech_processor=mock_speech_processor,
        safety_monitor=mock_safety_monitor,
        tts_service=mock_tts_service
    )


@pytest.fixture
def sample_audio_data():
    """Create sample audio data."""
    return b"fake_audio_data_for_testing"


@pytest.fixture
def sample_text():
    """Create sample text."""
    return "Hello, this is a test message for the child."


@pytest.fixture
def sample_language():
    """Create sample language code."""
    return "en-US"


@pytest.fixture
def sample_voice_id():
    """Create sample voice ID."""
    return "child_friendly_voice"


class TestAudioProcessingService:
    """Test suite for AudioProcessingService."""

    def test_init_sets_dependencies(self, mock_speech_processor, mock_safety_monitor, mock_tts_service):
        """Test that constructor properly sets dependencies."""
        service = AudioProcessingService(
            speech_processor=mock_speech_processor,
            safety_monitor=mock_safety_monitor,
            tts_service=mock_tts_service
        )
        
        assert service.speech_processor is mock_speech_processor
        assert service.safety_monitor is mock_safety_monitor
        assert service.tts_service is mock_tts_service

    @pytest.mark.asyncio
    async def test_process_audio_input_success(self, audio_processing_service, sample_audio_data, sample_language):
        """Test successful audio input processing."""
        # Act
        transcription, safety_level = await audio_processing_service.process_audio_input(
            audio_data=sample_audio_data,
            language=sample_language
        )
        
        # Assert
        assert transcription == "Mock transcription"
        assert safety_level == SafetyLevel.NONE
        
        # Verify dependencies were called
        assert audio_processing_service.speech_processor.speech_to_text_called
        assert audio_processing_service.safety_monitor.check_audio_safety_called

    @pytest.mark.asyncio
    async def test_process_audio_input_with_different_languages(self, audio_processing_service, sample_audio_data):
        """Test audio processing with different languages."""
        languages = ["en-US", "es-ES", "fr-FR", "de-DE", "zh-CN"]
        
        for language in languages:
            # Reset mocks
            audio_processing_service.speech_processor.speech_to_text_called = False
            audio_processing_service.safety_monitor.check_audio_safety_called = False
            
            # Act
            transcription, safety_level = await audio_processing_service.process_audio_input(
                audio_data=sample_audio_data,
                language=language
            )
            
            # Assert
            assert transcription == "Mock transcription"
            assert safety_level == SafetyLevel.NONE
            
            # Verify language was passed correctly
            last_call = audio_processing_service.speech_processor.call_history[-1]
            assert last_call[0] == "speech_to_text"
            assert last_call[2] == language

    @pytest.mark.asyncio
    async def test_process_audio_input_with_different_safety_levels(self, audio_processing_service, sample_audio_data, sample_language):
        """Test audio processing with different safety levels."""
        safety_levels = [SafetyLevel.NONE, SafetyLevel.LOW, SafetyLevel.MODERATE, SafetyLevel.HIGH, SafetyLevel.CRITICAL]
        
        for safety_level in safety_levels:
            # Configure mock
            audio_processing_service.safety_monitor.audio_safety_result = safety_level
            
            # Act
            transcription, returned_safety_level = await audio_processing_service.process_audio_input(
                audio_data=sample_audio_data,
                language=sample_language
            )
            
            # Assert
            assert returned_safety_level == safety_level

    @pytest.mark.asyncio
    async def test_process_audio_input_speech_processor_error(self, audio_processing_service, sample_audio_data, sample_language):
        """Test handling of speech processor errors."""
        # Arrange
        audio_processing_service.speech_processor.should_raise_exception = True
        audio_processing_service.speech_processor.exception_message = "Speech recognition failed"
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await audio_processing_service.process_audio_input(
                audio_data=sample_audio_data,
                language=sample_language
            )
        
        assert "Speech recognition failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_process_audio_input_safety_monitor_error(self, audio_processing_service, sample_audio_data, sample_language):
        """Test handling of safety monitor errors."""
        # Arrange
        audio_processing_service.safety_monitor.should_raise_exception = True
        audio_processing_service.safety_monitor.exception_message = "Safety check failed"
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await audio_processing_service.process_audio_input(
                audio_data=sample_audio_data,
                language=sample_language
            )
        
        assert "Safety check failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_process_audio_input_empty_audio(self, audio_processing_service, sample_language):
        """Test processing empty audio data."""
        # Arrange
        empty_audio = b""
        
        # Act
        transcription, safety_level = await audio_processing_service.process_audio_input(
            audio_data=empty_audio,
            language=sample_language
        )
        
        # Assert
        assert transcription == "Mock transcription"
        assert safety_level == SafetyLevel.NONE

    @pytest.mark.asyncio
    async def test_process_audio_input_large_audio(self, audio_processing_service, sample_language):
        """Test processing large audio data."""
        # Arrange
        large_audio = b"x" * 1000000  # 1MB of audio data
        
        # Act
        transcription, safety_level = await audio_processing_service.process_audio_input(
            audio_data=large_audio,
            language=sample_language
        )
        
        # Assert
        assert transcription == "Mock transcription"
        assert safety_level == SafetyLevel.NONE

    @pytest.mark.asyncio
    async def test_generate_audio_response_success(self, audio_processing_service, sample_text, sample_voice_id):
        """Test successful audio response generation."""
        # Act
        audio_data = await audio_processing_service.generate_audio_response(
            text=sample_text,
            voice_id=sample_voice_id
        )
        
        # Assert
        assert audio_data == b"mock_tts_audio"
        assert audio_processing_service.tts_service.text_to_speech_called
        
        # Verify parameters were passed correctly
        last_call = audio_processing_service.tts_service.call_history[-1]
        assert last_call[0] == "text_to_speech"
        assert last_call[1] == sample_text
        assert last_call[2] == sample_voice_id

    @pytest.mark.asyncio
    async def test_generate_audio_response_with_different_voices(self, audio_processing_service, sample_text):
        """Test audio response generation with different voice IDs."""
        voice_ids = [
            "child_friendly_voice",
            "storyteller_voice",
            "educational_voice",
            "calm_voice",
            "energetic_voice"
        ]
        
        for voice_id in voice_ids:
            # Reset mock
            audio_processing_service.tts_service.text_to_speech_called = False
            
            # Act
            audio_data = await audio_processing_service.generate_audio_response(
                text=sample_text,
                voice_id=voice_id
            )
            
            # Assert
            assert audio_data == b"mock_tts_audio"
            assert audio_processing_service.tts_service.text_to_speech_called
            
            # Verify voice_id was passed correctly
            last_call = audio_processing_service.tts_service.call_history[-1]
            assert last_call[2] == voice_id

    @pytest.mark.asyncio
    async def test_generate_audio_response_with_different_texts(self, audio_processing_service, sample_voice_id):
        """Test audio response generation with different text inputs."""
        texts = [
            "Hello, how are you today?",
            "Once upon a time, there was a brave little teddy bear.",
            "Let's learn about animals! What's your favorite animal?",
            "Great job! You're doing wonderful!",
            "Time for a fun story!"
        ]
        
        for text in texts:
            # Reset mock
            audio_processing_service.tts_service.text_to_speech_called = False
            
            # Act
            audio_data = await audio_processing_service.generate_audio_response(
                text=text,
                voice_id=sample_voice_id
            )
            
            # Assert
            assert audio_data == b"mock_tts_audio"
            assert audio_processing_service.tts_service.text_to_speech_called
            
            # Verify text was passed correctly
            last_call = audio_processing_service.tts_service.call_history[-1]
            assert last_call[1] == text

    @pytest.mark.asyncio
    async def test_generate_audio_response_empty_text(self, audio_processing_service, sample_voice_id):
        """Test audio response generation with empty text."""
        # Act
        audio_data = await audio_processing_service.generate_audio_response(
            text="",
            voice_id=sample_voice_id
        )
        
        # Assert
        assert audio_data == b"mock_tts_audio"
        assert audio_processing_service.tts_service.text_to_speech_called

    @pytest.mark.asyncio
    async def test_generate_audio_response_long_text(self, audio_processing_service, sample_voice_id):
        """Test audio response generation with very long text."""
        # Arrange
        long_text = "This is a very long story that goes on and on. " * 100
        
        # Act
        audio_data = await audio_processing_service.generate_audio_response(
            text=long_text,
            voice_id=sample_voice_id
        )
        
        # Assert
        assert audio_data == b"mock_tts_audio"
        assert audio_processing_service.tts_service.text_to_speech_called

    @pytest.mark.asyncio
    async def test_generate_audio_response_special_characters(self, audio_processing_service, sample_voice_id):
        """Test audio response generation with special characters."""
        # Arrange
        special_text = "Hello! How are you? Let's count: 1, 2, 3... Ready?"
        
        # Act
        audio_data = await audio_processing_service.generate_audio_response(
            text=special_text,
            voice_id=sample_voice_id
        )
        
        # Assert
        assert audio_data == b"mock_tts_audio"
        assert audio_processing_service.tts_service.text_to_speech_called

    @pytest.mark.asyncio
    async def test_generate_audio_response_unicode_text(self, audio_processing_service, sample_voice_id):
        """Test audio response generation with unicode text."""
        # Arrange
        unicode_text = "¡Hola! ¿Cómo estás? `}S“kao"
        
        # Act
        audio_data = await audio_processing_service.generate_audio_response(
            text=unicode_text,
            voice_id=sample_voice_id
        )
        
        # Assert
        assert audio_data == b"mock_tts_audio"
        assert audio_processing_service.tts_service.text_to_speech_called

    @pytest.mark.asyncio
    async def test_generate_audio_response_tts_error(self, audio_processing_service, sample_text, sample_voice_id):
        """Test handling of TTS service errors."""
        # Arrange
        audio_processing_service.tts_service.should_raise_exception = True
        audio_processing_service.tts_service.exception_message = "TTS generation failed"
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await audio_processing_service.generate_audio_response(
                text=sample_text,
                voice_id=sample_voice_id
            )
        
        assert "TTS generation failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_concurrent_audio_processing(self, audio_processing_service, sample_language):
        """Test concurrent audio processing operations."""
        # Arrange
        audio_data_list = [b"audio1", b"audio2", b"audio3", b"audio4", b"audio5"]
        
        # Act
        tasks = [
            audio_processing_service.process_audio_input(audio_data, sample_language)
            for audio_data in audio_data_list
        ]
        results = await asyncio.gather(*tasks)
        
        # Assert
        assert len(results) == 5
        for transcription, safety_level in results:
            assert transcription == "Mock transcription"
            assert safety_level == SafetyLevel.NONE

    @pytest.mark.asyncio
    async def test_concurrent_audio_generation(self, audio_processing_service, sample_voice_id):
        """Test concurrent audio generation operations."""
        # Arrange
        texts = [f"Message {i}" for i in range(5)]
        
        # Act
        tasks = [
            audio_processing_service.generate_audio_response(text, sample_voice_id)
            for text in texts
        ]
        results = await asyncio.gather(*tasks)
        
        # Assert
        assert len(results) == 5
        for audio_data in results:
            assert audio_data == b"mock_tts_audio"

    @pytest.mark.asyncio
    async def test_full_audio_workflow(self, audio_processing_service, sample_audio_data, sample_language, sample_voice_id):
        """Test complete audio processing workflow."""
        # Step 1: Process audio input
        transcription, safety_level = await audio_processing_service.process_audio_input(
            audio_data=sample_audio_data,
            language=sample_language
        )
        
        # Step 2: Generate audio response
        response_text = f"I heard you say: {transcription}"
        audio_response = await audio_processing_service.generate_audio_response(
            text=response_text,
            voice_id=sample_voice_id
        )
        
        # Assert
        assert transcription == "Mock transcription"
        assert safety_level == SafetyLevel.NONE
        assert audio_response == b"mock_tts_audio"

    @pytest.mark.asyncio
    async def test_audio_processing_with_safety_concerns(self, audio_processing_service, sample_audio_data, sample_language):
        """Test audio processing with safety concerns."""
        # Arrange
        audio_processing_service.safety_monitor.audio_safety_result = SafetyLevel.HIGH
        
        # Act
        transcription, safety_level = await audio_processing_service.process_audio_input(
            audio_data=sample_audio_data,
            language=sample_language
        )
        
        # Assert
        assert safety_level == SafetyLevel.HIGH
        assert transcription == "Mock transcription"

    @pytest.mark.asyncio
    async def test_audio_processing_performance(self, audio_processing_service, sample_audio_data, sample_language):
        """Test audio processing performance."""
        import time
        
        # Act
        start_time = time.time()
        transcription, safety_level = await audio_processing_service.process_audio_input(
            audio_data=sample_audio_data,
            language=sample_language
        )
        end_time = time.time()
        
        # Assert
        execution_time = end_time - start_time
        assert execution_time < 0.1  # Should be very fast with mocks
        assert transcription == "Mock transcription"
        assert safety_level == SafetyLevel.NONE

    @pytest.mark.asyncio
    async def test_audio_generation_performance(self, audio_processing_service, sample_text, sample_voice_id):
        """Test audio generation performance."""
        import time
        
        # Act
        start_time = time.time()
        audio_data = await audio_processing_service.generate_audio_response(
            text=sample_text,
            voice_id=sample_voice_id
        )
        end_time = time.time()
        
        # Assert
        execution_time = end_time - start_time
        assert execution_time < 0.1  # Should be very fast with mocks
        assert audio_data == b"mock_tts_audio"

    @pytest.mark.asyncio
    async def test_error_handling_maintains_service_state(self, audio_processing_service, sample_audio_data, sample_language):
        """Test that errors don't corrupt service state."""
        # Arrange
        audio_processing_service.speech_processor.should_raise_exception = True
        
        # Act & Assert
        with pytest.raises(Exception):
            await audio_processing_service.process_audio_input(
                audio_data=sample_audio_data,
                language=sample_language
            )
        
        # Reset error condition
        audio_processing_service.speech_processor.should_raise_exception = False
        
        # Should still work after error
        transcription, safety_level = await audio_processing_service.process_audio_input(
            audio_data=sample_audio_data,
            language=sample_language
        )
        
        assert transcription == "Mock transcription"
        assert safety_level == SafetyLevel.NONE

    @pytest.mark.asyncio
    async def test_return_types_validation(self, audio_processing_service, sample_audio_data, sample_language, sample_text, sample_voice_id):
        """Test that methods return correct types."""
        # Test process_audio_input return types
        transcription, safety_level = await audio_processing_service.process_audio_input(
            audio_data=sample_audio_data,
            language=sample_language
        )
        
        assert isinstance(transcription, str)
        assert isinstance(safety_level, SafetyLevel)
        
        # Test generate_audio_response return type
        audio_data = await audio_processing_service.generate_audio_response(
            text=sample_text,
            voice_id=sample_voice_id
        )
        
        assert isinstance(audio_data, bytes)

    @pytest.mark.asyncio
    async def test_dependency_call_order(self, audio_processing_service, sample_audio_data, sample_language):
        """Test that dependencies are called in correct order."""
        # Act
        await audio_processing_service.process_audio_input(
            audio_data=sample_audio_data,
            language=sample_language
        )
        
        # Assert
        speech_call = audio_processing_service.speech_processor.call_history[-1]
        safety_call = audio_processing_service.safety_monitor.call_history[-1]
        
        assert speech_call[0] == "speech_to_text"
        assert safety_call[0] == "check_audio_safety"
        
        # Both should have been called with correct parameters
        assert speech_call[1] == sample_audio_data
        assert speech_call[2] == sample_language
        assert safety_call[1] == sample_audio_data

    @pytest.mark.asyncio
    async def test_child_safe_audio_processing(self, audio_processing_service, sample_language):
        """Test processing of child-safe audio content."""
        # Arrange
        child_safe_audio = b"child_says_hello"
        audio_processing_service.safety_monitor.audio_safety_result = SafetyLevel.NONE
        
        # Act
        transcription, safety_level = await audio_processing_service.process_audio_input(
            audio_data=child_safe_audio,
            language=sample_language
        )
        
        # Assert
        assert safety_level == SafetyLevel.NONE
        assert safety_level.is_safe()

    @pytest.mark.asyncio
    async def test_unsafe_audio_detection(self, audio_processing_service, sample_language):
        """Test detection of unsafe audio content."""
        # Arrange
        unsafe_audio = b"potentially_unsafe_audio"
        audio_processing_service.safety_monitor.audio_safety_result = SafetyLevel.CRITICAL
        
        # Act
        transcription, safety_level = await audio_processing_service.process_audio_input(
            audio_data=unsafe_audio,
            language=sample_language
        )
        
        # Assert
        assert safety_level == SafetyLevel.CRITICAL
        assert not safety_level.is_safe()

    @pytest.mark.asyncio
    async def test_educational_content_processing(self, audio_processing_service, sample_voice_id):
        """Test processing of educational content."""
        # Arrange
        educational_texts = [
            "A is for Apple, B is for Ball",
            "Two plus two equals four",
            "The sun rises in the east",
            "Animals need food, water, and shelter"
        ]
        
        # Act & Assert
        for text in educational_texts:
            audio_data = await audio_processing_service.generate_audio_response(
                text=text,
                voice_id=sample_voice_id
            )
            assert isinstance(audio_data, bytes)
            assert len(audio_data) > 0

    @pytest.mark.asyncio
    async def test_storytelling_content_processing(self, audio_processing_service, sample_voice_id):
        """Test processing of storytelling content."""
        # Arrange
        story_parts = [
            "Once upon a time, in a magical forest...",
            "There lived a friendly teddy bear named Benny.",
            "Benny loved to help other animals in the forest.",
            "One day, he found a lost bunny rabbit.",
            "Together, they went on an amazing adventure!"
        ]
        
        # Act & Assert
        for part in story_parts:
            audio_data = await audio_processing_service.generate_audio_response(
                text=part,
                voice_id=sample_voice_id
            )
            assert isinstance(audio_data, bytes)
            assert len(audio_data) > 0

    def test_service_component_integration(self, mock_speech_processor, mock_safety_monitor, mock_tts_service):
        """Test that service properly integrates all components."""
        service = AudioProcessingService(
            speech_processor=mock_speech_processor,
            safety_monitor=mock_safety_monitor,
            tts_service=mock_tts_service
        )
        
        # All components should be accessible
        assert service.speech_processor is mock_speech_processor
        assert service.safety_monitor is mock_safety_monitor
        assert service.tts_service is mock_tts_service
        
        # Service should be ready to use
        assert callable(service.process_audio_input)
        assert callable(service.generate_audio_response)


class TestSafetyLevelEnum:
    """Test suite for SafetyLevel enum."""

    def test_safety_level_values(self):
        """Test SafetyLevel enum values."""
        assert SafetyLevel.NONE.value == "none"
        assert SafetyLevel.LOW.value == "low"
        assert SafetyLevel.MODERATE.value == "moderate"
        assert SafetyLevel.HIGH.value == "high"
        assert SafetyLevel.CRITICAL.value == "critical"

    def test_safety_level_is_safe(self):
        """Test is_safe method."""
        assert SafetyLevel.NONE.is_safe() is True
        assert SafetyLevel.LOW.is_safe() is True
        assert SafetyLevel.MODERATE.is_safe() is False
        assert SafetyLevel.HIGH.is_safe() is False
        assert SafetyLevel.CRITICAL.is_safe() is False

    def test_safety_level_numeric_levels(self):
        """Test numeric level property."""
        assert SafetyLevel.NONE.level == 0
        assert SafetyLevel.LOW.level == 1
        assert SafetyLevel.MODERATE.level == 2
        assert SafetyLevel.HIGH.level == 3
        assert SafetyLevel.CRITICAL.level == 4

    def test_safety_level_create_safe_level(self):
        """Test create_safe_level class method."""
        safe_level = SafetyLevel.create_safe_level()
        assert safe_level == SafetyLevel.NONE
        assert safe_level.is_safe()

    def test_safety_level_comparison(self):
        """Test safety level comparison using numeric levels."""
        assert SafetyLevel.NONE.level < SafetyLevel.LOW.level
        assert SafetyLevel.LOW.level < SafetyLevel.MODERATE.level
        assert SafetyLevel.MODERATE.level < SafetyLevel.HIGH.level
        assert SafetyLevel.HIGH.level < SafetyLevel.CRITICAL.level