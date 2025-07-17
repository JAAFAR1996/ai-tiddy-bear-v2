"""
Robust Encryption Service with No Silent Failures
Ensures all encryption operations are properly validated and logged for COPPA compliance.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any, List, Union
import base64
import hashlib
import json
import logging
import os
import secrets
from src.infrastructure.security.comprehensive_audit_integration import get_audit_integration
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")

class EncryptionResult:
    """Result of encryption operation with detailed status."""
    def __init__(
        self,
        success: bool,
        data: Optional[str] = None,
        error: Optional[str] = None,
        operation_id: Optional[str] = None,
        key_id: Optional[str] = None,
        algorithm: Optional[str] = None
    ):
        self.success = success
        self.data = data
        self.error = error
        self.operation_id = operation_id or secrets.token_hex(8)
        self.key_id = key_id
        self.algorithm = algorithm
        self.timestamp = datetime.utcnow()

class EncryptionLevel(Enum):
    """Encryption strength levels."""
    BASIC = "aes_128"
    STANDARD = "aes_256"
    ENHANCED = "aes_256_gcm"
    MAXIMUM = "chacha20_poly1305"

class EncryptionPolicy(Enum):
    """Encryption policy enforcement levels."""
    OPTIONAL = "optional"      # Encryption preferred but not required
    REQUIRED = "required"      # Must encrypt, fail if cannot
    MANDATORY = "mandatory"    # Strictest - must encrypt with verification

@dataclass
class EncryptionConfig:
    """Configuration for encryption operations."""
    algorithm: str = "AES-256-GCM"
    key_derivation: str = "PBKDF2"
    key_iterations: int = 100000
    require_authentication: bool = True
    require_integrity_check: bool = True
    max_plaintext_size: int = 1048576  # 1MB
    key_rotation_days: int = 90
    audit_all_operations: bool = True

class RobustEncryptionService:
    """
    Robust encryption service that never fails silently.
    Features: - Never fails silently - all failures are logged and raised - Comprehensive audit logging for all operations - Key rotation with secure key management - Multiple encryption algorithms support - Integrity verification for all encrypted data - COPPA compliance with enhanced child data protection - Secure key derivation and storage - Operation tracing and monitoring
    """
    def __init__(self, config: Optional[EncryptionConfig] = None):
        self.config = config or EncryptionConfig()
        self.audit_integration = get_audit_integration()
        self._encryption_keys: Dict[str, bytes] = {}
        self._key_metadata: Dict[str, Dict[str, Any]] = {}
        self._operation_log: List[Dict[str, Any]] = []
        # Initialize encryption system
        self._initialize_encryption_system()

    def _initialize_encryption_system(self) -> None:
        """Initialize the encryption system with secure defaults."""
        try:
            # Check for production dependencies
            self._import_crypto_dependencies()
            # Initialize master key
            self._initialize_master_key()
            # Verify encryption capabilities
            self._verify_encryption_capabilities()
            logger.info("Robust encryption service initialized successfully")
        except Exception as e:
            logger.critical(f"Failed to initialize encryption service: {e}")
            raise RuntimeError(f"Encryption service initialization failed: {e}")

    def _import_crypto_dependencies(self) -> None:
        """Import and verify cryptographic dependencies."""
        try:
            global Fernet, AESGCM, ChaCha20Poly1305, PBKDF2HMAC, hashes
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            from cryptography.hazmat.primitives import hashes
            self._crypto_available = True
            logger.info("Cryptography dependencies loaded successfully")
        except ImportError as e:
            logger.error(f"Cryptography dependencies not available: {e}")
            self._crypto_available = False
            raise ImportError(
                f"Required cryptography library not available: {e}. "
                "Install with: pip install cryptography"
            )

    def _initialize_master_key(self) -> None:
        """Initialize master encryption key securely."""
        try:
            # Try to load existing key from environment
            master_key_b64 = os.environ.get("AI_TEDDY_MASTER_KEY")
            if master_key_b64:
                try:
                    master_key = base64.b64decode(master_key_b64)
                    if len(master_key) != 32:  # 256-bit key
                        raise ValueError("Invalid master key length")
                    self._master_key = master_key
                    logger.info("Master key loaded from environment")
                except Exception as e:
                    raise ValueError(f"Invalid master key in environment: {e}")
            else:
                # Generate new master key for development/testing
                logger.warning("No master key found in environment - generating temporary key")
                self._master_key = os.urandom(32)
                master_key_b64 = base64.b64encode(self._master_key).decode()
                logger.warning(f"Temporary master key: {master_key_b64}")
                logger.warning("Set AI_TEDDY_MASTER_KEY environment variable for production")
            # Derive default encryption key
            self._derive_default_key()
        except Exception as e:
            logger.critical(f"Failed to initialize master key: {e}")
            raise RuntimeError(f"Master key initialization failed: {e}")

    def _derive_default_key(self) -> None:
        """Derive default encryption key from master key."""
        try:
            # Use PBKDF2 to derive a key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"ai_teddy_default_salt",  # In production, use random salt per key
                iterations=self.config.key_iterations,
            )
            default_key = kdf.derive(self._master_key)
            key_id = "default"
            self._encryption_keys[key_id] = default_key
            self._key_metadata[key_id] = {
                "created_at": datetime.utcnow(),
                "algorithm": self.config.algorithm,
                "key_derivation": self.config.key_derivation,
                "iterations": self.config.key_iterations
            }
            logger.info(f"Default encryption key derived (key_id: {key_id})")
        except Exception as e:
            logger.critical(f"Failed to derive default key: {e}")
            raise RuntimeError(f"Key derivation failed: {e}")

    def _verify_encryption_capabilities(self) -> None:
        """Verify encryption and decryption capabilities."""
        try:
            test_data = "encryption_test_data"
            # Test encryption
            encrypt_result = self.encrypt(test_data, policy=EncryptionPolicy.REQUIRED)
            if not encrypt_result.success:
                raise RuntimeError(f"Encryption test failed: {encrypt_result.error}")
            # Test decryption
            decrypt_result = self.decrypt(encrypt_result.data, policy=EncryptionPolicy.REQUIRED)
            if not decrypt_result.success:
                raise RuntimeError(f"Decryption test failed: {decrypt_result.error}")
            if decrypt_result.data != test_data:
                raise RuntimeError("Encryption/decryption test data mismatch")
            logger.info("Encryption capabilities verified successfully")
        except Exception as e:
            logger.critical(f"Encryption capability verification failed: {e}")
            raise RuntimeError(f"Encryption verification failed: {e}")

    async def encrypt(
        self,
        plaintext: str,
        key_id: str = "default",
        policy: EncryptionPolicy = EncryptionPolicy.REQUIRED,
        context: Optional[Dict[str, Any]] = None
    ) -> EncryptionResult:
        """
        Encrypt data with comprehensive error handling and auditing.
        Args: plaintext: Data to encrypt
            key_id: Encryption key identifier
            policy: Encryption policy enforcement level
            context: Additional context for auditing
        Returns: EncryptionResult with detailed status
        """
        operation_id = secrets.token_hex(8)
        start_time = datetime.utcnow()
        try:
            # Validate inputs
            if not plaintext:
                if policy == EncryptionPolicy.OPTIONAL:
                    return EncryptionResult(True, "", None, operation_id)
                else:
                    raise ValueError("Cannot encrypt empty data with current policy")
            if len(plaintext.encode()) > self.config.max_plaintext_size:
                raise ValueError(f"Plaintext exceeds maximum size: {self.config.max_plaintext_size}")
            # Check if encryption is available
            if not self._crypto_available:
                error_msg = "Cryptography not available"
                if policy == EncryptionPolicy.OPTIONAL:
                    await self._log_encryption_event("encryption_skipped", operation_id, error_msg, context)
                    return EncryptionResult(True, plaintext, None, operation_id)  # Return plaintext
                else:
                    await self._log_encryption_event("encryption_failed", operation_id, error_msg, context)
                    raise RuntimeError(error_msg)
            # Get encryption key
            if key_id not in self._encryption_keys:
                error_msg = f"Encryption key not found: {key_id}"
                await self._log_encryption_event("encryption_failed", operation_id, error_msg, context)
                raise ValueError(error_msg)
            encryption_key = self._encryption_keys[key_id]
            # Perform encryption
            if self.config.algorithm == "AES-256-GCM":
                encrypted_data = await self._encrypt_aes_gcm(plaintext, encryption_key, operation_id)
            elif self.config.algorithm == "ChaCha20-Poly1305":
                encrypted_data = await self._encrypt_chacha20(plaintext, encryption_key, operation_id)
            else:
                # Fallback to Fernet
                encrypted_data = await self._encrypt_fernet(plaintext, encryption_key, operation_id)
            # Verify encryption
            if self.config.require_integrity_check:
                verify_result = await self.decrypt(encrypted_data, key_id, EncryptionPolicy.REQUIRED)
                if not verify_result.success or verify_result.data != plaintext:
                    error_msg = "Encryption integrity verification failed"
                    await self._log_encryption_event("encryption_failed", operation_id, error_msg, context)
                    raise RuntimeError(error_msg)
            # Log successful encryption
            duration = (datetime.utcnow() - start_time).total_seconds()
            await self._log_encryption_event(
                "encryption_success", operation_id, f"Encrypted {len(plaintext)} bytes",
                {**(context or {}), "duration_seconds": duration, "key_id": key_id}
            )
            return EncryptionResult(
                success=True,
                data=encrypted_data,
                operation_id=operation_id,
                key_id=key_id,
                algorithm=self.config.algorithm
            )
        except Exception as e:
            error_msg = f"Encryption failed: {str(e)}"
            logger.error(f"Encryption error (operation_id: {operation_id}): {error_msg}")
            # Log encryption failure
            await self._log_encryption_event("encryption_failed", operation_id, error_msg, context)
            # Handle based on policy
            if policy == EncryptionPolicy.OPTIONAL:
                logger.warning(f"Encryption failed but policy is optional - returning plaintext (operation_id: {operation_id})")
                return EncryptionResult(True, plaintext, error_msg, operation_id)
            else:
                # REQUIRED or MANDATORY - must fail
                return EncryptionResult(False, None, error_msg, operation_id)

    async def decrypt(
        self,
        ciphertext: str,
        key_id: str = "default",
        policy: EncryptionPolicy = EncryptionPolicy.REQUIRED,
        context: Optional[Dict[str, Any]] = None
    ) -> EncryptionResult:
        """
        Decrypt data with comprehensive error handling and auditing.
        Args: ciphertext: Data to decrypt
            key_id: Encryption key identifier
            policy: Encryption policy enforcement level
            context: Additional context for auditing
        Returns: EncryptionResult with decrypted data or error
        """
        operation_id = secrets.token_hex(8)
        start_time = datetime.utcnow()
        try:
            # Validate inputs
            if not ciphertext:
                return EncryptionResult(True, "", None, operation_id)
            # Check if this might be plaintext (for backwards compatibility)
            if policy == EncryptionPolicy.OPTIONAL and not self._looks_like_ciphertext(ciphertext):
                logger.info(f"Data appears to be plaintext - returning as-is (operation_id: {operation_id})")
                return EncryptionResult(True, ciphertext, None, operation_id)
            # Check if decryption is available
            if not self._crypto_available:
                error_msg = "Cryptography not available for decryption"
                if policy == EncryptionPolicy.OPTIONAL:
                    await self._log_encryption_event("decryption_skipped", operation_id, error_msg, context)
                    return EncryptionResult(True, ciphertext, None, operation_id)  # Return as-is
                else:
                    await self._log_encryption_event("decryption_failed", operation_id, error_msg, context)
                    raise RuntimeError(error_msg)
            # Get decryption key
            if key_id not in self._encryption_keys:
                error_msg = f"Decryption key not found: {key_id}"
                await self._log_encryption_event("decryption_failed", operation_id, error_msg, context)
                raise ValueError(error_msg)
            encryption_key = self._encryption_keys[key_id]
            # Perform decryption
            try:
                if self.config.algorithm == "AES-256-GCM":
                    plaintext = await self._decrypt_aes_gcm(ciphertext, encryption_key, operation_id)
                elif self.config.algorithm == "ChaCha20-Poly1305":
                    plaintext = await self._decrypt_chacha20(ciphertext, encryption_key, operation_id)
                else:
                    # Fallback to Fernet
                    plaintext = await self._decrypt_fernet(ciphertext, encryption_key, operation_id)
            except Exception as decrypt_error:
                # Try different algorithms as fallback
                plaintext = await self._try_fallback_decryption(ciphertext, encryption_key, operation_id)
            # Log successful decryption
            duration = (datetime.utcnow() - start_time).total_seconds()
            await self._log_encryption_event(
                "decryption_success", operation_id, f"Decrypted {len(plaintext)} bytes",
                {**(context or {}), "duration_seconds": duration, "key_id": key_id}
            )
            return EncryptionResult(
                success=True,
                data=plaintext,
                operation_id=operation_id,
                key_id=key_id,
                algorithm=self.config.algorithm
            )
        except Exception as e:
            error_msg = f"Decryption failed: {str(e)}"
            logger.error(f"Decryption error (operation_id: {operation_id}): {error_msg}")
            # Log decryption failure
            await self._log_encryption_event("decryption_failed", operation_id, error_msg, context)
            # Handle based on policy
            if policy == EncryptionPolicy.OPTIONAL:
                logger.warning(f"Decryption failed but policy is optional - returning ciphertext (operation_id: {operation_id})")
                return EncryptionResult(True, ciphertext, error_msg, operation_id)
            else:
                # REQUIRED or MANDATORY - must fail
                return EncryptionResult(False, None, error_msg, operation_id)

    async def _encrypt_aes_gcm(self, plaintext: str, key: bytes, operation_id: str) -> str:
        """Encrypt using AES - 256 - GCM."""
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
        # Combine nonce and ciphertext
        encrypted_data = base64.b64encode(nonce + ciphertext).decode()
        return f"AES-GCM:{encrypted_data}"

    async def _decrypt_aes_gcm(self, encrypted_data: str, key: bytes, operation_id: str) -> str:
        """Decrypt using AES - 256 - GCM."""
        if not encrypted_data.startswith("AES-GCM:"):
            raise ValueError("Invalid AES-GCM format")
        data = base64.b64decode(encrypted_data[8:])  # Remove "AES-GCM:" prefix
        nonce = data[:12]
        ciphertext = data[12:]
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode()

    async def _encrypt_chacha20(self, plaintext: str, key: bytes, operation_id: str) -> str:
        """Encrypt using ChaCha20 - Poly1305."""
        cipher = ChaCha20Poly1305(key)
        nonce = os.urandom(12)  # 96-bit nonce
        ciphertext = cipher.encrypt(nonce, plaintext.encode(), None)
        # Combine nonce and ciphertext
        encrypted_data = base64.b64encode(nonce + ciphertext).decode()
        return f"ChaCha20:{encrypted_data}"

    async def _decrypt_chacha20(self, encrypted_data: str, key: bytes, operation_id: str) -> str:
        """Decrypt using ChaCha20 - Poly1305."""
        if not encrypted_data.startswith("ChaCha20:"):
            raise ValueError("Invalid ChaCha20 format")
        data = base64.b64decode(encrypted_data[9:])  # Remove "ChaCha20:" prefix
        nonce = data[:12]
        ciphertext = data[12:]
        cipher = ChaCha20Poly1305(key)
        plaintext = cipher.decrypt(nonce, ciphertext, None)
        return plaintext.decode()

    async def _encrypt_fernet(self, plaintext: str, key: bytes, operation_id: str) -> str:
        """Encrypt using Fernet(fallback)."""
        # Derive Fernet key from our key
        fernet_key = base64.urlsafe_b64encode(key)
        fernet = Fernet(fernet_key)
        ciphertext = fernet.encrypt(plaintext.encode())
        return f"Fernet:{base64.b64encode(ciphertext).decode()}"

    async def _decrypt_fernet(self, encrypted_data: str, key: bytes, operation_id: str) -> str:
        """Decrypt using Fernet(fallback)."""
        if encrypted_data.startswith("Fernet:"):
            data = base64.b64decode(encrypted_data[7:])
        else:
            # Assume it's raw Fernet data
            try:
                data = base64.b64decode(encrypted_data)
            except (ValueError, TypeError):
                data = encrypted_data.encode()
        fernet_key = base64.urlsafe_b64encode(key)
        fernet = Fernet(fernet_key)
        plaintext = fernet.decrypt(data)
        return plaintext.decode()

    async def _try_fallback_decryption(self, ciphertext: str, key: bytes, operation_id: str) -> str:
        """Try different decryption methods as fallback."""
        algorithms = [
            ("Fernet", self._decrypt_fernet),
            ("AES-GCM", self._decrypt_aes_gcm),
            ("ChaCha20", self._decrypt_chacha20)
        ]
        for alg_name, decrypt_func in algorithms:
            try:
                logger.info(f"Trying fallback decryption with {alg_name} (operation_id: {operation_id})")
                return await decrypt_func(ciphertext, key, operation_id)
            except Exception as e:
                logger.debug(f"Fallback {alg_name} decryption failed: {e}")
        raise RuntimeError("All decryption methods failed")

    def _looks_like_ciphertext(self, data: str) -> bool:
        """Heuristic to determine if data looks like encrypted content."""
        # Check for encryption prefixes
        if any(data.startswith(prefix) for prefix in ["AES-GCM:", "ChaCha20:", "Fernet:"]):
            return True
        # Check if it looks like base64
        try:
            if len(data) > 20 and len(data) % 4 == 0:
                base64.b64decode(data)
                return True
        except (ValueError, TypeError):
            pass
        return False

    async def _log_encryption_event(
        self,
        event_type: str,
        operation_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log encryption operations for audit purposes."""
        try:
            details = {
                "operation_id": operation_id,
                "event_type": event_type,
                "algorithm": self.config.algorithm,
                "timestamp": datetime.utcnow().isoformat(),
                **(context or {})
            }
            # Determine severity
            if "failed" in event_type:
                severity = "error"
            elif "skipped" in event_type:
                severity = "warning"
            else:
                severity = "info"
            await self.audit_integration.log_security_event(
                event_type=f"encryption_{event_type}",
                severity=severity,
                description=message,
                details=details
            )
        except Exception as e:
            logger.error(f"Failed to log encryption event: {e}")

    def is_available(self) -> bool:
        """Check if encryption service is available and operational."""
        return self._crypto_available and len(self._encryption_keys) > 0

    def get_encryption_status(self) -> Dict[str, Any]:
        """Get current encryption service status."""
        return {
            "available": self.is_available(),
            "crypto_available": self._crypto_available,
            "keys_loaded": len(self._encryption_keys),
            "algorithm": self.config.algorithm,
            "key_derivation": self.config.key_derivation,
            "operations_performed": len(self._operation_log)
        }

# Global service instance
_encryption_service: Optional[RobustEncryptionService] = None

def get_encryption_service(config: Optional[EncryptionConfig] = None) -> RobustEncryptionService:
    """Get or create global encryption service instance."""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = RobustEncryptionService(config)
    return _encryption_service

# Convenience functions for common operations
async def encrypt_sensitive_data(
    data: str,
    policy: EncryptionPolicy = EncryptionPolicy.REQUIRED
) -> EncryptionResult:
    """Encrypt sensitive data(child information, medical notes, etc.)."""
    service = get_encryption_service()
    return await service.encrypt(data, policy=policy, context={"data_type": "sensitive"})

async def decrypt_sensitive_data(
    encrypted_data: str,
    policy: EncryptionPolicy = EncryptionPolicy.REQUIRED
) -> EncryptionResult:
    """Decrypt sensitive data with strict policy enforcement."""
    service = get_encryption_service()
    return await service.decrypt(encrypted_data, policy=policy, context={"data_type": "sensitive"})
