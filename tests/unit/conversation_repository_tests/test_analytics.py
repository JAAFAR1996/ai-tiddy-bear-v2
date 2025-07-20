from domain.entities.conversation import Conversation
from datetime import datetime, timedelta
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


class TestConversationRepositoryAnalytics:
    """Test analytics and insights functionality"""

    @pytest.mark.asyncio
    async def test_get_conversation_summary(
        self, conversation_repository, sample_conversation
    ):
        """Test generating conversation summary"""
        # Arrange
        _created_conversation = await conversation_repository.create(
            sample_conversation
        )

        # Act
        summary = await conversation_repository.get_conversation_summary(
            _created_conversation.id
        )

        # Assert
        pytest.assume(summary is not None)
        pytest.assume(summary["conversation_id"] == _created_conversation.id)
        pytest.assume("quality_scores" in summary)
        pytest.assume("emotional_progression" in summary)
        pytest.assume("role_statistics" in summary)
        pytest.assume("dominant_emotions" in summary)

    @pytest.mark.asyncio
    async def test_get_conversation_analytics(
        self, conversation_repository, sample_conversation
    ):
        """Test generating conversation analytics"""
        # Arrange
        await conversation_repository.create(sample_conversation)

        # Act
        analytics = await conversation_repository.get_conversation_analytics(
            child_id=sample_conversation.child_id
        )

        # Assert
        pytest.assume(analytics is not None)
        pytest.assume("summary" in analytics)
        pytest.assume("topics" in analytics)
        pytest.assume("quality_metrics" in analytics)
        pytest.assume("safety" in analytics)

    @pytest.mark.asyncio
    async def test_get_conversation_patterns(self, conversation_repository):
        """Test analyzing conversation patterns"""
        # Arrange
        child_id = "pattern-test-child"
        for i in range(5):
            conv = Conversation(
                child_id=child_id,
                start_time=datetime.now() - timedelta(days=i),
                duration_seconds=600 + (i * 60),  # Varying durations
                topics=[f"topic-{i % 3}"],  # Cycling topics
                quality_score=0.7 + (i * 0.05),  # Improving quality
                engagement_score=0.6 + (i * 0.08),
                messages=[],
                emotional_states=[],
            )
            await conversation_repository.create(conv)

        # Act
        patterns = await conversation_repository.get_conversation_patterns(
            child_id, days_back=7
        )

        # Assert
        pytest.assume(patterns["status"] == "success")
        pytest.assume(patterns["total_conversations"] >= 5)
        pytest.assume("avg_duration_minutes" in patterns)
        pytest.assume("most_common_topics" in patterns)
        pytest.assume("conversation_frequency" in patterns)

    @pytest.mark.asyncio
    async def test_get_conversation_health_metrics(
        self, conversation_repository, sample_conversation
    ):
        """Test generating health metrics for a child's conversations"""
        # Arrange
        _created_conversation = await conversation_repository.create(
            sample_conversation
        )

        # Act
        health_metrics = await conversation_repository.get_conversation_health_metrics(
            sample_conversation.child_id
        )

        # Assert
        pytest.assume(health_metrics["status"] == "success")
        pytest.assume("health_score" in health_metrics)
        pytest.assume("health_level" in health_metrics)
        pytest.assume("metrics" in health_metrics)
        pytest.assume("emotional_analysis" in health_metrics)
        pytest.assume("recommendations" in health_metrics)
