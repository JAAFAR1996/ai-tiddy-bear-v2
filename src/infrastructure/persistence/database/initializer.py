import os

from src.infrastructure.validators.data.database_validators import (
    DatabaseConnectionValidator,
)

from .config import DatabaseConfig
from .migrations import DatabaseMigrationManager

"""Database Initialization Logic
Extracted from production_database_config.py to reduce file size
Translated Arabic comments to English"""

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="persistence")


def get_database_config() -> DatabaseConfig:
    """Get database configuration."""
    config = DatabaseConfig.from_environment()
    # Validate production requirements
    if config.environment == "production":
        config.validate_production_requirements()
    return config


async def initialize_production_database() -> bool:
    """Initialize production database."""
    try:
        config = get_database_config()

        # Validate connection
        validator = DatabaseConnectionValidator(config)
        if not await validator.validate_connection():
            raise RuntimeError("Database connection validation failed")

        # Setup schema compatibility
        if not await validator.validate_schema_compatibility():
            logger.warning("Schema compatibility issues detected")

        # Setup production optimizations
        migration_manager = DatabaseMigrationManager(config)
        if config.environment == "production" and config.engine_type == "postgresql":
            if not await migration_manager.create_production_schema():
                raise RuntimeError("Production schema setup failed")

        # Setup child data security
        if not await migration_manager.setup_child_data_security():
            logger.warning("Child data security setup had issues")

        logger.info(
            f"Database initialization completed for {config.environment} environment",
        )
        return True
    except Exception as e:
        logger.critical(f"Database initialization failed: {e}")
        raise


def validate_database_environment() -> None:
    """Validate database environment."""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    database_url = os.getenv("DATABASE_URL")

    if environment == "production":
        if not database_url:
            raise RuntimeError(
                "CRITICAL: DATABASE_URL environment variable is required in production",
            )
        if "sqlite" in database_url.lower():
            raise RuntimeError(
                "CRITICAL: SQLite is not allowed in production for child safety applications. "
                "Use PostgreSQL with proper encryption and backup strategies.",
            )
        if "postgresql" not in database_url.lower():
            raise RuntimeError(
                "CRITICAL: Production environment requires PostgreSQL database",
            )
        logger.info("Production database environment validation passed")

    return True
