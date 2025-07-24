"""COPPA Consent and Safety Event Models.

Enterprise-grade models for child safety and compliance tracking
"""

import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.models.consent_models_domain import ConsentType
from src.infrastructure.persistence.models.base import Base


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
        default=lambda: str(uuid.uuid4()),
    )

    # Relationships
    parent_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("parents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Consent details
    consent_type: Mapped[ConsentType] = mapped_column(
        SQLEnum(ConsentType),
        nullable=False,
    )
    granted: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Tracking
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Verification
    verification_method: Mapped[str] = mapped_column(String(100), nullable=False)
    verification_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)

    __table_args__ = (Index("idx_consent_parent_type", "parent_id", "consent_type"),)

    def __repr__(self) -> str:
        return (
            f"<ConsentModel(id={self.id}, parent_id={self.parent_id}, "
            f"type='{self.consent_type.value}', granted={self.granted})>"
        )


class SafetyEventModel(Base):
    """Safety event logging model for monitoring and alerts."""

    __tablename__ = "safety_events"

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # Relationships
    child_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("children.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    conversation_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        index=True,
    )

    # Event details
    event_type: Mapped[SafetyEventType] = mapped_column(
        SQLEnum(SafetyEventType),
        nullable=False,
    )
    details: Mapped[str] = mapped_column(Text, nullable=False)
    event_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Tracking
    event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_safety_event_child_time", "child_id", "event_time"),
        Index("idx_safety_event_type", "event_type"),
    )

    def __repr__(self) -> str:
        return (
            f"<SafetyEventModel(id={self.id}, child_id={self.child_id}, "
            f"type='{self.event_type.value}')>"
        )
