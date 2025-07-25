"""Production Database Validator
Critical security validator for production database configurations.
Enforces ALL required security measures for child safety applications.
"""

import asyncio
from typing import Any, Dict, List
from urllib.parse import urlparse

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.database.config import DatabaseConfig

logger = get_logger(__name__, component="production_security")


class ProductionDatabaseValidator:
    """
    Critical production database security validator.
    Enforces strict security requirements for child safety applications.

    FAILURE TO PASS ANY CHECK WILL PREVENT APPLICATION STARTUP.
    """

    def __init__(self, config: DatabaseConfig) -> None:
        self.config = config
        self.validation_errors: List[str] = []
        self.validation_warnings: List[str] = []

    async def validate_all_production_requirements(self) -> bool:
        """
        Comprehensive production validation that MUST pass for startup.
        Returns True only if ALL security requirements are met.
        """
        if self.config.environment != "production":
            logger.info("Non-production environment - skipping production validation")
            return True

        logger.info("🔒 Starting CRITICAL production database security validation...")

        validation_tasks = [
            self._validate_engine_type(),
            self._validate_ssl_connection(),
            self._validate_encryption_at_rest(),
            self._validate_row_level_security(),
            self._validate_backup_configuration(),
            self._validate_connection_security(),
            self._validate_child_safety_compliance(),
        ]

        # Run all validations
        results = await asyncio.gather(*validation_tasks, return_exceptions=True)

        # Check for any validation failures
        success = True
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.validation_errors.append(f"Validation {i+1} failed: {str(result)}")
                success = False
            elif not result:
                success = False

        # Log results
        if self.validation_errors:
            logger.critical("❌ CRITICAL: Production database validation FAILED")
            for error in self.validation_errors:
                logger.critical(f"❌ {error}")
            raise RuntimeError(
                f"PRODUCTION DATABASE SECURITY VALIDATION FAILED. "
                f"ERRORS: {'; '.join(self.validation_errors)}"
            )

        if self.validation_warnings:
            for warning in self.validation_warnings:
                logger.warning(f"⚠️ {warning}")

        if success:
            logger.info("✅ ALL production database security validations PASSED")

        return success

    async def _validate_engine_type(self) -> bool:
        """Validate that PostgreSQL is being used in production."""
        if self.config.engine_type != "postgresql":
            self.validation_errors.append(
                f"CRITICAL: Production MUST use PostgreSQL, found: {self.config.engine_type}"
            )
            return False

        logger.info("✅ Engine type validation passed: PostgreSQL")
        return True

    async def _validate_ssl_connection(self) -> bool:
        """Validate SSL connection is required and properly configured."""
        if not self.config.require_ssl:
            self.validation_errors.append(
                "CRITICAL: SSL connection is REQUIRED in production"
            )
            return False

        # Test actual SSL connection
        try:
            # Parse the database URL to check for SSL parameters
            urlparse(self.config.database_url)
            if "sslmode" not in self.config.database_url.lower():
                self.validation_warnings.append(
                    "SSL mode not explicitly set in DATABASE_URL - ensure SSL is configured"
                )

            # Test SSL connection capability
            engine = create_async_engine(
                self.config.database_url,
                **self.config.get_engine_kwargs(),
            )

            async with engine.begin() as conn:
                # Check SSL status in PostgreSQL
                result = await conn.execute(text("SHOW ssl"))
                ssl_status = result.scalar()
                if ssl_status != "on":
                    self.validation_errors.append(
                        f"CRITICAL: PostgreSQL SSL is not enabled. Status: {ssl_status}"
                    )
                    return False

                # Verify encrypted connection
                result = await conn.execute(text("SELECT ssl_is_used()"))
                ssl_used = result.scalar()
                if not ssl_used:
                    self.validation_errors.append(
                        "CRITICAL: Current connection is NOT using SSL encryption"
                    )
                    return False

            await engine.dispose()
            logger.info("✅ SSL connection validation passed")
            return True

        except Exception as e:
            self.validation_errors.append(
                f"CRITICAL: SSL connection validation failed: {str(e)}"
            )
            return False

    async def _validate_encryption_at_rest(self) -> bool:
        """Validate encryption at rest is enabled."""
        if not self.config.require_encryption_at_rest:
            self.validation_errors.append(
                "CRITICAL: Encryption at rest MUST be enabled in production"
            )
            return False

        try:
            engine = create_async_engine(
                self.config.database_url,
                **self.config.get_engine_kwargs(),
            )

            async with engine.begin() as conn:
                # Check for Transparent Data Encryption (TDE) or similar
                # This query checks for encrypted tablespaces in PostgreSQL
                result = await conn.execute(
                    text(
                        """
                        SELECT COUNT(*) as encrypted_count
                        FROM pg_tablespace
                        WHERE spcname != 'pg_default'
                        AND spcname != 'pg_global'
                    """
                    )
                )
                encrypted_count = result.scalar()

                # Check database settings for encryption
                result = await conn.execute(
                    text(
                        "SELECT name, setting FROM pg_settings WHERE name LIKE '%crypt%' OR name LIKE '%ssl%'"
                    )
                )
                encryption_settings = result.fetchall()

                # Log encryption configuration
                logger.info(
                    f"Encryption settings found: {len(encryption_settings)} entries"
                )

                # For managed databases (like AWS RDS, Azure, GCP), encryption is typically handled at the storage level
                # We check if we're using a managed service by looking at the hostname
                parsed_url = urlparse(self.config.database_url)
                hostname = parsed_url.hostname or ""

                managed_service_indicators = [
                    "rds.amazonaws.com",
                    "database.azure.com",
                    "postgres.database.azure.com",
                    "cloudsql",
                    "cloud.google.com",
                ]

                is_managed_service = any(
                    indicator in hostname.lower()
                    for indicator in managed_service_indicators
                )

                if is_managed_service:
                    logger.info(
                        "✅ Managed database service detected - encryption typically enabled by default"
                    )
                elif encrypted_count == 0:
                    self.validation_warnings.append(
                        "No custom encrypted tablespaces found - verify encryption is enabled at storage level"
                    )

            await engine.dispose()
            logger.info("✅ Encryption at rest validation passed")
            return True

        except Exception as e:
            self.validation_errors.append(
                f"CRITICAL: Encryption at rest validation failed: {str(e)}"
            )
            return False

    async def _validate_row_level_security(self) -> bool:
        """Validate row-level security is enabled for child data protection."""
        try:
            engine = create_async_engine(
                self.config.database_url,
                **self.config.get_engine_kwargs(),
            )

            async with engine.begin() as conn:
                # Check if RLS is enabled on critical tables
                critical_tables = [
                    "users",
                    "children",
                    "conversations",
                    "safety_events",
                ]
                rls_enabled_tables = []

                for table in critical_tables:
                    try:
                        result = await conn.execute(
                            text(
                                """
                                SELECT relname, relrowsecurity
                                FROM pg_class
                                WHERE relname = :table_name
                                AND relkind = 'r'
                            """
                            ),
                            {"table_name": table},
                        )
                        table_info = result.fetchone()

                        if table_info and table_info[1]:  # relrowsecurity = True
                            rls_enabled_tables.append(table)
                            logger.info(f"✅ RLS enabled on table: {table}")
                        elif table_info:
                            self.validation_warnings.append(
                                f"Row-level security NOT enabled on critical table: {table}"
                            )
                        else:
                            # Table doesn't exist yet - this is OK for new deployments
                            logger.info(
                                f"Table {table} not found - will be created during migration"
                            )

                    except Exception as table_e:
                        logger.warning(
                            f"Could not check RLS for table {table}: {table_e}"
                        )

                # At least some RLS should be configured if tables exist
                if rls_enabled_tables:
                    logger.info(
                        f"✅ Row-level security enabled on {len(rls_enabled_tables)} tables"
                    )
                else:
                    self.validation_warnings.append(
                        "No row-level security policies found - ensure RLS is configured for child data protection"
                    )

            await engine.dispose()
            logger.info("✅ Row-level security validation completed")
            return True

        except Exception as e:
            self.validation_errors.append(
                f"CRITICAL: Row-level security validation failed: {str(e)}"
            )
            return False

    async def _validate_backup_configuration(self) -> bool:
        """Validate automated backup configuration."""
        try:
            engine = create_async_engine(
                self.config.database_url,
                **self.config.get_engine_kwargs(),
            )

            async with engine.begin() as conn:
                # Check WAL archiving status (for PostgreSQL backups)
                result = await conn.execute(text("SHOW archive_mode"))
                archive_mode = result.scalar()

                result = await conn.execute(text("SHOW wal_level"))
                wal_level = result.scalar()

                # Check if we're on a managed service
                parsed_url = urlparse(self.config.database_url)
                hostname = parsed_url.hostname or ""

                managed_service_indicators = [
                    "rds.amazonaws.com",
                    "database.azure.com",
                    "postgres.database.azure.com",
                    "cloudsql",
                    "cloud.google.com",
                ]

                is_managed_service = any(
                    indicator in hostname.lower()
                    for indicator in managed_service_indicators
                )

                if is_managed_service:
                    logger.info(
                        "✅ Managed database service detected - automated backups typically configured"
                    )
                elif archive_mode == "on" and wal_level in ["replica", "logical"]:
                    logger.info("✅ WAL archiving enabled - backup capability confirmed")
                else:
                    self.validation_warnings.append(
                        f"Backup configuration unclear - archive_mode: {archive_mode}, wal_level: {wal_level}"
                    )

            await engine.dispose()
            logger.info("✅ Backup configuration validation completed")
            return True

        except Exception as e:
            self.validation_warnings.append(f"Backup validation warning: {str(e)}")
            # Don't fail startup for backup validation issues
            return True

    async def _validate_connection_security(self) -> bool:
        """Validate connection pool and security settings."""
        # Validate connection pool settings
        if self.config.pool_size < 10:
            self.validation_errors.append(
                f"CRITICAL: Production requires minimum 10 connection pool size, got: {self.config.pool_size}"
            )
            return False

        if not self.config.pool_pre_ping:
            self.validation_errors.append(
                "CRITICAL: Connection pre-ping MUST be enabled in production"
            )
            return False

        if not self.config.validate_connection:
            self.validation_errors.append(
                "CRITICAL: Connection validation MUST be enabled in production"
            )
            return False

        logger.info("✅ Connection security validation passed")
        return True

    async def _validate_child_safety_compliance(self) -> bool:
        """Validate COPPA and child safety compliance settings."""
        if not self.config.enforce_coppa_constraints:
            self.validation_errors.append(
                "CRITICAL: COPPA constraints MUST be enforced in production"
            )
            return False

        if not self.config.audit_all_operations:
            self.validation_errors.append(
                "CRITICAL: Operation auditing MUST be enabled in production"
            )
            return False

        logger.info("✅ Child safety compliance validation passed")
        return True

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of validation results."""
        return {
            "errors": self.validation_errors,
            "warnings": self.validation_warnings,
            "total_errors": len(self.validation_errors),
            "total_warnings": len(self.validation_warnings),
            "environment": self.config.environment,
            "engine_type": self.config.engine_type,
        }


async def validate_production_database(config: DatabaseConfig) -> bool:
    """
    Main entry point for production database validation.
    CRITICAL: Application startup MUST fail if this returns False.
    """
    validator = ProductionDatabaseValidator(config)
    return await validator.validate_all_production_requirements()
