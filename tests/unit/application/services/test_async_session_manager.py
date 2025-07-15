"""
Comprehensive test suite for application/services/async_session_manager.py

This test file validates the AsyncSessionManager including
session creation, retrieval, updates, expiration handling, and 
background cleanup processes for child-safe session management.
"""

import pytest
import asyncio
import logging
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from uuid import uuid4

from src.application.services.async_session_manager import (
    AsyncSessionManager,
    get_session_manager,
    get_session_storage
)
from src.application.services.session.session_models import (
    AsyncSessionData,
    SessionStatus,
    SessionStats
)
from src.application.services.session.session_storage import SessionStorage


class MockSessionStorage:
    """Mock implementation of SessionStorage for testing."""
    
    def __init__(self):
        self.sessions = {}
        self.store_session_called = False
        self.retrieve_session_called = False
        self.get_child_sessions_called = False
        self.get_session_count_called = False
        self.get_active_session_count_called = False
        self.cleanup_expired_sessions_called = False
        self.should_raise_exception = False
        self.exception_message = "Storage error"
        
    async def store_session(self, session: AsyncSessionData) -> None:
        """Mock store_session implementation."""
        self.store_session_called = True
        if self.should_raise_exception:
            raise Exception(self.exception_message)
        self.sessions[session.session_id] = session
    
    async def retrieve_session(self, session_id: str) -> Optional[AsyncSessionData]:
        """Mock retrieve_session implementation."""
        self.retrieve_session_called = True
        if self.should_raise_exception:
            raise Exception(self.exception_message)
        return self.sessions.get(session_id)
    
    async def get_child_sessions(self, child_id: str) -> List[AsyncSessionData]:
        """Mock get_child_sessions implementation."""
        self.get_child_sessions_called = True
        if self.should_raise_exception:
            raise Exception(self.exception_message)
        return [session for session in self.sessions.values() if session.child_id == child_id]
    
    async def get_session_count(self) -> int:
        """Mock get_session_count implementation."""
        self.get_session_count_called = True
        if self.should_raise_exception:
            raise Exception(self.exception_message)
        return len(self.sessions)
    
    async def get_active_session_count(self) -> int:
        """Mock get_active_session_count implementation."""
        self.get_active_session_count_called = True
        if self.should_raise_exception:
            raise Exception(self.exception_message)
        return len([s for s in self.sessions.values() if s.status == SessionStatus.ACTIVE])
    
    async def cleanup_expired_sessions(self, timeout_minutes: int) -> int:
        """Mock cleanup_expired_sessions implementation."""
        self.cleanup_expired_sessions_called = True
        if self.should_raise_exception:
            raise Exception(self.exception_message)
        
        expired_count = 0
        to_remove = []
        for session_id, session in self.sessions.items():
            if session.is_expired(timeout_minutes):
                to_remove.append(session_id)
                expired_count += 1
        
        for session_id in to_remove:
            del self.sessions[session_id]
        
        return expired_count


@pytest.fixture
def mock_storage():
    """Create a mock session storage."""
    return MockSessionStorage()


@pytest.fixture
def session_manager(mock_storage):
    """Create AsyncSessionManager with mock storage."""
    manager = AsyncSessionManager(default_timeout_minutes=30)
    manager.storage = mock_storage
    return manager


@pytest.fixture
def sample_child_id():
    """Create a sample child ID."""
    return "child_123"


@pytest.fixture
def sample_session_data():
    """Create sample session data."""
    return {
        "current_activity": "story_time",
        "preferences": {"voice_speed": 1.0, "volume": 0.8},
        "progress": {"stories_completed": 2}
    }


@pytest.fixture
def sample_metadata():
    """Create sample metadata."""
    return {
        "device_type": "tablet",
        "app_version": "1.0.0",
        "language": "en-US"
    }


class TestAsyncSessionManager:
    """Test suite for AsyncSessionManager."""

    def test_init_default_timeout(self):
        """Test initialization with default timeout."""
        manager = AsyncSessionManager()
        assert manager.default_timeout == 30

    def test_init_custom_timeout(self):
        """Test initialization with custom timeout."""
        manager = AsyncSessionManager(default_timeout_minutes=60)
        assert manager.default_timeout == 60

    def test_init_creates_storage(self):
        """Test that initialization creates storage."""
        manager = AsyncSessionManager()
        assert manager.storage is not None
        assert isinstance(manager.storage, SessionStorage)

    def test_init_cleanup_task_none(self):
        """Test that cleanup task is initially None."""
        manager = AsyncSessionManager()
        assert manager._cleanup_task is None

    @pytest.mark.asyncio
    async def test_create_session_success(self, session_manager, sample_child_id, sample_session_data, sample_metadata):
        """Test successful session creation."""
        # Act
        session = await session_manager.create_session(
            child_id=sample_child_id,
            initial_data=sample_session_data,
            metadata=sample_metadata
        )
        
        # Assert
        assert isinstance(session, AsyncSessionData)
        assert session.child_id == sample_child_id
        assert session.data == sample_session_data
        assert session.metadata == sample_metadata
        assert session.status == SessionStatus.ACTIVE
        assert session.session_id is not None
        assert session.interaction_count == 0
        assert session.safety_score == 1.0
        
        # Verify storage was called
        assert session_manager.storage.store_session_called

    @pytest.mark.asyncio
    async def test_create_session_with_defaults(self, session_manager, sample_child_id):
        """Test session creation with default values."""
        # Act
        session = await session_manager.create_session(child_id=sample_child_id)
        
        # Assert
        assert session.child_id == sample_child_id
        assert session.data == {}
        assert session.metadata == {}
        assert session.status == SessionStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_create_session_storage_error(self, session_manager, sample_child_id):
        """Test handling of storage errors during session creation."""
        # Arrange
        session_manager.storage.should_raise_exception = True
        session_manager.storage.exception_message = "Storage error"
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await session_manager.create_session(child_id=sample_child_id)
        
        assert "Storage error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_session_success(self, session_manager, sample_child_id, sample_session_data):
        """Test successful session retrieval."""
        # Arrange
        created_session = await session_manager.create_session(
            child_id=sample_child_id,
            initial_data=sample_session_data
        )
        
        # Act
        retrieved_session = await session_manager.get_session(created_session.session_id)
        
        # Assert
        assert retrieved_session is not None
        assert retrieved_session.session_id == created_session.session_id
        assert retrieved_session.child_id == sample_child_id
        assert retrieved_session.data == sample_session_data
        assert retrieved_session.status == SessionStatus.ACTIVE
        
        # Verify activity was updated
        assert retrieved_session.interaction_count == 1

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, session_manager):
        """Test retrieval of non-existent session."""
        # Act
        session = await session_manager.get_session("nonexistent_session_id")
        
        # Assert
        assert session is None

    @pytest.mark.asyncio
    async def test_get_session_expired(self, session_manager, sample_child_id):
        """Test retrieval of expired session."""
        # Arrange
        created_session = await session_manager.create_session(child_id=sample_child_id)
        
        # Manually expire the session
        past_time = datetime.utcnow() - timedelta(minutes=60)
        created_session.last_activity = past_time
        await session_manager.storage.store_session(created_session)
        
        # Act
        retrieved_session = await session_manager.get_session(created_session.session_id)
        
        # Assert
        assert retrieved_session is None
        
        # Verify session status was updated to expired
        stored_session = await session_manager.storage.retrieve_session(created_session.session_id)
        assert stored_session.status == SessionStatus.EXPIRED

    @pytest.mark.asyncio
    async def test_update_session_success(self, session_manager, sample_child_id):
        """Test successful session update."""
        # Arrange
        created_session = await session_manager.create_session(child_id=sample_child_id)
        
        data_updates = {"new_field": "new_value"}
        metadata_updates = {"updated_field": "updated_value"}
        
        # Act
        result = await session_manager.update_session(
            session_id=created_session.session_id,
            data_updates=data_updates,
            metadata_updates=metadata_updates
        )
        
        # Assert
        assert result is True
        
        # Verify updates were applied
        updated_session = await session_manager.storage.retrieve_session(created_session.session_id)
        assert updated_session.data["new_field"] == "new_value"
        assert updated_session.metadata["updated_field"] == "updated_value"

    @pytest.mark.asyncio
    async def test_update_session_not_found(self, session_manager):
        """Test update of non-existent session."""
        # Act
        result = await session_manager.update_session(
            session_id="nonexistent_session_id",
            data_updates={"test": "value"}
        )
        
        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_update_session_expired(self, session_manager, sample_child_id):
        """Test update of expired session."""
        # Arrange
        created_session = await session_manager.create_session(child_id=sample_child_id)
        
        # Manually expire the session
        past_time = datetime.utcnow() - timedelta(minutes=60)
        created_session.last_activity = past_time
        await session_manager.storage.store_session(created_session)
        
        # Act
        result = await session_manager.update_session(
            session_id=created_session.session_id,
            data_updates={"test": "value"}
        )
        
        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_update_session_data_only(self, session_manager, sample_child_id):
        """Test updating session data only."""
        # Arrange
        created_session = await session_manager.create_session(child_id=sample_child_id)
        
        # Act
        result = await session_manager.update_session(
            session_id=created_session.session_id,
            data_updates={"data_field": "data_value"}
        )
        
        # Assert
        assert result is True
        
        updated_session = await session_manager.storage.retrieve_session(created_session.session_id)
        assert updated_session.data["data_field"] == "data_value"

    @pytest.mark.asyncio
    async def test_update_session_metadata_only(self, session_manager, sample_child_id):
        """Test updating session metadata only."""
        # Arrange
        created_session = await session_manager.create_session(child_id=sample_child_id)
        
        # Act
        result = await session_manager.update_session(
            session_id=created_session.session_id,
            metadata_updates={"meta_field": "meta_value"}
        )
        
        # Assert
        assert result is True
        
        updated_session = await session_manager.storage.retrieve_session(created_session.session_id)
        assert updated_session.metadata["meta_field"] == "meta_value"

    @pytest.mark.asyncio
    async def test_end_session_success(self, session_manager, sample_child_id):
        """Test successful session termination."""
        # Arrange
        created_session = await session_manager.create_session(child_id=sample_child_id)
        
        # Act
        result = await session_manager.end_session(created_session.session_id)
        
        # Assert
        assert result is True
        
        # Verify session status was updated
        ended_session = await session_manager.storage.retrieve_session(created_session.session_id)
        assert ended_session.status == SessionStatus.ENDED

    @pytest.mark.asyncio
    async def test_end_session_not_found(self, session_manager):
        """Test ending non-existent session."""
        # Act
        result = await session_manager.end_session("nonexistent_session_id")
        
        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_get_child_sessions_success(self, session_manager, sample_child_id):
        """Test retrieval of child sessions."""
        # Arrange
        session1 = await session_manager.create_session(child_id=sample_child_id)
        session2 = await session_manager.create_session(child_id=sample_child_id)
        session3 = await session_manager.create_session(child_id="other_child")
        
        # Act
        child_sessions = await session_manager.get_child_sessions(sample_child_id)
        
        # Assert
        assert len(child_sessions) == 2
        session_ids = [s.session_id for s in child_sessions]
        assert session1.session_id in session_ids
        assert session2.session_id in session_ids
        assert session3.session_id not in session_ids

    @pytest.mark.asyncio
    async def test_get_child_sessions_filters_inactive(self, session_manager, sample_child_id):
        """Test that get_child_sessions filters out inactive sessions."""
        # Arrange
        active_session = await session_manager.create_session(child_id=sample_child_id)
        ended_session = await session_manager.create_session(child_id=sample_child_id)
        
        # End one session
        await session_manager.end_session(ended_session.session_id)
        
        # Act
        child_sessions = await session_manager.get_child_sessions(sample_child_id)
        
        # Assert
        assert len(child_sessions) == 1
        assert child_sessions[0].session_id == active_session.session_id

    @pytest.mark.asyncio
    async def test_get_child_sessions_filters_expired(self, session_manager, sample_child_id):
        """Test that get_child_sessions filters out expired sessions."""
        # Arrange
        active_session = await session_manager.create_session(child_id=sample_child_id)
        expired_session = await session_manager.create_session(child_id=sample_child_id)
        
        # Manually expire one session
        past_time = datetime.utcnow() - timedelta(minutes=60)
        expired_session.last_activity = past_time
        await session_manager.storage.store_session(expired_session)
        
        # Act
        child_sessions = await session_manager.get_child_sessions(sample_child_id)
        
        # Assert
        assert len(child_sessions) == 1
        assert child_sessions[0].session_id == active_session.session_id

    @pytest.mark.asyncio
    async def test_get_session_stats_success(self, session_manager, sample_child_id):
        """Test retrieval of session statistics."""
        # Arrange
        await session_manager.create_session(child_id=sample_child_id)
        await session_manager.create_session(child_id="other_child")
        
        # Act
        stats = await session_manager.get_session_stats()
        
        # Assert
        assert isinstance(stats, SessionStats)
        assert stats.total_sessions == 2
        assert stats.active_sessions == 2
        assert stats.expired_sessions == 0
        assert stats.average_duration_minutes == 0.0  # Mock implementation
        assert stats.total_interactions == 0
        assert stats.average_safety_score == 1.0

    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions_success(self, session_manager, sample_child_id):
        """Test manual cleanup of expired sessions."""
        # Arrange
        active_session = await session_manager.create_session(child_id=sample_child_id)
        expired_session = await session_manager.create_session(child_id="other_child")
        
        # Manually expire one session
        past_time = datetime.utcnow() - timedelta(minutes=60)
        expired_session.last_activity = past_time
        await session_manager.storage.store_session(expired_session)
        
        # Act
        cleaned_count = await session_manager.cleanup_expired_sessions()
        
        # Assert
        assert cleaned_count == 1
        assert session_manager.storage.cleanup_expired_sessions_called

    @pytest.mark.asyncio
    async def test_start_cleanup_task(self, session_manager):
        """Test starting background cleanup task."""
        # Act
        await session_manager.start_cleanup_task()
        
        # Assert
        assert session_manager._cleanup_task is not None
        assert not session_manager._cleanup_task.done()
        
        # Cleanup
        await session_manager.stop_cleanup_task()

    @pytest.mark.asyncio
    async def test_start_cleanup_task_already_running(self, session_manager):
        """Test starting cleanup task when already running."""
        # Arrange
        await session_manager.start_cleanup_task()
        first_task = session_manager._cleanup_task
        
        # Act
        await session_manager.start_cleanup_task()
        
        # Assert
        assert session_manager._cleanup_task is first_task  # Same task
        
        # Cleanup
        await session_manager.stop_cleanup_task()

    @pytest.mark.asyncio
    async def test_stop_cleanup_task(self, session_manager):
        """Test stopping background cleanup task."""
        # Arrange
        await session_manager.start_cleanup_task()
        
        # Act
        await session_manager.stop_cleanup_task()
        
        # Assert
        assert session_manager._cleanup_task.cancelled()

    @pytest.mark.asyncio
    async def test_stop_cleanup_task_not_running(self, session_manager):
        """Test stopping cleanup task when not running."""
        # Act (should not raise exception)
        await session_manager.stop_cleanup_task()
        
        # Assert
        assert session_manager._cleanup_task is None

    @pytest.mark.asyncio
    async def test_concurrent_session_operations(self, session_manager, sample_child_id):
        """Test concurrent session operations."""
        # Arrange
        tasks = []
        
        # Create multiple sessions concurrently
        for i in range(5):
            task = session_manager.create_session(
                child_id=f"child_{i}",
                initial_data={"test": f"data_{i}"}
            )
            tasks.append(task)
        
        # Act
        sessions = await asyncio.gather(*tasks)
        
        # Assert
        assert len(sessions) == 5
        assert all(isinstance(s, AsyncSessionData) for s in sessions)
        assert len(set(s.session_id for s in sessions)) == 5  # All unique

    @pytest.mark.asyncio
    async def test_session_activity_tracking(self, session_manager, sample_child_id):
        """Test that session activity is properly tracked."""
        # Arrange
        session = await session_manager.create_session(child_id=sample_child_id)
        original_activity = session.last_activity
        original_count = session.interaction_count
        
        # Wait a bit to ensure timestamp difference
        await asyncio.sleep(0.01)
        
        # Act
        retrieved_session = await session_manager.get_session(session.session_id)
        
        # Assert
        assert retrieved_session.last_activity > original_activity
        assert retrieved_session.interaction_count == original_count + 1

    @pytest.mark.asyncio
    async def test_session_timeout_behavior(self, session_manager, sample_child_id):
        """Test session timeout behavior with different timeout values."""
        # Arrange
        session = await session_manager.create_session(child_id=sample_child_id)
        
        # Set custom timeout
        session_manager.default_timeout = 1  # 1 minute timeout
        
        # Manually set old activity time
        past_time = datetime.utcnow() - timedelta(minutes=2)
        session.last_activity = past_time
        await session_manager.storage.store_session(session)
        
        # Act
        retrieved_session = await session_manager.get_session(session.session_id)
        
        # Assert
        assert retrieved_session is None  # Should be expired

    @pytest.mark.asyncio
    async def test_session_data_isolation(self, session_manager):
        """Test that session data is properly isolated."""
        # Arrange
        session1 = await session_manager.create_session(
            child_id="child1",
            initial_data={"user_data": "data1"}
        )
        session2 = await session_manager.create_session(
            child_id="child2",
            initial_data={"user_data": "data2"}
        )
        
        # Act
        await session_manager.update_session(
            session_id=session1.session_id,
            data_updates={"new_field": "value1"}
        )
        
        # Assert
        retrieved_session1 = await session_manager.get_session(session1.session_id)
        retrieved_session2 = await session_manager.get_session(session2.session_id)
        
        assert retrieved_session1.data["new_field"] == "value1"
        assert "new_field" not in retrieved_session2.data
        assert retrieved_session2.data["user_data"] == "data2"

    @pytest.mark.asyncio
    async def test_large_session_data_handling(self, session_manager, sample_child_id):
        """Test handling of large session data."""
        # Arrange
        large_data = {
            f"key_{i}": f"value_{i}" * 100
            for i in range(100)
        }
        
        # Act
        session = await session_manager.create_session(
            child_id=sample_child_id,
            initial_data=large_data
        )
        
        # Assert
        retrieved_session = await session_manager.get_session(session.session_id)
        assert retrieved_session.data == large_data

    @pytest.mark.asyncio
    async def test_session_safety_score_tracking(self, session_manager, sample_child_id):
        """Test that session safety score is properly tracked."""
        # Arrange
        session = await session_manager.create_session(child_id=sample_child_id)
        
        # Act
        await session_manager.update_session(
            session_id=session.session_id,
            metadata_updates={"safety_check": "passed"}
        )
        
        # Assert
        retrieved_session = await session_manager.get_session(session.session_id)
        assert retrieved_session.safety_score == 1.0  # Default safe score

    @pytest.mark.asyncio
    async def test_error_handling_preserves_state(self, session_manager, sample_child_id):
        """Test that errors don't corrupt session manager state."""
        # Arrange
        session = await session_manager.create_session(child_id=sample_child_id)
        
        # Cause storage error
        session_manager.storage.should_raise_exception = True
        
        # Act & Assert
        with pytest.raises(Exception):
            await session_manager.update_session(
                session_id=session.session_id,
                data_updates={"test": "value"}
            )
        
        # Reset error condition
        session_manager.storage.should_raise_exception = False
        
        # Should still be able to retrieve session
        retrieved_session = await session_manager.get_session(session.session_id)
        assert retrieved_session is not None


class TestSessionData:
    """Test suite for AsyncSessionData model."""

    def test_session_data_creation(self):
        """Test AsyncSessionData creation with defaults."""
        session = AsyncSessionData(child_id="test_child")
        
        assert session.child_id == "test_child"
        assert session.session_id is not None
        assert session.status == SessionStatus.ACTIVE
        assert session.data == {}
        assert session.metadata == {}
        assert session.interaction_count == 0
        assert session.safety_score == 1.0

    def test_session_data_is_expired(self):
        """Test session expiration logic."""
        session = AsyncSessionData(child_id="test_child")
        
        # Fresh session should not be expired
        assert not session.is_expired(30)
        
        # Manually set old activity
        session.last_activity = datetime.utcnow() - timedelta(minutes=60)
        assert session.is_expired(30)

    def test_session_data_is_expired_non_active(self):
        """Test that non-active sessions are considered expired."""
        session = AsyncSessionData(child_id="test_child")
        session.status = SessionStatus.ENDED
        
        assert session.is_expired(30)

    def test_session_data_update_activity(self):
        """Test activity update functionality."""
        session = AsyncSessionData(child_id="test_child")
        original_activity = session.last_activity
        original_count = session.interaction_count
        
        # Update activity
        session.update_activity()
        
        assert session.last_activity >= original_activity
        assert session.interaction_count == original_count + 1

    def test_session_data_get_duration(self):
        """Test session duration calculation."""
        session = AsyncSessionData(child_id="test_child")
        
        # Set specific times
        session.created_at = datetime.utcnow() - timedelta(minutes=30)
        session.last_activity = datetime.utcnow()
        
        duration = session.get_session_duration()
        assert duration.total_seconds() >= 30 * 60  # At least 30 minutes

    def test_session_data_to_dict(self):
        """Test session data serialization."""
        session = AsyncSessionData(
            child_id="test_child",
            data={"key": "value"},
            metadata={"meta": "data"}
        )
        
        session_dict = session.to_dict()
        
        assert session_dict["child_id"] == "test_child"
        assert session_dict["data"] == {"key": "value"}
        assert session_dict["metadata"] == {"meta": "data"}
        assert session_dict["status"] == "active"
        assert "created_at" in session_dict
        assert "last_activity" in session_dict


class TestSessionStatus:
    """Test suite for SessionStatus enum."""

    def test_session_status_values(self):
        """Test SessionStatus enum values."""
        assert SessionStatus.ACTIVE == "active"
        assert SessionStatus.EXPIRED == "expired"
        assert SessionStatus.ENDED == "ended"
        assert SessionStatus.SUSPENDED == "suspended"

    def test_session_status_enum_membership(self):
        """Test SessionStatus enum membership."""
        assert SessionStatus.ACTIVE in SessionStatus
        assert SessionStatus.EXPIRED in SessionStatus
        assert SessionStatus.ENDED in SessionStatus
        assert SessionStatus.SUSPENDED in SessionStatus


class TestSessionStats:
    """Test suite for SessionStats model."""

    def test_session_stats_creation(self):
        """Test SessionStats creation with defaults."""
        stats = SessionStats()
        
        assert stats.total_sessions == 0
        assert stats.active_sessions == 0
        assert stats.expired_sessions == 0
        assert stats.average_duration_minutes == 0.0
        assert stats.total_interactions == 0
        assert stats.average_safety_score == 1.0

    def test_session_stats_with_values(self):
        """Test SessionStats creation with custom values."""
        stats = SessionStats(
            total_sessions=100,
            active_sessions=80,
            expired_sessions=20,
            average_duration_minutes=45.5,
            total_interactions=500,
            average_safety_score=0.95
        )
        
        assert stats.total_sessions == 100
        assert stats.active_sessions == 80
        assert stats.expired_sessions == 20
        assert stats.average_duration_minutes == 45.5
        assert stats.total_interactions == 500
        assert stats.average_safety_score == 0.95


class TestFactoryFunctions:
    """Test suite for factory functions."""

    def test_get_session_manager_default(self):
        """Test get_session_manager with default timeout."""
        manager = get_session_manager()
        
        assert isinstance(manager, AsyncSessionManager)
        assert manager.default_timeout == 30

    def test_get_session_manager_custom_timeout(self):
        """Test get_session_manager with custom timeout."""
        manager = get_session_manager(timeout_minutes=60)
        
        assert isinstance(manager, AsyncSessionManager)
        assert manager.default_timeout == 60

    def test_get_session_storage(self):
        """Test get_session_storage factory function."""
        storage = get_session_storage()
        
        assert isinstance(storage, SessionStorage)


class TestIntegrationScenarios:
    """Test suite for integration scenarios."""

    @pytest.mark.asyncio
    async def test_complete_session_lifecycle(self, session_manager, sample_child_id):
        """Test complete session lifecycle."""
        # Create session
        session = await session_manager.create_session(
            child_id=sample_child_id,
            initial_data={"activity": "story_time"}
        )
        
        # Update session
        await session_manager.update_session(
            session_id=session.session_id,
            data_updates={"progress": "chapter_1"}
        )
        
        # Retrieve session
        retrieved_session = await session_manager.get_session(session.session_id)
        assert retrieved_session.data["activity"] == "story_time"
        assert retrieved_session.data["progress"] == "chapter_1"
        
        # End session
        result = await session_manager.end_session(session.session_id)
        assert result is True
        
        # Verify session is ended
        final_session = await session_manager.storage.retrieve_session(session.session_id)
        assert final_session.status == SessionStatus.ENDED

    @pytest.mark.asyncio
    async def test_multi_child_session_management(self, session_manager):
        """Test managing sessions for multiple children."""
        # Create sessions for different children
        child1_session = await session_manager.create_session(
            child_id="child1",
            initial_data={"activity": "reading"}
        )
        child2_session = await session_manager.create_session(
            child_id="child2",
            initial_data={"activity": "games"}
        )
        
        # Verify isolation
        child1_sessions = await session_manager.get_child_sessions("child1")
        child2_sessions = await session_manager.get_child_sessions("child2")
        
        assert len(child1_sessions) == 1
        assert len(child2_sessions) == 1
        assert child1_sessions[0].data["activity"] == "reading"
        assert child2_sessions[0].data["activity"] == "games"

    @pytest.mark.asyncio
    async def test_session_cleanup_integration(self, session_manager):
        """Test session cleanup integration."""
        # Create sessions
        active_session = await session_manager.create_session(child_id="child1")
        expired_session = await session_manager.create_session(child_id="child2")
        
        # Expire one session
        past_time = datetime.utcnow() - timedelta(minutes=60)
        expired_session.last_activity = past_time
        await session_manager.storage.store_session(expired_session)
        
        # Run cleanup
        cleaned_count = await session_manager.cleanup_expired_sessions()
        
        # Verify cleanup
        assert cleaned_count == 1
        remaining_sessions = await session_manager.storage.get_session_count()
        assert remaining_sessions == 1