"""Database Session Manager for AI Teddy Bear PostgreSQL Database.

This module provides a centralized session management system for PostgreSQL database
connections, including transaction handling, connection pooling, and session lifecycle
management for the AI Teddy Bear application.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.database_manager import Database

logger = get_logger(__name__, component="session_manager")


class SessionManager:
    """Centralized database session manager for PostgreSQL.

    Provides:
    - Session lifecycle management
    - Transaction handling with automatic rollback
    - Connection pooling through Database class
    - Error handling and logging
    - Context manager support for async sessions
    """

    def __init__(self, database: Database | None = None):
        """Initialize the session manager.

        Args:
            database: Optional Database instance. If None, uses get_database().
        """
        self._database = database
        self._session_count = 0
        logger.info("Session manager initialized")

    @property
    def database(self) -> Database:
        """Get the database instance, creating one if needed."""
        if self._database is None:
            # Import here to avoid circular import
            from src.infrastructure.config.settings import get_settings

            settings = get_settings()
            self._database = Database(str(settings.database.DATABASE_URL))
        return self._database

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session with automatic transaction management.

        This context manager:
        - Creates a new AsyncSession from the session factory
        - Automatically commits on successful completion
        - Automatically rolls back on any exception
        - Properly closes the session
        - Provides logging for debugging

        Yields:
            AsyncSession: A SQLAlchemy async session

        Raises:
            SQLAlchemyError: For database-related errors
            Exception: For other unexpected errors

        Example:
            async with session_manager.get_session() as session:
                result = await session.execute(select(User))
                users = result.scalars().all()
        """
        session_id = self._get_next_session_id()
        logger.debug("Creating database session %s", session_id)

        async with self.database.get_session() as session:
            try:
                logger.debug("Session %s created successfully", session_id)
                yield session
                logger.debug("Session %s completed successfully", session_id)

            except SQLAlchemyError:
                logger.exception("Database error in session %s", session_id)
                raise
            except Exception:
                logger.exception("Unexpected error in session %s", session_id)
                raise
            finally:
                logger.debug("Session %s cleaned up", session_id)

    async def execute_with_session(self, operation, *args, **kwargs):
        """Execute a database operation with automatic session management.

        Args:
            operation: Async callable that takes a session as first argument
            *args: Additional positional arguments for the operation
            **kwargs: Additional keyword arguments for the operation

        Returns:
            The result of the operation

        Example:
            async def get_user(session, user_id):
                return await session.get(User, user_id)

            user = await session_manager.execute_with_session(get_user, user_id=123)
        """
        async with self.get_session() as session:
            return await operation(session, *args, **kwargs)

    def _get_next_session_id(self) -> int:
        """Get the next session ID for logging purposes."""
        self._session_count += 1
        return self._session_count

    async def health_check(self) -> bool:
        """Perform a health check on the database connection.

        Returns:
            bool: True if the database is accessible, False otherwise
        """
        try:
            async with self.get_session() as session:
                # Simple query to test connection
                result = await session.execute("SELECT 1")
                result.scalar()
                logger.info("Database health check passed")
                return True
        except SQLAlchemyError:
            logger.exception("Database health check failed")
            return False


# Module-level session manager instance
_session_manager: SessionManager | None = None


def get_session_manager() -> SessionManager:
    """Get the global session manager instance.

    Returns:
        SessionManager: The global session manager
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
        logger.info("Global session manager created")
    return _session_manager


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session (convenience function).

    This is a convenience function that uses the global session manager.
    It's the main entry point for getting database sessions throughout
    the application.

    Yields:
        AsyncSession: A SQLAlchemy async session

    Example:
        async with get_async_session() as session:
            result = await session.execute(select(User))
    """
    session_manager = get_session_manager()
    async with session_manager.get_session() as session:
        yield session


# Transaction management utilities


@asynccontextmanager
async def transaction() -> AsyncGenerator[AsyncSession, None]:
    """Execute operations within an explicit transaction.

    This provides more control over transaction boundaries than the
    automatic transaction management in get_async_session().

    Yields:
        AsyncSession: A SQLAlchemy async session with explicit transaction
    """
    async with get_async_session() as session, session.begin():
        yield session


async def execute_in_transaction(operation, *args, **kwargs):
    """Execute an operation within a transaction.

    Args:
        operation: Async callable that takes a session as first argument
        *args: Additional positional arguments
        **kwargs: Additional keyword arguments

    Returns:
        The result of the operation
    """
    async with transaction() as session:
        return await operation(session, *args, **kwargs)


# Session utilities for specific use cases


@asynccontextmanager
async def read_only_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a read-only database session.

    This session automatically rolls back at the end to ensure
    no accidental writes occur.

    Yields:
        AsyncSession: A read-only SQLAlchemy async session
    """
    async with get_async_session() as session:
        try:
            yield session
        finally:
            # For read-only, we rollback to be safe
            await session.rollback()


# Batch operation utilities


@asynccontextmanager
async def batch_session(batch_size: int = 100) -> AsyncGenerator[AsyncSession, None]:
    """Get a session optimized for batch operations.

    Args:
        batch_size: Number of operations before auto-commit

    Yields:
        AsyncSession: A session with batch operation support
    """
    async with get_async_session() as session:
        operation_count = 0

        # Add a method to the session for batch tracking
        async def add_operation():
            nonlocal operation_count
            operation_count += 1
            if operation_count >= batch_size:
                await session.commit()
                operation_count = 0
                logger.debug("Batch committed after %s operations", batch_size)

        # Attach the method to the session
        session.add_batch_operation = add_operation
        yield session
