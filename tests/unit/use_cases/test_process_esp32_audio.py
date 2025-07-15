import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

"""Tests for ProcessESP32AudioUseCase."""

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
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from application.dto.esp32_request import ESP32Request
from application.dto.ai_response import AIResponse
from application.use_cases.process_esp32_audio import ProcessESP32AudioUseCase
from domain.entities.child_profile import ChildProfile
from domain.value_objects.safety_level import SafetyLevel
try:
    from fastapi
except ImportError:
    from common.mock_fastapi import HTTPException


class TestProcessESP32AudioUseCase:
    """Test ProcessESP32AudioUseCase functionality."""

    @pytest.fixture
    def child_profile(self):
        """Mock child profile."""
        profile = MagicMock(spec=ChildProfile)
        profile.id = uuid4()
        profile.name = "Test Child"
        profile.age = 5
        profile.preferences = MagicMock()
        profile.preferences.voice_preference = "child-voice-1"
        profile.preferences.vocabulary_size = 100
        profile.preferences.interaction_history_summary = ""
        profile.preferences.emotional_tendencies = {}
        return profile

    @pytest.fixture
    def esp32_request(self):
        """Mock ESP32 request."""
        return ESP32Request(
            child_id=uuid4(),
            audio_data=b"fake_audio_data",
            language_code="en"
        )

    @pytest.fixture
    def ai_response(self):
        """Mock AI response."""
        return AIResponse(
            response_text="Hello! How are you today?",
            audio_response=b"fake_audio_response",
            emotion="happy",
            sentiment=0.8,
            safe=True,
            conversation_id=str(uuid4())
        )

    @pytest.fixture
    def use_case(self):
        """Create ProcessESP32AudioUseCase with mocked dependencies."""
        audio_service = AsyncMock()
        ai_service = AsyncMock()
        conversation_service = AsyncMock()
        child_repository = AsyncMock()
        
        return ProcessESP32AudioUseCase(
            audio_processing_service=audio_service,
            ai_orchestration_service=ai_service,
            conversation_service=conversation_service,
            child_repository=child_repository
        )

    @pytest.mark.asyncio
    async def test_execute_success_flow(self, use_case, esp32_request, child_profile, ai_response):
        """Test successful audio processing flow."""
        # Setup mocks
        transcription = "Hello teddy bear"
        safety_level = SafetyLevel.HIGH
        conversation_history = []
        
        use_case.audio_processing_service.process_audio_input.return_value = (
            transcription, safety_level
        )
        use_case.child_repository.get_by_id.return_value = child_profile
        use_case.conversation_service.get_conversation_history.return_value = conversation_history
        use_case.ai_orchestration_service.get_ai_response.return_value = ai_response
        use_case.audio_processing_service.generate_audio_response.return_value = b"audio_output"

        # Execute
        result = await use_case.execute(esp32_request)

        # Verify
        assert result.response_text == "Hello! How are you today?"
        assert result.emotion == "happy"
        assert result.sentiment == 0.8
        assert result.safe is True
        assert result.audio_response == b"audio_output"

        # Verify service calls
        use_case.audio_processing_service.process_audio_input.assert_called_once_with(
            esp32_request.audio_data, esp32_request.language_code
        )
        use_case.child_repository.get_by_id.assert_called_once_with(esp32_request.child_id)
        use_case.conversation_service.get_conversation_history.assert_called_once_with(
            esp32_request.child_id
        )
        use_case.child_repository.save.assert_called_once_with(child_profile)

    @pytest.mark.asyncio
    async def test_execute_critical_safety_level(self, use_case, esp32_request):
        """Test handling of critical safety level."""
        # Setup mocks
        transcription = "inappropriate content"
        safety_level = SafetyLevel.CRITICAL
        
        use_case.audio_processing_service.process_audio_input.return_value = (
            transcription, safety_level
        )

        # Execute
        result = await use_case.execute(esp32_request)

        # Verify safety response
        assert result.response_text == "I'm sorry, I can't process that. Let's talk about something else."
        assert result.safe is False
        assert result.emotion == "neutral"
        assert result.sentiment == 0.0
        assert result.audio_response == b""

        # Verify no further processing
        use_case.child_repository.get_by_id.assert_not_called()
        use_case.ai_orchestration_service.get_ai_response.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_child_not_found(self, use_case, esp32_request):
        """Test handling when child profile not found."""
        # Setup mocks
        transcription = "Hello teddy bear"
        safety_level = SafetyLevel.HIGH
        
        use_case.audio_processing_service.process_audio_input.return_value = (
            transcription, safety_level
        )
        use_case.child_repository.get_by_id.return_value = None

        # Execute and verify exception
        with pytest.raises(HTTPException) as exc_info:
            await use_case.execute(esp32_request)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Child profile not found"

    @pytest.mark.asyncio
    async def test_execute_updates_child_preferences(self, use_case, esp32_request, child_profile, ai_response):
        """Test that child preferences are updated after interaction."""
        # Setup mocks
        transcription = "I love stories about animals"
        safety_level = SafetyLevel.HIGH
        conversation_history = []
        
        child_profile.preferences.vocabulary_size = 100
        child_profile.preferences.interaction_history_summary = ""
        child_profile.preferences.emotional_tendencies = {}
        
        use_case.audio_processing_service.process_audio_input.return_value = (
            transcription, safety_level
        )
        use_case.child_repository.get_by_id.return_value = child_profile
        use_case.conversation_service.get_conversation_history.return_value = conversation_history
        use_case.ai_orchestration_service.get_ai_response.return_value = ai_response
        use_case.audio_processing_service.generate_audio_response.return_value = b"audio_output"

        # Execute
        await use_case.execute(esp32_request)

        # Verify preferences were updated
        assert child_profile.preferences.vocabulary_size > 100  # Should increase
        assert transcription in child_profile.preferences.interaction_history_summary
        assert ai_response.response_text in child_profile.preferences.interaction_history_summary
        assert ai_response.emotion in child_profile.preferences.emotional_tendencies

    @pytest.mark.asyncio
    async def test_execute_conversation_tracking(self, use_case, esp32_request, child_profile, ai_response):
        """Test that conversation is properly tracked."""
        # Setup mocks
        transcription = "Tell me a story"
        safety_level = SafetyLevel.HIGH
        conversation_history = []
        
        use_case.audio_processing_service.process_audio_input.return_value = (
            transcription, safety_level
        )
        use_case.child_repository.get_by_id.return_value = child_profile
        use_case.conversation_service.get_conversation_history.return_value = conversation_history
        use_case.ai_orchestration_service.get_ai_response.return_value = ai_response
        use_case.audio_processing_service.generate_audio_response.return_value = b"audio_output"

        # Execute
        await use_case.execute(esp32_request)

        # Verify conversation tracking
        use_case.conversation_service.start_new_conversation.assert_called_once_with(
            esp32_request.child_id, transcription
        )
        use_case.conversation_service.update_conversation_analysis.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_audio_generation(self, use_case, esp32_request, child_profile, ai_response):
        """Test audio response generation."""
        # Setup mocks
        transcription = "Hello teddy bear"
        safety_level = SafetyLevel.HIGH
        conversation_history = []
        audio_output = b"generated_audio_data"
        
        use_case.audio_processing_service.process_audio_input.return_value = (
            transcription, safety_level
        )
        use_case.child_repository.get_by_id.return_value = child_profile
        use_case.conversation_service.get_conversation_history.return_value = conversation_history
        use_case.ai_orchestration_service.get_ai_response.return_value = ai_response
        use_case.audio_processing_service.generate_audio_response.return_value = audio_output

        # Execute
        result = await use_case.execute(esp32_request)

        # Verify audio generation
        use_case.audio_processing_service.generate_audio_response.assert_called_once_with(
            ai_response.response_text,
            voice_id=child_profile.preferences.voice_preference
        )
        assert result.audio_response == audio_output