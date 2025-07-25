#!/usr/bin/env python3
"""Startup validation script for HashiCorp Vault integration.

This script performs comprehensive validation of the Vault integration
and all required secrets before the application starts. It implements
fail-fast behavior to ensure the system never starts without proper
security configuration.

CRITICAL REQUIREMENTS:
- System MUST fail if Vault is unavailable
- ALL required secrets must exist in Vault
- Child-related encryption keys MUST be validated
- Health checks MUST pass before startup
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Optional

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.encryption.vault_client import (
    VaultClient,
    VaultSecretNotFoundError,
    get_vault_client_async,
)
from src.infrastructure.security.secrets_management.production_vault_manager import (
    ProductionVaultSecretsManager,
    SecretType,
    validate_production_startup,
)

logger = get_logger(__name__, component="startup")


class StartupValidationError(Exception):
    """Raised when startup validation fails."""


class VaultStartupValidator:
    """Comprehensive Vault startup validation."""

    def __init__(self):
        self.vault_client: Optional[VaultClient] = None
        self.secrets_manager: Optional[ProductionVaultSecretsManager] = None
        self.environment = os.getenv("ENVIRONMENT", "production").lower()
        self.is_production = self.environment == "production"

        # Required environment variables
        self.required_env_vars = ["VAULT_URL", "VAULT_TOKEN"]

        # Critical secrets that MUST exist
        self.critical_secrets = [
            "jwt_secret_key",
            "database_encryption_key",
            "master_encryption_key",
            "child_data_encryption_key",
            "child_pii_encryption_key",
            "coppa_compliance_key",
        ]

        # Optional secrets (warnings only)
        self.optional_secrets = [
            "openai_api_key",
            "elevenlabs_api_key",
            "smtp_password",
        ]

    async def run_full_validation(self) -> bool:
        """Run complete startup validation.

        Returns:
            True if all validations pass

        Raises:
            StartupValidationError: If critical validation fails
        """
        logger.info("=" * 80)
        logger.info("🚀 STARTING HASHICORP VAULT INTEGRATION VALIDATION")
        logger.info("=" * 80)
        logger.info(f"Environment: {self.environment}")
        logger.info(f"Production mode: {self.is_production}")
        logger.info(f"Timestamp: {datetime.utcnow().isoformat()}")
        logger.info("-" * 80)

        try:
            # Step 1: Validate environment variables
            await self._validate_environment_variables()

            # Step 2: Initialize Vault client
            await self._initialize_vault_client()

            # Step 3: Test Vault connectivity
            await self._test_vault_connectivity()

            # Step 4: Validate Vault authentication
            await self._validate_vault_authentication()

            # Step 5: Check Vault health
            await self._check_vault_health()

            # Step 6: Initialize secrets manager
            await self._initialize_secrets_manager()

            # Step 7: Validate critical secrets
            await self._validate_critical_secrets()

            # Step 8: Validate encryption keys
            await self._validate_encryption_keys()

            # Step 9: Test secret operations
            await self._test_secret_operations()

            # Step 10: Run production startup validation
            if self.is_production:
                await self._run_production_validation()

            logger.info("=" * 80)
            logger.info("✅ ALL VAULT INTEGRATION VALIDATIONS PASSED")
            logger.info("🔒 System is ready for secure operation")
            logger.info("=" * 80)

            return True

        except Exception as e:
            logger.critical("=" * 80)
            logger.critical("❌ VAULT INTEGRATION VALIDATION FAILED")
            logger.critical(f"❌ Error: {e}")
            logger.critical("❌ SYSTEM STARTUP ABORTED")
            logger.critical("=" * 80)

            if self.is_production:
                raise StartupValidationError(
                    f"Production startup validation failed: {e}"
                ) from e
            else:
                logger.warning("Non-production environment - continuing with warnings")
                return False

    async def _validate_environment_variables(self) -> None:
        """Validate required environment variables."""
        logger.info("🔍 Validating environment variables...")

        missing_vars = []
        invalid_vars = []

        for var_name in self.required_env_vars:
            value = os.getenv(var_name)

            if not value:
                missing_vars.append(var_name)
                continue

            # Validate VAULT_URL format
            if var_name == "VAULT_URL":
                if not (value.startswith("http://") or value.startswith("https://")):
                    invalid_vars.append(
                        f"{var_name}: Must start with http:// or https://"
                    )
                if "localhost" in value and self.is_production:
                    invalid_vars.append(
                        f"{var_name}: Localhost not allowed in production"
                    )

            # Validate VAULT_TOKEN format
            if var_name == "VAULT_TOKEN":
                if len(value) < 20:
                    invalid_vars.append(f"{var_name}: Token appears too short")
                if value in ["test-token", "dev-token", "changeme"]:
                    invalid_vars.append(f"{var_name}: Using default/test token")

        if missing_vars:
            raise StartupValidationError(
                f"Missing required environment variables: {missing_vars}"
            )

        if invalid_vars:
            raise StartupValidationError(
                f"Invalid environment variables: {invalid_vars}"
            )

        logger.info("✅ Environment variables validation passed")

    async def _initialize_vault_client(self) -> None:
        """Initialize the Vault client."""
        logger.info("🔧 Initializing Vault client...")

        try:
            self.vault_client = await get_vault_client_async()
            logger.info("✅ Vault client initialized successfully")

        except Exception as e:
            raise StartupValidationError(
                f"Failed to initialize Vault client: {e}"
            ) from e

    async def _test_vault_connectivity(self) -> None:
        """Test basic Vault connectivity."""
        logger.info("🌐 Testing Vault connectivity...")

        try:
            # Test basic connection
            health_status = await self.vault_client.health_check()

            if health_status["status"] != "healthy":
                raise StartupValidationError(f"Vault is not healthy: {health_status}")

            logger.info(f"✅ Vault connectivity test passed")
            logger.info(f"   Vault version: {health_status.get('version', 'unknown')}")
            logger.info(f"   Cluster: {health_status.get('cluster_name', 'unknown')}")

        except Exception as e:
            raise StartupValidationError(f"Vault connectivity test failed: {e}") from e

    async def _validate_vault_authentication(self) -> None:
        """Validate Vault authentication."""
        logger.info("🔐 Validating Vault authentication...")

        try:
            # The client should already be authenticated, but let's verify
            health_status = await self.vault_client.health_check()

            if not health_status.get("authenticated", False):
                raise StartupValidationError("Vault authentication failed")

            logger.info("✅ Vault authentication validated")

        except Exception as e:
            raise StartupValidationError(
                f"Vault authentication validation failed: {e}"
            ) from e

    async def _check_vault_health(self) -> None:
        """Perform detailed Vault health check."""
        logger.info("🏥 Performing Vault health check...")

        try:
            health_status = await self.vault_client.health_check()

            # Check critical health indicators
            if health_status.get("vault_sealed", True):
                raise StartupValidationError("Vault is sealed - cannot access secrets")

            if not health_status.get("vault_initialized", False):
                raise StartupValidationError("Vault is not initialized")

            logger.info("✅ Vault health check passed")
            logger.info(f"   Status: {health_status['status']}")
            logger.info(f"   Sealed: {health_status.get('vault_sealed', 'unknown')}")
            logger.info(
                f"   Initialized: {health_status.get('vault_initialized', 'unknown')}"
            )

        except Exception as e:
            raise StartupValidationError(f"Vault health check failed: {e}") from e

    async def _initialize_secrets_manager(self) -> None:
        """Initialize the production secrets manager."""
        logger.info("🔒 Initializing production secrets manager...")

        try:
            self.secrets_manager = ProductionVaultSecretsManager(self.vault_client)
            await self.secrets_manager.initialize()

            logger.info("✅ Production secrets manager initialized")

        except Exception as e:
            raise StartupValidationError(
                f"Secrets manager initialization failed: {e}"
            ) from e

    async def _validate_critical_secrets(self) -> None:
        """Validate that all critical secrets exist."""
        logger.info("🗝️ Validating critical secrets...")

        try:
            validation_results = await self.vault_client.validate_required_secrets(
                self.critical_secrets
            )

            missing_secrets = [
                secret for secret, exists in validation_results.items() if not exists
            ]

            if missing_secrets:
                raise StartupValidationError(
                    f"Critical secrets missing from Vault: {missing_secrets}. "
                    f"These must be provisioned by the security team."
                )

            logger.info(
                f"✅ All {len(self.critical_secrets)} critical secrets validated"
            )

            # Log which secrets were found (no values)
            for secret in self.critical_secrets:
                logger.info(f"   ✓ {secret}")

        except Exception as e:
            raise StartupValidationError(
                f"Critical secrets validation failed: {e}"
            ) from e

    async def _validate_encryption_keys(self) -> None:
        """Validate encryption keys and their properties."""
        logger.info("🔑 Validating encryption keys...")

        encryption_keys = [
            "master_encryption_key",
            "database_encryption_key",
            "child_data_encryption_key",
            "child_pii_encryption_key",
        ]

        try:
            for key_name in encryption_keys:
                try:
                    # Test key retrieval
                    key_bytes = await self.vault_client.get_encryption_key(key_name)

                    # Validate key length (should be 32 bytes for AES-256)
                    if len(key_bytes) < 32:
                        logger.warning(
                            f"Encryption key '{key_name}' is shorter than recommended (32 bytes)"
                        )

                    logger.info(f"   ✓ {key_name} ({len(key_bytes)} bytes)")

                except VaultSecretNotFoundError:
                    raise StartupValidationError(f"Encryption key missing: {key_name}")

            logger.info(f"✅ All {len(encryption_keys)} encryption keys validated")

        except Exception as e:
            raise StartupValidationError(
                f"Encryption keys validation failed: {e}"
            ) from e

    async def _test_secret_operations(self) -> None:
        """Test basic secret operations."""
        logger.info("🧪 Testing secret operations...")

        test_secret_name = f"_startup_test_{int(datetime.utcnow().timestamp())}"
        test_secret_value = f"test_value_{int(datetime.utcnow().timestamp())}"

        try:
            # Test secret storage
            await self.secrets_manager.set_secret(
                test_secret_name,
                test_secret_value,
                SecretType.TOKEN,
                tags={"test": "startup_validation"},
            )

            # Test secret retrieval
            retrieved_value = await self.secrets_manager.get_secret(test_secret_name)

            if retrieved_value != test_secret_value:
                raise StartupValidationError(
                    "Secret read/write test failed - values don't match"
                )

            # Test secret rotation
            new_test_value = f"rotated_{test_secret_value}"
            await self.secrets_manager.rotate_secret(test_secret_name, new_test_value)

            # Verify rotation
            rotated_value = await self.secrets_manager.get_secret(test_secret_name)
            if rotated_value != new_test_value:
                raise StartupValidationError("Secret rotation test failed")

            # Cleanup test secret
            await self.vault_client.delete_secret(test_secret_name)

            logger.info("✅ Secret operations test passed")
            logger.info("   ✓ Store secret")
            logger.info("   ✓ Retrieve secret")
            logger.info("   ✓ Rotate secret")
            logger.info("   ✓ Delete secret")

        except Exception as e:
            # Try to cleanup on failure
            try:
                await self.vault_client.delete_secret(test_secret_name)
            except:
                pass
            raise StartupValidationError(f"Secret operations test failed: {e}") from e

    async def _run_production_validation(self) -> None:
        """Run production-specific validation."""
        logger.info("🏭 Running production-specific validation...")

        try:
            # Use the production validation function
            validation_result = await validate_production_startup()

            if not validation_result:
                raise StartupValidationError("Production startup validation failed")

            logger.info("✅ Production validation passed")

        except Exception as e:
            raise StartupValidationError(f"Production validation failed: {e}") from e

    async def _validate_optional_secrets(self) -> None:
        """Validate optional secrets (warnings only)."""
        logger.info("📋 Checking optional secrets...")

        try:
            validation_results = await self.vault_client.validate_required_secrets(
                self.optional_secrets
            )

            missing_optional = [
                secret for secret, exists in validation_results.items() if not exists
            ]

            if missing_optional:
                logger.warning(
                    f"Optional secrets missing (functionality may be limited): {missing_optional}"
                )
            else:
                logger.info(
                    f"✅ All {len(self.optional_secrets)} optional secrets found"
                )

        except Exception as e:
            logger.warning(f"Optional secrets check failed: {e}")


async def main() -> int:
    """Main startup validation function.

    Returns:
        0 if validation passes, 1 if it fails
    """
    try:
        validator = VaultStartupValidator()
        success = await validator.run_full_validation()

        if success:
            print("\n🎉 VAULT INTEGRATION VALIDATION COMPLETED SUCCESSFULLY")
            print("🔐 System is ready for secure operation with HashiCorp Vault")
            return 0
        else:
            print("\n⚠️ VAULT INTEGRATION VALIDATION COMPLETED WITH WARNINGS")
            print("🔓 Some validations failed but system can continue (non-production)")
            return 0

    except StartupValidationError as e:
        print(f"\n💥 STARTUP VALIDATION FAILED: {e}")
        print("🚫 System startup aborted due to security requirements")
        return 1
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR DURING VALIDATION: {e}")
        print("🚫 System startup aborted")
        return 1


if __name__ == "__main__":
    # Run the validation
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
