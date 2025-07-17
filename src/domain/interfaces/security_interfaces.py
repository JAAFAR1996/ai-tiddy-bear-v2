"""Security-related interfaces for the domain layer.
These interfaces define contracts for security services without
creating dependencies on infrastructure implementations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from uuid import UUID


class IEncryptionService(ABC):
    """Interface for encryption operations."""

    @abstractmethod
    async def encrypt(self, data: str) -> str:
        """Encrypt sensitive data."""

    @abstractmethod
    async def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""

    @abstractmethod
    async def hash_password(self, password: str) -> str:
        """Hash a password securely."""

    @abstractmethod
    async def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""


class ISecurityService(ABC):
    """Interface for security validation and monitoring."""

    @abstractmethod
    async def validate_child_access(
        self, parent_id: UUID, child_id: UUID
    ) -> bool:
        """Validate that a parent has access to a child's data."""

    @abstractmethod
    async def log_security_event(
        self, event_type: str, data: Dict[str, Any]
    ) -> None:
        """Log a security-related event for audit purposes."""

    @abstractmethod
    async def validate_content_safety(self, content: str) -> Dict[str, Any]:
        """Validate content for child safety."""