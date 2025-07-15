import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from datetime import datetime, timedelta

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

from domain.entities.conversation import Conversation


class TestConversationRepositoryMaintenance:
    """Test maintenance and optimization functionality"""

    @pytest.mark.asyncio
    async def test_bulk_archive_old_conversations(self, conversation_repository):
        """Test archiving old conversations"""
        # Arrange
        old_conversations = []
        for i in range(3):
            conv = Conversation(
                child_id=f"child-{i}",
                start_time=datetime.now() - timedelta(days=100 + i),  # Very old
                messages=[],
                emotional_states=[],
            )
            old_conversations.append(await conversation_repository.create(conv))

        # Act
        archived_count = await conversation_repository.bulk_archive_old_conversations(
            days_old=90
        )

        # Assert
        pytest.assume(archived_count >= 3)

    @pytest.mark.asyncio
    async def test_get_conversation_metrics_summary(
        self, conversation_repository, sample_conversation
    ):
        """Test getting overall conversation metrics summary"""
        # Arrange
        await conversation_repository.create(sample_conversation)

        # Act
        metrics = await conversation_repository.get_conversation_metrics_summary()

        # Assert
        pytest.assume("total_conversations" in metrics)
        pytest.assume("unique_children_count" in metrics)
        pytest.assume("average_duration_minutes" in metrics)
        pytest.assume("average_quality_score" in metrics)
        pytest.assume("recent_activity_7_days" in metrics)
        pytest.assume("top_interaction_types" in metrics)

    @pytest.mark.asyncio
    async def test_optimize_conversation_performance(self, conversation_repository):
        """Test performance optimization analysis"""
        # Arrange - Create some conversations for analysis
        for i in range(5):
            conv = Conversation(
                child_id=f"child-{i}",
                start_time=datetime.now() - timedelta(days=i),
                duration_seconds=300 + (i * 100),
                total_messages=5 + i,
                quality_score=0.8 + (i * 0.02),
                safety_score=1.0,
                messages=[],
                emotional_states=[],
            )
            await conversation_repository.create(conv)

        # Act
        optimization = await conversation_repository.optimize_conversation_performance()

        # Assert
        pytest.assume("performance_score" in optimization)
        pytest.assume("performance_level" in optimization)
        pytest.assume("statistics" in optimization)
        pytest.assume("optimizations" in optimization)
        pytest.assume("recommendations" in optimization)

    @pytest.mark.asyncio
    async def test_find_conversations_requiring_review(self, conversation_repository):
        """Test finding conversations that require review"""
        # Arrange
        flagged_conv = Conversation(
            child_id="child-flagged",
            safety_score=0.7,  # Low safety score
            moderation_flags=3,  # High moderation flags
            messages=[],
            emotional_states=[],
        )
        await conversation_repository.create(flagged_conv)

        # Act
        review_conversations = (
            await conversation_repository.find_conversations_requiring_review()
        )

        # Assert
        pytest.assume(len(review_conversations) >= 1)
        flagged_found = any(
            conv.child_id == "child-flagged" for conv in review_conversations
        )
        pytest.assume(flagged_found)
