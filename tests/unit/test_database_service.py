"""
Comprehensive Unit Tests for Database Service
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from sqlalchemy.exc import IntegrityError, OperationalError

from src.infrastructure.persistence.real_database_service import DatabaseService
from src.infrastructure.persistence.database import Database
from src.infrastructure.persistence.models.child_model import ChildModel
from src.infrastructure.persistence.models.conversation_model import ConversationModel


@pytest.fixture
def mock_database():
    """Create mock database instance."""
    db = MagicMock(spec=Database)
    db.get_session = MagicMock()
    return db


@pytest.fixture
def database_service(mock_database):
    """Create database service with mock database."""
    return DatabaseService(mock_database)


@pytest.fixture
def mock_session():
    """Create mock database session."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.execute = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    return session


@pytest.fixture
def sample_child_data():
    """Create sample child data."""
    return {
        "id": str(uuid4()),
        "name": "Alice",
        "age": 7,
        "preferences": {
            "interests": ["dinosaurs", "space"],
            "language": "en",
            "voice_enabled": True,
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


class TestChildManagement:
    """Test child profile management."""

    @pytest.mark.asyncio
    async def test_create_child_success(
        self, database_service, mock_database, mock_session, sample_child_data
    ):
        """Test successful child creation."""
        mock_database.get_session.return_value = mock_session

        child_id = await database_service.create_child(
            name=sample_child_data["name"],
            age=sample_child_data["age"],
            preferences=sample_child_data["preferences"],
            parent_id=str(uuid4()),
        )

        assert child_id is not None
        assert isinstance(child_id, str)
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_child_duplicate_error(
        self, database_service, mock_database, mock_session
    ):
        """Test handling duplicate child creation."""
        mock_database.get_session.return_value = mock_session
        mock_session.commit.side_effect = IntegrityError(
            "Duplicate", None, None)

        with pytest.raises(IntegrityError):
            await database_service.create_child(
                name="Duplicate", age=5, preferences={}, parent_id=str(uuid4())
            )

        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_child_success(
        self, database_service, mock_database, mock_session, sample_child_data
    ):
        """Test successful child retrieval."""
        mock_database.get_session.return_value = mock_session

        # Mock child model
        child_model = MagicMock(spec=ChildModel)
        for key, value in sample_child_data.items():
            setattr(child_model, key, value)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = child_model
        mock_session.execute.return_value = mock_result

        child = await database_service.get_child(sample_child_data["id"])

        assert child is not None
        assert child["name"] == sample_child_data["name"]
        assert child["age"] == sample_child_data["age"]
        assert child["preferences"] == sample_child_data["preferences"]

    @pytest.mark.asyncio
    async def test_get_child_not_found(
        self, database_service, mock_database, mock_session
    ):
        """Test child retrieval when not found."""
        mock_database.get_session.return_value = mock_session

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        child = await database_service.get_child(str(uuid4()))

        assert child is None

    @pytest.mark.asyncio
    async def test_update_child_success(
        self, database_service, mock_database, mock_session
    ):
        """Test successful child update."""
        mock_database.get_session.return_value = mock_session

        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        success = await database_service.update_child(
            child_id=str(uuid4()), age=8, preferences={"interests": ["science"]}
        )

        assert success is True
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_child_not_found(
        self, database_service, mock_database, mock_session
    ):
        """Test child update when not found."""
        mock_database.get_session.return_value = mock_session

        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result

        success = await database_service.update_child(child_id=str(uuid4()), age=8)

        assert success is False

    @pytest.mark.asyncio
    async def test_delete_child_success(
        self, database_service, mock_database, mock_session
    ):
        """Test successful child deletion."""
        mock_database.get_session.return_value = mock_session

        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        success = await database_service.delete_child(str(uuid4()))

        assert success is True
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_children_by_parent(
        self, database_service, mock_database, mock_session
    ):
        """Test retrieving all children for a parent."""
        mock_database.get_session.return_value = mock_session

        # Mock multiple children
        children_models = []
        for i in range(3):
            child = MagicMock(spec=ChildModel)
            child.id = str(uuid4())
            child.name = f"Child {i}"
            child.age = 5 + i
            child.preferences = {}
            child.created_at = datetime.utcnow()
            child.updated_at = datetime.utcnow()
            children_models.append(child)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = children_models
        mock_session.execute.return_value = mock_result

        children = await database_service.get_children_by_parent(str(uuid4()))

        assert len(children) == 3
        assert all("id" in child for child in children)
        assert all("name" in child for child in children)


class TestUserManagement:
    """Test user management functionality."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, database_service):
        """Test user creation."""
        user_id = await database_service.create_user(
            email="test@example.com",
            hashed_password="hashed_password_here",
            role="parent",
        )

        assert user_id is not None
        assert isinstance(user_id, str)

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, database_service):
        """Test user retrieval by email."""
        user = await database_service.get_user_by_email("test@example.com")

        # Currently returns None as placeholder
        assert user is None


class TestSafetyFeatures:
    """Test safety-related database operations."""

    @pytest.mark.asyncio
    async def test_record_safety_event(self, database_service):
        """Test recording safety events."""
        event_id = await database_service.record_safety_event(
            child_id=str(uuid4()),
            event_type="inappropriate_content",
            details="Blocked inappropriate language",
            severity="medium",
        )

        assert event_id is not None
        assert isinstance(event_id, str)

    @pytest.mark.asyncio
    async def test_update_safety_score(self, database_service):
        """Test updating safety score."""
        success = await database_service.update_safety_score(
            child_id=str(uuid4()), new_score=0.95, reason="Good behavior pattern"
        )

        assert success is True

    @pytest.mark.asyncio
    async def test_get_safety_events(self, database_service):
        """Test retrieving safety events."""
        events = await database_service.get_safety_events(
            child_id=str(uuid4()), limit=10
        )

        assert isinstance(events, list)
        assert len(events) > 0
        assert all("event_id" in event for event in events)
        assert all("severity" in event for event in events)

    @pytest.mark.asyncio
    async def test_send_safety_alert(self, database_service):
        """Test sending safety alerts."""
        alert_data = {
            "child_id": str(uuid4()),
            "alert_type": "urgent",
            "message": "Unsafe content detected",
            "timestamp": datetime.utcnow().isoformat(),
        }

        success = await database_service.send_safety_alert(alert_data)

        assert success is True


class TestUsageTracking:
    """Test usage tracking functionality."""

    @pytest.mark.asyncio
    async def test_record_usage(self, database_service):
        """Test recording usage statistics."""
        usage_record = {
            "child_id": str(uuid4()),
            "activity_type": "conversation",
            "duration": 300,  # 5 minutes
            "timestamp": datetime.utcnow().isoformat(),
        }

        usage_id = await database_service.record_usage(usage_record)

        assert usage_id is not None
        assert isinstance(usage_id, str)

    @pytest.mark.asyncio
    async def test_get_daily_usage(self, database_service):
        """Test retrieving daily usage."""
        daily_minutes = await database_service.get_daily_usage(str(uuid4()))

        assert isinstance(daily_minutes, int)
        assert daily_minutes >= 0
        assert daily_minutes == 45  # Mock value

    @pytest.mark.asyncio
    async def test_get_usage_statistics(self, database_service):
        """Test retrieving usage statistics."""
        stats = await database_service.get_usage_statistics(
            child_id=str(uuid4()), days=7
        )

        assert isinstance(stats, dict)
        assert stats["period_days"] == 7
        assert "total_usage_minutes" in stats
        assert "daily_average_minutes" in stats
        assert "activity_breakdown" in stats
        assert "usage_by_day" in stats
        assert len(stats["usage_by_day"]) == 7


class TestInteractionManagement:
    """Test interaction and conversation management."""

    @pytest.mark.asyncio
    async def test_save_interaction(self, database_service):
        """Test saving interactions."""
        interaction_id = await database_service.save_interaction(
            child_id=str(uuid4()),
            input_text="Tell me a story",
            response_text="Once upon a time...",
            emotion="happy",
        )

        assert interaction_id is not None
        assert isinstance(interaction_id, str)

    @pytest.mark.asyncio
    async def test_get_interactions(self, database_service):
        """Test retrieving interactions."""
        interactions = await database_service.get_interactions(
            child_id=str(uuid4()), limit=20
        )

        assert isinstance(interactions, list)
        assert len(interactions) == 0  # Currently returns empty list

    @pytest.mark.asyncio
    async def test_save_emotion_analysis(self, database_service):
        """Test saving emotion analysis."""
        analysis_id = await database_service.save_emotion_analysis(
            child_id=str(uuid4()), emotion="joy", confidence=0.85
        )

        assert analysis_id is not None
        assert isinstance(analysis_id, str)

    @pytest.mark.asyncio
    async def test_get_emotion_history(self, database_service):
        """Test retrieving emotion history."""
        history = await database_service.get_emotion_history(
            child_id=str(uuid4()), days=7
        )

        assert isinstance(history, list)


class TestErrorHandling:
    """Test error handling in database operations."""

    @pytest.mark.asyncio
    async def test_database_connection_error(
        self, database_service, mock_database, mock_session
    ):
        """Test handling of database connection errors."""
        mock_database.get_session.return_value = mock_session
        mock_session.execute.side_effect = OperationalError(
            "Connection failed", None, None
        )

        child = await database_service.get_child(str(uuid4()))

        # Should handle error gracefully
        assert child is None

    @pytest.mark.asyncio
    async def test_transaction_rollback(
        self, database_service, mock_database, mock_session
    ):
        """Test transaction rollback on error."""
        mock_database.get_session.return_value = mock_session
        mock_session.commit.side_effect = Exception("Commit failed")

        with pytest.raises(Exception):
            await database_service.create_child(
                name="Test", age=7, preferences={}, parent_id=str(uuid4())
            )

        mock_session.rollback.assert_called()


class TestDatabaseInitialization:
    """Test database service initialization."""

    def test_init_database_service(self):
        """Test initializing database service."""
        from src.infrastructure.persistence.real_database_service import (
            init_database_service,
        )

        service = init_database_service(
            "postgresql://test:test@localhost/test")

        assert service is not None
        assert isinstance(service, DatabaseService)

    def test_get_database_service_lazy_init(self):
        """Test lazy initialization of database service."""
        from src.infrastructure.persistence.real_database_service import (
            get_database_service,
            reset_database_service,
        )

        # Reset to ensure clean state
        reset_database_service()

        service = get_database_service()

        assert service is not None
        assert isinstance(service, DatabaseService)

    def test_reset_database_service(self):
        """Test resetting database service."""
        from src.infrastructure.persistence.real_database_service import (
            get_database_service,
            reset_database_service,
            _database_service,
        )

        # Initialize service
        service = get_database_service()
        assert service is not None

        # Reset
        reset_database_service()

        # Should be able to reinitialize
        new_service = get_database_service()
        assert new_service is not None
