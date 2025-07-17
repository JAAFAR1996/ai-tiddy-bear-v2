"""
Tests for Conversation Service
Testing conversation history and interactions management.
"""

import pytest
from uuid import UUID, uuid4
from unittest.mock import Mock, AsyncMock, patch

from src.application.services.conversation_service import ConversationService
from src.domain.entities.conversation import Conversation
from src.domain.repositories.conversation_repository import (
    ConversationRepository,
)


class TestConversationService:
    """Test the Conversation Service."""

    @pytest.fixture
    def mock_conversation_repo(self):
        """Create a mock conversation repository."""
        repo = Mock(spec=ConversationRepository)
        repo.save = AsyncMock()
        repo.get_by_id = AsyncMock()
        repo.find_by_child_id = AsyncMock()
        return repo

    @pytest.fixture
    def service(self, mock_conversation_repo):
        """Create a conversation service instance."""
        return ConversationService(conversation_repo=mock_conversation_repo)

    @pytest.fixture
    def child_id(self):
        """Create a test child ID."""
        return uuid4()

    @pytest.fixture
    def conversation_id(self):
        """Create a test conversation ID."""
        return uuid4()

    def test_initialization(self, mock_conversation_repo):
        """Test service initialization."""
        service = ConversationService(conversation_repo=mock_conversation_repo)
        assert service.conversation_repo == mock_conversation_repo

    @pytest.mark.asyncio
    async def test_start_new_conversation_success(
        self, service, mock_conversation_repo, child_id
    ):
        """Test successfully starting a new conversation."""
        # Arrange
        initial_text = "Hello, how are you today?"

        with patch(
            "src.domain.entities.conversation.Conversation.create_new"
        ) as mock_create:
            mock_conversation = Mock(spec=Conversation)
            mock_conversation.update_summary = Mock()
            mock_create.return_value = mock_conversation

            # Act
            result = await service.start_new_conversation(
                child_id, initial_text
            )

            # Assert
            assert result == mock_conversation
            mock_create.assert_called_once_with(child_id)
            mock_conversation.update_summary.assert_called_once_with(
                initial_text
            )
            mock_conversation_repo.save.assert_called_once_with(
                mock_conversation
            )

    @pytest.mark.asyncio
    async def test_start_new_conversation_empty_text(
        self, service, mock_conversation_repo, child_id
    ):
        """Test starting a new conversation with empty initial text."""
        # Arrange
        initial_text = ""

        with patch(
            "src.domain.entities.conversation.Conversation.create_new"
        ) as mock_create:
            mock_conversation = Mock(spec=Conversation)
            mock_conversation.update_summary = Mock()
            mock_create.return_value = mock_conversation

            # Act
            result = await service.start_new_conversation(
                child_id, initial_text
            )

            # Assert
            assert result == mock_conversation
            mock_conversation.update_summary.assert_called_once_with(
                initial_text
            )

    @pytest.mark.asyncio
    async def test_start_new_conversation_repository_error(
        self, service, mock_conversation_repo, child_id
    ):
        """Test handling repository error when starting new conversation."""
        # Arrange
        initial_text = "Hello"
        mock_conversation_repo.save.side_effect = Exception("Database error")

        with patch(
            "src.domain.entities.conversation.Conversation.create_new"
        ) as mock_create:
            mock_conversation = Mock(spec=Conversation)
            mock_create.return_value = mock_conversation

            # Act & Assert
            with pytest.raises(Exception, match="Database error"):
                await service.start_new_conversation(child_id, initial_text)

    @pytest.mark.asyncio
    async def test_get_conversation_history_success(
        self, service, mock_conversation_repo, child_id
    ):
        """Test successfully retrieving conversation history."""
        # Arrange
        mock_conversations = [
            Mock(spec=Conversation, id=uuid4()),
            Mock(spec=Conversation, id=uuid4()),
            Mock(spec=Conversation, id=uuid4()),
        ]
        mock_conversation_repo.find_by_child_id.return_value = (
            mock_conversations
        )

        # Act
        result = await service.get_conversation_history(child_id)

        # Assert
        assert result == mock_conversations
        assert len(result) == 3
        mock_conversation_repo.find_by_child_id.assert_called_once_with(
            child_id
        )

    @pytest.mark.asyncio
    async def test_get_conversation_history_empty(
        self, service, mock_conversation_repo, child_id
    ):
        """Test retrieving conversation history when none exists."""
        # Arrange
        mock_conversation_repo.find_by_child_id.return_value = []

        # Act
        result = await service.get_conversation_history(child_id)

        # Assert
        assert result == []
        mock_conversation_repo.find_by_child_id.assert_called_once_with(
            child_id
        )

    @pytest.mark.asyncio
    async def test_get_conversation_by_id_success(
        self, service, mock_conversation_repo, conversation_id
    ):
        """Test successfully retrieving a conversation by ID."""
        # Arrange
        mock_conversation = Mock(spec=Conversation, id=conversation_id)
        mock_conversation_repo.get_by_id.return_value = mock_conversation

        # Act
        result = await service._get_conversation_by_id(conversation_id)

        # Assert
        assert result == mock_conversation
        mock_conversation_repo.get_by_id.assert_called_once_with(
            conversation_id
        )

    @pytest.mark.asyncio
    async def test_get_conversation_by_id_not_found(
        self, service, mock_conversation_repo, conversation_id
    ):
        """Test retrieving a conversation that doesn't exist."""
        # Arrange
        mock_conversation_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(
            ValueError,
            match=f"Conversation with ID {conversation_id} not found",
        ):
            await service._get_conversation_by_id(conversation_id)

    @pytest.mark.asyncio
    async def test_update_conversation_analysis_success(
        self, service, mock_conversation_repo, conversation_id
    ):
        """Test successfully updating conversation analysis."""
        # Arrange
        emotion_analysis = "happy and excited"
        sentiment_score = 0.85

        mock_conversation = Mock(spec=Conversation)
        mock_conversation.update_analysis = Mock()
        mock_conversation_repo.get_by_id.return_value = mock_conversation

        # Act
        result = await service.update_conversation_analysis(
            conversation_id, emotion_analysis, sentiment_score
        )

        # Assert
        assert result == mock_conversation
        mock_conversation.update_analysis.assert_called_once_with(
            emotion_analysis, sentiment_score
        )
        mock_conversation_repo.save.assert_called_once_with(mock_conversation)

    @pytest.mark.asyncio
    async def test_update_conversation_analysis_invalid_id(
        self, service, mock_conversation_repo, conversation_id
    ):
        """Test updating analysis for non-existent conversation."""
        # Arrange
        mock_conversation_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(
            ValueError,
            match=f"Conversation with ID {conversation_id} not found",
        ):
            await service.update_conversation_analysis(
                conversation_id, "happy", 0.8
            )

    @pytest.mark.asyncio
    async def test_update_conversation_analysis_edge_scores(
        self, service, mock_conversation_repo, conversation_id
    ):
        """Test updating analysis with edge case sentiment scores."""
        # Arrange
        test_cases = [
            ("very negative", -1.0),
            ("neutral", 0.0),
            ("very positive", 1.0),
            ("slightly positive", 0.1),
            ("slightly negative", -0.1),
        ]

        mock_conversation = Mock(spec=Conversation)
        mock_conversation.update_analysis = Mock()
        mock_conversation_repo.get_by_id.return_value = mock_conversation

        for emotion_analysis, sentiment_score in test_cases:
            # Act
            result = await service.update_conversation_analysis(
                conversation_id, emotion_analysis, sentiment_score
            )

            # Assert
            mock_conversation.update_analysis.assert_called_with(
                emotion_analysis, sentiment_score
            )

    @pytest.mark.asyncio
    async def test_update_conversation_summary_success(
        self, service, mock_conversation_repo, conversation_id
    ):
        """Test successfully updating conversation summary."""
        # Arrange
        summary = "The child talked about their favorite animals and asked questions about dinosaurs."

        mock_conversation = Mock(spec=Conversation)
        mock_conversation.update_summary = Mock()
        mock_conversation_repo.get_by_id.return_value = mock_conversation

        # Act
        result = await service.update_conversation_summary(
            conversation_id, summary
        )

        # Assert
        assert result == mock_conversation
        mock_conversation.update_summary.assert_called_once_with(summary)
        mock_conversation_repo.save.assert_called_once_with(mock_conversation)

    @pytest.mark.asyncio
    async def test_update_conversation_summary_empty(
        self, service, mock_conversation_repo, conversation_id
    ):
        """Test updating summary with empty string."""
        # Arrange
        summary = ""

        mock_conversation = Mock(spec=Conversation)
        mock_conversation.update_summary = Mock()
        mock_conversation_repo.get_by_id.return_value = mock_conversation

        # Act
        result = await service.update_conversation_summary(
            conversation_id, summary
        )

        # Assert
        mock_conversation.update_summary.assert_called_once_with(summary)

    @pytest.mark.asyncio
    async def test_add_interaction_new_conversation(
        self, service, mock_conversation_repo, child_id
    ):
        """Test adding interaction when no conversation exists."""
        # Arrange
        user_input = "Tell me a story"
        ai_response = "Once upon a time..."

        mock_conversation_repo.find_by_child_id.return_value = (
            []
        )  # No existing conversations

        with patch.object(service, "start_new_conversation") as mock_start_new:
            mock_conversation = Mock(spec=Conversation)
            mock_conversation.add_interaction = Mock()
            mock_start_new.return_value = mock_conversation

            # Act
            result = await service.add_interaction(
                child_id, user_input, ai_response
            )

            # Assert
            assert result == mock_conversation
            mock_start_new.assert_called_once_with(child_id, user_input)
            mock_conversation.add_interaction.assert_called_once_with(
                user_input, ai_response
            )
            mock_conversation_repo.save.assert_called_once_with(
                mock_conversation
            )

    @pytest.mark.asyncio
    async def test_add_interaction_existing_conversation(
        self, service, mock_conversation_repo, child_id
    ):
        """Test adding interaction to existing conversation."""
        # Arrange
        user_input = "What happens next?"
        ai_response = "The brave knight continued on..."

        mock_conversation = Mock(spec=Conversation)
        mock_conversation.add_interaction = Mock()
        mock_conversation_repo.find_by_child_id.return_value = [
            mock_conversation
        ]

        # Act
        result = await service.add_interaction(
            child_id, user_input, ai_response
        )

        # Assert
        assert result == mock_conversation
        mock_conversation.add_interaction.assert_called_once_with(
            user_input, ai_response
        )
        mock_conversation_repo.save.assert_called_once_with(mock_conversation)

    @pytest.mark.asyncio
    async def test_add_interaction_multiple_conversations(
        self, service, mock_conversation_repo, child_id
    ):
        """Test adding interaction when multiple conversations exist."""
        # Arrange
        user_input = "Hello again"
        ai_response = "Welcome back!"

        # Create multiple conversations, first one should be selected
        mock_conversations = [
            Mock(spec=Conversation, id=uuid4()),
            Mock(spec=Conversation, id=uuid4()),
            Mock(spec=Conversation, id=uuid4()),
        ]
        for conv in mock_conversations:
            conv.add_interaction = Mock()

        mock_conversation_repo.find_by_child_id.return_value = (
            mock_conversations
        )

        # Act
        result = await service.add_interaction(
            child_id, user_input, ai_response
        )

        # Assert
        # Should use the first conversation
        assert result == mock_conversations[0]
        mock_conversations[0].add_interaction.assert_called_once_with(
            user_input, ai_response
        )
        mock_conversation_repo.save.assert_called_once_with(
            mock_conversations[0]
        )

    @pytest.mark.asyncio
    async def test_add_interaction_special_characters(
        self, service, mock_conversation_repo, child_id
    ):
        """Test adding interaction with special characters."""
        # Arrange
        user_input = "What's 2+2? 🤔"
        ai_response = "2 + 2 equals 4! 😊"

        mock_conversation = Mock(spec=Conversation)
        mock_conversation.add_interaction = Mock()
        mock_conversation_repo.find_by_child_id.return_value = [
            mock_conversation
        ]

        # Act
        result = await service.add_interaction(
            child_id, user_input, ai_response
        )

        # Assert
        mock_conversation.add_interaction.assert_called_once_with(
            user_input, ai_response
        )

    @pytest.mark.asyncio
    async def test_add_interaction_long_text(
        self, service, mock_conversation_repo, child_id
    ):
        """Test adding interaction with very long text."""
        # Arrange
        user_input = "Tell me a very long story " * 100
        ai_response = "Once upon a time... " * 200

        mock_conversation = Mock(spec=Conversation)
        mock_conversation.add_interaction = Mock()
        mock_conversation_repo.find_by_child_id.return_value = [
            mock_conversation
        ]

        # Act
        result = await service.add_interaction(
            child_id, user_input, ai_response
        )

        # Assert
        mock_conversation.add_interaction.assert_called_once_with(
            user_input, ai_response
        )

    @pytest.mark.asyncio
    async def test_repository_error_handling(
        self, service, mock_conversation_repo, child_id
    ):
        """Test handling of repository errors in various methods."""
        # Test save error in add_interaction
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.add_interaction = Mock()
        mock_conversation_repo.find_by_child_id.return_value = [
            mock_conversation
        ]
        mock_conversation_repo.save.side_effect = Exception(
            "Database connection lost"
        )

        with pytest.raises(Exception, match="Database connection lost"):
            await service.add_interaction(child_id, "test", "response")

    @pytest.mark.asyncio
    async def test_concurrent_operations(
        self, service, mock_conversation_repo, child_id
    ):
        """Test handling of concurrent operations."""
        import asyncio

        # Arrange
        mock_conversations = []
        for i in range(3):
            conv = Mock(spec=Conversation)
            conv.add_interaction = Mock()
            mock_conversations.append(conv)

        mock_conversation_repo.find_by_child_id.return_value = (
            mock_conversations
        )

        # Act - simulate concurrent interactions
        tasks = []
        for i in range(5):
            task = service.add_interaction(
                child_id, f"User input {i}", f"AI response {i}"
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # Assert - all should complete successfully
        assert len(results) == 5
        assert all(r == mock_conversations[0] for r in results)

    @pytest.mark.parametrize(
        "child_id_value",
        [
            uuid4(),
            UUID("12345678-1234-5678-1234-567812345678"),
            UUID(int=0),
            UUID(int=2**128 - 1),
        ],
    )
    @pytest.mark.asyncio
    async def test_various_uuid_formats(
        self, service, mock_conversation_repo, child_id_value
    ):
        """Test service with various UUID formats."""
        mock_conversation_repo.find_by_child_id.return_value = []

        # Should handle any valid UUID
        result = await service.get_conversation_history(child_id_value)

        assert result == []
        mock_conversation_repo.find_by_child_id.assert_called_once_with(
            child_id_value
        )
