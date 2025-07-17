"""Parent / Guardian Models.

Enterprise-grade models for parent authentication and account management
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.models.base import Base


class ParentModel(Base):
    """Parent / Guardian model with comprehensive security features."""

    __tablename__ = "parents"

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Personal information
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))

    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Security tracking
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

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

    # COPPA compliance
    age_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Preferences
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Relationships
    children = relationship(
        "ChildModel",
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    consents = relationship(
        "ConsentModel",
        back_populates="parent",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "failed_login_attempts >= 0",
            name="check_failed_login_attempts_non_negative",
        ),
    )

    def __repr__(self) -> str:
        return f"<ParentModel(id={self.id}, email='{self.email}', is_active={self.is_active})>"
