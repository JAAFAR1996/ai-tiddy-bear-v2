from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional


class IEncryptionService(ABC):
    @abstractmethod
    async def encrypt_child_data(self, data: str) -> str:
        """Encrypt child data"""
        pass

    @abstractmethod
    async def decrypt_child_data(self, encrypted_data: str) -> str:
        """Decrypt child data"""
        pass

    @abstractmethod
    async def rotate_keys(self) -> bool:
        """Rotate encryption keys"""
        pass


class IDataRetentionService(ABC):
    @abstractmethod
    async def schedule_deletion(self, child_id: str, retention_days: int) -> None:
        """Schedule data for deletion"""
        pass

    @abstractmethod
    async def export_child_data(self, child_id: str) -> str:
        """Export child data for parent"""
        pass

    @abstractmethod
    async def delete_expired_data(self) -> List[str]:
        """Delete expired data and return deleted IDs"""
        pass


class IParentVerificationService(ABC):
    @abstractmethod
    async def verify_parent_identity(self, parent_id: str, verification_method: str, verification_data: Dict[str, Any]) -> bool:
        """Verify parent identity using specified method"""
        pass

    @abstractmethod
    async def get_verification_methods(self) -> List[str]:
        """Get available verification methods"""
        pass


class IAuditLogger(ABC):
    @abstractmethod
    async def log_child_access(
        self,
        parent_id: str,
        child_id: str,
        action: str,
        ip_address: str,
        success: bool
    ) -> None:
        """Log child data access"""
        pass

    @abstractmethod
    async def log_consent_change(
        self,
        parent_id: str,
        child_id: str,
        consent_type: str,
        action: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Log consent changes"""
        pass


class IAccessControlService(ABC):
    @abstractmethod
    async def verify_parent_child_access(self, parent_id: str, child_id: str, operation: str) -> bool:
        """Verify parent has access to child"""
        pass

    @abstractmethod
    async def get_parent_children(self, parent_id: str) -> List[str]:
        """Get children accessible by parent"""
        pass


class IContentFilterService(ABC):
    @abstractmethod
    async def filter_content(
        self,
        content: str,
        child_age: int,
        context: str = "general"
    ) -> Dict[str, Any]:
        """Filter content for child safety"""
        pass

    @abstractmethod
    async def validate_topic(self, topic: str, child_id: str) -> bool:
        """Validate if topic is appropriate"""
        pass


class IEmailService(ABC):
    @abstractmethod
    async def send_email(self, to: str, subject: str, template: str, context: Dict[str, Any]) -> bool:
        """Send templated email"""
        pass

    @abstractmethod
    async def send_deletion_warning(self, parent_email: str, child_name: str, deletion_date: str, export_url: str) -> bool:
        """Send data deletion warning"""
        pass


class ISettingsProvider(ABC):
    @abstractmethod
    def get_database_url(self) -> str:
        """Get database URL"""
        pass

    @abstractmethod
    def get_encryption_key(self) -> str:
        """Get encryption key"""
        pass

    @abstractmethod
    def get_coppa_settings(self) -> Dict[str, Any]:
        """Get COPPA compliance settings"""
        pass

    @abstractmethod
    def is_production(self) -> bool:
        """Check if running in production"""
        pass


class IEventBus(ABC):
    @abstractmethod
    async def publish_event(self, event_name: str, data: Dict[str, Any]) -> None:
        """Publish domain event"""
        pass

    @abstractmethod
    async def subscribe_to_events(self, event_names: List[str], handler: Any) -> None:
        """Subscribe to domain events"""
        pass
