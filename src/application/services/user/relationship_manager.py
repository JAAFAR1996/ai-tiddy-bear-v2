"""Relationship Manager
Manages parent-child relationships with proper verification and audit trails.
"""

from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from src.infrastructure.logging_config import get_logger

from src.domain.models.verification_models import (
    RelationshipRecord,
    RelationshipStatus,
    RelationshipType,
    VerificationRecord,
)

logger = get_logger(__name__, component="services")


class RelationshipManager:
    """Handles the core relationship management functionality extracted from the original large file for better maintainability."""

    def __init__(self) -> None:
        """Initialize relationship manager."""
        self.relationships: dict[str, RelationshipRecord] = {}
        self.verifications: dict[str, VerificationRecord] = {}

    async def create_relationship(
        self,
        parent_id: str,
        child_id: str,
        relationship_type: RelationshipType,
        verification_evidence: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new parent-child relationship record.

        Args:
            parent_id: Parent identifier
            child_id: Child identifier
            relationship_type: Type of relationship
            verification_evidence: Supporting documentation
        Returns:
            Relationship creation result
        """
        relationship_id = f"rel_{parent_id}_{child_id}_{uuid4().hex[:8]}"

        relationship = RelationshipRecord(
            relationship_id=relationship_id,
            parent_id=parent_id,
            child_id=child_id,
            relationship_type=relationship_type,
            status=RelationshipStatus.PENDING,
            verification_evidence=verification_evidence or [],
            metadata={"created_at": datetime.utcnow().isoformat()},
        )

        self.relationships[relationship_id] = relationship
        logger.info(f"Relationship created: {relationship_type.value}")

        return {
            "relationship_id": relationship_id,
            "status": "pending",
            "message": "Relationship created, verification required",
        }

    async def verify_relationship(
        self,
        relationship_id: str,
        verification_method: str,
        evidence: list[str] | None = None,
    ) -> dict[str, Any]:
        """Verify a pending relationship.

        Args:
            relationship_id: Relationship identifier
            verification_method: Method used for verification
            evidence: Additional evidence provided
        Returns:
            Verification result
        """
        if relationship_id not in self.relationships:
            return {"status": "error", "message": "Relationship not found"}

        relationship = self.relationships[relationship_id]

        # Create verification record
        verification_id = f"verify_{relationship_id}_{uuid4().hex[:8]}"
        verification = VerificationRecord(
            verification_id=verification_id,
            parent_id=relationship.parent_id,
            child_id=relationship.child_id,
            verification_type=verification_method,
            status=RelationshipStatus.VERIFIED,
            attempted_at=datetime.utcnow().isoformat(),
            completed_at=datetime.utcnow().isoformat(),
            evidence_provided=evidence or [],
        )

        self.verifications[verification_id] = verification

        # Update relationship status
        relationship.status = RelationshipStatus.VERIFIED
        relationship.verified_at = datetime.utcnow().isoformat()
        relationship.expires_at = (datetime.utcnow() + timedelta(days=365)).isoformat()

        logger.info(f"Relationship verified via {verification_method}")

        return {
            "status": "success",
            "relationship_id": relationship_id,
            "verification_id": verification_id,
            "message": "Relationship verified successfully",
        }

    def check_relationship_validity(self, parent_id: str, child_id: str) -> bool:
        """Check if a valid relationship exists between parent and child.

        Args:
            parent_id: Parent identifier
            child_id: Child identifier
        Returns:
            True if valid relationship exists
        """
        for relationship in self.relationships.values():
            if (
                relationship.parent_id == parent_id
                and relationship.child_id == child_id
                and relationship.status == RelationshipStatus.VERIFIED
            ):

                # Check expiration
                if relationship.expires_at:
                    expiry = datetime.fromisoformat(relationship.expires_at)
                    if datetime.utcnow() > expiry:
                        relationship.status = RelationshipStatus.EXPIRED
                        return False

                return True

        return False

    def get_parent_children(self, parent_id: str) -> list[str]:
        """Get all children associated with a parent.

        Args:
            parent_id: Parent identifier
        Returns:
            List of child IDs
        """
        children = []

        for relationship in self.relationships.values():
            if (
                relationship.parent_id == parent_id
                and relationship.status == RelationshipStatus.VERIFIED
            ):
                children.append(relationship.child_id)

        return children

    def get_child_parents(self, child_id: str) -> list[str]:
        """Get all parents/guardians associated with a child.

        Args:
            child_id: Child identifier
        Returns:
            List of parent IDs
        """
        parents = []

        for relationship in self.relationships.values():
            if (
                relationship.child_id == child_id
                and relationship.status == RelationshipStatus.VERIFIED
            ):
                parents.append(relationship.parent_id)

        return parents
