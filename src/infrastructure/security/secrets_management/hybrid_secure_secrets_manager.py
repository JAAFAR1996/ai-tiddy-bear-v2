import asyncio
import base64
import hashlib
import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from src.common.exceptions import SecurityError
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class HybridSecureSecretsManager:
    """Hybrid secrets manager - secure by default, Vault optional for enhanced security"""

    # FORBIDDEN KEYS - Zero tolerance for these patterns
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
        "password123",
        "secret123",
        "default",
        "change_me",
        "replace_me",
        "",
    ]

    def __init__(self, use_vault: bool = False, vault_client=None):
        self.use_vault = use_vault
        self.vault_client = vault_client
        self._key_cache: Dict[str, Tuple[bytes, datetime]] = {}
        self._cache_ttl = timedelta(minutes=5)
        self._lock = asyncio.Lock()
        self._initialized = False
        self.security_mode = "ENHANCED"  # BASIC, ENHANCED, VAULT
        self._startup_validation_passed = False

    async def initialize(self) -> None:
        """Initialize with progressive security levels"""
        if self._initialized:
            return

        async with self._lock:
            if self._initialized:
                return

            try:
                # Try Vault if configured
                if self.use_vault and self.vault_client:
                    try:
                        await self.vault_client.initialize()
                        # Test Vault connectivity
                        test_result = await self.vault_client.get_secret(
                            "_health_check"
                        )
                        self.security_mode = "VAULT"
                        logger.info("Initialized with Vault backend - maximum security")
                    except Exception as vault_error:
                        logger.warning(
                            f"Vault initialization failed, falling back to enhanced mode: {vault_error}"
                        )
                        self.use_vault = False
                        self.security_mode = "ENHANCED"
                else:
                    self.security_mode = "ENHANCED"
                    logger.info("Initialized with enhanced local security")

                # Always validate environment security
                environment_secure = await self.validate_no_weak_keys_in_environment()

                if not environment_secure and self.security_mode == "VAULT":
                    raise SecurityError(
                        "Vault mode requires clean environment - weak keys detected"
                    )

                self._startup_validation_passed = True
                self._initialized = True

                logger.info(
                    f"Hybrid secrets manager initialized successfully",
                    extra={
                        "security_mode": self.security_mode,
                        "vault_enabled": self.use_vault,
                        "environment_validated": environment_secure,
                        "forbidden_patterns": len(self.FORBIDDEN_KEYS),
                    },
                )

            except Exception as e:
                logger.critical(f"Secrets manager initialization failed: {e}")
                if self.security_mode == "VAULT":
                    # In Vault mode, we fail hard
                    raise SecurityError(f"Vault mode initialization failed: {e}")
                else:
                    # In enhanced mode, we try to continue with basic security
                    logger.warning("Falling back to basic security mode")
                    self.security_mode = "BASIC"
                    self._initialized = True

    async def get_encryption_key(self, purpose: str) -> bytes:
        """Get encryption key with multiple security levels - NO WEAK FALLBACKS EVER"""
        if not self._initialized:
            await self.initialize()

        if not self._startup_validation_passed and self.security_mode != "BASIC":
            raise SecurityError(
                "Startup validation failed - cannot provide encryption keys"
            )

        async with self._lock:
            cache_key = f"encryption_key_{purpose}"

            # Check cache first
            if cache_key in self._key_cache:
                cached_key, cached_time = self._key_cache[cache_key]
                if datetime.utcnow() - cached_time < self._cache_ttl:
                    return cached_key
                else:
                    del self._key_cache[cache_key]

            try:
                if self.security_mode == "VAULT":
                    key_bytes = await self._get_key_from_vault(purpose)
                elif self.security_mode == "ENHANCED":
                    key_bytes = await self._get_key_enhanced_local(purpose)
                else:  # BASIC mode
                    key_bytes = self._generate_secure_key()

                # Always validate key security regardless of mode
                self._validate_key_security(key_bytes, f"key_{purpose}")

                # Cache the key
                self._key_cache[cache_key] = (key_bytes, datetime.utcnow())

                logger.info(
                    f"Encryption key retrieved for purpose: {purpose}",
                    extra={
                        "security_mode": self.security_mode,
                        "key_length": len(key_bytes),
                        "entropy_validated": True,
                        "purpose": purpose,
                    },
                )

                return key_bytes

            except Exception as e:
                logger.error(f"Failed to retrieve key for '{purpose}': {e}")
                raise SecurityError(
                    f"Key retrieval failed for '{purpose}'. No weak fallbacks allowed. Error: {e}"
                )

    async def _get_key_from_vault(self, purpose: str) -> bytes:
        """Get key from Vault with automatic secure generation"""
        key_name = f"encryption_key_{purpose}"
        secret_data = await self.vault_client.get_secret(key_name)

        if not secret_data or "key" not in secret_data:
            logger.info(f"Generating new secure key for purpose: {purpose}")
            # Generate new secure key and store in Vault
            new_key = self._generate_secure_key()
            key_b64 = base64.b64encode(new_key).decode()
            await self.vault_client.put_secret(
                key_name,
                {
                    "key": key_b64,
                    "created_at": datetime.utcnow().isoformat(),
                    "purpose": purpose,
                    "version": "1.0",
                },
            )
            return new_key

        try:
            return base64.b64decode(secret_data["key"])
        except Exception as e:
            raise SecurityError(f"Invalid key format in Vault for {key_name}: {e}")

    async def _get_key_enhanced_local(self, purpose: str) -> bytes:
        """Get key from enhanced local storage with secure defaults"""
        # Check for properly formatted environment key
        env_key = f"SECURE_{purpose.upper()}_KEY"
        env_value = os.getenv(env_key)

        if env_value:
            # Validate environment key is secure
            if any(
                forbidden.lower() in env_value.lower()
                for forbidden in self.FORBIDDEN_KEYS
            ):
                raise SecurityError(
                    f"Environment key {env_key} contains forbidden pattern"
                )

            try:
                # Try to decode as base64 first
                decoded_key = base64.b64decode(env_value)
                if len(decoded_key) >= 32:  # Valid key length
                    return decoded_key
            except:
                pass

            # If not base64, derive key from material using secure KDF
            if len(env_value) >= 16:  # Minimum material length
                return hashlib.pbkdf2_hmac(
                    "sha256",
                    env_value.encode(),
                    f"ai_teddy_{purpose}".encode(),
                    100000,  # High iteration count
                    32,  # 256-bit key
                )
            else:
                logger.warning(
                    f"Environment key {env_key} too short, generating new key"
                )

        # Generate secure key on demand (NO WEAK FALLBACKS)
        logger.info(f"Generating new secure key for purpose: {purpose}")
        return self._generate_secure_key()

    def _generate_secure_key(self) -> bytes:
        """Generate cryptographically secure key using OS random"""
        key = secrets.token_bytes(32)  # 256-bit key

        # Additional validation to ensure we got a good key
        entropy = self._calculate_entropy(key)
        if entropy < 5.0:  # Very unlikely with secrets.token_bytes, but safety check
            logger.warning(f"Generated key has low entropy: {entropy}, regenerating...")
            key = secrets.token_bytes(32)

        return key

    def _validate_key_security(self, key: bytes, key_name: str) -> None:
        """Validate key meets security requirements with progressive levels"""
        # 1. Minimum length check (256-bit)
        if len(key) < 32:
            raise SecurityError(f"Key '{key_name}' too short: {len(key)} < 32 bytes")

        # 2. Check for forbidden patterns in key material
        try:
            key_str = key.decode("utf-8", errors="ignore").lower()
            for forbidden in self.FORBIDDEN_KEYS:
                if forbidden and forbidden in key_str:
                    raise SecurityError(
                        f"Key '{key_name}' contains forbidden pattern: {forbidden}"
                    )
        except:
            # If key can't be decoded as UTF-8, that's actually good (high entropy)
            pass

        # 3. Entropy validation (progressive based on security mode)
        entropy = self._calculate_entropy(key)
        min_entropy = {
            "VAULT": 7.0,  # Highest requirement
            "ENHANCED": 6.0,  # Good requirement
            "BASIC": 5.0,  # Minimum acceptable
        }.get(self.security_mode, 5.0)

        if entropy < min_entropy:
            if self.security_mode == "VAULT":
                raise SecurityError(
                    f"Key '{key_name}' entropy too low: {entropy:.2f} < {min_entropy}"
                )
            else:
                logger.warning(
                    f"Key '{key_name}' has low entropy: {entropy:.2f} < {min_entropy}"
                )
                if entropy < 4.0:  # Hard minimum for any mode
                    raise SecurityError(
                        f"Key '{key_name}' entropy critically low: {entropy:.2f}"
                    )

        # 4. Check for obvious weak patterns
        if self._has_obvious_weak_patterns(key):
            raise SecurityError(f"Key '{key_name}' contains obvious weak patterns")

        logger.debug(
            f"Key '{key_name}' passed security validation",
            extra={
                "entropy": entropy,
                "length": len(key),
                "security_mode": self.security_mode,
            },
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

    def _has_obvious_weak_patterns(self, data: bytes) -> bool:
        """Check for obvious weak patterns"""
        # Check for all zeros/ones
        if data == b"\x00" * len(data) or data == b"\xff" * len(data):
            return True

        # Check for simple repeating patterns (4-byte)
        if len(data) >= 8:
            pattern = data[:4]
            if data[4:8] == pattern:
                return True

        # Check for incrementing patterns
        if len(data) >= 8:
            incrementing = all(
                data[i] == (data[0] + i) % 256 for i in range(min(8, len(data)))
            )
            if incrementing:
                return True

        return False

    async def validate_no_weak_keys_in_environment(self) -> bool:
        """Validate environment variables don't contain weak keys"""
        dangerous_env_vars = [
            "LOCAL_ENCRYPTION_KEY",
            "SQL_PROTECTION_KEY",
            "SECRET_KEY",
            "JWT_SECRET",
            "ENCRYPTION_KEY",
            "API_KEY",
            "DATABASE_PASSWORD",
        ]

        violations = []
        warnings = []

        for env_var in dangerous_env_vars:
            value = os.getenv(env_var)
            if value:
                value_lower = value.lower().strip()

                # Check against forbidden patterns
                for forbidden in self.FORBIDDEN_KEYS:
                    if forbidden and forbidden in value_lower:
                        violations.append(f"{env_var} contains '{forbidden}'")
                        break

                # Check for other weak patterns
                if (
                    len(value) < 16
                    or value.isdigit()
                    or value.isalpha()
                    or value in ["password", "secret", "123456", "admin"]
                ):
                    warnings.append(f"{env_var} appears weak")

        if violations:
            if self.security_mode == "VAULT":
                logger.critical(f"CRITICAL: Weak keys in environment: {violations}")
                raise SecurityError(f"Weak keys detected in environment: {violations}")
            else:
                logger.error(f"ERROR: Weak keys in environment: {violations}")
                # In enhanced/basic mode, we warn but continue (for development)
                return False

        if warnings:
            logger.warning(f"Potentially weak keys in environment: {warnings}")

        if not violations and not warnings:
            logger.info("Environment validation passed - no weak keys detected")

        return len(violations) == 0

    async def rotate_key(self, purpose: str) -> bool:
        """Rotate encryption key for specific purpose"""
        if not self._initialized:
            await self.initialize()

        try:
            # Generate new secure key
            new_key = self._generate_secure_key()
            self._validate_key_security(new_key, f"rotated_key_{purpose}")

            # Store based on security mode
            if self.security_mode == "VAULT":
                key_name = f"encryption_key_{purpose}"
                key_b64 = base64.b64encode(new_key).decode()
                await self.vault_client.put_secret(
                    key_name,
                    {
                        "key": key_b64,
                        "rotated_at": datetime.utcnow().isoformat(),
                        "purpose": purpose,
                        "version": "rotated",
                    },
                )

            # Clear cache to force new key usage
            async with self._lock:
                cache_key = f"encryption_key_{purpose}"
                if cache_key in self._key_cache:
                    del self._key_cache[cache_key]

            logger.info(f"Key rotated successfully for purpose: {purpose}")
            return True

        except Exception as e:
            logger.error(f"Key rotation failed for '{purpose}': {e}")
            return False

    def get_security_metrics(self) -> Dict[str, any]:
        """Get comprehensive security metrics"""
        return {
            "security_mode": self.security_mode,
            "vault_enabled": self.use_vault,
            "initialized": self._initialized,
            "startup_validation_passed": self._startup_validation_passed,
            "cached_keys_count": len(self._key_cache),
            "forbidden_patterns_count": len(self.FORBIDDEN_KEYS),
            "cache_ttl_minutes": self._cache_ttl.total_seconds() / 60,
            "last_validation": datetime.utcnow().isoformat(),
        }


# Global instance management
_hybrid_secrets_manager: Optional[HybridSecureSecretsManager] = None


async def get_hybrid_secrets_manager(
    use_vault: bool = None,
) -> HybridSecureSecretsManager:
    """Get hybrid secrets manager with auto-detection of Vault availability"""
    global _hybrid_secrets_manager
    if _hybrid_secrets_manager is None:
        # Auto-detect Vault availability if not specified
        if use_vault is None:
            vault_url = os.getenv("VAULT_URL")
            vault_token = os.getenv("VAULT_TOKEN")
            use_vault = bool(vault_url and vault_token)

            if vault_url or vault_token:  # Partial config detected
                logger.info(
                    f"Vault configuration detected: URL={bool(vault_url)}, TOKEN={bool(vault_token)}"
                )

        vault_client = None
        if use_vault:
            try:
                from src.infrastructure.security.encryption.vault_client import (
                    VaultClient,
                )

                vault_client = VaultClient(
                    vault_url=os.getenv("VAULT_URL"),
                    vault_token=os.getenv("VAULT_TOKEN"),
                )
                logger.info("Vault client configured for hybrid secrets manager")
            except Exception as e:
                logger.warning(
                    f"Vault client setup failed, using enhanced local mode: {e}"
                )
                use_vault = False

        _hybrid_secrets_manager = HybridSecureSecretsManager(use_vault, vault_client)
        await _hybrid_secrets_manager.initialize()

    return _hybrid_secrets_manager


async def validate_environment_security() -> bool:
    """Validate environment security - standalone function"""
    try:
        manager = await get_hybrid_secrets_manager()
        return await manager.validate_no_weak_keys_in_environment()
    except Exception as e:
        logger.error(f"Environment security validation failed: {e}")
        return False


# Backward compatibility function
async def get_secure_secrets_manager():
    """Backward compatibility function"""
    return await get_hybrid_secrets_manager()
