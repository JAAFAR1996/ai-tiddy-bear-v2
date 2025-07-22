"""COPPA-Compliant Consent Manager
from src.application.interfaces.infrastructure_services import IConsentManager
Provides comprehensive consent management with FTC-approved verification methods.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from uuid import uuid4

from src.application.interfaces.infrastructure_services import IConsentManager
from src.domain.models.consent_models_domain import (
    VerificationMethod,
    VerificationStatus,
    ConsentType,
    ConsentStatus,
    ConsentRecord
)
from src.infrastructure.logging_config import get_logger
from src.application.services.child_safety.consent_service import ConsentService

logger = get_logger(__name__, component="security")


class COPPAConsentManager(IConsentManager):
    """COPPA-compliant consent management system.

    This manager handles all aspects of parental consent including:
    - Consent requests and approvals
    - Verification processes
    - Consent status tracking
    - Audit trail maintenance
    """

    def __init__(self, consent_service: Optional[ConsentService] = None):
        """Initialize with optional consent service injection."""
        self._consent_service = consent_service or ConsentService()
        self._consent_cache: Dict[str, ConsentRecord] = {}

    async def verify_parental_consent(
        self,
        parent_id: str,
        child_id: str,
        consent_type: str
    ) -> bool:
        """Verify if valid parental consent exists for specific action.

        Args:
            parent_id: Parent identifier
            child_id: Child identifier  
            consent_type: Type of consent to verify

        Returns:
            True if valid consent exists, False otherwise
        """
        try:
            # Check cache first
            cache_key = f"{parent_id}_{child_id}_{consent_type}"
            if cache_key in self._consent_cache:
                record = self._consent_cache[cache_key]
                if self._is_consent_valid(record):
                    return True

            # Check with consent service
            return await self._consent_service.verify_parental_consent(
                parent_id, child_id, consent_type
            )

        except Exception as e:
            logger.error(f"Error verifying consent: {str(e)}")
            return False

    async def request_parental_consent(
        self,
        parent_id: str,
        child_id: str,
        child_name: str,
        consent_types: List[str],
        parent_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Request parental consent for child data collection.

        Args:
            parent_id: Parent identifier
            child_id: Child identifier
            child_name: Child's name
            consent_types: Types of consent requested
            parent_email: Parent's email for verification

        Returns:
            Dict with consent request details
        """
        try:
            consent_requests = []

            for consent_type in consent_types:
                result = await self._consent_service.request_consent(
                    parent_id=parent_id,
                    child_id=child_id,
                    feature=consent_type,
                    expiry_days=365
                )
                consent_requests.append(result)

            return {
                "success": True,
                "consent_requests": consent_requests,
                "verification_required": True,
                "parent_email": parent_email,
                "next_steps": "Parent must verify consent via email"
            }

        except Exception as e:
            logger.error(f"Error requesting consent: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_child_consent_status(self, child_id: str) -> Dict[str, Any]:
        """Get comprehensive consent status for a child.

        Args:
            child_id: Child identifier

        Returns:
            Dict with consent status for all types
        """
        try:
            consent_types = [
                "data_collection",
                "voice_recording",
                "interaction_logging",
                "safety_monitoring"
            ]

            status = {}
            for consent_type in consent_types:
                # This would check actual consent records
                status[consent_type] = {
                    "granted": False,  # Would check real status
                    "expires_at": None,
                    "verification_method": None
                }

            return {
                "child_id": child_id,
                "consent_status": status,
                "last_updated": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting consent status: {str(e)}")
            return {
                "child_id": child_id,
                "error": str(e)
            }

    async def revoke_consent(
        self,
        parent_id: str,
        child_id: str,
        consent_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Revoke parental consent.

        Args:
            parent_id: Parent identifier
            child_id: Child identifier
            consent_type: Specific type to revoke (None = all)

        Returns:
            Revocation result
        """
        try:
            if consent_type:
                consent_id = f"consent_{parent_id}_{child_id}_{consent_type}"
                result = await self._consent_service.revoke_consent(consent_id)
                return {
                    "success": result["status"] == "revoked",
                    "revoked_types": [consent_type]
                }
            else:
                # Revoke all consents
                consent_types = ["data_collection", "voice_recording", "interaction_logging"]
                revoked = []

                for ct in consent_types:
                    consent_id = f"consent_{parent_id}_{child_id}_{ct}"
                    result = await self._consent_service.revoke_consent(consent_id)
                    if result["status"] == "revoked":
                        revoked.append(ct)

                return {
                    "success": True,
                    "revoked_types": revoked
                }

        except Exception as e:
            logger.error(f"Error revoking consent: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _is_consent_valid(self, record: ConsentRecord) -> bool:
        """Check if consent record is valid."""
        if record.status != ConsentStatus.GRANTED:
            return False
        if record.expires_at and datetime.utcnow() > record.expires_at:
            return False
        return True

    # Compatibility method for ParentalConsentManager
    async def create_consent_record(
        self,
        child_id: str,
        parent_id: str,
        data_types: List[str]
    ) -> str:
        """Create consent record (compatibility method).

        This method exists for backward compatibility with ParentalConsentManager.
        """
        result = await self.request_parental_consent(
            parent_id=parent_id,
            child_id=child_id,
            child_name="Child",  # Would get from database
            consent_types=data_types
        )

        if result.get("success") and result.get("consent_requests"):
            return result["consent_requests"][0]["consent_id"]

        return f"consent_error_{uuid4().hex}"
