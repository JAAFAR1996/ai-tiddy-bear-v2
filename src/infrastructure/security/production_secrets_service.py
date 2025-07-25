"""Production Secrets Service for DI Integration.

Integrates secrets management with the existing dependency injection container.
Provides secure configuration loading for all application services.
"""

import os
from functools import lru_cache
from typing import Any, Dict

from pydantic import SecretStr

from src.infrastructure.config.settings import get_settings
from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.secrets_management import (
    SecretType,
    create_secrets_manager,
)

logger = get_logger(__name__, component="security")


class ProductionSecretsService:
    """Production secrets service for secure configuration management."""

    def __init__(self):
        self._secrets_manager = None
        self._cached_secrets: Dict[str, str] = {}

    @property
    def secrets_manager(self):
        """Lazy-loaded secrets manager."""
        if self._secrets_manager is None:
            settings = get_settings()
            environment = getattr(settings, "ENVIRONMENT", "production")

            # Get Vault configuration from environment
            vault_url = os.environ.get("VAULT_URL")
            vault_token = os.environ.get("VAULT_TOKEN")

            self._secrets_manager = create_secrets_manager(
                environment=environment,
                vault_url=vault_url,
                vault_token=vault_token,
            )
            logger.info(f"Initialized secrets manager for environment: {environment}")

        return self._secrets_manager

    async def get_secret(self, name: str, required: bool = True) -> str | None:
        """Get a secret value with caching."""
        try:
            # Check cache first
            if name in self._cached_secrets:
                return self._cached_secrets[name]

            # Get from secrets manager
            value = await self.secrets_manager.get_secret(name)

            if value is None and required:
                logger.error(f"Required secret '{name}' not found")
                raise ValueError(f"Required secret '{name}' not found")

            if value:
                self._cached_secrets[name] = value
                logger.debug(f"Retrieved secret '{name}' successfully")

            return value

        except Exception as e:
            logger.error(f"Failed to get secret '{name}': {e}")
            if required:
                raise
            return None

    async def get_secret_str(
        self, name: str, required: bool = True
    ) -> SecretStr | None:
        """Get a secret as SecretStr."""
        value = await self.get_secret(name, required)
        return SecretStr(value) if value else None

    async def set_secret(
        self,
        name: str,
        value: str,
        secret_type: SecretType = SecretType.TOKEN,
    ) -> bool:
        """Set a secret value."""
        try:
            success = await self.secrets_manager.set_secret(name, value, secret_type)
            if success:
                # Update cache
                self._cached_secrets[name] = value
                logger.info(f"Set secret '{name}' successfully")
            return success

        except Exception as e:
            logger.error(f"Failed to set secret '{name}': {e}")
            return False

    async def rotate_secret(self, name: str, new_value: str) -> bool:
        """Rotate a secret to a new value."""
        try:
            success = await self.secrets_manager.rotate_secret(name, new_value)
            if success:
                # Update cache
                self._cached_secrets[name] = new_value
                logger.info(f"Rotated secret '{name}' successfully")
            return success

        except Exception as e:
            logger.error(f"Failed to rotate secret '{name}': {e}")
            return False

    def get_env_with_fallback(
        self, name: str, default: str | None = None
    ) -> str | None:
        """Get environment variable with fallback to default."""
        value = os.environ.get(name, default)
        if value:
            logger.debug(f"Retrieved environment variable '{name}'")
        return value

    def validate_required_secrets(self, required_secrets: list[str]) -> None:
        """Validate that all required secrets are available."""
        missing_secrets = []

        for secret_name in required_secrets:
            # Check environment first for immediate validation
            if not os.environ.get(secret_name):
                missing_secrets.append(secret_name)

        if missing_secrets:
            error_msg = f"Missing required secrets: {missing_secrets}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info(f"All required secrets validated: {required_secrets}")

    async def health_check(self) -> Dict[str, Any]:
        """Health check for secrets service."""
        try:
            # Test basic functionality
            test_secret = "health_check_test"
            test_value = "test_value_123"

            # Try to set and get a test secret
            set_success = await self.set_secret(
                test_secret, test_value, SecretType.TOKEN
            )
            if set_success:
                retrieved_value = await self.get_secret(test_secret, required=False)
                get_success = retrieved_value == test_value

                # Clean up test secret
                await self.secrets_manager.delete_secret(test_secret)
            else:
                get_success = False

            return {
                "status": "healthy" if (set_success and get_success) else "unhealthy",
                "secrets_manager_available": self._secrets_manager is not None,
                "set_operation": set_success,
                "get_operation": get_success,
                "cached_secrets_count": len(self._cached_secrets),
            }

        except Exception as e:
            logger.error(f"Secrets service health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "secrets_manager_available": self._secrets_manager is not None,
                "cached_secrets_count": len(self._cached_secrets),
            }


@lru_cache(maxsize=1)
def get_secrets_service() -> ProductionSecretsService:
    """Get singleton secrets service instance."""
    return ProductionSecretsService()


# Production secrets loading functions
async def load_database_secrets() -> Dict[str, str]:
    """Load database connection secrets."""
    secrets_service = get_secrets_service()

    return {
        "DATABASE_URL": await secrets_service.get_secret("DATABASE_URL", required=True),
        "DB_PASSWORD": await secrets_service.get_secret("DB_PASSWORD", required=False)
        or "",
    }


async def load_security_secrets() -> Dict[str, str]:
    """Load security-related secrets."""
    secrets_service = get_secrets_service()

    return {
        "SECRET_KEY": await secrets_service.get_secret("SECRET_KEY", required=True),
        "JWT_SECRET_KEY": await secrets_service.get_secret(
            "JWT_SECRET_KEY", required=True
        ),
        "COPPA_ENCRYPTION_KEY": await secrets_service.get_secret(
            "COPPA_ENCRYPTION_KEY", required=True
        ),
    }


async def load_ai_service_secrets() -> Dict[str, str]:
    """Load AI service API keys."""
    secrets_service = get_secrets_service()

    return {
        "OPENAI_API_KEY": await secrets_service.get_secret(
            "OPENAI_API_KEY", required=True
        ),
        "ANTHROPIC_API_KEY": await secrets_service.get_secret(
            "ANTHROPIC_API_KEY", required=False
        )
        or "",
        "ELEVENLABS_API_KEY": await secrets_service.get_secret(
            "ELEVENLABS_API_KEY", required=False
        )
        or "",
    }


async def load_redis_secrets() -> Dict[str, str]:
    """Load Redis connection secrets."""
    secrets_service = get_secrets_service()

    return {
        "REDIS_URL": await secrets_service.get_secret("REDIS_URL", required=True),
        "REDIS_PASSWORD": await secrets_service.get_secret(
            "REDIS_PASSWORD", required=False
        )
        or "",
    }


# Validation functions for production deployment
def validate_production_secrets() -> None:
    """Validate all required secrets for production deployment."""
    secrets_service = get_secrets_service()

    required_secrets = [
        "SECRET_KEY",
        "JWT_SECRET_KEY",
        "COPPA_ENCRYPTION_KEY",
        "DATABASE_URL",
        "REDIS_URL",
        "OPENAI_API_KEY",
    ]

    try:
        secrets_service.validate_required_secrets(required_secrets)
        logger.info("✅ All production secrets validated successfully")
    except ValueError as e:
        logger.error(f"❌ Production secrets validation failed: {e}")
        raise


def setup_production_environment() -> None:
    """Setup production environment with secure secrets loading."""
    try:
        # Validate environment
        environment = os.environ.get("ENVIRONMENT", "development")

        if environment == "production":
            validate_production_secrets()
            logger.info("🔒 Production environment configured with secure secrets")
        else:
            logger.info(f"🔧 Development environment configured: {environment}")

    except Exception as e:
        logger.error(f"❌ Failed to setup production environment: {e}")
        raise
