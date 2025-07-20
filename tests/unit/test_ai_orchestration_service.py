from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.application.dto.ai_response import AIResponse
from src.application.interfaces.ai_provider import AIProvider
from src.application.interfaces.safety_monitor import SafetyMonitor
from src.application.interfaces.tts_provider import TextToSpeechService
from src.application.services.ai_orchestration_service import (
    AIOrchestrationService,
)
from src.application.services.conversation_service import ConversationService
from src.domain.value_objects.child_preferences import ChildPreferences


@pytest.fixture
def mock_ai_provider():
    provider = AsyncMock(spec=AIProvider)
    provider.generate_response.return_value = "AI generated response"
    provider.analyze_sentiment.return_value = "neutral"
    provider.analyze_emotion.return_value = "happy"
    return provider


@pytest.fixture
def mock_safety_monitor():
    monitor = AsyncMock(spec=SafetyMonitor)
    monitor.check_content_safety.return_value = MagicMock(is_safe=True, severity="none")
    return monitor


@pytest.fixture
def mock_conversation_service():
    service = AsyncMock(spec=ConversationService)
    service.add_message.return_value = str(uuid4())
    return service


@pytest.fixture
def mock_tts_service():
    service = AsyncMock(spec=TextToSpeechService)
    service.generate_speech.return_value = b"mock_audio_data"
    return service


@pytest.fixture
def ai_orchestration_service(
    mock_ai_provider,
    mock_safety_monitor,
    mock_conversation_service,
    mock_tts_service,
):
    return AIOrchestrationService(
        ai_provider=mock_ai_provider,
        safety_monitor=mock_safety_monitor,
        conversation_service=mock_conversation_service,
        tts_service=mock_tts_service,
    )


@pytest.fixture
def test_child_id():
    return uuid4()


@pytest.fixture
def test_conversation_history():
    return ["Hello, teddy!"]


@pytest.fixture
def test_current_input():
    return "Tell me a story about a brave knight."


@pytest.fixture
def test_voice_id():
    return "standard_voice_1"


@pytest.fixture
def test_child_preferences():
    return ChildPreferences(
        age=6,
        interests=["adventure", "fantasy"],
        language="en",
        personality_traits=["imaginative"],
    )


@pytest.mark.asyncio
async def test_get_ai_response_safe_content(
    ai_orchestration_service,
    mock_ai_provider,
    mock_safety_monitor,
    mock_conversation_service,
    mock_tts_service,
    test_child_id,
    test_conversation_history,
    test_current_input,
    test_voice_id,
    test_child_preferences,
):
    response = await ai_orchestration_service.get_ai_response(
        test_child_id,
        test_conversation_history,
        test_current_input,
        test_voice_id,
        test_child_preferences,
    )

    mock_ai_provider.generate_response.assert_called_once_with(
        test_child_id,
        test_conversation_history,
        test_current_input,
        test_child_preferences,
    )
    mock_safety_monitor.check_content_safety.assert_called_once()
    mock_ai_provider.analyze_sentiment.assert_called_once()
    mock_ai_provider.analyze_emotion.assert_called_once()
    mock_tts_service.generate_speech.assert_called_once()
    mock_conversation_service.add_message.assert_called_once()

    assert isinstance(response, AIResponse)
    assert response.response_text == "AI generated response"
    assert response.audio_response == b"mock_audio_data"
    assert response.safe is True
    assert response.emotion == "happy"
    assert response.sentiment == "neutral"
