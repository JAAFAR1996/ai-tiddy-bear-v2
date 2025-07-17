"""Child Profile Models

Enterprise-grade models for child profiles with COPPA compliance
"""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import uuid
from sqlalchemy import (
    Column, String, DateTime, Boolean, Integer, Float,
    ForeignKey, Index, CheckConstraint, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.domain.value_objects.child_age import ChildAge
from src.domain.value_objects.safety_level import SafetyLevel
from src.infrastructure.persistence.models.base import Base

class ChildModel(Base):
    """Child profile model with COPPA compliance."""
    __tablename__ = "children"

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Relationship to parent
    parent_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("parents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Basic information (encrypted)
    name_encrypted: Mapped[str] = mapped_column(String(500), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    age_group: Mapped[ChildAge] = mapped_column(SQLEnum(ChildAge), nullable=False)

    # Preferences and interests
    interests: Mapped[list] = mapped_column(ARRAY(String), default=list)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    personality_traits: Mapped[dict] = mapped_column(JSONB, default=dict)
    learning_goals: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Safety settings
    safety_level: Mapped[SafetyLevel] = mapped_column(
        SQLEnum(SafetyLevel),
        default=SafetyLevel.HIGH,
        nullable=False
    )
    content_filters: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Usage tracking
    total_interactions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_interaction: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    parent = relationship("ParentModel", back_populates="children")
    conversations = relationship("ConversationModel", back_populates="child", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_child_parent_id", "parent_id"),
        CheckConstraint("age >= 0", name="check_age_non_negative"),
    )

    def __repr__(self) -> str:
        return f"<ChildModel(id={self.id}, parent_id={self.parent_id}, age_group='{self.age_group.value}')>"