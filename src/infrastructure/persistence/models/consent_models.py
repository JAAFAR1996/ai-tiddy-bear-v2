"""COPPA Consent and Safety Event Models

Enterprise-grade models for child safety and compliance tracking
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import uuid
from sqlalchemy import (
    Column, String, DateTime, Boolean, Integer,
    ForeignKey, Text, Index, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
import enum
from src.infrastructure.persistence.models.base import Base

class ConsentType(enum.Enum):
    """Types of parental consent."""
    DATA_COLLECTION = "data_collection"
    VOICE_RECORDING = "voice_recording"
    USAGE_ANALYTICS = "usage_analytics"
    MARKETING = "marketing"

class SafetyEventType(enum.Enum):
    """Types of safety events."""
    CONTENT_FILTERED = "content_filtered"
    INAPPROPRIATE_REQUEST = "inappropriate_request"
    EXCESSIVE_USAGE = "excessive_usage"
    PARENTAL_ALERT = "parental_alert"

class ConsentModel(Base):
    """Parental consent tracking model with COPPA compliance."""
    __tablename__ = "consents"

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Relationships
    parent_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("parents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Consent details
    consent_type: Mapped[ConsentType] = mapped_column(
        SQLEnum(ConsentType),
        nullable=False
    )
    granted: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Tracking
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Verification
    verification_method: Mapped[str] = mapped_column(String(100), nullable=False)
    verification_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)

    __table_args__ = (
        Index("idx_consent_parent_type", "parent_id", "consent_type"),
    )

    def __repr__(self) -> str:
        return f"<ConsentModel(id={self.id}, parent_id={self.parent_id}, type='{self.consent_type.value}', granted={self.granted})>"

class SafetyEventModel(Base):
    """Safety event logging model for monitoring and alerts."""
    __tablename__ = "safety_events"

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Relationships
    child_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("children.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    conversation_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        index=True
    )

    # Event details
    event_type: Mapped[SafetyEventType] = mapped_column(
        SQLEnum(SafetyEventType),
        nullable=False
    )
    details: Mapped[str] = mapped_column(Text, nullable=False)
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Tracking
    event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    __table_args__ = (
        Index("idx_safety_event_child_time", "child_id", "event_time"),
        Index("idx_safety_event_type", "event_type"),
    )

    def __repr__(self) -> str:
        return f"<SafetyEventModel(id={self.id}, child_id={self.child_id}, type='{self.event_type.value}')>"