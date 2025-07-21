"""Verification Data Models
Defines core data structures for parent-child relationship verification.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class RelationshipStatus(Enum):
    """Parent-child relationship verification status."""

    VERIFIED = "verified"
    PENDING = "pending"
    DENIED = "denied"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class RelationshipType(Enum):
    """Types of parent-child relationships."""

    BIOLOGICAL_PARENT = "biological_parent"
    ADOPTIVE_PARENT = "adoptive_parent"
    LEGAL_GUARDIAN = "legal_guardian"
    CUSTODIAL_PARENT = "custodial_parent"


@dataclass
class VerificationRecord:
    """Individual verification attempt record."""

    verification_id: str
    parent_id: str
    child_id: str
    verification_type: str
    status: RelationshipStatus
    attempted_at: str
    completed_at: str | None = None
    evidence_provided: list[str] | None = None
    notes: str | None = None


@dataclass
class RelationshipRecord:
    """Parent-child relationship record."""

    relationship_id: str
    parent_id: str
    child_id: str
    relationship_type: RelationshipType
    status: RelationshipStatus
    verified_at: str | None = None
    expires_at: str | None = None
    verification_evidence: list[str] | None = None
    emergency_contact: bool = False
    metadata: dict[str, Any] | None = None
