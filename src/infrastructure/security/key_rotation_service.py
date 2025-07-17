"""Key Rotation Service

Provides automated and manual key rotation for enhanced security.
Implements secure key management with child safety compliance.
"""
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Protocol
import base64
import hashlib
import json
import logging
import secrets
import threading

from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__, component="security")

class KeyType(Enum):
    """Types of keys that can be rotated."""
    ENCRYPTION = "encryption"
    SIGNING = "signing"
    JWT = "jwt"
    SESSION = "session"
    DATABASE = "database"
    CHILD_DATA = "child_data"  # Special keys for child data encryption

class RotationTrigger(Enum):
    """Triggers that can initiate key rotation."""
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    SECURITY_INCIDENT = "security_incident"
    COMPLIANCE_REQUIREMENT = "compliance_requirement"
    AGE_LIMIT = "age_limit"

@dataclass
class KeyMetadata:
    """Metadata for encryption keys."""
    key_id: str
    key_type: KeyType
    created_at: datetime
    expires_at: Optional[datetime]
    algorithm: str
    key_size: int
    usage_count: int = 0
    last_used: Optional[datetime] = None
    is_active: bool = True
    rotation_trigger: Optional[RotationTrigger] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        if self.last_used:
            data['last_used'] = self.last_used.isoformat()
        # Convert enums to values
        data['key_type'] = self.key_type.value
        if self.rotation_trigger:
            data['rotation_trigger'] = self.rotation_trigger.value
        return data

@dataclass
class KeyRotationPolicy:
    """Policy for key rotation."""
    rotation_interval: timedelta = timedelta(days=90)
    max_key_age: timedelta = timedelta(days=180)
    auto_rotate: bool = True

class KeyStorage(Protocol):
    """Protocol for key storage backends."""
    def store_key(self, key_type: KeyType, key_id: str, key_data: Dict[str, Any]) -> None:
        ...
    def retrieve_key(self, key_type: KeyType, key_id: str) -> Optional[Dict[str, Any]]:
        ...
    def get_active_key_id(self, key_type: KeyType) -> Optional[str]:
        ...
    def set_active_key_id(self, key_type: KeyType, key_id: str) -> None:
        ...

class KeyRotationService:
    """Service for managing key rotation."""
    def __init__(self, policy: KeyRotationPolicy, storage: KeyStorage) -> None:
        self.policy = policy
        self.storage = storage
        self.rotation_lock = threading.Lock()

    def generate_key(self, key_type: KeyType, key_size: int = 256) -> Tuple[str, str]:
        """Generate a new key and key ID."""
        key = secrets.token_bytes(key_size // 8)
        key_id = hashlib.sha256(key).hexdigest()
        return key_id, base64.b64encode(key).decode('utf-8')

    def rotate_key(self, key_type: KeyType, trigger: RotationTrigger) -> None:
        """Rotate a key for a specific type."""
        with self.rotation_lock:
            logger.info(f"Rotating key for type {key_type.value} due to {trigger.value}")
            key_id, key_data_b64 = self.generate_key(key_type)
            metadata = KeyMetadata(
                key_id=key_id,
                key_type=key_type,
                created_at=datetime.now(),
                expires_at=datetime.now() + self.policy.rotation_interval,
                algorithm="AES-256-GCM",
                key_size=256,
                rotation_trigger=trigger
            )
            key_storage_data = {
                "key": key_data_b64,
                "metadata": metadata.to_dict()
            }
            self.storage.store_key(key_type, key_id, key_storage_data)
            self.storage.set_active_key_id(key_type, key_id)
            logger.info(f"Successfully rotated key for {key_type.value}. New key ID: {key_id}")

    def get_active_key(self, key_type: KeyType) -> Optional[Dict[str, Any]]:
        """Get the active key for a specific type."""
        active_key_id = self.storage.get_active_key_id(key_type)
        if not active_key_id:
            logger.warning(f"No active key found for {key_type.value}. Initiating rotation.")
            self.rotate_key(key_type, RotationTrigger.MANUAL)
            active_key_id = self.storage.get_active_key_id(key_type)
        return self.storage.retrieve_key(key_type, active_key_id)