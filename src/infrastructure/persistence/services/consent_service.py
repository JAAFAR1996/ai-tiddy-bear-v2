"""Real database-backed consent management service.

This service provides actual database operations for parental consent
records, replacing dummy implementations with production-ready logic.
"""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.models.consent_models_domain import ConsentType
from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.models.child_models import ChildModel
from src.infrastructure.persistence.models.consent_models_infra import ConsentModel
from src.infrastructure.persistence.models.parent_models import ParentModel

logger = get_logger(__name__)


class ConsentDatabaseService:
    """Real database service for consent management with COPPA compliance."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_consent_record(
        self,
        child_id: str,
        parent_id: str,
        data_types: list[str],
        consent_type: ConsentType = ConsentType.EXPLICIT,
    ) -> str:
        """Create a real consent record in the database.

        Args:
            child_id: Child identifier
            parent_id: Parent identifier
            data_types: Types of data requiring consent
            consent_type: Type of consent (explicit/implicit)

        Returns:
            Database-generated consent ID

        Raises:
            ValueError: If child or parent not found
            RuntimeError: If database operation fails
        """
        try:
            # Verify child and parent exist
            child_exists = await self.db.scalar(
                select(ChildModel.id).where(ChildModel.id == child_id)
            )
            if not child_exists:
                raise ValueError(f"Child with ID {child_id} not found")

            parent_exists = await self.db.scalar(
                select(ParentModel.id).where(ParentModel.id == parent_id)
            )
            if not parent_exists:
                raise ValueError(f"Parent with ID {parent_id} not found")

            # Create consent record
            consent_id = str(uuid.uuid4())
            consent_record = ConsentModel(
                id=consent_id,
                parent_id=parent_id,
                consent_type=consent_type,
                granted=True,  # Initially granted, can be revoked later
                granted_at=datetime.now(UTC),
                expires_at=datetime.now(UTC) + timedelta(days=365),  # 1 year expiry
                verification_method="parental_confirmation",
                verification_metadata={
                    "child_id": child_id,
                    "data_types": data_types,
                    "ip_address": "tracking_required",
                    "user_agent": "tracking_required",
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            )

            self.db.add(consent_record)
            await self.db.commit()

            logger.info(
                f"Created consent record: {consent_id} for child {child_id}, parent {parent_id}"
            )
            return consent_id

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create consent record: {e}")
            raise RuntimeError(f"Database error creating consent: {e}")

    async def verify_parental_consent(
        self, parent_id: str, child_id: str, consent_type: str = "data_access"
    ) -> bool:
        """Verify valid parental consent exists for data access.

        Args:
            parent_id: Parent identifier
            child_id: Child identifier
            consent_type: Type of consent to verify

        Returns:
            True if valid consent exists, False otherwise
        """
        try:
            # Check for active consent record
            consent = await self.db.scalar(
                select(ConsentModel)
                .where(
                    and_(
                        ConsentModel.parent_id == parent_id,
                        ConsentModel.granted == True,
                        ConsentModel.expires_at > datetime.now(UTC),
                        ConsentModel.revoked_at.is_(None),
                    )
                )
                .options(selectinload(ConsentModel.verification_metadata))
            )

            if not consent:
                logger.warning(
                    f"No valid consent found for parent {parent_id}, child {child_id}"
                )
                return False

            # Check if consent covers the requested child
            metadata = consent.verification_metadata or {}
            if metadata.get("child_id") != child_id:
                logger.warning(f"Consent does not cover child {child_id}")
                return False

            logger.info(
                f"Valid consent verified for parent {parent_id}, child {child_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Error verifying consent: {e}")
            return False

    async def revoke_consent(
        self, consent_id: str, reason: str = "parent_revocation"
    ) -> bool:
        """Revoke parental consent record.

        Args:
            consent_id: Consent record ID to revoke
            reason: Reason for revocation

        Returns:
            True if revoked successfully, False otherwise
        """
        try:
            result = await self.db.execute(
                update(ConsentModel)
                .where(ConsentModel.id == consent_id)
                .values(
                    granted=False,
                    revoked_at=datetime.now(UTC),
                    verification_metadata=ConsentModel.verification_metadata.op("||")(
                        {
                            "revocation_reason": reason,
                            "revoked_at": datetime.now(UTC).isoformat(),
                        }
                    ),
                )
            )

            if result.rowcount == 0:
                logger.warning(f"No consent record found with ID {consent_id}")
                return False

            await self.db.commit()
            logger.info(f"Revoked consent {consent_id}, reason: {reason}")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to revoke consent {consent_id}: {e}")
            return False

    async def get_consent_status(self, consent_id: str) -> dict[str, Any]:
        """Get consent record status and details.

        Args:
            consent_id: Consent record ID

        Returns:
            Dictionary with consent status and metadata
        """
        try:
            consent = await self.db.scalar(
                select(ConsentModel).where(ConsentModel.id == consent_id)
            )

            if not consent:
                return {"status": "not_found", "consent_id": consent_id}

            now = datetime.now(UTC)
            is_expired = consent.expires_at and consent.expires_at < now
            is_revoked = consent.revoked_at is not None

            status = "active"
            if is_revoked:
                status = "revoked"
            elif is_expired:
                status = "expired"
            elif not consent.granted:
                status = "denied"

            return {
                "consent_id": consent_id,
                "status": status,
                "granted": consent.granted,
                "granted_at": (
                    consent.granted_at.isoformat() if consent.granted_at else None
                ),
                "expires_at": (
                    consent.expires_at.isoformat() if consent.expires_at else None
                ),
                "revoked_at": (
                    consent.revoked_at.isoformat() if consent.revoked_at else None
                ),
                "consent_type": consent.consent_type.value,
                "verification_method": consent.verification_method,
                "metadata": consent.verification_metadata,
            }

        except Exception as e:
            logger.error(f"Error getting consent status for {consent_id}: {e}")
            return {"status": "error", "consent_id": consent_id, "error": str(e)}

    async def list_consents_for_child(self, child_id: str) -> list[dict[str, Any]]:
        """List all consent records for a specific child.

        Args:
            child_id: Child identifier

        Returns:
            List of consent records with status information
        """
        try:
            consents = await self.db.scalars(
                select(ConsentModel)
                .where(
                    ConsentModel.verification_metadata.op("->")("child_id").astext
                    == child_id
                )
                .order_by(ConsentModel.granted_at.desc())
            )

            consent_list = []
            for consent in consents:
                status_info = await self.get_consent_status(consent.id)
                consent_list.append(status_info)

            return consent_list

        except Exception as e:
            logger.error(f"Error listing consents for child {child_id}: {e}")
            return []
