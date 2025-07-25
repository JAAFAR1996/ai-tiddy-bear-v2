"""Test the PostgreSQL database session manager functionality."""

import pytest
from sqlalchemy import text

from src.infrastructure.persistence.session_manager import (
    execute_in_transaction,
    get_async_session,
    get_session_manager,
    read_only_session,
    transaction,
)


class TestPostgreSQLSessionManager:
    """Test cases for the PostgreSQL database session manager."""

    @pytest.mark.asyncio
    async def test_session_manager_creation(self):
        """Test that session manager can be created."""
        session_manager = get_session_manager()
        assert session_manager is not None
        assert hasattr(session_manager, "get_session")
        assert hasattr(session_manager, "health_check")

    @pytest.mark.asyncio
    async def test_get_async_session(self):
        """Test that get_async_session provides a working session."""
        async with get_async_session() as session:
            assert session is not None
            # Test a simple query
            result = await session.execute(text("SELECT 1 as test_value"))
            row = result.first()
            assert row[0] == 1

    @pytest.mark.asyncio
    async def test_session_manager_health_check(self):
        """Test the health check functionality."""
        session_manager = get_session_manager()
        health_status = await session_manager.health_check()
        assert isinstance(health_status, bool)
        # Should be True if database is accessible

    @pytest.mark.asyncio
    async def test_transaction_context_manager(self):
        """Test the transaction context manager."""
        async with transaction() as session:
            assert session is not None
            # Test that we can execute queries within transaction
            result = await session.execute(text("SELECT 1 as test_value"))
            row = result.first()
            assert row[0] == 1

    @pytest.mark.asyncio
    async def test_read_only_session(self):
        """Test the read-only session."""
        async with read_only_session() as session:
            assert session is not None
            # Test a simple read query
            result = await session.execute(text("SELECT 1 as test_value"))
            row = result.first()
            assert row[0] == 1

    @pytest.mark.asyncio
    async def test_execute_in_transaction(self):
        """Test executing operations within a transaction."""

        async def test_operation(session):
            result = await session.execute(text("SELECT 42 as test_value"))
            return result.scalar()

        result = await execute_in_transaction(test_operation)
        assert result == 42

    @pytest.mark.asyncio
    async def test_session_manager_singleton(self):
        """Test that session manager is a singleton."""
        manager1 = get_session_manager()
        manager2 = get_session_manager()
        assert manager1 is manager2  # Should be the same instance

    @pytest.mark.asyncio
    async def test_session_isolation(self):
        """Test that sessions are properly isolated."""
        async with get_async_session() as session1:
            async with get_async_session() as session2:
                # These should be different session objects
                assert session1 is not session2

                # Both should work independently
                result1 = await session1.execute(text("SELECT 1"))
                result2 = await session2.execute(text("SELECT 2"))

                assert result1.scalar() == 1
                assert result2.scalar() == 2


@pytest.mark.asyncio
async def test_postgresql_session_manager_integration():
    """Integration test for PostgreSQL session manager with real database operations."""
    # Test that we can create a session and perform basic operations
    async with get_async_session() as session:
        # Test basic connectivity
        result = await session.execute(text("SELECT current_timestamp"))
        timestamp = result.scalar()
        assert timestamp is not None

        # Test that session has expected methods
        assert hasattr(session, "execute")
        assert hasattr(session, "commit")
        assert hasattr(session, "rollback")
        assert hasattr(session, "close")


if __name__ == "__main__":
    # Simple test runner for manual execution
    import asyncio

    async def run_basic_test():
        """Run a basic test manually."""
        print("Testing PostgreSQL session manager...")

        try:
            # Test session creation
            session_manager = get_session_manager()
            print("✓ Session manager created")

            # Test health check
            health = await session_manager.health_check()
            print(f"✓ Health check: {'PASS' if health else 'FAIL'}")

            # Test basic session usage
            async with get_async_session() as session:
                result = await session.execute(text("SELECT 1"))
                value = result.scalar()
                assert value == 1
                print("✓ Basic session operation successful")

            print("All tests passed!")

        except Exception as e:
            print(f"✗ Test failed: {e}")
            raise

    # Run the test
    asyncio.run(run_basic_test())
