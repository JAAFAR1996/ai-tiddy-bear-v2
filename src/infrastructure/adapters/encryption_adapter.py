"""Encryption Service Adapter
Implements the domain encryption interface using infrastructure encryption services,
maintaining Hexagonal Architecture separation of concerns.
"""

from src.domain.interfaces.encryption_interface import (
    EncryptionServiceInterface,
)


class InfrastructureEncryptionAdapter(EncryptionServiceInterface):
    """Adapter that implements domain encryption interface using infrastructure services.
    This adapter allows the domain layer to use encryption without coupling
    to specific infrastructure implementations.
    """

    def __init__(self) -> None:
        """Initialize adapter with lazy loading of infrastructure service."""
        self._service = None
        self._initialized = False

    def _get_service(self):
        """Lazy load the infrastructure encryption service."""
        if not self._initialized:
            try:
                from src.infrastructure.security.encryption.robust_encryption_service import (
                    get_encryption_service,
                )

                self._service = get_encryption_service()
                self._initialized = True
            except ImportError:
                # Infrastructure service not available
                self._service = None
                self._initialized = True
        return self._service

    def encrypt(self, data: str) -> str:
        """Encrypt data using infrastructure service."""
        service = self._get_service()
        if service:
            return service.encrypt(data)
        # Fallback: return data as-is if encryption not available
        return data

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data using infrastructure service."""
        service = self._get_service()
        if service:
            return service.decrypt(encrypted_data)
        # Fallback: return data as-is if decryption not available
        return encrypted_data

    def is_available(self) -> bool:
        """Check if infrastructure encryption service is available."""
        service = self._get_service()
        return service is not None and hasattr(service, "encrypt")


# Global adapter instance
_encryption_adapter: InfrastructureEncryptionAdapter | None = None


def get_encryption_adapter() -> InfrastructureEncryptionAdapter:
    """Get or create global encryption adapter instance."""
    global _encryption_adapter
    if _encryption_adapter is None:
        _encryption_adapter = InfrastructureEncryptionAdapter()
    return _encryption_adapter
