from datetime import datetime
from typing import Any

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.child_safety.data_retention import DataRetentionManager
from src.infrastructure.security.encryption.robust_encryption_service import (
    RobustEncryptionService as ChildDataEncryption,
)
from src.infrastructure.validators.security.coppa_validator import COPPAValidator

logger = get_logger(__name__, component="security")


class ChildDataSecurityManager:
    """Enhanced child data security manager."""

    def __init__(self, encryption_key: str | None = None) -> None:
        self.encryption = ChildDataEncryption(encryption_key)
        self.coppa_validator = COPPAValidator()
        self.data_retention_manager = DataRetentionManager()

    def secure_child_profile(
        self,
        child_data: dict[str, Any],
        parent_consent: dict[str, Any],
    ) -> dict[str, Any]:
        """Secure child profile with COPPA compliance."""
        try:
            # Create COPPA consent record
            consent_record = self.encryption.create_consent_record(
                child_id=child_data.get("id", ""),
                consent_method=parent_consent.get("method", "digital"),
                ip_address=parent_consent.get("ip_address"),
            )

            compliance_check = self.encryption.validate_coppa_compliance(
                child_data,
                consent_record,
            )

            if not compliance_check["compliant"]:
                raise ValueError(
                    f"COPPA compliance violations: {compliance_check['violations']}",
                )

            # Encrypt sensitive data
            encrypted_data = self.encryption.encrypt_child_data(child_data)

            # Add compliance information
            encrypted_data["_coppa_compliance"] = {
                "consent_timestamp": consent_record.consent_timestamp.isoformat(),
                "data_retention_expires": consent_record.data_retention_expires.isoformat(),
                "compliance_verified": True,
            }

            return encrypted_data
        except Exception as e:
            logger.error(f"Failed to secure child profile: {e}")
            raise

    def get_child_data_for_interaction(
        self,
        encrypted_child_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Get child data for interaction with COPPA check."""
        try:
            # Decrypt data
            decrypted_data = self.encryption.decrypt_child_data(encrypted_child_data)

            # Check data expiration
            coppa_info = encrypted_child_data.get("_coppa_compliance", {})
            if coppa_info.get("data_retention_expires"):
                expiry = datetime.fromisoformat(coppa_info["data_retention_expires"])
                if datetime.utcnow() > expiry:
                    raise ValueError(
                        "Child data retention period expired - data access denied",
                    )

            return decrypted_data
        except Exception as e:
            logger.error(f"Failed to get child data for interaction: {e}")
            raise

    async def schedule_data_cleanup(self) -> dict[str, Any]:
        """Schedule cleanup of expired data."""
        # Use DataRetentionManager to find expired children
        expired_children = await self.data_retention_manager._find_expired_children()
        cleanup_summary = {
            "total_expired": len(expired_children),
            "expired_records": expired_children,
            "cleanup_scheduled": datetime.utcnow().isoformat(),
        }

        if expired_children:
            logger.warning(
                f"Found {len(expired_children)} child records requiring data deletion",
            )

        return cleanup_summary
