from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import relationship

from src.domain.entities.conversation import Conversation
from src.infrastructure.persistence.database import Base

class ConversationModel(Base):
    """SQLAlchemy model for conversations."""

    __tablename__ = "conversations"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    child_id = Column(String(36), ForeignKey("children.id"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    summary = Column(String, nullable=False, default="")
    emotion_analysis = Column(String, nullable=False, default="neutral")
    sentiment_score = Column(Float, nullable=False, default=0.0)
    child = relationship("ChildModel", back_populates="conversations")

    @staticmethod
    def from_entity(entity: Conversation) -> "ConversationModel":
        """Convert domain entity to SQLAlchemy model."""
        return ConversationModel(
            id=str(entity.id),  # Convert UUID to string for SQLite compatibility
            child_id=str(entity.child_id),  # Convert UUID to string
            start_time=entity.start_time,
            end_time=entity.end_time,
            summary=entity.summary,
            emotion_analysis=entity.emotion_analysis,
            sentiment_score=entity.sentiment_score,
        )

    def to_entity(self) -> Conversation:
        """Convert SQLAlchemy model to domain entity."""
        return Conversation(
            id=UUID(self.id),  # Convert string back to UUID for domain entity
            child_id=UUID(self.child_id),  # Convert string back to UUID
            start_time=self.start_time,
            end_time=self.end_time,
            summary=self.summary,
            emotion_analysis=self.emotion_analysis,
            sentiment_score=self.sentiment_score,
        )
