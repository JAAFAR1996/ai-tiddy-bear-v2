"""Parent-Child Verification Package
Modular verification system for parent-child relationships with COPPA compliance.
"""

from .relationship_manager import RelationshipManager
from .verification_models import (
    RelationshipRecord,
    RelationshipStatus,
    RelationshipType,
    VerificationRecord,
)
from .verification_service import ParentChildVerificationService

__all__ = [
    "ParentChildVerificationService",
    "RelationshipManager",
    "RelationshipRecord",
    "RelationshipStatus",
    "RelationshipType",
    "VerificationRecord",
]
