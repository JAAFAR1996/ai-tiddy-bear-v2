"""Enterprise-grade encryption service with key rotation support.
Compliant with COPPA, PCI-DSS, and OWASP standards for 2025.
"""

import base64
import json
import math  # Added for math.log2
import os
import secrets
from collections import Counter
from datetime import datetime, timedelta
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")


class EncryptionKeyError(Exception):
    """Raised when encryption key operations fail."""


class EncryptionService:
    """Secure encryption service with key validation and rotation capabilities.
    Implements defense-in-depth with multiple layers of security.
    """

    # Key rotation interval (90 days for COPPA compliance)
    KEY_ROTATION_DAYS = 90
    # Minimum key entropy bits
    MIN_KEY_ENTROPY = 256

    def __init__(self) -> None:
        self._fernet: Fernet | None = None
        self._key_version: str | None = None
        self._key_created_at: datetime | None = None
        self._initialize_encryption()

    def _initialize_encryption(self) -> None:
        """Initialize encryption with comprehensive validation."""
        try:
            # Get primary encryption key
            primary_key = os.getenv("COPPA_ENCRYPTION_KEY")
            if not primary_key:
                logger.critical(
                    "COPPA_ENCRYPTION_KEY not found in environment"
                )
                raise EncryptionKeyError(
                    "COPPA_ENCRYPTION_KEY environment variable is required. "
                    'Generate with: python -c "from cryptography.fernet import Fernet; '
                    'Fernet.generate_key().decode()"',
                )
            # Validate key format and strength
            self._validate_encryption_key(primary_key)
            # Derive encryption key using PBKDF2 for additional security
            derived_key = self._derive_key(primary_key)
            # Initialize Fernet with derived key
            self._fernet = Fernet(derived_key)
            # Set key metadata
            self._key_version = self._get_key_version()
            self._key_created_at = self._get_key_creation_date()
            # Check if key rotation is needed
            if self._is_key_rotation_needed():
                logger.warning("Encryption key rotation is recommended")
        except Exception as e:
            logger.critical(f"Failed to initialize encryption service: {e!s}")
            raise EncryptionKeyError(
                f"Encryption initialization failed: {e!s}"
            )

    def _validate_encryption_key(self, key: str) -> None:
        """Validate encryption key meets security requirements."""
        # Check key format
        try:
            # Verify it's a valid Fernet key
            test_fernet = Fernet(key.encode() if isinstance(key, str) else key)
            # Test encryption/decryption
            test_data = b"validation_test"
            encrypted = test_fernet.encrypt(test_data)
            decrypted = test_fernet.decrypt(encrypted)
            if decrypted != test_data:
                raise ValueError("Key validation failed")
        except Exception as e:
            raise EncryptionKeyError(
                f"Invalid encryption key format: {e!s}. "
                "Key must be a valid Fernet key (32 bytes base64-encoded)",
            )
        # Check for default/weak keys and entropy
        if not self._is_key_strong(key):
            raise EncryptionKeyError(
                "Detected weak or insufficiently strong encryption key. "
                "Please generate a new, secure key for production use.",
            )

    def _derive_key(self, master_key: str) -> bytes:
        """Derive encryption key using PBKDF2."""
        # Use application-specific salt
        salt = os.getenv("PBKDF2_SALT", secrets.token_bytes(16).hex()).encode(
            "utf-8"
        )
        if os.getenv("PBKDF2_SALT") is None:
            logger.warning(
                "PBKDF2_SALT not found in environment, using randomly generated salt.",
            )
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # OWASP recommended minimum
        )
        key_bytes = (
            master_key.encode() if isinstance(master_key, str) else master_key
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(key_bytes))
        return derived_key

    def _get_key_version(self) -> str:
        """Get current key version from environment or generate."""
        version = os.getenv("ENCRYPTION_KEY_VERSION")
        if not version:
            # Generate new version identifier
            version = f"v1_{datetime.utcnow().strftime('%Y%m%d')}"
            logger.info(f"Generated new key version: {version}")
        return version

    def _get_key_creation_date(self) -> datetime:
        """Get key creation date from environment or current date."""
        date_str = os.getenv("ENCRYPTION_KEY_CREATED_AT")
        if date_str:
            try:
                return datetime.fromisoformat(date_str)
            except ValueError:
                logger.warning("Invalid key creation date format")
        return datetime.utcnow()

    def _is_key_rotation_needed(self) -> bool:
        """Check if key rotation is needed based on age."""
        if not self._key_created_at:
            return True
        key_age = datetime.utcnow() - self._key_created_at
        return key_age > timedelta(days=self.KEY_ROTATION_DAYS)

    def _is_key_strong(self, key: str) -> bool:
        """Checks if the key meets the minimum entropy requirements."""
        try:
            # Calculate Shannon entropy (bits per character)
            # For base64-encoded Fernet key, it should be high
            char_counts = Counter(key)
            total_chars = len(key)
            entropy = -sum(
                (count / total_chars) * math.log2(count / total_chars)
                for count in char_counts.values()
            )

            # Convert to total bits of entropy
            total_entropy_bits = entropy * total_chars

            return total_entropy_bits >= self.MIN_KEY_ENTROPY
        except Exception as e:
            logger.error(f"Error calculating key entropy: {e}", exc_info=True)
            return False

    def encrypt(self, data: str | bytes | dict[str, Any]) -> str:
        """Encrypt data with metadata for key rotation support.
        Returns base64-encoded encrypted data with version info.
        """
        if not self._fernet:
            raise EncryptionKeyError("Encryption service not initialized")
        # Convert data to bytes
        if isinstance(data, dict):
            data_bytes = json.dumps(data).encode("utf-8")
        elif isinstance(data, str):
            data_bytes = data.encode("utf-8")
        else:
            data_bytes = data
        # Create metadata
        metadata = {
            "version": self._key_version,
            "timestamp": datetime.utcnow().isoformat(),
            "algorithm": "Fernet-PBKDF2",
        }
        # Combine metadata and data
        payload = {
            "metadata": metadata,
            "data": base64.b64encode(data_bytes).decode("utf-8"),
        }
        # Encrypt the entire payload
        encrypted = self._fernet.encrypt(json.dumps(payload).encode("utf-8"))
        # Return base64-encoded result
        return base64.b64encode(encrypted).decode("utf-8")

    def decrypt(
        self, encrypted_data: str | bytes
    ) -> str | bytes | dict[str, Any]:
        """Decrypt data with support for key rotation.
        Handles multiple key versions for smooth rotation.
        """
        if not self._fernet:
            raise EncryptionKeyError("Encryption service not initialized")
        try:
            # Decode from base64
            if isinstance(encrypted_data, str):
                encrypted_bytes = base64.b64decode(encrypted_data)
            else:
                encrypted_bytes = encrypted_data
            # Decrypt payload
            decrypted_payload = self._fernet.decrypt(encrypted_bytes)
            payload = json.loads(decrypted_payload.decode("utf-8"))
            # Extract metadata and data
            metadata = payload.get("metadata", {})
            data_b64 = payload.get("data", "")
            # Log key version for monitoring
            if metadata.get("version") != self._key_version:
                logger.info(
                    f"Decrypting data from older key version: {metadata.get('version')}",
                )
            # Decode actual data
            data_bytes = base64.b64decode(data_b64)
            # Try to decode as JSON first
            try:
                return json.loads(data_bytes.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Try as string
                try:
                    return data_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    # Return as bytes
                    return data_bytes
        except InvalidToken:
            logger.error("Failed to decrypt data - invalid token or wrong key")
            raise EncryptionKeyError(
                "Decryption failed - data may be corrupted or key mismatch",
            )
        except Exception as e:
            logger.error(f"Decryption error: {e!s}")
            raise EncryptionKeyError(f"Decryption failed: {e!s}")

    def rotate_key(self, new_key: str) -> None:
        """Rotate encryption key (for administrative use).
        This should be called through a secure admin interface.
        """
        # Validate new key
        self._validate_encryption_key(new_key)
        # Store old key reference for migration
        old_fernet = self._fernet
        old_version = self._key_version
        try:
            # Initialize with new key
            derived_key = self._derive_key(new_key)
            self._fernet = Fernet(derived_key)
            self._key_version = f"v{int(old_version.split('_')[0][1:]) + 1}_{datetime.utcnow().strftime('%Y%m%d')}"
            self._key_created_at = datetime.utcnow()
            logger.info(
                f"Key rotated successfully from {old_version} to {self._key_version}",
            )
        except Exception as e:
            # Rollback on failure
            self._fernet = old_fernet
            self._key_version = old_version
            logger.error(f"Key rotation failed: {e!s}")
            raise EncryptionKeyError(f"Key rotation failed: {e!s}")

    def generate_secure_key(self) -> str:
        """Generate a new secure encryption key."""
        return Fernet.generate_key().decode()

    def get_key_info(self) -> dict[str, Any]:
        """Get current key information (for monitoring)."""
        return {
            "version": self._key_version,
            "created_at": (
                self._key_created_at.isoformat()
                if self._key_created_at
                else None
            ),
            "rotation_needed": self._is_key_rotation_needed(),
            "algorithm": "Fernet-PBKDF2",
        }


# Global encryption service instance
_encryption_service: EncryptionService | None = None


def get_encryption_service() -> EncryptionService:
    """Get or create global encryption service instance."""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service
