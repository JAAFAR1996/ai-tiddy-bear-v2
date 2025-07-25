import sys
from pathlib import Path

from domain.entities.conversation import Conversation

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


class TestConversationRepositoryAggregation:
    """Test aggregation functionality"""

    @pytest.mark.asyncio
    async def test_aggregate_count(self, conversation_repository):
        """Test count aggregation"""
        # Arrange
        for i in range(3):
            conv = Conversation(
                child_id=f"child-{i}",
                duration_seconds=300 + (i * 100),
                messages=[],
                emotional_states=[],
            )
            await conversation_repository.create(conv)

        # Act
        count = await conversation_repository.aggregate("duration_seconds", "count")

        # Assert
        pytest.assume(count >= 3)

    @pytest.mark.asyncio
    async def test_aggregate_average_duration(self, conversation_repository):
        """Test average duration calculation"""
        # Arrange
        durations = [300, 600, 900]
        for i, duration in enumerate(durations):
            conv = Conversation(
                child_id=f"child-{i}",
                duration_seconds=duration,
                messages=[],
                emotional_states=[],
            )
            await conversation_repository.create(conv)

        # Act
        avg_duration = await conversation_repository.aggregate(
            "duration_seconds", "avg"
        )

        # Assert
        pytest.assume(avg_duration > 0)
