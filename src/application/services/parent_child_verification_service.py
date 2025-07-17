"""
Provides services for parent-child verification and relationship management.

This module has been refactored into a clean, modular architecture.
The original functionality is preserved while improving maintainability and security.
It re-exports key classes and provides factory functions for convenience.

**Migration Note**: For new code, import from the 'verification' package:

```python
from src.application.services.verification import ParentChildVerificationService
```
"""

from .verification.relationship_manager import RelationshipManager
from .verification.verification_models import (
    RelationshipRecord,
    RelationshipStatus,
    RelationshipType,
    VerificationRecord,
)
from .verification.verification_service import ParentChildVerificationService

# Re-export for backward compatibility
__all__ = [
    "ParentChildVerificationService",
    "RelationshipManager",
    "RelationshipStatus",
    "RelationshipType",
    "VerificationRecord",
    "RelationshipRecord",
]


def get_verification_service() -> ParentChildVerificationService:
    """
    Factory function to create a ParentChildVerificationService instance.

    Returns:
        A configured verification service instance.
    """
    return ParentChildVerificationService()


def get_relationship_manager() -> RelationshipManager:
    """
    Factory function to create a RelationshipManager instance.

    Returns:
        A configured relationship manager instance.
    """
    return RelationshipManager()
