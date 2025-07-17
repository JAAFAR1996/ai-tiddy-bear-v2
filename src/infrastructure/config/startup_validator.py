"""Startup validation to ensure all critical dependencies are available."""

import importlib.metadata
from typing import Any

from fastapi import Depends  # Only Depends is needed at the module level

from src.infrastructure.config.settings import Settings
from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.database_health_check import (
    check_database_connection,
)

logger = get_logger(__name__, component="infrastructure")


class StartupValidator:
    """Validates that all critical dependencies and configuration are properly set up."""

    def __init__(
        self,
        settings: Settings = Depends(Settings),
    ) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.settings = settings

    def validate_dependencies(self) -> bool:
        """Validate that all required dependencies are installed using modern metadata."""
        logger.info("🔍 Validating critical dependencies...")
        required_packages = [
            ("pydantic", "Pydantic"),
            ("fastapi", "FastAPI"),
            ("sqlalchemy", "SQLAlchemy"),
            ("asyncpg", "AsyncPG"),
            ("redis", "Redis"),
            ("uvicorn", "Uvicorn"),
            ("python-jose", "Python-JOSE"),
            ("passlib", "Passlib"),
            ("openai", "OpenAI"),
            ("cryptography", "Cryptography"),
        ]
        for package_name, display_name in required_packages:
            try:
                importlib.metadata.version(package_name)
                logger.debug(f"✅ {display_name} available")
            except importlib.metadata.PackageNotFoundError:
                error_msg = f"❌ {display_name} ({package_name}) is required but not installed"
                self.errors.append(error_msg)
                logger.error(error_msg)
        return len(self.errors) == 0

    def validate_environment(self) -> bool:
        """Validate environment configuration."""
        logger.info("🔍 Validating environment configuration...")
        # Access settings directly from the injected settings object
        # This assumes that the settings object has already loaded values from environment variables
        # and performed basic Pydantic validation.
        # Check for critical settings presence
        if not self.settings.security.SECRET_KEY:
            self._add_error("❌ SECRET_KEY is required but not set")
        elif len(self.settings.security.SECRET_KEY) < 32:
            self._add_error(
                "❌ SECRET_KEY must be at least 32 characters long"
            )
        else:
            logger.debug("✅ SECRET_KEY configured")
        if not self.settings.security.JWT_SECRET_KEY:
            self._add_error("❌ JWT_SECRET_KEY is required but not set")
        elif len(self.settings.security.JWT_SECRET_KEY) < 32:
            self._add_error(
                "❌ JWT_SECRET_KEY must be at least 32 characters long"
            )
        else:
            logger.debug("✅ JWT_SECRET_KEY configured")
        if not self.settings.ai.OPENAI_API_KEY:
            self._add_error("❌ OPENAI_API_KEY is required but not set")
        elif not self.settings.ai.OPENAI_API_KEY.startswith("sk-"):
            self._add_error(
                "❌ OPENAI_API_KEY must be a valid OpenAI API key (starts with 'sk-')",
            )
        else:
            logger.debug("✅ OPENAI_API_KEY configured")
        if not self.settings.database.DATABASE_URL:
            self._add_error("❌ DATABASE_URL is required but not set")
        else:
            logger.debug("✅ DATABASE_URL configured")
        if not self.settings.redis.REDIS_URL:
            self._add_error("❌ REDIS_URL is required but not set")
        else:
            logger.debug("✅ REDIS_URL configured")
        if not self.settings.security.COPPA_ENCRYPTION_KEY:
            self._add_error("❌ COPPA_ENCRYPTION_KEY is required but not set")
        elif len(self.settings.security.COPPA_ENCRYPTION_KEY) != 44:
            self._add_error(
                "❌ COPPA_ENCRYPTION_KEY must be a valid Fernet key (44 characters)",
            )
        else:
            logger.debug("✅ COPPA_ENCRYPTION_KEY configured")
        return len(self.errors) == 0

    def validate_security(self) -> bool:
        """Validate security configuration."""
        logger.info("🔍 Validating security configuration...")
        # Check for development/test values in production
        secret_key = self.settings.security.SECRET_KEY
        jwt_secret = self.settings.security.JWT_SECRET_KEY
        dangerous_values = [
            "changeme",
            "test",
            "development",
            "default",
            "secret",
            "password",
            "12345",
        ]
        for dangerous in dangerous_values:
            if dangerous.lower() in secret_key.lower():
                error_msg = f"❌ SECRET_KEY contains unsafe value: {dangerous}"
                self.errors.append(error_msg)
                logger.error(error_msg)
            if dangerous.lower() in jwt_secret.lower():
                error_msg = (
                    f"❌ JWT_SECRET_KEY contains unsafe value: {dangerous}"
                )
                self.errors.append(error_msg)
                logger.error(error_msg)
        return len(self.errors) == 0

    async def _validate_database_connection_robust(self) -> bool:
        """Validates the database connection with proper error handling, timeouts, and retries."""
        logger.info("🔍 Validating database connection...")
        if not self.settings.DATABASE_URL:
            self._add_error("DATABASE_URL is not configured.")
            return False
        try:
            is_healthy = await check_database_connection(
                self.settings.DATABASE_URL
            )
            if not is_healthy:
                self._add_error(
                    "Database connection health check failed after multiple retries.",
                )
                return False
            logger.info("✅ Database connection is healthy.")
            return True
        except Exception as e:
            self._add_error(
                f"An unexpected error occurred during database validation: {e}",
                e,
            )
            return False

    async def validate_all(self) -> bool:
        """Runs all startup validations, including asynchronous checks."""
        logger.info("🚀 Starting comprehensive startup validation...")
        # Synchronous validations
        sync_validations = [
            self.validate_dependencies,
            self.validate_environment,
            self.validate_security,
        ]
        for validation_fn in sync_validations:
            validation_fn()
        # Asynchronous validations
        await self._validate_database_connection_robust()
        # Report results
        if self.warnings:
            logger.warning(f"⚠️ {len(self.warnings)} warnings found:")
            for warning in self.warnings:
                logger.warning(f"  - {warning}")
        if self.errors:
            logger.error(f"❌ {len(self.errors)} critical errors found:")
            for error in self.errors:
                logger.error(f"  - {error}")
            logger.critical(
                "🛑 System cannot start due to critical validation errors."
            )
            return False
        logger.info(
            "✅ All startup validations passed successfully. System is ready."
        )
        return True

    def _add_error(self, message: str, exc: Exception | None = None) -> None:
        """Adds an error to the list and logs it, optionally with an exception."""
        self.errors.append(message)
        if exc:
            logger.error(message, exc_info=True)
        else:
            logger.error(message)

    def get_validation_report(self) -> dict[str, Any]:
        """Get detailed validation report."""
        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
        }


async def validate_startup(validator: "StartupValidator") -> bool:
    """Asynchronous startup validation function.
    Runs the provided validator, raising a critical error if validation fails.
    """
    try:
        is_valid = await validator.validate_all()
        if not is_valid:
            # Errors are already logged by the validator
            raise RuntimeError(
                "Startup validation failed. Check logs for critical errors.",
            )
        return True
    except Exception as e:
        logger.critical(
            f"A critical exception occurred during startup validation: {e}",
            exc_info=True,
        )
        # Re-raise to ensure the application startup is halted
        raise RuntimeError("Critical startup validation failed") from e


if __name__ == "__main__":
    import asyncio

    # Example of how to run the async validation directly
    async def main():
        logger.info("Running startup validation directly...")
        # This requires the container to be properly configured and initialized
        # For direct script execution, you might need a mock or simplified setup.
        # The following line is for demonstration and may need adjustment.
        # The original code had container.wire(modules=[__name__]) which is removed.
        # If you need to wire dependencies for direct script execution, you'll need to do it here.
        # For now, we'll just run the validation directly.
        try:
            # Assuming Settings is available directly or needs to be imported/instantiated
            # For direct script execution, you might need a mock or simplified setup.
            # The following line is for demonstration and may need adjustment.
            # settings = Settings() # Uncomment and adjust if Settings needs to be instantiated here
            # validator = StartupValidator(settings=settings) # Uncomment and
            # adjust if Settings needs to be passed to validator
            validator = (
                StartupValidator()
            )  # Directly instantiate without Settings dependency
            await validate_startup(validator)
            logger.info("Direct validation check passed.")
        except RuntimeError as e:
            logger.error(f"Direct validation check failed: {e}")

    asyncio.run(main())
