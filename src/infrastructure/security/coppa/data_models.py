"""COPPA Data Models and Validation
Enterprise-grade COPPA data models with comprehensive validation.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from src.domain.constants import COPPA_AGE_THRESHOLD, MINIMUM_CHILD_AGE


class ChildData(BaseModel):
    """Production child data model with comprehensive validation."""

    child_id: str = Field(..., description="Unique child identifier")
    name: str = Field(
        ..., min_length=1, max_length=50, description="Child's name"
    )
    age: int = Field(..., ge=1, le=13, description="Child's age (COPPA limit)")
    date_of_birth: datetime | None = Field(
        None,
        description="Date of birth for precise age calculation",
    )
    parent_id: str = Field(..., description="Parent/guardian identifier")
    parent_consent: bool = Field(
        default=False, description="Parental consent status"
    )
    consent_date: datetime | None = Field(
        None, description="Date consent was given"
    )
    consent_type: str = Field(
        default="explicit",
        description="Type of consent obtained",
    )

    # Data collection permissions
    data_collection_consent: bool = Field(
        default=False,
        description="Consent for data collection",
    )
    voice_recording_consent: bool = Field(
        default=False,
        description="Consent for voice recording",
    )
    usage_analytics_consent: bool = Field(
        default=False,
        description="Consent for usage analytics",
    )
    marketing_consent: bool = Field(
        default=False,
        description="Consent for marketing communications",
    )

    # Data retention settings
    data_retention_days: int = Field(
        default=90,
        ge=1,
        le=365,
        description="Data retention period in days",
    )
    scheduled_deletion: datetime | None = Field(
        None,
        description="Scheduled deletion date",
    )

    # Privacy and security settings
    privacy_level: str = Field(
        default="strict", description="Privacy protection level"
    )
    location_tracking: bool = Field(
        default=False,
        description="Location tracking permission",
    )
    third_party_sharing: bool = Field(
        default=False,
        description="Third-party data sharing permission",
    )

    # Audit trail
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp",
    )

    @field_validator("age")
    @classmethod
    def validate_coppa_age(cls, v: int) -> int:
        """Validate age compliance with COPPA."""
        if v < MINIMUM_CHILD_AGE:
            raise ValueError(f"Age must be at least {MINIMUM_CHILD_AGE} years")
        if v > COPPA_AGE_THRESHOLD:
            raise ValueError(
                f"COPPA applies to children under {COPPA_AGE_THRESHOLD}"
            )
        return v

    @field_validator("consent_date")
    @classmethod
    def validate_consent_date(
        cls, v: datetime | None, info
    ) -> datetime | None:
        """Validate consent date is not in the future."""
        if v and v > datetime.utcnow():
            raise ValueError("Consent date cannot be in the future")
        return v


class ParentConsent(BaseModel):
    """Parent consent record with detailed tracking."""

    consent_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique consent ID",
    )
    parent_id: str = Field(..., description="Parent identifier")
    child_id: str = Field(..., description="Child identifier")

    # Consent details
    consent_type: str = Field(
        ...,
        description="Type of consent (data_collection, voice_recording, etc.)",
    )
    granted: bool = Field(..., description="Whether consent was granted")
    consent_text: str = Field(..., description="Full text of consent request")

    # Verification details
    verification_method: str = Field(
        ...,
        description="How consent was verified (email, sms, etc.)",
    )
    ip_address: str = Field(
        ..., description="IP address where consent was given"
    )
    user_agent: str = Field(..., description="Browser/device user agent")

    # Timing
    granted_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When consent was granted",
    )
    expires_at: datetime | None = Field(
        None, description="When consent expires"
    )
    revoked_at: datetime | None = Field(
        None, description="When consent was revoked"
    )

    # Audit trail
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DataRetentionPolicy(BaseModel):
    """Data retention policy configuration."""

    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    child_id: str = Field(..., description="Child this policy applies to")

    # Retention settings
    retention_period_days: int = Field(default=90, ge=1, le=365)
    auto_delete_enabled: bool = Field(default=True)
    deletion_scheduled_date: datetime | None = Field(None)

    # Data types and retention
    conversation_data_days: int = Field(default=90)
    voice_data_days: int = Field(default=30)
    analytics_data_days: int = Field(default=180)
    log_data_days: int = Field(default=365)

    # Compliance settings
    coppa_compliance_mode: bool = Field(default=True)
    gdpr_compliance_mode: bool = Field(default=True)
    california_ccpa_mode: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLogEntry(BaseModel):
    """Comprehensive audit log entry for compliance tracking."""

    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Event details
    event_type: str = Field(
        ...,
        description="Type of event (data_access, consent_change, etc.)",
    )
    event_description: str = Field(
        ..., description="Detailed description of the event"
    )

    # Actor information
    actor_type: str = Field(
        ...,
        description="Who performed the action (user, system, admin)",
    )
    actor_id: str | None = Field(None, description="ID of the actor")

    # Target information
    target_type: str = Field(
        ...,
        description="What was affected (child_data, consent, etc.)",
    )
    target_id: str = Field(..., description="ID of the affected resource")

    # Context
    ip_address: str | None = Field(
        None, description="IP address of the request"
    )
    user_agent: str | None = Field(None, description="User agent string")
    session_id: str | None = Field(None, description="Session identifier")

    # Compliance flags
    coppa_relevant: bool = Field(
        default=True,
        description="Whether this event is relevant for COPPA compliance",
    )
    gdpr_relevant: bool = Field(
        default=False,
        description="Whether this event is relevant for GDPR compliance",
    )

    # Additional metadata
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional event metadata",
    )


class DataDeletionRequest(BaseModel):
    """Data deletion request for COPPA compliance."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    child_id: str = Field(
        ..., description="Child whose data should be deleted"
    )
    parent_id: str = Field(..., description="Parent requesting deletion")

    # Request details
    deletion_type: str = Field(
        ...,
        description="Type of deletion (full, partial, specific)",
    )
    data_types: list[str] = Field(
        default_factory=list,
        description="Specific data types to delete",
    )
    reason: str = Field(..., description="Reason for deletion request")

    # Timing
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    scheduled_for: datetime | None = Field(
        None,
        description="When deletion should occur",
    )
    completed_at: datetime | None = Field(
        None,
        description="When deletion was completed",
    )

    # Status tracking
    status: str = Field(
        default="pending", description="Status of deletion request"
    )
    verification_required: bool = Field(
        default=True,
        description="Whether parent verification is required",
    )
    verified_at: datetime | None = Field(
        None,
        description="When parent verification was completed",
    )

    # Audit
    processed_by: str | None = Field(
        None,
        description="System component that processed the request",
    )
    processing_notes: str | None = Field(
        None, description="Notes about the processing"
    )


# Export all models
__all__ = [
    "AuditLogEntry",
    "ChildData",
    "DataDeletionRequest",
    "DataRetentionPolicy",
    "ParentConsent",
]
