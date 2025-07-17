"""Key Rotation Orchestrator
Coordinates key rotation operations using specialized services.
"""

from typing import Any

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.key_management.key_generator import (
    KeyGenerator,
)
from src.infrastructure.security.key_management.key_lifecycle_manager import (
    KeyLifecycleManager,
)
from src.infrastructure.security.key_management.rotation_executor import (
    RotationExecutor,
)
from src.infrastructure.security.key_management.rotation_policy_manager import (
    RotationPolicyManager,
)
from src.infrastructure.security.key_management.rotation_statistics import (
    RotationStatistics,
)
from src.infrastructure.security.key_rotation_service import (
    FileKeyStorage,
    KeyStorageInterface,
    KeyType,
    RotationResult,
    RotationTrigger,
)

logger = get_logger(__name__, component="security")


class KeyRotationOrchestrator:
    """Orchestrates key rotation operations using specialized services.
    This is the main entry point for key rotation functionality,
    delegating specific responsibilities to focused services.
    """

    def __init__(self, storage: KeyStorageInterface | None = None) -> None:
        """Initialize orchestrator with all required services.

        Args:
            storage: Key storage backend (defaults to FileKeyStorage)

        """
        # Initialize storage
        self.storage = storage or FileKeyStorage()

        # Initialize specialized services
        self.generator = KeyGenerator()
        self.lifecycle_manager = KeyLifecycleManager(
            self.storage, self.generator
        )
        self.policy_manager = RotationPolicyManager(self.storage)
        self.executor = RotationExecutor(
            self.storage,
            self.generator,
            self.lifecycle_manager,
            self.policy_manager,
        )
        self.statistics = RotationStatistics(self.storage, self.policy_manager)

        logger.info("Key rotation orchestrator initialized")

    def create_key(
        self, key_type: KeyType, algorithm: str = "AES-256"
    ) -> str | None:
        """Create a new key.

        Args:
            key_type: Type of key to create
            algorithm: Encryption algorithm
        Returns:
            Key ID if successful

        """
        return self.lifecycle_manager.create_key(key_type, algorithm)

    def rotate_key(
        self,
        key_id: str,
        trigger: RotationTrigger = RotationTrigger.MANUAL,
    ) -> RotationResult:
        """Rotate a specific key.

        Args:
            key_id: ID of key to rotate
            trigger: What triggered this rotation
        Returns:
            RotationResult with operation details

        """
        return self.executor.rotate_key(key_id, trigger)

    def rotate_all_keys(
        self, key_type: KeyType | None = None
    ) -> list[RotationResult]:
        """Rotate all keys of specified type.

        Args:
            key_type: Type of keys to rotate, or None for all
        Returns:
            List of rotation results

        """
        results = []
        keys = self.storage.list_keys(key_type)

        for key_metadata in keys:
            if key_metadata.is_active:
                result = self.executor.rotate_key(
                    key_metadata.key_id,
                    RotationTrigger.MANUAL,
                )
                results.append(result)

        return results

    def perform_scheduled_rotation(self) -> dict[str, Any]:
        """Perform scheduled rotation for eligible keys.

        Returns:
            Summary of rotation operations

        """
        return self.executor.perform_scheduled_rotation()

    def emergency_rotation(
        self,
        trigger: RotationTrigger = RotationTrigger.SECURITY_INCIDENT,
    ) -> dict[str, Any]:
        """Perform emergency rotation of all keys.

        Args:
            trigger: What triggered the emergency
        Returns:
            Summary of emergency rotation

        """
        return self.executor.emergency_rotation(trigger)

    def cleanup_old_keys(self, days: int = 30) -> int:
        """Clean up old inactive keys.

        Args:
            days: Remove keys older than this many days
        Returns:
            Number of keys cleaned up

        """
        from datetime import timedelta

        return self.lifecycle_manager.cleanup_old_keys(timedelta(days=days))

    def get_rotation_statistics(self) -> dict[str, Any]:
        """Get comprehensive rotation statistics.

        Returns:
            Dictionary with rotation statistics

        """
        return self.statistics.get_rotation_statistics()

    def check_rotation_needed(self) -> list[str]:
        """Get list of key IDs that need rotation.

        Returns:
            List of key IDs needing rotation

        """
        keys_needing_rotation = self.policy_manager.get_keys_needing_rotation()
        return [k.key_id for k in keys_needing_rotation]
