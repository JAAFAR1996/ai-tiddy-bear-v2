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


class TestConversationRepositoryMessaging:
    """Test message management functionality"""

    @pytest.mark.asyncio
    async def test_add_message_to_conversation(
        self, conversation_repository, sample_conversation
    ):
        """Test adding a single message to an existing conversation"""
        # Arrange
        created_conversation = await conversation_repository.create(sample_conversation)
        initial_message_count = created_conversation.total_messages

        # Act
        success = await conversation_repository.add_message_to_conversation(
            created_conversation.id, "user", "This is a new message", {
                "test": True}
        )

        # Assert
        pytest.assume(success is True)

        # Verify message was added
        updated_conversation = await conversation_repository.get_by_id(
            created_conversation.id
        )
        pytest.assume(updated_conversation.total_messages ==
                      initial_message_count + 1)

    @pytest.mark.asyncio
    async def test_end_conversation(
            self, conversation_repository, sample_conversation):
        """Test ending a conversation"""
        # Arrange
        sample_conversation.end_time = None  # Make it an active conversation
        created_conversation = await conversation_repository.create(sample_conversation)

        # Act
        success = await conversation_repository.end_conversation(
            created_conversation.id
        )

        # Assert
        pytest.assume(success is True)

        # Verify conversation was ended
        updated_conversation = await conversation_repository.get_by_id(
            created_conversation.id
        )
        pytest.assume(updated_conversation.end_time is not None)
        pytest.assume(updated_conversation.duration_seconds > 0)
