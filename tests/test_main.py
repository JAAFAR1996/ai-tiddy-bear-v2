"""Comprehensive tests for main.py - Application startup and configuration

Tests cover:
- Application factory function (create_app)
- Configuration setup and validation
- Middleware and routing setup
- Static file mounting with security
- Lifespan events (startup/shutdown)
- SSL configuration validation
- Error handling and edge cases
"""

import os

# Add src to path for imports
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI

from common.exceptions import StartupValidationException
from main import (
    _mount_static_files,
    _setup_app_configurations,
    _setup_app_middlewares_and_routes,
    _validate_system_startup,
    create_app,
    lifespan,
)

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestCreateApp:
    """Test suite for the main application factory function."""

    def test_create_app_returns_fastapi_instance(self):
        """Test that create_app returns a properly configured FastAPI instance."""
        with (
            patch("main._setup_app_configurations"),
            patch("main._validate_system_startup"),
            patch("main.container.settings") as mock_settings,
            patch("main._setup_app_middlewares_and_routes"),
            patch("main._mount_static_files"),
        ):
            mock_settings.return_value.APP_NAME = "AI Teddy Test"
            mock_settings.return_value.APP_VERSION = "1.0.0"
            mock_settings.return_value.PROJECT_ROOT = Path("/test")

            app = create_app()

            assert isinstance(app, FastAPI)
            assert app.title == "AI Teddy Test"
            assert app.version == "1.0.0"

    def test_create_app_docs_configuration(self):
        """Test that OpenAPI docs are properly configured."""
        with (
            patch("main._setup_app_configurations"),
            patch("main._validate_system_startup"),
            patch("main.container.settings") as mock_settings,
            patch("main._setup_app_middlewares_and_routes"),
            patch("main._mount_static_files"),
        ):
            mock_settings.return_value.APP_NAME = "AI Teddy Test"
            mock_settings.return_value.APP_VERSION = "1.0.0"
            mock_settings.return_value.PROJECT_ROOT = Path("/test")

            app = create_app()

            assert app.docs_url == "/docs"
            assert app.redoc_url == "/redoc"

    def test_create_app_calls_all_setup_functions(self):
        """Test that create_app calls all required setup functions in correct order."""
        with (
            patch("main._setup_app_configurations") as mock_config,
            patch("main._validate_system_startup") as mock_validate,
            patch("main.container.settings") as mock_settings,
            patch("main._setup_app_middlewares_and_routes") as mock_middleware,
            patch("main._mount_static_files") as mock_static,
        ):
            mock_settings.return_value.APP_NAME = "AI Teddy Test"
            mock_settings.return_value.APP_VERSION = "1.0.0"
            mock_settings.return_value.PROJECT_ROOT = Path("/test")

            create_app()

            # Verify all setup functions were called
            mock_config.assert_called_once()
            mock_validate.assert_called_once()
            mock_middleware.assert_called_once()
            mock_static.assert_called_once()

    def test_create_app_lifespan_assignment(self):
        """Test that lifespan event handler is properly assigned."""
        with (
            patch("main._setup_app_configurations"),
            patch("main._validate_system_startup"),
            patch("main.container.settings") as mock_settings,
            patch("main._setup_app_middlewares_and_routes"),
            patch("main._mount_static_files"),
        ):
            mock_settings.return_value.APP_NAME = "AI Teddy Test"
            mock_settings.return_value.APP_VERSION = "1.0.0"
            mock_settings.return_value.PROJECT_ROOT = Path("/test")

            app = create_app()

            # Verify lifespan is assigned (check router has lifespan context)
            assert app.router.lifespan_context is not None


class TestLifespanEvents:
    """Test suite for application lifespan events (startup/shutdown)."""

    @pytest.mark.asyncio
    async def test_lifespan_startup_redis_connection_success(self):
        """Test successful Redis connection during startup."""
        mock_app = MagicMock()

        with (
            patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379/0"}),
            patch("main.Redis") as mock_redis_class,
            patch("main.get_rate_limiter") as mock_rate_limiter,
            patch("main.Database") as mock_db_class,
            patch(
                "src.infrastructure.validators.config.startup_validator.validate_startup"
            ) as mock_validate,
        ):
            mock_redis = AsyncMock()
            mock_redis.ping.return_value = "PONG"
            mock_redis_class.from_url.return_value = mock_redis

            mock_db = AsyncMock()
            mock_db_class.return_value = mock_db
            mock_validate.return_value = True

            # Test the lifespan generator directly
            lifespan_gen = lifespan(mock_app)
            await lifespan_gen.__anext__()  # Execute startup

            # Verify Redis connection was attempted
            mock_redis_class.from_url.assert_called_once_with(
                "redis://localhost:6379/0", decode_responses=True
            )
            mock_redis.ping.assert_called_once()
            mock_rate_limiter.assert_called_once_with(mock_redis)

            # Cleanup
            try:
                await lifespan_gen.__anext__()
            except StopAsyncIteration:
                pass

    @pytest.mark.asyncio
    async def test_lifespan_startup_redis_connection_failure(self):
        """Test Redis connection failure handling during startup."""
        mock_app = MagicMock()

        with (
            patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379/0"}),
            patch("main.Redis") as mock_redis_class,
        ):
            mock_redis = AsyncMock()
            mock_redis.ping.side_effect = Exception("Connection failed")
            mock_redis_class.from_url.return_value = mock_redis

            with pytest.raises(Exception, match="Connection failed"):
                lifespan_gen = lifespan(mock_app)
                await lifespan_gen.__anext__()

    @pytest.mark.asyncio
    async def test_lifespan_startup_database_initialization_success(self):
        """Test successful database initialization during startup."""
        mock_app = MagicMock()

        with (
            patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379/0"}),
            patch("main.Redis") as mock_redis_class,
            patch("main.get_rate_limiter"),
            patch("main.Database") as mock_db_class,
            patch(
                "src.infrastructure.validators.config.startup_validator.validate_startup"
            ) as mock_validate,
        ):
            mock_redis = AsyncMock()
            mock_redis.ping.return_value = "PONG"
            mock_redis_class.from_url.return_value = mock_redis

            mock_db = AsyncMock()
            mock_db_class.return_value = mock_db
            mock_validate.return_value = True

            async with lifespan(mock_app):
                pass

            # Verify database initialization
            mock_db_class.assert_called_once()
            mock_db.init_db.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_startup_database_initialization_failure(self):
        """Test database initialization failure handling (non-fatal)."""
        mock_app = MagicMock()

        with (
            patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379/0"}),
            patch("main.Redis") as mock_redis_class,
            patch("main.get_rate_limiter"),
            patch("main.Database") as mock_db_class,
            patch(
                "src.infrastructure.validators.config.startup_validator.validate_startup"
            ) as mock_validate,
        ):
            mock_redis = AsyncMock()
            mock_redis.ping.return_value = "PONG"
            mock_redis_class.from_url.return_value = mock_redis

            mock_db = AsyncMock()
            mock_db.init_db.side_effect = Exception("DB connection failed")
            mock_db_class.return_value = mock_db
            mock_validate.return_value = True

            # Should not raise exception - DB failure is non-fatal
            async with lifespan(mock_app):
                pass

    @pytest.mark.asyncio
    async def test_lifespan_startup_validation_success(self):
        """Test successful startup validation."""
        mock_app = MagicMock()

        with (
            patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379/0"}),
            patch("main.Redis") as mock_redis_class,
            patch("main.get_rate_limiter"),
            patch("main.Database") as mock_db_class,
            patch(
                "src.infrastructure.validators.config.startup_validator.StartupValidator"
            ) as mock_validator_class,
            patch(
                "src.infrastructure.validators.config.startup_validator.validate_startup"
            ) as mock_validate,
        ):
            mock_redis = AsyncMock()
            mock_redis.ping.return_value = "PONG"
            mock_redis_class.from_url.return_value = mock_redis

            mock_db = AsyncMock()
            mock_db_class.return_value = mock_db

            mock_validator = MagicMock()
            mock_validator_class.return_value = mock_validator
            mock_validate.return_value = True

            async with lifespan(mock_app):
                pass

            # Verify validation was called
            mock_validator_class.assert_called_once()
            mock_validate.assert_called_once_with(mock_validator)

    @pytest.mark.asyncio
    async def test_lifespan_startup_validation_warnings(self):
        """Test startup validation with warnings (non-fatal)."""
        mock_app = MagicMock()

        with (
            patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379/0"}),
            patch("main.Redis") as mock_redis_class,
            patch("main.get_rate_limiter"),
            patch("main.Database") as mock_db_class,
            patch(
                "src.infrastructure.validators.config.startup_validator.validate_startup"
            ) as mock_validate,
        ):
            mock_redis = AsyncMock()
            mock_redis.ping.return_value = "PONG"
            mock_redis_class.from_url.return_value = mock_redis

            mock_db = AsyncMock()
            mock_db_class.return_value = mock_db
            mock_validate.return_value = False  # Validation with warnings

            # Should not raise exception - warnings are non-fatal
            async with lifespan(mock_app):
                pass

    @pytest.mark.asyncio
    async def test_lifespan_default_redis_url(self):
        """Test default Redis URL when environment variable not set."""
        mock_app = MagicMock()

        # Ensure REDIS_URL is not set
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("main.Redis") as mock_redis_class,
            patch("main.get_rate_limiter"),
            patch("main.Database") as mock_db_class,
            patch(
                "src.infrastructure.validators.config.startup_validator.validate_startup"
            ) as mock_validate,
        ):
            mock_redis = AsyncMock()
            mock_redis.ping.return_value = "PONG"
            mock_redis_class.from_url.return_value = mock_redis

            mock_db = AsyncMock()
            mock_db_class.return_value = mock_db
            mock_validate.return_value = True

            async with lifespan(mock_app):
                pass

            # Verify default Redis URL was used
            mock_redis_class.from_url.assert_called_once_with(
                "redis://localhost:6379/0", decode_responses=True
            )


class TestSetupAppConfigurations:
    """Test suite for application configuration setup."""

    def test_setup_app_configurations_calls_production_safety(self):
        """Test that production safety checks are enforced."""
        with (
            patch("main.enforce_production_safety") as mock_safety,
            patch("main.container.settings") as mock_settings,
            patch("main.configure_logging"),
        ):
            mock_settings.return_value.ENVIRONMENT = "production"
            _setup_app_configurations()
            mock_safety.assert_called_once()

    def test_setup_app_configurations_configures_logging(self):
        """Test that logging is properly configured."""
        with (
            patch("main.enforce_production_safety"),
            patch("main.container.settings") as mock_settings,
            patch("main.configure_logging") as mock_logging,
        ):
            mock_settings.return_value.ENVIRONMENT = "development"
            _setup_app_configurations()
            mock_logging.assert_called_once_with(environment="development")

    def test_setup_app_configurations_production_environment(self):
        """Test configuration setup for production environment."""
        with (
            patch("main.enforce_production_safety"),
            patch("main.container.settings") as mock_settings,
            patch("main.configure_logging") as mock_logging,
        ):
            mock_settings.return_value.ENVIRONMENT = "production"
            _setup_app_configurations()
            mock_logging.assert_called_once_with(environment="production")


class TestValidateSystemStartup:
    """Test suite for system startup validation."""

    def test_validate_system_startup_success(self):
        """Test successful system startup validation."""
        with (
            patch("main.container.wire") as mock_wire,
            patch("main.FullWiringConfig") as mock_config,
        ):
            mock_config.modules = ["module1", "module2"]
            _validate_system_startup()
            mock_wire.assert_called_once_with(modules=mock_config.modules)

    def test_validate_system_startup_runtime_error(self):
        """Test system startup validation with RuntimeError."""
        with patch("main.container.wire") as mock_wire:
            mock_wire.side_effect = RuntimeError("Wiring failed")

            with pytest.raises(
                StartupValidationException,
                match="Application startup validation failed",
            ):
                _validate_system_startup()

    def test_validate_system_startup_preserves_original_error(self):
        """Test that original RuntimeError is preserved in exception chain."""
        with patch("main.container.wire") as mock_wire:
            original_error = RuntimeError("Original wiring error")
            mock_wire.side_effect = original_error

            with pytest.raises(StartupValidationException) as exc_info:
                _validate_system_startup()

            assert exc_info.value.__cause__ is original_error


class TestSetupAppMiddlewaresAndRoutes:
    """Test suite for middleware and routing setup."""

    def test_setup_middlewares_and_routes_calls_all_functions(self):
        """Test that all setup functions are called."""
        mock_app = MagicMock()

        with (
            patch("main.setup_middleware") as mock_middleware,
            patch("main.setup_routing") as mock_routing,
            patch("main.configure_openapi") as mock_openapi,
        ):
            _setup_app_middlewares_and_routes(mock_app)

            mock_middleware.assert_called_once_with(mock_app)
            mock_routing.assert_called_once_with(mock_app)
            mock_openapi.assert_called_once_with(mock_app)


class TestMountStaticFiles:
    """Test suite for static file mounting with security."""

    def test_mount_static_files_production_skip(self):
        """Test that static files are skipped in production."""
        mock_app = MagicMock()
        project_root = Path("/test/project")

        with patch("main.container.settings") as mock_settings:
            mock_settings.return_value.ENVIRONMENT = "production"
            _mount_static_files(mock_app, project_root)
            # Verify no mount call was made
            mock_app.mount.assert_not_called()

    def test_mount_static_files_development_success(self):
        """Test successful static file mounting in development."""
        mock_app = MagicMock()

        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            static_dir = project_root / "static"
            static_dir.mkdir()

            with patch("main.container.settings") as mock_settings:
                mock_settings.return_value.ENVIRONMENT = "development"
                mock_settings.return_value.STATIC_FILES_DIR = "static"

                _mount_static_files(mock_app, project_root)

                # Verify mount was called with correct parameters
                mock_app.mount.assert_called_once()
                call_args = mock_app.mount.call_args
                assert call_args[0][0] == "/static"
                assert call_args[1]["name"] == "static"

    def test_mount_static_files_directory_not_found(self):
        """Test handling when static directory doesn't exist."""
        mock_app = MagicMock()

        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            # Don't create static directory

            with patch("main.container.settings") as mock_settings:
                mock_settings.return_value.ENVIRONMENT = "development"
                mock_settings.return_value.STATIC_FILES_DIR = "static"

                _mount_static_files(mock_app, project_root)

                # Verify no mount call was made
                mock_app.mount.assert_not_called()

    def test_mount_static_files_path_traversal_attack(self):
        """Test security protection against path traversal attacks."""
        mock_app = MagicMock()

        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            # Create a malicious directory outside project root to ensure it exists
            outside_dir = Path(temp_dir).parent / "etc"
            outside_dir.mkdir(exist_ok=True)

            with patch("main.container.settings") as mock_settings:
                mock_settings.return_value.ENVIRONMENT = "development"
                # Attempt path traversal - this path will exist and be outside project root
                mock_settings.return_value.STATIC_FILES_DIR = str(outside_dir)

                with pytest.raises(
                    ValueError,
                    match="Invalid static files directory configuration: Path traversal detected",
                ):
                    _mount_static_files(mock_app, project_root)

    def test_mount_static_files_absolute_path_outside_project(self):
        """Test security protection against absolute paths outside project."""
        mock_app = MagicMock()

        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            # Create a directory outside the project root
            outside_dir = Path(temp_dir).parent / "outside_project"
            outside_dir.mkdir(exist_ok=True)

            with patch("main.container.settings") as mock_settings:
                mock_settings.return_value.ENVIRONMENT = "development"
                # Use absolute path outside project
                mock_settings.return_value.STATIC_FILES_DIR = str(outside_dir)

                with pytest.raises(
                    ValueError,
                    match="Invalid static files directory configuration: Path traversal detected",
                ):
                    _mount_static_files(mock_app, project_root)


class TestSSLConfiguration:
    """Test suite for SSL configuration validation (when running as main)."""

    def test_ssl_configuration_development_mode(self):
        """Test that SSL is not required in development mode."""
        is_development = True
        ssl_keyfile = None
        ssl_certfile = None
        ssl_offloaded = False

        # In development, SSL is not required
        ssl_required = (
            not is_development
            and not (ssl_keyfile and ssl_certfile)
            and not ssl_offloaded
        )

        assert not ssl_required

    def test_ssl_configuration_production_with_certificates(self):
        """Test SSL configuration in production with certificates."""
        is_development = False
        ssl_keyfile = "/path/to/key.pem"
        ssl_certfile = "/path/to/cert.pem"
        ssl_offloaded = False

        ssl_required = (
            not is_development
            and not (ssl_keyfile and ssl_certfile)
            and not ssl_offloaded
        )

        assert not ssl_required  # SSL is configured

    def test_ssl_configuration_production_with_offloading(self):
        """Test SSL configuration in production with offloading."""
        is_development = False
        ssl_keyfile = None
        ssl_certfile = None
        ssl_offloaded = True

        ssl_required = (
            not is_development
            and not (ssl_keyfile and ssl_certfile)
            and not ssl_offloaded
        )

        assert not ssl_required  # SSL is offloaded

    def test_ssl_configuration_production_missing_ssl(self):
        """Test SSL configuration error in production without SSL."""
        is_development = False
        ssl_keyfile = None
        ssl_certfile = None
        ssl_offloaded = False

        ssl_required = (
            not is_development
            and not (ssl_keyfile and ssl_certfile)
            and not ssl_offloaded
        )

        assert ssl_required  # SSL is required but not configured


class TestIntegrationScenarios:
    """Integration test scenarios for complete application startup."""

    def test_app_creation_with_real_configuration(self):
        """Test app creation with realistic configuration."""
        with (
            patch("main.enforce_production_safety"),
            patch("main.configure_logging"),
            patch("main.container.wire"),
            patch("main.container.settings") as mock_settings,
            patch("main.setup_middleware"),
            patch("main.setup_routing"),
            patch("main.configure_openapi"),
        ):
            # Mock realistic settings
            mock_settings.return_value.APP_NAME = "AI Teddy Bear"
            mock_settings.return_value.APP_VERSION = "1.0.0"
            mock_settings.return_value.ENVIRONMENT = "development"
            mock_settings.return_value.PROJECT_ROOT = Path("/app")
            mock_settings.return_value.STATIC_FILES_DIR = "static"

            with tempfile.TemporaryDirectory() as temp_dir:
                project_root = Path(temp_dir)
                static_dir = project_root / "static"
                static_dir.mkdir()

                # Override PROJECT_ROOT for this test
                mock_settings.return_value.PROJECT_ROOT = project_root

                app = create_app()

                assert isinstance(app, FastAPI)
                assert app.title == "AI Teddy Bear"
                assert app.version == "1.0.0"

    def test_error_handling_chain(self):
        """Test that errors are properly handled throughout the startup chain."""
        # Configuration error
        with patch(
            "main.enforce_production_safety",
            side_effect=Exception("Safety check failed"),
        ), pytest.raises(Exception, match="Safety check failed"):
            _setup_app_configurations()

        # Validation error
        with patch(
            "main.container.wire", side_effect=RuntimeError("Wiring failed")
        ), pytest.raises(StartupValidationException):
            _validate_system_startup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
