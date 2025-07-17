from collections.abc import AsyncGenerator

from sqlalchemy.exc import DatabaseError, DataError, IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.database.config import DatabaseConfig
from src.infrastructure.persistence.database.validators import (
    DatabaseConnectionValidator,
)

logger = get_logger(__name__, component="persistence")

# SQLAlchemy declarative base for all models
Base = declarative_base()


class Database:
    """Enterprise-grade database service with production PostgreSQL support."""

    def __init__(
        self,
        database_url: str | None = None,
        pool_size: int | None = None,
        max_overflow: int | None = None,
        pool_recycle: int | None = None,
        pool_pre_ping: bool | None = None,
        pool_timeout: int | None = None,
    ) -> None:
        """Initialize database with production-grade configuration."""
        if database_url:
            self.database_url = database_url
            self.config = DatabaseConfig.from_environment()
            self.config.database_url = database_url
        else:
            self.config = DatabaseConfig.from_environment()
            self.database_url = self.config.database_url

        # Override config with explicitly provided init parameters
        if pool_size is not None:
            self.config.pool_size = pool_size
        if max_overflow is not None:
            self.config.max_overflow = max_overflow
        if pool_recycle is not None:
            self.config.pool_recycle = pool_recycle
        if pool_pre_ping is not None:
            self.config.pool_pre_ping = pool_pre_ping
        if pool_timeout is not None:
            self.config.pool_timeout = pool_timeout

        # Log database configuration
        logger.info(
            f"Initializing database for {self.config.environment} environment"
        )
        logger.info(f"Database engine: {self.config.engine_type}")

        # Validate production requirements
        if self.config.environment == "production":
            self.config.validate_production_requirements()
            logger.info("Production database requirements validated")

        try:
            # Get engine configuration from config
            engine_kwargs = self.config.get_engine_kwargs()
            # Create async engine with production configuration
            self.engine = create_async_engine(
                self.database_url, **engine_kwargs
            )
            # Create session maker with optimized settings
            session_kwargs = {
                "expire_on_commit": False,
                "class_": AsyncSession,
                "autoflush": self.config.environment
                != "production",  # Manual control in production
                "autocommit": False,  # Always explicit transaction control
            }
            self.async_session = async_sessionmaker(
                self.engine, **session_kwargs
            )
            # Log successful initialization (without exposing credentials)
            safe_url = self._get_safe_url_for_logging(self.database_url)
            logger.info(f"Database engine created successfully: {safe_url}")
        except Exception as e:
            logger.critical(f"Failed to create database engine: {e}")
            safe_url = self._get_safe_url_for_logging(self.database_url)
            raise ConnectionError(
                f"Database connection failed: {safe_url}"
            ) from e

    def _get_safe_url_for_logging(self, url: str) -> str:
        """Create safe URL for logging (without exposing passwords)."""
        try:
            from urllib.parse import urlparse, urlunparse

            parsed = urlparse(url)
            if parsed.password or parsed.username:
                if parsed.username and parsed.password:
                    safe_netloc = (
                        f"{parsed.username}:[REDACTED]@{parsed.hostname}"
                    )
                elif parsed.username:
                    safe_netloc = f"{parsed.username}@{parsed.hostname}"
                else:
                    safe_netloc = parsed.hostname
                if parsed.port:
                    safe_netloc = f"{safe_netloc}:{parsed.port}"
                safe_parsed = parsed._replace(netloc=safe_netloc)
                safe_url = urlunparse(safe_parsed)
            else:
                safe_url = url
            return safe_url
        except Exception as e:
            logger.warning(f"Failed to redact database URL: {e}")
            return "[DATABASE_URL_REDACTED_DUE_TO_PARSING_ERROR]"

    async def init_db(self) -> None:
        """Initialize database tables with production-grade setup."""
        try:
            # Validate connection first if required
            if self.config.validate_connection:
                validator = DatabaseConnectionValidator(self.config)
                if not await validator.validate_connection():
                    raise ConnectionError(
                        "Database connection validation failed"
                    )
            async with self.engine.begin() as conn:
                # Register all models using the model registry
                from src.infrastructure.persistence.model_registry import (
                    get_model_registry,
                )

                registry = get_model_registry()
                models = registry.get_all_models()
                logger.info(f"Registered {len(models)} database models")
                # Create all tables
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created successfully")
                # Apply production optimizations if in production
                if (
                    self.config.environment == "production"
                    and self.config.engine_type == "postgresql"
                ):
                    await self._apply_production_optimizations(conn)
        except Exception as e:
            logger.critical(f"Failed to initialize database tables: {e}")
            raise ConnectionError("Database initialization failed") from e

    async def _apply_production_optimizations(self, conn) -> None:
        """Apply production optimizations."""
        try:
            from sqlalchemy import text

            # Enable necessary PostgreSQL extensions
            extensions = [
                'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"',
                'CREATE EXTENSION IF NOT EXISTS "pgcrypto"',
                'CREATE EXTENSION IF NOT EXISTS "pg_stat_statements"',
            ]
            for extension in extensions:
                try:
                    await conn.execute(text(extension))
                except Exception as e:
                    logger.warning(f"Could not create extension: {e}")
            # Create performance indexes
            indexes = [
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_children_parent_id ON children(parent_id)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_child_id ON conversations(child_id)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)",
            ]
            for index in indexes:
                try:
                    await conn.execute(text(index))
                except Exception as e:
                    logger.warning(f"Could not create index: {e}")
            logger.info("Production PostgreSQL optimizations applied")
        except Exception as e:
            logger.warning(f"Failed to apply production optimizations: {e}")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session with proper transaction handling."""
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except (IntegrityError, DataError, DatabaseError) as db_error:
                logger.error(f"Database error during transaction: {db_error}")
                await session.rollback()
                raise DatabaseError(
                    f"Transaction failed: {db_error}"
                ) from db_error
            except (ConnectionError, TimeoutError) as conn_error:
                logger.error(
                    f"Connection error during transaction: {conn_error}"
                )
                await session.rollback()
                raise ConnectionError(
                    f"Database connection failed: {conn_error}",
                ) from conn_error
            except Exception as unexpected_error:
                logger.critical(
                    "Unexpected error during database transaction",
                    exc_info=True,
                )
                await session.rollback()
                raise RuntimeError(
                    "Database operation failed due to unexpected error",
                ) from unexpected_error
            finally:
                await session.close()

    async def close(self) -> None:
        """Close database engine."""
        await self.engine.dispose()
        logger.info("Database connection closed")
