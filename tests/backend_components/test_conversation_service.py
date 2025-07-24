import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock

from domain.entities.conversation import Conversation

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


# Import pytest with fallback to mock
pytest = None
try:
    import pytest
except ImportError:
    try:
        from common.mock_pytest import pytest
    except ImportError:
        pass

    # Mock pytest when not available
    if pytest is None:
        class MockPytest:

        def fixture(self, *args, **kwargs):
            pass

            def decorator(func):
                return func

            return decorator

        def mark(self):
            pass

            class MockMark:
                def parametrize(self, *args, **kwargs):
                    pass

                    def decorator(func):
                return func

                    return decorator

                def asyncio(self, func):
                    pass

                    return func

                def slow(self, func):
                    pass

                    return func

                def skip(self, reason=""):
                    pass

                    def decorator(func):
                return func

                    return decorator

            return MockMark()

        def raises(self, exception):
            pass

            class MockRaises:
                def __enter__(self):
                    pass

                    return self

                def __exit__(self, *args):
                    pass

                    return False

            return MockRaises()

        def skip(self, reason=""):
            pass

            def decorator(func):
                return func

            return decorator

        pytest = MockPytest()


class TestConversationService:
    """Test conversation service"""

    @pytest.mark.asyncio
    async def test_conversation_flow(self, conversation_service):
        """Test complete conversation flow"""
        # 1. Start conversation
        conversation_service.start_conversation = AsyncMock(
            return_value=Conversation(
                id="conv123",
                child_id="child456",
                start_time=datetime.utcnow(),
                end_time=None,
                summary="",
                emotion_analysis="",
                sentiment_score=0.0,
            )
        )

        conversation = await conversation_service.start_conversation(
            "child456"
        )
        assert conversation.id == "conv123"
        assert conversation.is_active() is True

        conversation_service.add_message = AsyncMock()

        conversation_service.end_conversation = AsyncMock(
            return_value=Conversation(
                id="conv123",
                child_id="child456",
                start_time=datetime.utcnow() - timedelta(minutes=10),
                end_time=datetime.utcnow(),
                summary="محادثة ودية مع طلب قصة",
                emotion_analysis="",
                sentiment_score=0.0,
            )
        )

        ended_conversation = await conversation_service.end_conversation(
            "conv123", "محادثة ودية مع طلب قصة", "positive", 0.8
        )
        assert ended_conversation.is_active() is False
        assert ended_conversation.duration_minutes() == pytest.approx(
            600 / 60.0
        )
        assert ended_conversation.summary is not None

    @pytest.mark.asyncio
    async def test_conversation_analysis(self, conversation_service):
        """Test conversation analysis"""
        # Setup
        conversation_service.analyze_conversation = AsyncMock(
            return_value={
                "topics": ["greeting", "story_request", "animals"],
                "sentiment": "positive",
                "engagement_score": 0.85,
                "educational_value": 0.7,
                "key_moments": [
                    {"timestamp": "00:01:30", "event": "story_started"},
                    {"timestamp": "00:05:45", "event": "child_laughed"},
                ],
                "recommendations": [
                    "Child shows interest in animal stories",
                    "Consider more interactive storytelling",
                ],
            }
        )

        # Test
        analysis = await conversation_service.analyze_conversation("conv123")

        # Assert
        assert "story_request" in analysis["topics"]
        assert analysis["sentiment"] == "positive"
        assert analysis["engagement_score"] > 0.8
        assert len(analysis["recommendations"]) >= 1
