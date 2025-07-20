import asyncio
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

from application.services.emotion_analyzer import (
    EmotionAnalyzer,
    EmotionResult,
)
from application.services.response_generator import (
    ActivityType,
    ResponseContext,
    ResponseGenerator,
)
from application.services.session_manager import (
    SessionData,
    SessionManager,
)
from application.services.transcription_service import (
    TranscriptionResult,
    TranscriptionService,
)

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

#!/usr/bin/env python3
"""
Integration Tests for AI Service Modules
Testing the interaction between newly split modules
"""


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

# AsyncMock compatibility for Python < 3.8
try:
    from unittest.mock import AsyncMock
except ImportError:
    from unittest.mock import MagicMock

    class AsyncMock(MagicMock):
        def __call__(self, *args, **kwargs):
            sup = super(AsyncMock, self)

            async def coro():
                return sup.__call__(*args, **kwargs)

            return coro()

        def __await__(self):
            return self().__await__()


# Import modules to test

# Import main service with fallback
try:
    from application.services.ai.main_service import AITeddyBearService
except ImportError:
    # Fallback for testing environment
    import os
    import sys

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
    from application.services.ai_teddy_bear_service import AITeddyBearService


@pytest.fixture
def mock_registry():
    """Mock service registry"""
    registry = Mock()
    return registry


@pytest.fixture
def mock_config():
    """Mock configuration"""
    return {
        "ai": {"provider": "openai", "model": "gpt-4", "temperature": 0.7},
        "voice": {"provider": "google", "language": "en-US"},
    }


@pytest.fixture
def mock_ai_service():
    """Mock AI service"""
    service = AsyncMock()
    service.generate_response = AsyncMock(return_value="Hello, I'm Teddy!")
    service.analyze_emotion = AsyncMock(
        return_value={
            "primary": "happy",
            "confidence": 0.9,
            "secondary": {},
            "valence": 0.8,
            "arousal": 0.6,
        }
    )
    return service


@pytest.fixture
def mock_voice_service():
    """Mock voice service"""
    service = AsyncMock()
    service.text_to_speech = AsyncMock(return_value=b"audio_data")
    service.transcribe = AsyncMock(
        return_value={
            "text": "Hello Teddy",
            "confidence": 0.95,
            "language": "en",
            "duration_ms": 1500,
        }
    )
    return service


class TestSessionManagerIntegration:
    """Test SessionManager integration"""

    @pytest.mark.asyncio
    async def test_session_lifecycle(self):
        """Test complete session lifecycle"""
        # Arrange
        manager = SessionManager()
        child_id = "child-123"
        metadata = {"age": 5, "language": "en"}

        # Act - Create session
        session = await manager.create_session(child_id, metadata)

        # Assert session created
        assert session.child_id == child_id
        assert session.session_id is not None
        assert session.metadata == metadata
        assert session.interaction_count == 0

        # Act - Add interaction
        interaction = {
            "timestamp": datetime.utcnow(),
            "transcription": "Hello Teddy",
            "response": "Hello! How are you?",
            "emotion": {"primary": "happy"},
            "activity_type": "conversation",
        }
        await manager.add_interaction(session.session_id, interaction)

        # Assert interaction added
        updated_session = await manager.get_session(session.session_id)
        assert updated_session is not None
        assert updated_session.interaction_count == 1
        assert len(updated_session.interactions) == 1

        # Act - End session
        ended_session = await manager.end_session(session.session_id)

        # Assert session ended
        assert ended_session is not None
        assert await manager.get_session(session.session_id) is None
        assert await manager.get_active_sessions_count() == 0

    @pytest.mark.asyncio
    async def test_session_cleanup(self):
        """Test old session cleanup"""
        # Arrange
        manager = SessionManager()

        # Create multiple sessions
        for i in range(5):
            await manager.create_session(f"child-{i}")

        assert await manager.get_active_sessions_count() == 5

        # Act - Clean up with 0 hours (should clean all)
        cleaned = await manager.cleanup_old_sessions(max_age_hours=0)

        # Assert all cleaned
        assert cleaned == 5
        assert await manager.get_active_sessions_count() == 0


class TestEmotionAnalyzerIntegration:
    """Test EmotionAnalyzer integration"""

    @pytest.mark.asyncio
    async def test_text_emotion_analysis(self):
        """Test text-based emotion analysis"""
        # Arrange
        analyzer = EmotionAnalyzer()

        # Test different emotional texts
        test_cases = [
            ("I'm so happy and excited!", "happy"),
            ("I'm feeling sad and lonely", "sad"),
            ("I'm scared of the dark", "scared"),
            ("That makes me angry!", "angry"),
            ("Okay, that's fine", "neutral"),
        ]

        for text, expected_emotion in test_cases:
            # Act
            result = await analyzer.analyze_text(text)

            # Assert
            assert isinstance(result, EmotionResult)
            assert result.primary_emotion == expected_emotion
            assert result.confidence >= 0.6
            assert -1 <= result.valence <= 1

    @pytest.mark.asyncio
    async def test_multimodal_analysis_with_ai_service(self, mock_ai_service):
        """Test multimodal emotion analysis with AI service"""
        # Arrange
        analyzer = EmotionAnalyzer(ai_service=mock_ai_service)
        text = "I love playing with you!"
        audio_data = b"fake_audio_data"
        context = {
            "previous_emotions": [{"primary": "happy", "confidence": 0.8}],
            "current_activity": ActivityType.GAME,
        }

        # Act
        result = await analyzer.analyze_multimodal(text, audio_data, context)

        # Assert
        assert result["primary"] == "happy"
        assert result["confidence"] == 0.9
        assert mock_ai_service.analyze_emotion.called

    def test_emotion_to_voice_mapping(self):
        """Test emotion to voice mapping"""
        # Arrange
        analyzer = EmotionAnalyzer()

        test_cases = [
            (EmotionResult("happy", 0.9, {}, 0.8, 0.8), "cheerful"),
            (EmotionResult("happy", 0.9, {}, 0.8, 0.5), "friendly"),
            (EmotionResult("sad", 0.9, {}, -0.7, 0.3), "sympathetic"),
            (EmotionResult("scared", 0.9, {}, -0.6, 0.7), "comforting"),
            (EmotionResult("angry", 0.9, {}, -0.8, 0.8), "calm"),
            (EmotionResult("neutral", 0.5, {}, 0.0, 0.5), "warm"),
        ]

        for emotion_result, expected_voice in test_cases:
            # Act
            voice = analyzer.map_emotion_to_voice(emotion_result)

            # Assert
            assert voice == expected_voice


class TestResponseGeneratorIntegration:
    """Test ResponseGenerator integration"""

    @pytest.mark.asyncio
    async def test_activity_type_detection(self):
        """Test activity type detection from input"""
        # Arrange
        generator = ResponseGenerator()
        session = SessionData(
            child_id="child-123",
            session_id="session-456",
            start_time=datetime.utcnow(),
        )

        test_cases = [
            ("Tell me a story about dragons", ActivityType.STORY),
            ("Let's play a game!", ActivityType.GAME),
            ("What is photosynthesis?", ActivityType.LEARNING),
            ("I'm tired, time for bed", ActivityType.SLEEP_ROUTINE),
            ("Hello, how are you?", ActivityType.CONVERSATION),
        ]

        for text, expected_activity in test_cases:
            # Act
            emotion = EmotionResult("neutral", 0.5)
            activity = await generator.determine_activity_type(text, emotion, session)

            # Assert
            assert activity == expected_activity

    @pytest.mark.asyncio
    async def test_comfort_response_for_sad_emotion(self):
        """Test comfort response generation for sad emotions"""
        # Arrange
        generator = ResponseGenerator()
        session = SessionData(
            child_id="child-123",
            session_id="session-456",
            start_time=datetime.utcnow(),
        )

        # Act
        text = "I miss my mommy"
        emotion = EmotionResult("sad", 0.9, {}, -0.7, 0.3)
        activity = await generator.determine_activity_type(text, emotion, session)

        # Assert
        assert activity == ActivityType.COMFORT

    @pytest.mark.asyncio
    async def test_response_generation_with_ai_service(self, mock_ai_service):
        """Test response generation with AI service"""
        # Arrange
        generator = ResponseGenerator(ai_service=mock_ai_service)
        session = SessionContext(
            child_id="child-123",
            session_id="session-456",
            start_time=datetime.utcnow(),
            metadata={"age": 5},
        )

        # Act
        text = "Can you help me learn numbers?"
        emotion = EmotionResult("neutral", 0.7)
        response = await generator.generate_contextual_response(text, emotion, session)

        # Assert
        assert isinstance(response, ResponseContext)
        assert response.text == "Hello, I'm Teddy!"
        assert response.activity_type == ActivityType.LEARNING
        assert response.emotion in ["warm", "friendly"]
        assert mock_ai_service.generate_response.called


class TestTranscriptionServiceIntegration:
    """Test TranscriptionService integration"""

    @pytest.mark.asyncio
    async def test_transcription_with_voice_service(self, mock_voice_service):
        """Test transcription with voice service fallback"""
        # Arrange
        service = TranscriptionService(voice_service=mock_voice_service)
        audio_data = b"fake_audio_data"

        # Act
        result = await service.transcribe_with_fallback(audio_data, "en")

        # Assert
        assert isinstance(result, TranscriptionResult)
        assert result.text == "Hello Teddy"
        assert result.confidence == 0.95
        assert result.language == "en"
        assert result.audio_duration_ms == 1500
        assert mock_voice_service.transcribe.called

    def test_audio_format_validation(self):
        """Test audio format validation"""
        # Arrange
        service = TranscriptionService()

        # Test valid formats
        valid_formats = [
            b"RIFF" + b"\x00" * 4 + b"WAVE",  # WAV
            b"ID3" + b"\x00" * 100,  # MP3 with ID3
            b"\xff\xfb" + b"\x00" * 100,  # MP3 without ID3
            b"OggS" + b"\x00" * 100,  # OGG
            b"\x00" * 1000,  # Raw PCM
        ]

        for audio in valid_formats:
            # Act & Assert
            assert asyncio.run(service.validate_audio_format(audio)) is True

        # Test invalid format (too small)
        assert asyncio.run(service.validate_audio_format(b"tiny")) is False

    def test_supported_languages(self):
        """Test supported languages list"""
        # Arrange
        service = TranscriptionService()

        # Act
        languages = service.get_supported_languages()

        # Assert
        assert isinstance(languages, list)
        assert len(languages) >= 10
        assert "en" in languages
        assert "ar" in languages
        assert "es" in languages


class TestMainServiceIntegration:
    """Test main service integration with modules"""

    @pytest.mark.asyncio
    async def test_process_voice_interaction_full_flow(
        self, mock_registry, mock_config, mock_ai_service, mock_voice_service
    ):
        """Test complete voice interaction flow"""
        # Arrange
        service = AITeddyBearService(mock_registry, mock_config)

        # Mock audit logger
        audit_logger = AsyncMock()
        service.audit_logger = audit_logger

        # Inject mocked services
        service.ai_service = mock_ai_service
        service.voice_service = mock_voice_service
        service.emotion_analyzer.ai_service = mock_ai_service
        service.response_generator.ai_service = mock_ai_service
        service.transcription_service.voice_service = mock_voice_service

        # Create session
        session = await service.session_manager.create_session("child-123")
        session_id = session.session_id

        # Prepare audio data
        audio_data = b"fake_audio_data"

        # Act
        result = await service.process_voice_interaction(session_id, audio_data)

        # Assert
        assert result["success"] is True
        assert result["transcription"] == "Hello Teddy"
        assert result["emotion"]["primary"] == "happy"
        assert result["response"] == "Hello, I'm Teddy!"
        assert result["audio_data"] == b"audio_data"
        assert result["activity_type"] == "conversation"

        # Verify services were called
        assert mock_voice_service.transcribe.called
        assert mock_ai_service.analyze_emotion.called
        assert mock_ai_service.generate_response.called
        assert mock_voice_service.text_to_speech.called
        assert audit_logger.log_event.called

    @pytest.mark.asyncio
    async def test_session_lifecycle_with_main_service(
        self, mock_registry, mock_config, mock_ai_service, mock_voice_service
    ):
        """Test full session lifecycle through main service"""
        # Arrange
        service = AITeddyBearService(mock_registry, mock_config)
        service.audit_logger = AsyncMock()
        service.ai_service = mock_ai_service
        service.voice_service = mock_voice_service
        service._get_child_preferences = AsyncMock(
            return_value={
                "language": "en",
                "voice": "default",
                "age": 5,
                "interests": ["animals", "space"],
            }
        )

        # Act - Start session
        start_result = await service.start_session("child-123", {"device": "esp32-001"})

        # Assert session started
        assert "session_id" in start_result
        assert "message" in start_result
        assert "audio_data" in start_result
        assert "preferences" in start_result

        session_id = start_result["session_id"]

        # Act - Process interaction
        interaction_result = await service.process_voice_interaction(
            session_id, b"child_audio"
        )

        # Assert interaction processed
        assert interaction_result["success"] is True

        # Act - End session
        end_result = await service.end_session(session_id)

        # Assert session ended
        assert "message" in end_result
        assert "audio_data" in end_result
        assert "summary" in end_result
        assert end_result["summary"]["interaction_count"] == 1
        assert end_result["summary"]["emotion_summary"]["dominant"] == "happy"


@pytest.mark.asyncio
async def test_module_independence():
    """Test that modules can work independently"""
    # Test SessionManager independently
    session_manager = SessionManager()
    session = await session_manager.create_session("child-1")
    assert session.child_id == "child-1"

    # Test EmotionAnalyzer independently
    emotion_analyzer = EmotionAnalyzer()
    emotion = await emotion_analyzer.analyze_text("I'm happy!")
    assert emotion.primary_emotion == "happy"

    # Test ResponseGenerator independently
    response_generator = ResponseGenerator()
    activity = await response_generator.determine_activity_type(
        "Tell me a story", EmotionResult("neutral", 0.5), session
    )
    assert activity == ActivityType.STORY

    # Test TranscriptionService independently
    transcription_service = TranscriptionService()
    is_valid = await transcription_service.validate_audio_format(
        b"RIFF" + b"\x00" * 100 + b"WAVE"
    )
    assert is_valid is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
