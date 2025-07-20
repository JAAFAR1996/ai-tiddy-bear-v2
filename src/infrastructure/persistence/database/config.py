import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

"""Database Configuration
Extracted from production_database_config.py to reduce file size
Translated Arabic comments to English"""


@dataclass
class DatabaseConfig:
    """Database configuration settings."""

    database_url: str
    engine_type: str  # postgresql, sqlite
    environment: str  # production, development, testing
    # Connection pool settings - optimized for production
    pool_size: int = 20  # Base connections maintained in pool
    max_overflow: int = 30  # Additional connections when needed
    pool_recycle: int = 3600  # Recycle connections every hour
    pool_pre_ping: bool = True  # Validate connections before use
    pool_timeout: int = 30  # Timeout for getting connection from pool
    # Performance settings
    echo: bool = False
    isolation_level: str = "READ_COMMITTED"
    # Security settings
    require_ssl: bool = True
    validate_connection: bool = True
    # Child safety compliance
    enforce_coppa_constraints: bool = True
    require_encryption_at_rest: bool = True
    audit_all_operations: bool = True

    @classmethod
    def from_environment(cls) -> "DatabaseConfig":
        """Create database configuration from environment variables."""
        environment = os.getenv("ENVIRONMENT", "development").lower()
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            # Default configurations for different environments
            if environment == "production":
                raise RuntimeError(
                    "CRITICAL: DATABASE_URL must be set in production environment. "
                    "SQLite is not allowed for child safety applications.",
                )
            if environment == "testing":
                database_url = "sqlite+aiosqlite:///test_ai_teddy.db"
            else:
                database_url = "sqlite+aiosqlite:///ai_teddy_dev.db"
        # Parse database URL to determine engine type
        parsed_url = urlparse(database_url)
        if parsed_url.scheme.startswith("postgresql"):
            engine_type = "postgresql"
        elif parsed_url.scheme.startswith("sqlite"):
            engine_type = "sqlite"
        else:
            raise ValueError(f"Unsupported database scheme: {parsed_url.scheme}")
        return cls._create_for_environment(database_url, engine_type, environment)

    @classmethod
    def _create_for_environment(
        cls,
        database_url: str,
        engine_type: str,
        environment: str,
    ) -> "DatabaseConfig":
        """Create environment-specific configuration."""
        if environment == "production":
            return cls._production_config(database_url, engine_type)
        if environment == "testing":
            return cls._testing_config(database_url, engine_type)
        return cls._development_config(database_url, engine_type)

    @classmethod
    def _production_config(
        cls,
        database_url: str,
        engine_type: str,
    ) -> "DatabaseConfig":
        """Production safe configuration."""
        if engine_type == "sqlite":
            raise RuntimeError(
                "CRITICAL: SQLite is not allowed in production for child safety applications. "
                "Use PostgreSQL with proper encryption and backup strategies.",
            )
        return cls(
            database_url=database_url,
            engine_type=engine_type,
            environment="production",
            pool_size=int(os.getenv("DB_POOL_SIZE", "20")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "0")),
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "300")),
            pool_pre_ping=True,
            echo=False,  # Never log SQL in production
            isolation_level="READ_COMMITTED",
            require_ssl=True,
            validate_connection=True,
            enforce_coppa_constraints=True,
            require_encryption_at_rest=True,
            audit_all_operations=True,
        )

    @classmethod
    def _development_config(
        cls,
        database_url: str,
        engine_type: str,
    ) -> "DatabaseConfig":
        """Development configuration."""
        return cls(
            database_url=database_url,
            engine_type=engine_type,
            environment="development",
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=os.getenv("DB_ECHO", "false").lower() == "true",
            isolation_level="READ_COMMITTED",
            require_ssl=False,  # More flexible in development
            validate_connection=True,
            enforce_coppa_constraints=True,
            require_encryption_at_rest=False,  # Optional in dev
            audit_all_operations=True,
        )

    @classmethod
    def _testing_config(cls, database_url: str, engine_type: str) -> "DatabaseConfig":
        """Testing configuration."""
        return cls(
            database_url=database_url,
            engine_type=engine_type,
            environment="testing",
            pool_size=1,
            max_overflow=0,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=False,
            isolation_level="READ_COMMITTED",
            require_ssl=False,
            validate_connection=False,
            enforce_coppa_constraints=False,  # Simplified for tests
            require_encryption_at_rest=False,
            audit_all_operations=False,
        )

    def get_engine_kwargs(self) -> dict[str, Any]:
        """Get database engine parameters."""
        base_kwargs = {
            "echo": self.echo,
            "pool_pre_ping": self.pool_pre_ping,
        }
        if self.engine_type == "postgresql":
            base_kwargs.update(
                {
                    "pool_size": self.pool_size,
                    "max_overflow": self.max_overflow,
                    "pool_recycle": self.pool_recycle,
                    "isolation_level": self.isolation_level,
                },
            )
            # PostgreSQL specific connection arguments
            connect_args = {
                "server_settings": {
                    "application_name": "ai_teddy_backend",
                    "jit": "off",  # Security optimization
                },
            }
            if self.environment == "production":
                # Production optimizations
                connect_args["server_settings"].update(
                    {
                        "shared_preload_libraries": "pg_stat_statements",
                        "max_connections": "200",
                        "effective_cache_size": "4GB",
                        "maintenance_work_mem": "256MB",
                        "checkpoint_completion_target": "0.9",
                        "wal_buffers": "16MB",
                        "default_statistics_target": "100",
                        "random_page_cost": "1.1",  # SSD optimization
                        "effective_io_concurrency": "200",
                    },
                )
            if self.require_ssl:
                connect_args["sslmode"] = "require"
            base_kwargs["connect_args"] = connect_args
        elif self.engine_type == "sqlite":
            # SQLite specific settings
            if self.environment == "production":
                raise RuntimeError("SQLite not allowed in production")
            base_kwargs["connect_args"] = {
                "check_same_thread": False,
                "timeout": 20,
            }
        return base_kwargs

    def validate_production_requirements(self) -> bool:
        """Validate production requirements."""
        if self.environment != "production":
            return True
        validation_errors = []
        # Database engine validation
        if self.engine_type != "postgresql":
            validation_errors.append(
                f"Production requires PostgreSQL, got {self.engine_type}",
            )
        # SSL requirement
        if not self.require_ssl:
            validation_errors.append("SSL is required in production")
        # COPPA compliance
        if not self.enforce_coppa_constraints:
            validation_errors.append("COPPA constraints must be enforced in production")
        if not self.require_encryption_at_rest:
            validation_errors.append("Encryption at rest is required in production")
        if not self.audit_all_operations:
            validation_errors.append("Operation auditing is required in production")
        # Connection security
        if not self.validate_connection:
            validation_errors.append("Connection validation is required in production")
        # Performance requirements
        if self.pool_size < 10:
            validation_errors.append(
                "Production requires at least 10 connection pool size",
            )
        if validation_errors:
            error_message = "Production database validation failed:\n" + "\n".join(
                f"- {error}" for error in validation_errors
            )
            raise RuntimeError(error_message)
        return True
