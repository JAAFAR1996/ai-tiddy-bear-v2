import json
import logging
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Integer, String, Text

from src.domain.entities.child_profile import ChildProfile
from src.infrastructure.persistence.database import Base
from src.infrastructure.security.encryption_service import (
    EncryptionKeyError,
    get_encryption_service,
)

logger = logging.getLogger(__name__)

class ChildModel(Base):
    """All PII is encrypted at rest for COPPA compliance."""

    __tablename__ = "children"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    # Store encrypted data as Text for better compatibility
    encrypted_name = Column(
        Text, nullable=False
    )  # Base64 encoded encrypted name
    encrypted_preferences = Column(
        Text,
        nullable=False,
    )  # Base64 encoded encrypted preferences
    age = Column(
        Integer, nullable=False
    )  # Age can be stored as range for COPPA
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    # Track encryption key version for rotation support
    encryption_key_version = Column(String(50), nullable=True)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._encryption_service = get_encryption_service()

    @property
    def name(self) -> str:
        """Decrypt and return child name with proper error handling."""
        if self.encrypted_name:
            try:
                decrypted = self._encryption_service.decrypt(
                    self.encrypted_name
                )
                return (
                    decrypted
                    if isinstance(decrypted, str)
                    else decrypted.decode("utf-8")
                )
            except EncryptionKeyError as e:
                logger.error(f"Failed to decrypt child name: {e!s}")
                return "[Name Decryption Failed]"
        return ""

    @name.setter
    def name(self, value: str) -> None:
        """Encrypt and set child name."""
        self.encrypted_name = self._encryption_service.encrypt(value)

    @property
    def preferences(self) -> dict[str, Any]:
        """Decrypt and return child preferences with proper error handling."""
        if self.encrypted_preferences:
            try:
                decrypted_json = self._encryption_service.decrypt(
                    self.encrypted_preferences,
                )
                return json.loads(decrypted_json)
            except (json.JSONDecodeError, EncryptionKeyError) as e:
                logger.error(f"Failed to decrypt/decode preferences: {e!s}")
                return {}
        return {}

    @preferences.setter
    def preferences(self, value: dict[str, Any]) -> None:
        """Encrypt and set child preferences."""
        self.encrypted_preferences = self._encryption_service.encrypt(
            json.dumps(value)
        )

    @staticmethod
    def from_entity(entity: ChildProfile) -> "ChildModel":
        """Convert domain entity to SQLAlchemy model."""
        child_model = ChildModel(
            id=str(entity.id),
            age=entity.age,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
        child_model.name = entity.name
        child_model.preferences = entity.preferences
        return child_model

    def to_entity(self) -> ChildProfile:
        """Convert SQLAlchemy model to domain entity."""
        return ChildProfile(
            id=UUID(self.id),
            name=self.name,
            age=self.age,
            preferences=self.preferences,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
