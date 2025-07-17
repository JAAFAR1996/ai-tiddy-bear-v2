"""
Test Conversation Repository

Comprehensive unit tests for ConversationRepository with security and rate limiting coverage.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from sqlalchemy.sql import func
from src.infrastructure.persistence.repositories.conversation_repository import (
    ConversationRepository,
)
from src.infrastructure.persistence.models.conversation_model import ConversationModel
from src.infrastructure.persistence.database import Database
from src.infrastructure.security.database_input_validator import SecurityError


@pytest.fixture
def mock_database():
    """Create mock database instance."""
    database = MagicMock(spec=Database)
    database.get_session = MagicMock()
    return database


@pytest.fixture
def conversation_repository(mock_database):
    """Create ConversationRepository instance with mocked dependencies."""
    return ConversationRepository(mock_database)


@pytest.fixture
def sample_conversation_data():
    """Sample conversation data for testing."""
    return {
        "child_id": str(uuid4()),
        "message": "Tell me a story about space!",
        "response": "Once upon a time, in a galaxy far away...",
    }


class TestConversationRepositoryCreate:
    """Test conversation creation functionality."""

    @pytest.mark.asyncio
    async def test_create_conversation_success(
        self, conversation_repository, mock_database, sample_conversation_data
    ):
        """Test successful conversation creation."""
        # Arrange
        mock_session = AsyncMock()
        mock_database.get_session.return_value.__aenter__.return_value = mock_session

        with patch(
            "src.infrastructure.persistence.repositories.conversation_repository.validate_database_operation",
            return_value={"data": sample_conversation_data},
        ):
            # Act
            conversation_id = await conversation_repository.create_conversation(
                **sample_conversation_data
            )

            # Assert
            assert conversation_id is not None
            assert isinstance(conversation_id, str)
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_conversation_empty_message(
        self, conversation_repository, mock_database
    ):
        """Test conversation creation with empty message."""
        # Arrange
        data = {
            "child_id": str(uuid4()),
            "message": "",
            "response": "Cannot process empty message",
        }

        with patch(
            "src.infrastructure.persistence.repositories.conversation_repository.validate_database_operation",
            side_effect=SecurityError("Empty message not allowed"),
        ):
            # Act & Assert
            with pytest.raises(ValueError, match="Invalid conversation data"):
                await conversation_repository.create_conversation(**data)

    @pytest.mark.asyncio
    async def test_create_conversation_security_violation(
        self, conversation_repository, mock_database
    ):
        """Test conversation creation with SQL injection attempt."""
        # Arrange
        malicious_data = {
            "child_id": str(uuid4()),
            "message": "'; DROP TABLE conversations; --",
            "response": "Nice try!",
        }

        with patch(
            "src.infrastructure.persistence.repositories.conversation_repository.validate_database_operation",
            side_effect=SecurityError("SQL injection detected"),
        ):
            # Act & Assert
            with pytest.raises(ValueError, match="Invalid conversation data"):
                await conversation_repository.create_conversation(**malicious_data)

    @pytest.mark.asyncio
    async def test_create_conversation_database_error(
        self, conversation_repository, mock_database, sample_conversation_data
    ):
        """Test conversation creation with database error."""
        # Arrange
        mock_session = AsyncMock()
        mock_session.commit.side_effect = Exception("Database connection lost")
        mock_database.get_session.return_value.__aenter__.return_value = mock_session

        with patch(
            "src.infrastructure.persistence.repositories.conversation_repository.validate_database_operation",
            return_value={"data": sample_conversation_data},
        ):
            # Act & Assert
            with pytest.raises(RuntimeError, match="Database error"):
                await conversation_repository.create_conversation(
                    **sample_conversation_data
                )


class TestConversationRepositoryHistory:
    """Test conversation history retrieval functionality."""

    @pytest.mark.asyncio
    async def test_get_conversation_history_success(
        self, conversation_repository, mock_database
    ):
        """Test successful conversation history retrieval."""
        # Arrange
        child_id = str(uuid4())

        # Create mock conversations
        conversations = []
        for i in range(5):
            mock_conv = MagicMock(spec=ConversationModel)
            mock_conv.id = str(uuid4())
            mock_conv.child_id = child_id
            mock_conv.message = f"Message {i}"
            mock_conv.response = f"Response {i}"
            mock_conv.created_at = datetime.utcnow() - timedelta(hours=i)
            conversations.append(mock_conv)

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = conversations
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        mock_database.get_session.return_value.__aenter__.return_value = mock_session

        # Act
        result = await conversation_repository.get_conversation_history(
            child_id, limit=5
        )

        # Assert
        assert len(result) == 5
        for i, conv in enumerate(result):
            assert conv["message"] == f"Message {i}"
            assert conv["response"] == f"Response {i}"
            assert "created_at" in conv

    @pytest.mark.asyncio
    async def test_get_conversation_history_with_limit(
        self, conversation_repository, mock_database
    ):
        """Test conversation history with custom limit."""
        # Arrange
        child_id = str(uuid4())
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        mock_database.get_session.return_value.__aenter__.return_value = mock_session

        # Act
        result = await conversation_repository.get_conversation_history(
            child_id, limit=20
        )

        # Assert
        assert result == []
        # Verify the query was executed with proper limit
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_conversation_history_invalid_limit(
        self, conversation_repository, mock_database
    ):
        """Test conversation history with invalid limit values."""
        child_id = str(uuid4())

        # Test negative limit
        with pytest.raises(ValueError, match="Limit must be between 1 and 100"):
            await conversation_repository.get_conversation_history(child_id, limit=-1)

        # Test zero limit
        with pytest.raises(ValueError, match="Limit must be between 1 and 100"):
            await conversation_repository.get_conversation_history(child_id, limit=0)

        # Test excessive limit
        with pytest.raises(ValueError, match="Limit must be between 1 and 100"):
            await conversation_repository.get_conversation_history(child_id, limit=101)

    @pytest.mark.asyncio
    async def test_get_conversation_history_database_error(
        self, conversation_repository, mock_database
    ):
        """Test conversation history retrieval with database error."""
        # Arrange
        child_id = str(uuid4())
        mock_session = AsyncMock()
        mock_session.execute.side_effect = Exception("Query timeout")

        mock_database.get_session.return_value.__aenter__.return_value = mock_session

        # Act & Assert
        with pytest.raises(RuntimeError, match="Database error"):
            await conversation_repository.get_conversation_history(child_id)


class TestConversationRepositoryCount:
    """Test conversation count functionality for rate limiting."""

    @pytest.mark.asyncio
    async def test_get_conversation_count_success(
        self, conversation_repository, mock_database
    ):
        """Test successful conversation count retrieval."""
        # Arrange
        child_id = str(uuid4())
        expected_count = 42

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = expected_count
        mock_session.execute.return_value = mock_result

        mock_database.get_session.return_value.__aenter__.return_value = mock_session

        # Act
        count = await conversation_repository.get_conversation_count(child_id, hours=24)

        # Assert
        assert count == expected_count
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_conversation_count_no_conversations(
        self, conversation_repository, mock_database
    ):
        """Test conversation count when no conversations exist."""
        # Arrange
        child_id = str(uuid4())

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = None  # No conversations
        mock_session.execute.return_value = mock_result

        mock_database.get_session.return_value.__aenter__.return_value = mock_session

        # Act
        count = await conversation_repository.get_conversation_count(child_id, hours=24)

        # Assert
        assert count == 0

    @pytest.mark.asyncio
    async def test_get_conversation_count_invalid_hours(
        self, conversation_repository, mock_database
    ):
        """Test conversation count with invalid hour values."""
        child_id = str(uuid4())

        # Test negative hours
        with pytest.raises(ValueError, match="Hours must be between 1 and 168"):
            await conversation_repository.get_conversation_count(child_id, hours=-1)

        # Test zero hours
        with pytest.raises(ValueError, match="Hours must be between 1 and 168"):
            await conversation_repository.get_conversation_count(child_id, hours=0)

        # Test excessive hours (more than 1 week)
        with pytest.raises(ValueError, match="Hours must be between 1 and 168"):
            await conversation_repository.get_conversation_count(child_id, hours=169)

    @pytest.mark.asyncio
    async def test_get_conversation_count_database_error(
        self, conversation_repository, mock_database
    ):
        """Test conversation count with database error."""
        # Arrange
        child_id = str(uuid4())
        mock_session = AsyncMock()
        mock_session.execute.side_effect = Exception("Database locked")

        mock_database.get_session.return_value.__aenter__.return_value = mock_session

        # Act & Assert
        with pytest.raises(RuntimeError, match="Database error"):
            await conversation_repository.get_conversation_count(child_id, hours=24)


class TestConversationRepositoryDeletion:
    """Test conversation deletion for COPPA compliance."""

    @pytest.mark.asyncio
    async def test_delete_old_conversations_success(
        self, conversation_repository, mock_database
    ):
        """Test successful deletion of old conversations."""
        # Arrange
        old_conversations = []
        for i in range(5):
            mock_conv = MagicMock(spec=ConversationModel)
            mock_conv.id = str(uuid4())
            mock_conv.created_at = datetime.utcnow() - timedelta(days=100)
            old_conversations.append(mock_conv)

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = old_conversations
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        mock_database.get_session.return_value.__aenter__.return_value = mock_session

        # Act
        deleted_count = await conversation_repository.delete_old_conversations(days=90)

        # Assert
        assert deleted_count == 5
        assert mock_session.delete.call_count == 5
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_old_conversations_none_found(
        self, conversation_repository, mock_database
    ):
        """Test deletion when no old conversations exist."""
        # Arrange
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        mock_database.get_session.return_value.__aenter__.return_value = mock_session

        # Act
        deleted_count = await conversation_repository.delete_old_conversations(days=90)

        # Assert
        assert deleted_count == 0
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_old_conversations_invalid_days(
        self, conversation_repository, mock_database
    ):
        """Test deletion with invalid day values."""
        # Test zero days
        with pytest.raises(ValueError, match="Days must be positive"):
            await conversation_repository.delete_old_conversations(days=0)

        # Test negative days
        with pytest.raises(ValueError, match="Days must be positive"):
            await conversation_repository.delete_old_conversations(days=-1)

    @pytest.mark.asyncio
    async def test_delete_old_conversations_database_error(
        self, conversation_repository, mock_database
    ):
        """Test deletion with database error."""
        # Arrange
        mock_session = AsyncMock()
        mock_session.execute.side_effect = Exception(
            "Cannot delete: foreign key constraint"
        )

        mock_database.get_session.return_value.__aenter__.return_value = mock_session

        # Act & Assert
        with pytest.raises(RuntimeError, match="Failed to delete old conversations"):
            await conversation_repository.delete_old_conversations(days=90)


class TestConversationRepositoryEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_create_conversation_very_long_message(
        self, conversation_repository, mock_database
    ):
        """Test conversation creation with very long message."""
        # Arrange
        long_message = "x" * 10000  # 10k character message
        data = {
            "child_id": str(uuid4()),
            "message": long_message,
            "response": "That's a very long message!",
        }

        mock_session = AsyncMock()
        mock_database.get_session.return_value.__aenter__.return_value = mock_session

        with patch(
            "src.infrastructure.persistence.repositories.conversation_repository.validate_database_operation",
            return_value={"data": data},
        ):
            # Act
            conversation_id = await conversation_repository.create_conversation(**data)

            # Assert
            assert conversation_id is not None

    @pytest.mark.asyncio
    async def test_get_conversation_history_with_metadata(
        self, conversation_repository, mock_database
    ):
        """Test conversation history including metadata field."""
        # Arrange
        child_id = str(uuid4())

        mock_conv = MagicMock(spec=ConversationModel)
        mock_conv.id = str(uuid4())
        mock_conv.child_id = child_id
        mock_conv.message = "Test message"
        mock_conv.response = "Test response"
        mock_conv.created_at = datetime.utcnow()
        mock_conv.metadata = {"emotion": "happy", "topic": "story"}

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_conv]
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        mock_database.get_session.return_value.__aenter__.return_value = mock_session

        # Act
        result = await conversation_repository.get_conversation_history(
            child_id, limit=1
        )

        # Assert
        assert len(result) == 1
        assert result[0]["metadata"] == {"emotion": "happy", "topic": "story"}
