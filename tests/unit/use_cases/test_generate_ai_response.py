from application.dto.ai_response import AIResponse
from application.use_cases.generate_ai_response import GenerateAIResponseUseCase
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

"""Tests for GenerateAIResponseUseCase."""

try:
    import pytest
except ImportError:
    try:
        from common.mock_pytest import pytest
    except ImportError:
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


class TestGenerateAIResponseUseCase:
    """Test GenerateAIResponseUseCase functionality."""

    @pytest.fixture
    def ai_response(self):
        """Mock AI response."""
        return AIResponse(
            response_text="Hello! That's a great question about animals.",
            audio_response=b"audio_data",
            emotion="curious",
            sentiment=0.7,
            safe=True,
            conversation_id=str(uuid4()),
        )

    @pytest.fixture
    def use_case(self):
        """Create GenerateAIResponseUseCase with mocked dependencies."""
        ai_orchestration_service = AsyncMock()
        audio_processing_service = AsyncMock()

        return GenerateAIResponseUseCase(
            ai_orchestration_service=ai_orchestration_service,
            audio_processing_service=audio_processing_service,
        )

    @pytest.mark.asyncio
    async def test_execute_success(self, use_case, ai_response):
        """Test successful AI response generation."""
        # Setup
        child_id = uuid4()
        conversation_history = ["Hello teddy!", "Tell me about dogs"]
        user_input = "What do cats eat?"
        child_preferences = {"language": "en", "interests": ["animals"]}
        voice_id = "child-voice-1"
        audio_data = b"generated_audio"

        use_case.ai_orchestration_service.get_ai_response.return_value = ai_response
        use_case.audio_processing_service.generate_audio_response.return_value = (
            audio_data
        )

        # Execute
        result = await use_case.execute(
            child_id=child_id,
            conversation_history=conversation_history,
            user_input=user_input,
            child_preferences=child_preferences,
            voice_id=voice_id,
        )

        # Verify
        assert isinstance(result, AIResponse)
        assert result.response_text == ai_response.response_text
        assert result.emotion == "curious"
        assert result.sentiment == 0.7
        assert result.safe is True
        assert result.audio_response == audio_data

        # Verify service calls
        use_case.ai_orchestration_service.get_ai_response.assert_called_once_with(
            child_id=child_id,
            conversation_history=conversation_history,
            user_input=user_input,
            child_preferences=child_preferences,
            voice_id=voice_id,
        )
        use_case.audio_processing_service.generate_audio_response.assert_called_once_with(
            ai_response.response_text, voice_id=voice_id
        )

    @pytest.mark.asyncio
    async def test_execute_with_minimal_parameters(
            self, use_case, ai_response):
        """Test AI response generation with minimal parameters."""
        # Setup
        child_id = uuid4()
        user_input = "Hi!"
        audio_data = b"minimal_audio"

        use_case.ai_orchestration_service.get_ai_response.return_value = ai_response
        use_case.audio_processing_service.generate_audio_response.return_value = (
            audio_data
        )

        # Execute
        result = await use_case.execute(
            child_id=child_id, conversation_history=[], user_input=user_input
        )

        # Verify
        assert isinstance(result, AIResponse)
        assert result.audio_response == audio_data

        # Verify service calls with defaults
        use_case.ai_orchestration_service.get_ai_response.assert_called_once_with(
            child_id=child_id,
            conversation_history=[],
            user_input=user_input,
            child_preferences=None,
            voice_id=None,
        )
        use_case.audio_processing_service.generate_audio_response.assert_called_once_with(
            ai_response.response_text, voice_id=None
        )

    @pytest.mark.asyncio
    async def test_execute_unsafe_content_handling(self, use_case):
        """Test handling of unsafe AI response."""
        # Setup
        child_id = uuid4()
        user_input = "inappropriate question"

        unsafe_response = AIResponse(
            response_text="I can't discuss that topic.",
            audio_response=b"",
            emotion="neutral",
            sentiment=0.0,
            safe=False,
            conversation_id=str(uuid4()),
        )

        use_case.ai_orchestration_service.get_ai_response.return_value = unsafe_response
        use_case.audio_processing_service.generate_audio_response.return_value = (
            b"safety_audio"
        )

        # Execute
        result = await use_case.execute(
            child_id=child_id, conversation_history=[], user_input=user_input
        )

        # Verify
        assert result.safe is False
        assert result.emotion == "neutral"
        assert "can't discuss" in result.response_text.lower()

    @pytest.mark.asyncio
    async def test_execute_with_complex_conversation_history(
        self, use_case, ai_response
    ):
        """Test AI response with complex conversation history."""
        # Setup
        child_id = uuid4()
        conversation_history = [
            "Hello! What's your name?",
            "My name is Teddy. What would you like to talk about?",
            "I love dinosaurs! Tell me about T-Rex.",
            "T-Rex was a huge dinosaur that lived millions of years ago...",
            "Were they scary?",
            "They might seem scary, but they lived long before people...",
        ]
        user_input = "What did they eat?"
        child_preferences = {
            "language": "en",
            "interests": ["dinosaurs", "science"],
            "age_appropriate_level": "elementary",
        }
        voice_id = "educational-voice"
        audio_data = b"educational_audio"

        use_case.ai_orchestration_service.get_ai_response.return_value = ai_response
        use_case.audio_processing_service.generate_audio_response.return_value = (
            audio_data
        )

        # Execute
        result = await use_case.execute(
            child_id=child_id,
            conversation_history=conversation_history,
            user_input=user_input,
            child_preferences=child_preferences,
            voice_id=voice_id,
        )

        # Verify
        assert isinstance(result, AIResponse)
        assert result.audio_response == audio_data

        # Verify AI service received full context
        use_case.ai_orchestration_service.get_ai_response.assert_called_once_with(
            child_id=child_id,
            conversation_history=conversation_history,
            user_input=user_input,
            child_preferences=child_preferences,
            voice_id=voice_id,
        )

    @pytest.mark.asyncio
    async def test_execute_audio_generation_failure(
            self, use_case, ai_response):
        """Test handling when audio generation fails."""
        # Setup
        child_id = uuid4()
        user_input = "Hello!"

        use_case.ai_orchestration_service.get_ai_response.return_value = ai_response
        use_case.audio_processing_service.generate_audio_response.side_effect = (
            Exception("Audio service unavailable")
        )

        # Execute - should not fail completely
        with pytest.raises(Exception) as exc_info:
            await use_case.execute(
                child_id=child_id, conversation_history=[], user_input=user_input
            )

        assert "Audio service unavailable" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_execute_with_different_languages(self, use_case):
        """Test AI response generation with different languages."""
        # Setup for Spanish
        child_id = uuid4()
        user_input = "¿Cómo estás?"
        child_preferences = {"language": "es"}

        spanish_response = AIResponse(
            response_text="¡Hola! Estoy muy bien, gracias por preguntar.",
            audio_response=b"",
            emotion="happy",
            sentiment=0.8,
            safe=True,
            conversation_id=str(uuid4()),
        )

        use_case.ai_orchestration_service.get_ai_response.return_value = (
            spanish_response
        )
        use_case.audio_processing_service.generate_audio_response.return_value = (
            b"spanish_audio"
        )

        # Execute
        result = await use_case.execute(
            child_id=child_id,
            conversation_history=[],
            user_input=user_input,
            child_preferences=child_preferences,
        )

        # Verify
        assert result.response_text == "¡Hola! Estoy muy bien, gracias por preguntar."
        assert result.emotion == "happy"

    @pytest.mark.asyncio
    async def test_execute_emotional_response_tracking(self, use_case):
        """Test that emotional responses are properly tracked."""
        # Setup
        child_id = uuid4()
        user_input = "I'm feeling sad today"

        empathetic_response = AIResponse(
            response_text="I'm sorry you're feeling sad. Would you like to talk about it?",
            audio_response=b"",
            emotion="empathetic",
            sentiment=0.3,  # Lower sentiment due to child's sadness
            safe=True,
            conversation_id=str(uuid4()),
        )

        use_case.ai_orchestration_service.get_ai_response.return_value = (
            empathetic_response
        )
        use_case.audio_processing_service.generate_audio_response.return_value = (
            b"empathetic_audio"
        )

        # Execute
        result = await use_case.execute(
            child_id=child_id, conversation_history=[], user_input=user_input
        )

        # Verify emotional intelligence
        assert result.emotion == "empathetic"
        assert result.sentiment == 0.3
        assert "sorry" in result.response_text.lower()
        assert "talk about it" in result.response_text.lower()
