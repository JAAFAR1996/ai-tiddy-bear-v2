"""Key rotation service interfaces and implementations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class KeyStorageInterface(ABC):
    """Interface for key storage."""

    @abstractmethod
    async def store_key(self, key_id: str, key_data: bytes) -> None:
        """Store encryption key."""

    @abstractmethod
    async def retrieve_key(self, key_id: str) -> Optional[bytes]:
        """Retrieve encryption key."""


class FileKeyStorage(KeyStorageInterface):
    """File-based key storage implementation."""

    def __init__(self, storage_path: str):
        self.storage_path = storage_path

    async def store_key(self, key_id: str, key_data: bytes) -> None:
        """Store key in file system."""
        # Implementation here

    async def retrieve_key(self, key_id: str) -> Optional[bytes]:
        """Retrieve key from file system."""
        # Implementation here
        return None


@dataclass
class RotationResult:
    """Result of key rotation operation."""

    success: bool
    old_key_id: str
    new_key_id: str
    timestamp: datetime
    error: Optional[str] = None
