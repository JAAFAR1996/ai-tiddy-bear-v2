"""Key Lifecycle Manager
Manages the creation, expiration, and deletion of cryptographic keys.
"""

from datetime import datetime, timedelta

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.key_management.key_generator import (
    KeyGenerator,
)
from src.infrastructure.security.key_rotation_service import (
    KeyMetadata,
    KeyStorageInterface,
    KeyType,
)

logger = get_logger(__name__, component="security")


class KeyLifecycleManager:
    """Manages key lifecycle operations."""

    def __init__(
        self, storage: KeyStorageInterface, generator: KeyGenerator
    ) -> None:
        """Initialize lifecycle manager.

        Args:
            storage: Key storage backend
            generator: Key generator service

        """
        self.storage = storage
        self.generator = generator
        self.rotation_schedules = self._get_default_schedules()

    def _get_default_schedules(self) -> dict[KeyType, timedelta]:
        """Get default rotation schedules for different key types."""
        return {
            KeyType.ENCRYPTION: timedelta(days=90),
            KeyType.SIGNING: timedelta(days=60),
            KeyType.JWT: timedelta(days=30),
            KeyType.SESSION: timedelta(days=7),
            KeyType.DATABASE: timedelta(days=180),
            KeyType.CHILD_DATA: timedelta(
                days=30
            ),  # More frequent for child data
        }

    def create_key(
        self,
        key_type: KeyType,
        algorithm: str = "AES-256",
        expires_in: timedelta | None = None,
    ) -> str | None:
        """Create and store a new key.

        Args:
            key_type: Type of key to create
            algorithm: Encryption algorithm
            expires_in: Key expiration time
        Returns:
            Key ID if successful, None otherwise

        """
        try:
            key_id, key_data = self.generator.generate_key(key_type, algorithm)

            # Calculate expiration
            created_at = datetime.utcnow()
            if expires_in:
                expires_at = created_at + expires_in
            else:
                expires_at = created_at + self.rotation_schedules[key_type]

            # Create metadata
            metadata = KeyMetadata(
                key_id=key_id,
                key_type=key_type,
                created_at=created_at,
                expires_at=expires_at,
                algorithm=algorithm,
                key_size=256 if algorithm in ["AES-256", "ChaCha20"] else 128,
            )

            # Store key
            if self.storage.store_key(key_id, key_data, metadata):
                logger.info(f"Created new {key_type.value} key: {key_id}")
                return key_id
            logger.error(f"Failed to store key {key_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to create key: {e}")
            return None

    def deactivate_key(self, key_id: str) -> bool:
        """Mark a key as inactive.

        Args:
            key_id: ID of key to deactivate
        Returns:
            Success status

        """
        try:
            key_data = self.storage.retrieve_key(key_id)
            if not key_data:
                logger.error(f"Key not found: {key_id}")
                return False

            key_bytes, metadata = key_data
            metadata.is_active = False
            return self.storage.store_key(key_id, key_bytes, metadata)
        except Exception as e:
            logger.error(f"Failed to deactivate key {key_id}: {e}")
            return False

    def cleanup_old_keys(
        self, older_than: timedelta = timedelta(days=30)
    ) -> int:
        """Clean up old inactive keys.

        Args:
            older_than: Remove keys older than this duration
        Returns:
            Number of keys cleaned up

        """
        cutoff_time = datetime.utcnow() - older_than
        cleaned_count = 0

        for key_metadata in self.storage.list_keys():
            if (
                not key_metadata.is_active
                and key_metadata.created_at < cutoff_time
            ):
                if self.storage.delete_key(key_metadata.key_id):
                    cleaned_count += 1
                    logger.info(f"Cleaned up old key: {key_metadata.key_id}")

        logger.info(f"Key cleanup completed: {cleaned_count} keys removed")
        return cleaned_count
