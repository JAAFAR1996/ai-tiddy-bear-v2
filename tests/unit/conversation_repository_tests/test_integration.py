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


class TestConversationRepositoryIntegration:
    """Integration tests with complete conversation lifecycle"""

    @pytest.mark.asyncio
    async def test_conversation_lifecycle(
        self, conversation_repository, sample_conversation
    ):
        """Test complete conversation lifecycle"""
        # Create
        created_conversation = await conversation_repository.create(sample_conversation)
        pytest.assume(created_conversation.id is not None)

        # Add messages
        success = await conversation_repository.add_message_to_conversation(
            created_conversation.id, "user", "Additional message"
        )
        pytest.assume(success is True)

        # Update
        created_conversation.quality_score = 0.95
        updated_conversation = await conversation_repository.update(
            created_conversation
        )
        pytest.assume(updated_conversation.quality_score == 0.95)

        # Get summary
        summary = await conversation_repository.get_conversation_summary(
            created_conversation.id
        )
        pytest.assume(summary is not None)

        # End conversation
        end_success = await conversation_repository.end_conversation(
            created_conversation.id
        )
        pytest.assume(end_success is True)

        # Archive (soft delete)
        delete_result = await conversation_repository.delete(created_conversation.id)
        pytest.assume(delete_result is True)

        # Verify archived
        archived_conversation = await conversation_repository.get_by_id(
            created_conversation.id
        )
        pytest.assume(archived_conversation is None)
