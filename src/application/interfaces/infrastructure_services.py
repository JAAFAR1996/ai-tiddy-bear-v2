from abc import ABC, abstractmethod
from typing import Any


class IDataRetentionService(ABC):
    @abstractmethod
    async def schedule_deletion(self, child_id: str, retention_days: int) -> None:
        """Schedule data for deletion"""

    @abstractmethod
    async def export_child_data(self, child_id: str) -> str:
        """Export child data for parent"""

    @abstractmethod
    async def delete_expired_data(self) -> list[str]:
        """Delete expired data and return deleted IDs"""


class IParentVerificationService(ABC):
    @abstractmethod
    async def verify_parent_identity(
        self,
        parent_id: str,
        verification_method: str,
        verification_data: dict[str, Any],
    ) -> bool:
        """Verify parent identity using specified method"""

    @abstractmethod
    async def get_verification_methods(self) -> list[str]:
        """Get available verification methods"""


class IAuditLogger(ABC):
    @abstractmethod
    async def log_child_access(
        self, parent_id: str, child_id: str, action: str, ip_address: str, success: bool
    ) -> None:
        """Log child data access"""

    @abstractmethod
    async def log_consent_change(
        self,
        parent_id: str,
        child_id: str,
        consent_type: str,
        action: str,
        metadata: dict[str, Any],
    ) -> None:
        """Log consent changes"""


class IAccessControlService(ABC):
    @abstractmethod
    async def verify_parent_child_access(
        self, parent_id: str, child_id: str, operation: str
    ) -> bool:
        """Verify parent has access to child"""

    @abstractmethod
    async def get_parent_children(self, parent_id: str) -> list[str]:
        """Get children accessible by parent"""


class IContentFilterService(ABC):
    @abstractmethod
    async def filter_content(
        self, content: str, child_age: int, context: str = "general"
    ) -> dict[str, Any]:
        """Filter content for child safety"""

    @abstractmethod
    async def validate_topic(self, topic: str, child_id: str) -> bool:
        """Validate if topic is appropriate"""


class IEmailService(ABC):
    @abstractmethod
    async def send_email(
        self, to: str, subject: str, template: str, context: dict[str, Any]
    ) -> bool:
        """Send templated email"""

    @abstractmethod
    async def send_deletion_warning(
        self, parent_email: str, child_name: str, deletion_date: str, export_url: str
    ) -> bool:
        """Send data deletion warning"""


class ISettingsProvider(ABC):
    @abstractmethod
    def get_database_url(self) -> str:
        """Get database URL"""

    @abstractmethod
    def get_encryption_key(self) -> str:
        """Get encryption key"""

    @abstractmethod
    def get_coppa_settings(self) -> dict[str, Any]:
        """Get COPPA compliance settings"""

    @abstractmethod
    def is_production(self) -> bool:
        """Check if running in production"""


class IEventBus(ABC):
    @abstractmethod
    async def publish_event(self, event_name: str, data: dict[str, Any]) -> None:
        """Publish domain event"""

    @abstractmethod
    async def subscribe_to_events(self, event_names: list[str], handler: Any) -> None:
        """Subscribe to domain events"""


class IExternalAPIClient(ABC):
    """Interface for external API integrations."""

    @abstractmethod
    async def make_request(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """Make request to external API endpoint."""

    @abstractmethod
    async def generate_response(
        self, child_id: str, conversation_history: list[str], current_input: str
    ) -> dict[str, Any]:
        """Generate AI response for child interaction."""


class IConsentManager(ABC):
    """Interface for COPPA consent management."""

    @abstractmethod
    async def verify_consent(self, child_id: str, operation: str) -> bool:
        """Verify parental consent for operation."""
