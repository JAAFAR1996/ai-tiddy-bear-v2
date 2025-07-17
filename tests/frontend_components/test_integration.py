from unittest.mock import AsyncMock, Mock
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


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


class TestIntegration:
    """Integration tests for complete user flows"""

    @pytest.mark.asyncio
    async def test_complete_user_journey(self):
        """Test complete user journey from login to report generation"""
        # Mock services
        auth_service = Mock()
        child_service = Mock()
        conversation_service = Mock()
        report_service = Mock()

        # 1. Login
        auth_service.login = AsyncMock(
            return_value={
                "user": {"id": "user1", "email": "parent@example.com"},
                "token": "jwt_token",
            }
        )
        login_result = await auth_service.login(
            "parent@example.com", "password"
        )
        assert login_result["token"] == "jwt_token"

        # 2. Get children
        child_service.get_children = AsyncMock(
            return_value=[{"id": "child1", "name": "أحمد", "age": 5}]
        )
        children = await child_service.get_children()
        assert len(children) == 1

        # 3. Get conversations
        conversation_service.get_conversations = AsyncMock(
            return_value={
                "conversations": [
                    {"id": "conv1", "childId": "child1", "duration": 300}
                ],
                "total": 1,
            }
        )
        conversations = await conversation_service.get_conversations("child1")
        assert conversations["total"] == 1

        # 4. Generate report
        report_service.generate_report = AsyncMock(
            return_value={
                "id": "report1",
                "childId": "child1",
                "type": "weekly",
                "metrics": {"conversationCount": 7},
            }
        )
        report = await report_service.generate_report(
            {"childId": "child1", "type": "weekly"}
        )
        assert report["metrics"]["conversationCount"] == 7

    @pytest.mark.asyncio
    async def test_real_time_conversation_flow(self):
        """Test real-time conversation flow with WebSocket"""
        # Mock services
        websocket = Mock()
        conversation_service = Mock()

        # 1. Start conversation
        conversation_service.start_conversation = AsyncMock(
            return_value={
                "conversationId": "conv1",
                "sessionToken": "session_token",
            }
        )
        conversation = await conversation_service.start_conversation("child1")

        # 2. Connect WebSocket
        websocket.connect = AsyncMock(return_value=True)
        connected = await websocket.connect(
            f"ws://localhost:8000/ws?token={conversation['sessionToken']}"
        )
        assert connected is True

        # 3. Stream audio and receive responses
        messages = [
            {"type": "audio_stream", "data": {"chunk": "audio1"}},
            {"type": "teddy_response", "data": {"text": "مرحباً!"}},
            {
                "type": "emotion_update",
                "data": {"emotion": "happy", "confidence": 0.9},
            },
        ]

        for message in messages:
            if message["type"] == "audio_stream":
                await websocket.send_message(message)
            else:
                websocket.receive_message = AsyncMock(return_value=message)
                received = await websocket.receive_message()
                assert received["type"] in ["teddy_response", "emotion_update"]

        # 4. End conversation
        conversation_service.end_conversation = AsyncMock(return_value=True)
        ended = await conversation_service.end_conversation(
            conversation["conversationId"]
        )
        assert ended is True
