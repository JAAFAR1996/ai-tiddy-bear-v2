"""Conversation and Message Models.

Enterprise-grade models for conversation tracking and analysis
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.models.base import Base


class ConversationModel(Base):
    """Conversation model with comprehensive tracking and analysis."""

    __tablename__ = "conversations"

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

    # Session information
    session_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    conversation_type: Mapped[str] = mapped_column(String(20), default="chat")

    # Timing
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[int | None] = mapped_column(Integer)

    # Content summary
    summary: Mapped[str] = mapped_column(Text, default="")
    message_count: Mapped[int] = mapped_column(Integer, default=0)

    # AI Analysis
    emotion_analysis: Mapped[str] = mapped_column(String(50), default="neutral")
    sentiment_score: Mapped[float] = mapped_column(Float, default=0.0)
    engagement_level: Mapped[str] = mapped_column(String(20), default="medium")

    # Safety metrics
    safety_flags: Mapped[int] = mapped_column(Integer, default=0)
    content_warnings: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Relationships
    child = relationship("ChildModel", back_populates="conversations")
    messages = relationship(
        "MessageModel",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_conversation_child_id", "child_id"),
        Index("idx_conversation_session_id", "session_id"),
    )

    def __repr__(self) -> str:
        return f"<ConversationModel(id={self.id}, child_id={self.child_id}, start_time={self.start_time})>"


class MessageModel(Base):
    """Message model for individual messages within a conversation."""

    __tablename__ = "messages"

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # Relationships
    conversation_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Message content
    sender: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )  # "child" or "teddy"
    content_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(20), default="text")

    # Timing
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # AI Analysis
    emotion: Mapped[str] = mapped_column(String(50), default="neutral")
    sentiment: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationships
    conversation = relationship("ConversationModel", back_populates="messages")

    __table_args__ = (
        Index("idx_message_conversation_id", "conversation_id"),
        Index("idx_message_timestamp", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<MessageModel(id={self.id}, conversation_id={self.conversation_id}, sender='{self.sender}')>"
