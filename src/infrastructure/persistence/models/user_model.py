"""User Model for AI Teddy Bear Authentication System.

Production-grade SQLAlchemy model with comprehensive security features
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.types import JSON

from src.infrastructure.persistence.database import Base


class UserModel(Base):
    """SQLAlchemy model for user accounts with comprehensive security features."""

    __tablename__ = "users"

    # Primary identification
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # User information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)

    # Account status and security
    role = Column(String(50), nullable=False, default="parent")
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    phone_verified = Column(Boolean, default=False, nullable=False)

    # Security tracking
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    account_locked_until = Column(DateTime, nullable=True)
    last_password_change = Column(DateTime, default=datetime.utcnow)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Preferences and settings
    preferences = Column(JSON, nullable=False, default=dict)

    # COPPA and compliance
    date_of_birth = Column(DateTime, nullable=True)
    parental_consent_given = Column(Boolean, default=False, nullable=False)
    parental_consent_date = Column(DateTime, nullable=True)
    data_retention_preference = Column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email='{self.email}', role='{self.role}')>"
