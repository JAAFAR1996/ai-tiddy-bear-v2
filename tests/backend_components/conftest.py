from unittest.mock import AsyncMock, MagicMock

try:
    import pytest
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

# Mock imports for testing


class Child:
    def __init__(self, id, name, age):
        self.id = id
        self.name = name
        self.age = age


class Conversation:
    def __init__(
        self, id, child_id, start_time, messages=None, is_active=True, **kwargs
    ):
        self.id = id
        self.child_id = child_id
        self.start_time = start_time
        self.messages = messages or []
        self.is_active = is_active
        for k, v in kwargs.items():
            setattr(self, k, v)


class EmotionType:
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    CALM = "calm"


class Emotion:
    def __init__(self, type, confidence):
        self.type = type
        self.confidence = confidence


class AudioData:
    def __init__(self, data):
        self.data = data


try:
    from src.infrastructure.security.unified_encryption_service import (
        EncryptionLevel,
        UnifiedEncryptionService,
    )
except ImportError:
    # If import fails, use mock versions
    UnifiedEncryptionService = MagicMock

    class EncryptionLevel:
        BASIC = "basic"
        STANDARD = "standard"
        HIGH = "high"
        CRITICAL = "critical"


# Mock services for testing
AIService = MagicMock
ConversationService = MagicMock
EmotionService = MagicMock


@pytest.fixture
def encryption_service():
    """Create encryption service instance"""
    return UnifiedEncryptionService(master_key="")


@pytest.fixture
def ai_service():
    """Mock AI service"""
    service = MagicMock(spec=AIService)
    service.generate_response = MagicMock()
    service.analyze_sentiment = MagicMock()
    service.detect_emotion = MagicMock()
    service.generate_story = MagicMock()
    service.moderate_content = MagicMock()
    return service


@pytest.fixture
def conversation_service():
    """Create conversation service"""
    service = MagicMock(spec=ConversationService)
    service.start_conversation = AsyncMock()
    service.add_message = AsyncMock()
    service.end_conversation = AsyncMock()
    service.get_conversation = AsyncMock()
    service.analyze_conversation = AsyncMock()
    return service


@pytest.fixture
def emotion_service():
    """Create emotion service"""
    service = MagicMock(spec=EmotionService)
    service.analyze_audio_emotion = MagicMock()
    service.analyze_text_emotion = MagicMock()
    service.track_emotion_history = MagicMock()
    service.get_emotion_trends = MagicMock()
    return service


@pytest.fixture
def esp32_service():
    """Mock ESP32 service"""
    service = MagicMock()
    service.register_device = MagicMock()
    service.update_status = MagicMock()
    service.stream_audio = MagicMock()
    service.send_command = MagicMock()
    return service


@pytest.fixture
def safety_service():
    """Mock safety service"""
    service = MagicMock()
    service.check_content_safety = MagicMock()
    service.detect_emergency_keywords = MagicMock()
    service.analyze_behavioral_patterns = MagicMock()
    service.trigger_alert = MagicMock()
    return service


@pytest.fixture
def report_service():
    """Mock report service"""
    service = MagicMock()
    service.generate_daily_report = MagicMock()
    service.generate_weekly_report = MagicMock()
    service.generate_custom_report = MagicMock()
    service.export_report = MagicMock()
    return service
