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


class TestConversationRepositorySearch:
    """Test search and filtering functionality"""

    @pytest.mark.asyncio
    async def test_get_conversations_by_child(self, conversation_repository):
        """Test finding conversations by child ID"""
        # Arrange
        child_id = "test-child-123"
        conversations = []
        for i in range(3):
            conv = Conversation(
                child_id=child_id,
                session_id=f"session-{i}",
                start_time=datetime.now() - timedelta(hours=i),
                topics=[f"topic-{i}"],
                messages=[],
                emotional_states=[],
            )
            conversations.append(await conversation_repository.create(conv))

        # Act
        child_conversations = await conversation_repository.get_conversations_by_child(
            child_id
        )

        # Assert
        pytest.assume(len(child_conversations) >= 3)
        pytest.assume(all(conv.child_id == child_id for conv in child_conversations))

    @pytest.mark.asyncio
    async def test_get_conversations_by_topics(self, conversation_repository):
        """Test finding conversations by topics"""
        # Arrange
        conversations = [
            Conversation(
                child_id="child-1",
                topics=["math", "science"],
                messages=[],
                emotional_states=[],
            ),
            Conversation(
                child_id="child-2",
                topics=["art", "creativity"],
                messages=[],
                emotional_states=[],
            ),
            Conversation(
                child_id="child-3",
                topics=["math", "games"],
                messages=[],
                emotional_states=[],
            ),
        ]

        for conv in conversations:
            await conversation_repository.create(conv)

        # Act
        math_conversations = await conversation_repository.get_conversations_by_topics(
            ["math"]
        )

        # Assert
        pytest.assume(len(math_conversations) >= 2)
        for conv in math_conversations:
            pytest.assume("math" in conv.topics)

    @pytest.mark.asyncio
    async def test_find_conversations_with_emotion(
        self, conversation_repository, sample_conversation
    ):
        """Test finding conversations containing specific emotions"""
        # Arrange
        created_conversation = await conversation_repository.create(sample_conversation)

        # Act
        happy_conversations = (
            await conversation_repository.find_conversations_with_emotion(
                "happy", confidence_threshold=0.8
            )
        )

        # Assert
        pytest.assume(len(happy_conversations) >= 1)
        found_conversation = next(
            (
                conv
                for conv in happy_conversations
                if conv.id == created_conversation.id
            ),
            None,
        )
        pytest.assume(found_conversation is not None)

    @pytest.mark.asyncio
    async def test_search_conversation_content(
        self, conversation_repository, sample_conversation
    ):
        """Test full-text search in conversation messages"""
        # Arrange
        created_conversation = await conversation_repository.create(sample_conversation)

        # Act
        search_results = await conversation_repository.search_conversation_content(
            "math"
        )

        # Assert
        pytest.assume(len(search_results) >= 1)
        conversation, messages = search_results[0]
        pytest.assume(conversation.id == created_conversation.id)
        pytest.assume(any("math" in msg.content.lower() for msg in messages))
