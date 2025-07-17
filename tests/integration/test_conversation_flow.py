from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
import uuid
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


class ChildProfile:
    """Mock child profile for testing"""

    def __init__(self, name: str, age: int):
        self.id = str(uuid.uuid4())
        self.name = name
        self.age = age


@pytest.mark.asyncio
class TestConversationFlow:
    """Test complete conversation flow"""

    async def test_start_conversation(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        test_child: ChildProfile,
    ):
        """Test starting a new conversation"""
        # Start conversation
        response = await async_client.post(
            "/api/v1/conversations/start",
            json={"child_id": test_child.id, "initial_message": "مرحبا"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "welcome_message" in data
        assert "voice_url" in data

    async def test_send_message(
        self, async_client: AsyncClient, active_session: str
    ):
        """Test sending message in active session"""
        response = await async_client.post(
            f"/api/v1/conversations/{active_session}/messages",
            json={"text": "ما هي الشمس؟"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "response_text" in data
        assert "voice_url" in data
        assert "emotion" in data

    async def test_end_conversation(
        self, async_client: AsyncClient, active_session: str
    ):
        """Test ending a conversation"""
        response = await async_client.post(
            f"/api/v1/conversations/{active_session}/end"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ended"

    async def test_conversation_history(
        self, async_client: AsyncClient, test_child: ChildProfile
    ):
        """Test retrieving conversation history"""
        response = await async_client.get(
            f"/api/v1/children/{test_child.id}/conversations",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data
        assert isinstance(data["conversations"], list)
