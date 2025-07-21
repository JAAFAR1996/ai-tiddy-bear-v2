
from src.application.services.child_safety.verification_service import VerificationService
from src.application.services.user.relationship_manager import RelationshipManager
from src.domain.models.verification_models import (
    RelationshipRecord,
    RelationshipStatus,
    RelationshipType,
    VerificationRecord,
)
from src.application.services.user.verification_service import ParentChildVerificationService


# Re-export for backward compatibility
__all__ = [
    "ParentChildVerificationService",
    "RelationshipManager",
    "RelationshipRecord",
    "RelationshipStatus",
    "RelationshipType",
    "VerificationRecord",
]


def get_verification_service() -> ParentChildVerificationService:
    """Factory function to create a ParentChildVerificationService instance.

    Returns:
        A configured verification service instance.

    """
    return ParentChildVerificationService()


def get_relationship_manager() -> RelationshipManager:
    """Factory function to create a RelationshipManager instance.

    Returns:
        A configured relationship manager instance.

    """
    return RelationshipManager()
