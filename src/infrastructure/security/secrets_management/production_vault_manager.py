"""Production-grade secrets manager with HashiCorp Vault as primary backend.

This module provides a comprehensive secrets management solution that:
- Uses HashiCorp Vault as the PRIMARY and ONLY backend in production
- Implements fail-fast behavior when Vault is unavailable
- Provides comprehensive audit logging without exposing secret values
- Supports key rotation and health monitoring
- NO fallback mechanisms in production (security requirement)

CRITICAL SECURITY REQUIREMENTS:
- Production systems MUST fail if Vault is unavailable
- NO dummy, mock, or placeholder values allowed
- ALL operations must be audited
- Key rotation must be supported for child-related secrets
"""

import asyncio
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional, Tuple

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.encryption.vault_client import (
    VaultClient,
    VaultConnectionError,
    VaultSecretNotFoundError,
    get_vault_client_async,
)

logger = get_logger(__name__, component="security")


class SecretType(str, Enum):
    """Types of secrets for categorization and handling."""

    API_KEY = "api_key"
    DATABASE_CREDENTIAL = "database_credential"
    ENCRYPTION_KEY = "encryption_key"
    JWT_SECRET = "jwt_secret"
    CERTIFICATE = "certificate"
    PASSWORD = "password"
    TOKEN = "token"
    CHILD_DATA_KEY = "child_data_key"  # Special handling for child-related keys


@dataclass
class SecretMetadata:
    """Metadata for secrets stored in Vault."""

    secret_type: SecretType
    created_at: datetime
    last_accessed: datetime
    last_rotated: Optional[datetime] = None
    rotation_interval_days: Optional[int] = None
    tags: Optional[Dict[str, str]] = None
    child_related: bool = False  # Flag for COPPA-sensitive data


class ProductionVaultSecretsManager:
    """Production secrets manager using HashiCorp Vault as the ONLY backend.

    Features:
    - Vault-only operation (NO fallbacks in production)
    - Comprehensive audit logging
    - Key rotation support
    - Health monitoring
    - Fail-fast behavior
    - Special handling for child-related secrets
    """

    # Secrets that are CRITICAL for child data protection
    CHILD_CRITICAL_SECRETS = [
        "child_data_encryption_key",
        "child_pii_encryption_key",
        "child_profile_key",
        "coppa_compliance_key",
    ]

    # All required secrets for production operation
    REQUIRED_PRODUCTION_SECRETS = [
        "jwt_secret_key",
        "database_encryption_key",
        "master_encryption_key",
        "api_encryption_key",
        *CHILD_CRITICAL_SECRETS,
    ]

    def __init__(self, vault_client: Optional[VaultClient] = None):
        self.vault_client = vault_client
        self._initialized = False
        self._last_health_check = datetime.min
        self._health_check_interval = timedelta(minutes=5)
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._cache_ttl = timedelta(minutes=5)
        self._lock = asyncio.Lock()

        # Determine environment
        self.environment = os.getenv("ENVIRONMENT", "production").lower()
        self.is_production = self.environment == "production"

        logger.info(
            f"ProductionVaultSecretsManager initialized for environment: {self.environment}"
        )

    async def initialize(self) -> None:
        """Initialize the secrets manager with strict validation."""
        if self._initialized:
            return

        async with self._lock:
            if self._initialized:
                return

            try:
                # Get or create Vault client
                if not self.vault_client:
                    self.vault_client = await get_vault_client_async()

                # Verify Vault connectivity
                health_status = await self.vault_client.health_check()
                if health_status["status"] != "healthy":
                    raise VaultConnectionError(f"Vault is not healthy: {health_status}")

                # In production, validate ALL required secrets exist
                if self.is_production:
                    await self._validate_production_secrets()

                # Test basic operations
                await self._test_vault_operations()

                self._initialized = True
                logger.info("ProductionVaultSecretsManager successfully initialized")

            except Exception as e:
                logger.critical(f"Secrets manager initialization FAILED: {e}")
                if self.is_production:
                    # FAIL FAST in production
                    raise RuntimeError(
                        "CRITICAL: Secrets manager cannot start without Vault connectivity. "
                        "This is a HARD REQUIREMENT for production child data safety."
                    ) from e
                else:
                    raise

    async def _validate_production_secrets(self) -> None:
        """Validate that all required production secrets exist in Vault."""
        logger.info("Validating required production secrets in Vault...")

        validation_results = await self.vault_client.validate_required_secrets(
            self.REQUIRED_PRODUCTION_SECRETS
        )

        missing_secrets = [
            secret for secret, exists in validation_results.items() if not exists
        ]

        if missing_secrets:
            logger.critical(
                f"CRITICAL: Missing required secrets in Vault: {missing_secrets}"
            )
            raise VaultSecretNotFoundError(
                f"Required production secrets missing from Vault: {missing_secrets}. "
                f"These must be provisioned by the security team before system startup."
            )

        logger.info(
            f"All {len(self.REQUIRED_PRODUCTION_SECRETS)} required secrets validated in Vault"
        )

    async def _test_vault_operations(self) -> None:
        """Test basic Vault operations to ensure functionality."""
        test_secret_path = "_health_check_test"
        test_data = {"test": "health_check", "timestamp": datetime.utcnow().isoformat()}

        try:
            # Test write
            await self.vault_client.put_secret(test_secret_path, test_data)

            # Test read
            retrieved_data = await self.vault_client.get_secret(test_secret_path)

            if retrieved_data.get("test") != "health_check":
                raise VaultConnectionError("Vault read/write test failed")

            # Test delete
            await self.vault_client.delete_secret(test_secret_path)

            logger.debug("Vault operations test completed successfully")

        except Exception as e:
            logger.error(f"Vault operations test failed: {e}")
            raise VaultConnectionError(f"Vault functionality test failed: {e}") from e

    async def get_secret(
        self,
        secret_name: str,
        secret_type: Optional[SecretType] = None,
        use_cache: bool = True,
    ) -> str:
        """Get a secret value from Vault.

        Args:
            secret_name: Name of the secret
            secret_type: Type of secret for proper handling
            use_cache: Whether to use local cache

        Returns:
            Secret value as string

        Raises:
            VaultSecretNotFoundError: If secret doesn't exist
            VaultConnectionError: If Vault is not accessible
        """
        if not self._initialized:
            await self.initialize()

        # Check cache first (if enabled)
        if use_cache:
            cached_value = self._get_from_cache(secret_name)
            if cached_value is not None:
                logger.debug(f"Secret retrieved from cache: {secret_name}")
                return cached_value

        try:
            secret_data = await self.vault_client.get_secret(secret_name)

            # Extract the actual secret value
            secret_value = secret_data.get("value")
            if secret_value is None:
                raise VaultSecretNotFoundError(
                    f"Secret value not found for: {secret_name}"
                )

            # Update cache
            if use_cache:
                self._cache[secret_name] = (secret_value, datetime.utcnow())

            # Update access metadata (in background)
            asyncio.create_task(self._update_secret_metadata(secret_name, "accessed"))

            # Audit log (NO secret value)
            logger.info(f"Secret retrieved: name={secret_name}, type={secret_type}")

            return secret_value

        except VaultSecretNotFoundError:
            logger.warning(f"Secret not found: {secret_name}")
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{secret_name}': {e}")
            raise VaultConnectionError(
                f"Secret retrieval failed for '{secret_name}': {e}"
            ) from e

    async def set_secret(
        self,
        secret_name: str,
        secret_value: str,
        secret_type: SecretType,
        rotation_interval_days: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None,
        child_related: bool = False,
    ) -> bool:
        """Store a secret in Vault with metadata.

        Args:
            secret_name: Name of the secret
            secret_value: Secret value to store
            secret_type: Type of secret
            rotation_interval_days: Days between rotations
            tags: Additional tags for the secret
            child_related: Whether this secret is related to child data

        Returns:
            True if successful
        """
        if not self._initialized:
            await self.initialize()

        if not secret_value or secret_value.strip() == "":
            raise ValueError(f"Secret value cannot be empty for: {secret_name}")

        # Validate against forbidden values
        forbidden_values = [
            "dev-key-not-secure",
            "test-key",
            "default-key",
            "changeme",
            "password",
            "secret",
            "key123",
            "placeholder",
            "dummy",
            "mock",
        ]

        if secret_value.lower() in forbidden_values:
            raise ValueError(
                f"Secret value for '{secret_name}' is a forbidden placeholder. "
                f"Production secrets must be cryptographically secure."
            )

        try:
            current_time = datetime.utcnow()

            # Prepare secret data with metadata
            secret_data = {
                "value": secret_value,
                "secret_type": secret_type.value,
                "created_at": current_time.isoformat(),
                "last_accessed": current_time.isoformat(),
                "child_related": child_related,
                "tags": tags or {},
                "rotation_interval_days": rotation_interval_days,
            }

            # Store in Vault
            await self.vault_client.put_secret(secret_name, secret_data)

            # Clear cache
            self._cache.pop(secret_name, None)

            # Audit log (NO secret value)
            logger.info(
                f"Secret stored: name={secret_name}, type={secret_type.value}, "
                f"child_related={child_related}, rotation_days={rotation_interval_days}"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to store secret '{secret_name}': {e}")
            raise VaultConnectionError(
                f"Secret storage failed for '{secret_name}': {e}"
            ) from e

    async def rotate_secret(
        self,
        secret_name: str,
        new_secret_value: str,
        secret_type: Optional[SecretType] = None,
    ) -> bool:
        """Rotate a secret to a new value.

        Args:
            secret_name: Name of the secret to rotate
            new_secret_value: New secret value
            secret_type: Type of secret (if not provided, will be read from existing)

        Returns:
            True if successful
        """
        if not self._initialized:
            await self.initialize()

        try:
            # Get existing metadata
            existing_data = await self.vault_client.get_secret(secret_name)

            # Update with new value and rotation timestamp
            existing_data["value"] = new_secret_value
            existing_data["last_rotated"] = datetime.utcnow().isoformat()
            existing_data["last_accessed"] = datetime.utcnow().isoformat()

            # Store updated secret
            await self.vault_client.put_secret(secret_name, existing_data)

            # Clear cache
            self._cache.pop(secret_name, None)

            # Special logging for child-related secrets
            is_child_related = existing_data.get("child_related", False)
            if is_child_related:
                logger.info(f"CHILD-RELATED secret rotated: {secret_name}")

            logger.info(f"Secret rotated successfully: {secret_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to rotate secret '{secret_name}': {e}")
            raise VaultConnectionError(
                f"Secret rotation failed for '{secret_name}': {e}"
            ) from e

    async def get_encryption_key(
        self, key_name: str, purpose: str = "default"
    ) -> bytes:
        """Get an encryption key from Vault.

        Args:
            key_name: Name of the encryption key
            purpose: Purpose of the key (for audit trail)

        Returns:
            Raw encryption key bytes
        """
        if not self._initialized:
            await self.initialize()

        try:
            key_bytes = await self.vault_client.get_encryption_key(key_name, purpose)

            logger.info(f"Encryption key retrieved: name={key_name}, purpose={purpose}")
            return key_bytes

        except VaultSecretNotFoundError:
            logger.critical(
                f"Encryption key '{key_name}' not found in Vault. "
                f"This key must be manually provisioned by the security team."
            )
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve encryption key '{key_name}': {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of the secrets management system.

        Returns:
            Dictionary containing health status information
        """
        current_time = datetime.utcnow()

        # Skip frequent health checks
        if current_time - self._last_health_check < self._health_check_interval:
            return {
                "status": "healthy",
                "cached": True,
                "last_check": self._last_health_check.isoformat(),
            }

        try:
            if not self._initialized:
                await self.initialize()

            # Check Vault health
            vault_health = await self.vault_client.health_check()

            # Check required secrets (in production)
            secrets_status = "unknown"
            if self.is_production:
                validation_results = await self.vault_client.validate_required_secrets(
                    self.REQUIRED_PRODUCTION_SECRETS
                )
                missing_secrets = [
                    s for s, exists in validation_results.items() if not exists
                ]
                secrets_status = (
                    "healthy" if not missing_secrets else f"missing: {missing_secrets}"
                )

            self._last_health_check = current_time

            result = {
                "status": "healthy"
                if vault_health["status"] == "healthy" and not missing_secrets
                else "unhealthy",
                "vault_health": vault_health,
                "secrets_validation": secrets_status,
                "environment": self.environment,
                "initialized": self._initialized,
                "cache_size": len(self._cache),
                "last_check": current_time.isoformat(),
            }

            if result["status"] == "healthy":
                logger.debug("Secrets manager health check: HEALTHY")
            else:
                logger.warning(f"Secrets manager health check: UNHEALTHY - {result}")

            return result

        except Exception as e:
            logger.error(f"Secrets manager health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "environment": self.environment,
                "last_check": current_time.isoformat(),
            }

    async def validate_startup_requirements(self) -> bool:
        """Validate that all startup requirements are met.

        Returns:
            True if all requirements are satisfied

        Raises:
            RuntimeError: If critical requirements are not met in production
        """
        try:
            logger.info("Validating secrets manager startup requirements...")

            # Initialize if not done
            if not self._initialized:
                await self.initialize()

            # Check Vault connectivity
            health_status = await self.health_check()
            if health_status["status"] != "healthy":
                if self.is_production:
                    raise RuntimeError(f"Vault health check failed: {health_status}")
                else:
                    logger.warning(
                        f"Vault health check failed (non-production): {health_status}"
                    )

            # Validate child-critical secrets (always required)
            child_secrets_status = await self.vault_client.validate_required_secrets(
                self.CHILD_CRITICAL_SECRETS
            )
            missing_child_secrets = [
                s for s, exists in child_secrets_status.items() if not exists
            ]

            if missing_child_secrets:
                raise RuntimeError(
                    f"CRITICAL: Child-related secrets missing from Vault: {missing_child_secrets}. "
                    f"These are REQUIRED for COPPA compliance and child data protection."
                )

            logger.info("All startup requirements validated successfully")
            return True

        except Exception as e:
            logger.critical(f"Startup validation failed: {e}")
            if self.is_production:
                raise RuntimeError(f"Production startup validation failed: {e}") from e
            else:
                logger.warning(f"Non-production startup validation failed: {e}")
                return False

    def _get_from_cache(self, secret_name: str) -> Optional[str]:
        """Get secret from cache if still valid."""
        if secret_name not in self._cache:
            return None

        secret_value, cached_time = self._cache[secret_name]

        if datetime.utcnow() - cached_time > self._cache_ttl:
            # Expired
            del self._cache[secret_name]
            return None

        return secret_value

    async def _update_secret_metadata(self, secret_name: str, operation: str) -> None:
        """Update secret metadata in background (non-blocking)."""
        try:
            # This is a background operation, so we don't want to fail the main request
            secret_data = await self.vault_client.get_secret(secret_name)
            secret_data["last_accessed"] = datetime.utcnow().isoformat()
            await self.vault_client.put_secret(secret_name, secret_data)
        except Exception as e:
            # Log but don't raise
            logger.debug(f"Failed to update metadata for {secret_name}: {e}")

    async def cleanup(self) -> None:
        """Cleanup resources."""
        self._cache.clear()
        logger.info("ProductionVaultSecretsManager cleanup completed")


# Global instance
_secrets_manager: Optional[ProductionVaultSecretsManager] = None


async def get_production_secrets_manager() -> ProductionVaultSecretsManager:
    """Get the global production secrets manager instance."""
    global _secrets_manager

    if _secrets_manager is None:
        _secrets_manager = ProductionVaultSecretsManager()
        await _secrets_manager.initialize()

    return _secrets_manager


async def validate_production_startup() -> bool:
    """Validate that the production environment is properly configured.

    This function should be called during application startup to ensure
    all security requirements are met before processing any requests.

    Returns:
        True if validation passes

    Raises:
        RuntimeError: If validation fails in production
    """
    secrets_manager = await get_production_secrets_manager()
    return await secrets_manager.validate_startup_requirements()
