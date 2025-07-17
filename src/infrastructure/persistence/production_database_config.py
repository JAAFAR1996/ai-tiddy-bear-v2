"""
🔒 AI Teddy Bear - Production Database Configuration

Refactored to be under 300 lines by extracting components
Translated Arabic comments to English

This file now serves as a facade that re-exports functionality from modular components.

The actual implementation is split across:
- database/config.py: Configuration dataclass and environment settings
- database/validators.py: Connection and schema validation
- database/migrations.py: Migration and security setup
- database/initializer.py: Database initialization logic
"""
import warnings

from .database import (
    DatabaseConfig,
    DatabaseConnectionValidator,
    DatabaseMigrationManager,
    get_database_config,
    initialize_production_database,
    validate_database_environment,
)

# Re-export for backward compatibility
__all__ = [
    "DatabaseConfig",
    "DatabaseConnectionValidator",
    "DatabaseMigrationManager",
    "get_database_config",
    "initialize_production_database",
    "validate_database_environment",
]

# Deprecation warning for direct imports
warnings.warn(
    "Importing from production_database_config.py is deprecated. "
    "Please import from src.infrastructure.persistence.database instead.",
    DeprecationWarning,
    stacklevel=2,
)