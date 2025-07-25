"""Rotation Statistics Service
Provides key rotation statistics and reporting.
"""

from datetime import datetime
from typing import Any

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.key_management.key_rotation_service import (
    KeyMetadata,
    KeyStorageInterface,
    KeyType,
)
from src.infrastructure.security.key_management.rotation_policy_manager import (
    RotationPolicyManager,
)

logger = get_logger(__name__, component="security")


class RotationStatistics:
    """Calculates and reports key rotation statistics."""

    def __init__(
        self,
        storage: KeyStorageInterface,
        policy_manager: RotationPolicyManager,
    ) -> None:
        """Initialize statistics service.

        Args:
            storage: Key storage backend
            policy_manager: Rotation policy manager

        """
        self.storage = storage
        self.policy_manager = policy_manager

    def get_rotation_statistics(self) -> dict[str, Any]:
        """Get comprehensive rotation statistics.

        Returns:
            Dictionary with rotation statistics

        """
        all_keys = self.storage.list_keys()
        active_keys = [k for k in all_keys if k.is_active]

        # Group by key type
        by_type = {}
        for key_type in KeyType:
            type_keys = [k for k in active_keys if k.key_type == key_type]
            by_type[key_type.value] = {
                "active_count": len(type_keys),
                "avg_age_days": self._calculate_average_age(type_keys),
                "needs_rotation": len(
                    [
                        k
                        for k in type_keys
                        if self.policy_manager.check_rotation_needed(k)
                    ],
                ),
            }

        next_rotation = self.policy_manager.get_next_rotation_time()
        return {
            "total_keys": len(all_keys),
            "active_keys": len(active_keys),
            "inactive_keys": len(all_keys) - len(active_keys),
            "keys_by_type": by_type,
            "next_scheduled_rotation": (
                next_rotation.isoformat() if next_rotation else None
            ),
            "child_data_keys": len(
                [k for k in active_keys if k.key_type == KeyType.CHILD_DATA],
            ),
        }

    def _calculate_average_age(self, keys: list[KeyMetadata]) -> float:
        """Calculate average age of keys in days.

        Args:
            keys: List of key metadata
        Returns:
            Average age in days

        """
        if not keys:
            return 0.0

        current_time = datetime.utcnow()
        total_age = sum((current_time - key.created_at).days for key in keys)
        return total_age / len(keys)

    def get_key_usage_report(self) -> dict[str, Any]:
        """Generate key usage report.

        Returns:
            Usage statistics by key type

        """
        usage_report = {}
        for key_type in KeyType:
            keys = [
                k
                for k in self.storage.list_keys()
                if k.key_type == key_type and k.is_active
            ]
            if keys:
                total_usage = sum(k.usage_count for k in keys)
                avg_usage = total_usage / len(keys) if keys else 0
                usage_report[key_type.value] = {
                    "total_keys": len(keys),
                    "total_usage": total_usage,
                    "average_usage": avg_usage,
                    "most_used_key": (
                        max(keys, key=lambda k: k.usage_count).key_id if keys else None
                    ),
                }
        return usage_report

    def get_rotation_history(self, days: int = 30) -> list[dict[str, Any]]:
        """Get rotation history for the past N days.

        Args:
            days: Number of days to look back
        Returns:
            List of rotation events

        """
        # This would normally query from an audit log
        # For now, we'll return a placeholder
        return []
