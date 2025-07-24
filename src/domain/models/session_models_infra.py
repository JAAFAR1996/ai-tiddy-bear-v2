
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from src.domain.value_objects.session_status import SessionStatus
from src.infrastructure.persistence.models.base import Base


class Session(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True)
    child_id = Column(String, nullable=False)
    status = Column(String, default=SessionStatus.ACTIVE.value)
    created_at = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now(), onupdate=func.now())
    interaction_count = Column(Integer, default=0)
    ended_at = Column(DateTime, nullable=True)
    end_reason = Column(Text, nullable=True)
    session_data = Column(Text, nullable=True)  # Store JSON string of session data
