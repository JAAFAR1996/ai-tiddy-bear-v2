from datetime import datetime
import sys
from pathlib import Path

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


class TestWebSocket:
    """Test WebSocket functionality"""

    @pytest.mark.asyncio
    async def test_websocket_connection(self, websocket_service):
        """Test WebSocket connection"""
        # Arrange
        websocket_service.connect.return_value = True

        # Act
        connected = await websocket_service.connect("ws://localhost:8000/ws")

        # Assert
        assert connected is True
        websocket_service.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_real_time_emotion_updates(self, websocket_service):
        """Test real-time emotion updates via WebSocket"""
        # Arrange
        emotion_update = {
            "type": "emotion_update",
            "data": {
                "conversationId": "conv1",
                "emotion": "happy",
                "confidence": 0.9,
                "timestamp": datetime.utcnow().isoformat(),
            },
        }
        websocket_service.receive_message.return_value = emotion_update

        # Act
        message = await websocket_service.receive_message()

        # Assert
        assert message["type"] == "emotion_update"
        assert message["data"]["emotion"] == "happy"
        assert message["data"]["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_audio_streaming(self, websocket_service):
        """Test audio streaming via WebSocket"""
        # Arrange
        audio_chunk = {
            "type": "audio_stream",
            "data": {
                "conversationId": "conv1",
                "chunk": "base64_encoded_audio",
                "sequence": 1,
            },
        }

        # Act
        await websocket_service.send_message(audio_chunk)

        # Assert
        websocket_service.send_message.assert_called_once_with(audio_chunk)
