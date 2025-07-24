"""Consent Repository for COPPA Compliance.

Enterprise-grade repository for managing parental consent records with full audit trails.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from src.infrastructure.logging_config import get_logger
from src.infrastructure.persistence.database_manager import Database
from src.infrastructure.persistence.models.consent_models_infra import ConsentModel
from src.infrastructure.validators.security.database_input_validator import (
    SecurityError,
    create_safe_database_session,
    database_input_validation,
)

logger = get_logger(__name__, component="persistence")


class ConsentRepository:
    """Repository for consent-related database operations with COPPA compliance."""

    def __init__(self, database: Database) -> None:
        """Initialize consent repository.

        Args:
            database: Database instance
        """
        self.database = database
        logger.info("ConsentRepository initialized")

    @database_input_validation("consents")
    async def create_consent_record(
        self,
        parent_id: str,
        child_id: str,
        consent_type: str,
        data_types: List[str],
        expires_days: int = 365,
    ) -> str:
        """Create a new consent record with full audit trail.

        Args:
            parent_id: Parent identifier
            child_id: Child identifier
            consent_type: Type of consent (e.g., 'data_collection', 'voice_recording')
            data_types: List of data types being consented to
            expires_days: Number of days until consent expires

        Returns:
            Consent record ID

        Raises:
            SecurityError: If validation fails
            IntegrityError: If database constraints are violated
        """
        consent_id = str(uuid4())
        expires_at = datetime.utcnow() + timedelta(days=expires_days)

        async with create_safe_database_session(self.database) as session:
            try:
                # Create consent record
                consent_record = ConsentModel(
                    id=consent_id,
                    parent_id=parent_id,
                    consent_type=consent_type,
                    granted=False,  # Initially pending
                    granted_at=None,
                    expires_at=expires_at,
                    verification_method="pending",
                    verification_metadata={
                        "child_id": child_id,
                        "data_types": data_types,
                        "created_by": "system",
                        "created_at": datetime.utcnow().isoformat(),
                    },
                )

                session.add(consent_record)
                await session.commit()

                logger.info(
                    f"Created consent record {consent_id} for parent {parent_id} "
                    f"covering {len(data_types)} data types"
                )
                return consent_id

            except IntegrityError as e:
                await session.rollback()
                logger.error(f"Failed to create consent record: {e}")
                raise SecurityError(f"Failed to create consent record: {e}")

    @database_input_validation("consents")
    async def grant_consent(
        self,
        consent_id: str,
        verification_method: str,
        verification_metadata: Optional[dict] = None,
    ) -> bool:
        """Grant a pending consent request.

        Args:
            consent_id: Consent record ID
            verification_method: Method used for verification
            verification_metadata: Additional verification details

        Returns:
            True if consent was granted successfully

        Raises:
            SecurityError: If validation fails
        """
        async with create_safe_database_session(self.database) as session:
            try:
                # Find the consent record
                stmt = select(ConsentModel).where(ConsentModel.id == consent_id)
                result = await session.execute(stmt)
                consent = result.scalar_one_or_none()

                if not consent:
                    logger.warning(f"Consent record {consent_id} not found")
                    return False

                if consent.granted:
                    logger.info(f"Consent {consent_id} already granted")
                    return True

                # Update consent record
                consent.granted = True
                consent.granted_at = datetime.utcnow()
                consent.verification_method = verification_method

                if verification_metadata:
                    consent.verification_metadata.update(verification_metadata)

                await session.commit()

                logger.info(f"Granted consent {consent_id} via {verification_method}")
                return True

            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to grant consent: {e}")
                raise SecurityError(f"Failed to grant consent: {e}")

    @database_input_validation("consents")
    async def revoke_consent(
        self,
        consent_id: str,
        revocation_reason: Optional[str] = None,
    ) -> bool:
        """Revoke a granted consent.

        Args:
            consent_id: Consent record ID
            revocation_reason: Reason for revocation

        Returns:
            True if consent was revoked successfully

        Raises:
            SecurityError: If validation fails
        """
        async with create_safe_database_session(self.database) as session:
            try:
                # Find the consent record
                stmt = select(ConsentModel).where(ConsentModel.id == consent_id)
                result = await session.execute(stmt)
                consent = result.scalar_one_or_none()

                if not consent:
                    logger.warning(f"Consent record {consent_id} not found")
                    return False

                # Update consent record
                consent.granted = False
                consent.revoked_at = datetime.utcnow()

                if revocation_reason:
                    consent.verification_metadata.update(
                        {
                            "revocation_reason": revocation_reason,
                            "revoked_at": datetime.utcnow().isoformat(),
                        }
                    )

                await session.commit()

                logger.info(f"Revoked consent {consent_id}: {revocation_reason}")
                return True

            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to revoke consent: {e}")
                raise SecurityError(f"Failed to revoke consent: {e}")

    async def verify_consent(
        self,
        parent_id: str,
        child_id: str,
        consent_type: str,
    ) -> bool:
        """Verify if valid consent exists for a specific operation.

        Args:
            parent_id: Parent identifier
            child_id: Child identifier
            consent_type: Type of consent to verify

        Returns:
            True if valid consent exists

        Raises:
            SecurityError: If validation fails
        """
        async with create_safe_database_session(self.database) as session:
            try:
                # Query for valid consent
                stmt = select(ConsentModel).where(
                    and_(
                        ConsentModel.parent_id == parent_id,
                        ConsentModel.consent_type == consent_type,
                        ConsentModel.granted == True,
                        or_(
                            ConsentModel.expires_at.is_(None),
                            ConsentModel.expires_at > datetime.utcnow(),
                        ),
                        ConsentModel.revoked_at.is_(None),
                    )
                )

                # Check if child_id matches (stored in verification_metadata)
                result = await session.execute(stmt)
                consents = result.scalars().all()

                for consent in consents:
                    metadata = consent.verification_metadata or {}
                    if metadata.get("child_id") == child_id:
                        logger.debug(
                            f"Valid consent found: {consent.id} for parent {parent_id}, "
                            f"child {child_id}, type {consent_type}"
                        )
                        return True

                logger.debug(
                    f"No valid consent found for parent {parent_id}, "
                    f"child {child_id}, type {consent_type}"
                )
                return False

            except Exception as e:
                logger.error(f"Failed to verify consent: {e}")
                raise SecurityError(f"Failed to verify consent: {e}")

    async def get_consent_status(
        self,
        parent_id: str | None = None,
        child_id: str | None = None,
        consent_type: str | None = None,
    ) -> list[dict]:
        """Get consent status records with optional filtering.

        Args:
            parent_id: Optional parent filter
            child_id: Optional child filter
            consent_type: Optional consent type filter

        Returns:
            List of consent status dictionaries

        Raises:
            SecurityError: If validation fails
        """
        async with create_safe_database_session(self.database) as session:
            try:
                # Build query with optional filters
                stmt = select(ConsentModel)

                conditions = []
                if parent_id:
                    conditions.append(ConsentModel.parent_id == parent_id)
                if consent_type:
                    conditions.append(ConsentModel.consent_type == consent_type)

                if conditions:
                    stmt = stmt.where(and_(*conditions))

                result = await session.execute(stmt)
                consents = result.scalars().all()

                # Filter by child_id if specified (stored in metadata)
                consent_statuses = []
                for consent in consents:
                    metadata = consent.verification_metadata or {}

                    # If child_id filter is specified, check metadata
                    if child_id and metadata.get("child_id") != child_id:
                        continue

                    # Check if consent is still valid
                    is_valid = (
                        consent.granted
                        and (
                            not consent.expires_at
                            or consent.expires_at > datetime.utcnow()
                        )
                        and not consent.revoked_at
                    )

                    consent_statuses.append(
                        {
                            "consent_id": consent.id,
                            "parent_id": consent.parent_id,
                            "child_id": metadata.get("child_id"),
                            "consent_type": consent.consent_type,
                            "granted": consent.granted,
                            "valid": is_valid,
                            "granted_at": (
                                consent.granted_at.isoformat()
                                if consent.granted_at
                                else None
                            ),
                            "expires_at": (
                                consent.expires_at.isoformat()
                                if consent.expires_at
                                else None
                            ),
                            "revoked_at": (
                                consent.revoked_at.isoformat()
                                if consent.revoked_at
                                else None
                            ),
                            "verification_method": consent.verification_method,
                            "data_types": metadata.get("data_types", []),
                        }
                    )

                logger.debug(f"Retrieved {len(consent_statuses)} consent records")
                return consent_statuses

            except Exception as e:
                logger.error(f"Failed to get consent status: {e}")
                raise SecurityError(f"Failed to get consent status: {e}")

    @database_input_validation("consents")
    async def cleanup_expired_consents(self) -> int:
        """Clean up expired consent records for compliance.

        Returns:
            Number of records cleaned up

        Raises:
            SecurityError: If validation fails
        """
        async with create_safe_database_session(self.database) as session:
            try:
                # Find expired consents
                stmt = select(ConsentModel).where(
                    and_(
                        ConsentModel.expires_at < datetime.utcnow(),
                        ConsentModel.revoked_at.is_(None),
                    )
                )

                result = await session.execute(stmt)
                expired_consents = result.scalars().all()

                # Mark as revoked (don't delete for audit purposes)
                count = 0
                for consent in expired_consents:
                    consent.revoked_at = datetime.utcnow()
                    consent.verification_metadata.update(
                        {
                            "auto_revoked": True,
                            "auto_revoked_reason": "expired",
                            "auto_revoked_at": datetime.utcnow().isoformat(),
                        }
                    )
                    count += 1

                await session.commit()

                logger.info(f"Auto-revoked {count} expired consent records")
                return count

            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to cleanup expired consents: {e}")
                raise SecurityError(f"Failed to cleanup expired consents: {e}")
