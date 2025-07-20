"""Rotation Executor
Executes key rotation operations with proper orchestration and error handling.
"""

import threading
from dataclasses import asdict
from datetime import datetime
from typing import Any

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.key_management.key_generator import (
    KeyGenerator,
)
from src.infrastructure.security.key_management.key_lifecycle_manager import (
    KeyLifecycleManager,
)
from src.infrastructure.security.key_management.rotation_policy_manager import (
    RotationPolicyManager,
)
from src.infrastructure.security.key_rotation_service import (
    KeyStorageInterface,
    RotationResult,
    RotationTrigger,
)

logger = get_logger(__name__, component="security")


class RotationExecutor:
    """Executes key rotation operations."""

    def __init__(
        self,
        storage: KeyStorageInterface,
        generator: KeyGenerator,
        lifecycle_manager: KeyLifecycleManager,
        policy_manager: RotationPolicyManager,
    ) -> None:
        """Initialize rotation executor.

        Args:
            storage: Key storage backend
            generator: Key generator service
            lifecycle_manager: Key lifecycle manager
            policy_manager: Rotation policy manager

        """
        self.storage = storage
        self.generator = generator
        self.lifecycle_manager = lifecycle_manager
        self.policy_manager = policy_manager
        self.active_rotations: dict[str, datetime] = {}
        self._lock = threading.RLock()

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
        with self._lock:
            try:
                # Check if rotation is already in progress
                if key_id in self.active_rotations:
                    return RotationResult(
                        success=False,
                        old_key_id=key_id,
                        error_message="Rotation already in progress for this key",
                    )

                # Mark rotation as active
                self.active_rotations[key_id] = datetime.utcnow()

                # Retrieve current key
                current_key_data = self.storage.retrieve_key(key_id)
                if not current_key_data:
                    return RotationResult(
                        success=False,
                        old_key_id=key_id,
                        error_message="Key not found",
                    )

                _, current_metadata = current_key_data

                # Create new key with same type and algorithm
                new_key_id = self.lifecycle_manager.create_key(
                    current_metadata.key_type,
                    current_metadata.algorithm,
                )

                if not new_key_id:
                    return RotationResult(
                        success=False,
                        old_key_id=key_id,
                        error_message="Failed to create new key",
                    )

                # Deactivate old key
                if not self.lifecycle_manager.deactivate_key(key_id):
                    logger.warning(f"Failed to deactivate old key {key_id}")

                # Log rotation for audit
                logger.info(
                    f"Successfully rotated key {key_id} -> {new_key_id} "
                    f"(trigger: {trigger.value})",
                )

                return RotationResult(
                    success=True,
                    old_key_id=key_id,
                    new_key_id=new_key_id,
                    rotation_time=datetime.utcnow(),
                    affected_services=self.policy_manager.get_affected_services(
                        current_metadata.key_type,
                    ),
                )
            except Exception as e:
                logger.error(f"Key rotation failed for {key_id}: {e}")
                return RotationResult(
                    success=False,
                    old_key_id=key_id,
                    error_message=str(e),
                )
            finally:
                # Remove from active rotations
                self.active_rotations.pop(key_id, None)

    def perform_scheduled_rotation(self) -> dict[str, Any]:
        """Perform automatic scheduled rotation for eligible keys.

        Returns:
            Summary of rotation operations

        """
        keys_to_rotate = self.policy_manager.get_keys_needing_rotation()
        results = []

        for key_metadata in keys_to_rotate:
            result = self.rotate_key(key_metadata.key_id, RotationTrigger.SCHEDULED)
            results.append(result)

        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_keys_checked": len(self.storage.list_keys()),
            "keys_needing_rotation": len(keys_to_rotate),
            "successful_rotations": successful,
            "failed_rotations": failed,
            "rotation_results": [asdict(r) for r in results],
        }

        logger.info(
            f"Scheduled rotation completed: {successful} successful, {failed} failed",
        )

        return summary

    def emergency_rotation(
        self,
        trigger: RotationTrigger = RotationTrigger.SECURITY_INCIDENT,
    ) -> dict[str, Any]:
        """Perform emergency rotation of all active keys.

        Args:
            trigger: What triggered the emergency rotation
        Returns:
            Summary of emergency rotation

        """
        logger.warning(f"Emergency key rotation initiated: {trigger.value}")

        # Rotate all active keys immediately
        active_keys = [k for k in self.storage.list_keys() if k.is_active]
        results = []

        for key_metadata in active_keys:
            result = self.rotate_key(key_metadata.key_id, trigger)
            results.append(result)

        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "trigger": trigger.value,
            "total_keys_rotated": len(active_keys),
            "successful_rotations": successful,
            "failed_rotations": failed,
            "rotation_results": [asdict(r) for r in results],
        }

        logger.warning(
            f"Emergency rotation completed: {successful} successful, {failed} failed",
        )

        return summary
