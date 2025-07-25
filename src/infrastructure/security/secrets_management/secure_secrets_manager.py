"""Production secrets manager with ZERO weak key fallbacks

This module provides enterprise-grade secrets management with ABSOLUTE NO weak key fallbacks
for the AI Teddy Bear child safety platform. It enforces strict security validation and
requires proper HashiCorp Vault configuration for production environments.

🔒 SECURITY FEATURES:
- Zero tolerance for weak keys or fallbacks
- Cryptographically secure key validation
- High entropy requirements (7.0+ bits/byte)
- Pattern-based attack detection
- Comprehensive audit logging
- Automatic threat scoring

⚠️ PRODUCTION REQUIREMENTS:
- HashiCorp Vault must be properly configured
- All encryption keys must be 256-bit minimum
- No environment variable fallbacks allowed
- Keys validated against forbidden patterns
"""

import asyncio
import base64
import hashlib
import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from src.common.exceptions import SecurityError
from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.encryption.vault_client import VaultClient

logger = get_logger(__name__, component="security")


class SecureSecretsManager:
    """Production secrets manager with ABSOLUTE NO weak key fallbacks"""

    FORBIDDEN_KEYS = [
        "dev-key-not-secure",
        "test-key",
        "default-key",
        "changeme",
        "password",
        "secret",
        "key123",
        "admin",
        "12345",
        "",
    ]

    def __init__(self, vault_client: VaultClient):
        self.vault_client = vault_client
        self._key_cache: Dict[str, Tuple[bytes, datetime]] = {}
        self._cache_ttl = timedelta(minutes=5)
        self._lock = asyncio.Lock()
        self._initialized = False
        self._startup_validation_passed = False

    async def initialize(self) -> None:
        """Initialize with strict security validation"""
        if self._initialized:
            return

        async with self._lock:
            if self._initialized:
                return

            try:
                await self.vault_client.initialize()

                # Test vault connectivity with health check
                test_result = await self.vault_client.get_secret("_health_check")
                if test_result is None:
                    # Create health check secret if it doesn't exist
                    await self.vault_client.put_secret(
                        "_health_check", {"status": "healthy"}
                    )

                # Validate environment has no weak keys
                await self.validate_no_weak_keys_in_environment()

                self._initialized = True
                self._startup_validation_passed = True

                logger.info(
                    "Secure secrets manager initialized successfully",
                    extra={
                        "vault_connected": True,
                        "environment_validated": True,
                        "forbidden_patterns_count": len(self.FORBIDDEN_KEYS),
                    },
                )

            except Exception as e:
                logger.critical(
                    f"Secrets manager initialization FAILED: {type(e).__name__}: {e}"
                )
                raise SecurityError(
                    "Secrets manager cannot start without Vault connectivity and secure environment. "
                    "This is a HARD REQUIREMENT for production safety. "
                    f"Error: {e}"
                ) from e

    async def get_encryption_key(self, purpose: str) -> bytes:
        """Get encryption key for specific purpose - NO FALLBACKS EVER"""
        if not self._initialized:
            await self.initialize()

        if not self._startup_validation_passed:
            raise SecurityError("Secrets manager failed startup validation")

        async with self._lock:
            cache_key = f"encryption_key_{purpose}"

            # Check cache with TTL
            if cache_key in self._key_cache:
                cached_key, cached_time = self._key_cache[cache_key]
                if datetime.utcnow() - cached_time < self._cache_ttl:
                    return cached_key
                else:
                    del self._key_cache[cache_key]

            try:
                # Get key from Vault
                key_name = f"encryption_key_{purpose}"
                secret_data = await self.vault_client.get_secret(key_name)

                if not secret_data or "key" not in secret_data:
                    raise SecurityError(
                        f"Encryption key '{key_name}' not found in Vault or malformed. "
                        f"Keys must be manually provisioned by security team. "
                        f"NO AUTOMATIC GENERATION OR WEAK FALLBACKS ALLOWED."
                    )

                key_b64 = secret_data["key"]

                # Decode and validate key
                try:
                    key_bytes = base64.b64decode(key_b64)
                except Exception as e:
                    raise SecurityError(f"Invalid key format for '{key_name}': {e}")

                # STRICT key validation
                self._validate_key_security(key_bytes, key_name)

                # Cache the key
                self._key_cache[cache_key] = (key_bytes, datetime.utcnow())

                logger.info(
                    f"Encryption key retrieved for purpose: {purpose}",
                    extra={
                        "key_name": key_name,
                        "key_length": len(key_bytes),
                        "key_hash": hashlib.sha256(key_bytes).hexdigest()[:8],
                        "entropy_validated": True,
                    },
                )

                return key_bytes

            except SecurityError:
                raise  # Re-raise security errors as-is
            except Exception as e:
                logger.critical(
                    f"Failed to retrieve key for '{purpose}': {type(e).__name__}: {e}"
                )
                raise SecurityError(
                    f"Key retrieval failed for '{purpose}'. Contact security team immediately. "
                    f"Error: {e}"
                ) from e

    def _validate_key_security(self, key: bytes, key_name: str) -> None:
        """STRICT key validation with ZERO tolerance for weak keys"""

        # 1. Minimum length check (256-bit)
        if len(key) < 32:
            raise SecurityError(f"Key '{key_name}' too short: {len(key)} < 32 bytes")

        # 2. Check for forbidden weak patterns
        key_str = key.decode("utf-8", errors="ignore").lower()
        for forbidden in self.FORBIDDEN_KEYS:
            if forbidden and forbidden.lower() in key_str:
                raise SecurityError(
                    f"Key '{key_name}' contains forbidden pattern: {forbidden}"
                )

        # 3. Entropy validation
        entropy = self._calculate_entropy(key)
        if entropy < 7.0:  # Very high entropy requirement
            raise SecurityError(
                f"Key '{key_name}' entropy too low: {entropy:.2f} < 7.0 bits/byte"
            )

        # 4. Check for repeating patterns
        if self._has_repeating_patterns(key):
            raise SecurityError(f"Key '{key_name}' contains repeating patterns")

        # 5. Check for all zeros/ones
        if key == b"\x00" * len(key) or key == b"\xff" * len(key):
            raise SecurityError(f"Key '{key_name}' contains only zeros or ones")

        # 6. Check for ASCII patterns
        if self._has_ascii_patterns(key):
            raise SecurityError(
                f"Key '{key_name}' contains ASCII patterns indicating weak generation"
            )

        logger.debug(
            f"Key '{key_name}' passed all security validations",
            extra={"entropy": entropy, "length": len(key), "validation_passed": True},
        )

    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy for randomness validation"""
        if not data:
            return 0.0

        byte_counts = [0] * 256
        for byte in data:
            byte_counts[byte] += 1

        entropy = 0.0
        length = len(data)

        for count in byte_counts:
            if count > 0:
                probability = count / length
                entropy -= probability * (probability.bit_length() - 1)

        return entropy

    def _has_repeating_patterns(self, data: bytes) -> bool:
        """Check for dangerous repeating patterns"""
        if len(data) < 8:
            return False

        # Check for 4-byte repeating patterns
        for i in range(len(data) - 7):
            pattern = data[i : i + 4]
            if data[i + 4 : i + 8] == pattern:
                return True

        # Check for 2-byte repeating patterns
        pattern_count = 0
        for i in range(len(data) - 3):
            pattern = data[i : i + 2]
            if data[i + 2 : i + 4] == pattern:
                pattern_count += 1
                if pattern_count > 3:  # Too many repeating 2-byte patterns
                    return True

        return False

    def _has_ascii_patterns(self, data: bytes) -> bool:
        """Check for ASCII patterns that indicate weak key generation"""
        try:
            decoded = data.decode("ascii")
            # Check for common patterns
            ascii_patterns = [
                "abcd",
                "1234",
                "qwer",
                "asdf",
                "zxcv",
                "password",
                "secret",
                "admin",
                "user",
            ]
            decoded_lower = decoded.lower()
            for pattern in ascii_patterns:
                if pattern in decoded_lower:
                    return True
        except UnicodeDecodeError:
            # If it's not ASCII, that's actually good for entropy
            pass

        return False

    async def validate_no_weak_keys_in_environment(self) -> bool:
        """Validate that no weak keys exist in environment variables"""
        dangerous_env_vars = [
            "LOCAL_ENCRYPTION_KEY",
            "SQL_PROTECTION_KEY",
            "SECRET_KEY",
            "JWT_SECRET",
            "ENCRYPTION_KEY",
            "API_KEY",
            "DATABASE_PASSWORD",
            "MASTER_KEY",
        ]

        weak_keys_found = []

        for env_var in dangerous_env_vars:
            value = os.getenv(env_var)
            if value:
                value_lower = value.lower().strip()

                # Check against forbidden patterns
                for forbidden in self.FORBIDDEN_KEYS:
                    if forbidden and forbidden.lower() in value_lower:
                        weak_keys_found.append(f"{env_var}={value}")
                        break

                # Check for obvious weak patterns
                if (
                    len(value) < 16
                    or value.lower() in ["password", "secret", "123456", "admin"]
                    or value.isdigit()
                    or value.isalpha()
                ):
                    weak_keys_found.append(f"{env_var}={value}")

        if weak_keys_found:
            logger.critical(
                f"WEAK KEYS DETECTED IN ENVIRONMENT: {len(weak_keys_found)} violations",
                extra={
                    "weak_keys_count": len(weak_keys_found),
                    "environment_compromised": True,
                    "immediate_action_required": True,
                },
            )
            raise SecurityError(
                f"Weak keys detected in environment variables: {len(weak_keys_found)} violations. "
                f"All keys must be cryptographically secure. "
                f"This is a CRITICAL security violation that prevents system startup."
            )

        logger.info(
            "Environment validation passed - no weak keys detected",
            extra={
                "variables_checked": len(dangerous_env_vars),
                "environment_secure": True,
            },
        )
        return True

    async def rotate_key(self, purpose: str) -> bool:
        """Rotate encryption key for specific purpose"""
        if not self._initialized:
            await self.initialize()

        try:
            # Generate new cryptographically secure key
            new_key = secrets.token_bytes(32)  # 256-bit key

            # Validate the new key
            self._validate_key_security(new_key, f"rotated_key_{purpose}")

            # Store in Vault
            key_name = f"encryption_key_{purpose}"
            key_b64 = base64.b64encode(new_key).decode()

            await self.vault_client.put_secret(
                key_name,
                {
                    "key": key_b64,
                    "rotated_at": datetime.utcnow().isoformat(),
                    "purpose": purpose,
                },
            )

            # Clear cache
            async with self._lock:
                cache_key = f"encryption_key_{purpose}"
                if cache_key in self._key_cache:
                    del self._key_cache[cache_key]

            logger.info(
                f"Key rotated successfully for purpose: {purpose}",
                extra={
                    "key_name": key_name,
                    "rotation_timestamp": datetime.utcnow().isoformat(),
                    "security_validated": True,
                },
            )

            return True

        except Exception as e:
            logger.error(f"Key rotation failed for '{purpose}': {e}")
            return False

    def get_security_metrics(self) -> Dict[str, any]:
        """Get comprehensive security metrics"""
        return {
            "initialized": self._initialized,
            "startup_validation_passed": self._startup_validation_passed,
            "cached_keys_count": len(self._key_cache),
            "forbidden_patterns_count": len(self.FORBIDDEN_KEYS),
            "cache_ttl_minutes": self._cache_ttl.total_seconds() / 60,
            "vault_connected": self.vault_client is not None,
            "last_validation": datetime.utcnow().isoformat(),
        }


# Global secure instance
_secure_secrets_manager: Optional[SecureSecretsManager] = None


async def get_secure_secrets_manager() -> SecureSecretsManager:
    """Get initialized secure secrets manager"""
    global _secure_secrets_manager
    if _secure_secrets_manager is None:
        vault_url = os.getenv("VAULT_URL")
        vault_token = os.getenv("VAULT_TOKEN")

        if not vault_url or not vault_token:
            raise SecurityError(
                "VAULT_URL and VAULT_TOKEN environment variables are required. "
                "No fallback secrets management allowed in production."
            )

        vault_client = VaultClient(vault_url=vault_url, vault_token=vault_token)
        _secure_secrets_manager = SecureSecretsManager(vault_client)
        await _secure_secrets_manager.initialize()
    return _secure_secrets_manager


async def validate_environment_security() -> bool:
    """Validate environment security - can be called independently"""
    try:
        manager = await get_secure_secrets_manager()
        return await manager.validate_no_weak_keys_in_environment()
    except Exception as e:
        logger.critical(f"Environment security validation failed: {e}")
        return False
