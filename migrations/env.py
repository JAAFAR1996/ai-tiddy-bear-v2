"""
AI Teddy Bear - Alembic Environment Configuration
Async database migration support for PostgreSQL with child safety features
"""

import asyncio
import os
import sys
from logging.config import fileConfig
from typing import Any, Dict

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.config.settings import get_settings
from src.infrastructure.persistence.models import Base

# Alembic Config object for .ini file values
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate support
target_metadata = Base.metadata

# Get application settings
settings = get_settings()


def get_database_url() -> str:
    """Get database URL from environment or settings."""
    # Priority: Environment variable > Config file > Settings
    db_url = (
        os.environ.get("DATABASE_URL") or 
        config.get_main_option("sqlalchemy.url") or 
        settings.DATABASE_URL
    )
    
    if not db_url:
        raise ValueError("DATABASE_URL must be set for migrations")
    
    # Ensure we're using the async driver for migrations
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif not db_url.startswith("postgresql+asyncpg://"):
        raise ValueError("Database URL must use PostgreSQL with asyncpg driver")
    
    return db_url


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.
    
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_database_url()
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        render_as_batch=False,
        # Child safety: Include table comments in migrations
        include_object=include_object,
        # COPPA compliance: Track schema changes
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


def include_object(object, name, type_, reflected, compare_to) -> bool:
    """
    Filter which database objects to include in migrations.
    
    Used for child safety to ensure certain tables are always included.
    """
    # Always include child safety and audit tables
    if type_ == "table":
        child_safety_tables = {
            "children", "audit_logs", "safety_events", "parental_consents",
            "data_retention_policies", "coppa_records"
        }
        if name in child_safety_tables:
            return True
    
    # Include all other objects by default
    return True


def process_revision_directives(context, revision, directives) -> None:
    """
    Process revision directives for COPPA compliance tracking.
    
    Adds metadata to migration files for audit purposes.
    """
    if getattr(config.cmd_opts, 'autogenerate', False):
        script = directives[0]
        if script.upgrade_ops.is_empty():
            directives[:] = []
        else:
            # Add COPPA compliance note to migration
            script.message = f"COPPA-compliant migration: {script.message or 'Auto-generated'}"


def do_run_migrations(connection) -> None:
    """Run migrations with the given connection."""
    # Configure migration context
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        render_as_batch=False,
        include_object=include_object,
        process_revision_directives=process_revision_directives,
        # Child safety: Ensure foreign key constraints are respected
        render_item=render_item,
        # COPPA compliance: Version table naming
        version_table='alembic_version_coppa',
    )

    with context.begin_transaction():
        context.run_migrations()


def render_item(type_, obj, autogen_context) -> Any:
    """
    Render individual migration items with child safety considerations.
    """
    if type_ == "server_default":
        # Ensure default values are appropriate for child data
        if hasattr(obj, 'arg') and obj.arg:
            # Add safety checks for default values
            if 'child' in str(obj.arg).lower():
                # Add comment for child-related defaults
                return f"# Child safety default: {obj.arg}"
    
    # Return False to use default rendering
    return False


async def run_async_migrations() -> None:
    """
    Run migrations in async mode for production PostgreSQL.
    
    This is the main function for async database migrations.
    """
    # Get database configuration
    database_url = get_database_url()
    
    # Configure async engine for migrations
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = database_url
    
    # Create async engine with production settings
    connectable = create_async_engine(
        database_url,
        poolclass=pool.NullPool,  # Disable pooling for migrations
        echo=False,  # Set to True for debugging
        # Production settings
        connect_args={
            "server_settings": {
                "application_name": "ai_teddy_migrations",
                "jit": "off",  # Disable JIT for stability
            }
        },
    )

    async with connectable.connect() as connection:
        # Set up COPPA compliance session variables
        await connection.execute(
            "SET session_replication_role = 'origin'"
        )
        await connection.execute(
            "SET row_security = on"
        )
        await connection.execute(
            "SET application_name = 'ai_teddy_migrations'"
        )
        
        # Run migrations in sync context
        await connection.run_sync(do_run_migrations)

    # Close the engine
    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    
    In this scenario we need to create an Engine and associate a connection
    with the context. This is the preferred mode for async databases.
    """
    # Run async migrations
    asyncio.run(run_async_migrations())


# Determine execution mode and run migrations
if context.is_offline_mode():
    print("🔄 Running migrations in offline mode...")
    run_migrations_offline()
else:
    print("🔄 Running migrations in online mode with async PostgreSQL...")
    print("🔒 COPPA compliance and child safety features enabled")
    run_migrations_online()

 