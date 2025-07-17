"""Domain Encryption Interface
Defines the contract for encryption services without depending on
infrastructure implementations, maintaining Hexagonal Architecture principles.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class EncryptionServiceInterface(ABC):
    """Abstract interface for encryption services.
    This interface allows the domain layer to use encryption functionality
    without coupling to specific infrastructure implementations.
    """

    @abstractmethod
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data.

        Args:
            data: Plain text data to encrypt

        Returns:
            Encrypted data as string

        """

    @abstractmethod
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt encrypted data.

        Args:
            encrypted_data: Encrypted data to decrypt

        Returns:
            Decrypted plain text data

        """

    @abstractmethod
    def is_available(self) -> bool:
        """Check if encryption service is available.

        Returns:
            True if encryption is available, False otherwise

        """


class SecureFieldInterface(Generic[T], ABC):
    """Interface for encrypted field value objects.
    Provides a domain-level abstraction for encrypted fields that can
    be implemented with various encryption strategies.
    """

    @abstractmethod
    def get_value(self) -> T:
        """Get the decrypted value.

        Returns:
            The decrypted value

        """

    @abstractmethod
    def is_encrypted(self) -> bool:
        """Check if the field contains encrypted data.

        Returns:
            True if data is encrypted, False otherwise

        """

    @abstractmethod
    def get_encrypted_representation(self) -> str:
        """Get the encrypted representation for persistence.

        Returns:
            Encrypted data suitable for storage

        """


class NullEncryptionService(EncryptionServiceInterface):
    """Null object implementation for when encryption is not available.
    This prevents the domain from breaking when infrastructure
    services are unavailable during testing or initialization.
    """

    def encrypt(self, data: str) -> str:
        """Return data as-is (no encryption)."""
        return data

    def decrypt(self, encrypted_data: str) -> str:
        """Return data as-is (no decryption)."""
        return encrypted_data

    def is_available(self) -> bool:
        """Always returns False as this is a null implementation."""
        return False


class SecureString(SecureFieldInterface[str]):
    """Domain-safe encrypted string implementation.
    This value object encapsulates encryption concerns while providing
    a clean domain interface for working with sensitive strings.
    """

    def __init__(
        self, value: str, encryption_service: EncryptionServiceInterface
    ):
        """Initialize secure string.

        Args:
            value: The string value to secure
            encryption_service: Service to handle encryption

        """
        self._encryption_service = encryption_service
        self._encrypted_value = encryption_service.encrypt(value)
        self._is_encrypted = encryption_service.is_available()

    def get_value(self) -> str:
        """Get the decrypted string value."""
        if self._is_encrypted:
            return self._encryption_service.decrypt(self._encrypted_value)
        return self._encrypted_value

    def is_encrypted(self) -> bool:
        """Check if the string is encrypted."""
        return self._is_encrypted

    def get_encrypted_representation(self) -> str:
        """Get encrypted representation for storage."""
        return self._encrypted_value

    def __eq__(self, other) -> bool:
        """Compare secure strings by their decrypted values."""
        if isinstance(other, SecureString):
            return self.get_value() == other.get_value()
        if isinstance(other, str):
            return self.get_value() == other
        return False

    def __str__(self) -> str:
        """Safe string representation that doesn't expose the value."""
        return f"SecureString(encrypted={self.is_encrypted()})"

    def __repr__(self) -> str:
        """Safe representation that doesn't expose the value."""
        return f"SecureString(encrypted={self.is_encrypted()})"
