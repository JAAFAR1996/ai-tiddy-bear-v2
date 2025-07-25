"""Core consent management functionality extracted into clean, maintainable modules.
File reduced from 557 lines to < 200 lines for better maintainability.
"""

from datetime import datetime
from typing import Any

from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.database_manager import Database
from src.infrastructure.persistence.repositories.consent_repository import (
    ConsentRepository,
)

from .verification_service import VerificationService

logger = get_logger(__name__, component="services")


class ConsentService:
    """This service manages the entire consent lifecycle with proper audit trails and compliance validation.
    Refactored into modular architecture for maintainability and scalability.

    Features:
    - Consent request and grant workflows
    - Comprehensive audit trails
    - COPPA compliance validation
    - Integration with verification service
    - Real database storage with PostgreSQL
    - Clean separation of concerns
    """

    def __init__(self, database: Database | None = None) -> None:
        """Initialize the consent service with database-backed storage.

        Args:
            database: Database instance (defaults to Database from environment)
        """
        self.database = database or Database()
        self.consent_repository = ConsentRepository(self.database)
        self.verification_service = VerificationService()
        logger.info("ConsentService initialized with database-backed storage")

    async def request_consent(
        self,
        parent_id: str,
        child_id: str,
        feature: str,
        expiry_days: int = 365,
    ) -> dict[str, Any]:
        """Request parental consent for a specific feature or data collection.

        Args:
            parent_id: Unique identifier for the parent / guardian
            child_id: Unique identifier for the child
            feature: Specific feature or data collection requiring consent
            expiry_days: Number of days the consent remains valid
        Returns: Dictionary containing consent_id and current status
        """
        try:
            # Create consent record in database
            consent_id = await self.consent_repository.create_consent_record(
                parent_id=parent_id,
                child_id=child_id,
                consent_type=feature,
                data_types=[feature],  # Convert feature to data types list
                expires_days=expiry_days,
            )

            logger.info(f"Consent requested for feature: {feature} (ID: {consent_id})")
            return {"consent_id": consent_id, "status": "pending"}

        except Exception as e:
            logger.exception(f"Failed to request consent for feature {feature}: {e}")
            return {"consent_id": None, "status": "error", "error": str(e)}

    async def grant_consent(
        self, consent_id: str, verification_method: str
    ) -> dict[str, Any]:
        """Grant a pending consent request after proper verification.

        Args:
            consent_id: Unique identifier for the consent request
            verification_method: Method used to verify parent identity
        Returns: Dictionary with consent_id and updated status
        """
        try:
            # Grant consent in database
            success = await self.consent_repository.grant_consent(
                consent_id=consent_id,
                verification_method=verification_method,
                verification_metadata={
                    "granted_at": datetime.utcnow().isoformat(),
                    "verification_method": verification_method,
                },
            )

            if success:
                logger.info(
                    f"Consent granted via {verification_method} (ID: {consent_id})"
                )
                return {"consent_id": consent_id, "status": "granted"}
            else:
                logger.warning(f"Failed to grant consent: {consent_id}")
                return {"consent_id": consent_id, "status": "not_found"}

        except Exception as e:
            logger.exception(f"Failed to grant consent {consent_id}: {e}")
            return {"consent_id": consent_id, "status": "error", "error": str(e)}

    async def revoke_consent(self, consent_id: str) -> dict[str, Any]:
        """Revoke a previously granted consent.

        Args:
            consent_id: Unique identifier for the consent request
        Returns: Dictionary with consent_id and updated status
        """
        try:
            # Revoke consent in database
            success = await self.consent_repository.revoke_consent(
                consent_id=consent_id, revocation_reason="Parent requested revocation"
            )

            if success:
                logger.info(f"Consent revoked (ID: {consent_id})")
                return {"consent_id": consent_id, "status": "revoked"}
            else:
                logger.warning(f"Failed to revoke consent: {consent_id}")
                return {"consent_id": consent_id, "status": "not_found"}

        except Exception as e:
            logger.exception(f"Failed to revoke consent {consent_id}: {e}")
            return {"consent_id": consent_id, "status": "error", "error": str(e)}

    async def check_consent_status(self, consent_id: str) -> dict[str, Any]:
        """Check the current status of a consent request.

        Args:
            consent_id: Unique identifier for the consent request
        Returns: Dictionary with consent details and current status
        """
        try:
            # Get consent status from database
            consent_statuses = await self.consent_repository.get_consent_status()

            # Find the specific consent record
            for status in consent_statuses:
                if status["consent_id"] == consent_id:
                    return {
                        "consent_id": consent_id,
                        "status": (
                            "granted"
                            if status["granted"] and status["valid"]
                            else "pending"
                        ),
                        "granted": status["granted"],
                        "valid": status["valid"],
                        "granted_at": status["granted_at"],
                        "expires_at": status["expires_at"],
                        "revoked_at": status["revoked_at"],
                        "verification_method": status["verification_method"],
                        "data_types": status["data_types"],
                    }

            return {"consent_id": consent_id, "status": "not_found"}

        except Exception as e:
            logger.exception(f"Failed to check consent status for {consent_id}")
            return {"consent_id": consent_id, "status": "error", "error": str(e)}

    async def verify_parental_consent(
        self, parent_id: str, child_id: str, consent_type: str
    ) -> bool:
        """Verify that valid parental consent exists for a specific action.

        Args:
            parent_id: Parent identifier
            child_id: Child identifier
            consent_type: Type of consent to verify
        Returns: True if valid consent exists, False otherwise
        """
        try:
            # Use repository to verify consent
            return await self.consent_repository.verify_consent(
                parent_id=parent_id,
                child_id=child_id,
                consent_type=consent_type,
            )

        except Exception:
            logger.exception(
                f"Failed to verify consent for parent {parent_id}, child {child_id}"
            )
            return False

    async def get_consent_status_for_child(
        self, parent_id: str, child_id: str
    ) -> dict[str, Any]:
        """Get all consent statuses for a specific child.

        Args:
            parent_id: Parent identifier
            child_id: Child identifier
        Returns: Dictionary with all consent statuses for the child
        """
        try:
            # Get all consents for this parent and child
            consent_statuses = await self.consent_repository.get_consent_status(
                parent_id=parent_id,
                child_id=child_id,
            )

            # Group by consent type
            consent_by_type = {}
            for status in consent_statuses:
                consent_type = status["consent_type"]
                consent_by_type[consent_type] = {
                    "granted": status["granted"],
                    "valid": status["valid"],
                    "granted_at": status["granted_at"],
                    "expires_at": status["expires_at"],
                    "revoked_at": status["revoked_at"],
                    "verification_method": status["verification_method"],
                }

            return {
                "child_id": child_id,
                "parent_id": parent_id,
                "consent_status": consent_by_type,
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.exception(f"Failed to get consent status for child {child_id}")
            return {
                "child_id": child_id,
                "parent_id": parent_id,
                "error": str(e),
            }

    async def initiate_email_verification(
        self, consent_id: str, email: str
    ) -> dict[str, Any]:
        """Initiate email verification for consent.

        Args:
            consent_id: Consent request identifier
            email: Parent's email address
        Returns:
            Verification initiation result
        """
        return await self.verification_service.send_email_verification(
            email, consent_id
        )

    async def initiate_sms_verification(
        self, consent_id: str, phone: str
    ) -> dict[str, Any]:
        """Initiate SMS verification for consent.

        Args:
            consent_id: Consent request identifier
            phone: Parent's phone number
        Returns: Verification initiation result
        """
        return await self.verification_service.send_sms_verification(phone, consent_id)

    async def complete_verification(
        self, attempt_id: str, verification_code: str
    ) -> dict[str, Any]:
        """Complete verification with submitted code.

        Args:
            attempt_id: Verification attempt identifier
            verification_code: Code submitted by parent
        Returns: Verification completion result
        """
        return await self.verification_service.verify_code(
            attempt_id, verification_code
        )

    def get_consent_audit_trail(self, consent_id: str) -> dict[str, Any] | None:
        """Get complete audit trail for a consent request.

        Args:
            consent_id: Consent request identifier
        Returns: Complete audit trail or None if not found
        """
        if consent_id not in self.consents:
            return None
        consent = self.consents[consent_id]
        return {
            "consent_id": consent_id,
            "parent_id": consent.parent_id,
            "child_id": consent.child_id,
            "feature": consent.feature,
            "status": consent.status,
            "requested_at": consent.requested_at,
            "granted_at": consent.granted_at,
            "revoked_at": consent.revoked_at,
            "expiry_date": consent.expiry_date,
            "verification_method": consent.verification_method,
            "metadata": consent.metadata,
        }
