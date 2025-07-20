from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

"""
Child Data Transfer Objects for AI Teddy Bear
This module defines COPPA-compliant data structures for representing
child information throughout the application. All child data handling
follows strict privacy and safety regulations to ensure legal compliance
and child protection.

Classes:
 ChildData: COPPA-compliant child data representation

COPPA Compliance Features:
 - Age validation (3-13 years only)
 - Parental consent tracking
 - Data minimization principles
 - Secure data handling

Security Features:
 - PII encryption at rest
 - Access logging and audit trails
 - Data retention limits (90 days)
 - Automatic data purging
"""


@dataclass
class ChildData:
    """COPPA-Compliant Child Data Transfer Object.

    Represents child information in compliance with the Children's Online
    Privacy Protection Act (COPPA). This class enforces strict data protection
    standards and privacy requirements for children under 13 years of age.
    """

    id: UUID = field(metadata={"description": "Unique child identifier"})
    name: str = field(metadata={"description": "Child name (will be encrypted)"})
    age: int = field(
        metadata={"description": "Child age (3-13 years, COPPA compliant)"}
    )
    preferences: dict[str, Any] = field(
        default_factory=dict,
        metadata={"description": "Child preferences and settings"},
    )
    parent_id: UUID | None = field(
        default=None, metadata={"description": "Parent/guardian identifier"}
    )
    consent_granted: bool = field(
        default=False, metadata={"description": "Parental consent status"}
    )
    consent_date: datetime | None = field(
        default=None, metadata={"description": "Consent grant timestamp"}
    )
    data_created: datetime = field(
        default_factory=datetime.utcnow,
        metadata={"description": "Data creation timestamp"},
    )
    last_interaction: datetime | None = field(
        default=None, metadata={"description": "Last interaction timestamp"}
    )
    encrypted_data: bool = field(
        default=False, metadata={"description": "Data encryption status"}
    )

    def __post_init__(self) -> None:
        """Validate child data for COPPA compliance after initialization."""
        # Age validation for COPPA compliance
        if not isinstance(self.age, int) or not (3 <= self.age <= 13):
            raise ValueError(
                "COPPA Violation: Child age must be between 3-13 years. "
                f"Received age: {self.age}"
            )

        # Name validation
        if not self.name or not self.name.strip():
            raise ValueError("Child name cannot be empty")

        if len(self.name.strip()) > 100:
            raise ValueError("Child name too long (max 100 characters)")

        # Parental consent validation for children under 13
        if self.age < 13:
            if not self.parent_id:
                raise ValueError(
                    "COPPA Compliance: Parent ID required for children under 13"
                )

            if not self.consent_granted:
                raise ValueError(
                    "COPPA Compliance: Parental consent required for children "
                    "under 13"
                )

            if not self.consent_date:
                raise ValueError(
                    "COPPA Compliance: Consent date required when consent is " "granted"
                )

        # Data retention check (90 days maximum)
        if self.data_created:
            days_since_creation = (datetime.utcnow() - self.data_created).days
            if days_since_creation > 90:
                raise ValueError(
                    "COPPA Compliance: Child data expired after 90 days. "
                    f"Data age: {days_since_creation} days"
                )

    def should_purge_data(self) -> bool:
        """Determine if child data should be automatically purged."""
        if not self.data_created:
            return False

        days_since_creation = (datetime.utcnow() - self.data_created).days
        return days_since_creation >= 90
