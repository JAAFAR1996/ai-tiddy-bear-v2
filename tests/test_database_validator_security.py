"""
Database Validator Tests
Tests for production database security validation.
Covers both secure and insecure configurations to ensure fail-fast behavior.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.infrastructure.persistence.database.config import DatabaseConfig
from src.infrastructure.validators.data.production_database_validator import (
    ProductionDatabaseValidator,
    validate_production_database,
)


class TestProductionDatabaseValidator:
    """Test production database security validation."""

    @pytest.fixture
    def secure_production_config(self):
        """Create a secure production configuration."""
        return DatabaseConfig(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/testdb?sslmode=require",
            engine_type="postgresql",
            environment="production",
            pool_size=20,
            max_overflow=10,
            pool_recycle=3600,
            pool_pre_ping=True,
            require_ssl=True,
            validate_connection=True,
            enforce_coppa_constraints=True,
            require_encryption_at_rest=True,
            audit_all_operations=True,
        )

    @pytest.fixture
    def insecure_production_config(self):
        """Create an insecure production configuration."""
        return DatabaseConfig(
            database_url="sqlite+aiosqlite:///test.db",
            engine_type="sqlite",
            environment="production",
            pool_size=5,
            max_overflow=0,
            pool_recycle=3600,
            pool_pre_ping=False,
            require_ssl=False,
            validate_connection=False,
            enforce_coppa_constraints=False,
            require_encryption_at_rest=False,
            audit_all_operations=False,
        )

    @pytest.fixture
    def development_config(self):
        """Create a development configuration."""
        return DatabaseConfig(
            database_url="sqlite+aiosqlite:///dev.db",
            engine_type="sqlite",
            environment="development",
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
            pool_pre_ping=True,
            require_ssl=False,
            validate_connection=True,
            enforce_coppa_constraints=True,
            require_encryption_at_rest=False,
            audit_all_operations=True,
        )

    async def test_secure_production_config_passes(self, secure_production_config):
        """Test that a secure production configuration passes all validations."""
        validator = ProductionDatabaseValidator(secure_production_config)

        # Mock database connection responses for secure environment
        with patch(
            "src.infrastructure.validators.data.production_database_validator.create_async_engine"
        ) as mock_engine:
            mock_conn = AsyncMock()
            mock_engine.return_value.__aenter__ = AsyncMock(
                return_value=mock_engine.return_value
            )
            mock_engine.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_engine.return_value.begin.return_value.__aenter__ = AsyncMock(
                return_value=mock_conn
            )
            mock_engine.return_value.begin.return_value.__aexit__ = AsyncMock(
                return_value=None
            )
            mock_engine.return_value.dispose = AsyncMock()

            # Mock SSL validation responses
            ssl_result = MagicMock()
            ssl_result.scalar.return_value = "on"
            ssl_used_result = MagicMock()
            ssl_used_result.scalar.return_value = True

            # Mock encryption validation responses
            encrypt_result = MagicMock()
            encrypt_result.scalar.return_value = 2
            encrypt_settings_result = MagicMock()
            encrypt_settings_result.fetchall.return_value = [("ssl", "on")]

            # Mock RLS validation responses
            rls_result = MagicMock()
            rls_result.fetchone.return_value = ("users", True)

            # Mock backup validation responses
            archive_result = MagicMock()
            archive_result.scalar.return_value = "on"
            wal_result = MagicMock()
            wal_result.scalar.return_value = "replica"

            # Set up the mock responses based on SQL queries
            def mock_execute(query, params=None):
                query_str = str(query).lower()
                if "show ssl" in query_str:
                    return ssl_result
                elif "ssl_is_used" in query_str:
                    return ssl_used_result
                elif "encrypted_count" in query_str or "tablespace" in query_str:
                    return encrypt_result
                elif "pg_settings" in query_str and (
                    "crypt" in query_str or "ssl" in query_str
                ):
                    return encrypt_settings_result
                elif "relname" in query_str and "relrowsecurity" in query_str:
                    return rls_result
                elif "archive_mode" in query_str:
                    return archive_result
                elif "wal_level" in query_str:
                    return wal_result
                else:
                    return MagicMock()

            mock_conn.execute = AsyncMock(side_effect=mock_execute)

            # Test the validation
            result = await validator.validate_all_production_requirements()
            assert result is True
            assert len(validator.validation_errors) == 0

    async def test_insecure_production_config_fails(self, insecure_production_config):
        """Test that an insecure production configuration fails validation."""
        validator = ProductionDatabaseValidator(insecure_production_config)

        with pytest.raises(RuntimeError) as exc_info:
            await validator.validate_all_production_requirements()

        # Verify that critical security errors are detected
        assert "PRODUCTION DATABASE SECURITY VALIDATION FAILED" in str(exc_info.value)
        assert len(validator.validation_errors) > 0

        # Check for specific security violations
        error_messages = " ".join(validator.validation_errors)
        assert (
            "sqlite" in error_messages.lower() or "postgresql" in error_messages.lower()
        )
        assert "ssl" in error_messages.lower()
        assert "coppa" in error_messages.lower()
        assert "encryption" in error_messages.lower()

    async def test_development_config_skips_production_validation(
        self, development_config
    ):
        """Test that development configuration skips production validation."""
        validator = ProductionDatabaseValidator(development_config)

        result = await validator.validate_all_production_requirements()
        assert result is True
        assert len(validator.validation_errors) == 0

    async def test_engine_type_validation(self, secure_production_config):
        """Test engine type validation specifically."""
        validator = ProductionDatabaseValidator(secure_production_config)

        # Test PostgreSQL (should pass)
        result = await validator._validate_engine_type()
        assert result is True

        # Test SQLite (should fail)
        validator.config.engine_type = "sqlite"
        validator.validation_errors.clear()
        result = await validator._validate_engine_type()
        assert result is False
        assert len(validator.validation_errors) > 0

    async def test_connection_security_validation(self, secure_production_config):
        """Test connection security validation."""
        validator = ProductionDatabaseValidator(secure_production_config)

        # Test with secure settings (should pass)
        result = await validator._validate_connection_security()
        assert result is True

        # Test with insecure pool size
        validator.config.pool_size = 5
        validator.validation_errors.clear()
        result = await validator._validate_connection_security()
        assert result is False
        assert len(validator.validation_errors) > 0

    async def test_child_safety_compliance_validation(self, secure_production_config):
        """Test child safety compliance validation."""
        validator = ProductionDatabaseValidator(secure_production_config)

        # Test with compliant settings (should pass)
        result = await validator._validate_child_safety_compliance()
        assert result is True

        # Test with non-compliant settings
        validator.config.enforce_coppa_constraints = False
        validator.config.audit_all_operations = False
        validator.validation_errors.clear()
        result = await validator._validate_child_safety_compliance()
        assert result is False
        assert len(validator.validation_errors) > 0

    async def test_ssl_connection_validation_with_mocked_db(
        self, secure_production_config
    ):
        """Test SSL connection validation with mocked database responses."""
        validator = ProductionDatabaseValidator(secure_production_config)

        with patch(
            "src.infrastructure.validators.data.production_database_validator.create_async_engine"
        ) as mock_engine:
            mock_conn = AsyncMock()
            mock_engine.return_value.__aenter__ = AsyncMock(
                return_value=mock_engine.return_value
            )
            mock_engine.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_engine.return_value.begin.return_value.__aenter__ = AsyncMock(
                return_value=mock_conn
            )
            mock_engine.return_value.begin.return_value.__aexit__ = AsyncMock(
                return_value=None
            )
            mock_engine.return_value.dispose = AsyncMock()

            # Mock SSL enabled responses
            ssl_result = MagicMock()
            ssl_result.scalar.return_value = "on"
            ssl_used_result = MagicMock()
            ssl_used_result.scalar.return_value = True

            def mock_execute(query, params=None):
                query_str = str(query).lower()
                if "show ssl" in query_str:
                    return ssl_result
                elif "ssl_is_used" in query_str:
                    return ssl_used_result
                else:
                    return MagicMock()

            mock_conn.execute = AsyncMock(side_effect=mock_execute)

            result = await validator._validate_ssl_connection()
            assert result is True

    async def test_validation_summary(self, insecure_production_config):
        """Test validation summary generation."""
        validator = ProductionDatabaseValidator(insecure_production_config)

        # Add some mock errors and warnings
        validator.validation_errors = ["Error 1", "Error 2"]
        validator.validation_warnings = ["Warning 1"]

        summary = validator.get_validation_summary()

        assert summary["total_errors"] == 2
        assert summary["total_warnings"] == 1
        assert summary["environment"] == "production"
        assert summary["engine_type"] == "sqlite"
        assert "Error 1" in summary["errors"]
        assert "Warning 1" in summary["warnings"]

    async def test_validate_production_database_function(
        self, secure_production_config
    ):
        """Test the main validation function."""
        with patch(
            "src.infrastructure.validators.data.production_database_validator.create_async_engine"
        ) as mock_engine:
            mock_conn = AsyncMock()
            mock_engine.return_value.__aenter__ = AsyncMock(
                return_value=mock_engine.return_value
            )
            mock_engine.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_engine.return_value.begin.return_value.__aenter__ = AsyncMock(
                return_value=mock_conn
            )
            mock_engine.return_value.begin.return_value.__aexit__ = AsyncMock(
                return_value=None
            )
            mock_engine.return_value.dispose = AsyncMock()

            # Mock successful responses
            mock_result = MagicMock()
            mock_result.scalar.return_value = "on"
            mock_result.fetchall.return_value = []
            mock_result.fetchone.return_value = None
            mock_conn.execute = AsyncMock(return_value=mock_result)

            result = await validate_production_database(secure_production_config)
            assert result is True


class TestProductionValidationIntegration:
    """Integration tests for production validation in startup flow."""

    async def test_production_validation_blocks_insecure_startup(self):
        """Test that insecure production config blocks application startup."""
        # Create insecure configuration
        insecure_config = DatabaseConfig(
            database_url="sqlite+aiosqlite:///test.db",
            engine_type="sqlite",
            environment="production",
            pool_size=1,
            require_ssl=False,
            validate_connection=False,
            enforce_coppa_constraints=False,
            require_encryption_at_rest=False,
            audit_all_operations=False,
        )

        # Validation should fail and raise RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            await validate_production_database(insecure_config)

        assert "PRODUCTION DATABASE SECURITY VALIDATION FAILED" in str(exc_info.value)

    async def test_production_validation_allows_secure_startup(self):
        """Test that secure production config allows application startup."""
        # Create secure configuration
        secure_config = DatabaseConfig(
            database_url="postgresql+asyncpg://user:pass@rds.amazonaws.com:5432/testdb?sslmode=require",
            engine_type="postgresql",
            environment="production",
            pool_size=20,
            require_ssl=True,
            validate_connection=True,
            enforce_coppa_constraints=True,
            require_encryption_at_rest=True,
            audit_all_operations=True,
        )

        with patch(
            "src.infrastructure.validators.data.production_database_validator.create_async_engine"
        ) as mock_engine:
            mock_conn = AsyncMock()
            mock_engine.return_value.__aenter__ = AsyncMock(
                return_value=mock_engine.return_value
            )
            mock_engine.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_engine.return_value.begin.return_value.__aenter__ = AsyncMock(
                return_value=mock_conn
            )
            mock_engine.return_value.begin.return_value.__aexit__ = AsyncMock(
                return_value=None
            )
            mock_engine.return_value.dispose = AsyncMock()

            # Mock all successful responses
            mock_result = MagicMock()
            mock_result.scalar.return_value = "on"
            mock_result.fetchall.return_value = [("ssl", "on")]
            mock_result.fetchone.return_value = ("users", True)
            mock_conn.execute = AsyncMock(return_value=mock_result)

            # Should not raise exception
            result = await validate_production_database(secure_config)
            assert result is True


if __name__ == "__main__":
    # Run tests manually if needed
    pass

    async def run_tests():
        test_class = TestProductionDatabaseValidator()

        # Test secure config
        secure_config = DatabaseConfig(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/testdb?sslmode=require",
            engine_type="postgresql",
            environment="production",
            pool_size=20,
            max_overflow=10,
            pool_recycle=3600,
            pool_pre_ping=True,
            require_ssl=True,
            validate_connection=True,
            enforce_coppa_constraints=True,
            require_encryption_at_rest=True,
            audit_all_operations=True,
        )

        print("🔒 Testing secure production configuration...")
        try:
            await test_class.test_secure_production_config_passes(secure_config)
            print("✅ Secure configuration test passed")
        except Exception as e:
            print(f"❌ Secure configuration test failed: {e}")

        # Test insecure config
        insecure_config = DatabaseConfig(
            database_url="sqlite+aiosqlite:///test.db",
            engine_type="sqlite",
            environment="production",
            pool_size=5,
            require_ssl=False,
            validate_connection=False,
            enforce_coppa_constraints=False,
            require_encryption_at_rest=False,
            audit_all_operations=False,
        )

        print("🔒 Testing insecure production configuration...")
        try:
            await test_class.test_insecure_production_config_fails(insecure_config)
            print("✅ Insecure configuration test passed (correctly failed)")
        except Exception as e:
            print(f"❌ Insecure configuration test failed: {e}")

    # asyncio.run(run_tests())
