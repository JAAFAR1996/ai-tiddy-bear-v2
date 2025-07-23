"""Child Profile Models.

Enterprise-grade models for child profiles with COPPA compliance
"""

import uuid
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

# استيراد الـ Types الصحيحة
from src.domain.value_objects.child_age import ChildAge, AgeCategory
from src.domain.value_objects.safety_level import SafetyLevel
from .base import Base


class ChildModel(Base):
    """Child profile model with COPPA compliance."""

    __tablename__ = "children"

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # Relationship to parent
    parent_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("parents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic information (encrypted)
    name_encrypted: Mapped[str] = mapped_column(String(500), nullable=False)
    age_years: Mapped[int] = mapped_column(Integer, nullable=False)
    age_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ✅ استخدام AgeCategory (وهو Enum) بدلاً من ChildAge (وهو dataclass)
    age_category: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Age category: toddler, preschool, early_child, middle_child, preteen"
    )

    # Preferences and interests
    interests: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    personality_traits: Mapped[dict] = mapped_column(JSONB, default=dict)
    learning_goals: Mapped[dict] = mapped_column(JSONB, default=dict)

    # ✅ Safety settings - SafetyLevel كـ string
    safety_level: Mapped[str] = mapped_column(
        String(20),
        default=SafetyLevel.HIGH.value,
        nullable=False,
        comment="Safety level: none, low, strict, moderate, relaxed, high, critical"
    )
    content_filters: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Usage tracking
    total_interactions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_interaction: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    parent = relationship("ParentModel", back_populates="children")
    conversations = relationship(
        "ConversationModel",
        back_populates="child",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_child_parent_id", "parent_id"),
        Index("idx_child_age_category", "age_category"),
        Index("idx_child_safety_level", "safety_level"),
        CheckConstraint("age_years >= 2", name="check_age_min"),
        CheckConstraint("age_years <= 13", name="check_age_max"),
        CheckConstraint("age_months >= 0", name="check_months_min"),
        CheckConstraint("age_months <= 11", name="check_months_max"),
        CheckConstraint(
            "age_category IN ('toddler', 'preschool', 'early_child', 'middle_child', 'preteen')",
            name="check_valid_age_category"
        ),
        CheckConstraint(
            "safety_level IN ('none', 'low', 'strict', 'moderate', 'relaxed', 'high', 'critical')",
            name="check_valid_safety_level"
        ),
    )

    # ✅ Properties للتحويل بين database values والـ domain objects
    @property
    def child_age(self) -> ChildAge:
        """Get ChildAge domain object."""
        return ChildAge(years=self.age_years, months=self.age_months)

    @child_age.setter
    def child_age(self, value: ChildAge) -> None:
        """Set age from ChildAge domain object."""
        self.age_years = value.years
        self.age_months = value.months
        self.age_category = value.category.value  # تحديث الـ category تلقائياً

    @property
    def age_category_enum(self) -> AgeCategory:
        """Get age_category as enum."""
        return AgeCategory(self.age_category)

    @age_category_enum.setter
    def age_category_enum(self, value: AgeCategory) -> None:
        """Set age_category from enum."""
        self.age_category = value.value

    @property
    def safety_level_enum(self) -> SafetyLevel:
        """Get safety_level as enum."""
        return SafetyLevel(self.safety_level)

    @safety_level_enum.setter
    def safety_level_enum(self, value: SafetyLevel) -> None:
        """Set safety_level from enum."""
        self.safety_level = value.value

    # ✅ Helper methods للتكامل مع domain layer
    def get_interaction_guidelines(self) -> dict[str, str]:
        """Get age-appropriate interaction guidelines."""
        return self.child_age.get_interaction_guidelines()

    def get_recommended_topics(self) -> list[str]:
        """Get age-appropriate topic recommendations."""
        return self.child_age.recommended_topics

    def get_safety_restrictions(self) -> dict[str, bool]:
        """Get safety restrictions."""
        return self.child_age.safety_restrictions

    def is_appropriate_for_content(self, content_age_rating: int) -> bool:
        """Check if content is appropriate for this age."""
        return self.child_age.is_appropriate_for_content(content_age_rating)

    def __repr__(self) -> str:
        return f"<ChildModel(id={self.id}, age={self.age_years}, category='{self.age_category}', safety='{self.safety_level}')>"
