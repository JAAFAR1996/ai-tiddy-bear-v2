from typing import Any

from src.infrastructure.logging_config import get_logger
from src.infrastructure.security.child_data_encryption import (
    ChildDataEncryption,
)
from src.infrastructure.security.models import COPPAComplianceRecord

logger = get_logger(__name__, component="security")


class COPPAComplianceService:
    """COPPA compliance service."""

    def __init__(self, encryption_service: ChildDataEncryption) -> None:
        self.encryption = encryption_service
        self.consent_records: dict[str, COPPAComplianceRecord] = {}

    def process_parental_consent(
        self,
        child_id: str,
        parent_email: str,
        consent_method: str,
        ip_address: str,
    ) -> dict[str, Any]:
        """Process parental consent."""
        try:
            # Create consent record
            consent_record = self.encryption.create_consent_record(
                child_id=child_id,
                consent_method=consent_method,
                ip_address=ip_address,
            )
            self.consent_records[child_id] = consent_record
            self.encryption.add_audit_entry(
                consent_record,
                "parental_consent_processed",
                {"parent_email": parent_email, "method": consent_method},
            )
            return {
                "success": True,
                "child_id": child_id,
                "consent_timestamp": consent_record.consent_timestamp.isoformat(),
                "data_retention_expires": consent_record.data_retention_expires.isoformat(),
                "compliance_status": "compliant",
            }
        except Exception as e:
            logger.error(f"Failed to process parental consent: {e}")
            return {"success": False, "error": str(e)}

    def check_data_retention_compliance(self) -> list[dict[str, Any]]:
        """Check data retention compliance."""
        expired_records = []
        for child_id, consent_record in self.consent_records.items():
            if self.encryption.should_delete_data(consent_record):
                expired_records.append(
                    {
                        "child_id": child_id,
                        "expired_at": consent_record.data_retention_expires.isoformat(),
                        "action_required": "delete_data",
                    },
                )
        return expired_records
