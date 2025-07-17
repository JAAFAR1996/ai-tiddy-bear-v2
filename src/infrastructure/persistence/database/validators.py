import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from .config import DatabaseConfig

"""Database Connection and Schema Validators
Extracted from production_database_config.py to reduce file size
Translated Arabic comments to English"""

from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="persistence")


class DatabaseConnectionValidator:
    """Database connection validator"""
    
    def __init__(self, config: DatabaseConfig) -> None:
        self.config = config
    
    async def validate_connection(self) -> bool:
        """Validate database connection"""
        try:
            # Create temporary engine for validation
            engine = create_async_engine(
                self.config.database_url, **self.config.get_engine_kwargs()
            )
            # Test connection with safe parameterized queries
            async with engine.begin() as conn:
                if self.config.engine_type == "postgresql":
                    # Use text() for proper SQL handling even for simple queries
                    result = await conn.execute(text("SELECT version()"))
                    version_info = result.scalar()
                    logger.info(f"PostgreSQL connection validated: {version_info}")
                elif self.config.engine_type == "sqlite":
                    # Use text() for proper SQL handling
                    result = await conn.execute(text("SELECT sqlite_version()"))
                    version_info = result.scalar()
                    logger.info(f"SQLite connection validated: {version_info}")
            await engine.dispose()
            return True
        except Exception as e:
            logger.error(f"Database connection validation failed: {e}")
            if self.config.environment == "production":
                raise RuntimeError(f"Production database connection failed: {e}")
            return False
    
    async def validate_schema_compatibility(self) -> bool:
        """Validate database schema compatibility"""
        try:
            engine = create_async_engine(
                self.config.database_url, **self.config.get_engine_kwargs()
            )
            async with engine.begin() as conn:
                # Check for required tables
                required_tables = [
                    "users",
                    "children",
                    "conversations",
                    "safety_events",
                    "audit_logs",
                ]
                if self.config.engine_type == "postgresql":
                    # PostgreSQL table check
                    for table in required_tables:
                        result = await conn.execute(
                            text(
                                "SELECT EXISTS (SELECT FROM information_schema.tables "
                                "WHERE table_name = :table_name)"
                            ),
                            {"table_name": table},
                        )
                        exists = result.scalar()
                        if not exists:
                            logger.warning(
                                f"Table '{table}' does not exist - will be created"
                            )
                elif self.config.engine_type == "sqlite":
                    # SQLite table check
                    for table in required_tables:
                        result = await conn.execute(
                            text(
                                "SELECT name FROM sqlite_master "
                                "WHERE type='table' AND name=:table_name"
                            ),
                            {"table_name": table},
                        )
                        exists = result.fetchone() is not None
                        if not exists:
                            logger.warning(
                                f"Table '{table}' does not exist - will be created"
                            )
            await engine.dispose()
            return True
        except Exception as e:
            logger.error(f"Schema compatibility validation failed: {e}")
            return False