import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
while src_path.name != "backend" and src_path.parent != src_path:
    src_path = src_path.parent
src_path = src_path / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

#!/usr/bin/env python3
"""
🧪 Tests for the Clean SessionManager
Testing the new SQLite-based session management
"""

from datetime import datetime, timedelta

try:
    import pytest
except ImportError:
    try:
        from common.mock_pytest import pytest
    except ImportError:
        pass
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
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from infrastructure.session_manager.session_manager import SessionManager
from infrastructure.session_manager.session_models import Session, SessionStatus


@pytest.fixture
async def db_session():
    """Create an in-memory SQLite database for testing"""
    # Create async engine for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Session.metadata.create_all)

    # Create session factory
    async_session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Provide session
    async with async_session_factory() as session:
        yield session

    # Cleanup
    await engine.dispose()


@pytest.fixture
async def session_manager(db_session):
    """Create SessionManager with test database"""
    return SessionManager(db_session)


@pytest.mark.asyncio
async def test_create_session(session_manager):
    """Test creating a new session"""
    child_id = "test-child-123"
    initial_data = {"language": "ar", "name": "Ahmed"}

    session_id = await session_manager.create_session(child_id, initial_data)

    assert session_id is not None
    assert len(session_id) == 36  # UUID length

    # Verify session exists in database
    session = await session_manager.get_session(session_id)
    assert session is not None
    assert session.child_id == child_id
    assert session.status == SessionStatus.ACTIVE.value


@pytest.mark.asyncio
async def test_get_session(session_manager):
    """Test retrieving a session"""
    child_id = "test-child-456"
    session_id = await session_manager.create_session(child_id)

    # Get session
    session = await session_manager.get_session(session_id)

    assert session is not None
    assert session.id == session_id
    assert session.child_id == child_id
    assert session.status == SessionStatus.ACTIVE.value


@pytest.mark.asyncio
async def test_get_nonexistent_session(session_manager):
    """Test retrieving a non-existent session"""
    fake_session_id = "fake-session-id"

    session = await session_manager.get_session(fake_session_id)

    assert session is None


@pytest.mark.asyncio
async def test_update_activity(session_manager):
    """Test updating session activity"""
    child_id = "test-child-789"
    session_id = await session_manager.create_session(child_id)

    # Update activity
    success = await session_manager.update_activity(session_id)

    assert success is True

    # Verify interaction count increased
    session = await session_manager.get_session(session_id)
    assert session.interaction_count == 1


@pytest.mark.asyncio
async def test_end_session(session_manager):
    """Test ending a session"""
    child_id = "test-child-end"
    session_id = await session_manager.create_session(child_id)

    # End session
    success = await session_manager.end_session(session_id, "manual")

    assert success is True

    # Verify session status changed
    session = await session_manager.get_session(session_id)
    assert session.status == SessionStatus.ENDED.value
    assert session.ended_at is not None


@pytest.mark.asyncio
async def test_get_active_sessions(session_manager):
    """Test getting all active sessions"""
    # Create multiple sessions
    child_ids = ["child-1", "child-2", "child-3"]
    session_ids = []

    for child_id in child_ids:
        session_id = await session_manager.create_session(child_id)
        session_ids.append(session_id)

    # End one session
    await session_manager.end_session(session_ids[0])

    # Get active sessions
    active_sessions = await session_manager.get_active_sessions()

    assert len(active_sessions) == 2  # Two should still be active
    active_session_ids = [s.id for s in active_sessions]
    assert session_ids[1] in active_session_ids
    assert session_ids[2] in active_session_ids
    assert session_ids[0] not in active_session_ids  # This one was ended


@pytest.mark.asyncio
async def test_cleanup_inactive_sessions(session_manager):
    """Test cleaning up inactive sessions"""
    child_id = "test-child-cleanup"
    session_id = await session_manager.create_session(child_id)

    # Manually update last_activity to simulate old session
    session = await session_manager.get_session(session_id)
    old_time = datetime.utcnow() - timedelta(hours=1)

    # Update database directly to simulate old activity
    await session_manager.db.execute(
        text("UPDATE sessions SET last_activity = :old_time WHERE id = :session_id"),
        {"old_time": old_time, "session_id": session_id},
    )
    await session_manager.db.commit()

    # Run cleanup
    cleaned_count = await session_manager.cleanup_inactive_sessions()

    assert cleaned_count == 1

    # Verify session was marked as timeout
    session = await session_manager.get_session(session_id)
    assert session.status == SessionStatus.TIMEOUT.value


@pytest.mark.asyncio
async def test_get_session_stats(session_manager):
    """Test getting session statistics"""
    # Create some sessions
    for i in range(3):
        await session_manager.create_session(f"child-{i}")

    stats = await session_manager.get_session_stats()

    assert "active_sessions" in stats
    assert "sessions_today" in stats
    assert "memory_cache_size" in stats
    assert "session_timeout_minutes" in stats

    assert stats["active_sessions"] == 3
    assert stats["sessions_today"] == 3


@pytest.mark.asyncio
async def test_memory_cache(session_manager):
    """Test that memory cache works correctly"""
    child_id = "test-child-cache"
    session_id = await session_manager.create_session(child_id)

    # First get should populate cache
    session1 = await session_manager.get_session(session_id)
    assert session_id in session_manager._active_sessions

    # Second get should use cache
    session2 = await session_manager.get_session(session_id)
    assert session1 == session2

    # End session should remove from cache
    await session_manager.end_session(session_id)
    assert session_id not in session_manager._active_sessions


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__])
