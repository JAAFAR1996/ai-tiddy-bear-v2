"""Production secrets service for DI container integration."""

import asyncio
import os
from typing import Any, Dict, Optional

from src.infrastructure.config.settings import get_settings
from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.secrets_management.config import (
    SecretType,
)
from src.infrastructure.security.secrets_management.secrets_manager import (
    SecretsManager,
    create_secrets_manager,
)

logger = get_logger(__name__, component="security")


class ProductionSecretsService:
    """Production-ready secrets service for secure configuration management."""

    def __init__(self):
        self._manager: Optional[SecretsManager] = None
        self._initialized = False
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize the secrets manager with environment-specific configuration."""
        if self._initialized:
            return

        async with self._lock:
            if self._initialized:
                return

            try:
                settings = get_settings()
                environment = getattr(settings, "ENVIRONMENT", "development")

                # Create secrets manager with appropriate configuration
                vault_url = os.getenv("VAULT_URL")
                vault_token = os.getenv("VAULT_TOKEN")

                self._manager = create_secrets_manager(
                    environment=environment,
                    vault_url=vault_url,
                    vault_token=vault_token,
                )

                self._initialized = True
                logger.info(
                    "Secrets service initialized for environment: %s", environment
                )

            except Exception as e:
                logger.error("Failed to initialize secrets service: %s", e)
                raise

    async def get_secret(
        self, name: str, default: Optional[str] = None
    ) -> Optional[str]:
        """Get a secret value."""
        await self.initialize()

        if not self._manager:
            logger.error("Secrets manager not initialized")
            return default

        try:
            value = await self._manager.get_secret(name)
            return value if value is not None else default
        except Exception as e:
            logger.error("Failed to get secret '%s': %s", name, e)
            return default

    async def get_required_secret(self, name: str) -> str:
        """Get a required secret value, raising an error if not found."""
        value = await self.get_secret(name)
        if value is None:
            raise ValueError(f"Required secret '{name}' not found")
        return value

    async def set_secret(
        self,
        name: str,
        value: str,
        secret_type: SecretType = SecretType.GENERIC,
        rotation_interval_days: Optional[int] = None,
    ) -> bool:
        """Set a secret value."""
        await self.initialize()

        if not self._manager:
            logger.error("Secrets manager not initialized")
            return False

        try:
            return await self._manager.set_secret(
                name, value, secret_type, rotation_interval_days
            )
        except Exception as e:
            logger.error("Failed to set secret '%s': %s", name, e)
            return False

    async def delete_secret(self, name: str) -> bool:
        """Delete a secret."""
        await self.initialize()

        if not self._manager:
            logger.error("Secrets manager not initialized")
            return False

        try:
            return await self._manager.delete_secret(name)
        except Exception as e:
            logger.error("Failed to delete secret '%s': %s", name, e)
            return False

    async def rotate_secret(self, name: str, new_value: str) -> bool:
        """Rotate a secret to a new value."""
        await self.initialize()

        if not self._manager:
            logger.error("Secrets manager not initialized")
            return False

        try:
            return await self._manager.rotate_secret(name, new_value)
        except Exception as e:
            logger.error("Failed to rotate secret '%s': %s", name, e)
            return False

    async def validate_required_secrets(self, required_secrets: list[str]) -> bool:
        """Validate that all required secrets are available."""
        await self.initialize()

        missing_secrets = []

        for secret_name in required_secrets:
            value = await self.get_secret(secret_name)
            if value is None:
                missing_secrets.append(secret_name)

        if missing_secrets:
            logger.error("Missing required secrets: %s", missing_secrets)
            return False

        logger.info("All required secrets validated successfully")
        return True

    async def get_database_url(self) -> str:
        """Get the database URL with fallback logic."""
        # Try async database URL first (for async operations)
        db_url = await self.get_secret("ASYNC_DATABASE_URL")
        if db_url:
            return db_url

        # Fallback to synchronous database URL
        db_url = await self.get_secret("DATABASE_URL")
        if db_url:
            return db_url

        # Final fallback for development
        return "sqlite+aiosqlite:///./test.db"

    async def get_security_config(self) -> Dict[str, Any]:
        """Get all security-related configuration."""
        await self.initialize()

        config = {}

        # Core security secrets
        security_secrets = [
            "SECRET_KEY",
            "JWT_SECRET_KEY",
            "COPPA_ENCRYPTION_KEY",
            "JWT_SECRET",
            "JWT_REFRESH_SECRET",
            "SESSION_SECRET",
            "ENCRYPTION_KEY",
            "DATA_ENCRYPTION_KEY",
            "FIELD_ENCRYPTION_KEY",
        ]

        for secret_name in security_secrets:
            value = await self.get_secret(secret_name)
            if value:
                config[secret_name] = value

        return config

    async def get_api_keys(self) -> Dict[str, Any]:
        """Get all API keys."""
        await self.initialize()

        api_keys = {}

        # API key secrets
        api_key_secrets = [
            "OPENAI_API_KEY",
            "ELEVENLABS_API_KEY",
        ]

        for secret_name in api_key_secrets:
            value = await self.get_secret(secret_name)
            if value:
                api_keys[secret_name] = value

        return api_keys

    def get_sync_secret(
        self, name: str, default: Optional[str] = None
    ) -> Optional[str]:
        """Synchronous version for non-async contexts."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, but this is a sync call
                # Fall back to environment variables
                return os.getenv(name, default)
            else:
                return loop.run_until_complete(self.get_secret(name, default))
        except Exception as e:
            logger.warning("Failed to get secret '%s' synchronously: %s", name, e)
            return os.getenv(name, default)


# Global instance for easy access
_secrets_service: Optional[ProductionSecretsService] = None


def get_secrets_service() -> ProductionSecretsService:
    """Get the global secrets service instance."""
    global _secrets_service
    if _secrets_service is None:
        _secrets_service = ProductionSecretsService()
    return _secrets_service


async def initialize_secrets_service() -> ProductionSecretsService:
    """Initialize and return the secrets service."""
    service = get_secrets_service()
    await service.initialize()
    return service


# Required secrets for the application
REQUIRED_SECRETS = [
    "SECRET_KEY",
    "JWT_SECRET_KEY",
    "COPPA_ENCRYPTION_KEY",
    "DATABASE_URL",
    "OPENAI_API_KEY",
]


async def validate_startup_secrets() -> bool:
    """Validate that all required secrets are available at startup."""
    service = await initialize_secrets_service()
    return await service.validate_required_secrets(REQUIRED_SECRETS)
