"""Rotation Policy Manager
Manages key rotation policies and determines when keys need rotation.
"""

from datetime import datetime, timedelta

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.key_rotation_service import (
    KeyMetadata,
    KeyStorageInterface,
    KeyType,
)

logger = get_logger(__name__, component="security")


class RotationPolicyManager:
    """Manages rotation policies and checks."""

    def __init__(self, storage: KeyStorageInterface) -> None:
        """Initialize policy manager.

        Args:
            storage: Key storage backend

        """
        self.storage = storage
        self.max_key_usage = 1000000  # Maximum operations per key
        self.child_data_max_age = timedelta(days=30)  # Rotate child data keys monthly

    def check_rotation_needed(self, key_metadata: KeyMetadata) -> bool:
        """Check if a specific key needs rotation.

        Args:
            key_metadata: Metadata of key to check
        Returns:
            True if rotation is needed

        """
        if not key_metadata.is_active:
            return False

        current_time = datetime.utcnow()

        # Check age-based rotation
        if key_metadata.expires_at and current_time >= key_metadata.expires_at:
            return True

        # Check usage-based rotation
        if key_metadata.usage_count >= self.max_key_usage:
            return True

        # Special check for child data keys (more strict)
        return bool(
            key_metadata.key_type == KeyType.CHILD_DATA
            and current_time - key_metadata.created_at >= self.child_data_max_age
        )

    def get_keys_needing_rotation(self) -> list[KeyMetadata]:
        """Get all keys that need rotation.

        Returns:
            List of keys that need rotation

        """
        needs_rotation = []
        for key_metadata in self.storage.list_keys():
            if self.check_rotation_needed(key_metadata):
                needs_rotation.append(key_metadata)
        return needs_rotation

    def get_next_rotation_time(self) -> datetime | None:
        """Get the next scheduled rotation time.

        Returns:
            Next rotation time or None

        """
        active_keys = [k for k in self.storage.list_keys() if k.is_active]
        if not active_keys:
            return None

        # Find the key that expires soonest
        keys_with_expiry = [k for k in active_keys if k.expires_at]
        if not keys_with_expiry:
            return None

        next_key = min(keys_with_expiry, key=lambda k: k.expires_at)
        return next_key.expires_at

    def get_affected_services(self, key_type: KeyType) -> list[str]:
        """Get list of services affected by key rotation.

        Args:
            key_type: Type of key being rotated
        Returns:
            List of affected service names

        """
        service_map = {
            KeyType.ENCRYPTION: [
                "data_encryption",
                "file_storage",
                "backup_service",
            ],
            KeyType.SIGNING: ["api_gateway", "jwt_service", "audit_service"],
            KeyType.JWT: ["authentication", "session_management"],
            KeyType.SESSION: ["session_service", "cache_service"],
            KeyType.DATABASE: ["database_encryption", "backup_encryption"],
            KeyType.CHILD_DATA: [
                "child_profiles",
                "conversation_storage",
                "medical_data",
                "emergency_contacts",
            ],
        }
        return service_map.get(key_type, [])
