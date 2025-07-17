"""Key Generation Service
Responsible solely for cryptographic key generation with child safety enhancements.
"""

import secrets
from datetime import datetime

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.key_rotation_service import KeyType

logger = get_logger(__name__, component="security")


class KeyGenerator:
    """Generates cryptographic keys with algorithm-specific implementations."""

    def __init__(self) -> None:
        """Initialize key generator."""
        self.algorithm_key_sizes = {"AES-256": 32, "AES-128": 16, "ChaCha20": 32}

    def generate_key(
        self,
        key_type: KeyType,
        algorithm: str = "AES-256",
    ) -> tuple[str, bytes]:
        """Generate a new cryptographic key.

        Args:
            key_type: Type of key to generate
            algorithm: Encryption algorithm
        Returns:
            Tuple of (key_id, key_data)

        """
        # Generate unique key ID
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        random_suffix = secrets.token_hex(4)
        key_id = f"{key_type.value}_{timestamp}_{random_suffix}"

        # Enhanced security for child data keys
        if key_type == KeyType.CHILD_DATA:
            algorithm = "ChaCha20"  # Better performance and security for child data

        # Generate key based on algorithm
        key_size = self.algorithm_key_sizes.get(algorithm)
        if not key_size:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        key_data = secrets.token_bytes(key_size)
        logger.info(f"Generated new {algorithm} key: {key_id}")

        return key_id, key_data
